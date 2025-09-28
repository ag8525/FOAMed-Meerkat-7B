"""
This script performs a fourth cleaning pass on the SGEM Markdown files.

Its sole purpose is to remove all blockquote formatting. It reads each
markdown file and removes the blockquote character '>' and any subsequent
whitespace from the beginning of any line. This helps to flatten the text
structure for further processing.
"""

import os
import re

# --- Configuration ---
SOURCE_DIR = 'sgem_step3_cleaned'
OUTPUT_DIR = 'sgem_step4_cleaned'


def main():
    """
    Main function to orchestrate the removal of blockquotes from all files.
    """
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory not found at '{SOURCE_DIR}'")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Source:      '{SOURCE_DIR}'")
    print(f"Destination: '{OUTPUT_DIR}'\n")

    # This regex pattern finds any line that starts with one or more
    # blockquote characters ('>') followed by optional spaces.
    # - `^`         : Matches the start of a line (due to re.MULTILINE).
    # - `(>\s*)+`   : Matches one or more groups of '>' followed by zero or
    #                 more whitespace characters. This handles `>` and `>> `.
    blockquote_pattern = re.compile(r'^(>\s*)+', re.MULTILINE)

    try:
        filenames = os.listdir(SOURCE_DIR)
    except FileNotFoundError:
        print(f"Error: The source directory '{SOURCE_DIR}' was not found.")
        return

    files_processed = 0
    for filename in filenames:
        if not filename.lower().endswith(".md"):
            continue

        source_path = os.path.join(SOURCE_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        try:
            with open(source_path, 'r', encoding='utf-8') as source_file:
                content = source_file.read()

            # Replace the found blockquote patterns with an empty string.
            cleaned_content = blockquote_pattern.sub("", content)

            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(cleaned_content)

            files_processed += 1

        except Exception as e:
            print(f"Could not process file '{filename}'. Error: {e}")

    print(f"\nDone! Processed and removed blockquotes from {files_processed} files.")


if __name__ == "__main__":
    main()