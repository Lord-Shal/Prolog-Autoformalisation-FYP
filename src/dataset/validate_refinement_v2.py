import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

REFINEMENT_PATH = Path(
    "dataset/refinement/targeted_v2.jsonl"
)

TRAIN_PATH = Path(
    "dataset/splits/train.jsonl"
)

TEST_PATH = Path(
    "dataset/splits/test.jsonl"
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

def validate_prolog(prolog_code):
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".pl",
        delete=False,
        encoding="utf-8"
    ) as temp_file:
        temp_file.write(prolog_code)
        temp_path = temp_file.name

    result = subprocess.run(
        [
            "swipl",
            "--on-error=status",
            "-q",
            "-s",
            temp_path,
            "-g",
            "halt"
        ],
        capture_output=True,
        text=True
    )

    Path(temp_path).unlink()

    return {
        "valid": result.returncode == 0,
        "return_code": result.returncode,
        "stderr": result.stderr.strip()
    }

def normalise_text(text):
    return " ".join(
        text.lower().split()
    )

def main():
    refinement = load_jsonl(
        REFINEMENT_PATH
    )

    train = load_jsonl(
        TRAIN_PATH
    )

    test = load_jsonl(
        TEST_PATH
    )

    print(
        "===== V2 REFINEMENT VALIDATION ====="
    )
    print(
        f"Total refinement examples: "
        f"{len(refinement)}"
    )

    level_counts = Counter(
        example.get("level", "unknown")
        for example in refinement
    )

    category_counts = Counter(
        example.get("category", "unknown")
        for example in refinement
    )

    template_counts = Counter(
        example.get(
            "template_group",
            "unknown"
        )
        for example in refinement
    )

    print()
    print("===== BY LEVEL =====")

    for level in sorted(
        level_counts,
        key=lambda value: str(value)
    ):
        print(
            f"Level {level}: "
            f"{level_counts[level]}"
        )

    print()
    print("===== BY CATEGORY =====")

    for category in sorted(
        category_counts
    ):
        print(
            f"{category}: "
            f"{category_counts[category]}"
        )

    print()
    print("===== BY TEMPLATE GROUP =====")

    for template, count in sorted(
        template_counts.items()
    ):
        print(
            f"{template}: {count}"
        )

    required_fields = [
        "id",
        "level",
        "category",
        "natural_language",
        "prolog",
        "template_group"
    ]

    missing_fields = []

    for example in refinement:
        for field in required_fields:
            if field not in example:
                missing_fields.append(
                    (
                        example.get(
                            "id",
                            "unknown"
                        ),
                        field
                    )
                )

    print()
    print("===== REQUIRED FIELDS =====")

    if missing_fields:
        for example_id, field in missing_fields:
            print(
                f"{example_id}: "
                f"missing {field}"
            )
    else:
        print(
            "All required fields present."
        )

    ids = [
        example["id"]
        for example in refinement
        if "id" in example
    ]

    duplicate_ids = [
        example_id
        for example_id, count
        in Counter(ids).items()
        if count > 1
    ]

    print()
    print("===== DUPLICATE IDS =====")

    if duplicate_ids:
        for example_id in duplicate_ids:
            print(example_id)
    else:
        print("No duplicate IDs.")

    refinement_pairs = [
        (
            normalise_text(
                example["natural_language"]
            ),
            normalise_text(
                example["prolog"]
            )
        )
        for example in refinement
    ]

    duplicate_pairs = [
        pair
        for pair, count
        in Counter(
            refinement_pairs
        ).items()
        if count > 1
    ]

    print()
    print(
        "===== DUPLICATES WITHIN REFINEMENT ====="
    )

    if duplicate_pairs:
        print(
            f"Duplicate NL-Prolog pairs: "
            f"{len(duplicate_pairs)}"
        )

        for nl, prolog in duplicate_pairs[:10]:
            print()
            print(f"NL: {nl}")
            print(f"Prolog: {prolog}")
    else:
        print(
            "No duplicate NL-Prolog pairs."
        )

    train_pairs = {
        (
            normalise_text(
                example["natural_language"]
            ),
            normalise_text(
                example["prolog"]
            )
        )
        for example in train
    }

    train_overlap = [
        example
        for example in refinement
        if (
            normalise_text(
                example["natural_language"]
            ),
            normalise_text(
                example["prolog"]
            )
        ) in train_pairs
    ]

    print()
    print(
        "===== OVERLAP WITH V1 TRAIN SET ====="
    )

    print(
        f"Exact NL-Prolog overlap: "
        f"{len(train_overlap)}"
    )

    for example in train_overlap[:10]:
        print(
            f"- {example['id']}: "
            f"{example['natural_language']}"
        )

    test_pairs = {
        (
            normalise_text(
                example["natural_language"]
            ),
            normalise_text(
                example["prolog"]
            )
        )
        for example in test
    }

    test_overlap = [
        example
        for example in refinement
        if (
            normalise_text(
                example["natural_language"]
            ),
            normalise_text(
                example["prolog"]
            )
        ) in test_pairs
    ]

    print()
    print(
        "===== EXACT OVERLAP WITH TEST SET ====="
    )

    print(
        f"Exact NL-Prolog overlap: "
        f"{len(test_overlap)}"
    )

    for example in test_overlap[:10]:
        print(
            f"- {example['id']}: "
            f"{example['natural_language']}"
        )

    test_nl = {
        normalise_text(
            example["natural_language"]
        )
        for example in test
    }

    nl_test_overlap = [
        example
        for example in refinement
        if normalise_text(
            example["natural_language"]
        ) in test_nl
    ]

    print()
    print(
        "===== NATURAL LANGUAGE OVERLAP WITH TEST ====="
    )

    print(
        f"Exact NL overlap: "
        f"{len(nl_test_overlap)}"
    )

    for example in nl_test_overlap[:10]:
        print(
            f"- {example['id']}: "
            f"{example['natural_language']}"
        )

    print()
    print(
        "===== SWI-PROLOG VALIDATION ====="
    )

    valid_count = 0
    invalid_examples = []

    for index, example in enumerate(
        refinement,
        start=1
    ):
        result = validate_prolog(
            example["prolog"]
        )

        if result["valid"]:
            valid_count += 1
        else:
            invalid_examples.append(
                {
                    "id": example["id"],
                    "prolog": example[
                        "prolog"
                    ],
                    "stderr": result[
                        "stderr"
                    ]
                }
            )

        if index % 25 == 0:
            print(
                f"Validated "
                f"{index}/{len(refinement)}"
            )

    print()
    print(
        f"Syntax valid / executable: "
        f"{valid_count}/"
        f"{len(refinement)}"
    )

    if invalid_examples:
        print()
        print(
            "===== INVALID PROLOG ====="
        )

        for example in invalid_examples:
            print()
            print(
                f"ID: {example['id']}"
            )
            print(
                f"Prolog: "
                f"{example['prolog']}"
            )
            print(
                f"Error: "
                f"{example['stderr']}"
            )

    all_good = (
        len(refinement) == 250
        and not missing_fields
        and not duplicate_ids
        and not duplicate_pairs
        and len(test_overlap) == 0
        and len(nl_test_overlap) == 0
        and valid_count == len(refinement)
    )

    print()
    print(
        "===== FINAL VALIDATION STATUS ====="
    )

    if all_good:
        print(
            "PASS - refinement dataset is ready "
            "for the next stage."
        )
    else:
        print(
            "REVIEW REQUIRED - one or more "
            "validation checks failed."
        )

if __name__ == "__main__":
    main()