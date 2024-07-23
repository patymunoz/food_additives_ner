from gliner_finetune.synthetic import process_example
import argparse
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import openai
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

#------------------ Environment key ------------------#
def load_env():
    """
    Loads environment variables from a .env file.

    If the .env file does not exist, it creates one with an empty OPENAI_API_KEY variable.
    If the OPENAI_API_KEY is not set in the .env file, a ValueError is raised.

    Returns:
        openai.OpenAIApi: An instance of the OpenAI client configured with the OPENAI_API_KEY.

    Raises:
        ValueError: If the OPENAI_API_KEY is empty in the .env file.
    """
    console = Console()

    load_dotenv(dotenv_path=os.path.join('config', '.env'))

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the .env file")
    
    client = openai.OpenAI(api_key=api_key)
    console.print('[bold purple]Successfully loaded the API_KEY.[/bold purple]')
    return client

#------------------ Configuration ------------------#

def load_config(config_path='config/config_structure.json'):
    """
    Loads the configuration from a JSON file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: The configuration settings.
    """
    with open(config_path, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    return config

#------------------ Data generation ------------------#

def load_base_prompt():
    """
    Loads the base prompt from a JSON file.

    Returns:
        dict: The base prompt settings.
    """
    base_prompt_path = os.path.join('config', 'base_prompt.json')
    if not os.path.exists(base_prompt_path):
        console = Console()
        console.print(f"[bold red]Error:[/bold red] {base_prompt_path} does not exist.")
        sys.exit(1)

    with open(base_prompt_path, 'r', encoding='utf-8') as file:
        base_prompt = json.load(file)
    return base_prompt

def load_data_structure():
    """
    Loads the data structure from a JSON file.

    Returns:
        dict: The data structure settings.
    """
    data_structure_path = os.path.join('config', 'config_structure.json')
    if not os.path.exists(data_structure_path):
        console = Console()
        console.print(f"[bold red]Error:[/bold red] {data_structure_path} does not exist.")
        sys.exit(1)

    with open(data_structure_path, 'r', encoding='utf-8') as file:
        data_structure = json.load(file)
    return data_structure

def load_data(data_file):
    """
    Loads the data from a JSON file.

    Args:
        data_file (str): The name of the data file to load.

    Returns:
        dict: The data settings.
    """
    if not os.path.exists(data_file):
        console = Console()
        console.print(f"[bold red]Error:[/bold red] {data_file} does not exist.")
        sys.exit(1)

    with open(data_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

#------------------ Extract Entities ------------------#

def extract_entities(text, base_prompt, config):
    """
    Extracts entities from a given text using the OpenAI API.

    Args:
        text (str): The text to extract entities from.
        base_prompt (dict): The base prompt settings.
        config (dict): The configuration settings.

    Returns:
        dict: The extracted entities.
    """
    base_prompt_text = base_prompt.get("base_prompt", "")
    prompt = base_prompt_text.replace("{i}", text)

    # # Debug
    # console = Console()
    # console.print(f"[bold green]Generated Prompt:[/bold green] {prompt}")

    messages = [
        {"role": "system", "content": "You are a helpful information extraction system."},
        {"role": "user", "content": prompt}
    ]
    
    # # Debug
    # console.print(f"[bold green]Messages sent to API:[/bold green] {messages}")

    response = client.chat.completions.create(
        model=config["openai_model"],
        messages=messages,
        temperature=config["temperature"],
        top_p=config["top_p"],
        frequency_penalty=config["frequency_penalty"],
        presence_penalty=config["presence_penalty"]
    )

    # # Debug
    # console.print(f"[bold green]API Response:[/bold green] {response}")

    content = response.choices[0].message.content
    content = content.strip().strip('```json').strip('```')
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("The API response is not a valid JSON object: " + content)

#------------------ final dataset ------------------#

def process_finetune(loaded_results, progress, task):
    processed_results = []
    total_items = len(loaded_results)
    progress.update(task, total=total_items)
    for i, result in enumerate(loaded_results, 1):
        for key, value in result.items():
            if 'text' in value:
                processed_example = process_example(value)
                processed_results.append({key: processed_example})
        progress.update(task, advance=1)
    return processed_results

#------------------ Main ------------------#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate data structure")
    parser.add_argument('data_file', type=str, help="The path of the data file to load")
    args = parser.parse_args()

    # Load environment variables
    client = load_env()

    console = Console()
    progress = Progress(SpinnerColumn(), BarColumn(), TextColumn("{task.description}"))
    progress_finetune = Progress(SpinnerColumn(), BarColumn(), TextColumn("{task.description}"))
    
    with progress:
        task = progress.add_task("[red]Processing...", total=100)

        # Load configuration
        config = load_config()

        # Load base prompt
        base_prompt = load_base_prompt()

        # Load data
        data = load_data(args.data_file)

        # Extract entities using the loaded base prompt and config
        results = []
        total_items = len(data)
        progress.update(task, total=total_items)

        for i, (key, summary_text) in enumerate(data.items(), 1):
            #console.print(f"[bold blue]Processing {key}...[/bold blue]")
            entities = extract_entities(summary_text, base_prompt, config)
            #console.print(f"[bold green]Entities for {key}:[/bold green] {entities}")
            results.append({key: entities})
            progress.update(task, advance=1)

        #save the results to a JSON file
        path_out = os.path.join('data', 'processed', 'structure_output.json')
        with open(path_out, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    console.print(f"[bold green]Results saved to {path_out}[/bold green]")

    with open(path_out, 'r', encoding='utf-8') as f:
        loaded_results = json.load(f)

    with progress_finetune:
        task_finetune = progress_finetune.add_task("[green]Processing finetune structure...", total=100)
        processed_results = process_finetune(loaded_results, progress_finetune, task_finetune)

    path_processed_out = os.path.join('data', 'processed', 'processed_structure_output.json')
    with open(path_processed_out, 'w', encoding='utf-8') as f:
        json.dump(processed_results, f, ensure_ascii=False, indent=2)

#------------------ End of script ------------------#