from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
DB_PATH = STORAGE_DIR / "instagram.db"
CHROMA_DIR = STORAGE_DIR / "chroma"
COLLECTION_NAME = "instagram_content"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
