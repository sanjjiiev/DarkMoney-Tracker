---
title: Darkmoney Tracker
emoji: 💸
colorFrom: green
colorTo: gray
sdk: streamlit
sdk_version: "1.41.1"
app_file: src/3_dashboard.py
pinned: false
license: mit
python_version: "3.10"
---

# DarkMoney-Tracker

A financial intelligence tool designed to analyze and visualize transaction flows from the Epstein documents (DOJ Archives). This project uses Natural Language Processing (NLP) to extract financial entities and amounts from unstructured text and presents them in an interactive dashboard.

## Features

- **Automated Data Retrieval**: Downloads the latest dataset directly from Hugging Face.
- **NLP Analysis**: Uses `spaCy` and Regex to extract financial transactions, amounts, and involved entities (Organizations/Persons) from raw text.
- **Interactive Dashboard**: A Streamlit-based UI to explore the data.
- **Visualizations**:
  - **Sankey Diagram**: Visualizes the flow of funds.
  - **Treemap & Bar Charts**: Shows the distribution and frequency of entities involved.
- **Searchable Ledger**: Real-time filtering of the transaction database using a multi-select dropdown.

## Installation

1. **Clone the repository** (if applicable) or navigate to the project folder.

2. **Install dependencies**:
   ```bash
   pip install pandas huggingface_hub spacy streamlit plotly
   ```

3. **Download the spaCy model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Usage

The project is designed to be run in three sequential steps:

### 1. Download Data
Fetch the raw dataset from the Hugging Face repository.
```bash
python src/1_download.py
```

### 2. Analyze Text
Process the raw text to extract financial transactions. This script scans for currency patterns and financial verbs, then uses NER to identify entities.
```bash
python src/2_analyze.py
```

### 3. Launch Dashboard
Start the web interface to explore the results.
```bash
streamlit run src/3_dashboard.py
```

## Project Structure

```
DarkMoney-Tracker/
├── data/                   # Stores raw and processed CSV files (created automatically)
├── src/
│   ├── 1_download.py       # Downloads dataset from Hugging Face
│   ├── 2_analyze.py        # NLP extraction logic
│   └── 3_dashboard.py      # Streamlit visualization app
└── README.md
```
