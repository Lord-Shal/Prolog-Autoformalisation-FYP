import json
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

TEST_PATH = Path("dataset/splits/test.jsonl")
OUTPUT_PATH = Path("results/baseline/predictions.jsonl")

MAX_NEW_TOKENS = 256

def load_model():
    print(f"Loading model: {MODEL_NAME}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        dtype=torch.float16,
        device_map="cuda"
    )

    model.eval()

    return tokenizer, model

def load_test_set(path):
    examples = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                examples.append(json.loads(line))

    return examples

def build_messages(natural_language):
    return [
        {
            "role": "system",
            "content": (
                "Translate natural language into Prolog. "
                "Return only the Prolog code. "
                "Do not include explanations or Markdown code fences."
            )
        },
        {
            "role": "user",
            "content": natural_language
        }
    ]

def generate_prolog(model, tokenizer, natural_language):
    messages = build_messages(natural_language)

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(
        text,
        return_tensors="pt"
    ).to(model.device)

    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    generated_ids = output_ids[
        0,
        inputs["input_ids"].shape[1]:
    ]

    generated_text = tokenizer.decode(
        generated_ids,
        skip_special_tokens=True
    )

    return generated_text.strip()


def save_prediction(file, example, generated_prolog):
    prediction = {
        "id": example["id"],
        "level": example.get("level"),
        "category": example.get("category"),
        "natural_language": example["natural_language"],
        "reference_prolog": example["prolog"],
        "generated_prolog": generated_prolog,
        "template_group": example.get("template_group"),
        "nl_template": example.get("nl_template")
    }

    if "query" in example:
        prediction["query"] = example["query"]

    if "expected_result" in example:
        prediction["expected_result"] = example["expected_result"]

    file.write(json.dumps(prediction, ensure_ascii=False) + "\n")

def main():
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available.")

    print(f"GPU: {torch.cuda.get_device_name(0)}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    test_examples = load_test_set(TEST_PATH)

    print(f"Loaded {len(test_examples)} test examples.")

    tokenizer, model = load_model()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as output_file:

        for index, example in enumerate(test_examples, start=1):

            print(
                f"[{index}/{len(test_examples)}] "
                f"{example['id']}"
            )

            try:
                generated_prolog = generate_prolog(
                    model,
                    tokenizer,
                    example["natural_language"]
                )

            except Exception as error:
                print(f"Error on {example['id']}: {error}")
                generated_prolog = ""

            save_prediction(
                output_file,
                example,
                generated_prolog
            )

            output_file.flush()

    print()
    print("Baseline generation complete.")
    print(f"Predictions saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()