import pandas as pd
import os
import re
import spacy
import sys

# Load the small English model for finding Organization names
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Error: The spaCy model 'en_core_web_sm' is not installed.")
    print("Please run: python -m spacy download en_core_web_sm")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "..", "data", "epstein_full_text.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "data", "clean_transactions.csv")

def extract_financials():
    print("--- Loading Dataset (This may take a moment) ---")
    try:
        # The dataset is often large, so we read it in chunks or fully if memory allows
        # Assuming a CSV with columns like 'text' or 'content'
        df = pd.read_csv(INPUT_FILE, on_bad_lines='skip')
        print(f"Loaded {len(df)} documents.")
    except FileNotFoundError:
        print("Error: Run 1_download.py first!")
        return

    transactions = []
    
    # REGEX: Finds $50,000, $1M, 50k, etc.
    money_pattern = r'\$\s?([0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?)\s?(k|m|million|billion)?'
    
    # KEYWORDS: Context filters to reduce noise
    financial_verbs = ['wire', 'transfer', 'grant', 'donation', 'payment', 'fee', 'retainer']
    
    print("--- Scanning for Dark Money ---")
    
    # Iterate through documents (using a sample of 5000 for speed in this demo)
    # Remove [:5000] to run on the full set
    for index, row in df.iloc[:5000].iterrows(): 
        text = str(row.get('text', '')) # Adjust 'text' if column name differs
        
        # Split into sentences to keep context tight
        for line in text.split('\n'):
            money_match = re.search(money_pattern, line, re.IGNORECASE)
            
            if money_match:
                # Check for financial intent verbs
                if any(verb in line.lower() for verb in financial_verbs):
                    
                    # Extract Entities (Who paid/received?)
                    doc = nlp(line)
                    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
                    persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
                    
                    # Clean up the amount
                    amount_raw = money_match.group(0)
                    
                    transactions.append({
                        "doc_id": index,
                        "amount": amount_raw,
                        "entities": ", ".join(orgs + persons),
                        "context": line.strip()[:200] # Save snippet for proof
                    })
    
    # Save Results
    results_df = pd.DataFrame(transactions)
    results_df.to_csv(OUTPUT_FILE, index=False)
    print(f"--- Analysis Complete ---")
    print(f"Found {len(results_df)} suspicious transactions.")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_financials()