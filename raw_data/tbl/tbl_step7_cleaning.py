"""
This script performs the final content unification for "The Bottom Line" (TBL)
files.

Its purpose is to distill the processed Markdown files into a final, concise
format by keeping only the most essential clinical sections.

The process is as follows:
1.  Reads each Markdown file from the input directory.
2.  Parses the YAML front matter, cleaning it of common formatting issues first.
3.  Splits the main body of the document into sections based on Markdown headings.
4.  Filters these sections, retaining only a predefined set: "Summary,"
    "Clinical Point," "Background," and "Bottom Line."
5.  Reassembles the file with the cleaned YAML block followed by the essential
    sections in a fixed, logical order.
6.  Saves the final, unified file to the output directory.
"""

import os
import re
from typing import Dict, Any

import yaml

# --- Configuration ---
INPUT_DIR = "step6_cleaned_articles"
OUTPUT_DIR = "step7_cleaned_articles"

# Define the exact headers of the sections to keep from the TBL files.
# The keys are lowercased for easy matching, and values are the desired final format.
KEEP_TBL_HEADERS = {
    "clinical point": "## Clinical Point",
    "background":     "## Background",
    "bottom line":    "## Bottom Line",
}


def pre_clean_yaml(yaml_text: str) -> str:
    """
    Cleans up common YAML parsing issues before loading.

    This handles specific problems like stray '@' characters from author names
    and values that contain colons, which can break the parser.

    Args:
        yaml_text: The raw string content from the YAML block.

    Returns:
        A cleaned YAML string that is safer to parse.
    """
    cleaned_text = yaml_text.replace('@', '')  # Remove characters that are not needed
    
    # Enforce proper key: value formatting and quote values containing colons
    cleaned_lines = []
    for line in cleaned_text.split('\n'):
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip()
            # If a value itself contains a colon, it must be quoted for valid YAML
            if ':' in value and not (value.startswith('"') and value.endswith('"')):
                value = f'"{value}"'
            cleaned_lines.append(f"{key}: {value}")
        else:
            cleaned_lines.append(line)
            
    return "\n".join(cleaned_lines)


def process_tbl_file(body_content: str, metadata: Dict[str, Any]) -> str:
    """
    Filters and reorders sections of a TBL file to create the final content.

    Args:
        body_content: The main Markdown content of the file (after the YAML block).
        metadata: The parsed YAML data as a dictionary.

    Returns:
        The final, unified content as a single string.
    """
    # 1. Extract the summary from the metadata and prepare the final sections dict.
    summary_text = metadata.pop("summary", "").strip()
    final_sections = {}
    if summary_text:
        final_sections["## Summary"] = summary_text

    # 2. Split the body into sections using a regex that looks for headings.
    sections = re.split(r'\n(?=##? .*)', body_content)

    # 3. Iterate through sections and keep only those defined in KEEP_TBL_HEADERS.
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        
        header_match = re.match(r'##? (.*)', sec)
        if not header_match:
            continue
        
        header_text = header_match.group(1).strip().lower()
        if header_text in KEEP_TBL_HEADERS:
            target_header = KEEP_TBL_HEADERS[header_text]
            # Extract the content part of the section (everything after the heading).
            content_part = re.sub(r'##? .*', '', sec, count=1).strip()
            final_sections[target_header] = content_part

    # 4. Assemble the final content in a predefined order.
    ordered_body = ""
    section_order = ["## Summary", "## Clinical Point", "## Background", "## Bottom Line"]
    for header in section_order:
        if header in final_sections:
            # Add extra newlines for proper Markdown rendering.
            ordered_body += f"{header}\n\n{final_sections[header]}\n\n"
            
    # 5. Re-generate the YAML block and combine with the ordered body.
    final_content = ""
    if metadata:
        # Dump the remaining metadata back into a clean YAML string.
        new_yaml_text = yaml.dump(
            metadata, sort_keys=False, default_flow_style=False, allow_unicode=True
        ).strip()
        final_content = f"---\n{new_yaml_text}\n---\n\n"
        
    final_content += ordered_body.strip()
    return final_content


def main():
    """
    Main function to orchestrate the processing of all TBL files.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Processing TBL files from '{INPUT_DIR}'...")

    try:
        files_to_process = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".md")]
    except FileNotFoundError:
        print(f"? Error: Input directory '{INPUT_DIR}' not found. Exiting.")
        return

    for filename in files_to_process:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(output_path):
            print(f"  - Skipping '{filename}', output file already exists.")
            continue

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                raw_content = f.read()

            # Split the file into YAML front matter and body content.
            parts = raw_content.split('---', 2)
            if len(parts) < 3:
                raise ValueError("File does not contain a valid YAML front matter block.")

            yaml_text = parts[1]
            body_content = parts[2]
            
            # Clean and load the YAML data.
            cleaned_yaml_text = pre_clean_yaml(yaml_text)
            yaml_data = yaml.safe_load(cleaned_yaml_text) or {}
            
            # Process the file content.
            cleaned_content = process_tbl_file(body_content, yaml_data)

            # Write the final, unified content to the output file.
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned_content)
            print(f"  - ? Cleaned and saved '{filename}'")

        except Exception as e:
            print(f"  - ?? ERROR processing '{filename}': {e}")

    print(f"\nProcessing complete. Unified files are in '{OUTPUT_DIR}' ?")


if __name__ == "__main__":
    main()