import torch
from langdetect import detect
from transformers import MarianMTModel, MarianTokenizer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

device = torch.device("cpu")

# Cache models and tokenizers
language_model_cache = {}  # Cache for translation models
recipe_model_cache = None  # Cache for recipe generation model
recipe_tokenizer_cache = None  # Cache for recipe tokenizer

# Predefined list of optional ingredients
optional_ingredients = [
    "salt", "pepper", "oil", "garlic", "water", "butter", "lemon", "herbs", "cheese", "soy sauce", "vinegar"
]

# Load the recipe generation model once (this will be used across functions)
def load_recipe_model():
    global recipe_model_cache, recipe_tokenizer_cache
    if recipe_model_cache is None:
        recipe_model_cache = AutoModelForSeq2SeqLM.from_pretrained("flax-community/t5-recipe-generation").to(device)
        recipe_tokenizer_cache = AutoTokenizer.from_pretrained("flax-community/t5-recipe-generation")
    return recipe_model_cache, recipe_tokenizer_cache

# Load translation models once and cache them
def load_translation_model(source_lang, target_lang):
    global language_model_cache
    model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}'
    
    # If model is not already in cache, load it
    if model_name not in language_model_cache:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name).to(device)
        language_model_cache[model_name] = (model, tokenizer)
    
    return language_model_cache[model_name]

# Function to get user input for language selection (optional)
def get_user_language():
    print("Please select the language of the ingredients (Optional):")
    print("1. French")
    print("2. Italian")
    print("3. Greek")
    print("4. German")
    print("Press Enter to auto-detect the language.")
    user_input = input("Enter the number corresponding to your language choice (or press Enter to auto-detect): ")

    language_map = {
        "1": "fr",  # French
        "2": "it",  # Italian
        "3": "el",  # Greek
        "4": "de",  # German
    }
    # Return the language if selected, else auto-detect language
    return language_map.get(user_input, None)  # None means auto-detect

# Function to detect language (auto-detect)
def detect_language(text):
    return detect(text)

# Function to translate to English
def translate_to_english(text, source_lang):
    # Load the translation model
    model, tokenizer = load_translation_model(source_lang, "en")
    
    inputs = tokenizer(text, return_tensors="pt", padding=True).to(device)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

# Function to generate recipe
def generate_multiple_recipes(ingredients, num_recipes=5):
    # Load the pre-trained recipe generation model
    model, tokenizer = load_recipe_model()

    # Prepend "ingredients:" to the input for the model
    input_text = "ingredients: " + ingredients
    inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)

    # Generate recipe (output)
    outputs = model.generate(
        **inputs,
        max_length=350,
        do_sample=True,          # Enable sampling
        top_k=40,                # Limit token selection to top_k choices
        top_p=0.9,              # Nucleus sampling
        temperature=0.8,         # Randomness control (higher = more random)
        num_return_sequences=num_recipes  # Generate multiple recipes
    )

    recipes = [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
    return recipes

# Function to translate back
def translate_back(text, target_lang):
    # Load the translation model
    model, tokenizer = load_translation_model("en", target_lang)
    
    inputs = tokenizer(text, return_tensors="pt", padding=True).to(device)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

# Function to get optional ingredients from the user
def get_optional_ingredients():
    print("\nOptional ingredients to include (select any or press Enter to skip):")
    print("Available options:")
    for i, ingredient in enumerate(optional_ingredients, 1):
        print(f"{i}. {ingredient}")
    print(f"{len(optional_ingredients)+1}. None (skip optional ingredients)")

    # Let the user select multiple optional ingredients by number
    selected_numbers = input("Enter the numbers of the ingredients you want to add (comma separated): ")
    
    # Convert the input into a list of selected optional ingredients
    selected_indices = selected_numbers.split(",") if selected_numbers else []
    selected_ingredients = []
    
    # Add selected ingredients based on user input
    for index in selected_indices:
        try:
            # Convert index to integer and check if it is valid
            index = int(index.strip())
            if 1 <= index <= len(optional_ingredients):
                selected_ingredients.append(optional_ingredients[index - 1])
        except ValueError:
            pass
    
    return selected_ingredients

# Function to combine user ingredients with optional ingredients
def get_combined_ingredients(base_ingredients):
    selected_optional_ingredients = get_optional_ingredients()
    
    # Combine base ingredients with selected optional ones
    combined_ingredients = base_ingredients + ", "+",".join(selected_optional_ingredients)
    
    return combined_ingredients

def main():
    # Step 1: User selects language (optional)
    selected_language = get_user_language()

    # Step 2: If no language is selected, wait for user to input ingredients and auto-detect language
    if selected_language is None:
        # Ask for ingredients before detection
        ingredients = input("Please enter the ingredients (separate by commas): ")
        
        # Now auto-detect language
        detected_language = detect_language(ingredients)
        print(f"Auto-detected Language: {detected_language}")
        selected_language = detected_language
    else:
        # If the language is selected, ask for ingredients
        ingredients = input("Please enter the ingredients (separate by commas): ")

    # Step 3: Combine user input and optional ingredients, then generate recipe
    combined_ingredients = get_combined_ingredients(ingredients)
    print(f"Ingredients for recipe generation: {combined_ingredients}")

    # Step 4: Translate ingredients to English if not already in English
    if selected_language != "en":
        translated_ingredients = translate_to_english(combined_ingredients, selected_language)
        print(f"Translated Ingredients: {translated_ingredients}")
    else:
        translated_ingredients = combined_ingredients

    # Step 5: Generate recipe from translated ingredients
    recipes = generate_multiple_recipes(translated_ingredients, num_recipes=5)
   

    # Step 6: Translate the generated recipe back to the selected language
    if selected_language != "en":
        reversed_recipes = []
        print("\nTranslated Recipes:")
        for i, r in enumerate(recipes, 1):
            translated_back = translate_back(r, selected_language)
            reversed_recipes.append(translated_back)
            print(f"\nRecipe {i}:\n{translated_back}")
    else:
        print("\nRecipes:")
        for i, r in enumerate(recipes, 1):
          print(f"\nRecipe {i}:\n{r}") 


if __name__ == "__main__":
    main()
