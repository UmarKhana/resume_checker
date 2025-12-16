from .model import ResumeModel
import os
import pdfplumber
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

ml_model = ResumeModel()

# Path to training CVs
TRAINING_CV_FOLDER = '/Users/omarahmed/Desktop/web deloper cv code/Professional_Detailed_CVs'

# Cache for training CV texts (load once)
_training_texts_cache = None

def load_training_cvs():
    """Load all training CV texts once and cache them"""
    global _training_texts_cache
    
    if _training_texts_cache is not None:
        print(f"Using cached training CVs: {len(_training_texts_cache)} CVs")
        return _training_texts_cache
    
    print(f"Loading training CVs from: {TRAINING_CV_FOLDER}")
    
    if not os.path.exists(TRAINING_CV_FOLDER):
        print(f"ERROR: Training folder does not exist: {TRAINING_CV_FOLDER}")
        return []
    
    training_texts = []
    pdf_files = sorted([f for f in os.listdir(TRAINING_CV_FOLDER) if f.endswith('.pdf')])
    print(f"Found {len(pdf_files)} PDF files in training folder")
    
    # Load ALL 1000 training CVs for comparison
    total_to_load = len(pdf_files)  # Load all CVs
    print(f"Loading all {total_to_load} training CVs...")
    
    for i, filename in enumerate(pdf_files):
        if i % 100 == 0:
            print(f"  Loading training CV {i+1}/{total_to_load}...")
        
        filepath = os.path.join(TRAINING_CV_FOLDER, filename)
        try:
            with pdfplumber.open(filepath) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + " "
                
                if text.strip():
                    training_texts.append(text.strip())
        except Exception as e:
            if i < 10:  # Only show first 10 errors
                print(f"  Error reading {filename}: {e}")
            continue
    
    _training_texts_cache = training_texts
    print(f"✓ Successfully loaded {len(training_texts)} training CVs for comparison")
    return training_texts


