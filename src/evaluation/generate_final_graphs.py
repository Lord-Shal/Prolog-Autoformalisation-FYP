import json
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt

RESULTS_DIR = Path("results")
BASELINE_DIR = RESULTS_DIR / "baseline"
V1_DIR = RESULTS_DIR / "finetuned"
V2_DIR = RESULTS_DIR / "finetuned_v2"

OUTPUT_DIR = RESULTS_DIR / "figures"

V1_REVIEW_PATH = V1_DIR / "error_review.jsonl"
V2_REVIEW_PATH = V2_DIR / "error_review.jsonl"

def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)

def load_jsonl(path):
    examples = []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        for line in file:
            line = line.strip()

            if line:
                examples.append(
                    json.loads(line)
                )

    return examples

def save_figure(filename):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    path = OUTPUT_DIR / filename

    plt.tight_layout()
    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"Saved: {path}")

    plt.close()

def graph_overall_performance():
    baseline = load_json(
        BASELINE_DIR / "metrics.json"
    )

    v1 = load_json(
        V1_DIR / "metrics.json"
    )

    v2 = load_json(
        V2_DIR / "metrics.json"
    )

    models = [
        "Base",
        "Fine-tuned v1",
        "Fine-tuned v2"
    ]

    metric_names = [
        "Exact Match",
        "Syntax Valid",
        "Executable",
        "Reasoning Correct"
    ]

    metric_keys = [
        "exact_match",
        "syntax_valid",
        "executable",
        "reasoning_correct"
    ]

    all_metrics = [
        baseline,
        v1,
        v2
    ]

    x = range(len(metric_names))

    width = 0.25

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    for model_index, model in enumerate(models):

        values = [
            all_metrics[model_index][key][
                "percentage"
            ]
            for key in metric_keys
        ]

        positions = [
            position
            + (
                model_index - 1
            ) * width
            for position in x
        ]

        bars = ax.bar(
            positions,
            values,
            width,
            label=model
        )

        ax.bar_label(
            bars,
            fmt="%.1f",
            padding=3,
            fontsize=8
        )

    ax.set_ylabel("Percentage (%)")

    ax.set_title(
        "Overall Performance Across Model Versions"
    )

    ax.set_xticks(
        list(x)
    )

    ax.set_xticklabels(
        metric_names
    )

    ax.set_ylim(
        0,
        110
    )

    ax.legend()

    save_figure(
        "overall_performance.png"
    )

def graph_category_performance():
    v1 = load_json(
        V1_DIR / "metrics.json"
    )

    v2 = load_json(
        V2_DIR / "metrics.json"
    )

    categories = [
        "fact",
        "simple_rule",
        "multi_condition_rule",
        "reasoning"
    ]

    display_names = [
        "Fact",
        "Simple Rule",
        "Multi-condition Rule",
        "Reasoning"
    ]

    v1_values = [
        v1["by_category"][category][
            "exact_match"
        ]["percentage"]
        for category in categories
    ]

    v2_values = [
        v2["by_category"][category][
            "exact_match"
        ]["percentage"]
        for category in categories
    ]

    x = range(
        len(categories)
    )

    width = 0.35

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    v1_positions = [
        position - width / 2
        for position in x
    ]

    v2_positions = [
        position + width / 2
        for position in x
    ]

    bars_v1 = ax.bar(
        v1_positions,
        v1_values,
        width,
        label="Fine-tuned v1"
    )

    bars_v2 = ax.bar(
        v2_positions,
        v2_values,
        width,
        label="Fine-tuned v2"
    )

    ax.bar_label(
        bars_v1,
        fmt="%.1f",
        padding=3,
        fontsize=8
    )

    ax.bar_label(
        bars_v2,
        fmt="%.1f",
        padding=3,
        fontsize=8
    )

    ax.set_ylabel(
        "Exact Match (%)"
    )

    ax.set_title(
        "Exact Match Accuracy by Dataset Category"
    )

    ax.set_xticks(
        list(x)
    )

    ax.set_xticklabels(
        display_names
    )

    ax.set_ylim(
        0,
        110
    )

    ax.legend()

    save_figure(
        "exact_match_by_category.png"
    )

