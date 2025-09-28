import os
import argparse
import pandas as pd
import numpy as np
import json
from tqdm import tqdm
import transformers

from utils import (
    load_slm_and_tokenizer, 
    create_slm_pipeline, 
    format_question_text, 
    get_correct_answer_info, 
    parse_final_answer,
    get_retriever,
    load_sentence_transformer_reranker,
    sentence_transformer_scores,
    load_raw_transformer_reranker,
    raw_transformer_scores,
    create_simple_user_message,
    create_reasoning_user_message,
    create_simple_stepback_user_message,
    build_few_shot_stepback_message,
    parse_stepback_questions
)
from prompts import BASE_PROMPT, RAG_PROMPT, STEPBACK_PROMPT, FEW_SHOT_EXAMPLES

transformers.logging.set_verbosity_error()

# ---------------------- CLI ARGUMENTS ----------------------
parser = argparse.ArgumentParser(description="Run RAG and Baseline experiments.")
parser.add_argument('--mode', type=str, required=True, 
                    choices=['base', 'naive_rag', 'rerank_rag', 'stepback_rag'],
                    help="The evaluation mode to run.")
parser.add_argument('--output_dir', type=str, required=True)
parser.add_argument('--dataset_path', type=str, default="dataset/data_clean/questions/US/test_em_gpt_filtered.jsonl")
parser.add_argument('--vector_db_path', type=str, 
                    help="Path to the FAISS vector DB (Required for all RAG modes).")
parser.add_argument('--reranker_model', type=str, 
                    help="Cross-encoder model name for the reranker (Required for 'rerank_rag' and 'stepback_rag' modes).")
parser.add_argument('--user_message_type', type=int, choices=[1, 2], default=1,
                    help="Type of user message for RAG (1=simple, 2=reasoning).")
parser.add_argument('--sb_user_message_type', type=int, choices=[1, 2], default=1,
                    help="Type of user message for stepback RAG (1=simple, 2=few-shot).")
parser.add_argument('--threshold', type=float, default=0.8,
                    help="Reranker or retrieval score threshold.")
parser.add_argument('--use_sib_chunks', action='store_true',
                    help="Use sibling chunks as final content.")
parser.add_argument('--batch_size', type=int, default=5)
parser.add_argument('--limit', type=int, default=None)
parser.add_argument('--retrieval_top_k', type=int, default=10, 
                    help="Number of initial documents to retrieve.")
parser.add_argument('--reranker_top_k', type=int, default=2,
                    help="Number of documents to keep after reranking.")
args = parser.parse_args()

# ---------------------- VALIDATION LOGIC ----------------------
if args.mode != 'base' and not args.vector_db_path:
    parser.error("--vector_db_path is required for all RAG modes.")
if args.mode in ['rerank_rag', 'stepback_rag'] and not args.reranker_model:
    parser.error("--reranker_model is required for 'rerank_rag' and 'stepback_rag' modes.")

# ---------------------- DYNAMIC CONFIG ------------------------
MODE = args.mode
db_tag = ''
if args.vector_db_path:
    if 'md' in args.vector_db_path:
        db_tag = 'md'
    elif 'size' in args.vector_db_path:
        db_tag = 'size'
    else:
        raise ValueError("vector_db_path must include 'md' or 'size'.")

reranker_tag = ''
if args.reranker_model:
    if 'ms-marco' in args.reranker_model:
        reranker_tag = 'msMarco'
    elif 'MedCPT' in args.reranker_model:
        reranker_tag = 'MedCPT'
    else:
        reranker_tag = 'custom'

# Build experiment name based on mode
if MODE == 'base':
    EXPERIMENT_NAME = "base_model_evaluation"
