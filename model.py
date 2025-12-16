import joblib
import os
from app.scorer import WebDevScorer

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../ml/trained_model.pkl")
VECTORIZER_PATH = os.path.join(
    os.path.dirname(__file__), "../ml/vectorizer.pkl")


class ResumeModel:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.vectorizer = joblib.load(VECTORIZER_PATH)

    def predict(self, text):
        vectors = self.vectorizer.transform([text])
        prediction = self.model.predict(vectors)[0]
        probability = self.model.predict_proba(vectors)[0].max()
        return prediction, float(probability)
