"""
Configuration file for BioLitAI
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database configuration
DB_PATH = DATA_DIR / "bioliteai.db"

# PubMed API configuration
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_SEARCH_URL = f"{PUBMED_BASE_URL}/esearch.fcgi"
PUBMED_FETCH_URL = f"{PUBMED_BASE_URL}/efetch.fcgi"
PUBMED_EMAIL = "researcher@example.com"  # Required by NCBI Entrez
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY", "")  # Optional, increases rate limits

# NLP Model configuration
NER_MODEL = "en_core_sci_md"  # spaCy scientific model
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"  # Hugging Face model ID

# LLM configuration
LLM_MAX_LENGTH = 512
LLM_DEVICE = "cpu"  # Change to "cuda" if GPU available
LLM_TEMPERATURE = 0.7

# Streamlit configuration
STREAMLIT_PAGE_CONFIG = {
    "page_title": "BioLitAI",
    "page_icon": "🧬",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Search configuration
MAX_RESULTS_PER_SEARCH = 100
MIN_ABSTRACT_LENGTH = 100

# Named entities to extract
ENTITIES_TO_EXTRACT = {
    "DISEASE": "Diseases and medical conditions",
    "GENE": "Genes and proteins",
    "CHEMICAL": "Drugs and chemicals",
    "GPE": "Geographic locations",
}
