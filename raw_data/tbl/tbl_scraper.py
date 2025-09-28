"""
This script scrapes medical trial summaries from 'The Bottom Line' website.

It performs the following steps:
1.  Navigates through all pages of the Emergency Medicine (EM) summaries category.
2.  Collects the title and URL of each article.
3.  Visits each article URL to extract the main content.
4.  Saves the content to a local text file with a metadata header.
5.  Handles filename collisions by appending a number to duplicate filenames.
6.  Reports a final summary of successful and failed scrapes.
"""

import asyncio
import os
import re
from datetime import datetime
from typing import List, Tuple, Optional

from playwright.async_api import async_playwright, Playwright
from bs4 import BeautifulSoup

# --- Configuration ---
BASE_URL = "https://www.thebottomline.org.uk"
START_PAGE = f"{BASE_URL}/category/summaries/em/"
OUTPUT_DIR = "retrieved_articles"

# --- Global State Tracking ---
# Used for the final summary report.
successful_saves: List[Tuple[str, str]] = []
failed_saves: List[Tuple[str, str]] = []
renamed_files: List[Tuple[str, str]] = []


async def get_all_article_links(playwright: Playwright) -> List[Tuple[str, str]]:
    """
    Crawls through the website's pagination to collect all article links.

    Args:
        playwright: The active Playwright instance.

    Returns:
        A list of tuples, where each tuple contains the article title and its URL.
    """
    print("Getting all article links...")
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(START_PAGE)

    links = []
    while True:
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        articles = soup.select("h2.entry-title a")

        for a in articles:
            links.append((a.get_text(strip=True), a['href']))

        next_button = soup.select_one("a.next")
        if next_button and next_button.get("href"):
            next_href = next_button["href"]
            print(f"Navigating to next page: {next_href}")
            await page.goto(next_href)
        else:
            print("Reached the last page.")
            break

    await browser.close()
    print(f"Found {len(links)} articles.")
    return links


async def get_article_content(playwright: Playwright, url: str) -> Optional[str]:
    """
    Navigates to a single article URL and extracts its main text content.

    Args:
        playwright: The active Playwright instance.
        url: The URL of the article to scrape.

    Returns:
        The article's text content as a string, or None if an error occurs.
    """
    print(f"Visiting: {url}")
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    try:
        await page.goto(url, timeout=15000)
        await page.wait_for_selector("div.entry.clearfix", timeout=10000)
        
        # Use BeautifulSoup to parse the content for better text extraction
        html_content = await page.content()
        soup = BeautifulSoup(html_content, "html.parser")
        entry = soup.select_one("div.entry.clearfix")
        
        if entry:
            return entry.get_text(separator="\n", strip=True)
        else:
            print(f"No content found in selector for URL: {url}")
            return None
            
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return None
    finally:
        await browser.close()


def save_article_to_file(title: str, content: str, url: str) -> bool:
    """
    Saves the article content to a text file with a metadata header.

    Handles filename sanitization and collisions.

    Args:
        title: The title of the article.
        content: The text content of the article.
        url: The original URL of the article.

    Returns:
        True if the file was saved successfully, False otherwise.
    """
    # Sanitize title to create a valid filename
    base_name = title.lower().replace(" ", "_")
    base_name = re.sub(r'[^\w-]', '', base_name)  # Keep only word chars, hyphens, underscores
    
    output_filename = f"{base_name}.txt"
    filepath = os.path.join(OUTPUT_DIR, output_filename)

    # Handle potential filename collisions by appending a number
    collision_count = 1
    is_renamed = False
    while os.path.exists(filepath):
        is_renamed = True
        output_filename = f"{base_name}_{collision_count}.txt"
        filepath = os.path.join(OUTPUT_DIR, output_filename)
        collision_count += 1

    # Prepare metadata
    scrape_date = datetime.today().strftime("%Y-%m-%d")
    metadata_block = (
        "# Metadata\n"
        f"- Source: The Bottom Line\n"
        f"- Title: {title}\n"
        f"- Original URL: {url}\n"
        f"- Scrape Date: {scrape_date}\n"
        f"- Summary Date: AUTO_FILL_IF_AVAILABLE\n\n"
    )

    full_content = metadata_block + content

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        print(f"Saved: {output_filename}")
        if is_renamed:
            renamed_files.append((title, output_filename))
        return True
    except IOError as e:
        print(f"Failed to save file {output_filename}: {e}")
        return False


async def main():
    """Main function to orchestrate the scraping and saving process."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        links = await get_all_article_links(p)

        for title, url in links:
            content = await get_article_content(p, url)
            if content:
                if save_article_to_file(title, content, url):
                    successful_saves.append((title, url))
                else:
                    failed_saves.append((title, url))
            else:
                # If content is None, it means scraping failed
                failed_saves.append((title, url))

    # --- Final Summary Report ---
    print("\n" + "="*30)
    print("SCRAPING SUMMARY")
    print("="*30)
    print(f"Successfully saved: {len(successful_saves)}")
    print(f"Failed to save or scrape: {len(failed_saves)}")
    print(f"Filename collisions handled: {len(renamed_files)}")

    if failed_saves:
        print("\nFailed Articles (check for errors):")
        for title, url in failed_saves:
            print(f"- {title} -> {url}")

    if renamed_files:
        print("\nRenamed Files (due to duplicate titles):")
        for original_title, new_filename in renamed_files:
            print(f"- '{original_title}' -> was saved as '{new_filename}'")


if __name__ == "__main__":
    asyncio.run(main())