import json
from pathlib import Path


TRAIN_V1_PATH = Path(
    "dataset/splits/train.jsonl"
)

REFINEMENT_PATH = Path(
    "dataset/refinement/targeted_v2.jsonl"
)

TRAIN_V2_PATH = Path(
    "dataset/splits/train_v2.jsonl"
)


def load_jsonl(path):
    examples = []

    with open(path, "r", encoding="utf-8") as file:
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

    with open(path, "w", encoding="utf-8") as file:
        for example in examples:
            file.write(
                json.dumps(
                    example,
                    ensure_ascii=False
                )
                + "\n"
            )


def main():
    train_v1 = load_jsonl(
        TRAIN_V1_PATH
    )

    refinement = load_jsonl(
        REFINEMENT_PATH
    )

    train_v2 = (
        train_v1
        + refinement
    )

    ids = [
        example["id"]
        for example in train_v2
    ]

    unique_ids = set(ids)

    print("===== BUILD TRAIN V2 =====")
    print(
        f"Original train examples: "
        f"{len(train_v1)}"
    )
    print(
        f"Refinement examples: "
        f"{len(refinement)}"
    )
    print(
        f"Combined examples: "
        f"{len(train_v2)}"
    )

    print()

    if len(ids) != len(unique_ids):
        raise RuntimeError(
            "Duplicate IDs detected in "
            "combined v2 training data."
        )

    print("No duplicate IDs.")

    save_jsonl(
        train_v2,
        TRAIN_V2_PATH
    )

    print()
    print(
        f"Saved v2 training set to: "
        f"{TRAIN_V2_PATH}"
    )


if __name__ == "__main__":
    main()