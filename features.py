from .extractor import extract_text_from_pdf
from .cleaner import clean_text


def process_resume(pdf_path):
    raw = extract_text_from_pdf(pdf_path)
    clean = clean_text(raw)
    return clean
