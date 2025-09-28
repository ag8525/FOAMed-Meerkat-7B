# MedQA Emergency Medicine (EM) Filtering Pipeline

Create a high-quality **Emergency Medicine–focused** subset of the MedQA USMLE test set using a single, validated classification script.

---

## Table of Contents
1. [Overview](#overview)
2. [Validation Summary](#validation-summary)
3. [Environment](#environment)
4. [Folder Layout](#folder-layout)
5. [Input Preparation](#input-preparation)
6. [Usage](#usage)
7. [Outputs](#outputs)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This pipeline programmatically classifies questions from the official MedQA **USMLE test set** to isolate those relevant to Emergency Medicine (EM). The workflow is implemented in one script:

- **`classify_and_split_medqa.py`**
  1) **Read** the official `test.jsonl` file  
  2) **Classify** each question as EM / non-EM via a GPT-4o prompt defining EM scope  
  3) **Split** into two `.jsonl` files: EM-relevant vs. all other questions

---

## Validation Summary

A board-certified Emergency Medicine physician manually reviewed a **30-question** sample from the initial run and found the GPT-4o classifications to be **highly accurate**. The full test set (˜1200 questions) was then processed, yielding **379** EM-relevant questions. *(See Outputs for file names.)*

---

## Environment

Use the **same Python virtual environment** as the other data pipelines (TBL, CRACKCast, SGEM). For shared setup (creating a venv, installing dependencies, configuring `OPENAI_API_KEY`), see the repository’s **common setup guide** (e.g., `raw_data/README.md`).

---

## Folder Layout

The script expects the MedQA dataset to be present under your project root, e.g.:

```
FOAMed-Meerkat-7B/
+- dataset/
¦  +- classify_and_split_medqa.py    # run this script from here
¦  +- data_clean/
¦     +- questions/
¦        +- US/
¦           +- test.jsonl            # input file (official MedQA test set)
¦           +- ...
+- (other project files)
```

---

## Input Preparation

1.  **Download the MedQA Dataset**
    Download the official dataset from the link provided in the [MedQA GitHub repository](https://github.com/jind11/MedQA?tab=readme-ov-file), or use the direct [Google Drive link](https://drive.google.com/file/d/1ImYUSLk9JbgHXOemfvyiDiirluZHPeQw/view). Once downloaded, unzip the file.

2.  **Place the Dataset Folder**
    After unzipping, place the `dataset` folder at the root of your `FOAMed-Meerkat-7B` project directory. The script expects the input file to be at the following path:
    ```
    FOAMed-Meerkat-7B/dataset/data_clean/questions/US/test.jsonl
    ```
---

## Usage

Activate your environment, navigate to the folder containing the script, and run:

```bash
python classify_and_split_medqa.py
```

---

## Output

The script automatically creates and places two `.jsonl` output files in their final project directories.

* **`test_em_gpt_filtered.jsonl`**
    * **Content**: Contains all questions classified as relevant to Emergency Medicine. This is the primary output for downstream tasks.
    * **Location**: Saved directly to `FOAMed-Meerkat-7B/dataset/data_clean/questions/US/`.

* **`medqa_other_questions.jsonl`**
    * **Content**: Contains all remaining, non-EM questions from the dataset.
    * **Location**: Saved directly to `FOAMed-Meerkat-7B/dataset/`.

---

## Troubleshooting

- **OPENAI_API_KEY not set:** Ensure it’s available to the current shell (PowerShell: `$env:OPENAI_API_KEY="..."`; bash: `export OPENAI_API_KEY="..."`).  
- **Path errors for `test.jsonl`:** Confirm the input file path matches the expected layout.  
- **Rate limits / API errors:** Add simple retry logic or throttle calls if needed; verify your model and billing configuration.
