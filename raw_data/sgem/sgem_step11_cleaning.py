"""
This script performs a final content transformation on Markdown files.

It serves a dual purpose:
1.  **Structural Unification**: It filters the main content of each file,
    keeping only a predefined set of essential sections (e.g., "Summary,"
    "Clinical Point," "Bottom Line") and standardizing their headers.
2.  **Content Summarization**: It specifically targets the "Background" section,
    sending its content to the OpenAI GPT-4o model to generate a concise,
    encyclopedic summary, which then replaces the original background text.

"""

import os
import re
import time
from typing import Dict, Any, Optional, List

import yaml
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
INPUT_DIR = "sgem_step10_cleaned"
OUTPUT_DIR = "sgem_step11_cleaned"
MODEL_NAME = "gpt-4o"

# This dictionary maps canonical header names to a list of their variants
# found in the source files. This is used by `normalize_header`.
KEEP_HEADERS = {
    "summary": ["summary"],
    "background": ["background"],
    "case": ["case", "case scenario", "clinical case"],
    "point": ["point", "clinical point"],
    "bottom line": ["bottom line", "sgem bottom line", "beem bottom line"],
    "case resolution": ["case resolution"],
    "clinical application": ["clinical application"],
    "what do i tell": [
        "what do i tell", "what do i tell my patient", "what do i tell the patient"
    ],
}

# This prompt instructs the GPT model on how to summarize the 'Background' section.
GPT_PROMPT = """
You are a medical expert and writer creating content for a clinical AI knowledge base.
Your task is to summarize the following 'Background' text into a single, dense paragraph.
The summary will serve as foundational knowledge for a medical Q&A system.
Follow these instructions precisely:
---
### 1. Your summary must be concise, objective, and written in a formal, encyclopedic tone.
---
### 2. Focus only on the key information presented in the text provided.
---
### 3. Incorporate the following elements if they are present in the text:
- The definition of the primary medical condition.
- Its clinical significance (e.g., prevalence, risks, morbidity/mortality).
- The standard diagnostic or treatment approaches mentioned.
---
### 4. Your final output should be only the summary paragraph.
Do not include introductory phrases (e.g., "This text discusses...") or conversational filler.
---
"""


def normalize_header(header: str) -> Optional[str]:
    """
    Maps a raw header string to its canonical (standardized) name.

    For example, "Clinical Point:" would be normalized to "point".

    Args:
        header: The raw header text from the file.

    Returns:
        The canonical header name as a string, or None if it's not a header to keep.
    """
    clean_header = header.lower().strip().rstrip('?:')
    for canonical_name, variants in KEEP_HEADERS.items():
        if any(clean_header.startswith(v) for v in variants):
            return canonical_name
    return None


def summarize_background_with_gpt(text: str, filename: str) -> str:
    """
    Sends the background text to the GPT API for summarization.

    Args:
        text: The content of the 'Background' section.
        filename: The name of the file being processed, for error logging.

    Returns:
        The AI-generated summary, or the original text if an error occurs.
    """
    if not CLIENT:
        raise Exception("OpenAI client is not initialized.")

    messages = [{"role": "system", "content": GPT_PROMPT}, {"role": "user", "content": text}]
    try:
        response = CLIENT.chat.com.completions.create(
            model=MODEL_NAME, messages=messages, max_tokens=1000, temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error summarizing background in '{filename}': {e}. Using original text.")
        return text


def main():
    """
    Main function to orchestrate the file processing and summarization loop.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        filenames = os.listdir(INPUT_DIR)
    except FileNotFoundError:
        print(f"Error: Input directory '{INPUT_DIR}' not found. Exiting.")
        return

    print(f"Processing files from '{INPUT_DIR}'...")

    for filename in filenames:
        if not filename.lower().endswith(".md"):
            continue

        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(output_path):
            print(f"Skipping '{filename}', output file already exists.")
            continue

        print(f"Processing '{filename}'...")

        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Safely separate YAML metadata from the main body content.
        metadata: Dict[str, Any] = {}
        body = content
        if content.startswith("---"):
            try:
                parts = content.split("---", 2)
                yaml_text, body = parts[1], parts[2]
                metadata = yaml.safe_load(yaml_text) or {}
            except (yaml.YAMLError, IndexError):
                print(f"Warning: Could not parse YAML in '{filename}'.")
                metadata, body = {}, content

        # 2. Move the summary from metadata to become the first section of the body.
        summary_text = metadata.pop("summary", "").strip()
        new_body = f"**Summary:**\n{summary_text}\n\n" if summary_text else ""

        # 3. Split the body into sections using a regex that looks for bolded headers.
        sections = re.split(r"\n(?=\*\*[^*]+:\*\*|\*\*[^*]+\?\*\*)", body)

        # 4. Process each section.
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue
                
            header_match = re.match(r"\*\*([^*]+?[:?]?)\*\*", sec)
            if not header_match:
                continue

            header_text = header_match.group(1).strip()
            canonical_header = normalize_header(header_text)

            if canonical_header:
                content_part = re.sub(r"^\*\*([^*]+?[:?]?)\*\*", "", sec, count=1).strip()

                # If it's the background section, summarize it with GPT.
                if canonical_header == "background":
                    print(f"  - Summarizing 'Background' section...")
                    content_part = summarize_background_with_gpt(content_part, filename)
                    time.sleep(2) # Respect API rate limits

                # Reconstruct the section with the original header.
                new_body += f"**{header_text}**\n{content_part}\n\n"

        # 5. Re-assemble the final file content.
        final_content = ""
        if metadata:
            new_yaml_text = yaml.dump(
                metadata, sort_keys=False, default_flow_style=False, allow_unicode=True
            ).strip()
            final_content = f"---\n{new_yaml_text}\n---\n\n"

        final_content += new_body.strip() + "\n"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_content)

        print(f"Saved cleaned file to '{output_path}'")

    print(f"\nProcessing complete. Results saved in '{OUTPUT_DIR}' ?")

if __name__ == "__main__":
    main()