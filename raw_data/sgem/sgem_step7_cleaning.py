"""
This script performs a content-focused cleaning pass on the SGEM
Markdown files using the OpenAI GPT model.

It is designed to preserve all clinical information while removing minor
non-medical clutter and standardizing formatting within the main body of the text.

The process is as follows:
1.  Reads each Markdown file from an input directory.
2.  Safely separates the YAML front matter from the main content.
3.  Sends only the main content to the GPT API with a detailed prompt that
    specifies what to keep, what to delete, and how to format.
4.  The model returns either the cleaned text or a special "flag" if the
    file's structure is too complex to process reliably.
5.  If cleaning is successful, the script reassembles the file with the
    original metadata and the cleaned content.
6.  If the file is flagged, the original, untouched file is moved to a
    review directory for manual inspection.
7.  API errors and flagged files are logged.
"""

import os
import time
from typing import List

import openai

# --- Configuration ---
# Set your OpenAI API key in your environment variables
try:
    CLIENT = openai.OpenAI()
except openai.OpenAIError as e:
    print(f"Error: OpenAI client could not be initialized. {e}")
    print("Please ensure your OPENAI_API_KEY is set correctly.")
    CLIENT = None

# Define directories and model parameters
INPUT_DIR = 'sgem_step6_cleaned'
OUTPUT_DIR = 'sgem_step7_cleaned''
REVIEW_DIR = 'sgem_review'
MODEL_NAME = "gpt-4-turbo"

# This detailed prompt instructs the model on fine-grained cleaning tasks.
GPT_PROMPT = """
You are a meticulous text-processing AI specializing in medical documents for AI pipelines.

Your most important directive is to preserve all medically relevant information. When in doubt, do not delete. It is better to leave some non-medical clutter than to remove any clinical content.

Follow these rules precisely:

1. What to KEEP (Do NOT Delete)
- You MUST keep all of the content. 
- You MUST keep any text, paragraphs, or lists that appear after the 'Results' or 'Authors' Conclusions' section but before a 'Comment on Authors’ Conclusion' or 'Bottom Line' section under the "Commentary" heading. 
- You MUST also keep all of the following sections:
 - Case or Case Scenario
 - Background
 - Question or Clinical Question
 - Reference or Article
 - The PICO breakdown (Population, Intervention, Comparison, Outcome)
 - Authors' Conclusions and any commentary on them
 - Results, Key Results, or any sections related to results
 - Commentary
 - Limitations
 - Comment on Authors’ Conclusion
 - Case Resolution
 - Clinical Application
 - Sections like "What Do I Tell My ...?" and similar sections
 - The final SGEM Bottom Line or BEEM Bottom Line.

2. What to DELETE (Only Non-Medical Clutter):
You should ONLY delete the following types of non-essential content:
- Any remaining image link artifacts (e.g., ![checklist-cartoon](...), or a standalone name like Dr. Anthony Crocco that was clearly an image caption).
- Self-referential mentions to other SGEM episodes (e.g., (SGEM#95)).
- All horizontal rule separators (---) from the body of the text.

3. How to FORMAT:
- Correct Core Errors: Fix all spelling, grammar, and punctuation.
- Standardize Headers: Ensure all main section headers are bolded with two asterisks (e.g., **Background:**). Remove any leading numbers or hyphens from these headers.
- Standardize Lists: Ensure all bulleted lists use a hyphen (-).

4. Final Output:
- Only return the fully cleaned text. Do not add any commentary or introductions.
- If the file has significant structural problems you cannot fix, output only this flag on a single line:
`FLAG_FOR_MANUAL_REVIEW: This file has complex structural issues.`
- Final Check: Before finishing, re-read your output one last time to ensure you have followed the primary directive and have not deleted any potentially important clinical content.
"""


def clean_content_with_gpt(prompt: str, content: str) -> str:
    """
    Calls the GPT API to perform the final cleaning on the main content.

    Args:
        prompt: The system prompt with detailed instructions.
        content: The main body content of the markdown file.

    Returns:
        The cleaned content string from the model.
    """
    if not CLIENT:
        raise Exception("OpenAI client is not initialized.")

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": content}
    ]
    response = CLIENT.chat.com.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()


def main():
    """
    Main function to orchestrate the batch processing and flagging of files.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(REVIEW_DIR, exist_ok=True)
    
    log_path_error = os.path.join(OUTPUT_DIR, "api_error_log.log")
    log_path_review = os.path.join(REVIEW_DIR, "files_for_review.log")
    
    files_to_review: List[str] = []
    api_errors: List[str] = []

    try:
        files_to_process = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.md')]
    except FileNotFoundError:
        print(f"Error: Input directory '{INPUT_DIR}' not found. Exiting.")
        return

    print(f"Found {len(files_to_process)} markdown files to process.")

    for filename in files_to_process:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        review_path = os.path.join(REVIEW_DIR, filename)

        if os.path.exists(output_path) or os.path.exists(review_path):
            print(f"Skipping '{filename}', an output file already exists.")
            continue
            
        try:
            with open(input_path, 'r', encoding="utf-8") as f:
                full_content = f.read()
            
            # Safely separate metadata from main content.
            parts = full_content.split('---', 2)
            if len(parts) < 3:
                print(f"WARNING: No metadata block found in {filename}. Treating entire file as content.")
                metadata_block = ""
                main_content = full_content
            else:
                metadata_block = f"---\n{parts[1].strip()}\n---\n\n"
                main_content = parts[2]
            
            print(f"Processing '{filename}'...")
            cleaned_main_content = clean_content_with_gpt(GPT_PROMPT, main_content)
            
            if "FLAG_FOR_MANUAL_REVIEW" in cleaned_main_content:
                print(f"FLAGGED for manual review. Moving original to '{REVIEW_DIR}'.")
                # Move the original, untouched file to the review folder.
                os.rename(input_path, review_path)
                files_to_review.append(filename)
            else:
                # Re-assemble the file with original metadata and cleaned content.
                final_content = metadata_block + cleaned_main_content
                with open(output_path, "w", encoding="utf-8") as out_file:
                    out_file.write(final_content)
                print(f" Successfully cleaned and saved '{filename}'")
                
            time.sleep(1) # A small delay to respect API rate limits.
            
        except Exception as e:
            error_message = f"API Error with {filename}: {e}"
            print(f"{error_message}")
            api_errors.append(error_message)

    # Write logs after processing all files.
    if api_errors:
        print(f"\nLogged {len(api_errors)} API errors to {log_path_error}")
        with open(log_path_error, "w", encoding="utf-8") as log_file:
            log_file.write("\n".join(api_errors))
            
    if files_to_review:
        print(f"Logged {len(files_to_review)} files flagged for review to {log_path_review}")
        with open(log_path_review, "w", encoding="utf-8") as log_file:
            log_file.write("\n".join(files_to_review))
            
    print("\nAll files processed.")


if __name__ == "__main__":
    main()