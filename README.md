## Overview

<p align="center">
  <img src="assets/meerkat_foam.png" alt="Dr. Meerkat with foam" width="300">
</p>

<p align="center">
  <!-- Put your image at assets/rag_overview.png (or change the path below) -->
  <img src="assets/rag_overview.png" alt="RAG pipelines overview" width="800">
</p>

**Project aim.** FOAMed-Meerkat-7B evaluated whether a small language model (Meerkat-7B) can answer emergency-medicine MCQs more reliably using Retrieval-Augmented Generation (RAG). I built and compared several pipelines—naïve retrieval, cross-encoder reranking, step-back question generation, and sibling-chunk enrichment—on the EM-MedQA dataset derived from FOAMed sources. The repo includes reproducible code for vector-store creation and batched evaluation; raw data cleaning and EM-MedQA preparation (which involved GPT-4o assistance and some manual steps) are documented separately in `raw_data/` and `dataset/`.
