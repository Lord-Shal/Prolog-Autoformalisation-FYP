# Training Small Language Models for Autoformalization to Prolog

Final Year Project for the BSc Computer Science (Artificial Intelligence) programme at Royal Holloway, University of London.

## Overview

This project investigates whether a small language model can be fine-tuned to translate natural-language reasoning statements into executable Prolog programs.

Large language models can perform well on natural-language reasoning tasks but may produce logically inconsistent answers or hallucinated reasoning steps. Autoformalization provides an alternative approach by translating natural-language statements into a symbolic representation that can subsequently be checked and executed by a formal reasoning system.

This project uses **Qwen2.5-1.5B-Instruct** as the base small language model and **SWI-Prolog** as the symbolic execution environment. The model is fine-tuned using QLoRA to generate Prolog from natural-language inputs and evaluated according to exact-match accuracy, syntax validity, executability, and reasoning correctness.

## Project Objectives

The main objectives of the project are to:

* Construct a controlled dataset of natural-language and Prolog pairs.
* Fine-tune a small language model for natural-language-to-Prolog translation.
* Evaluate generated Prolog for syntactic validity and executability.
* Evaluate whether generated programs produce the expected logical conclusions.
* Analyse common translation errors.
* Investigate whether targeted refinement data can improve model performance.

## Dataset

A custom dataset of **2,000 natural-language/Prolog pairs** was generated for the project.

The dataset contains four levels of increasing complexity:

| Level     | Category              |  Examples |
| --------- | --------------------- | --------: |
| 1         | Facts                 |       500 |
| 2         | Simple rules          |       600 |
| 3         | Multi-condition rules |       500 |
| 4         | Reasoning problems    |       400 |
| **Total** |                       | **2,000** |

Examples include simple facts:

```text
Natural language:
Ash is a cat.

Prolog:
cat(ash).
```

Rules:

```text
Natural language:
Every cat is an animal.

Prolog:
animal(X) :- cat(X).
```

and more complex constructions involving conjunction, inequality and negation-as-failure.

Reasoning examples additionally contain a Prolog query and an expected Boolean result, allowing the generated program to be evaluated through execution.

### Dataset Split

A group-aware **80/10/10 train-validation-test split** was used:

| Split      | Examples |
| ---------- | -------: |
| Training   |    1,597 |
| Validation |      204 |
| Test       |      199 |

The split uses a fixed random seed:

```text
4242564
```

Examples derived from the same template group are kept within the same split to reduce direct leakage between closely related generated examples.

## Model

The base model used for the experiments is:

**Qwen/Qwen2.5-1.5B-Instruct**

The model was fine-tuned using **QLoRA**, allowing parameter-efficient training using 4-bit quantisation.

The primary training configuration used:

```text
Base model: Qwen/Qwen2.5-1.5B-Instruct
Training examples: 1,597
Validation examples: 204
Epochs: 3
Batch size: 2
Random seed: 4242564
Quantisation: 4-bit
Fine-tuning method: QLoRA / LoRA
```

The model was instructed to return only Prolog code without additional explanations or Markdown formatting.

## Experiments

Three model configurations were evaluated.

### Baseline

The original Qwen2.5-1.5B-Instruct model was evaluated without task-specific fine-tuning.

### Fine-Tuned v1

The model was fine-tuned on the original training dataset using QLoRA.

### Fine-Tuned v2

Error analysis was performed on the first fine-tuned model. A targeted refinement dataset of **250 additional examples** was then constructed to address recurring translation errors.

A second model was trained using the original training data together with this refinement data.

## Results

All models were evaluated using the same held-out **199-example test set**.

| Model             | Exact Match | Syntax Valid |  Executable | Reasoning Correct |
| ----------------- | ----------: | -----------: | ----------: | ----------------: |
| Baseline          |       0.50% |       39.70% |      39.70% |            14.63% |
| Fine-Tuned v1     |      81.41% |      100.00% |     100.00% |            87.80% |
| **Fine-Tuned v2** |  **87.94%** |  **100.00%** | **100.00%** |       **100.00%** |

Fine-tuning therefore produced a substantial improvement over the untuned baseline.

The final model generated syntactically valid and executable Prolog for every test example and achieved 100% correctness on the reasoning subset.

Exact-match accuracy remained lower because some generated programs differed lexically or structurally from the reference representation. Multi-condition rules were the most challenging category.

