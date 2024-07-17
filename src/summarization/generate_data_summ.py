from datetime import date
from datetime import datetime
from dotenv import load_dotenv
from rich import print
from rich.console import Console
from rich.prompt import Prompt
import openai
import json
import os

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

    load_dotenv()

    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    console.print('[bold purple]Successfully loaded the API_KEY.[/bold purple]')
    return client

def summarization_prompt(json_X, model, batch_size=10, temperature=0.2, top_p=0.9, frequency_penalty=0.8, presence_penalty=0.8):
    """
    Prompts the user for a text to summarize and returns the response from the model in batches.

    Args:
        json_X (dict): The JSON data with descriptions.
        model: The OpenAI model you want to use (e.g., gpt-3.5-turbo, gpt-4, etc.).
        batch_size (int): Number of descriptions to process in each batch.
        temperature (float): Sets the sampling temperature between 0 and 2.
        top_p (float): Uses nucleus sampling; considers tokens with top_p probability mass.
        frequency_penalty (float): Penalizes tokens based on their frequency, reducing repetition.
        presence_penalty (float): Penalizes new tokens based on their presence in the text.

    Returns:
        dict: The summaries of the texts.
    """
    
    client = load_env()
    
    today = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path_json = os.path.join('.', 'data', 'processed', f"additives_descr_summ_{today}.json")

    summaries = {}

    if not os.path.exists(path_json):
        with open(path_json, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
    else:
        with open(path_json, 'r', encoding='utf-8') as file:
            summaries = json.load(file)
    
    listDescriptions = [d for description in json_X.values() for d in description.values()]

    # Processing descriptions in batches and keep answers in json file
    for start_idx in range(0, len(listDescriptions), batch_size):
        batch = listDescriptions[start_idx:start_idx + batch_size]
        for i in batch:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an assistant that summarizes texts."},
                        {"role": "user", "content": f"Please, summarize the following text. Focus on synonyms, E number (European Union identifiers), food additive functional classes, and food industry applications: {i}"},
                        {"role": "user", "content": "Make sure to highlight food industry applications and do not add any other applications."},
                        {"role": "user", "content": "Build a paragraph no longer than 250 words."},
                        {"role": "user", "content": "Do not include any historical data or chemical compounds and pharmaceutical applications in the paragraph."}
                    ],
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

        # Save intermediate results to avoid data loss
        with open(path_json, 'w', encoding='utf-8') as file:
            json.dump(summaries, file, ensure_ascii=False, indent=4)

    return summaries