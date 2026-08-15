import json
from pathlib import Path


OUTPUT_PATH = Path("dataset/raw/examples.jsonl")


def create_example(
    example_id,
    level,
    category,
    natural_language,
    prolog,
    template_group
):
    return {
        "id": example_id,
        "level": level,
        "category": category,
        "natural_language": natural_language,
        "prolog": prolog,
        "template_group": template_group
    }

def generate_dataset():
    examples = [
        create_example(
            "L1_0001",
            1,
            "fact",
            "Luna is a cat.",
            "cat(luna).",
            "animal_fact"
        ),

        create_example(
            "L1_0002",
            1,
            "fact",
            "Luke is human.",
            "human(luke).",
            "human_fact"
        ),

        create_example(
            "L1_0003",
            1,
            "fact",
            "Taylor is a student.",
            "student(taylor).",
            "student_fact"
        ),

        create_example(
            "L2_0001",
            2,
            "simple_rule",
            "Every cat is an animal.",
            "animal(X) :- cat(X).",
            "classification_rule"
        ),

        create_example(
            "L2_0002",
            2,
            "simple_rule",
            "If someone is a student, then they study.",
            "studies(X) :- student(X).",
            "simple_implication_rule"
        )
    ]

    return examples

def save_dataset(examples):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        for example in examples:
            json.dump(example, file)
            file.write("\n")

def main():
    examples = generate_dataset()

    save_dataset(examples)

    print(f"Generated {len(examples)} examples.")
    print(f"Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()