import json
from pathlib import Path


RESULTS_DIR = Path("results")

BASELINE_DIR = RESULTS_DIR / "baseline"
V1_DIR = RESULTS_DIR / "finetuned"
V2_DIR = RESULTS_DIR / "finetuned_v2"

OUTPUT_PATH = RESULTS_DIR / "final_comparison.json"

def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)

def load_metrics(result_dir):
    return load_json(
        result_dir / "metrics.json"
    )

def load_error_analysis(result_dir):
    return load_json(
        result_dir / "error_analysis.json"
    )

def percentage(numerator, denominator):
    if denominator == 0:
        return 0.0

    return round(
        (numerator / denominator) * 100,
        2
    )

def percentage_point_change(old, new):
    return round(new - old, 2)

def print_overall_table(results):
    print()
    print("===== OVERALL PERFORMANCE =====")
    print()

    header = (
        f"{'Model':<18}"
        f"{'Exact Match':<20}"
        f"{'Syntax Valid':<20}"
        f"{'Executable':<20}"
        f"{'Reasoning':<20}"
    )

    print(header)
    print("-" * len(header))

    for model_name, metrics in results.items():

        exact = (
            f"{metrics['exact_match']['correct']}/"
            f"{metrics['exact_match']['total']} "
            f"({metrics['exact_match']['percentage']}%)"
        )

        syntax = (
            f"{metrics['syntax_valid']['correct']}/"
            f"{metrics['syntax_valid']['total']} "
            f"({metrics['syntax_valid']['percentage']}%)"
        )

        executable = (
            f"{metrics['executable']['correct']}/"
            f"{metrics['executable']['total']} "
            f"({metrics['executable']['percentage']}%)"
        )

        reasoning = (
            f"{metrics['reasoning_correct']['correct']}/"
            f"{metrics['reasoning_correct']['total']} "
            f"({metrics['reasoning_correct']['percentage']}%)"
        )

        print(
            f"{model_name:<18}"
            f"{exact:<20}"
            f"{syntax:<20}"
            f"{executable:<20}"
            f"{reasoning:<20}"
        )

def print_category_table(v1_errors, v2_errors):
    print()
    print("===== EXACT MATCH BY CATEGORY =====")
    print()

    v1_categories = v1_errors["by_category"]
    v2_categories = v2_errors["by_category"]

    categories = sorted(
        set(v1_categories)
        | set(v2_categories)
    )

    header = (
        f"{'Category':<25}"
        f"{'Test N':<10}"
        f"{'V1':<18}"
        f"{'V2':<18}"
        f"{'Change':<12}"
    )

    print(header)
    print("-" * len(header))

    for category in categories:
        v1 = v1_categories[category]
        v2 = v2_categories[category]

        v1_percentage = (
            v1["exact_match_percentage"]
        )

        v2_percentage = (
            v2["exact_match_percentage"]
        )

        change = percentage_point_change(
            v1_percentage,
            v2_percentage
        )

        v1_text = (
            f"{v1['exact']}/{v1['total']} "
            f"({v1_percentage}%)"
        )

        v2_text = (
            f"{v2['exact']}/{v2['total']} "
            f"({v2_percentage}%)"
        )

        change_text = (
            f"{change:+.2f} pp"
        )

        print(
            f"{category:<25}"
            f"{v1['total']:<10}"
            f"{v1_text:<18}"
            f"{v2_text:<18}"
            f"{change_text:<12}"
        )

def print_error_table(v1_errors, v2_errors):
    print()
    print("===== MANUAL ERROR COMPARISON =====")
    print()

    v1_counts = (
        v1_errors
        .get("manual_review", {})
        .get("error_type_counts", {})
    )

    v2_counts = (
        v2_errors
        .get("manual_review", {})
        .get("error_type_counts", {})
    )

    if not v1_counts and not v2_counts:
        print(
            "Manual error counts are not stored "
            "inside error_analysis.json."
        )
        print(
            "Update analyse_errors.py to save "
            "manual_review_results into the output."
        )
        return

    error_types = sorted(
        set(v1_counts)
        | set(v2_counts)
    )

    header = (
        f"{'Error Type':<30}"
        f"{'V1':<10}"
        f"{'V2':<10}"
        f"{'Change':<10}"
    )

    print(header)
    print("-" * len(header))

    for error_type in error_types:
        v1 = v1_counts.get(
            error_type,
            0
        )

        v2 = v2_counts.get(
            error_type,
            0
        )

        change = v2 - v1

        print(
            f"{error_type:<30}"
            f"{v1:<10}"
            f"{v2:<10}"
            f"{change:+d}"
        )

