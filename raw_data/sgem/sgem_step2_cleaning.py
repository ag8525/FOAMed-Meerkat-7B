"""
This script performs a second cleaning pass on the SGEM Markdown files.

Its primary purpose is to truncate each file at the first occurrence of several
predefined key phrases (e.g., "Keener Kontest", "Remember to be skeptical...").
This effectively removes recurring boilerplate content, such as contest announcements
and sign-offs, from the end of the show notes.

The script finds the earliest appearance of any of the target phrases and cuts
the file off starting from the beginning of that line.
"""

import os
from typing import List

# --- Configuration ---
SOURCE_DIR = 'sgem_step1_cleaned'
OUTPUT_DIR = 'sgem_step2_cleaned'

# The list of case-insensitive phrases that will trigger the truncation.
# The script will cut the file at the first one it encounters.
TRUNCATION_PHRASES: List[str] = [
    "Remember to be skeptical of anything",
    "Keener Kontest",
    "Keener Contest",
    "keener question",
    "Keener"
]


def main():
    """
    Main function to orchestrate the file truncation process.
    """
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory not found at '{SOURCE_DIR}'")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output will be saved in: '{OUTPUT_DIR}'")

    # Counters for the final summary.
    files_processed = 0
    files_truncated = 0

    try:
        filenames = os.listdir(SOURCE_DIR)
    except FileNotFoundError:
        print(f"Error: The source directory '{SOURCE_DIR}' was not found.")
        return

    print(f"Processing files from '{SOURCE_DIR}'...")

    for filename in filenames:
        if not filename.lower().endswith(".md"):
            continue

        files_processed += 1
        source_path = os.path.join(SOURCE_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        try:
            with open(source_path, 'r', encoding='utf-8') as source_file:
                content = source_file.read()

            # --- Find the earliest occurrence of any truncation phrase ---
            first_occurrence_index = -1
            content_lower = content.lower()

            for phrase in TRUNCATION_PHRASES:
                index = content_lower.find(phrase.lower())
                # If the phrase is found, check if it's the earliest one yet.
                if index != -1:
                    if first_occurrence_index == -1 or index < first_occurrence_index:
                        first_occurrence_index = index

            # --- Truncate the file content if a phrase was found ---
            if first_occurrence_index != -1:
                files_truncated += 1
                # Find the start of the line where the phrase was found
                # to ensure the entire line is removed.
                cut_point = content.rfind('\n', 0, first_occurrence_index) + 1
                cleaned_content = content[:cut_point]
                print(f"  - Truncated '{filename}'")
            else:
                # If no phrases were found, keep the original content.
                cleaned_content = content

            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(cleaned_content)

        except Exception as e:
            print(f"Could not process file '{filename}'. Error: {e}")

    print(f"\nDone! Processed {files_processed} files. Found and truncated {files_truncated} files.")


if __name__ == "__main__":
    main()