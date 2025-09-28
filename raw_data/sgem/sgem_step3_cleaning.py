"""
This script performs a third and final cleaning pass on the SGEM Markdown files.

Its purpose is to clean up and simplify various types of Markdown links,
image tags, and in-text citations, preparing the content for final processing.

The cleaning process involves three main steps:
1.  Removes complex, nested Markdown image links.
2.  Removes all standard Markdown image links.
3.  Simplifies all standard hyperlinks to just their link text, removing the URL.
"""

import os
import re
from typing import List

# --- Configuration ---
SOURCE_DIR = 'sgem_step2_cleaned'
OUTPUT_DIR = 'sgem_step3_cleaned'


def clean_links_and_citations(content: str) -> str:
    """
    Cleans various link and citation patterns from a content string.

    Args:
        content: The string content of a markdown file.

    Returns:
        The cleaned content string.
    """
    # Pattern 1: Remove complex nested image links, e.g., [![](url1)](url2)
    # These are often used to make an image a clickable link.
    nested_image_pattern = re.compile(r'\[!\[.*?\]\(.*?\)\]\(.*?\)\s?')
    content = nested_image_pattern.sub(' ', content)

    # Pattern 2: Remove all standard markdown image links, e.g., ![alt text](url)
    image_pattern = re.compile(r'!\[.*?\]\(.*?\)\s?')
    content = image_pattern.sub(' ', content)

    # Pattern 3: Simplify all remaining hyperlinks to just their text content.
    # e.g., [Click here](some_url.com) becomes "Click here".
    hyperlink_pattern = re.compile(r'\[(.*?)\]\(.*?\)')
    content = hyperlink_pattern.sub(r'\1', content)

    return content


def main():
    """
    Main function to orchestrate the cleaning of links and citations from all files.
    """
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory not found at '{SOURCE_DIR}'")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        filenames = os.listdir(SOURCE_DIR)
    except FileNotFoundError:
        print(f"Error: The source directory '{SOURCE_DIR}' was not found.")
        return

    print(f"Starting final cleaning of links and citations...")
    print(f"Source: '{SOURCE_DIR}'")
    print(f"Destination: '{OUTPUT_DIR}'")

    files_processed = 0
    for filename in filenames:
        if filename.lower().endswith(".md"):
            source_path = os.path.join(SOURCE_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename)

            try:
                with open(source_path, 'r', encoding='utf-8') as source_file:
                    original_content = source_file.read()

                # Apply the cleaning function.
                final_content = clean_links_and_citations(original_content)

                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(final_content)
                
                files_processed += 1

            except Exception as e:
                print(f"Could not process file '{filename}'. Error: {e}")
    
    print(f"\nDone! Processed and cleaned {files_processed} files.")


if __name__ == "__main__":
    main()