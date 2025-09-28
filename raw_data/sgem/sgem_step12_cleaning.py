"""
This script performs the final formatting conversion on the SGEM Markdown files.

Its specific purpose is to convert custom bolded headers (e.g., '**Summary:**')
into standard Markdown H2 headers (e.g., '## Summary'). This is the last step
to ensure all files adhere to a consistent, machine-readable format.

The script safely isolates the YAML front matter, applies the transformation
only to the main body of the text, and then reassembles the file.
"""

import os
import re
from typing import List

# --- Configuration ---
INPUT_DIR = "sgem_step11_cleaned"
OUTPUT_DIR = "sgem_step12_cleaned"


def convert_bold_to_markdown_headings(file_content: str) -> str:
    """
    Converts bolded headers to markdown H2 headings in the main body of the text.

    Args:
        file_content: The full string content of the markdown file.

    Returns:
        The processed file content with converted headings.
    """
    # 1. Split the file to isolate the main content from the YAML front matter.
    parts = file_content.split('---', 2)
    if len(parts) < 3:
        # No valid YAML front matter found; process the whole file as content.
        yaml_section = ""
        main_content = file_content
    else:
        # Reconstruct the YAML section to preserve it perfectly.
        yaml_section = f"---\n{parts[1].strip()}\n---\n\n"
        main_content = parts[2]

    # 2. Define the regex pattern to find bolded headers at the start of a line.
    # - `^`       : Start of a line (due to re.MULTILINE).
    # - `\*\*`    : Literal opening "**".
    # - `(.+?)`   : Non-greedily captures the heading text (Group 1).
    # - `:**`   : A literal colon followed by "**".
    pattern = re.compile(r'^\*\*(.+?):\*\*', re.MULTILINE)

    # 3. Define the replacement format.
    # '## ' is the markdown H2 heading syntax.
    # '\1' is a backreference to the captured heading text from Group 1.
    replacement = r'## \1'

    # 4. Perform the substitution on the main content only.
    modified_content = pattern.sub(replacement, main_content)

    # 5. Reassemble the file and return the full content.
    return f"{yaml_section}{modified_content}"


def main():
    """
    Main function to orchestrate the processing of all SGEM files.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Starting to process files from '{INPUT_DIR}'...")

    # Get a list of all markdown files in the input directory.
    try:
        filenames = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".md")]
        if not filenames:
            print(f"WARNING: No markdown files found in '{INPUT_DIR}'.")
            return
    except FileNotFoundError:
        print(f"? ERROR: Input directory '{INPUT_DIR}' not found.")
        return

    for filename in filenames:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        try:
            print(f"Processing '{filename}'...")
            with open(input_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Convert the headings using the main logic function.
            converted_content = convert_bold_to_markdown_headings(original_content)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(converted_content)

        except Exception as e:
            print(f"ERROR processing '{filename}': {e}")

    print(f"\nProcessing complete. Your converted files are in '{OUTPUT_DIR}'.")


if __name__ == "__main__":
    main()