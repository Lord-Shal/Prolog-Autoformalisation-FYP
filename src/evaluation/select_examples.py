import json
from pathlib import Path

BASELINE_PATH = Path(
    "results/baseline/evaluated.jsonl"
)

V1_PATH = Path(
    "results/finetuned/evaluated.jsonl"
)

V2_PATH = Path(
    "results/finetuned_v2/evaluated.jsonl"
)

OUTPUT_PATH = Path(
    "results/representative_examples.json"
)

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

def index_by_id(examples):
    return {
        example["id"]: example
        for example in examples
    }

def is_exact(example):
    return example[
        "evaluation"
    ]["exact_match"]

def build_comparison(
    baseline_example,
    v1_example,
    v2_example
):
    return {
        "id": v2_example["id"],
        "category": v2_example.get(
            "category"
        ),
        "level": v2_example.get(
            "level"
        ),
        "template_group": v2_example.get(
            "template_group"
        ),
        "natural_language": v2_example[
            "natural_language"
        ],
        "reference_prolog": v2_example[
            "reference_prolog"
        ],

        "baseline": {
            "generated_prolog":
                baseline_example[
                    "generated_prolog"
                ],
            "exact_match":
                is_exact(
                    baseline_example
                )
        },

        "finetuned_v1": {
            "generated_prolog":
                v1_example[
                    "generated_prolog"
                ],
            "exact_match":
                is_exact(
                    v1_example
                )
        },

        "finetuned_v2": {
            "generated_prolog":
                v2_example[
                    "generated_prolog"
                ],
            "exact_match":
                is_exact(
                    v2_example
                )
        }
    }

def print_example(
    title,
    comparison
):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)

    print(
        f"ID: {comparison['id']}"
    )

    print(
        f"Category: "
        f"{comparison['category']}"
    )

    print(
        f"Template: "
        f"{comparison['template_group']}"
    )

    print()

    print("Natural language:")
    print(
        comparison[
            "natural_language"
        ]
    )

    print()

    print("Reference:")
    print(
        comparison[
            "reference_prolog"
        ]
    )

    print()

    print("Baseline:")
    print(
        comparison[
            "baseline"
        ]["generated_prolog"]
    )

    print(
        "Exact:",
        comparison[
            "baseline"
        ]["exact_match"]
    )

    print()

    print("Fine-tuned v1:")
    print(
        comparison[
            "finetuned_v1"
        ]["generated_prolog"]
    )

    print(
        "Exact:",
        comparison[
            "finetuned_v1"
        ]["exact_match"]
    )

    print()

    print("Fine-tuned v2:")
    print(
        comparison[
            "finetuned_v2"
        ]["generated_prolog"]
    )

    print(
        "Exact:",
        comparison[
            "finetuned_v2"
        ]["exact_match"]
    )

