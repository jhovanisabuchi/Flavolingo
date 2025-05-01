import json
import os

LIKED_FILE = "G:\My Drive\Malti-language-recipe-generator\Dataset\liked_recipes.json"  # Ensures it's saved inside the "data" folder

def load_liked_recipes():
    if os.path.exists(LIKED_FILE):
        with open(LIKED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_liked_recipes(recipes):
    directory = os.path.dirname(LIKED_FILE)
    if directory:  # Only try to create directory if it's not empty
        os.makedirs(os.path.dirname(LIKED_FILE), exist_ok=True)
    with open(LIKED_FILE, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
