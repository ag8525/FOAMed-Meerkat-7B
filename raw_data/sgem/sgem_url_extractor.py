"""
This script extracts individual SGEM episode URLs from locally saved HTML
archive pages.

It scans a specified directory for HTML or text files, parses their content
to find all hyperlinks, and filters them to keep only the links that point
to specific SGEM episodes. The filtering is done using a regular expression
that matches the typical URL structure of an episode page (e.g., '/2023/09/...').

The final list of unique URLs is sorted in reverse chronological order and
saved to a text file.
"""

import os
import re
from typing import Set

from bs4 import BeautifulSoup

# --- Configuration ---
SOURCE_ARCHIVE_DIR = 'sgemurls'
OUTPUT_URL_FILE = 'sgem_all_episode_urls.txt'


def main():
    """
    Main function to orchestrate the URL extraction process.
    """
    episode_links: Set[str] = set()

    try:
        filenames = os.listdir(SOURCE_ARCHIVE_DIR)
    except FileNotFoundError:
        print(f"Error: The source directory '{SOURCE_ARCHIVE_DIR}' was not found.")
        return

    print(f"Found {len(filenames)} files to process in '{SOURCE_ARCHIVE_DIR}'...")

    for filename in filenames:
        # Process only .txt and .html files
        if not (filename.endswith('.txt') or filename.endswith('.html')):
            continue

        file_path = os.path.join(SOURCE_ARCHIVE_DIR, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all anchor tags with an 'href' attribute
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # Filter for links that look like episode pages (containing /YYYY/MM/)
                if re.search(r'/20\d\d/\d\d/', href):
                    # Remove URL fragments (e.g., #comments) to get the base URL
                    base_href = href.split('#')[0]
                    episode_links.add(base_href)
            
            print(f"Processed '{filename}'")

        except Exception as e:
            print(f"Could not process file '{filename}'. Error: {e}")

    # Deduplicate (handled by the set) and sort the links, newest first.
    sorted_links = sorted(list(episode_links), reverse=True)

    # Save the final list of URLs to the output file.
    try:
        with open(OUTPUT_URL_FILE, 'w', encoding='utf-8') as f:
            for url in sorted_links:
                f.write(url + '\n')
    except IOError as e:
        print(f"Error writing to output file '{OUTPUT_URL_FILE}': {e}")
        return

    print(f"\nExtraction complete. Saved {len(sorted_links)} unique episode URLs to '{OUTPUT_URL_FILE}'.")


if __name__ == "__main__":
    main()