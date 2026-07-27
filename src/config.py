import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Define GOOGLE_API_KEY en tu archivo .env (ver .env.example)")

MODEL_NAME = "gemini-flash-latest"
EMBEDDING_MODEL = "models/gemini-embedding-001"

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_BASE_DIR, "data")
POLITICAS_DIR = os.path.join(DATA_DIR, "politicas")
INVENTARIO_PATH = os.path.join(DATA_DIR, "inventario_de_supermercado_latam.xlsx")
VECTORSTORE_DIR = os.path.join(_BASE_DIR, "vectorstore")
