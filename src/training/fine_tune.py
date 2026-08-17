import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from trl import SFTConfig, SFTTrainer

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

TRAIN_PATH = Path("dataset/splits/train.jsonl")
VALIDATION_PATH = Path("dataset/splits/validation.jsonl")

OUTPUT_DIR = Path("models/qwen2.5-1.5b-prolog-lora")
CHECKPOINT_DIR = Path("models/checkpoints/qwen2.5-1.5b-prolog")

SEED = 4242564

SYSTEM_PROMPT = (
    "Translate natural language into Prolog."
    "Return only the Prolog code."
    "Do not include explanations or Markdown code fences."
)

def load_jsonl(path):
    examples = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                examples.append(json.loads(line))

    return examples

def build_training_text(example, tokenizer):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": example["natural_language"]
        },
        {
            "role": "assistant",
            "content": example["prolog"]
        }
    ]

    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )

def prepare_dataset(examples, tokenizer):
    records = []

    for example in examples:
        text = build_training_text(
            example,
            tokenizer
        )

        records.append({
            "text": text,
            "id": example["id"],
            "category": example.get("category"),
            "level": example.get("level")
        })

    return Dataset.from_list(records)

def main():
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is unavailable. "
            "Fine-tuning should run on the RTX 4070."
        )

    print("===== HARDWARE =====")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        "VRAM:",
        round(
            torch.cuda.get_device_properties(0).total_memory
            / 1024**3,
            2
        ),
        "GB"
    )

    print()
    print("===== DATASET =====")

    train_examples = load_jsonl(TRAIN_PATH)
    validation_examples = load_jsonl(
        VALIDATION_PATH
    )

    print(
        f"Training examples: {len(train_examples)}"
    )
    print(
        f"Validation examples: "
        f"{len(validation_examples)}"
    )

    print()
    print("===== TOKENIZER =====")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    tokenizer.padding_side = "right"

    train_dataset = prepare_dataset(
        train_examples,
        tokenizer
    )

    validation_dataset = prepare_dataset(
        validation_examples,
        tokenizer
    )

    print("Datasets formatted.")

    print()
    print("===== QUANTISATION =====")

    compute_dtype = torch.float16

    quantisation_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=True
    )

    print()
    print("===== MODEL =====")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=quantisation_config
    )

    model.config.use_cache = False

    model = prepare_model_for_kbit_training(
        model
    )

    print("Model loaded in 4-bit.")

    print()
    print("===== LORA =====")

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",

        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj"
        ]
    )

    print()
    print("===== TRAINING CONFIG =====")

    training_args = SFTConfig(
        output_dir=str(CHECKPOINT_DIR),

        num_train_epochs=3,

        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,

        gradient_accumulation_steps=4,

        learning_rate=2e-4,

        max_length=512,

        logging_steps=10,

        eval_strategy="epoch",
        save_strategy="epoch",

        save_total_limit=2,

        load_best_model_at_end=True,

        fp16=False,
        bf16=False,

        gradient_checkpointing=True,

        report_to="none",

        seed=SEED,
        data_seed=SEED,

        dataset_text_field="text"
    )

    print("Epochs: 3")
    print("Batch size: 2")
    print("Gradient accumulation: 4")
    print("Effective batch size: 8")
    print("Learning rate: 2e-4")
    print("LoRA rank: 16")
    print("LoRA alpha: 32")
    print("Maximum sequence length: 512")
    print(f"Seed: {SEED}")

    print()
    print("===== TRAINER =====")

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        peft_config=peft_config,
        processing_class=tokenizer
    )

    print()
    print("===== TRAINING =====")

    print("Accelerate precision:", trainer.accelerator.mixed_precision)
    print("CUDA BF16 supported:", torch.cuda.is_bf16_supported())

    trainer.train()

    print()
    print("===== SAVING =====")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    trainer.model.save_pretrained(
        OUTPUT_DIR
    )

    tokenizer.save_pretrained(
        OUTPUT_DIR
    )

    print(
        f"LoRA adapter saved to: {OUTPUT_DIR}"
    )

    print()
    print("Fine-tuning complete.")

if __name__ == "__main__":
    main()