"""
SwiftVisa - Configuration Settings
Central configuration for all components (multi-country edition)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# LM Studio Configuration — supports environment variables for deployment
LM_STUDIO_CONFIG = {
    "base_url": os.getenv("LM_STUDIO_BASE_URL", "http://192.168.0.103:1234/v1"),
    "model": os.getenv("LM_STUDIO_MODEL", "llama-3.2-3b-instruct"),
    "temperature": float(os.getenv("LM_STUDIO_TEMPERATURE", "0.3")),
    "max_tokens": int(os.getenv("LM_STUDIO_MAX_TOKENS", "500")),
    "top_p": float(os.getenv("LM_STUDIO_TOP_P", "0.9")),
}

# Embedding Model Configuration
EMBEDDING_CONFIG = {
    "model_name": "all-MiniLM-L6-v2",
    "cache_dir": str(MODELS_DIR / "sentence_transformer"),
    "batch_size": 32,
}

# FAISS Configuration
FAISS_CONFIG = {
    # Per-country index paths — built by build_vectorstore.py
    "index_paths": {
        "uk":          str(VECTORSTORE_DIR / "uk"          / "faiss_index"),
        "canada":      str(VECTORSTORE_DIR / "canada"      / "faiss_index"),
        "australia":   str(VECTORSTORE_DIR / "australia"   / "faiss_index"),
        "new_zealand": str(VECTORSTORE_DIR / "new_zealand" / "faiss_index"),
    },
    "similarity_metric": "cosine",
}

# Retrieval Configuration
RETRIEVAL_CONFIG = {
    "top_k": 5,  # Increased from 2 to get more context for LLM
    "score_threshold": 0.3,
    "rerank": True,
    "max_context_chars": 3000,  # Increased to accommodate more chunks
}

# ── Prompt Templates ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert visa eligibility assistant. Your role is to help users understand their visa eligibility based on official immigration policies for the requested country.

INSTRUCTIONS:
1. Use ONLY the provided policy context to answer questions
2. Be accurate and cite specific requirements when possible
3. If information is not in the context, say so clearly
4. Provide clear, structured answers
5. Include relevant warnings or important conditions
6. Be helpful but honest about limitations

IMPORTANT:
- Do not make up information
- Do not provide legal advice
- Encourage users to verify with official sources for final decisions"""

USER_PROMPT_TEMPLATE = """Based on the following visa policy information, please answer the user's question.

POLICY CONTEXT:
{context}

USER QUESTION:
{question}

Please provide a clear, accurate answer based only on the policy context above. If the context doesn't contain enough information to answer the question, say so."""

ELIGIBILITY_PROMPT_TEMPLATE = """Analyze the user profile against the provided visa policy context and provide a detailed assessment.

POLICY CONTEXT:
{context}

USER PROFILE:
{user_profile}

COUNTRY: {country}
VISA TYPE: {visa_type}

Provide a comprehensive eligibility evaluation with the following structure:
verdict: ELIGIBLE / NOT ELIGIBLE / UNCLEAR
explanation: Detailed reasoning behind the verdict
1. Eligibility Summary: Brief overall assessment
2. MISSING REQUIREMENTS: List any critical requirements not met
3. ADDITIONAL INFORMATION NEEDED: List any unclear or missing information needed for a full assessment

Be thorough but honest. If critical requirements are missing, state it clearly. If all requirements appear to be met, say so explicitly."""

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": str(LOGS_DIR / "rag_pipeline.log"),
}

# Create directories if they don't exist
for directory in [DATA_DIR, VECTORSTORE_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Create per-country data and vectorstore directories
SUPPORTED_COUNTRIES = ["uk", "canada", "australia", "new_zealand"]

for country in SUPPORTED_COUNTRIES:
    (DATA_DIR / f"{country}_policies").mkdir(parents=True, exist_ok=True)
    (VECTORSTORE_DIR / country / "faiss_index").mkdir(parents=True, exist_ok=True)