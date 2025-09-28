"""
This script processes raw text files from CRACKCast shownotes and reformats
them into a standardized Markdown structure using the OpenAI GPT-4o model.

The core of the script is a detailed, multi-step prompt that instructs the
model to perform structural reformatting and copy-editing without altering
the clinical content.

The process is as follows:
1.  Read each raw text file from an input directory.
2.  Send the content to the GPT-4o API with the detailed formatting prompt.
3.  The model returns either the cleaned Markdown content or a specific
    "outlier" message if the file is too disorganized to process.
4.  The script saves the successfully cleaned content as a .md file.
5.  Files identified as outliers are saved as .txt files and their names are
    logged for manual review.
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

# Define file paths and model parameters
INPUT_DIR = 'step1_cleaned_shownotes'
OUTPUT_DIR = 'step2_cleaned_shownotes'
MODEL_NAME = "gpt-4o"

# The detailed prompt that instructs the GPT model on how to format the text.
GPT_PROMPT = """
You are an expert medical data engineer.

Given the following CrackCast show notes file in plain text, do **not** summarize, rewrite, or change any clinical content except to fix spelling, grammar, or punctuation mistakes. Your task is strictly **structural formatting** and **copy-editing**. This involves two separate "summary" tasks: 1) adding a placeholder for a future summary in the metadata, and 2) preserving any existing summary section found in the document's main text.

---

### 1. Add a YAML metadata block at the very top, containing:
- `title` (from file or inline metadata, e.g., “CrackCast Episode 186: Substance Abuse”)
- `url` (from file if present, or the main CrackCast category URL if only that is available)
- `date` (use the most precise date in the file, in `YYYY-MM-DD`; if only month/year is given, use `YYYY-MM`)
- `soure` = "CanadiEM – CrackCast"
- `original_file` (if present in original metadata)
- `summary`: "Will be added later"

---

### 2. Remove non-content boilerplate:
- Strip repeated “CrackCast Show Notes – …” and site URLs except where they are part of a reference or attribution.
- Remove duplicated header banners or purely navigational lines.

---

### 3. Standardize section headers:
- Convert all **episode structure** elements into `##` major headers in this preferred order **if they are present in the source text**:
  1. Overview
  2. Key Concepts
  3. Rosens in Perspective
  4. Case 
  5. Core Questions
  6. Wisecracks
  7. Summary 
  8. Additional Notes / Commentary
  9. References
- For **Core Questions** and **Wisecracks**:
  - Each numbered question should be a `###` subheading under its parent section with the exact question text.
  - Keep all lists/tables/answers below them.
- If other clearly labeled sections exist (e.g., “Definitions”, “Clinical Features”, “Investigations”), keep them and format them as `## Section Name` or nest under the most relevant canonical section.
- If a section heading is a close variation of one of the major headers (e.g., “Episode Overview” ? `## Overview`, “Key Points” ? `## Key Concepts`, “Conclusion” ? `## Summary`), rename it to the corresponding major header name to ensure consistency.

---

### 4. Overview Section Rules
- If the source text contains any sections like **"Key Concepts"**, **"Rosens in Perspective"**, or **"Case"** before the "Core Questions" section, you must group them under a single `## Overview` heading.
- **Create the `## Overview` heading if it is not already present** to serve as a wrapper for this introductory content.
- If the **Core Questions** list appears under an Overview section, you must remove it from there (it will appear later in its own dedicated section).
- Format the original sections (e.g., "Key Concepts," "Rosens in Perspective", "Case") as `###` subheadings under `## Overview`.
---

### 5. Summary Section Rules (for main text body)
- **If and only if** the source text contains a clear summary section (e.g., under a heading like “Podcast Summary,” “Episode Summary,” or “Conclusion”), you must:
    - Standardize its heading to `## Summary`.
    - Place it immediately before the `## References` section if present.
- **Do NOT create a `## Summary` section if one is not explicitly present in the source text.** This rule is for preserving text in the document body and is separate from the `summary` field in the metadata.
---

