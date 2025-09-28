# The Bottom Line (TBL) Data Processing Pipeline

Transform **The Bottom Line** medical trial summaries into clean, standardized Markdown suitable for a clinical AI knowledge base and Retrieval-Augmented Generation (RAG) workflows.

> **Note:** Before running this pipeline, please complete the one-time setup instructions in the main `README.md` file located in the parent `data/` folder.

> **Environment & setup:** See [`../README.md`](../README.md).

---

## Table of Contents
1. [Overview](#overview)
2. [Manual Curation](#manual-curation)
3. [Pipeline Stages](#pipeline-stages)
4. [Environment & setup](#environment--setup)
5. [Usage](#usage)
6. [Output](#output)

---

## Overview

This repository provides a multi-step pipeline that:
- Scrapes **The Bottom Line** website for [Emergency Medicine–relevant trial summaries](https://www.thebottomline.org.uk/category/summaries/em/).
- Converts raw web content into Markdown with YAML front matter.
- Applies predictable, rule-based cleaning passes.
- Uses GPT-assisted steps for higher-level normalization and summarization.
- Produces ingestion-ready Markdown for RAG and knowledge-base use.

This approach blends deterministic scripts (for reproducibility) with model-assisted steps (for structure and concision).

---

## Manual Curation & QA

Automation handles most of the processing, but targeted manual review ensures clinical completeness and fidelity.

- **Content selection:** Only clinically relevant TBL trial summaries are included.
- **Post-GPT quality assurance:** After model-assisted steps, files are reviewed to:
  - Restore any clinically important content inadvertently removed.
  - Remove residual non-clinical or noisy text not fully stripped by automation.
- **Topic Splitting:** In cases where a single file contained information on multiple distinct topics, the file was manually split into separate, topic-specific files. This ensures each document maintains a singular clinical focus. 

This hybrid workflow addresses the limits of purely automated processing and preserves clinically critical details.

---

## Pipeline Stages

Run the following Python scripts **in order**:

1. **`tbl_scraper.py`**  
   Scrapes The Bottom Line for EM trial summaries and writes raw text with a simple metadata header.  
   **Output:** Raw `.txt` files.

2. **`tbl_step1_cleaning.py`** *(GPT-assisted)*  
   Applies initial, consistent formatting via few-shot prompting to create semi-structured text.  
   **Output:** Semi-structured text files.

3. **`tbl_step2_cleaning.py`** *(GPT-assisted)*  
   Reformats content into Markdown with YAML front matter.  
   **Output:** Clean `.md` files with a placeholder summary.

4. **`tbl_step3_cleaning.py`** *(GPT-assisted)*  
   Generates a dense clinical summary paragraph and inserts it into the YAML `summary` field.  
   **Output:** Summarized Markdown files.

5. **`tbl_step4_cleaning.py`** *(Rule-based)*  
   Validates and repairs YAML, removing common GPT artifacts (e.g., ```yaml code fences).  
   **Output:** YAML-valid Markdown files.

6. **`tbl_step5_cleaning.py`**  
   Renames processed files to `tbl-{study_name}.md`; on conflicts, moves clashing files to a review folder.  
   **Output:** Canonically named Markdown files.

7. **`tbl_step6_cleaning.py`**  
   Standardizes headers, replacing **Question/Answer** with **Point**.  
   **Output:** Uniform header terminology.

8. **`tbl_step7_cleaning.py`**  
   Unifies content by keeping essential sections only—**Summary**, **Clinical Point**, **Background**, **Bottom Line**—and ordering them consistently.  
   **Output:** Final, standardized Markdown.

---

## Environment & setup

> See [`../README.md`](../README.md).

---

## Usage

Run each stage sequentially, ensuring each completes successfully before proceeding.

```bash
python tbl_scraper.py
python tbl_step1_cleaning.py
python tbl_step2_cleaning.py
python tbl_step3_cleaning.py
python tbl_step4_cleaning.py
python tbl_step5_cleaning.py
python tbl_step6_cleaning.py
python tbl_step7_cleaning.py
```

---

## Output

Final, cleaned, and standardized TBL Markdown files are written to:
```
step7_cleaned_articles/
```