def get_error_counts(review_path):
    reviews = load_jsonl(
        review_path
    )

    counts = Counter()

    for review in reviews:
        for error_type in review.get(
            "error_types",
            []
        ):
            counts[
                error_type
            ] += 1

    return counts

def graph_error_distribution():
    v1_counts = get_error_counts(
        V1_REVIEW_PATH
    )

    v2_counts = get_error_counts(
        V2_REVIEW_PATH
    )

    error_types = [
        "incorrect_predicate",
        "reversed_arguments",
        "incorrect_arity",
        "incorrect_negation",
        "extra_condition",
        "missing_condition",
        "incorrect_structure"
    ]

    display_names = [
        "Incorrect\npredicate",
        "Reversed\narguments",
        "Incorrect\narity",
        "Incorrect\nnegation",
        "Extra\ncondition",
        "Missing\ncondition",
        "Incorrect\nstructure"
    ]

    v1_values = [
        v1_counts.get(
            error_type,
            0
        )
        for error_type in error_types
    ]

    v2_values = [
        v2_counts.get(
            error_type,
            0
        )
        for error_type in error_types
    ]

    x = range(
        len(error_types)
    )

    width = 0.35

    fig, ax = plt.subplots(
        figsize=(11, 6)
    )

    v1_positions = [
        position - width / 2
        for position in x
    ]

    v2_positions = [
        position + width / 2
        for position in x
    ]

    bars_v1 = ax.bar(
        v1_positions,
        v1_values,
        width,
        label="Fine-tuned v1"
    )

    bars_v2 = ax.bar(
        v2_positions,
        v2_values,
        width,
        label="Fine-tuned v2"
    )

    ax.bar_label(
        bars_v1,
        padding=3
    )

    ax.bar_label(
        bars_v2,
        padding=3
    )

    ax.set_ylabel(
        "Number of Errors"
    )

    ax.set_title(
        "Manual Error Distribution: "
        "Fine-tuned v1 vs v2"
    )

    ax.set_xticks(
        list(x)
    )

    ax.set_xticklabels(
        display_names
    )

    ax.legend()

    save_figure(
        "error_distribution_v1_v2.png"
    )

def find_trainer_state(model_dir):
    possible_files = list(
        model_dir.rglob(
            "trainer_state.json"
        )
    )

    if not possible_files:
        return None

    possible_files.sort(
        key=lambda path: (
            path.stat().st_mtime
        ),
        reverse=True
    )

    return possible_files[0]

def extract_training_loss(path):
    trainer_state = load_json(
        path
    )

    steps = []
    losses = []

    for entry in trainer_state.get(
        "log_history",
        []
    ):
        if (
            "loss" in entry
            and "step" in entry
        ):
            steps.append(
                entry["step"]
            )

            losses.append(
                entry["loss"]
            )

    return steps, losses

def graph_training_loss():
    trainer_state_path = Path(
        "models/checkpoints/"
        "qwen2.5-1.5b-prolog/"
        "checkpoint-693/"
        "trainer_state.json"
    )

    if not trainer_state_path.exists():
        print(
            "WARNING: Could not find "
            "trainer_state.json."
        )
        print(
            "Skipping training loss graph."
        )
        return

    steps, losses = extract_training_loss(
        trainer_state_path
    )

    if not steps:
        print(
            "WARNING: No training loss "
            "values found."
        )
        return

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    ax.plot(
        steps,
        losses,
        label="Training loss"
    )

    ax.set_xlabel(
        "Training Step"
    )

    ax.set_ylabel(
        "Training Loss"
    )

    ax.set_title(
        "Training Loss During Fine-tuning"
    )

    ax.legend()

    save_figure(
        "training_loss.png"
    )

def main():
    print(
        "===== GENERATING FINAL FIGURES ====="
    )

    graph_overall_performance()

    graph_category_performance()

    graph_error_distribution()

    graph_training_loss()

    print()
    print(
        "Finished generating figures."
    )

    print(
        f"Output directory: "
        f"{OUTPUT_DIR}"
    )

if __name__ == "__main__":
    main()