### 6. Preserve All Other Clinical Content:
- **Do not** remove any medical facts, tables, lists, or explanations not covered by other rules.
- Treat any bolded/underlined/CAPS line or any line ending with `:` as a possible heading and convert it to a proper markdown header.
- If in doubt, **keep** the content and assign it a meaningful section heading.

---

### 7. Lists, tables, and formatting:
- Maintain bullet/number lists exactly, but fix spacing and indentation.
- Preserve tables if present; if not possible, keep them as aligned plain text lists.
- Keep hyperlinks in `[label](url)` format.

---

### 8. References:
- Move all reference citations to a final `## References` section.
- Deduplicate repeated references.
- Include any relevant URLs from the original file that cite external sources.

---

### 9. Language corrections:
- Fix spelling, grammar, and punctuation errors.
- Do not paraphrase or alter medical meaning.
- Use consistent medical capitalization (e.g., “ECG” not “Ecg”).

---

### 10. Output rules:
- Keep one blank line between sections for readability.
- If the file is missing most expected sections or is highly disorganized, do **not** attempt conversion. Instead, output:
`This file [name of file] was not converted to standard format.`
and log its name in `outlier_files.log`.
---
"""


def format_content_with_gpt(prompt: str, content: str, filename: str) -> str:
    """
    Calls the GPT-4o API to reformat the provided text content.

    Args:
        prompt: The system prompt instructing the model on the formatting rules.
        content: The raw text content of the file to be processed.
        filename: The name of the file being processed (for context in the prompt).

    Returns:
        The cleaned and reformatted text as a string from the model.
    """
    if not CLIENT:
        raise Exception("OpenAI client is not initialized.")

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"File name: {filename}\n\n{content}"}
    ]
    response = CLIENT.chat.com.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=16384,  # A generous token limit for large shownotes
        temperature=0.0,   # Set to 0.0 for deterministic, consistent formatting
    )
    return response.choices[0].message.content.strip()


def main():
    """
    Main function to orchestrate the batch processing of raw text files.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log_path = os.path.join(OUTPUT_DIR, "outlier_files.log")
    outlier_files: List[str] = []

    try:
        files_to_process = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.txt')]
    except FileNotFoundError:
        print(f"Error: Input directory '{INPUT_DIR}' not found. Exiting.")
        return

    print(f"Found {len(files_to_process)} text files to process.")

    for filename in files_to_process:
        input_path = os.path.join(INPUT_DIR, filename)
        
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                raw_content = f.read()

            print(f"Processing '{filename}'...")
            result = format_content_with_gpt(GPT_PROMPT, raw_content, filename)

            # Check if the model identified the file as an outlier.
            outlier_message = f"This file {filename} was not converted to standard format."
            if outlier_message in result:
                print(f"  - ?? Identified as outlier: '{filename}'")
                outlier_files.append(filename)
                # Save the model's message to an outlier file for review.
                outlier_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(filename)[0]}_outlier.txt")
                with open(outlier_path, "w", encoding="utf-8") as out_file:
                    out_file.write(result)
            else:
                # Save the successfully cleaned content as a Markdown file.
                output_filename = f"{os.path.splitext(filename)[0]}_cleaned.md"
                output_path = os.path.join(OUTPUT_DIR, output_filename)
                with open(output_path, "w", encoding="utf-8") as out_file:
                    out_file.write(result)
                print(f"  - ? Successfully cleaned and saved: '{output_filename}'")

            # A brief pause to respect API rate limits.
            time.sleep(2)
            
        except Exception as e:
            print(f"  - ? An unexpected error occurred with '{filename}': {e}")
            outlier_files.append(filename)

    # After processing all files, write the names of outlier files to the log.
    if outlier_files:
        print(f"\nLogged {len(outlier_files)} outlier files to {log_path}")
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write("\n".join(sorted(list(set(outlier_files)))))

    print("\nAll files processed. ?")


if __name__ == "__main__":
    main()