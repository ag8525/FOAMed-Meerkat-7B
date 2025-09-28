"""
This script automates the conversion of PDF files from the CRACKCast
shownotes into plain text (.txt) files.

It recursively scans a source directory for PDFs, extracts the full text
content from each file, and saves it to a single, flat output directory.

A metadata header is prepended to each text file, containing the topic,
the original source folder, and the original filename for future reference.
"""

import os
import re
import fitz  # PyMuPDF library for PDF processing

# --- Configuration ---
SOURCE_PDF_ROOT = "CRACKCast_Shownotes"
OUTPUT_TXT_ROOT = "step1_cleaned_shownotes" 


def sanitize_filename(name: str) -> str:
    """
    Cleans a string to make it a safe and consistent filename.

    The process includes:
    - Lowercasing the string.
    - Replacing spaces with dashes.
    - Removing all period characters.
    - Removing any characters that are not alphanumeric, dash, or underscore.

    Args:
        name: The input string to sanitize.

    Returns:
        The sanitized string.
    """
    name = name.lower()
    name = name.replace(" ", "-")
    name = name.replace(".", "")  # Remove all dots
    name = re.sub(r'[^a-z0-9\-_]', '', name)
    return name


def main():
    """
    Main function to orchestrate the PDF to text conversion process.
    """
    os.makedirs(OUTPUT_TXT_ROOT, exist_ok=True)
    print(f"Starting PDF to text conversion...")
    print(f"Source Directory: '{SOURCE_PDF_ROOT}'")
    print(f"Output Directory: '{OUTPUT_TXT_ROOT}' (Flattened)")

    # Recursively walk through the source directory
    for root, _, files in os.walk(SOURCE_PDF_ROOT):
        for filename in files:
            if not filename.lower().endswith(".pdf"):
                continue

            pdf_path = os.path.join(root, filename)

            try:
                # --- Path and Metadata Generation ---
                relative_path = os.path.relpath(pdf_path, SOURCE_PDF_ROOT)
                folder_path = os.path.dirname(relative_path)
                main_topic = os.path.basename(folder_path)
                base_name = os.path.splitext(filename)[0]
                topic_value = f"{main_topic} - {base_name.replace('Ch.', '').strip()}"

                # Sanitize components
                sanitized_base_name = sanitize_filename(base_name)
                sanitized_folder_name = sanitize_filename(folder_path)

                # Combine folder and file name for a unique name in the flat directory
                unique_filename = f"{sanitized_folder_name}-{sanitized_base_name}.txt"
                txt_path = os.path.join(OUTPUT_TXT_ROOT, unique_filename)
                # No need to create subdirectories anymore

                # --- PDF Text Extraction ---
                with fitz.open(pdf_path) as doc:
                    text = "".join(page.get_text() for page in doc)

                # --- File Writing ---
                metadata = (
                    f"# Metadata\n"
                    f"- topic: {topic_value}\n"
                    f"- source_folder: {folder_path}\n"
                    f"- original_file: {filename}\n\n"
                )
                
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(metadata)
                    f.write(text)

                print(f"Extracted: {pdf_path} -> {txt_path}")

            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")

    print("\nAll PDFs have been processed.")


if __name__ == "__main__":
    main()