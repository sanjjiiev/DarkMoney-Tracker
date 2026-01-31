import os
from huggingface_hub import hf_hub_download
import shutil

# CONFIGURATION
# Note: If this specific repo is ever taken down, search "Epstein" on HuggingFace 
# and replace this ID with the newest mirror.
REPO_ID = "samvish/epstein-files"
FILENAME = "EPS_FILES_20K_NOV2025.csv" # The file name often updates, check the repo if this fails

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

def download_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    print(f"--- Connecting to Hugging Face: {REPO_ID} ---")
    try:
        # Download the file to the local cache
        cached_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME, repo_type="dataset")
        
        # Move it to our data folder for easy access
        final_path = os.path.join(DATA_DIR, "epstein_full_text.csv")
        shutil.copy(cached_path, final_path)
        
        print(f"Success! Data saved to: {final_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        

if __name__ == "__main__":
    download_data()