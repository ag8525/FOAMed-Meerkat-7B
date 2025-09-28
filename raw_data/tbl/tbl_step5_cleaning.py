# -*- coding: utf-8 -*-
"""
This script performs the final renaming and organization of the cleaned
Markdown files from 'The Bottom Line' source.

It implements a robust, safe renaming strategy:
1.  **Standardized Renaming**: It attempts to extract a clean "study name"
    from the beginning of each filename (e.g., '3mg-trial_final.md') and
    renames it to a standard format (e.g., 'tbl-3mg-trial.md').
2.  **Conflict Resolution**: If a renamed file would overwrite an existing file,
    it assumes a naming collision. To prevent data loss, it moves *both* the
    existing file and the new conflicting file to a 'review' directory for
    manual inspection.
3.  **Ambiguous Name Handling**: If the script cannot extract a valid study
    name from a filename, it considers the name ambiguous and moves the file
    to the 'review' directory.
4.  **Logging**: All actions (matches, conflicts, ambiguities) are recorded in
    a detailed log file for traceability.
"""

import os
import re
import shutil

# --- Configuration ---
SOURCE_DIR = "step4_cleaned_articles"
FINAL_OUTPUT_DIR = "step5_cleaned_articles/"
REVIEW_DIR = "review_tbl/"
LOG_FILE_PATH = "rename_log_tbl.txt"


def setup_directories_and_log():
    """Initializes output directories and the log file."""
    os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)
    os.makedirs(REVIEW_DIR, exist_ok=True)
    
    with open(LOG_FILE_PATH, 'w', encoding='utf-8') as log_file:
        log_file.write("--- TBL File Renaming Log ---\n")
        log_file.write(f"Source Directory: {SOURCE_DIR}\n")
        log_file.write("-------------------------------------\n")


def main():
    """
    Main function to orchestrate the final file processing and renaming.
    """
    setup_directories_and_log()
    print("--- Starting Final TBL File Processing ---")

    try:
        all_filenames = os.listdir(SOURCE_DIR)
        all_filenames.sort()  # Process files in a predictable order
    except FileNotFoundError:
        print(f"Error: Source directory not found at '{SOURCE_DIR}'. Exiting.")
        return

    # Counters for the final summary report
    processed_count = 0
    conflict_count = 0
    ambiguous_count = 0

    for filename in all_filenames:
        source_path = os.path.join(SOURCE_DIR, filename)

        # Ensure we only process files, not directories
        if not os.path.isfile(source_path):
            continue

        # Use regex to find the first continuous block of letters, numbers, or hyphens.
        # This is assumed to be the study name (e.g., '3mg-trial' from '3mg-trial_final.md').
        match = re.match(r'([a-zA-Z0-9-]+)', filename, re.IGNORECASE)

        if match:
            # --- Case 1: A valid study name was found ---
            study_name = match.group(1).lower()
            new_filename = f"tbl-{study_name}.md"
            new_path = os.path.join(FINAL_OUTPUT_DIR, new_filename)

            with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log_file:
                log_file.write(
                    f"[Matched] Original: {filename}\n"
                    f"          -> New Name: {new_filename}\n---\n"
                )

            if os.path.exists(new_path):
                # --- Conflict Detected ---
                # To prevent overwriting, move both files to the review directory.
                print(f"Conflict for '{new_filename}'! Moving both files to review.")
                
                # 1. Move the file that *already exists* in the output folder to review.
                shutil.move(new_path, os.path.join(REVIEW_DIR, new_filename))
                
                # 2. Copy the *current* file being processed to review.
                shutil.copy2(source_path, os.path.join(REVIEW_DIR, filename))
                
                conflict_count += 2  # Increment by 2 as two files were affected
            else:
                # --- No Conflict: Success Case ---
                shutil.copy2(source_path, new_path)
                print(f"Processed: '{filename}' -> '{new_filename}'")
                processed_count += 1
        else:
            # --- Case 2: No valid study name pattern was found ---
            print(f"Ambiguous: '{filename}' name not recognized. Moving to review.")
            
            with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log_file:
                log_file.write(
                    f"[Ambiguous] Original: {filename}\n"
                    f"             -> Moved to Review\n---\n"
                )
                
            shutil.copy2(source_path, os.path.join(REVIEW_DIR, filename))
            ambiguous_count += 1
            
    # --- Final Summary Report ---
    print("\n--- Final Processing Complete ---")
    print(f"Successfully processed and renamed: {processed_count} files.")
    print(f"Files moved to review due to naming conflicts: {conflict_count}.")
    print(f"Files moved to review due to ambiguous names: {ambiguous_count}.")
    print(f"A complete log has been saved to '{LOG_FILE_PATH}'")


if __name__ == "__main__":
    main()