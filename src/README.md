# FOAMed-Meerkat-7B — RAG Pipelines (`src`)

Welcome to **FOAMed-Meerkat-7B**.

This folder contained the code I used to build vector stores and run multiple Retrieval-Augmented Generation (RAG) variants with the Meerkat-7B model, available on [Hugging Face](https://huggingface.co/dmis-lab/meerkat-7b-v1.0) and described in the May 2025 paper, “[Small Language Models Learn Enhanced Reasoning Skills from Medical Textbooks](https://www.nature.com/articles/s41746-025-01653-8).”

## Contents

- `create_vectorstore.py` — builds a FAISS vector store from Markdown sources using either fixed-size splitting or Markdown-aware splitting.
- `experiment.py` — runs evaluations in four modes: `base`, `naive_rag`, `rerank_rag`, and `stepback_rag`; saves per-question results and accuracy.
- `utils.py` — helpers for loading models, building pipelines, formatting questions, parsing model outputs, retrieval, and cross-encoder reranking.
- `prompts.py` — system prompts for base, RAG, and step-back question generation, plus few-shot examples for the step-back variant.

## Data Preparation & Provenance (outside `src/`)

The **raw data cleaning** and **EM-MedQA dataset generation** steps were performed using a combination of GPT-4o calls and manual editing of source files. Because these steps are not fully deterministic, I did not include them in `src/`. Instead:

- See `raw_data/README.md` for a description of the raw-data cleanup pipeline, including environment details and scripts used.
- See `dataset/README.md` for how the **EM-MedQA** dataset was prepared from the cleaned sources, including the exact prompts, heuristics, and validation steps.
- The environments and runnable code for these phases live in the respective folders (`raw_data/` and `dataset/`).

## Quick Start

```bash
# 0) (Recommended) Create and activate a fresh env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 1) Build a Vector Store

Your Markdown sources should live under `data/` at the project root (the script auto-detects the path). Choose a chunking strategy:

```bash
# Strategy A: fixed-size chunks
python src/create_vectorstore.py --strategy size --chunk_size 1024 --chunk_overlap 100

# Strategy B: markdown-aware chunks (split on headers, then size)
python src/create_vectorstore.py --strategy markdown --chunk_size 1024 --chunk_overlap 100
```

**Outputs:**  
- `norm_size_vector_store/` or `norm_md_vector_store/` at the project root (FAISS index with PubMedBERT embeddings).

### 2) Run Experiments

All runs write results into `--output_dir/<auto_named_experiment>/results_<name>.csv`.

#### Base (no retrieval)
```bash
python src/experiment.py   --mode base   --output_dir results/   --dataset_path dataset/data_clean/questions/US/test_em_gpt_filtered.jsonl   --batch_size 5 --limit 100
```

#### Naïve RAG (retrieval + threshold)
```bash
python src/experiment.py   --mode naive_rag   --output_dir results/   --dataset_path dataset/data_clean/questions/US/test_em_gpt_filtered.jsonl   --vector_db_path norm_md_vector_store/   --threshold 0.8   --retrieval_top_k 10   --user_message_type 1   --batch_size 5 --limit 100
```

#### Rerank RAG (retrieval ? cross-encoder rerank ? top-N)
```bash
python src/experiment.py   --mode rerank_rag   --output_dir results/   --dataset_path dataset/data_clean/questions/US/test_em_gpt_filtered.jsonl   --vector_db_path norm_md_vector_store/   --reranker_model cross-encoder/ms-marco-MiniLM-L-6-v2   --threshold 1.5   --retrieval_top_k 10   --reranker_top_k 2   --user_message_type 1   --batch_size 5 --limit 100
```

#### Step-Back RAG (generate step-back Qs ? retrieve+rerank per SB ? merge ? answer)
```bash
python src/experiment.py   --mode stepback_rag   --output_dir results/   --dataset_path dataset/data_clean/questions/US/test_em_gpt_filtered.jsonl   --vector_db_path norm_md_vector_store/   --reranker_model cross-encoder/ms-marco-MiniLM-L-6-v2   --threshold 1.5   --retrieval_top_k 10   --reranker_top_k 2   --user_message_type 1   --sb_user_message_type 1   --batch_size 5 --limit 100
```

> Tip: `--user_message_type 1` = simple RAG message; `2` = reasoning-style message.  
> For step-back: `--sb_user_message_type 1` = simple; `2` = few-shot.

## What Each Script Does

### `create_vectorstore.py`
- Scans `data/` for `*.md`.
- **`--strategy size`**: plain recursive size splitter.  
- **`--strategy markdown`**: split on Markdown headers first (##/###/####), then size-split long chunks.
- Adds `metadata.filename` for sibling-chunk logic down-stream.
- Builds FAISS with **`NeuML/pubmedbert-base-embeddings`** (normalized) on CPU/GPU.

Key CLI flags:
- `--data_path` (default: project `data/`)
- `--chunk_size`, `--chunk_overlap`
- `--strategy {size, markdown}`

### `experiment.py`
- Loads **Meerkat-7B** with 4-bit NF4 quantization into a non-sampling (`do_sample=False`) text-generation pipeline.
- Modes:
  - `base`: no retrieval; just prompt and answer.
  - `naive_rag`: retrieves `k`, filters by `--threshold` (similarity score), builds context.
  - `rerank_rag`: retrieves `k`, cross-encoder scores each (question, chunk), keeps top-N = threshold.
  - `stepback_rag`: 1st model call generates 1–3 step-back questions; retrieve+rerank per SB Q; dedupe/merge; 2nd model call answers.
- Optional **sibling-chunk** enrichment (source-aware add-ons by filename and target headers) via `--use_sib_chunks` (use only where you intend it).
- Saves a row per question with correctness flag, context filenames, and basic score stats; prints accuracy at the end.

Important flags:
- `--mode {base,naive_rag,rerank_rag,stepback_rag}`
- `--vector_db_path` (`norm_md_vector_store/` or `norm_size_vector_store/`) for all RAG modes
- `--reranker_model` (for `rerank_rag`, `stepback_rag`): e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2` or an NCBI/MedCPT model
- `--threshold`, `--retrieval_top_k`, `--reranker_top_k`
- `--user_message_type` (1 simple, 2 reasoning)
- `--sb_user_message_type` (1 simple, 2 few-shot)
- `--use_sib_chunks` (flag)
- `--batch_size`, `--limit`

### `utils.py`
- **Formatting/parsing**:  
  - `format_question_text()` converts dataset JSON to the MCQ+options text block expected by the prompts.  
  - `parse_final_answer()` extracts the final letter from model output (“the answer is (X) …”).  
  - `parse_stepback_questions()` robustly parses numbered step-back questions from model text.
- **Models**:  
  - `load_slm_and_tokenizer()` loads the base SLM with bitsandbytes 4-bit quantization.  
  - `create_slm_pipeline()` builds a deterministic generation pipeline (`do_sample=False`, `max_new_tokens=1024`).  
  - Cross-encoder loaders for both Sentence-Transformers `CrossEncoder` and raw HF classification models.
- **Retrieval**:  
  - `get_retriever()` loads the FAISS index with PubMedBERT embeddings (normalized).

### `prompts.py`
- **`BASE_PROMPT`**: Standard MCQ solver with required “the answer is (X) …” format.  
- **`RAG_PROMPT`**: Same as base, but explicitly treats retrieved text as optional evidence (ignore if irrelevant).  
- **`STEPBACK_PROMPT`**: Generates 1–3 principle-level prompts with explicit medical “anchor terms” and task keywords; strict numbered output format.  
- **`FEW_SHOT_EXAMPLES`**: optional user/assistant exemplars for step-back generation.

## Outputs

Each run produces:
- `results/<experiment_name>/results_<experiment_name>.csv` with:
  - `question`, `correct_answer_letter`, `model_answer`, `<mode>_is_correct`, `model_full_response`
  - For RAG: `rag_context_used`, `rag_context_filenames`, `max_score`, `mean_score`
  - For step-back: `stepback_questions`

Experiment names are auto-generated from mode + key flags (e.g., `rerank_rag_md_um2_msMarco_15_top2_sibFalse`).

## Requirements

- Python =3.10
- Key packages: `torch`, `transformers`, `bitsandbytes`, `sentence-transformers`, `langchain-community`, `langchain-huggingface`, `langchain-text-splitters`, `faiss-cpu` (or `faiss-gpu`), `unstructured`, `tqdm`, `pandas`, `numpy`.

> GPU is optional but recommended (used when available for embeddings and cross-encoders).

## Reproducibility Notes

- Generation uses `do_sample=False` for deterministic decoding.  
- Retrieval/reranking thresholds (`--threshold`) and top-k settings materially affect context size and accuracy; record them in the experiment name (already handled).  
- If resuming a partially completed run, the script appends to the existing results CSV and skips previously processed questions.

## Troubleshooting

- **“vector_db_path must include 'md' or 'size'.”**  
  Name your FAISS folder `norm_md_vector_store/` or `norm_size_vector_store/` (created by `create_vectorstore.py`).

- **Empty or tiny context**  
  Lower `--threshold` or raise `--retrieval_top_k` (and `--reranker_top_k` for rerank/step-back).

- **Slow reranking**  
  Prefer `cross-encoder/ms-marco-MiniLM-L-6-v2` for speed; ensure GPU is visible.

- **Step-back too noisy**  
  Try `--sb_user_message_type 1` (simple), reduce `--retrieval_top_k`, and avoid `--use_sib_chunks` until needed.
