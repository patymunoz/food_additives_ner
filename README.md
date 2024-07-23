
# Food Additives NER

This repository is designed for two main processes: extraction and transformation of text. The objective is to generate a dataset that can be used to fine-tune a Named Entity Recognition (NER) model specifically for food additives. The project structure is organized as follows:

## Directory Structure

```plaintext
FOOD_ADDITIVES_NER
├── config
│   ├── .env
│   ├── base_prompt.json
│   ├── config_structure.json
│   └── config_summ.json
├── data
│   ├── auxiliar
│   ├── interim
│   ├── processed
│   └── raw
├── notebooks
│   └── pruebas.ipynb
├── src
|   ├── __init__.py
│   ├── scrapping
│   │   └── scrapping_data.py
│   ├── structure
│   │   └── generate_data_structure.py
│   └── summarization
│       └── generate_data_summ.py
├── .gitignore
├── README.md
└── requirements.in
```

# File Descriptions

## config

* `.env`: Environment variables.
* `base_prompt.json`: Base prompt for the generation of the dataset.
* `config_structure.json`: Configuration file for the structure generation.
* `config_summ.json`: Configuration file for the summarization generation.

## data
* `auxiliar`: Auxiliar data.
* `interim`: Intermediate data.
* `processed`: Processed data.
* `raw`: Raw data.

## notebooks
* `pruebas.ipynb`: Jupyter notebook for testing purposes.

## src
* `scrapping`: Module for scrapping data.
* `structure`: Module for generating the structure of the dataset.
* `summarization`: Module for generating the summarization of the dataset.

## Root files

* `.gitignore`: Git ignore file.
* `README.md`: Readme file.
* `requirements.in`: Requirements file.

# Installation

1. In the folder where this repository is located, create a virtual environment with Python 3.10 and activate it as follows:

* With `pipenv`:

```bash
pipenv shell --python 3.10
```

* with `conda`:
```bash
conda create --name environment_name python==3.10
conda activate environment_name
```

2. After activating the virtual environment and before synchronizing the dependencies listed in the requirements file, make sure to install pip-tools within the virtual environment:

* with `pip`:    
```bash
pip install pip-tools
```

* with `conda`:
```bash
conda install -c conda-forge pip-tools
```

3. Use `pip-sync` to install the dependencies listed in the requirements.in file:
    
```bash
pip-sync requirements.in
```

4. You can ensure that the dependency installation was successful by running the following command: `pip list` or `conda list`.

# Usage

## OpenAI API

To use the OpenAI API, you need to set the environment variable. Please create a file `.env` in the `config` folder and add the following line:
    
```bash
OPENAI_API_KEY="your_api_key"
 ```

## Extracting and transforming data

There are three main steps to generate the dataset:

1. Run the data scrapping script:

```bash
python src/scrapping/scrapping_data.py
```

2. Generate the data summaries (give the address and name of the file that contains the raw data and then give the adress and name of the file of configuration for the summarization):
    
```bash
python src/summarization/generate_data_summ.py data/raw/additives_descriptions_pre.json config/config_structure.json
```


3. Generate the data structure (give the address and name of the file that contains data summaries):

```bash
python src/structure/generate_data_structure.py data/processed/summaries.json
```

