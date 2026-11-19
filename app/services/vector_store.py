from typing import List, Dict, Any, Tuple
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding
from app.config import settings

class TacticalVectorStore:
    """
    In-Memory Vector Store powered by QdrantClient(:memory:) and FastEmbed.
    Provides fast, local embedding generation and vector similarity search.
    """
    COLLECTION_NAME = "riley_tactical_intel"

    def __init__(self):
        # 1. Initialize In-Memory Qdrant Client
        self.client = QdrantClient(location=":memory:")
        
        # 2. Initialize FastEmbed Embedding Model
        print(f"[RECON BOOT] Initializing FastEmbed model '{settings.FASTEMBED_MODEL_NAME}'...")
        self.embed_model = TextEmbedding(model_name=settings.FASTEMBED_MODEL_NAME)
        
        # Determine embedding dimension
        sample_emb = list(self.embed_model.embed(["test"]))[0]
        self.dimension = len(sample_emb)
        print(f"[RECON BOOT] FastEmbed ready. Vector dimension: {self.dimension}")

        # Setup collection
        self._init_collection()
        self.total_chunks = 0
        self.indexed_files: List[str] = []

    def _init_collection(self):
        if self.client.collection_exists(self.COLLECTION_NAME):
            self.client.delete_collection(self.COLLECTION_NAME)
        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE)
        )

    def build_index(self, chunks: List[Dict[str, Any]]):
        """
        Embeds chunks using FastEmbed and indexes them in In-Memory Qdrant.
        """
        if not chunks:
            print("[TACTICAL ADVISORY] No chunks provided for indexing.")
            return

        self._init_collection() # Clean reset for fresh drop-zone sync
        print(f"[MISSION TASK] Ingesting {len(chunks)} chunks into In-Memory Qdrant via FastEmbed...")

        texts = [chunk["content"] for chunk in chunks]
        
        # FastEmbed generates generators for fast streaming / batching
        embeddings_generator = self.embed_model.embed(texts)
        
        points = []
        files_set = set()

        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings_generator)):
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=emb.tolist(),
                    payload={
                        "source": chunk["source"],
                        "content": chunk["content"],
                        "meta": chunk.get("meta", {})
                    }
                )
            )
            files_set.add(chunk["source"])

        # Bulk upload to In-Memory Qdrant
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points
        )
        self.total_chunks = len(points)
        self.indexed_files = list(files_set)
        print(f"[SYSTEM SECURED] In-Memory Qdrant indexed {self.total_chunks} vectors across {len(self.indexed_files)} files.")

    def search(self, query: str, top_k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        """
        Vector similarity search in In-Memory Qdrant using FastEmbed query embedding.
        Uses query_points (or search fallback depending on qdrant-client version).
        """
        if self.total_chunks == 0:
            return []

        # Generate query embedding
        query_emb = list(self.embed_model.embed([query]))[0].tolist()
        limit = min(top_k, self.total_chunks)

        results = []
        try:
            # Modern Qdrant client 1.10+ / 1.20+
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.COLLECTION_NAME,
                    query=query_emb,
                    limit=limit
                )
                points = response.points
                for hit in points:
                    chunk_data = {
                        "source": hit.payload.get("source", "Unknown"),
                        "content": hit.payload.get("content", ""),
                        "meta": hit.payload.get("meta", {})
                    }
                    score = getattr(hit, "score", 1.0)
                    results.append((chunk_data, float(score)))
            elif hasattr(self.client, "search"):
                response = self.client.search(
                    collection_name=self.COLLECTION_NAME,
                    query_vector=query_emb,
                    limit=limit
                )
                for hit in response:
                    chunk_data = {
                        "source": hit.payload.get("source", "Unknown"),
                        "content": hit.payload.get("content", ""),
                        "meta": hit.payload.get("meta", {})
                    }
                    results.append((chunk_data, float(hit.score)))
        except Exception as e:
            print(f"[QDRANT SEARCH ERROR] {e}")

        return results

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_documents": len(self.indexed_files),
            "total_chunks": self.total_chunks,
            "document_files": self.indexed_files,
            "vector_dim": self.dimension
        }
