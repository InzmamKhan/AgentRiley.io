from pathlib import Path
from typing import List, Dict, Any
from app.config import settings
from app.services.document_parser import DocumentParser
from app.services.vector_store import TacticalVectorStore
from app.services.rag_engine import AgentRileyRAG

class TacticalController:
    def __init__(self):
        self.vector_store = TacticalVectorStore()
        self.rag_engine = AgentRileyRAG(self.vector_store)

    def scan_and_ingest(self) -> Dict[str, Any]:
        """
        Scans the `documents/` directory, extracts chunks with sliding window
        from .pdf, .docx, .csv, .xlsx, etc., and ingests into in-memory Qdrant.
        """
        doc_dir = Path(settings.DOCUMENTS_DIR)
        all_files = [f for f in doc_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
        
        if not all_files:
            return {
                "status": "EMPTY_DROPZONE",
                "message": "Drop zone is clear. No tactical files found in documents/.",
                "indexed_files": [],
                "total_chunks": 0
            }

        total_chunks = []
        indexed_names = []

        for f in all_files:
            file_chunks = DocumentParser.parse_file(f)
            if file_chunks:
                total_chunks.extend(file_chunks)
                indexed_names.append(f.name)

        if total_chunks:
            self.vector_store.build_index(total_chunks)

        return {
            "status": "INDEXED",
            "message": f"Successfully secured and indexed {len(indexed_names)} files ({len(total_chunks)} chunks into In-Memory Qdrant).",
            "indexed_files": indexed_names,
            "total_chunks": len(total_chunks)
        }

    def process_query(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        return self.rag_engine.execute_recon(query=query, top_k=top_k)

    def get_recon_stats(self) -> Dict[str, Any]:
        stats = self.vector_store.get_stats()
        doc_dir = Path(settings.DOCUMENTS_DIR)
        current_disk_files = [f.name for f in doc_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
        stats["disk_files"] = current_disk_files
        return stats