### Final Model Performance by Category

| Category              | Exact Match |
| --------------------- | ----------: |
| Facts                 |      86.79% |
| Simple rules          |     100.00% |
| Multi-condition rules |      62.22% |
| Reasoning             |     100.00% |

The remaining errors primarily involved predicate substitutions and structural differences in more complex rules.

## Evaluation Metrics

Four primary metrics are used.

### Exact Match

Checks whether the generated Prolog exactly matches the reference Prolog after normalisation.

### Syntax Validity

Checks whether the generated program is accepted as syntactically valid Prolog by SWI-Prolog.

### Executability

Checks whether the generated program can successfully be loaded and executed using SWI-Prolog.

### Reasoning Correctness

For reasoning examples, the generated program is executed with the associated query and the result is compared with the expected Boolean answer.

This allows the evaluation to distinguish between textual differences and errors that affect actual symbolic reasoning.

## Repository Structure

```text
.
├── dataset/
│   ├── raw/
│   ├── processed/
│   └── splits/
│
├── src/
│   ├── dataset/
│   ├── evaluation/
│   ├── inference/
│   ├── prolog/
│   └── training/
│
├── models/
│
├── results/
│   ├── baseline/
│   ├── finetuned/
│   ├── finetuned_v2/
│   └── figures/
│
├── dissertation/
│
├── requirements.txt
└── README.md
```

## Requirements

The project was developed using Python 3.12 and an NVIDIA CUDA-capable GPU.

Major Python dependencies include:

```text
torch==2.13.0+cu126
transformers==5.15.0
datasets==5.0.1
accelerate==1.14.0
peft==0.20.0
trl==1.10.0
bitsandbytes==0.50.1
```

The complete Python environment is provided in `requirements.txt`.

### External Dependency

**SWI-Prolog** is required for dataset validation and evaluation.

SWI-Prolog must be installed separately and the `swipl` executable must be available from the command line.

The experiments were performed using an NVIDIA GeForce RTX 4070 with CUDA support.

## Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd Prolog-Autoformalisation-FYP
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell, activate it using:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Install SWI-Prolog separately and confirm that it is accessible:

```bash
swipl --version
```

## Running the Project

The project is divided into separate stages for dataset construction, training, inference and evaluation.

### Dataset

Dataset-related scripts are located in:

```text
src/dataset/
```

The frozen train, validation and test sets used for the final experiments are stored in:

```text
dataset/splits/
```

The existing frozen splits should be used when reproducing the reported experiments rather than regenerating the split.

### Training

Fine-tuning scripts are located in:

```text
src/training/
```

The training process uses QLoRA and requires a CUDA-capable GPU for the configuration used in the project.

### Inference

Inference scripts are located in:

```text
src/inference/
```

These generate Prolog predictions for the held-out test set.

### Evaluation

Evaluation scripts are located in:

```text
src/evaluation/
```

Evaluation uses SWI-Prolog to test generated programs for syntax validity, executability and reasoning correctness.

Results from the experiments are stored under:

```text
results/
```

## Reproducibility

The project uses the fixed random seed:

```text
4242564
```

The final dataset split is frozen and included in the repository.

To reproduce the reported results, use the existing files under `dataset/splits/` rather than creating a new random split.

Exact package versions for the final development environment are recorded in `requirements.txt`.

## Limitations

The dataset was deliberately controlled and uses a restricted collection of predicates and linguistic templates. Performance therefore does not necessarily represent the model's ability to formalise unrestricted natural language.

Exact-match evaluation is also strict and may classify semantically equivalent Prolog programs as incorrect when their textual or structural representations differ.

More complex multi-condition rules remained the primary source of exact-match errors in the final model.

## Future Work

Possible extensions include:

* Expanding the dataset with more diverse natural-language expressions.
* Introducing more complex Prolog structures and reasoning tasks.
* Evaluating additional small language models.
* Developing semantic equivalence measures beyond exact string matching.
* Using automated Prolog execution feedback during training or iterative refinement.
* Evaluating generalisation on external natural-language reasoning datasets.

## Dissertation

A detailed description of the project methodology, experiments, results and analysis is provided in the accompanying dissertation:

**Training Small Language Models for Autoformalization to Prolog**

## Acknowledgements

This project was completed as a Final Year Project at Royal Holloway, University of London.
