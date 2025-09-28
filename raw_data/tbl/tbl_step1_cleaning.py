"""
This script processes raw medical trial summaries using the OpenAI GPT-4o model.

It employs a "few-shot learning" approach, where it provides the model with
a few examples of "raw" vs. "cleaned" text. The model then learns the desired
formatting and applies it to new, unseen raw files.

The script includes a retry mechanism with exponential backoff to handle
OpenAI API rate limits gracefully.

Prerequisites:
- An OpenAI API key must be set as an environment variable (`OPENAI_API_KEY`).
- The 'openai' and 'tqdm' libraries must be installed (`pip install openai tqdm`).
- A directory named 'retrieved_articles' must exist with raw text files.
- An 'examples' directory with few-shot example files must be present.
"""

import os
import time
from typing import List

import openai
from openai import RateLimitError
from tqdm import tqdm

# --- Configuration ---
# Set your OpenAI API key in your environment variables
try:
    CLIENT = openai.OpenAI()
except openai.OpenAIError as e:
    print(f"Error: OpenAI client could not be initialized. {e}")
    print("Please ensure your OPENAI_API_KEY is set correctly.")
    CLIENT = None

# Define input and output directories
RAW_FILES_DIR = 'retrieved_articles'
CLEANED_FILES_DIR = 'step1_cleaned_articles'

# Define paths for the few-shot learning examples
FEW_SHOT_RAW_PATHS = [
    'examples/3mg_trial.txt',
    'examples/ttm.txt'
]
FEW_SHOT_CLEAN_PATHS = [
    'examples/3mg_trial_cleaned.txt',
    'examples/ttm_cleaned.txt'
]


def build_few_shot_prompt(raw_paths: List[str], clean_paths: List[str]) -> str:
    """
    Constructs a string of examples for the GPT model.

    Reads pairs of raw and cleaned files and formats them into a single
    prompt string to demonstrate the desired transformation.

    Args:
        raw_paths: A list of file paths to the raw examples.
        clean_paths: A list of file paths to the cleaned examples.

    Returns:
        A formatted string containing all few-shot examples.
    """
    prompt_examples = ""
    for raw_path, clean_path in zip(raw_paths, clean_paths):
        try:
            with open(raw_path, "r", encoding="utf-8") as f:
                raw_content = f.read().strip()
            with open(clean_path, "r", encoding="utf-8") as f:
                clean_content = f.read().strip()
            prompt_examples += (
                f"\n---\nRaw Summary:\n{raw_content}\n\n"
                f"Cleaned Summary:\n{clean_content}\n"
            )
        except FileNotFoundError as e:
            print(f"Error: Example file not found - {e}. Skipping this example.")
            continue
    return prompt_examples


def clean_text_with_gpt(raw_text: str, examples_prompt: str, retries: int = 5) -> str:
    """
    Sends the raw text and examples to GPT-4o for cleaning.

    Includes a retry mechanism with increasing wait times to handle API rate limits.

    Args:
        raw_text: The raw article content to be cleaned.
        examples_prompt: The string of few-shot examples.
        retries: The maximum number of times to retry on a rate limit error.

    Returns:
        The cleaned text as a string.

    Raises:
        Exception: If the API call fails after all retry attempts.
    """
    if not CLIENT:
        raise Exception("OpenAI client is not initialized.")

    system_message = (
        "You are a meticulous medical editor. Clean and structure the following "
        "medical trial summary to match the provided examples."
    )
    user_prompt = (
        f"{examples_prompt}\n"
        "----\n"
        "Raw Summary:\n"
        f"{raw_text}\n\n"
        "Cleaned Summary (match the style above):\n"
    )

    for attempt in range(retries):
        try:
            response = CLIENT.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=4096,
                temperature=0.1,  # Low temperature for deterministic, consistent output
            )
            return response.choices[0].message.content.strip()
        except RateLimitError:
            # Exponential backoff: wait longer after each failed attempt
            wait_time = 20 * (2 ** attempt)
            print(
                f"Rate limit hit. Waiting {wait_time} seconds... "
                f"(Attempt {attempt + 1}/{retries})"
            )
            time.sleep(wait_time)
            
    raise Exception("API call failed after multiple retries due to rate limiting.")


def main():
    """
    Main function to orchestrate the batch cleaning process.
    """
    os.makedirs(CLEANED_FILES_DIR, exist_ok=True)

    # 1. Build the few-shot prompt from example files
    print("Building few-shot prompt from examples...")
    few_shot_examples_prompt = build_few_shot_prompt(
        FEW_SHOT_RAW_PATHS, FEW_SHOT_CLEAN_PATHS
    )
    if not few_shot_examples_prompt:
        print("Could not build few-shot prompt. Check example file paths. Exiting.")
        return

    # 2. Get a list of files to process
    try:
        files_to_process = [
            f for f in os.listdir(RAW_FILES_DIR) if f.endswith(".txt")
        ]
    except FileNotFoundError:
        print(f"Error: Input directory '{RAW_FILES_DIR}' not found. Exiting.")
        return
        
    if not files_to_process:
        print(f"No .txt files found in '{RAW_FILES_DIR}'.")
        return

    print(f"Found {len(files_to_process)} files to clean.")

    # 3. Process each file
    for filename in tqdm(files_to_process, desc="Cleaning Articles"):
        input_path = os.path.join(RAW_FILES_DIR, filename)
        output_path = os.path.join(CLEANED_FILES_DIR, filename)

        if os.path.exists(output_path):
            # Use tqdm.write to print without disturbing the progress bar
            tqdm.write(f"Skipping already cleaned file: {filename}")
            continue

        try:
            with open(input_path, "r", encoding="utf-8") as infile:
                raw_text = infile.read()

            cleaned_text = clean_text_with_gpt(raw_text, few_shot_examples_prompt)

            with open(output_path, "w", encoding="utf-8") as outfile:
                outfile.write(cleaned_text)
            
            # Add a small, consistent delay to respect API rate limits
            time.sleep(2)

        except Exception as e:
            tqdm.write(f"Failed to process {filename}: {e}")

    print("\nBatch cleaning complete!")


if __name__ == "__main__":
    main()