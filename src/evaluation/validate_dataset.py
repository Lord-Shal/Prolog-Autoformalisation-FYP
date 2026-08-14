import json
import subprocess
import tempfile
from pathlib import Path


DATASET_PATH = Path("dataset/processed/mini_dataset.json")


def load_dataset(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


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
            "-q",
            "-s", temp_path,
            "-g", "halt"
        ],
        capture_output=True,
        text=True
    )

    Path(temp_path).unlink()

    return {
        "valid": result.returncode == 0,
        "return_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip()
    }


def main():
    dataset = load_dataset(DATASET_PATH)

    print(f"Loaded {len(dataset)} examples.\n")

    valid_count = 0

    for example in dataset:
        result = validate_prolog(example["prolog"])

        if result["valid"]:
            valid_count += 1

        print(f"ID: {example['id']}")
        print(f"Natural language: {example['natural_language']}")
        print(f"Prolog: {example['prolog']}")
        print(f"Category: {example['category']}")
        print(f"Valid Prolog: {result['valid']}")

        if result["stderr"]:
            print(f"Error: {result['stderr']}")

        print("-" * 50)

    print()
    print(f"Valid examples: {valid_count}/{len(dataset)}")


if __name__ == "__main__":
    main()