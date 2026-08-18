import sys
import json
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

def get_paths(run_name):
    result_dir = Path("results") / run_name

    return (
        result_dir / "predictions.jsonl",
        result_dir / "evaluated.jsonl",
        result_dir / "metrics.jsonl"
    )

def load_jsonl(path):
    examples = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                examples.append(json.loads(line))

    return examples

def normalise_prolog(code):

    if not code:
        return ""

    code = code.replace("\r\n", "\n")
    code = code.replace("\r", "\n")

    lines = [
        line.rstrip()
        for line in code.split("\n")
    ]

    return "\n".join(lines).strip()

def exact_match(reference, generated):
    return normalise_prolog(reference) == normalise_prolog(generated)

def run_swipl(prolog_code, goal="halt"):

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".pl",
            delete=False,
            encoding="utf-8"
        ) as temp_file:

            temp_file.write(prolog_code)
            temp_path = Path(temp_file.name)

        result = subprocess.run(
            [
                "swipl",
                "--on-error=status",
                "-q",
                "-s",
                str(temp_path),
                "-g",
                goal
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "return_code": None,
            "stdout": "",
            "stderr": "SWI-Prolog execution timed out."
        }

    except Exception as error:
        return {
            "success": False,
            "return_code": None,
            "stdout": "",
            "stderr": str(error)
        }

    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()

def syntax_valid(generated):
    if not generated.strip():
        return False, "Empty generation."

    result = run_swipl(generated)

    return result["success"], result["stderr"]

def executable(generated):

    if not generated.strip():
        return False, "Empty generation."

    result = run_swipl(
        generated,
        goal="true,halt"
    )

    return result["success"], result["stderr"]

def run_reasoning_query(prolog_code, query):

    if not prolog_code.strip():
        return None, "Empty generation."

    query = query.strip()

    if query.endswith("."):
        query = query[:-1].strip()

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".pl",
            delete=False,
            encoding="utf-8"
        ) as temp_file:

            temp_file.write(prolog_code)
            temp_path = Path(temp_file.name)

        goal = (
            f"set_prolog_flag(unknown, fail),"
            f"catch("
            f"(({query}) -> "
            f"write('__QUERY_TRUE__') ; "
            f"write('__QUERY_FALSE__')),"
            f"_,"
            f"write('__QUERY_ERROR__')"
            f"),halt"
        )

        result = subprocess.run(
            [
                "swipl",
                "--on-error=status",
                "-q",
                "-s",
                str(temp_path),
                "-g",
                goal
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        stdout = result.stdout.strip()

        if "__QUERY_TRUE__" in stdout:
            return True, ""

        if "__QUERY_FALSE__" in stdout:
            return False, ""

        if "__QUERY_ERROR__" in stdout:
            return None, result.stderr.strip()

        return None, result.stderr.strip()

    except subprocess.TimeoutExpired:
        return None, "Reasoning query timed out."

    except Exception as error:
        return None, str(error)

    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()

def evaluate_example(example):
    reference = example["reference_prolog"]
    generated = example["generated_prolog"]

    is_exact = exact_match(
        reference,
        generated
    )

    is_syntax_valid, syntax_error = syntax_valid(
        generated
    )

    if is_syntax_valid:
        is_executable, execution_error = executable(
            generated
        )
    else:
        is_executable = False
        execution_error = syntax_error

    reasoning_correct = None
    reasoning_result = None
    reasoning_error = ""

    if (
        "query" in example
        and "expected_result" in example
    ):
        if is_executable:

            reasoning_result, reasoning_error = run_reasoning_query(
                generated,
                example["query"]
            )

            if reasoning_result is not None:
                reasoning_correct = (
                    reasoning_result
                    == example["expected_result"]
                )
            else:
                reasoning_correct = False

        else:
            reasoning_correct = False
            reasoning_error = execution_error

    evaluated = dict(example)

    evaluated["evaluation"] = {
        "exact_match": is_exact,
        "syntax_valid": is_syntax_valid,
        "executable": is_executable,
        "reasoning_correct": reasoning_correct,
        "reasoning_result": reasoning_result
    }

    evaluated["errors"] = {
        "syntax": syntax_error,
        "execution": execution_error,
        "reasoning": reasoning_error
    }

    return evaluated

def calculate_percentage(correct, total):
    if total == 0:
        return None

    return round(
        (correct / total) * 100,
        2
    )

def build_metrics(evaluated_examples):
    total = len(evaluated_examples)

    exact_count = sum(
        example["evaluation"]["exact_match"]
        for example in evaluated_examples
    )

    syntax_count = sum(
        example["evaluation"]["syntax_valid"]
        for example in evaluated_examples
    )

    executable_count = sum(
        example["evaluation"]["executable"]
        for example in evaluated_examples
    )

    reasoning_examples = [
        example
        for example in evaluated_examples
        if example["evaluation"]["reasoning_correct"] is not None
    ]

    reasoning_correct_count = sum(
        example["evaluation"]["reasoning_correct"]
        for example in reasoning_examples
    )

    metrics = {
        "total_examples": total,

        "exact_match": {
            "correct": exact_count,
            "total": total,
            "percentage": calculate_percentage(
                exact_count,
                total
            )
        },

        "syntax_valid": {
            "correct": syntax_count,
            "total": total,
            "percentage": calculate_percentage(
                syntax_count,
                total
            )
        },

        "executable": {
            "correct": executable_count,
            "total": total,
            "percentage": calculate_percentage(
                executable_count,
                total
            )
        },

        "reasoning_correct": {
            "correct": reasoning_correct_count,
            "total": len(reasoning_examples),
            "percentage": calculate_percentage(
                reasoning_correct_count,
                len(reasoning_examples)
            )
        }
    }

    return metrics

def build_category_metrics(evaluated_examples):
    categories = defaultdict(list)

    for example in evaluated_examples:
        category = example.get(
            "category",
            "unknown"
        )

        categories[category].append(example)

    results = {}

    for category, examples in categories.items():
        results[category] = build_metrics(examples)

    return results

def save_jsonl(path, examples):
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        for example in examples:
            file.write(
                json.dumps(
                    example,
                    ensure_ascii=False
                )
                + "\n"
            )

def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python src/evaluation/evaluate_predictions.py "
            "<baseline|finetuned|finetuned_v2>"
        )

    run_name = sys.argv[1].lower()

    if run_name not in {"baseline", "finetuned", "finetuned_v2"}:
        raise SystemExit(
            "Run name must be either 'baseline' or 'finetuned' or 'finetuned_v2'."
        )

    (
        predictions_path,
        evaluated_path,
        metrics_path
    ) = get_paths(run_name)

    print(
        f"Loading predictions from "
        f"{predictions_path}"
    )

    predictions = load_jsonl(
        predictions_path
    )

    print(
        f"Loaded {len(predictions)} predictions."
    )

    evaluated_examples = []

    for index, example in enumerate(
        predictions,
        start=1
    ):
        print(
            f"[{index}/{len(predictions)}] "
            f"Evaluating {example['id']}"
        )

        evaluated = evaluate_example(
            example
        )

        evaluated_examples.append(
            evaluated
        )

    save_jsonl(
        evaluated_path,
        evaluated_examples
    )

    metrics = build_metrics(
        evaluated_examples
    )

    metrics["by_category"] = (
        build_category_metrics(
            evaluated_examples
        )
    )

    metrics_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        metrics_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print(
        f"===== {run_name.upper()} RESULTS ====="
    )

    print(
        f"Exact Match: "
        f"{metrics['exact_match']['correct']}"
        f"/{metrics['exact_match']['total']} "
        f"({metrics['exact_match']['percentage']}%)"
    )

    print(
        f"Syntax Valid: "
        f"{metrics['syntax_valid']['correct']}"
        f"/{metrics['syntax_valid']['total']} "
        f"({metrics['syntax_valid']['percentage']}%)"
    )

    print(
        f"Executable: "
        f"{metrics['executable']['correct']}"
        f"/{metrics['executable']['total']} "
        f"({metrics['executable']['percentage']}%)"
    )

    print(
        f"Reasoning Correct: "
        f"{metrics['reasoning_correct']['correct']}"
        f"/{metrics['reasoning_correct']['total']} "
        f"({metrics['reasoning_correct']['percentage']}%)"
    )

    print()
    print(
        f"Detailed results: {evaluated_path}"
    )

    print(
        f"Aggregate metrics: {metrics_path}"
    )

if __name__ == "__main__":
    main()