# CRACKCast Data Processing Pipeline

Transform CRACKCast (CanadiEM) PDF show notes into clean, standardized Markdown suitable for a clinical AI knowledge base and Retrieval-Augmented Generation (RAG) workflows.

> **Note:** Before running this pipeline, please complete the one-time setup instructions in the main `README.md` file located in the parent `data/` folder.

> **Environment & setup:** See [`../README.md`](../README.md).

---

## Table of Contents
1. [Overview](#overview)
2. [Manual Curation](#manual-curation)
3. [Pipeline Stages](#pipeline-stages)
4. [Environment & setup](#environment--setup)
5. [Input Preparation](#input-preparation)
6. [Usage](#usage)
7. [Output](#output)

---

## Overview

This repository provides a multi-step pipeline that:
- Extracts text from CRACKCast PDF show notes
- Converts and structures content to Markdown with YAML front matter
- Applies deterministic, rule-based cleanup
- Uses GPT-assisted steps for higher-level formatting and summarization
- Produces standardized, ingestion-ready Markdown files

The approach combines predictable scripts with model-assisted normalization to preserve clinically meaningful content while removing noise.

---

## Manual Curation

Automation handles most of the work, but targeted manual review was essential to ensure clinical completeness and fidelity:

- **Content Selection:** Only clinically relevant CRACKCast PDF show notes were processed; non-clinical/administrative PDFs were excluded.
- **Post-GPT Quality Assurance:** After GPT-assisted steps, files were manually reviewed to restore any misformatted sections, fix missed headers, and correct extraction garbling when detected.
- **Topic Splitting:** In cases where a single file contained information on multiple distinct topics, the file was manually split into separate, topic-specific files. This ensures each document maintains a singular clinical focus. 

This hybrid approach addresses the limitations of purely automated processing and helps retain clinically critical details.

---

## Pipeline Stages

Run the following Python scripts **in order**:

1. **`cc_pdf_to_txt.py`**  
   Recursively finds PDF files in the source directory, extracts full text content, and saves raw `.txt` files in a flattened output folder.  
   **Output:** Raw `.txt` files with a simple metadata header (topic and original file info).

2. **`cc_step1_cleaning.py`** *(GPT-assisted)*  
   Deep structural reformatting of raw text. Creates YAML front matter and organizes content into standardized Markdown headers (e.g., `## Overview`, `## Core Questions`).  
   **Output:** Cleaned `.md` files; disorganized files are flagged for review.

3. **`cc_step2_cleaning.py`** *(GPT-assisted)*  
   Generates a dense clinical summary paragraph for each file and inserts it into the YAML `summary` field.  
   **Output:** Updated `.md` files with populated summaries.

4. **`cc_step3_cleaning.py`** *(Rule-based)*  
   Validates and repairs YAML front matter, removing GPT artifacts such as code fences (e.g., ```yaml).  
   **Output:** YAML-valid Markdown files.

5. **`cc_step4_cleaning.py`**  
   Renames processed files to `cc-{episode_number}.md` by extracting the first number in the original filename; robustly handles naming conflicts.  
   **Output:** Canonically named Markdown files.

6. **`cc_step5_cleaning.py`**  
   Standardizes headers by replacing **Question/Answer** with **Point** for consistency.  
   **Output:** Uniform header terminology across files.

7. **`cc_step6_cleaning.py`**  
   Moves the summary from the YAML front matter into the document body under a `## Summary` section.  
   **Output:** Final, standardized Markdown layout ready for ingestion.

---

## Environment & setup

> See [`../README.md`](../README.md).

---

## Input Preparation

This pipeline is designed to process the PDF versions of the CRACKCast shownotes.

1. **Download Shownotes:** Obtain the PDF files from the [Official CRACKCast Dropbox Archive](https://www.dropbox.com/scl/fo/921uirtwvi46x4dighpk9/AN6TnZOaYohizHV-jgVvC4I?rlkey=z2tz6186shmt1qm9yqgytl6xh&e=1&dl=0).

2. **Create Input Folder:** At the root of this project, create a folder and name it exactly `CRACKCast_Shownotes`.

3. **Place Files:** Move all the downloaded PDF shownotes into the `CRACKCast_Shownotes` folder.

The first script in the pipeline is configured to automatically scan this directory and its subdirectories to find all the PDFs to be processed.

---

## Usage

Run each stage sequentially from a terminal. Ensure each step finishes successfully before proceeding.

```bash
python cc_pdf_to_txt.py
python cc_step1_cleaning.py
python cc_step2_cleaning.py
python cc_step3_cleaning.py
python cc_step4_cleaning.py
python cc_step5_cleaning.py
python cc_step6_cleaning.py
```

---

## Output

Final, cleaned, and standardized CRACKCast Markdown files are written to:
```
step7_cleaned_shownotes/
```


