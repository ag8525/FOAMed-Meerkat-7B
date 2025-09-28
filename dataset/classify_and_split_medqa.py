# -*- coding: utf-8 -*-
"""
This script performs a classification and splitting workflow for the
MedQA dataset to isolate questions relevant to Emergency Medicine (EM).

The process is as follows:
1.  Reads MedQA questions from a source .jsonl file.
2.  Uses the OpenAI GPT-4o model to classify each question as EM-relevant or not.
3.  Separates the questions into two lists in memory based on the classification.
4.  Saves the results directly into two final .jsonl files: one for EM
    questions and one for all other questions.

"""

import os
import json
import time
from typing import List, Dict, Any

from openai import OpenAI
from tqdm import tqdm

# --- Configuration ---
INPUT_FILE = "data_clean/questions/US/test.jsonl"
EM_OUTPUT_FILE = "data_clean/questions/US/test_em_gpt_filtered.jsonl"
OTHER_OUTPUT_FILE = "medqa_other_questions.jsonl"
GPT_MODEL = "gpt-4o"

# Initialize the OpenAI client (ensure OPENAI_API_KEY is set in your environment)
try:
    CLIENT = OpenAI()
except openai.OpenAIError as e:
    print(f"Error: OpenAI client could not be initialized. {e}")
    CLIENT = None
# ---------------------

def create_classification_prompt(question_text: str) -> str:
    """
    Creates a robust prompt to classify a medical question for EM relevance.

    Args:
        question_text: The text of the medical question to be classified.

    Returns:
        A formatted prompt string for the GPT-4o model.
    """
    return f"""
    You are an expert medical classifier. Your task is to determine if a given medical question is relevant to the specialty of Emergency Medicine.

    Emergency Medicine focuses on the diagnosis and treatment of acute illnesses and injuries that require immediate medical attention. This includes topics like trauma, cardiac arrest, stroke, sepsis, respiratory distress, acute pain, and other life-threatening conditions. It does NOT typically involve chronic disease management, routine follow-ups, or highly specialized, non-acute surgical planning.

    Analyze the following question and determine if it falls most appropriately within the scope of Emergency Medicine as opposed to another specialty.

    [Question]:
    {question_text}

    Is this question relevant to Emergency Medicine? Respond with only the word "True" or "False".
    """

def save_list_to_jsonl(data_list: List[Dict[str, Any]], filepath: str):
    """Saves a list of dictionaries to a .jsonl file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in data_list:
                f.write(json.dumps(item) + '\n')
        print(f"Saved {len(data_list)} questions to '{filepath}'")
    except IOError as e:
        print(f"Error saving file {filepath}: {e}")

def main():
    """
    Main function to orchestrate the classification and splitting of MedQA questions.
    """
    if not CLIENT:
        print("Exiting script because OpenAI client failed to initialize.")
        return

    # --- 1. Load the dataset ---
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            dataset = [json.loads(line) for line in f]
        print(f"Successfully loaded {len(dataset)} questions from '{INPUT_FILE}'.")
    except FileNotFoundError:
        print(f"Error: The file '{INPUT_FILE}' was not found.")
        return

    # --- 2. Main Processing Loop ---
    em_questions: List[Dict[str, Any]] = []
    other_questions: List[Dict[str, Any]] = []
    
    for example in tqdm(dataset, desc="Classifying questions"):
        question_text = example.get('question', '')
        if not question_text:
            continue

        try:
            prompt = create_classification_prompt(question_text)
            
            response = CLIENT.chat.completions.create(
                model=GPT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=5
            )
            
            is_em_text = response.choices[0].message.content.strip().lower()
            
            # Append the original question object to the appropriate list
            if "true" in is_em_text:
                em_questions.append(example)
            else:
                other_questions.append(example)
            
            time.sleep(1) # Be respectful to the API

        except Exception as e:
            print(f"\nAn error occurred: {e}. Stopping classification.")
            # Optional: Save partial progress here if needed
            break

    # --- 3. Save Final Results ---
    if em_questions:
        save_list_to_jsonl(em_questions, EM_OUTPUT_FILE)
    
    if other_questions:
        save_list_to_jsonl(other_questions, OTHER_OUTPUT_FILE)

    print(f"\nClassification complete.")

if __name__ == "__main__":
    main()