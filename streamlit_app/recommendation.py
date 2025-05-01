import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from recipe_pipeline import translate_back
from scipy.sparse import hstack
import streamlit as st 
import os 

@st.cache_resource
def load_resources():
    base_path = os.path.dirname(__file__)  # Get the folder of the current script

    df = pd.read_csv(os.path.join(base_path, "known_recipes.csv"))
    cuis_vec = joblib.load(os.path.join(base_path, "cuisin_vectorizer.pkl"))
    ing_vec = joblib.load(os.path.join(base_path, "ingredient_vectorizer.pkl"))
    model = joblib.load(os.path.join(base_path, "nearest_neighbors.pkl"))

    return df, cuis_vec, ing_vec, model

known_recipes_df, cuisin_vectorizer, ingredient_vectorizer, knn_model = load_resources()


def get_recipe_index_by_name(name):
    """Return index of recipe from the dataframe based on its name"""
    match = known_recipes_df[known_recipes_df['title'] == name]
    return match.index[0] if not match.empty else None

def recommend_based_on_cuisin_liked_recipes_or_ingredients(
        input_ingredients=None, 
        liked_recipes=None, 
        preferred_cuisin=None, 
        top_n=5, 
        additional_n=5, 
        selected_language="en"):
    """Recommend recipes based on cuisin and liked recipes first, and fall back to ingredients if not provided."""
    
    recommendations = []

    # Step 1: First, recommend based on cuisin and liked recipes (priority)
    if preferred_cuisin or liked_recipes:
        # Ensure 'clean_cuisin' has no NaNs
        known_recipes_df['clean_cuisin'] = known_recipes_df['clean_cuisin'].fillna('')

        # Filter based on cuisine(s)
        if preferred_cuisin:
            if isinstance(preferred_cuisin, list):
                preferred_cuisin = [c.lower() for c in preferred_cuisin]
                filtered_recipes = known_recipes_df[
                    known_recipes_df['clean_cuisin'].str.lower().isin(preferred_cuisin)
                ]
            else:
                filtered_recipes = known_recipes_df[
                    known_recipes_df['clean_cuisin'].str.lower() == preferred_cuisin.lower()
                ]
        else:
            filtered_recipes = known_recipes_df

        # Further filter based on liked recipes (if provided)
        if liked_recipes:
            liked_indices = []
            liked_ingredients = []
            for title in liked_recipes:
                if title in known_recipes_df['title'].values:
                    liked_indices.append(known_recipes_df[known_recipes_df['title'] == title].index[0])
            
            if liked_indices:  # Ensure liked_indices is not empty
                liked_ingredients = known_recipes_df.iloc[liked_indices]['ingredients'].tolist()
                liked_ingredients_vectorized = ingredient_vectorizer.transform(liked_ingredients)
                liked_cuisins = [preferred_cuisin] * len(liked_ingredients) if preferred_cuisin else ["" for _ in liked_ingredients]
                cuisin_vectors = cuisin_vectorizer.transform(liked_cuisins)
                ingredient_vectors = ingredient_vectorizer.transform(liked_ingredients)
                combined_vectors = hstack([ingredient_vectors, cuisin_vectors])

                distances, indices = knn_model.kneighbors(combined_vectors, n_neighbors=additional_n)

                # Collect the liked-recipes-based recommendations
                for idx in indices[0]:
                    if idx < len(known_recipes_df):  # Check index validity
                        recipe = known_recipes_df.iloc[idx]
                        if preferred_cuisin and recipe['cuisin'] != preferred_cuisin:
                            continue  # Skip if cuisin doesn't match
                        title = recipe["title"]
                        ingredients = recipe["ingredients"]
                        directions = recipe["directions"]

                        if selected_language != "en":
                            title = translate_back(title, selected_language) if title else title
                            ingredients = translate_back(ingredients, selected_language) if ingredients else ingredients 
                            directions = translate_back(directions, selected_language) if directions else directions

                        recommendations.append({
                            "title": title,
                            "ingredients": ingredients,
                            "directions": directions
                        })

        # If cuisin and liked recipes are provided, return early (recommended by both)
        if recommendations:
            return recommendations

    # Step 2: If no cuisin or liked recipes provided, recommend based on ingredients
    if input_ingredients:
        input_str = " ".join(input_ingredients)
        ingredient_vector = ingredient_vectorizer.transform([input_str])
    
        # Use provided preferred_cuisin or empty string
        cuisin_str = preferred_cuisin if preferred_cuisin else ""
        cuisin_str = " ".join(preferred_cuisin) if isinstance(preferred_cuisin, list) else preferred_cuisin
        cuisin_vector = cuisin_vectorizer.transform([cuisin_str])

        # Combine the vectors
        combined_vector = hstack([ingredient_vector, cuisin_vector])

        # Get the nearest neighbors
        distances, indices = knn_model.kneighbors(combined_vector, n_neighbors=top_n)

        # Collect the ingredient-based recommendations
        for idx in indices[0]:
            if idx < len(known_recipes_df):  # Check index validity
                recipe = known_recipes_df.iloc[idx]
                title = recipe["title"]
                ingredients = recipe["ingredients"]
                directions = recipe["directions"]
                cuisin = recipe["clean_cuisin"]

                if selected_language != "en":
                    title = translate_back(title, selected_language)
                    ingredients = translate_back(ingredients, selected_language)
                    directions = translate_back(directions, selected_language)

                recommendations.append({
                    "title": title,
                    "ingredients": ingredients,
                    "directions": directions,
                    "cuisin": cuisin
                })

    return recommendations
