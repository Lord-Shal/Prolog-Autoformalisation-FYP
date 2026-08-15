import json
import subprocess
import tempfile
from pathlib import Path

INPUT_PATH = Path("dataset/raw/examples.jsonl")
VALIDATED_PATH = Path("dataset/processed/validated.jsonl")
REJECTED_PATH = Path("dataset/processed/rejected.jsonl")

def load_dataset(path):
    examples = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                examples.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {error}"
                )

    return examples

def run_swipl(prolog_code, goal=None):
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".pl",
        delete=False,
        encoding="utf-8"
    ) as temp_file:
        temp_file.write(prolog_code)
        temp_path = Path(temp_file.name)

    command = [
        "swipl",
        "--on-error=status",
        "-q",
        "-s",
        str(temp_path)
    ]

    if goal is not None:
        command.extend([
            "-g",
            goal
        ])
    else:
        command.extend([
            "-g",
            "halt"
        ])

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

        return {
            "return_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }

    except subprocess.TimeoutExpired:
        return {
            "return_code": -1,
            "stdout": "",
            "stderr": "SWI-Prolog execution timed out."
        }

    finally:
        if temp_path.exists():
            temp_path.unlink()

def check_syntax(prolog_code):
    result = run_swipl(prolog_code)

    return {
        "valid": result["return_code"] == 0,
        "stderr": result["stderr"]
    }

def check_execution(prolog_code):
    result = run_swipl(
        prolog_code,
        goal="true, halt"
    )

    return {
        "valid": result["return_code"] == 0,
        "stderr": result["stderr"]
    }

def normalise_query(query):
    query = query.strip()

    if query.endswith("."):
        query = query[:-1]

    return query

def execute_query(prolog_code, query):
    query = normalise_query(query)

    goal = (
        "set_prolog_flag(unknown, fail), "
        f"(({query}) "
        "-> writeln('QUERY_TRUE') "
        "; writeln('QUERY_FALSE')), "
        "halt"
    )

    result = run_swipl(
        prolog_code,
        goal=goal
    )

    if result["return_code"] != 0:
        return {
            "executed": False,
            "result": None,
            "stderr": result["stderr"]
        }

    if "QUERY_TRUE" in result["stdout"]:
        query_result = True

    elif "QUERY_FALSE" in result["stdout"]:
        query_result = False

    else:
        return {
            "executed": False,
            "result": None,
            "stderr": (
                "Query executed but no recognised "
                "true/false result was returned."
            )
        }

    return {
        "executed": True,
        "result": query_result,
        "stderr": result["stderr"]
    }

def validate_example(example):
    validation = {
        "syntax_valid": False,
        "executable": False,
        "query_checked": False,
        "query_correct": None,
        "fully_valid": False,
        "errors": []
    }

    prolog_code = example.get("prolog")

    if not prolog_code:
        validation["errors"].append(
            "Example has no Prolog code."
        )
        return validation

    syntax = check_syntax(prolog_code)

    validation["syntax_valid"] = syntax["valid"]

    if not syntax["valid"]:
        validation["errors"].append(
            f"Syntax error: {syntax['stderr']}"
        )

        return validation

    execution = check_execution(prolog_code)

    validation["executable"] = execution["valid"]

    if not execution["valid"]:
        validation["errors"].append(
            f"Execution error: {execution['stderr']}"
        )

        return validation

    if example.get("category") == "reasoning":
        query = example.get("query")
        expected_result = example.get("expected_result")

        if query is None:
            validation["errors"].append(
                "Reasoning example has no query."
            )

            return validation

        if not isinstance(expected_result, bool):
            validation["errors"].append(
                "Reasoning example has no valid expected_result."
            )

            return validation

        query_check = execute_query(
            prolog_code,
            query
        )

        validation["query_checked"] = query_check["executed"]

        if not query_check["executed"]:
            validation["errors"].append(
                f"Query execution error: "
                f"{query_check['stderr']}"
            )

            return validation

        validation["query_correct"] = (
            query_check["result"] == expected_result
        )

        if not validation["query_correct"]:
            validation["errors"].append(
                f"Query returned {query_check['result']} "
                f"but expected {expected_result}."
            )

            return validation

    validation["fully_valid"] = True

    return validation

def save_jsonl(examples, path):
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with path.open("w", encoding="utf-8") as file:
        for example in examples:
            json.dump(
                example,
                file,
                ensure_ascii=False
            )

            file.write("\n")

def print_report(stats):
    total = stats["total"]

    if total == 0:
        validation_rate = 0
    else:
        validation_rate = (
            stats["fully_valid"] / total
        ) * 100

    print()
    print("=" * 45)
    print("DATASET VALIDATION REPORT")
    print("=" * 45)

    print()
    print(
        f"Total examples:              "
        f"{stats['total']}"
    )

    print()
    print(
        f"Syntax valid:                "
        f"{stats['syntax_valid']}"
    )

    print(
        f"Syntax invalid:              "
        f"{stats['syntax_invalid']}"
    )

    print()
    print(
        f"Executable:                  "
        f"{stats['executable']}"
    )

    print(
        f"Execution failures:          "
        f"{stats['execution_failures']}"
    )

    print()
    print(
        f"Reasoning examples:          "
        f"{stats['reasoning_examples']}"
    )

    print(
        f"Correct expected result:     "
        f"{stats['query_correct']}"
    )

    print(
        f"Incorrect expected result:   "
        f"{stats['query_incorrect']}"
    )

    print()
    print(
        f"Fully valid examples:        "
        f"{stats['fully_valid']}"
    )

    print(
        f"Rejected examples:           "
        f"{stats['rejected']}"
    )

    print()
    print(
        f"Validation rate:             "
        f"{validation_rate:.1f}%"
    )

    print("=" * 45)

def main():
    dataset = load_dataset(INPUT_PATH)

    validated_examples = []
    rejected_examples = []

    stats = {
        "total": len(dataset),
        "syntax_valid": 0,
        "syntax_invalid": 0,
        "executable": 0,
        "execution_failures": 0,
        "reasoning_examples": 0,
        "query_correct": 0,
        "query_incorrect": 0,
        "fully_valid": 0,
        "rejected": 0
    }

    print(
        f"Loaded {len(dataset)} examples."
    )

    for index, example in enumerate(
        dataset,
        start=1
    ):
        validation = validate_example(example)

        if validation["syntax_valid"]:
            stats["syntax_valid"] += 1
        else:
            stats["syntax_invalid"] += 1

        if validation["executable"]:
            stats["executable"] += 1

        elif validation["syntax_valid"]:
            stats["execution_failures"] += 1

        if example.get("category") == "reasoning":
            stats["reasoning_examples"] += 1

            if validation["query_correct"] is True:
                stats["query_correct"] += 1

            elif validation["query_correct"] is False:
                stats["query_incorrect"] += 1

        if validation["fully_valid"]:
            stats["fully_valid"] += 1
            validated_examples.append(example)

        else:
            stats["rejected"] += 1

            rejected_example = example.copy()

            rejected_example["validation"] = validation

            rejected_examples.append(
                rejected_example
            )

        if index % 100 == 0:
            print(
                f"Validated {index}/{len(dataset)}..."
            )

    save_jsonl(
        validated_examples,
        VALIDATED_PATH
    )

    save_jsonl(
        rejected_examples,
        REJECTED_PATH
    )
    print()
    print("REJECTION REASONS")
    print("=" * 45)

    error_counts = {}

    for example in rejected_examples:
        for error in example["validation"]["errors"]:
            error_counts[error] = error_counts.get(error, 0) + 1

    for error, count in error_counts.items():
        print(f"{count}x: {error}")
    
    print_report(stats)

    print()
    print(
        f"Validated dataset saved to: "
        f"{VALIDATED_PATH}"
    )

    print(
        f"Rejected examples saved to: "
        f"{REJECTED_PATH}"
    )

if __name__ == "__main__":
    main()