"""
This script performs a content enrichment step for the SGEM Markdown files.

It reads each cleaned Markdown file, checks if a clinical summary already
exists in the YAML front matter, and if not, generates one using the
OpenAI GPT-4o model.

The process is as follows:
1.  Scans an input directory for Markdown files.
2.  For each file, it parses the YAML front matter to check for a 'summary' key.
3.  If a summary is missing, it sends the main body content to the GPT API.
4.  A specialized prompt instructs the model to act as an expert medical writer
    and generate a single, dense summary paragraph.
5.  The script inserts the new summary into the YAML block of the original file.
6.  The final, updated Markdown content is saved to a new file in the
    output directory.
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
INPUT_DIR = 'sgem_step7_cleaned'
OUTPUT_DIR = 'sgem_step8_cleaned'
MODEL_NAME = "gpt-4o"

# This prompt instructs the GPT model to generate a clinical summary paragraph.
GPT_PROMPT = """
You are an expert medical writer and data engineer specializing in creating concise clinical summaries for metadata.

Your sole task is to read the provided medical document, generate a high-quality clinical summary, and return the summary.

Follow these steps precisely:

---

### 1. Analyze the Document
Carefully read the entire content of the provided file to understand its clinical focus. Use all available information to inform the summary you will write.

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
    Sends content to the GPT API and returns the generated summary.

    Args:
        content: The main body content of the markdown file.

    Returns:
        The summary paragraph as a string.
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
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()


def main():
    """
    Orchestrates the batch processing of files to generate and add summaries.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log_path = os.path.join(OUTPUT_DIR, "error_log.log")
    error_logs: List[str] = []

    try:
        files_to_process = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.md')]
    except FileNotFoundError:
        print(f"Error: Input directory '{INPUT_DIR}' not found. Exiting.")
        return

    print(f"Found {len(files_to_process)} markdown files to process.")

    for filename in files_to_process:
        input_path = os.path.join(INPUT_DIR, filename)
        output_filename = filename.replace('.md', '_final.md')
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        if os.path.exists(output_path):
            print(f"Skipping '{filename}', output file already exists.")
            continue

        try:
            with open(input_path, 'r', encoding="utf-8") as f:
                raw_content = f.read()

            # 1. Split the file into YAML front matter and main content.
            parts = raw_content.split('---', 2)
            if len(parts) < 3:
                print(f"Skipping '{filename}', no valid YAML block found.")
                continue

            yaml_content = parts[1]
            main_content = parts[2]

            # 2. Check if a summary already exists in the YAML to avoid re-processing.
            if 'summary:' in yaml_content.lower():
                print(f"Skipping '{filename}', summary key already exists.")
                continue

            print(f"Processing '{filename}'...")

            # 3. Get the summary from the API using the main content.
            summary_text = generate_clinical_summary(main_content)

            # 4. Prepare the summary for YAML multi-line format.
            indented_summary = textwrap.indent(summary_text, '  ')
            # The '|\n' creates a literal block scalar in YAML for multi-line strings.
            new_summary_entry = f"summary: |\n{indented_summary}\n"

            # 5. Reconstruct the file with the new summary added to the YAML.
            final_content = f"---{yaml_content}{new_summary_entry}---{main_content}"

            # 6. Write the final content to the new file.
            with open(output_path, "w", encoding="utf-8") as out_file:
                out_file.write(final_content)

            print(f"Successfully created {output_filename}")

            # A brief pause to respect API rate limits.
            time.sleep(2)

        except Exception as e:
            error_message = f"An error occurred with {filename}: {e}"
            print(f"{error_message}")
            error_logs.append(error_message)

    if error_logs:
        print(f"\nLogged {len(error_logs)} errors to {log_path}")
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write("\n".join(error_logs))

    print("\nAll files processed.")


if __name__ == "__main__":
    main()