from datetime import date
from datetime import datetime
from dotenv import load_dotenv
from rich import print
from rich.console import Console
from rich.progress import Progress
import openai
import json
import os
import argparse

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

    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    console.print('[bold purple]Successfully loaded the API_KEY.[/bold purple]')
    return client

#------------------ Configuration ------------------#

def load_config(config_path='config/config_summ.json'):
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
def summarization_prompt(json_X, model, messages, batch_size=10, temperature=0.2, top_p=0.9, frequency_penalty=0.8, presence_penalty=0.8):
    """
    Prompts the user for a text to summarize and returns the response from the model in batches.

    Args:
        json_X (dict): The JSON data with descriptions.
        model: The OpenAI model you want to use (e.g., gpt-3.5-turbo, gpt-4, etc.).
        messages (list): Custom instructions for the summarization prompt.
        batch_size (int): Number of descriptions to process in each batch.
        temperature (float): Sets the sampling temperature between 0 and 2. Default is 0.2.
        top_p (float): Uses nucleus sampling; considers tokens with top_p probability mass. Default is 0.9.
        frequency_penalty (float): Penalizes tokens based on their frequency, reducing repetition. Default is 0.8.
        presence_penalty (float): Penalizes new tokens based on their presence in the text. Default is 0.8.

    Returns:
        dict: The summaries of the texts.
    """
    
    client = load_env()
    
    today = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path_json = os.path.join('data', 'interim', f"descr_summ_{today}.json")

    summaries = {}

    if not os.path.exists(path_json):
        with open(path_json, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
    else:
        with open(path_json, 'r', encoding='utf-8') as file:
            summaries = json.load(file)
    
    listDescriptions = [d for description in json_X.values() for d in description.values()]

    with Progress() as progress:
        task = progress.add_task("[green]Generating data summaries...", total=len(listDescriptions))

    # Processing descriptions in batches and keep answers in json file
    for start_idx in range(0, len(listDescriptions), batch_size):
        batch = listDescriptions[start_idx:start_idx + batch_size]
        for i in batch:
            try:
                formatted_messages = [
                    {**message, "content": message["content"].format(text=i) if "{text}" in message["content"] else message["content"]}
                    for message in messages
                ]
                response = client.chat.completions.create(
                    model=model,
                    messages=formatted_messages,
                    temperature=temperature,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty
                )

                content = response.choices[0].message.content
                summary_key = f"summary_{len(summaries) + 1}"
                summaries[summary_key] = content
            except Exception as e:
                summaries[f"error_{len(summaries) + 1}"] = f"Error summarizing description: {str(e)}"
            progress.update(task, advance=1)

        # Save intermediate results to avoid data loss
        with open(path_json, 'w', encoding='utf-8') as file:
            json.dump(summaries, file, ensure_ascii=False, indent=4)

    return summaries

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize JSON data using OpenAI model.")
    parser.add_argument('json_file', type=str, help='The path to the JSON file containing descriptions.')
    args = parser.parse_args()

    json_file_path = args.json_file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    config = load_config()
    messages = config.get("messages")
    model = config.get("openai_model", "gpt-3.5-turbo")
    batch_size = config.get("batch_size", 10)
    temperature = config.get("temperature", 0.2)
    top_p = config.get("top_p", 0.9)
    frequency_penalty = config.get("frequency_penalty", 0.8)
    presence_penalty = config.get("presence_penalty", 0.8)

    summaries = summarization_prompt(json_data, model, messages, batch_size, temperature, top_p, frequency_penalty, presence_penalty)

    console = Console()
    console.print(f"[bold green]Summarization completed successfully. Summaries saved to {os.path.join('data', 'interim')}[/bold green]")