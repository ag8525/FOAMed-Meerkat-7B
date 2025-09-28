"""
This script performs a final structural transformation on the CRACKCast
Markdown files.

Its specific purpose is to move the clinical summary from the YAML front
matter block into the main body of the document.

The process is as follows:
1.  Reads each Markdown file from the input directory.
2.  Parses the YAML front matter to find and extract the 'summary' field.
3.  Removes the 'summary' key from the YAML data.
4.  Prepends the extracted summary text to the main content under a new
    '## Summary' heading.
5.  Reconstructs the file, only including a YAML block if other metadata
    keys still exist.
6.  Saves the final, correctly structured file to the output directory.
"""

import os
from typing import Dict, Any

import yaml

# --- Configuration ---
INPUT_DIR = "step6_cleaned_shownotes"
OUTPUT_DIR = "step7_cleaned_shownotes"


def move_summary_from_yaml_to_body(raw_file_content: str) -> str:
    """
    Parses a markdown file, moves the 'summary' key from the YAML front
    matter to the top of the main content under a '## Summary' heading.

    If no summary exists, it returns the original content unchanged.

    Args:
        raw_file_content: The full string content of the markdown file.

    Returns:
        The processed file content as a string.
    """
    try:
        # Split the content into front matter and main body.
        # The '2' ensures it only splits on the first two '---' delimiters.
        parts = raw_file_content.split('---', 2)
        if len(parts) < 3:
            # This file doesn't have a valid front matter structure.
            return raw_file_content

        frontmatter_str = parts[1]
        main_content = parts[2]

        # Load the YAML data from the front matter string.
        yaml_data: Dict[str, Any] = yaml.safe_load(frontmatter_str) or {}

        # Ensure the parsed YAML is a dictionary before proceeding.
        if not isinstance(yaml_data, dict):
             print(f"WARNING: YAML front matter is not a valid dictionary. Skipping.")
             return raw_file_content

        # Check for and 'pop' the summary. pop() gets the value and removes the key.
        if 'summary' in yaml_data:
            summary_text = yaml_data.pop('summary', '').strip()

            # --- Reconstruct the final file ---
            # 1. Create the new YAML block (if any metadata is left).
            updated_yaml_str = ""
            if yaml_data:  # Only add YAML block if there's remaining metadata.
                updated_yaml_str = yaml.dump(
                    yaml_data,
                    sort_keys=False,
                    default_flow_style=False,
                    allow_unicode=True
                ).strip()

            # 2. Create the new summary section for the main text.
            summary_section = f"## Summary\n\n{summary_text}\n\n"

            # 3. Assemble the final content.
            if updated_yaml_str:
                # If metadata remains, include the --- delimiters.
                final_content = (
                    f"---\n{updated_yaml_str}\n---\n\n"
                    f"{summary_section}{main_content.lstrip()}"
                )
            else:
                # If no metadata is left, omit the --- block entirely.
                final_content = f"{summary_section}{main_content.lstrip()}"

            return final_content
        else:
            # No 'summary' key found, return the original content unchanged.
            return raw_file_content

    except (yaml.YAMLError, IndexError) as e:
        # Handle cases where the file is malformed.
        print(f"WARNING: Could not parse front matter for a file. Error: {e}")
        return raw_file_content


def main():
    """
    Main function to orchestrate the processing of all CRACKCast files.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Processing CRACKCast files from '{INPUT_DIR}'...")

    try:
        files_to_process = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".md")]
    except FileNotFoundError:
        print(f"Error: Input directory '{INPUT_DIR}' not found. Exiting.")
        return

    for filename in files_to_process:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(output_path):
            print(f"Skipping '{filename}', already exists.")
            continue

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                raw_content = f.read()

            # Process the file using the main logic function.
            processed_content = move_summary_from_yaml_to_body(raw_content)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(processed_content)
            print(f"Processed and saved '{filename}'")
            
        except Exception as e:
            print(f"ERROR processing '{filename}': {e}")

    print(f"\nProcessing complete. Final files are in '{OUTPUT_DIR}' ?")


if __name__ == "__main__":
    main()