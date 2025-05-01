

import streamlit as st
from recipe_pipeline import (
    translate_to_english,
    generate_multiple_recipes,
    translate_back,
)
from recommendation import recommend_based_on_cuisin_liked_recipes_or_ingredients

@st.cache_data(show_spinner=False)
def cached_translate_to_english(ingredients, language):
    return translate_to_english(ingredients, language)

@st.cache_data(show_spinner=False)
def cached_generate_multiple_recipes(translated_ingredients, num_recipes=5):
    return generate_multiple_recipes(translated_ingredients, num_recipes)

@st.cache_data(show_spinner=False)
def cached_translate_back(recipe, language):
    return translate_back(recipe, language)

@st.cache_data(show_spinner=False)
def cached_recommend(liked_recipes, input_ingredients, preferred_cuisin, top_n, additional_n, selected_language):
    return recommend_based_on_cuisin_liked_recipes_or_ingredients(
        str(liked_recipes), str(input_ingredients), str(preferred_cuisin), 
        top_n, additional_n, selected_language
    )

