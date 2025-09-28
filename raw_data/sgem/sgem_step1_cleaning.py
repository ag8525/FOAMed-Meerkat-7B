"""
This script performs an initial cleaning pass on the raw SGEM Markdown files.

It is designed to remove specific, known artifacts from the initial scrape:
1.  Lines containing the WordPress shortcode '[display_podcast]'.
2.  Lines that contain a bolded "Date:" heading (e.g., '**Date:** ...').

The script reads each .md file from a source directory, applies these cleaning
rules, and saves the result to a new file in an output directory.
"""

import os
import re

# --- Configuration ---
SOURCE_DIR = 'sgem_shownotes'
OUTPUT_DIR = 'sgem_step1_cleaned'


def main():
    """
    Main function to orchestrate the file cleaning process.
    """
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory not found at '{SOURCE_DIR}'")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output will be saved in: '{OUTPUT_DIR}'")

    # Pre-compile regex patterns for efficiency.
    # Pattern 1: Matches any line containing '[display_podcast]' or '[display\_podcast]'.
    podcast_pattern = re.compile(r".*\[display\\?_podcast\].*\n?")
    # Pattern 2: Matches any line starting with '**Date:**' (with optional colons).
    date_pattern = re.compile(r"\*\*Date:?\*\*:?.*\n?")

    # Counters for the final summary.
    files_processed = 0
    files_cleaned = 0

    try:
        filenames = os.listdir(SOURCE_DIR)
    except FileNotFoundError:
        print(f"Error: The source directory '{SOURCE_DIR}' was not found.")
        return

    for filename in filenames:
        if filename.lower().endswith(".md"):
            files_processed += 1
            source_path = os.path.join(SOURCE_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename)

            try:
                with open(source_path, 'r', encoding='utf-8') as source_file:
                    original_content = source_file.read()

                # Apply the cleaning patterns.
                content = podcast_pattern.sub("", original_content)
                content = date_pattern.sub("", content)

                # Check if any changes were actually made.
                if original_content != content:
                    files_cleaned += 1
                    print(f"  - Cleaned '{filename}'")

                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(content)

            except Exception as e:
                print(f"Could not process file '{filename}'. Error: {e}")

    print(f"\nDone! Processed {files_processed} files. Found and removed artifacts from {files_cleaned} files.")


if __name__ == "__main__":
    main()