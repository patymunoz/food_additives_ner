import os
import json
import requests
from bs4 import BeautifulSoup
from rich.progress import Progress

#-----------------# Scrape wikipedia description #-----------------#
def scrape_description(url):
    """
    Scrapes the description from a Wikipedia page given its URL.

    Args:
        url (str): URL of the Wikipedia page.

    Returns:
        str: The scraped description text, or None if scraping fails.
    """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        content = soup.find("div", {"class": "mw-parser-output"})
        if content:
            paragraphs = content.find_all("p")
            description = ""
            for para in paragraphs:
                description += para.get_text()
            return description.strip()
    return None

#-----------------# Clean newlines #-----------------#
def clean_newlines(data):
    """
    Recursively removes newlines from strings in the provided data.

    Args:
        data (str, dict, list): The data to clean.

    Returns:
        The cleaned data.
    """
    if isinstance(data, str):
        return data.replace("\n", " ")
    elif isinstance(data, dict):
        return {key: clean_newlines(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_newlines(element) for element in data]
    else:
        return data

#-----------------# Processing #-----------------#
def process_additives():
    """
    Processes the list of Wikipedia URLs to scrape descriptions and save them to JSON files.
    """
    path = os.path.join('data', 'auxiliar')

    with open(os.path.join(path, "wiki_additives.json"), encoding='utf-8') as f:
        additives = json.load(f)

    urls = additives.get("urls", [])
    descriptions = {}
    failed_urls = []

    with Progress() as progress:
        task = progress.add_task("[green]Scraping descriptions...", total=len(urls))

        for url in urls:
            name = url.split("/")[-1]
            description = scrape_description(url)
            if description:
                descriptions[name] = {"description": description}
            else:
                failed_urls.append(url.split("/")[-1])
            progress.update(task, advance=1)

    path_raw = os.path.join('data', 'raw')
    
    # Clean newlines from descriptions
    descriptions_cleaned = clean_newlines(descriptions)

    # Save successful descriptions :)
    try:
        with open(os.path.join(path_raw, "additives_descriptions.json"), "w", encoding='utf-8') as f:
            json.dump(descriptions, f, ensure_ascii=False, indent=4)

        with open(os.path.join(path_raw, "additives_descriptions_pre.json"), "w", encoding='utf-8') as f:
            json.dump(descriptions_cleaned, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving descriptions: {e}")

    # Save failed URLs :(
    try:
        with open(os.path.join(path_raw, "failed_urls.json"), "w", encoding='utf-8') as f:
            json.dump(failed_urls, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving failed URLs: {e}")

if __name__ == "__main__":
    process_additives()