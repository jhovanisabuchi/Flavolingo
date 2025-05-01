import streamlit as st
from streamlit_lottie import st_lottie
import requests
import json
from liked_manager import load_liked_recipes, save_liked_recipes
from cached import (
    cached_translate_to_english,
    cached_generate_multiple_recipes,
    cached_translate_back,
    cached_recommend)
from recipe_pipeline import (
    detect_language, optional_ingredients
)
st.set_page_config(
        page_title="FlavorLingo",
        layout="centered",
        initial_sidebar_state="expanded",
        page_icon=None,  
        menu_items={
            "Get help": None,
            "Report a Bug": None,
            "About": None
        })
def load_lottiefile(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

    
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load animations
welcome_anim = load_lottiefile("G:\My Drive\Malti-language-recipe-generator\Images\Animation - 1746042124836 (2).json")  
loading_anim = load_lottiefile(r"C:\Users\johnk\Flavolingo\Images\Animation - 1746117095425.json")
loading_anim2 = load_lottiefile(r"C:\Users\johnk\Flavolingo\Images\Animation - 1746117383611.json")
success_anim = load_lottiefile("G:\My Drive\Malti-language-recipe-generator\Images\Animation - 1746045412549.json")
bonjour_anim = load_lottiefile (r"C:\Users\johnk\Flavolingo\Images\Animation - 1746118436776.json")

end_anim1 = load_lottiefile(r"C:\Users\johnk\Flavolingo\Images\Animation - 1746118189609.json")
end_anim2 = load_lottiefile(r"C:\Users\johnk\Flavolingo\Images\Animation - 1746118797005.json")
end_anim3 = load_lottiefile(r"C:\Users\johnk\Flavolingo\Images\Animation - 1746117383611.json")
end_anim4 = load_lottiefile(r"C:\Users\johnk\Flavolingo\Images\Animation - 1746118189609.json")
# Custom CSS for background color and other styles 
st.markdown("""
    <style>
        body {
            background-color: #f7f1e1;  /* Light cooking-related color */
            font-family: 'Arial', sans-serif;
        }
        .css-18e3th9 {
            background-color: #f7f1e1 !important;
        }
    </style>
""", unsafe_allow_html=True)



# Main Streamlit UI
def main():
    if "liked_recipes" not in st.session_state:
        st.session_state.liked_recipes = load_liked_recipes()
    
    st.title("👨‍🍳 FlavorLingo")

    # Welcome Animation
    st_lottie(welcome_anim, height=300)
    st.markdown("Welcome! Enter ingredients and get recipes in your language ✨")

    # ========== Sidebar: User Preferences ==========    
    st.sidebar.header("👤 User Preferences")
    diet = st.sidebar.multiselect("Dietary Restrictions:", ["Vegetarian", "Vegan", "Gluten-Free", "Keto"])
    cuisines = st.sidebar.multiselect("Preferred Cuisin:", ["Italian", "Mexican", "Indian", "Mediterranean", "Asian", "French", "Chinese", "Greek"])
    dislikes = st.sidebar.text_input("Ingredients you dislike (comma-separated):")

    # Combine the selected cuisines into a string
    preferred_cuisin = ", ".join(cuisines)

    # === Sidebar: View Liked Recipes ===
    st.sidebar.markdown("***")
    st.sidebar.subheader("💖 Liked Recipes")
    if st.session_state.liked_recipes:
        for idx, liked in enumerate(st.session_state.liked_recipes, 1):
            st.sidebar.markdown(f"**{idx}.** {liked[:60]}...")  
        if st.sidebar.button("🗑️ Clear Liked Recipes"):
            st.session_state.liked_recipes = []
            save_liked_recipes([])  
            st.sidebar.success("Liked recipes cleared.")
    else:
        st.sidebar.info("You haven’t liked any recipes yet.")

    # ========== Main Input Section ==========    
    language_choice = st.selectbox("Select the language of the ingredients:", ["Auto-detect", "French", "Italian", "Greek", "German"])
    ingredients = st.text_input("📝 Enter the main ingredients (comma-separated):")

    selected_optional_ingredients = st.multiselect(
        "🧂 Add optional ingredients (if any):",
        sorted(optional_ingredients)  # Sorted for easier navigation
    )

    if ingredients:
        if language_choice == "Auto-detect":
            selected_language = detect_language(ingredients)
            st.info(f"🌍 Auto-detected Language: **{selected_language.upper()}**")
        else:
            language_map = {"French": "fr", "Italian": "it", "Greek": "el", "German": "de"}
            selected_language = language_map.get(language_choice)

        combined_ingredients = ingredients + ", " + ", ".join(selected_optional_ingredients)
    
        if selected_language != "en":
            translated_ingredients = cached_translate_to_english(combined_ingredients, selected_language)
        else:
            translated_ingredients = combined_ingredients

        # Loading animation
        with st.spinner("Generating your delicious recipes..."):
            # Display all three animations side by side using Streamlit columns
            col1, col2, col3 = st.columns(3)

            with col1:
                st_lottie(loading_anim2, height=200, width=200)

            with col2:
                st_lottie(loading_anim, height=200, width=200)

            with col3:
                st_lottie(success_anim, height=200, width=200)

            recipes = cached_generate_multiple_recipes(translated_ingredients, num_recipes=5)
            
        #st.success("✅ Recipes ready!")
        

        # Show the recipes
        st.markdown("## 🍽️ Your Recipes:")
        
        for i, recipe in enumerate(recipes, 1):
            if selected_language != "en":
                displayed_recipe = cached_translate_back(recipe, selected_language)
                st.markdown(f"### 🥘 Recipe {i}:\n\n{displayed_recipe}")
            else:
                st.markdown(f"### 🥘 Recipe {i}:\n\n{recipe}")
            liked_recipe = displayed_recipe if selected_language != "en" else recipe

            if st.button(f"💖 Like this recipe", key=f"like_{i}"):
                if displayed_recipe not in st.session_state.liked_recipes:
                    st.session_state.liked_recipes.append(liked_recipe)
                    save_liked_recipes(st.session_state.liked_recipes)
                    st.success("Added to liked recipes!")
        st.lottie(bonjour_anim , height=450)
        st.markdown("## 🔁 You may also like:")

        if st.session_state.liked_recipes or ingredients:
            recommendations = cached_recommend(
                liked_recipes=st.session_state.liked_recipes,
                preferred_cuisin=preferred_cuisin, 
                input_ingredients=combined_ingredients.split(", "),
                top_n=5,
                additional_n=5,
                selected_language=selected_language
            )

            if recommendations:
                for rec in recommendations:
                    with st.expander(f"🍽️ {rec['title']}"):
                        st.markdown("**Ingredients:**")
                        st.write(rec['ingredients']) 
                        
                        st.markdown("**Directions:**")
                        if isinstance(rec['directions'], list):
                            for step in rec['directions']:
                                st.write(f"- {step}")
                        else:
                            st.write(rec['directions'])
            else:
                st.info("No similar recipes found.")
        st.markdown("---")
        st.markdown("### 🎉 Thanks for using FlavorLingo!")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st_lottie(end_anim1, height=250)

        with col2:
            st_lottie(end_anim2, height=250)

        with col3:
            st_lottie(end_anim3, height=250)

        with col4:
            st_lottie(end_anim4, height=250)

if __name__ == "__main__":
    main()
