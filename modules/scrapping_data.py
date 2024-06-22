import os
import json
import requests
from bs4 import BeautifulSoup
from rich.progress import Progress

#-----------------# Scrape wikipedia description #-----------------#
def scrape_description(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        content = soup.find("div", {"class": "mw-parser-output"})
        if content:
            paragraphs = content.find_all("p", recursive=False)
            description = ""
            for para in paragraphs:
                text = para.get_text().strip()
                if text:
                    description += text + "\n\n"
            return description.strip()
        else:
            return "Can't find content of webpage."
    else:
        return f"Error accessing the page: {response.status_code}"

#-----------------# Processing #-----------------#
def process_additives():
    path = os.path.join('.', 'data', 'auxiliar')

    with open(os.path.join(path, "wiki_additives.json"), encoding='utf-8') as f:
        additives = json.load(f)

    urls = additives.get("urls", [])
    descriptions = {}

    with Progress() as progress:
        task = progress.add_task("[green]Scraping descriptions...", total=len(urls))

        for url in urls:
            name = url.split("/")[-1]
            description = scrape_description(url)
            descriptions[name] = {"description": description}
            progress.update(task, advance=1)

    path_raw = os.path.join('.', 'data', 'raw')

    if not os.path.exists(path_raw):
        os.makedirs(path_raw)

    with open(os.path.join(path_raw, "additives_descriptions.json"), "w", encoding='utf-8') as f:
        json.dump(descriptions, f, ensure_ascii=False, indent=4)