"""
This script serves as an interactive Quality Check (QC) tool to review
significant changes between two sets of files.

It is designed to help identify cases where a cleaning script may have
aggressively removed too much content.

The process is as follows:
1.  Compares the file sizes of corresponding files in an 'original' and a
    'cleaned' directory.
2.  Flags any file where the size has been reduced by more than a configurable
    threshold (e.g., 70%).
3.  Initiates an interactive review session, displaying a full, color-coded,
    line-by-line comparison ('diff') for each flagged file.
4.  Pauses after each comparison, allowing the user to review the changes
    before proceeding to the next file.
"""

import os
import difflib

# --- Configuration ---
# Directory with the files before the cleaning step in question.
ORIGINAL_DIR = 'sgem_step10_cleaned'
# Directory with the files after the cleaning step.
CLEANED_DIR = 'sgem_step11_cleaned'
# The percentage of size reduction that will trigger a manual review.
# For example, 0.7 means a file will be flagged if it is >70% smaller.
REDUCTION_THRESHOLD = 0.7


def main():
    """
    Main function to orchestrate the file comparison and interactive review.
    """
    # --- Directory Validation ---
    if not os.path.exists(ORIGINAL_DIR):
        print(f"Error: Original directory not found at '{ORIGINAL_DIR}'")
        return
    if not os.path.exists(CLEANED_DIR):
        print(f"Error: Cleaned directory not found at '{CLEANED_DIR}'")
        return

    # --- Phase 1: Flag Files with Significant Changes ---
    flagged_files = []
    print(f"Comparing files to find significant changes (>{REDUCTION_THRESHOLD:.0%})...")

    for filename in os.listdir(ORIGINAL_DIR):
        original_path = os.path.join(ORIGINAL_DIR, filename)
        cleaned_path = os.path.join(CLEANED_DIR, filename)

        if os.path.isfile(original_path) and os.path.exists(cleaned_path):
            original_size = os.path.getsize(original_path)
            cleaned_size = os.path.getsize(cleaned_path)

            if original_size > 0:
                reduction_percent = (original_size - cleaned_size) / original_size
                if reduction_percent > REDUCTION_THRESHOLD:
                    flagged_files.append(filename)

    # --- Phase 2: Interactive Review Loop ---
    print("\n--- Quality Check Complete ---")
    if not flagged_files:
        print("No files exceeded the size reduction threshold.")
        return
    
    print(f"Found {len(flagged_files)} files exceeding threshold. Beginning interactive review:\n")
    
    for i, filename in enumerate(flagged_files):
        print(f"--- ({i+1}/{len(flagged_files)}) Comparison for: {filename} ---")
        
        original_path = os.path.join(ORIGINAL_DIR, filename)
        cleaned_path = os.path.join(CLEANED_DIR, filename)

        with open(original_path, 'r', encoding='utf-8') as f1, \
             open(cleaned_path, 'r', encoding='utf-8') as f2:
            original_lines = f1.readlines()
            cleaned_lines = f2.readlines()

        # Use difflib to compare the two lists of lines.
        matcher = difflib.SequenceMatcher(None, original_lines, cleaned_lines)

        # Process the "opcodes" to display the differences.
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for line in original_lines[i1:i2]:
                    print(f"  {line}", end='')  # Unchanged lines (no color)
            elif tag == 'delete':
                for line in original_lines[i1:i2]:
                    # Use ANSI escape codes for color in the terminal.
                    print(f'\033[91m- {line}\033[0m', end='')  # Red for deleted
            elif tag == 'insert':
                for line in cleaned_lines[j1:j2]:
                    print(f'\033[92m+ {line}\033[0m', end='')  # Green for inserted
            elif tag == 'replace':
                for line in original_lines[i1:i2]:
                    print(f'\033[91m- {line}\033[0m', end='')  # Red for original
                for line in cleaned_lines[j1:j2]:
                    print(f'\033[92m+ {line}\033[0m', end='')  # Green for replacement
        
        # Pause for user input before proceeding to the next file.
        if i < len(flagged_files) - 1:
            input("\n\nPress Enter to review the next file...")
            print("\n" + "="*50 + "\n")

    print("\n\nAll flagged files have been reviewed.")


if __name__ == "__main__":
    main()