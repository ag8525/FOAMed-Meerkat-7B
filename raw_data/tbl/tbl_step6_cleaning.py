"""
This script performs a final text replacement task on a directory of
cleaned Markdown files.

Its specific purpose is to standardize terminology by replacing any lingering
instances of the whole words "Question" or "Answer" with the word "Point".
This is useful for ensuring consistency in section headings like
"## Clinical Question" across all documents.

The process is as follows:
1.  Reads all .md files from a specified source folder.
2.  Uses a case-insensitive regular expression to find and replace the
    target words.
3.  Saves the modified content to a new file in an output folder, preserving
    the original filename.
"""

import os
import re

def standardize_markdown_files(source_folder: str, output_folder: str) -> None:
    """
    Reads .md files, replaces 'Question' and 'Answer' with 'Point',
    and saves them to a new location.

    Args:
        source_folder: The path to the directory containing the original .md files.
        output_folder: The path to the directory where cleaned files will be saved.
    """
    # Create the output folder if it doesn't already exist.
    os.makedirs(output_folder, exist_ok=True)
    print(f"? Output folder is ready at: '{output_folder}'")

    try:
        files_to_process = os.listdir(source_folder)
    except FileNotFoundError:
        print(f"? Error: The source folder '{source_folder}' was not found.")
        print("Please ensure the folder name in the configuration is correct.")
        return

    print(f"Found {len(files_to_process)} items in the source folder.")

    # Loop through each file in the source directory.
    for filename in files_to_process:
        # Process only files with a .md extension.
        if filename.lower().endswith(".md"):
            source_filepath = os.path.join(source_folder, filename)
            output_filepath = os.path.join(output_folder, filename)

            print(f"Processing '{filename}'...")

            try:
                # Read the content of the source file.
                with open(source_filepath, 'r', encoding='utf-8') as source_file:
                    content = source_file.read()

                # Perform a case-insensitive replacement of "Question" or "Answer".
                # The pattern r'\b(Question|Answer)\b' uses word boundaries (\b)
                # to ensure we only match whole words and not partial words
                # like "Questionnaire".
                cleaned_content = re.sub(
                    r'\b(Question|Answer)\b',
                    'Point',
                    content,
                    flags=re.IGNORECASE
                )

                # Write the modified content to the new file in the output directory.
                with open(output_filepath, 'w', encoding='utf-8') as output_file:
                    output_file.write(cleaned_content)

            except Exception as e:
                print(f"  - ?? Could not process file {filename}. Error: {e}")

    print("\n? All Markdown files have been processed successfully!")


if __name__ == "__main__":
    # --- Configuration ---
    SOURCE_DIRECTORY = "step5_cleaned_articles"
    OUTPUT_DIRECTORY = "step6_cleaned_articles"
    # -------------------

    standardize_markdown_files(SOURCE_DIRECTORY, OUTPUT_DIRECTORY)