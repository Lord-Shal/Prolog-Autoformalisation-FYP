import json
import random
from collections import defaultdict
from datetime import date
from pathlib import Path

INPUT_PATH = Path("dataset/processed/validated.jsonl")

SPLIT_DIR = Path("dataset/splits")
TRAIN_PATH = SPLIT_DIR / "train.jsonl"
VALIDATION_PATH = SPLIT_DIR / "validation.jsonl"
TEST_PATH = SPLIT_DIR / "test.jsonl"

VERSION_PATH = Path("dataset/DATASET_VERSION")

RANDOM_SEED = 4242564

TRAIN_RATIO = 0.80
VALIDATION_RATIO = 0.10
TEST_RATIO = 0.10

def load_jsonl(path):
    examples = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                examples.append(json.loads(line))

    return examples

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

def group_examples(examples):
    groups = defaultdict(list)

    for example in examples:
        key = (
            example["category"],
            example["template_group"]
        )

        groups[key].append(example)

    return groups

def split_category(groups, total_examples, rng):
    targets = {
        "train": round(total_examples * TRAIN_RATIO),
        "validation": round(
            total_examples * VALIDATION_RATIO
        ),
    }

    targets["test"] = (
        total_examples
        - targets["train"]
        - targets["validation"]
    )

    split_groups = {
        "train": [],
        "validation": [],
        "test": []
    }

    counts = {
        "train": 0,
        "validation": 0,
        "test": 0
    }

    group_list = list(groups.items())

    rng.shuffle(group_list)

    group_list.sort(
        key=lambda item: len(item[1]),
        reverse=True
    )

    for group_key, examples in group_list:
        group_size = len(examples)

        best_split = None
        best_score = None

        for split_name in split_groups:
            new_counts = counts.copy()
            new_counts[split_name] += group_size

            score = sum(
                abs(
                    new_counts[name]
                    - targets[name]
                )
                for name in split_groups
            )

            if (
                best_score is None
                or score < best_score
            ):
                best_score = score
                best_split = split_name

        split_groups[best_split].append(
            (group_key, examples)
        )

        counts[best_split] += group_size

    return split_groups

def create_splits(dataset):
    rng = random.Random(RANDOM_SEED)

    categories = defaultdict(list)

    for example in dataset:
        categories[example["category"]].append(
            example
        )

    final_splits = {
        "train": [],
        "validation": [],
        "test": []
    }

    for category, examples in categories.items():
        groups = group_examples(examples)

        category_splits = split_category(
            groups,
            len(examples),
            rng
        )

        for split_name in final_splits:
            for _, group_examples_list in (
                category_splits[split_name]
            ):
                final_splits[split_name].extend(
                    group_examples_list
                )

    for split_name in final_splits:
        rng.shuffle(final_splits[split_name])

    return final_splits

def check_ids(splits):
    train_ids = {
        example["id"]
        for example in splits["train"]
    }

    validation_ids = {
        example["id"]
        for example in splits["validation"]
    }

    test_ids = {
        example["id"]
        for example in splits["test"]
    }

    if train_ids & validation_ids:
        raise ValueError(
            "Train/validation ID leakage detected."
        )

    if train_ids & test_ids:
        raise ValueError(
            "Train/test ID leakage detected."
        )

    if validation_ids & test_ids:
        raise ValueError(
            "Validation/test ID leakage detected."
        )

def check_template_groups(splits):
    group_locations = {}

    for split_name, examples in splits.items():
        for example in examples:
            key = (
                example["category"],
                example["template_group"]
            )

            if key in group_locations:
                if group_locations[key] != split_name:
                    raise ValueError(
                        "Template-group leakage detected: "
                        f"{key} appears in both "
                        f"{group_locations[key]} and "
                        f"{split_name}."
                    )

            else:
                group_locations[key] = split_name

def count_category(examples, category):
    return sum(
        1
        for example in examples
        if example["category"] == category
    )

def print_report(splits):
    print()
    print("=" * 55)
    print("DATASET SPLIT REPORT")
    print("=" * 55)

    categories = [
        "fact",
        "simple_rule",
        "multi_condition_rule",
        "reasoning"
    ]

    for split_name in [
        "train",
        "validation",
        "test"
    ]:
        examples = splits[split_name]

        print()
        print(
            f"{split_name.upper()}: "
            f"{len(examples)}"
        )

        for category in categories:
            count = count_category(
                examples,
                category
            )

            print(
                f"  {category}: {count}"
            )

    total = sum(
        len(examples)
        for examples in splits.values()
    )

    print()
    print(f"Total: {total}")
    print("=" * 55)

def write_version_file(splits):
    train_count = len(splits["train"])
    validation_count = len(
        splits["validation"]
    )
    test_count = len(splits["test"])

    total = (
        train_count
        + validation_count
        + test_count
    )

    content = (
        "Dataset version: v1.0\n"
        f"Frozen: {date.today().isoformat()}\n"
        f"Random seed: {RANDOM_SEED}\n"
        f"Total examples: {total}\n"
        f"Train: {train_count}\n"
        f"Validation: {validation_count}\n"
        f"Test: {test_count}\n"
        "Split strategy: grouped by category and template_group\n"
        "Source: dataset/processed/validated.jsonl\n"
    )

    VERSION_PATH.write_text(
        content,
        encoding="utf-8"
    )

def main():
    dataset = load_jsonl(INPUT_PATH)

    print(
        f"Loaded {len(dataset)} validated examples."
    )

    splits = create_splits(dataset)

    check_ids(splits)
    check_template_groups(splits)

    save_jsonl(
        splits["train"],
        TRAIN_PATH
    )

    save_jsonl(
        splits["validation"],
        VALIDATION_PATH
    )

    save_jsonl(
        splits["test"],
        TEST_PATH
    )

    write_version_file(splits)

    print_report(splits)

    print()
    print("No ID leakage detected.")
    print("No template-group leakage detected.")

    print()
    print(f"Train:      {TRAIN_PATH}")
    print(f"Validation: {VALIDATION_PATH}")
    print(f"Test:       {TEST_PATH}")
    print(f"Version:    {VERSION_PATH}")

if __name__ == "__main__":
    main()