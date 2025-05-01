🍽️ FlavoLingo: Multilingual Recipe Generation & Recommendation System
Transform your ingredients into mouthwatering recipes — in your language, from millions of global inspirations.
Powered by intelligent translation, massive recipe data, and personalized cuisine recommendations.

📌 Overview
FlavoLingo is an AI-powered recipe generation and recommendation system that helps users around the world discover, create, and enjoy recipes in their preferred language — using just the ingredients they have in hand.

It is built on a massive dataset of over 2 million English-language recipes. For personalized suggestions, 65,000 curated recipes across 8 major cuisines were selected and used to train a recommendation system that adapts to your preferences.

FlavoLingo uses a translation pipeline to:

Accept user input in any of 200+ languages,

Generate a recipe in English using advanced NLP models,

Translate the result back into the user’s language.

It also features a smart recommendation engine that suggests recipes based on:

🧾 User’s preferred cuisine

❤️ Previously liked recipes

🥬 Input ingredients

🔁 Project Pipeline
mermaid
Copy
Edit
graph TD
    A[User enters ingredients<br>in any language] --> B[Translate to English<br>(MarianMT)]
    B --> C[Generate recipe<br>(T5 by FluxCommunity)]
    C --> D[Translate back to user’s language<br>(MarianMT)]
    D --> E[Display full recipe with instructions]
    A --> F[Trigger recommendation engine<br>(KNN + Cosine Similarity)]
    F --> G[Suggest related recipes]
🔧 Data Processing
To enable effective recipe generation and personalized recommendations, significant preprocessing was done on the raw dataset:

🧹 Column Cleaning & Standardization
Cleaned and standardized the title, ingredients, and instructions fields.

Removed duplicates, null entries, and malformed data rows.

🌎 Cuisine Extraction
The original dataset (2M+ recipes) did not include cuisine labels.

Extracted country of origin from the recipe title (e.g., "Authentic Mexican Tacos", "Italian Lasagna").

Mapped these to standard cuisine names:

"Mexican" → Mexican cuisine

"Italy" → Italian cuisine

etc.

✅ From this full dataset, 65,000 recipes across 8 key cuisines were selected and cleaned for use in the recommendation system.

🔢 Data Vectorization
Vectorized the ingredient and cuisine columns.

Used TF-IDF and CountVectorizer for feature extraction.

Encoded cuisines for clustering and KNN recommendations.

🌍 Key Features
🗣️ Multilingual Support
Uses MarianMT (HuggingFace) for bidirectional translation.

Supports 200+ languages for both input and output.

🧠 AI-Powered Recipe Generation
Fine-tuned FluxCommunity’s T5 model on HuggingFace.

Generates high-quality recipes using only ingredients.

🎯 Personalized Recommendation System
Implemented with K-Nearest Neighbors (KNN) and cosine similarity.

Learns from:

Cuisine preference

User's liked history

Ingredient similarity

Trained using 65,000 curated recipes across 8 cuisines from the main 2M+ recipe dataset.

🧪 Modules & Models Used

Component	Module / Library	Details
Translation	MarianMT (HuggingFace)	Translates between 200+ languages
Recipe Generation	FluxCommunity/t5-recipe-generation	T5 model trained for culinary tasks
Recommendation Engine	KNN + cosine similarity	Scikit-learn or custom implementation
NLP & Transformers	transformers, datasets	HuggingFace ecosystem
Core Language	Python 3.10+	With PyTorch backend
📁 Directory Structure
css
Copy
Edit
FlavoLingo/
├── data/
│   └── recipes_dataset.csv        
├── models/
│   ├── marian_mt/                 
│   ├── t5_recipe_generator/      
│   └── knn_recommender/          
├── notebooks/
│   └── analysis/                  
├── app/
│   ├── main.py                    
│   ├── recipe_gen.py              
│   ├── translator.py              
│   └── recommender.py            
├── images/
│   └── pipeline_diagram.png       
├── README.md
└── requirements.txt