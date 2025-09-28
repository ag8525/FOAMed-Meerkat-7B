# SGEM Data Processing Pipeline

Transform SGEM (Skeptics’ Guide to Emergency Medicine) web content into clean, structured Markdown suitable for a clinical AI knowledge base and Retrieval-Augmented Generation (RAG) workflows.

> **Note:** Before running this pipeline, please complete the one-time setup instructions in the main `README.md` file located in the parent `data/` folder.

> **Environment & setup:** See [`../README.md`](../README.md).

---

## Table of Contents
1. [Overview](#overview)
2. [Manual Curation & QA](#manual-curation--qa)
3. [Pipeline Stages](#pipeline-stages)
4. [Environment & setup](#environment--setup)
5. [Input Preparation](#input-preparation)
6. [Usage](#usage)
7. [Quality Check Tool](#quality-check-tool)
8. [Output](#output)

---

## Overview

This repository provides a multi-step pipeline that:
- Scrapes SGEM episode pages
- Converts HTML to Markdown with YAML front matter
- Applies deterministic, rule-based cleaning passes
- Performs GPT-assisted normalization and summarization
- Produces standardized, ingestion-ready Markdown

The approach combines deterministic scripts for predictable cleanup with model-assisted steps for higher-level formatting and summarization.

---

## Manual Curation & QA

While most processing is automated, targeted manual review ensures clinical completeness and fidelity:

- **Content Selection:** Only clinically relevant SGEM episodes are included (interviews, announcements, etc. excluded).
- **Restoring Image-Only Clinical Content:** Algorithms, charts, or tables embedded as images were manually transcribed into the raw files before processing.
- **Post-GPT Quality Assurance:** After GPT-assisted steps, files were reviewed to restore any inadvertently removed clinical content and to remove any residual noise.
- **Topic Splitting:** In cases where a single file contained information on multiple distinct topics, the file was manually split into separate, topic-specific files. This ensures each document maintains a singular clinical focus. 

This hybrid workflow addresses limitations of purely automated pipelines and preserves clinically critical details.

---

## Pipeline Stages

Run the following Python scripts **in order**:

1. **`sgem_url_extractor.py`**  
   Parses locally saved SGEM HTML archive pages and writes a unique, sorted list of episode URLs to `sgem_all_episode_urls.txt`.

2. **`sgem_content_extractor.py`**  
   Reads the URL list, scrapes each episode, extracts metadata, and converts main content to Markdown with YAML front matter.

3. **`sgem_step1_cleaning.py`** ? **`sgem_step6_cleaning.py`** *(Rule-based cleaning)*  
   Deterministic transformations:  
   - **Step 1:** Remove specific WordPress shortcodes and redundant date lines.  
   - **Step 2:** Truncate at boilerplate phrases (e.g., “Keener Kontest”) to drop footers.  
   - **Step 3:** Simplify Markdown links and image tags.  
   - **Step 4:** Remove blockquote formatting (`>`).  
   - **Step 5:** Remove the introductory **Guest Skeptic** section.  
   - **Step 6:** Remove the recurring **Quality Checklist** section.

4. **`sgem_step7_cleaning.py`** *(GPT-assisted)*  
   Standardizes headers, fixes formatting, removes non-medical clutter per a detailed prompt; flags disorganized files for manual review.

5. **`sgem_step8_cleaning.py`** *(GPT-assisted)*  
   Generates a dense clinical summary paragraph and inserts it into the file’s YAML front matter.

6. **`sgem_step9_cleaning.py`**  
   Renames processed files to `sgem-{episode_number}.md`, handling name collisions by appending a counter.

7. **`sgem_step10_cleaning.py`**  
   Standardizes header terms by replacing **Question/Answer** with **Point**.

8. **`sgem_step11_cleaning.py`** *(GPT-assisted)*  
   Unifies file structure by retaining essential sections and summarizing **Background** with GPT, replacing the original text.

9. **`sgem_step12_cleaning.py`**  
   Converts custom bolded headers (e.g., `**Summary:**`) to canonical Markdown H2 headers (e.g., `## Summary`).

---

## Environment & setup

> See [`../README.md`](../README.md).

---

## Input Preparation

This pipeline begins by processing locally saved HTML archive pages from the SGEM website to gather all episode URLs.

1.  **Save Archive Pages**: Manually browse to the [SGEM website](https://thesgem.com/category/podcast/). Save each page of the archives (e.g., `thesgem.com/page/1/`, `page/2/`, etc.) as a separate `.txt` file on your local machine.
    > *Note: At the time this project was created, 51 archive pages were saved and are included in the `sgem` folder for reference.*

2.  **Create Input Folder**: At the root of your project, create a folder and name it exactly `sgemurls`.

3.  **Place Files**: Move all the saved archive files into the `sgemurls` folder.

The first script in the pipeline, `urlextractor.py`, is configured to automatically scan this folder to find all the individual episode URLs to be scraped.

---

## Usage

Run each stage sequentially from a terminal. Ensure each step finishes successfully before proceeding.

```bash
python sgem_url_extractor.py
python sgem_content_extractor.py
python sgem_step1_cleaning.py
python sgem_step2_cleaning.py
python sgem_step3_cleaning.py
python sgem_step4_cleaning.py
python sgem_step5_cleaning.py
python sgem_step6_cleaning.py
python sgem_step7_cleaning.py
python sgem_step8_cleaning.py
python sgem_step9_cleaning.py
python sgem_step10_cleaning.py
python sgem_step11_cleaning.py
python sgem_step12_cleaning.py
```

---

## Quality Check Tool

**`QQ.py`** is an interactive comparator to review differences between any two stages.  
It flags files with significant size reductions and presents a color-coded, line-by-line diff to guide manual QA.

---

## Output

Final, cleaned, and standardized SGEM Markdown files are written to:  
```
sgem_step12_cleaned/
```
