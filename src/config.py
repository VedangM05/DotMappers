import os
from dotenv import load_dotenv

load_dotenv()

# Workspace paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, "support_tickets.csv")
SQLITE_DB_PATH = os.path.join(BASE_DIR, "support_tickets.db")

# LLM Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Active LLM Provider preference: groq, gemini, or fallback
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto")

# Vector Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM = 384

# Server Ports
API_PORT = int(os.getenv("API_PORT", 8000))
UI_PORT = int(os.getenv("UI_PORT", 3000))
