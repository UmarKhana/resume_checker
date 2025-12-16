import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import sys
# Add project root to path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.scorer import WebDevScorer

MODEL_PATH = os.path.join(os.path.dirname(__file__), "trained_model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")

# Define ideal Web Developer profile
ideal_web_dev_profile = """
HTML CSS JavaScript TypeScript React Angular Vue.js Node.js Express
MongoDB PostgreSQL MySQL REST API GraphQL
Git GitHub responsive design frontend backend full-stack
Bootstrap Tailwind Sass SCSS webpack Vite
Next.js Nuxt Django Flask Laravel PHP
web development web application website e-commerce
deployment hosting AWS Azure Heroku Netlify Vercel
"""

print("Creating Web Development scoring model...")

# Create vectorizer
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))

# Fit on ideal profile
vectorizer.fit([ideal_web_dev_profile])

# Create model instance
model = WebDevScorer(vectorizer, ideal_web_dev_profile)

# Save
joblib.dump(model, MODEL_PATH)
joblib.dump(vectorizer, VECTORIZER_PATH)

print("✓ Web Development scoring model created!")
print(f"Model saved to: {MODEL_PATH}")
print(f"Vectorizer saved to: {VECTORIZER_PATH}")
