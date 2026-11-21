import chromadb
from sentence_transformers import SentenceTransformer
from src.config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL

class Retriever:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_collection(COLLECTION_NAME)

    def search(self, question, top_k=5, kind=None):
        vector = self.model.encode([question], normalize_embeddings=True).tolist()[0]
        where = {"kind": kind} if kind else None
        result = self.collection.query(
            query_embeddings=[vector], n_results=min(top_k, self.collection.count()),
            where=where, include=["documents", "metadatas", "distances"]
        )
        hits = []
        for i, doc_id in enumerate(result["ids"][0]):
            hits.append({
                "id": doc_id,
                "text": result["documents"][0][i],
                "metadata": result["metadatas"][0][i],
                "distance": result["distances"][0][i],
            })
        return hits
