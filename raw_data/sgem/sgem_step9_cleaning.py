"""
This script performs the final, standardized renaming of the SGEM Markdown files.

It scans a directory of processed files and renames them based on the SGEM
episode number found in the original filename.

The process is as follows:
1.  **Episode Number Extraction**: It uses a regular expression to find the
    episode number (e.g., the '123' in 'SGEM#123_some_topic.md').
2.  **Standardized Renaming**: It renames the file to a standard format:
    'sgem-{episode_number}.md'.
3.  **Collision Handling**: If a file with the target name already exists
    (e.g., from a re-run or duplicate episode), it appends a counter
    (e.g., 'sgem-123-1.md', 'sgem-123-2.md') to prevent overwriting data.
4.  **Skipping**: Files that do not match the expected SGEM naming pattern are
    skipped.
"""

import os
import re
import shutil

# --- Configuration ---
SOURCE_DIR = "sgem_step8_cleaned"
OUTPUT_DIR = "sgem_step9_cleaned"


def main():
    """
    Main function to orchestrate the file renaming and copying process.
    """
    print(f"--- Starting final SGEM file processing ---")
    print(f"Source:      '{SOURCE_DIR}'")
    print(f"Destination: '{OUTPUT_DIR}'")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        all_filenames = os.listdir(SOURCE_DIR)
        all_filenames.sort()  # Process files in a predictable order
    except FileNotFoundError:
        print(f"Error: Source directory not found at '{SOURCE_DIR}'. Please check the path.")
        return

    # Counters for the final summary report
    copied_count = 0
    skipped_count = 0

    for filename in all_filenames:
        source_path = os.path.join(SOURCE_DIR, filename)

        # Ensure we only process files, not directories
        if not os.path.isfile(source_path):
            continue

        # Use regex to find "SGEM" followed by '#' or '_', and capture the digits.
        match = re.search(r'SGEM[#_](\d+)', filename, re.IGNORECASE)

        if match:
            episode_number = match.group(1)
            
            # --- Filename Collision Handling ---
            base_name = f"sgem-{episode_number}"
            extension = ".md"
            new_filename = f"{base_name}{extension}"
            output_path = os.path.join(OUTPUT_DIR, new_filename)
            
            # If a file with this name already exists, append a counter.
            counter = 1
            while os.path.exists(output_path):
                new_filename = f"{base_name}-{counter}{extension}"
                output_path = os.path.join(OUTPUT_DIR, new_filename)
                counter += 1

            # --- Copy the file ---
            try:
                # Use shutil.copy2 to copy the file and preserve metadata.
                shutil.copy2(source_path, output_path)
                print(f"Copied: '{filename}'  ->  '{new_filename}'")
                copied_count += 1
            except OSError as e:
                print(f"Error copying '{filename}': {e}")
                skipped_count += 1
        else:
            # If the filename doesn't match the 'SGEM#...' pattern, skip it.
            print(f"? Skipped: '{filename}' (pattern not found)")
            skipped_count += 1
    
    print("\n--- Processing Complete ---")
    print(f"Successfully copied and renamed: {copied_count} files.")
    print(f"Skipped (pattern not found or error): {skipped_count} files.")


if __name__ == "__main__":
    main()