"""
This script performs a sixth cleaning pass on the SGEM Markdown files.

Its specific purpose is to find and remove the "Quality Checklist" section
from each document. This section is a recurring, structured element that can
be safely removed to standardize the core clinical content.

The script uses a single, complex regular expression to identify the start
of the checklist and removes all content up to the beginning of the next
major section (e.g., 'Key Results').
"""

import os
import re

# --- Configuration ---
SOURCE_DIR = 'sgem_step5_cleaned'
OUTPUT_DIR = 'sgem_step6_cleaned'

# This complex regex is designed to find and remove the entire 'Quality Checklist' section.
# Breakdown:
# - `^`: Matches the start of a line (due to re.MULTILINE).
# - `\s*`: Matches any leading whitespace.
# - `(!\[.*?\]\(.*?\))?`: Optionally matches a leading image (like a checkmark icon).
# - `(\*\*?)?Quality\s+Check\s?list.*?:`: Matches "Quality Checklist" and its variations,
#   allowing for different spacing, optional bolding, and a trailing colon.
# - `.*?`: Non-greedily matches all characters (the content of the checklist).
# - `(?=...)`: A positive lookahead that stops the match right BEFORE it
#   finds the start of the next major section or a horizontal rule ('---'),
#   ensuring that section is not deleted.
QUALITY_CHECKLIST_PATTERN = re.compile(
    r'^\s*(!\[.*?\]\(.*?\))?\s*(\*\*?)?Quality\s+Check\s?list.*?:.*?'
    r'(?=\s*---|\s*\*\*(What were the\s)?\s*Key\sResults:?\*\*|\s*\*\*\s*Results:?\*\*:?|\s*\*\*Comment on Author)',
    re.DOTALL | re.IGNORECASE | re.MULTILINE
)


def remove_quality_checklist(content: str) -> str:
    """
    Applies the regex pattern to remove the Quality Checklist section.

    Args:
        content: The string content of a markdown file.

    Returns:
        The content string with the checklist section removed.
    """

    cleaned_content = QUALITY_CHECKLIST_PATTERN.sub("", content)
    return cleaned_content


def main():
    """
    Main function to orchestrate the cleaning process for all files.
    """
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory not found at '{SOURCE_DIR}'")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Processing files in '{SOURCE_DIR}'...")

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

            # Run the cleaning function.
            cleaned_content = remove_quality_checklist(content)

            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(cleaned_content)

            files_processed += 1

        except Exception as e:
            print(f"Could not process file '{filename}'. Error: {e}")

    print(f"\nDone! Processed {files_processed} files.")
    print(f"Final files are in '{OUTPUT_DIR}'")


if __name__ == "__main__":
    main()