def score_resume(resume_text, target_category):
    predicted_category, confidence = ml_model.predict(resume_text)
    
    # Load training CVs
    training_texts = load_training_cvs()
    
    if len(training_texts) == 0:
        print("ERROR: No training CVs loaded! Cannot compare.")
        return {
            "predicted": predicted_category,
            "confidence": confidence,
            "score": 0.0,
            "raw_score": 0.0,
            "avg_similarity_to_training": 0.0,
            "max_similarity_to_training": 0.0
        }
    
    # Show first training CV sample (first 200 chars) for debugging
    if len(training_texts) > 0:
        print(f"Sample from first training CV: {training_texts[0][:200]}...")
    
    # Vectorize the uploaded CV and all training CVs
    all_texts = [resume_text] + training_texts
    vectors = ml_model.vectorizer.transform(all_texts)
    
    # Calculate similarity between uploaded CV and each training CV
    uploaded_vector = vectors[0:1]
    training_vectors = vectors[1:]
    similarities = cosine_similarity(uploaded_vector, training_vectors)[0]
    
    # Use average similarity to training set as the score
    avg_similarity = np.mean(similarities)
    max_similarity = np.max(similarities)
    
    # Use average of mean and max for final score
    base_score = (avg_similarity * 0.7 + max_similarity * 0.3)
    
    # Apply keyword-based adjustments
    resume_lower = resume_text.lower()
    
    # Pure web development keywords (must have these)
    web_keywords = [
        'react', 'angular', 'vue', 'svelte',
        'javascript', 'typescript', 
        'html', 'css', 'sass', 'scss',
        'node.js', 'express', 'fastapi', 'django', 'flask', 'laravel',
        'mongodb', 'postgresql', 'mysql',
        'frontend', 'backend', 'full stack', 'full-stack',
        'web development', 'web developer', 'web application',
        'redux', 'mobx', 'vuex',
        'webpack', 'vite', 'rollup',
        'npm', 'yarn', 'pnpm',
        'bootstrap', 'tailwind', 'material-ui',
        'rest api', 'graphql',
        'responsive design', 'spa', 'single page application'
    ]
    
    # Cloud/DevOps/Infrastructure keywords (heavy penalty)
    infrastructure_keywords = [
        'aws architecture', 'cloud architecture', 'azure architecture',
        'microservices architecture', 'distributed systems',
        'kubernetes', 'k8s', 'docker orchestration',
        'terraform', 'ansible', 'chef', 'puppet',
        'devops engineer', 'site reliability', 'sre',
        'infrastructure as code', 'iac',
        'cloud native', 'cloud engineer',
        'system design', 'scalability', 'high-scale systems'
    ]
    
    # Other non-web keywords (medium penalty)
    other_non_web_keywords = [
        'data science', 'machine learning', 'deep learning', 'ai engineer',
        'data engineer', 'data analyst', 'big data', 'spark', 'hadoop',
        'mobile development', 'ios developer', 'android developer',
        'swift', 'kotlin', 'react native',
        'embedded systems', 'firmware', 'hardware engineer',
        'network engineer', 'system administrator', 'cybersecurity',
        'blockchain', 'smart contracts', 'solidity'
    ]
    
    # Count matches
    web_count = sum(1 for kw in web_keywords if kw in resume_lower)
    infra_count = sum(1 for kw in infrastructure_keywords if kw in resume_lower)
    other_non_web_count = sum(1 for kw in other_non_web_keywords if kw in resume_lower)
    
    total_non_web = infra_count + other_non_web_count
    
    # Calculate penalty
    if infra_count >= 3:
        # Heavy infrastructure/DevOps focus - 70% penalty
        penalty = 0.3
        final_score = base_score * penalty
    elif total_non_web > web_count:
        # More non-web than web - 60% penalty
        penalty = 0.4
        final_score = base_score * penalty
    elif total_non_web >= 3:
        # Some non-web keywords - 40% penalty
        penalty = 0.6
        final_score = base_score * penalty
    elif web_count < 3:
        # Very few web keywords - 50% penalty
        penalty = 0.5
        final_score = base_score * penalty
    else:
        # Mostly web development - no penalty
        final_score = base_score

    # Return raw confidence from the model (no boosting)
    # This shows the true model confidence
    
    return {
        "predicted": predicted_category,
        "confidence": confidence,
        "score": final_score,
        "raw_score": base_score,
        "avg_similarity_to_training": avg_similarity,
        "max_similarity_to_training": max_similarity,
        "web_keywords_count": web_count,
        "non_web_keywords_count": total_non_web,
        "infrastructure_keywords_count": infra_count
    }


def shortlist(resume_list, target_category, top_k=10, min_score=0.03):
    scored = []

    for person_name, resume_text in resume_list:
        result = score_resume(resume_text, target_category)
        result["name"] = person_name
        
        print(f"CV: {person_name}, Score: {result['score']:.3f}, Avg: {result['avg_similarity_to_training']:.3f}, Max: {result['max_similarity_to_training']:.3f}")
        
        # Include CVs with at least 3% similarity
        if result["score"] >= min_score:
            scored.append(result)

    print(f"\nTotal candidates: {len(scored)} out of {len(resume_list)}")
    
    # Sort by score (highest first)
    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
    
    # Take top K candidates
    top_candidates = ranked[:top_k]
    
    # Check if the best candidate has at least 40% raw score
    # If not, return empty list (show 0 results)
    if len(top_candidates) > 0:
        best_raw_score = top_candidates[0]["score"]
        
        # 40% threshold check (lowered to match Antigravity behavior)
        # Scores are in 0-1 range, so 0.40 = 40%
        if best_raw_score < 0.40:
            print(f"\n⚠️  Best candidate score ({best_raw_score:.1%}) is below 40% threshold.")
            print("   No qualified candidates found. Returning 0 results.")
            return []
    
    # Multiply scores by 2 for better display (49% → 98%)
    # Cap at 100% (1.0)
    for candidate in top_candidates:
        candidate["score"] = min(candidate["score"] * 2, 1.0)
    
    # Filter: Only include candidates with score >= 85% (after multiplication)
    filtered_candidates = [c for c in top_candidates if c["score"] >= 0.85]
    
    print(f"After 85% filter: {len(filtered_candidates)} candidates qualify out of {len(top_candidates)}")
    
    return filtered_candidates