def main():
    baseline_examples = load_jsonl(
        BASELINE_PATH
    )

    v1_examples = load_jsonl(
        V1_PATH
    )

    v2_examples = load_jsonl(
        V2_PATH
    )

    baseline_by_id = index_by_id(
        baseline_examples
    )

    v1_by_id = index_by_id(
        v1_examples
    )

    v2_by_id = index_by_id(
        v2_examples
    )

    common_ids = sorted(
        set(baseline_by_id)
        & set(v1_by_id)
        & set(v2_by_id)
    )

    print(
        "===== REPRESENTATIVE EXAMPLE SELECTION ====="
    )

    print(
        f"Common examples: "
        f"{len(common_ids)}"
    )

    base_fail_v1_v2_success = []

    for example_id in common_ids:
        baseline = baseline_by_id[
            example_id
        ]

        v1 = v1_by_id[
            example_id
        ]

        v2 = v2_by_id[
            example_id
        ]

        if (
            not is_exact(baseline)
            and is_exact(v1)
            and is_exact(v2)
        ):
            base_fail_v1_v2_success.append(
                build_comparison(
                    baseline,
                    v1,
                    v2
                )
            )

    example_1 = next(
        (
            example
            for example
            in base_fail_v1_v2_success
            if example["category"]
            == "multi_condition_rule"
        ),
        base_fail_v1_v2_success[0]
        if base_fail_v1_v2_success
        else None
    )

    v1_fail_v2_success = []

    for example_id in common_ids:
        baseline = baseline_by_id[
            example_id
        ]

        v1 = v1_by_id[
            example_id
        ]

        v2 = v2_by_id[
            example_id
        ]

        if (
            not is_exact(v1)
            and is_exact(v2)
        ):
            v1_fail_v2_success.append(
                build_comparison(
                    baseline,
                    v1,
                    v2
                )
            )

    example_2 = next(
        (
            example
            for example
            in v1_fail_v2_success
            if example["category"]
            == "multi_condition_rule"
        ),
        v1_fail_v2_success[0]
        if v1_fail_v2_success
        else None
    )

    v1_success_v2_fail = []

    for example_id in common_ids:
        baseline = baseline_by_id[
            example_id
        ]

        v1 = v1_by_id[
            example_id
        ]

        v2 = v2_by_id[
            example_id
        ]

        if (
            is_exact(v1)
            and not is_exact(v2)
        ):
            v1_success_v2_fail.append(
                build_comparison(
                    baseline,
                    v1,
                    v2
                )
            )

    example_regression = (
        v1_success_v2_fail[0]
        if v1_success_v2_fail
        else None
    )

    v2_failures = []

    for example_id in common_ids:
        baseline = baseline_by_id[
            example_id
        ]

        v1 = v1_by_id[
            example_id
        ]

        v2 = v2_by_id[
            example_id
        ]

        if not is_exact(v2):
            v2_failures.append(
                build_comparison(
                    baseline,
                    v1,
                    v2
                )
            )

    example_3 = next(
        (
            example
            for example
            in v2_failures
            if example[
                "template_group"
            ] == "shared_child_inequality"
        ),
        v2_failures[0]
        if v2_failures
        else None
    )

    selected = {
        "base_fail_v1_v2_success":
            example_1,

        "v1_fail_v2_success":
            example_2,

        "v1_success_v2_fail":
            example_regression,

        "v2_remaining_failure":
            example_3,

        "candidate_counts": {
            "base_fail_v1_v2_success":
                len(
                    base_fail_v1_v2_success
                ),

            "v1_fail_v2_success":
                len(
                    v1_fail_v2_success
                ),

            "v1_success_v2_fail":
                len(
                    v1_success_v2_fail
                ),

            "v2_failures":
                len(
                    v2_failures
                )
        }
    }

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
            selected,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()

    print(
        "Candidate counts:"
    )

    print(
        "Base fail -> V1 success -> V2 success:",
        len(
            base_fail_v1_v2_success
        )
    )

    print(
        "V1 success -> V2 fail:",
        len(
            v1_success_v2_fail
        )
    )

    print(
        "V1 fail -> V2 success:",
        len(
            v1_fail_v2_success
        )
    )

    print(
        "V2 remaining failures:",
        len(
            v2_failures
        )
    )

    if example_1 is not None:
        print_example(
            "EXAMPLE 1 - "
            "BASE FAILS, V1 AND V2 SUCCEED",
            example_1
        )

    if example_2 is not None:
        print_example(
            "EXAMPLE 2 - "
            "V1 FAILS, V2 SUCCEEDS",
            example_2
        )

    if example_3 is not None:
        print_example(
            "EXAMPLE 3 - "
            "V2 REMAINING FAILURE",
            example_3
        )

    if example_regression is not None:
        print_example(
            "EXAMPLE 4 - "
            "V1 SUCCEEDS, V2 REGRESSES",
            example_regression
        )

    print()

    print(
        f"Selected examples saved to: "
        f"{OUTPUT_PATH}"
    )

if __name__ == "__main__":
    main()