else:
    user_message_tag = f"um{args.user_message_type}"
    threshold_tag = str(args.threshold).replace('.', '')
    retrieval_top_k_tag = f"top{args.retrieval_top_k}"
    reranker_top_k_tag = f"top{args.reranker_top_k}"
    sib_tag = f"sib{args.use_sib_chunks}"
    if MODE == 'naive_rag':
        EXPERIMENT_NAME = f"{MODE}_{db_tag}_{user_message_tag}_{threshold_tag}_{retrieval_top_k_tag}_{sib_tag}"
    elif MODE == 'rerank_rag':
        EXPERIMENT_NAME = f"{MODE}_{db_tag}_{user_message_tag}_{reranker_tag}_{threshold_tag}_{reranker_top_k_tag}_{sib_tag}"
    else: # MODE == 'stepback_rag'
        sb_user_message_tag = f"sbum{args.sb_user_message_type}"
        EXPERIMENT_NAME = f"{MODE}_{db_tag}_{user_message_tag}_{reranker_tag}_{threshold_tag}_{reranker_top_k_tag}_{sb_user_message_tag}_{sib_tag}"    

OUT_DIR = os.path.join(args.output_dir, EXPERIMENT_NAME)
os.makedirs(OUT_DIR, exist_ok=True)
RESULTS_FILE = os.path.join(OUT_DIR, f"results_{EXPERIMENT_NAME}.csv")

