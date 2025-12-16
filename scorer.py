import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class WebDevScorer:
    def __init__(self, vectorizer, ideal_profile):
        self.vectorizer = vectorizer
        self.ideal_vector = vectorizer.transform([ideal_profile])
    
    def predict(self, texts):
        # Always return 'Web Development' for compatibility
        # Handle both sparse matrices and regular arrays
        if hasattr(texts, 'shape'):
            n_samples = texts.shape[0]
        else:
            n_samples = len(texts)
        return np.array(['Web Development'] * n_samples)
    
    def predict_proba(self, texts):
        # Calculate similarity scores
        # texts is already a sparse matrix from vectorizer.transform()
        similarities = cosine_similarity(texts, self.ideal_vector).flatten()
        
        # Convert to probability format (2D array with probabilities for each class)
        # Since we only have one class, return [1-score, score] format
        probs = np.column_stack([1 - similarities, similarities])
        return probs
