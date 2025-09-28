import os
import torch
import re
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig, AutoModelForSequenceClassification
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from sentence_transformers import CrossEncoder

# --- Data Formatting Helpers ---
def format_question_text(example):
    question = example['question']
    options_dict = {key.upper(): choice for key, choice in example['options'].items()}
    options_str = "\n".join([f"{key}: {value}" for key, value in options_dict.items()])
    return f"{question}\n\nOptions:\n{options_str}"

def get_correct_answer_info(example):
    correct_answer_text = example['answer']
    for key, value in example['options'].items():
        if value == correct_answer_text:
            return key.upper(), correct_answer_text
    return "Unknown", ""

def parse_final_answer(model_response):
    match = re.search(r'the answer is \(([A-E])\)', model_response, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return "No Answer"

def parse_stepback_questions(model_response: str) -> list[str]:
    """
    Parses a model's response to extract numbered questions, supporting
    formats like (1), 1., (1)., 1), and 1).
    
    Args:
        model_response: A string containing the numbered questions.
        
    Returns:
        A list of the extracted question strings.
    """
    # This pattern is updated to include `|d+).?` to handle the new formats.
    pattern = r"^\s*(?:\(\d+\)\.?|\d+\.|\d+\)\.?)\s*(.*)"
    
    questions = re.findall(pattern, model_response, re.MULTILINE)
    
    return [q.strip() for q in questions]

# --- Reranking Helpers ---
def sentence_transformer_scores(query, docs, ce_model):
    """ Calculates similarity score between query and docs."""
    if not docs:
        return []
    pairs = [[query, d.page_content] for d in docs]
    scores = ce_model.predict(pairs)
    return scores

def raw_transformer_scores(query, docs, ce_model, ce_tokenizer, ce_device):
    """ Calculates similarity score between query and docs."""
    if not docs:
        return []
    pairs = [[query, d.page_content] for d in docs]
    with torch.no_grad():
        encoded = ce_tokenizer(
            pairs,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=512
        ).to(ce_device)
        logits = ce_model(**encoded).logits.squeeze(dim=1)
        return logits.detach().cpu().tolist()

# --- Prompt Building ---
def create_simple_user_message(context: str, question: str) -> str:
    """Creates a simple user message with context and the question."""
    return (
        f"Retrieved context:\n{context}\n\n"
        f"Question:\n{question}"
    )

def create_reasoning_user_message(context: str, question: str) -> str:
    """Creates a user message that asks the model to reason about context relevance first."""
    return (
        "Retrieved context (may contain irrelevant material): "
        f"{context}\n\n"
        "For each retrieved chunk, first, label it Relevant/Irrelevant with a one-line reason. "
        "Then, using only the Relevant chunks (if any) and/or your own knowledge, answer the following question. "
        "Provide your final answer as instructed in the system prompt.\n\n"
        f"Question:\n{question}"
    )

def create_simple_stepback_user_message(specific_question: str):
    """Creates a simple user message that asks the model to generate stepback questions."""
    return (
        f"Specific question:\n{specific_question}"
    )

def build_few_shot_stepback_message(stepback_prompt, question_text, examples):
    """
    Builds a messages list for few-shot step-back prompting,
    following the correct multi-turn chat format.
    """
    # Start the message list with the system prompt
    messages = [{"role": "system", "content": stepback_prompt}]

    # Add each example as a user/assistant turn
    for ex in examples:
        messages.append({"role": "user", "content": ex['specific']})
        messages.append({"role": "assistant", "content": ex['step_back']})

    # Add the final user query
    messages.append({"role": "user", "content": question_text})

    return messages

# --- Model Loading ---
def load_slm_and_tokenizer(model_name):
    """Loads the base model and tokenizer."""
    print("Loading base model...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto"
    )
    print("Base model loaded.")
    return model, tokenizer

def load_sentence_transformer_reranker(encoder):
    """Loads encoder model."""
    print("Loading encoder model...")

    ce_model = CrossEncoder(encoder, device='cuda' if torch.cuda.is_available() else 'cpu')

    print("Cross encoder model loaded.")
    return ce_model

def load_raw_transformer_reranker(encoder):
    """Loads encoder model."""
    print("Loading Cross-Encoder for re-ranking...")
    ce_tokenizer = AutoTokenizer.from_pretrained(encoder, use_fast=True)
    ce_model = AutoModelForSequenceClassification.from_pretrained(encoder)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    ce_model.to(device)
    ce_model.eval()
    print("Cross-Encoder loaded.")
    return ce_model, ce_tokenizer, device

def create_slm_pipeline(model, tokenizer):
    """Creates a pipeline for inference."""
    return pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=1024,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )

def get_retriever(db_path, embedding_model):
    """Loads the retriever."""
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    return FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)