def print_failure_groups(v2_errors):
    print()
    print("===== V2 REMAINING FAILURE GROUPS =====")
    print()

    groups = v2_errors[
        "template_group_failure_counts"
    ]

    sorted_groups = sorted(
        groups.items(),
        key=lambda item: item[1],
        reverse=True
    )

    total_failures = v2_errors[
        "summary"
    ]["non_exact_matches"]

    for group, count in sorted_groups:

        share = percentage(
            count,
            total_failures
        )

        print(
            f"{group:<30}"
            f"{count:>3} "
            f"({share:.2f}% of failures)"
        )

def build_output(
    baseline_metrics,
    v1_metrics,
    v2_metrics,
    v1_errors,
    v2_errors
):
    base_exact = baseline_metrics[
        "exact_match"
    ]["percentage"]

    v1_exact = v1_metrics[
        "exact_match"
    ]["percentage"]

    v2_exact = v2_metrics[
        "exact_match"
    ]["percentage"]

    v1_failures = v1_errors[
        "summary"
    ]["non_exact_matches"]

    v2_failures = v2_errors[
        "summary"
    ]["non_exact_matches"]

    failures_removed = (
        v1_failures - v2_failures
    )

    failure_reduction = percentage(
        failures_removed,
        v1_failures
    )

    return {
        "overall": {
            "baseline": baseline_metrics,
            "finetuned_v1": v1_metrics,
            "finetuned_v2": v2_metrics
        },

        "exact_match_improvement": {
            "baseline_to_v1_percentage_points":
                percentage_point_change(
                    base_exact,
                    v1_exact
                ),

            "v1_to_v2_percentage_points":
                percentage_point_change(
                    v1_exact,
                    v2_exact
                ),

            "baseline_to_v2_percentage_points":
                percentage_point_change(
                    base_exact,
                    v2_exact
                )
        },

        "v1_to_v2_failures": {
            "v1_non_exact": v1_failures,
            "v2_non_exact": v2_failures,
            "failures_removed":
                failures_removed,
            "relative_failure_reduction_percentage":
                failure_reduction
        },

        "category_comparison": {
            "v1": v1_errors[
                "by_category"
            ],
            "v2": v2_errors[
                "by_category"
            ]
        },

        "error_comparison": {
            "v1": (
                v1_errors
                .get("manual_review", {})
                .get(
                    "error_type_counts",
                    {}
                )
            ),
            "v2": (
                v2_errors
                .get("manual_review", {})
                .get(
                    "error_type_counts",
                    {}
                )
            )
        },

        "v2_remaining_failure_groups":
            v2_errors[
                "template_group_failure_counts"
            ]
    }

def main():
    print(
        "===== FINAL EXPERIMENT COMPARISON ====="
    )

    baseline_metrics = load_metrics(
        BASELINE_DIR
    )

    v1_metrics = load_metrics(
        V1_DIR
    )

    v2_metrics = load_metrics(
        V2_DIR
    )

    v1_errors = load_error_analysis(
        V1_DIR
    )

    v2_errors = load_error_analysis(
        V2_DIR
    )

    results = {
        "Base": baseline_metrics,
        "Fine-tuned v1": v1_metrics,
        "Fine-tuned v2": v2_metrics
    }

    print_overall_table(
        results
    )

    print_category_table(
        v1_errors,
        v2_errors
    )

    print_error_table(
        v1_errors,
        v2_errors
    )

    print_failure_groups(
        v2_errors
    )

    output = build_output(
        baseline_metrics,
        v1_metrics,
        v2_metrics,
        v1_errors,
        v2_errors
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("===== SUMMARY =====")

    base_exact = baseline_metrics[
        "exact_match"
    ]["percentage"]

    v1_exact = v1_metrics[
        "exact_match"
    ]["percentage"]

    v2_exact = v2_metrics[
        "exact_match"
    ]["percentage"]

    print(
        "Baseline -> V1 exact match: "
        f"{base_exact:.2f}% -> "
        f"{v1_exact:.2f}%"
    )

    print(
        "V1 -> V2 exact match: "
        f"{v1_exact:.2f}% -> "
        f"{v2_exact:.2f}%"
    )

    print(
        "V1 -> V2 improvement: "
        f"{v2_exact - v1_exact:+.2f} "
        "percentage points"
    )

    v1_failures = v1_errors[
        "summary"
    ]["non_exact_matches"]

    v2_failures = v2_errors[
        "summary"
    ]["non_exact_matches"]

    reduction = percentage(
        v1_failures - v2_failures,
        v1_failures
    )

    print(
        "V1 -> V2 non-exact predictions: "
        f"{v1_failures} -> "
        f"{v2_failures}"
    )

    print(
        "Relative reduction in "
        f"non-exact predictions: "
        f"{reduction:.2f}%"
    )

    print()
    print(
        f"Final comparison saved to: "
        f"{OUTPUT_PATH}"
    )

if __name__ == "__main__":
    main()