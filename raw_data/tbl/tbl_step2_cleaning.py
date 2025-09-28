# -*- coding: utf-8 -*-
"""
This script processes semi-structured text files and reformats them into
a clean, standardized Markdown format with a YAML front matter block.

It uses the OpenAI GPT-4o model with a detailed, specific prompt to perform
the structural conversion. The script is designed to be a formatting and
copy-editing tool, and it does not alter or summarize the clinical content.

The process is as follows:
1.  Read each text file from an input directory.
2.  Send the content to the GPT-4o API with a detailed set of instructions.
3.  The instructions guide the model to:
    - Create a YAML metadata block.
    - Format the main title as a level-one Markdown header.
    - Standardize all other section headings to level-two headers.
    - Merge 'Strengths' and 'Weaknesses' into a single section.
4.  Save the cleaned Markdown content to an output directory.
5.  Log any files that cause errors during processing.
"""

import os
import time
import math
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
INPUT_DIR = 'step1_cleaned_articles'
OUTPUT_DIR = 'step2_cleaned_articles'
MODEL_NAME = "gpt-4o"
MAX_MODEL_TOKENS = 16384  # Max token limit for gpt-4o

# The detailed prompt that instructs the GPT model on how to format the text.
GPT_PROMPT = """
You are an expert data engineer specializing in reformatting clinical trial summaries for an AI analysis pipeline.

Your task is to convert the provided document from its current format into the standardized Markdown structure shown in the example. This is a structural formatting and copy-editing task only; do not alter or summarize the clinical content.

Follow these steps precisely:

---

### 1. Create a Strict YAML Metadata Block
- Find the bulleted list of metadata at the top of the file (e.g., lines starting with "- Source:").
- **You must convert this list into a formal YAML block.** The block must start with `---` on its own line, followed by the key-value pairs, and end with `---` on its own line.
- Each key must be followed by a colon and a space (e.g., `source: The Bottom Line`).
- **Crucially, the final output must NOT use Markdown bullet points (`-`) for the metadata section.**
- The YAML block must include any available keys from the source (`source`, `title`, `original_url`, `scrape_date`, `summary_author`, `summary_date`, `peer_review_editor`).
- Ensure the `summary_date` is in `YYYY-MM-DD` format.
- Add the field `summary: "Will be added later"` to the end of the YAML block.

---

### 2. Format the Main Title
- Locate the section under the `# Title` heading.
- Extract only the primary title of the study.
- Discard the author, journal, and DOI information.
- Format this primary title as a single level-one Markdown header (`#`).

---

### 3. Standardize All Section Headings
- Identify all remaining top-level section headings in the main body (e.g., `# Clinical Question`, `# Design`, `# Population`, etc).
- Convert all of these headings to level-two Markdown headers (`##`).
- This is a catch-all rule: ensure that standard sections and any non-standard sections (like `# Methods` or `# Competing Interests`) are all preserved and correctly formatted as `##`.

---

### 4. Merge "Strengths" and "Weaknesses"
- Find the `# Strengths` and `# Weaknesses` sections.
- Combine them into a single section titled `## Strengths and Weaknesses`.
- The content from the original sections should be placed under bolded labels (`- **Strengths**` and `- **Weaknesses**`) within this new, merged section.

---

### 5. Preserve All Content
- Ensure all lists, text, and tables within every section are preserved exactly as they appear in the original file.

---

### Example Transformation:

**IF YOU RECEIVE THIS INPUT:**
```markdown
# Metadata
- Source: The Bottom Line
- Title: Yeatts
...

# Title
Effect of Video Laryngoscopy on Trauma Patient Survival: A Randomised Controlled Trial  
**Yeatts.** J Trauma Acute Care Surg 2013; 75(2):212-219...

# Clinical Question
In adults requiring emergency intubation...

# Strengths
- Addresses an important clinical question...

# Weaknesses
- Lack of detail on randomisation...

**YOUR OUTPUT MUST BE IN THIS EXACT FORMAT:**

---
source: The Bottom Line
title: Yeatts
summary: "Will be added later"
---

# Effect of Video Laryngoscopy on Trauma Patient Survival: A Randomised Controlled Trial

## Clinical Question
In adults requiring emergency intubation...

## Strengths and Weaknesses
- **Strengths**
  - Addresses an important clinical question...
- **Weaknesses**
  - Lack of detail on randomisation...
---
"""


def format_content_with_gpt(prompt: str, content: str, filename: str) -> str:
    """
    Calls the GPT-4o API to reformat the provided text content.

    It dynamically calculates the required number of output tokens to avoid
    truncating the model's response.

    Args:
        prompt: The system prompt instructing the model.
        content: The raw text content of the file to be processed.
        filename: The name of the file being processed (for context).

    Returns:
        The cleaned and reformatted text as a string.
    """
    if not CLIENT:
        raise Exception("OpenAI client is not initialized.")
        
    # --- Dynamic Token Calculation ---
    # Estimate input tokens (1 token ~= 4 chars) and add a buffer for the output.
    input_tokens = math.ceil(len(content) / 4)
    estimated_output_tokens = input_tokens + 1000  # Add a safe buffer
    
    # Ensure the requested token count doesn't exceed the model's absolute maximum.
    max_tokens_for_call = min(estimated_output_tokens, MAX_MODEL_TOKENS)

    print(f"  - Setting max_tokens for API call to: {max_tokens_for_call}")

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"File name: {filename}\n\n{content}"}
    ]
    response = CLIENT.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=max_tokens_for_call,
        temperature=0.0,  # Set to 0.0 for maximum determinism and consistency
    )
    return response.choices[0].message.content.strip()


def main():
    """
    Main function to orchestrate the batch processing of files.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log_path = os.path.join(OUTPUT_DIR, "error_files.log")
    error_files: List[str] = []

    try:
        files_to_process = [
            f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.txt')
        ]
    except FileNotFoundError:
        print(f"Error: Input directory '{INPUT_DIR}' not found. Exiting.")
        return
        
    if not files_to_process:
        print(f"No .txt files found in '{INPUT_DIR}'.")
        return

    print(f"Found {len(files_to_process)} text files to process.")

    for filename in files_to_process:
        input_path = os.path.join(INPUT_DIR, filename)
        output_filename = filename.replace('.txt', '.md')
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        if os.path.exists(output_path):
            print(f"Skipping '{filename}', output file already exists.")
            continue
            
        print(f"Processing '{filename}'...")
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
            
            result = format_content_with_gpt(GPT_PROMPT, raw_content, filename)
            
            with open(output_path, "w", encoding="utf-8") as out_file:
                out_file.write(result)
                
            # A brief pause to respect API rate limits and avoid errors.
            time.sleep(2)
            
        except Exception as e:
            error_message = f"Error processing {filename}: {e}"
            print(error_message)
            error_files.append(error_message)
            
    # After processing all files, write any errors to the log file.
    if error_files:
        print(f"\nLogged {len(error_files)} errors to {log_path}")
        with open(log_path, "w", encoding="utf-8") as log_file:
            for error_entry in error_files:
                log_file.write(error_entry + "\n")
        
    print("\nAll files processed.")


if __name__ == "__main__":
    main()