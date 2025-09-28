"""
This script performs a fifth and final cleaning pass on the SGEM Markdown files.

Its purpose is to remove the introductory "Guest Skeptic" section (and its
variations like 'Featuring' or 'Guest Host'). This section typically appears
at the top of the document before the main clinical content.

The script uses a complex regular expression to identify the start of this
section and removes all content up to the beginning of the next major section
(e.g., 'Background', 'Case Scenario', 'Clinical Question').
"""

import os
import re

# --- Configuration ---
SOURCE_DIR = 'sgem_step4_cleaned'
OUTPUT_DIR = 'sgem_step5_cleaned'

# This complex regex is designed to find and remove the entire introductory
# 'Guest Skeptic' section from the start of the file.
# Breakdown:
# - `^`: Matches the start of a line (due to re.MULTILINE).
# - `\s*`: Matches any leading whitespace.
# - `(\*\*|\*|\s)*`: Matches any combination of bold markers or spaces.
# - `((Classic\s|...|Featuring)`: Matches the core phrases like "Guest Skeptic",
#   "Guest Host", "Classic Guest Skeptic", or "Featuring".
# - `.*?`: Non-greedily matches all characters (the content of the section).
# - `(?=...)`: A positive lookahead that stops the match right BEFORE it
#   finds the start of the next major section, ensuring that section is not deleted.
INTRO_SECTION_PATTERN = re.compile(
    r'^\s*(\*\*|\*|\s)*((Classic\s|Featuring\s)?Guest (Skeptics?|Host)|Featuring)(\*|\s)*:?(\*\*|\*)?.*?'
    r'(?=\s*\*\*\s*Background|\s*\*\*\s*Case Scenario|\s*\*\*\s*Case|\s*###\s*\*\*\s*Clinical Question|\s*\*\*\s*Reference)',
    re.DOTALL | re.IGNORECASE | re.MULTILINE
)


def main():
    """
    Main function to orchestrate the removal of introductory sections from all files.
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

            # Replace the found introductory section pattern with an empty string.
            cleaned_content = INTRO_SECTION_PATTERN.sub("", content)

            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(cleaned_content)

            files_processed += 1

        except Exception as e:
            print(f"Could not process file '{filename}'. Error: {e}")

    print(f"\nDone! Processed and cleaned {files_processed} files.")
    print(f"Final files are in '{OUTPUT_DIR}'")


if __name__ == "__main__":
    main()