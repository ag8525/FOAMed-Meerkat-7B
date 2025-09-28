> **Disclaimer:** All code, models, and outputs in this repository are intended **only** for research purposes. They are **not validated for clinical, diagnostic, or real-world operational use** and should not be relied upon in any setting involving patient care or safety-critical 

# Clinical Content Data Processing Pipelines

Clean and standardize Emergency Medicine content from three sources into **Markdown** suitable for a clinical AI knowledge base and **Retrieval-Augmented Generation (RAG)** workflows.

---

## Table of Contents
1. [Sources & Pipelines](#sources--pipelines)
2. [Folder Layout](#folder-layout)
3. [Unified Environment Setup](#unified-environment-setup)
4. [Configuration (API Keys)](#configuration-api-keys)
5. [Running the Pipelines](#running-the-pipelines)

---

## Sources & Pipelines

This repository contains **three pipelines**, one per source:

- **The Bottom Line (TBL):** Medical trial summaries scraped from the TBL website.  
- **CRACKCast:** Show notes extracted from PDF files.  
- **SGEM (Skeptics’ Guide to Emergency Medicine):** Show notes scraped from the SGEM website.

Each pipeline has its own folder and README describing **inputs**, **script order**, and **outputs**.

---

## Folder Layout

```text
data/
+- README_SETUP.md          # Shared environment & setup (centralized)
+- requirements.txt         # Shared dependency list
+- requirements.lock.txt    # Exact, pinned versions (generated)
+- tbl/                     # TBL pipeline + README.md
+- crackcast/               # CRACKCast pipeline + README.md
+- sgem/                    # SGEM pipeline + README.md
```

---

## Unified Environment Setup

Run **all three pipelines from a single Python virtual environment**.

### 1) Create & activate the environment

**macOS/Linux (bash):**
```bash
python -m venv clinical-data-env
source clinical-data-env/bin/activate
python -m pip install --upgrade pip
```

**Windows (PowerShell):**
```powershell
python -m venv clinical-data-env
.\clinical-data-env\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2) Install dependencies

**Exact reproduction (recommended):**
```bash
pip install -r requirements.lock.txt
```

**For development (latest compatible):**
```bash
pip install -r requirements.txt
```

**Playwright browsers (required for the TBL scraper):**
```bash
playwright install
```

---

## Configuration (API Keys)

Set your OpenAI API key for pipelines that use GPT-assisted steps.

**macOS/Linux (bash):**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-api-key-here"     # current session only
# or persist for future sessions:
setx OPENAI_API_KEY "your-api-key-here"
```

---

## Running the Pipelines

Run the scripts **inside each folder** and follow that folder’s README for input preparation and script order:

- `tbl/README.md`
- `crackcast/README.md`
- `sgem/README.md`

---
