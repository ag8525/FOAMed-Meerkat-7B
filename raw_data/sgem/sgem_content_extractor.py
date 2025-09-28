"""
This script scrapes SGEM (Skeptics' Guide to Emergency Medicine) episode pages.

It reads a list of episode URLs from a text file, then for each URL it:
1.  Downloads the HTML content of the page.
2.  Parses the HTML to extract structured metadata (title, date, guest, etc.).
3.  Isolates the main "show notes" content and removes irrelevant elements
    like audio players, navigation links, and footers.
4.  Converts the cleaned HTML content into Markdown format.
5.  Saves the final output as a .md file with a YAML front matter block
    containing the extracted metadata.
"""

import os
import re
import time
from datetime import datetime
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# --- Configuration ---
URL_LIST_FILE = "sgem_all_episode_urls.txt"
OUTPUT_DIR = "sgem_shownotes"

# Standard headers to mimic a web browser and avoid being blocked.
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}


def extract_metadata(soup: BeautifulSoup, url: str) -> Dict[str, str]:
    """
    Parses a BeautifulSoup object to extract structured metadata.

    Args:
        soup: The parsed BeautifulSoup object of an SGEM episode page.
        url: The original URL of the page.

    Returns:
        A dictionary containing the extracted metadata.
    """
    metadata = {'url': url}
    
    # Extract title from the main H1 tag
    title_tag = soup.find("h1", class_="entry-title")
    metadata['title'] = title_tag.text.strip() if title_tag else "Unknown Title"
    
    # Extract publication date from meta tag, with a fallback to the URL structure
    date_tag = soup.find("meta", property="article:published_time")
    if date_tag and date_tag.get('content'):
        metadata['date'] = date_tag['content'][:10]  # Format as YYYY-MM-DD
    else:
        match = re.search(r'/(\d{4})/(\d{2})/', url)
        metadata['date'] = f"{match.group(1)}-{match.group(2)}" if match else ""

    # Extract guest skeptic name
    guest_tag = soup.find('p', string=re.compile(r'Guest Skeptic:'))
    if guest_tag:
        guest_name = guest_tag.get_text(strip=True).replace('Guest Skeptic:', '').strip()
        metadata['guest_skeptic'] = guest_name
    
    # Extract the direct link to the MP3 audio file
    audio_tag = soup.find("a", href=re.compile(r'\.mp3'))
    metadata['audio_url'] = audio_tag['href'] if audio_tag else ""
    
    metadata['download_date'] = datetime.now().strftime("%Y-%m-%d")
    return metadata


def clean_and_convert_html(soup: BeautifulSoup) -> Optional[str]:
    """

    Isolates the main content, removes unwanted elements, and converts it to Markdown.
    Args:
        soup: The parsed BeautifulSoup object of an SGEM episode page.

    Returns:
        The cleaned content as a Markdown string, or None if content is not found.
    """
    content_div = soup.find("div", class_="post-content")
    if not content_div:
        return None

    # Define CSS selectors for elements to be removed (e.g., audio players, nav links)
    junk_selectors = [
        '.powerpress_player', 'p.powerpress_links', 'div.et_extra_other_module',
        'nav.post-nav', 'div.post-footer', 'iframe'
    ]
    for selector in junk_selectors:
        for element in content_div.select(selector):
            element.decompose() # Remove the element from the parse tree
            
    # Convert the cleaned HTML to Markdown, preserving heading styles.
    return md(str(content_div), heading_style="ATX")


def process_url(url: str, output_dir: str) -> None:
    """
    Orchestrates the scraping and saving process for a single URL.

    Args:
        url: The SGEM episode URL to process.
        output_dir: The directory where the final .md file will be saved.
    """
    try:
        # --- Scrape and Parse ---
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # --- Extract and Process Data ---
        metadata = extract_metadata(soup, url)
        
        # Create a safe filename from the title
        base_filename = re.sub(r'[^\w\-]+', '_', metadata['title'])
        output_path = os.path.join(output_dir, f"{base_filename[:70]}.md") # Truncate to avoid long names
        
        if os.path.exists(output_path):
            print(f"Skipping '{metadata['title']}', file already exists.")
            return

        show_notes_md = clean_and_convert_html(soup)
        if not show_notes_md:
            print(f"Main content not found for {url}")
            return

        # --- Assemble and Save File ---
        # Build the YAML front matter block
        meta_lines = ["---"]
        for key, value in metadata.items():
            if value:
                # Quote values with special characters to ensure valid YAML
                if ':' in str(value) and key not in ['url', 'audio_url']:
                     meta_lines.append(f'{key}: "{value}"')
                else:
                     meta_lines.append(f'{key}: {value}')
        meta_lines.append("---\n")
        yaml_block = "\n".join(meta_lines)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(yaml_block)
            f.write(show_notes_md)
        print(f"Saved: {metadata['title']}")

    except Exception as e:
        print(f"Failed to process {url}: {e}")


def main():
    """
    Main function to read URLs and manage the scraping process.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        with open(URL_LIST_FILE, "r", encoding="utf-8") as f:
            all_episode_links = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The URL list file '{URL_LIST_FILE}' was not found. Exiting.")
        return
    
    print(f"Loaded {len(all_episode_links)} episode URLs to scrape.")

    for ep_url in all_episode_links:
        process_url(ep_url, OUTPUT_DIR)
        time.sleep(1) # Be respectful to the server by waiting between requests


if __name__ == "__main__":
    main()