import json
from collections import Counter, defaultdict
from pathlib import Path

EVALUATED_PATH = Path(
    "results/finetuned/evaluated.jsonl"
)
OUTPUT_PATH = Path(
    "results/finetuned/error_analysis.json"
)
REVIEW_PATH = Path(
    "results/finetuned/error_review.jsonl"
)

def load_jsonl(path):
    examples = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                examples.append(json.loads(line))

    return examples

def main():
    examples = load_jsonl(EVALUATED_PATH)

    non_exact = [
        example
        for example in examples
        if not example["evaluation"]["exact_match"]
    ]

    with open(
        REVIEW_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        for example in non_exact:
            review_item = {
                "id": example["id"],
                "category": example.get("category"),
                "level": example.get("level"),
                "template_group": example.get(
                    "template_group"
                ),
                "natural_language": example[
                    "natural_language"
                ],
                "reference_prolog": example[
                    "reference_prolog"
                ],
                "generated_prolog": example[
                    "generated_prolog"
                ],

                # Fill these in manually
                "error_type": "",
                "semantically_correct": None,
                "notes": ""
            }

            file.write(
                json.dumps(
                    review_item,
                    ensure_ascii=False
                )
                + "\n"
            )
    
    reasoning_failures = [
        example
        for example in examples
        if (
            example["evaluation"]["reasoning_correct"]
            is False
        )
    ]

    print("===== ERROR ANALYSIS =====")
    print(f"Total examples: {len(examples)}")
    print(f"Non-exact matches: {len(non_exact)}")
    print(
        f"Reasoning failures: "
        f"{len(reasoning_failures)}"
    )

    category_failures = Counter(
        example.get("category", "unknown")
        for example in non_exact
    )

    category_totals = Counter(
        example.get("category", "unknown")
        for example in examples
    )

    print()
    print("===== NON-EXACT BY CATEGORY =====")

    category_results = {}

    for category in sorted(category_totals):
        total = category_totals[category]
        failed = category_failures[category]
        correct = total - failed

        accuracy = round(
            (correct / total) * 100,
            2
        )

        category_results[category] = {
            "total": total,
            "exact": correct,
            "non_exact": failed,
            "exact_match_percentage": accuracy
        }

        print(
            f"{category}: "
            f"{correct}/{total} exact "
            f"({accuracy}%), "
            f"{failed} failures"
        )

    level_failures = Counter(
        example.get("level", "unknown")
        for example in non_exact
    )

    level_totals = Counter(
        example.get("level", "unknown")
        for example in examples
    )

    print()
    print("===== NON-EXACT BY LEVEL =====")

    level_results = {}

    for level in sorted(
        level_totals,
        key=lambda value: str(value)
    ):
        total = level_totals[level]
        failed = level_failures[level]
        correct = total - failed

        accuracy = round(
            (correct / total) * 100,
            2
        )

        level_results[str(level)] = {
            "total": total,
            "exact": correct,
            "non_exact": failed,
            "exact_match_percentage": accuracy
        }

        print(
            f"Level {level}: "
            f"{correct}/{total} exact "
            f"({accuracy}%), "
            f"{failed} failures"
        )

    template_failures = Counter(
        example.get("template_group", "unknown")
        for example in non_exact
    )

    print()
    print("===== MOST COMMON FAILURE GROUPS =====")

    for template, count in template_failures.most_common(10):
        print(
            f"{template}: {count}"
        )

    print()
    print("===== REASONING FAILURE DETAILS =====")

    for example in reasoning_failures:
        print()
        print("-" * 70)
        print(f"ID: {example['id']}")
        print(f"Template: {example.get('template_group')}")

        print()
        print("Natural language:")
        print(example["natural_language"])

        print()
        print("Reference:")
        print(example["reference_prolog"])

        print()
        print("Generated:")
        print(example["generated_prolog"])

        print()
        print(f"Query: {example.get('query')}")
        print(f"Expected: {example.get('expected_result')}")
        print(
            "Actual:",
            example["evaluation"].get("reasoning_result")
        )

    failures_by_category = defaultdict(list)

    for example in non_exact:
        category = example.get(
            "category",
            "unknown"
        )

        failures_by_category[category].append({
            "id": example["id"],
            "natural_language":
                example["natural_language"],
            "reference_prolog":
                example["reference_prolog"],
            "generated_prolog":
                example["generated_prolog"],
            "template_group":
                example.get("template_group"),
            "level":
                example.get("level")
        })

    reasoning_failure_details = []

    for example in reasoning_failures:
        reasoning_failure_details.append({
            "id": example["id"],
            "natural_language":
                example["natural_language"],
            "reference_prolog":
                example["reference_prolog"],
            "generated_prolog":
                example["generated_prolog"],
            "query":
                example.get("query"),
            "expected_result":
                example.get("expected_result"),
            "reasoning_result":
                example["evaluation"].get(
                    "reasoning_result"
                ),
            "template_group":
                example.get("template_group")
        })

    output = {
        "summary": {
            "total_examples": len(examples),
            "exact_matches":
                len(examples) - len(non_exact),
            "non_exact_matches":
                len(non_exact),
            "reasoning_failures":
                len(reasoning_failures)
        },

        "by_category": category_results,

        "by_level": level_results,

        "template_group_failure_counts":
            dict(template_failures),

        "failures_by_category":
            dict(failures_by_category),

        "reasoning_failures":
            reasoning_failure_details
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
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print(
        f"Full error analysis saved to: "
        f"{OUTPUT_PATH}"
    )
    print(
        f"Manual review file saved to: "
        f"{REVIEW_PATH}"
    )

if __name__ == "__main__":
    main()