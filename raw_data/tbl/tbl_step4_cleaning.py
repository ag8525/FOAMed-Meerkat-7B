"""
This script serves as the final validation and formatting cleanup tool.

Its primary purpose is to ensure that every Markdown file has a perfectly
formed YAML Front Matter block. Sometimes, GPT models can mistakenly wrap the
YAML in code fences (e.g., ```yaml) or add extra delimiters. This script
corrects those common errors programmatically.

The process is as follows:
1.  Reads each Markdown file from the input directory.
2.  Intelligently separates the metadata section from the main content by
    locating the first H1 heading ('# ').
3.  Cleans the metadata section by stripping away any extraneous wrappers or
    delimiters, while carefully preserving the actual key-value content,
    including multi-line summaries.
4.  Rebuilds the file with a guaranteed-correct YAML block (starting and
    ending with '---') followed by the original main content.
5.  Saves the corrected file to a new output directory.
"""

import os
from typing import List

# --- Configuration ---
INPUT_DIR = 'step3_cleaned_articles'
OUTPUT_DIR = 'step4_cleaned_articles'


def fix_and_validate_file_format(filename: str):
    """
    Processes a single file to fix its YAML Front Matter.

    Args:
        filename: The name of the file to process.
    """
    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(output_path):
        print(f"Skipping '{filename}', output file already exists.")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading '{filename}': {e}")
        return

    if not lines:
        print(f"Skipping empty file: '{filename}'")
        return
        
    print(f"Processing '{filename}'...")
    
    # 1. Find the start of the main content. We assume the main content
    #    always begins with the first H1 Markdown heading (e.g., '# Title...').
    content_start_index = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('# '):
            content_start_index = i
            break
    
    # 2. Separate the file into the metadata section and the main content.
    metadata_lines = lines[:content_start_index]
    main_content_lines = lines[content_start_index:]
    
    # 3. Clean the metadata block itself, preserving all its content.
    #    This logic carefully extracts only the valid metadata lines,
    #    ignoring any incorrect wrappers or extra delimiters.
    clean_metadata_lines: List[str] = []
    in_metadata_block = False
    for line in metadata_lines:
        stripped_line = line.strip()
        
        # A line is considered part of the metadata if it contains a colon.
        # This marks the beginning of the actual content to preserve.
        if ':' in stripped_line and not in_metadata_block:
            in_metadata_block = True
        
        # Ignore any blank lines before the metadata content begins.
        if not in_metadata_block and not stripped_line:
            continue
        
        # Once inside the block, add all lines except for junk wrappers.
        if in_metadata_block:
            if stripped_line not in ('---', '```', '```yaml', '```markdown'):
                # Append the original line to preserve indentation for multi-line summaries.
                clean_metadata_lines.append(line)

    # 4. Rebuild the file with a perfect YAML Front Matter block.
    try:
        with open(output_path, 'w', encoding='utf-8') as output_file:
            # Write the opening delimiter
            output_file.write('---\n')
            
            # Write the cleaned metadata lines
            output_file.writelines(clean_metadata_lines)
            
            # Write the closing delimiter
            output_file.write('---\n')

            # Add a blank line for readability between metadata and content
            output_file.write('\n')
            
            # Write the rest of the original main content
            output_file.writelines(main_content_lines)
    except Exception as e:
        print(f"Error writing '{filename}': {e}")


def main():
    """
    Main function to orchestrate the validation and fixing of all files.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        files_to_process = [
            f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.md')
        ]
    except FileNotFoundError:
        print(f"Error: Input directory '{INPUT_DIR}' not found. Exiting.")
        return

    if not files_to_process:
        print(f"No .md files found in '{INPUT_DIR}'.")
        return

    print(f"Found {len(files_to_process)} markdown files to process.")
    
    processed_count = 0
    for filename in files_to_process:
        fix_and_validate_file_format(filename)
        processed_count += 1

    print(f"\nProcessing complete. Processed {processed_count} files.")
    print(f"Corrected files are saved in the '{OUTPUT_DIR}' directory.")


if __name__ == "__main__":
    main()