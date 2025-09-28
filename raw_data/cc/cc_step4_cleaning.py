"""
This script performs the final renaming and organization of the cleaned
Markdown files from the CRACKCast source.

It uses a "first number" rule to create a standardized filename:
1.  **Standardized Renaming**: It scans each filename for the first sequence
    of digits, which is assumed to be the episode number. It then renames the
    file to a standard format (e.g., 'cc-186.md').
2.  **Conflict Resolution**: If a renamed file would overwrite an existing file,
    it assumes a naming collision. To prevent data loss, it moves *both* the
    existing file and the new conflicting file to a 'review' directory.
3.  **No-Number Handling**: If the script cannot find any digits in a filename,
    it considers the name ambiguous and moves the file to the 'review' directory.
4.  **Logging**: All actions are recorded in a detailed log file.
"""

import os
import re
import shutil

# --- Configuration ---
SOURCE_DIR = "step4_cleaned_shownotes"
FINAL_OUTPUT_DIR = "step5_cleaned_shownotes"
REVIEW_DIR = "review_cc/"
LOG_FILE_PATH = "rename_log_cc.txt"


def setup_directories_and_log():
    """Initializes output directories and the log file."""
    os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)
    os.makedirs(REVIEW_DIR, exist_ok=True)
    
    with open(LOG_FILE_PATH, 'w', encoding='utf-8') as log_file:
        log_file.write("--- CRACKCast File Renaming Log ---\n")
        log_file.write(f"Source Directory: {SOURCE_DIR}\n")
        log_file.write("-------------------------------------\n")


def main():
    """
    Main function to orchestrate the final file processing and renaming.
    """
    setup_directories_and_log()
    print("--- Starting Final CRACKCast File Processing ---")

    try:
        all_filenames = os.listdir(SOURCE_DIR)
        all_filenames.sort()  # Process files in a predictable order
    except FileNotFoundError:
        print(f"Error: Source directory not found at '{SOURCE_DIR}'. Exiting.")
        return

    # Counters for the final summary report
    processed_count = 0
    conflict_count = 0
    no_number_count = 0

    for filename in all_filenames:
        source_path = os.path.join(SOURCE_DIR, filename)

        # Ensure we only process files, not directories
        if not os.path.isfile(source_path):
            continue

        # Find the first sequence of one or more digits (\d+) in the filename.
        match = re.search(r'(\d+)', filename)

        if match:
            # --- Case 1: An episode number was found ---
            # Convert to int and back to string to remove leading zeros (e.g., '09' -> '9').
            episode_number = str(int(match.group(1)))
            new_filename = f"cc-{episode_number}.md"
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
                # 1. Move the file that *already exists* in the output folder.
                shutil.move(new_path, os.path.join(REVIEW_DIR, new_filename))
                # 2. Copy the *current* file being processed to review.
                shutil.copy2(source_path, os.path.join(REVIEW_DIR, filename))
                conflict_count += 2
            else:
                # --- No Conflict: Success Case ---
                shutil.copy2(source_path, new_path)
                print(f"Processed: '{filename}' -> '{new_filename}'")
                processed_count += 1
        else:
            # --- Case 2: No number was found in the filename ---
            print(f"No Number: '{filename}'. Moving to review.")
            with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log_file:
                log_file.write(
                    f"[No Number] Original: {filename}\n"
                    f"             -> Moved to Review\n---\n"
                )
            shutil.copy2(source_path, os.path.join(REVIEW_DIR, filename))
            no_number_count += 1
            
    # --- Final Summary Report ---
    print("\n--- Processing Complete ---")
    print(f"Successfully processed and renamed: {processed_count} files.")
    print(f"Files moved to review due to naming conflicts: {conflict_count}.")
    print(f"Files moved to review because no number was found: {no_number_count}.")
    print(f"A complete log has been saved to '{LOG_FILE_PATH}'")


if __name__ == "__main__":
    main()