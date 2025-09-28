# -*- coding: utf-8 -*-
"""
This script processes cleaned Markdown files of CRACKCast shownotes to
generate and insert a final clinical overview.

The process is as follows:
1.  Scans an input directory for Markdown files that contain a specific
    YAML placeholder: `summary: "Will be added later"`.
2.  For each such file, it sends the entire content to the OpenAI GPT-4o model.
3.  A specialized prompt instructs the model to act as an expert medical writer
    and generate a single, dense paragraph summarizing the document's key
    clinical information.
4.  The script receives the summary, formats it as a YAML multi-line block
    string, and replaces the original placeholder in the file's content.
5.  The final, updated Markdown content is saved to a new file in the
    output directory.
6.  Any errors encountered during the process are logged.
"""

import os
import time
import textwrap
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

# Define file paths and model parameters
INPUT_DIR = 'step2_cleaned_shownotes'
OUTPUT_DIR = 'step3_cleaned_shownotes'
MODEL_NAME = "gpt-4o"

# This prompt instructs the GPT model to generate a clinical summary paragraph.
GPT_PROMPT = """
You are an expert medical writer and data engineer specializing in creating concise clinical summaries for metadata.

Your sole task is to read the provided medical document, generate a high-quality clinical summary, and return the summary.

Follow these steps precisely:

---

### 1. Analyze the Document
Carefully read the entire content of the provided file to understand its clinical focus. This includes the "Overview," "Core Questions," "Wisecracks," and any existing "Summary" section in the main text. Use all of this information to inform the summary you will write.

---

### 2. Generate the Clinical Summary
Write a single, dense paragraph of 3-5 sentences that summarizes the document's key clinical information. The summary should be written for a medical professional and highlight:
- The main conditions or topics discussed (e.g., DKA, hip fractures, ASA toxicity).
- Key diagnostic principles or findings.
- Critical management steps and treatments.
- Any major warnings or pitfalls mentioned.

---

### 3. Output the Summary 
Do not write anything else. Only output the summary paragraph.

---
"""


def generate_clinical_summary(content: str) -> str:
    """
    Calls the GPT-4o API to generate a clinical summary for the given content.

    Args:
        content: The full text of the medical summary document.

    Returns:
        A string containing the generated summary paragraph.
    """
    if not CLIENT:
        raise Exception("OpenAI client is not initialized.")

    messages = [
        {"role": "system", "content": GPT_PROMPT},
        {"role": "user", "content": content}
    ]
    response = CLIENT.chat.com.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=1000,  # A generous token limit for the summary
        temperature=0.0,  # Low temperature for focused, consistent output
    )
    return response.choices[0].message.content.strip()


def main():
    """
    Main function to orchestrate the batch processing of files to add summaries.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log_path = os.path.join(OUTPUT_DIR, "error_log.log")
    error_files: List[str] = []

    try:
        files_to_process = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.md')]
    except FileNotFoundError:
        print(f"Error: Input directory '{INPUT_DIR}' not found. Exiting.")
        return

    print(f"Found {len(files_to_process)} markdown files to process.")

    for filename in files_to_process:
        input_path = os.path.join(INPUT_DIR, filename)
        output_filename = filename.replace('_cleaned.md', '_final.md')
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        if os.path.exists(output_path):
            print(f"Skipping '{filename}', output file already exists.")
            continue

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                raw_content = f.read()

            # Process only if the placeholder is present.
            placeholder = 'summary: "Will be added later"'
            if placeholder not in raw_content:
                print(f"Skipping '{filename}', summary placeholder not found.")
                continue

            print(f"Processing '{filename}'...")

            # 1. Get the summary string from the API.
            summary_text = generate_clinical_summary(raw_content)

            # 2. Format the summary for YAML multi-line block style (using '|').
            # The 'textwrap.indent' function adds the required indentation.
            indented_summary = textwrap.indent(summary_text, '  ')
            replacement_text = f"summary: |\n{indented_summary}"

            # 3. Replace the placeholder with the new formatted summary.
            final_content = raw_content.replace(placeholder, replacement_text)

            # 4. Write the final content to the new file.
            with open(output_path, "w", encoding="utf-8") as out_file:
                out_file.write(final_content)

            print(f"  - ? Successfully created {output_filename}")

            # A brief pause to respect API rate limits.
            time.sleep(2)

        except Exception as e:
            error_message = f"An error occurred with {filename}: {e}"
            print(f"  - ? {error_message}")
            error_files.append(error_message)

    # After processing all files, write any errors to the log file.
    if error_files:
        print(f"\nLogged {len(error_files)} errors to {log_path}")
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write("\n".join(error_files))

    print("\nAll files processed. ?")


if __name__ == "__main__":
    main()