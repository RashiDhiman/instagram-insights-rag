import json
import chromadb
from sentence_transformers import SentenceTransformer
from src.config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL
from src.data import load_records, build_sqlite

def main():
    records = load_records()
    if not records:
        raise SystemExit("No CSV data found. Put reels_dataset.csv, stories_dataset.csv and posts_dataset.csv in data/.")
    count = build_sqlite(records)
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
    batch_size = 64
    for start in range(0, len(records), batch_size):
        batch = records[start:start+batch_size]
        texts = [r["semantic_text"] or r["caption"] or r["id"] for r in batch]
        embeddings = model.encode(texts, normalize_embeddings=True).tolist()
        metadatas = []
        for r in batch:
            md = {"kind": r["kind"], "record_id": r["record_id"], "published_at": r["published_at"] or "", "caption": r["caption"][:1500]}
            # Chroma metadata values must be scalar.
            metadatas.append(md)
        collection.add(ids=[r["id"] for r in batch], documents=texts, embeddings=embeddings, metadatas=metadatas)
    print(f"Indexed {count} records into SQLite and Chroma.")
    print(f"Chroma collection count: {collection.count()}")

if __name__ == "__main__":
    main()
