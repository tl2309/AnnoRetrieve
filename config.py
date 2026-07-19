# config.py
import os

class Config:
    # ---------- Paths ----------
    DATA_ROOT = "./data"
    RAW_DIR = os.path.join(DATA_ROOT, "raw")
    GROUND_TRUTH_DIR = os.path.join(DATA_ROOT, "ground_truth")
    QUERY_DIR = os.path.join(DATA_ROOT, "queries")
    INDEX_DIR = "./index_storage"
    RESULT_DIR = "./results"

    # ---------- OpenAI ----------
    OPENAI_KEY = os.getenv("OPENAI_KEY", "your-openai-key-here")
    USE_MOCK_LLM = False   # Set True to avoid real API calls (for testing)

    # ---------- SchemaLoop ----------
    SR_THRESHOLD = 0.6          # extraction success rate
    FE_THRESHOLD = 0.3          # filtering efficiency
    MAX_SCHEMA_ITER = 5

    # ---------- Query Engine ----------
    LLM_BUDGET = 10             # max LLM calls per query (soft limit)
    REUSE_THRESHOLD = 10        # promote virtual field after this many extractions
    EXTRACT_ORDER = ["regex", "slm", "llm"]   # ascending cost

    # ---------- Evaluation ----------
    SAMPLE_SIZE_FOR_VERIFICATION = 5