# ------------------ MAIN --------------------------
def main():
    print(f"Starting experiment: {EXPERIMENT_NAME}")
    print(f"Results will be saved to '{RESULTS_FILE}'.")

    # --- Load Models ---
    model, tokenizer = load_slm_and_tokenizer("dmis-lab/meerkat-7b-v1.0")
    pipe = create_slm_pipeline(model, tokenizer)

    retriever, ce_model, ce_tokenizer, ce_device, reranker_type = None, None, None, None, None
    if MODE != 'base':
        retriever = get_retriever(args.vector_db_path, "NeuML/pubmedbert-base-embeddings")
    if MODE in ['rerank_rag', 'stepback_rag']:
        if reranker_tag in ['msMarco', 'custom']: # Default to sentence-transformer for custom
            reranker_type = 'sentence-transformer'
            ce_model = load_sentence_transformer_reranker(args.reranker_model)
        elif reranker_tag == 'MedCPT':
            reranker_type = 'raw-transformer'
            ce_model, ce_tokenizer, ce_device = load_raw_transformer_reranker(args.reranker_model)

    # --- Load Data & Resume Logic ---
    with open(args.dataset_path, "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f]
    if args.limit:
        dataset = dataset[:args.limit]

    processed_q = set()
    if os.path.exists(RESULTS_FILE):
        results_df = pd.read_csv(RESULTS_FILE)
        processed_q = set(results_df['question'].tolist())
        print(f"Found {len(results_df)} existing results. Resuming evaluation.")
    else:
        results_df = pd.DataFrame()

    # --- Main Loop ---
    for i in tqdm(range(0, len(dataset), args.batch_size), desc="Processing Questions"):
        batch_data = [q for q in dataset[i:i + args.batch_size] if format_question_text(q) not in processed_q]
        if not batch_data:
            continue
        
        # --- 1. PREPARE BATCH OF PROMPTS AND METADATA ---
        batch_prompts = []
        batch_metadata = []

        # --- Step-Back Pre-processing (if needed) ---
        if MODE == 'stepback_rag':
            stepback_source_texts = [format_question_text(q) for q in batch_data]
            if args.sb_user_message_type == 1:
                batch_sb_prompts = []
                for text in stepback_source_texts:
                    sb_user_msg = create_simple_stepback_user_message(text)
                    sb_prompt = [{"role": "system", "content": STEPBACK_PROMPT}, {"role": "user", "content": sb_user_msg}]
                    batch_sb_prompts.append(sb_prompt)
            else: # args.sb_user_message_type == 2
                batch_sb_prompts = [build_few_shot_stepback_message(STEPBACK_PROMPT, text, FEW_SHOT_EXAMPLES) for text in stepback_source_texts]
                    
            sb_responses = pipe(batch_sb_prompts, return_full_text=False)
            batch_sb_questions = [parse_stepback_questions(resp[0]["generated_text"]) for resp in sb_responses]
        
        # --- Prepare each item in the batch ---
        for idx, q_data in enumerate(batch_data):
            question_with_options = format_question_text(q_data)
            context_str, scores, filenames = "", [], []

            if MODE == 'base':
                pass # No context needed
            
            else: # For all RAG modes, retrieve context
                if MODE == 'stepback_rag':
                    sb_question_list = batch_sb_questions[idx]
                    all_docs, scores, filenames = [], [], []
                    for sbq in sb_question_list:
                        docs = retriever.similarity_search(sbq, k=args.retrieval_top_k)
                        if reranker_type == 'sentence-transformer':
                            rerank_scores = sentence_transformer_scores(sbq, docs, ce_model)
                        else:
                            rerank_scores = raw_transformer_scores(sbq, docs, ce_model, ce_tokenizer, ce_device)
                        
                        docs_with_scores = sorted(zip(docs, rerank_scores), key=lambda x: x[1], reverse=True)
                        all_docs.extend([doc for doc, score in docs_with_scores if score >= args.threshold][:args.reranker_top_k])
                        scores.extend([score for doc, score in docs_with_scores if score >= args.threshold][:args.reranker_top_k])
                    
                    final_docs = {doc.page_content: doc for doc in all_docs}.values()
                    filenames = list(set([os.path.basename(d.metadata.get("source", "Unknown")) for d in final_docs]))

                elif MODE == 'rerank_rag':
                    docs = retriever.similarity_search(question_with_options, k=args.retrieval_top_k)
                    if reranker_type == 'sentence-transformer':
                        rerank_scores = sentence_transformer_scores(question_with_options, docs, ce_model)
                    else:
                        rerank_scores = raw_transformer_scores(question_with_options, docs, ce_model, ce_tokenizer, ce_device)
                    
                    docs_with_scores = sorted(zip(docs, rerank_scores), key=lambda x: x[1], reverse=True)
                    final_docs = [doc for doc, score in docs_with_scores if score >= args.threshold][:args.reranker_top_k]
                    scores = [score for doc, score in docs_with_scores if score >= args.threshold][:args.reranker_top_k]
                    filenames = [os.path.basename(doc.metadata.get("source", "Unknown")) for doc in final_docs]

                elif MODE == 'naive_rag':
                    docs_with_scores = retriever.similarity_search_with_relevance_scores(question_with_options, k=args.retrieval_top_k)
                    final_docs = [doc for doc, score in docs_with_scores if score >= args.threshold]
                    scores = [score for doc, score in docs_with_scores if score >= args.threshold]
                    filenames = [os.path.basename(doc.metadata.get("source", "Unknown")) for doc in final_docs]

            # --- Source-aware processing to find sibling chunks ---
            if final_docs and sib_tag:
                print(f"\n[INFO] Processing {len(final_docs)} top documents with source-aware logic...")

                # --- Group all documents by filename ONCE ---
                if 'docs_by_filename' not in locals():
                    print("[INFO] Creating a filename-to-document map for efficient lookup...")
                    docs_by_filename = {}
                    for doc_obj in retriever.docstore._dict.values():
                        fname = doc_obj.metadata.get("filename") 
                        if fname:
                            if fname not in docs_by_filename:
                                docs_by_filename[fname] = []
                            docs_by_filename[fname].append(doc_obj)

                processed_docs = []
                for doc in final_docs:
                    # --- Get filename from the current doc's metadata ---
                    current_filename = doc.metadata.get("filename", "") 

                    target_keywords = []
                    if 'sgem' in current_filename:
                        target_keywords = ["summary", "case resolution"]
                    elif 'tbl' in current_filename:
                        target_keywords = ["summary", "bottom line"]

                    if target_keywords:
                        sibling_chunks = docs_by_filename.get(current_filename, [])
                        
                        found_target_sections = []
                        if sibling_chunks:
                            for chunk in sibling_chunks:
                                header = chunk.metadata.get("header", "").lower()
                                if any(keyword in header for keyword in target_keywords):
                                    found_target_sections.append(chunk)
                        
                        if found_target_sections:
                            print(f"[INFO] Found {len(found_target_sections)} target sections for {os.path.basename(current_filename)}.")
                            processed_docs.extend(found_target_sections)
                        else:
                            print(f"[INFO] No target sections found for {os.path.basename(current_filename)}. Keeping original chunk.")
                            processed_docs.append(doc)
                    else:
                        # For other files (like 'cc'), just keep the original retrieved chunk
                        processed_docs.append(doc)

                # De-duplicate the results
                final_context_docs = []
                seen_content = set()
                for doc in processed_docs:
                    if doc.page_content not in seen_content:
                        final_context_docs.append(doc)
                        seen_content.add(doc.page_content)

                print(f"[INFO] Final context size after processing: {len(final_context_docs)} chunks.")
                final_docs = final_context_docs

            context_str = "\n---\n".join([doc.page_content for doc in final_docs])

            # --- Construct Final Prompt ---
            if context_str:
                user_msg = create_simple_user_message(context_str, question_with_options) if args.user_message_type == 1 else create_reasoning_user_message(context_str, question_with_options)
                final_prompt = [{"role": "system", "content": RAG_PROMPT}, {"role": "user", "content": user_msg}]
            else: # Base case or RAG with no retrieved context
                final_prompt = [{"role": "system", "content": BASE_PROMPT}, {"role": "user", "content": question_with_options}]

            batch_prompts.append(final_prompt)
            meta = {"q_data": q_data, "question_text": question_with_options, "context": context_str, "scores": scores, "filenames": filenames}
            if MODE == 'stepback_rag':
                meta["sb_questions"] = "\n".join(batch_sb_questions[idx])
            batch_metadata.append(meta)

        # --- 2. EXECUTE BATCH ---
        if not batch_prompts:
            continue
        final_responses = pipe(batch_prompts, return_full_text=False)

        # --- 3. PROCESS AND SAVE RESULTS ---
        new_results = []
        for response, metadata in zip(final_responses, batch_metadata):
            try:
                text = response[0]["generated_text"]
                correct_letter, _ = get_correct_answer_info(metadata["q_data"])
                parsed = parse_final_answer(text)
                
                result = {
                    "question": metadata["question_text"],
                    "correct_answer_letter": correct_letter,
                    "model_answer": parsed,
                    f"{MODE}_is_correct": (parsed == correct_letter),
                    "model_full_response": text.strip(),
                }
                if MODE != 'base':
                    result.update({
                        "rag_context_used": metadata["context"],
                        "rag_context_filenames": " | ".join(metadata["filenames"]),
                        "max_score": max(metadata["scores"]) if metadata["scores"] else 0.0,
                        "mean_score": np.mean(metadata["scores"]) if metadata["scores"] else 0.0,
                    })
                if MODE == 'stepback_rag':
                    result["stepback_questions"] = metadata["sb_questions"]

                new_results.append(result)
                processed_q.add(metadata["question_text"])
            except Exception as e:
                print(f"Error processing a response: {e}")

        if new_results:
            results_df = pd.concat([results_df, pd.DataFrame(new_results)], ignore_index=True)
            results_df.to_csv(RESULTS_FILE, index=False)
                                            
    print("\n--- Evaluation Complete ---")
    print(f"Total results saved for {len(results_df)} questions to '{RESULTS_FILE}'.")
    if not results_df.empty and f"{MODE}_is_correct" in results_df.columns:
        accuracy = results_df[f"{MODE}_is_correct"].mean() * 100
        print(f"Total Accuracy ({MODE}): {accuracy:.2f}%")

if __name__ == "__main__":
    main()