import os
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from docx import Document as DocxDocument
import pypdf
from app.config import settings

class TacticalChunker:
    """
    Sliding window chunker with configurable chunk size and overlap.
    """
    @staticmethod
    def chunk_text(
        text: str, 
        source: str, 
        prefix: str = "", 
        chunk_size: int = settings.CHUNK_SIZE, 
        overlap: int = settings.CHUNK_OVERLAP,
        meta_extra: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        chunks = []
        words = text.split()
        if not words:
            return chunks

        start = 0
        chunk_idx = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_slice = " ".join(words[start:end])
            
            chunk_content = f"{prefix}{chunk_slice}" if prefix else chunk_slice
            
            metadata = {
                "source": source,
                "chunk_id": chunk_idx,
                "start_word": start,
                "end_word": end,
                "total_words": len(words)
            }
            if meta_extra:
                metadata.update(meta_extra)

            chunks.append({
                "source": source,
                "content": chunk_content,
                "meta": metadata
            })
            chunk_idx += 1

            if end == len(words):
                break
            start += max(1, (chunk_size - overlap))

        return chunks

class DocumentParser:
    """
    Parser for tactical drop-zone files:
    Supports .txt, .pdf, .docx, .csv, .xlsx, .xls, .md, .log
    """

    @staticmethod
    def parse_file(file_path: Path) -> List[Dict[str, Any]]:
        suffix = file_path.suffix.lower()
        chunks = []
        
        try:
            if suffix in [".txt", ".text", ".md", ".log"]:
                chunks = DocumentParser._parse_text(file_path)
            elif suffix == ".pdf":
                chunks = DocumentParser._parse_pdf(file_path)
            elif suffix == ".docx":
                chunks = DocumentParser._parse_docx(file_path)
            elif suffix == ".csv":
                chunks = DocumentParser._parse_csv(file_path)
            elif suffix in [".xlsx", ".xls"]:
                chunks = DocumentParser._parse_excel(file_path)
            else:
                print(f"[TACTICAL WARNING] Unsupported format: {file_path.name}")
        except Exception as e:
            print(f"[RECON ERROR] Failed processing {file_path.name}: {str(e)}")

        return chunks

    @staticmethod
    def _parse_text(file_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts content from plain text (.txt, .md, .log) files and applies chunking.
        """
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return TacticalChunker.chunk_text(
            text=content,
            source=file_path.name,
            prefix=f"[FILE: {file_path.name} | TACTICAL TEXT INTEL]:\n",
            meta_extra={"doc_type": "txt"}
        )

    @staticmethod
    def _parse_pdf(file_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts pages from PDF, applies page tagging and sliding window chunking.
        """
        reader = pypdf.PdfReader(str(file_path))
        chunks = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                page_chunks = TacticalChunker.chunk_text(
                    text=text,
                    source=file_path.name,
                    prefix=f"[FILE: {file_path.name} | PAGE {idx+1}]:\n",
                    meta_extra={"doc_type": "pdf", "page": idx + 1}
                )
                chunks.extend(page_chunks)
        return chunks

    @staticmethod
    def _parse_docx(file_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts paragraphs and tables from Word (.docx), applying sliding window chunking.
        """
        doc = DocxDocument(file_path)
        full_text = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                full_text.append(text)
        
        # Table data extraction
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    full_text.append(" | ".join(row_text))

        all_content = "\n".join(full_text)
        return TacticalChunker.chunk_text(
            text=all_content,
            source=file_path.name,
            prefix=f"[FILE: {file_path.name} | DOCX INTEL]:\n",
            meta_extra={"doc_type": "docx"}
        )

    @staticmethod
    def _parse_csv(file_path: Path) -> List[Dict[str, Any]]:
        """
        Chunks CSV with column summaries and sliding row batches.
        """
        df = pd.read_csv(file_path)
        chunks = []
        batch_size = 15
        total_rows = len(df)
        
        # Header/Overview chunk
        summary = f"[FILE: {file_path.name} | CSV SCHEMA & OVERVIEW]\nColumns: {', '.join(df.columns.astype(str))}\nTotal Rows: {total_rows}\nSample Data:\n{df.head(3).to_string(index=False)}"
        chunks.append({
            "source": file_path.name,
            "content": summary,
            "meta": {"doc_type": "csv_summary", "rows": total_rows}
        })

        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i : i + batch_size]
            content = f"[FILE: {file_path.name} | ROWS {i+1} TO {min(i+batch_size, total_rows)} OF {total_rows}]:\n"
            content += batch.to_string(index=False)
            chunks.append({
                "source": file_path.name,
                "content": content,
                "meta": {"doc_type": "csv_data", "start_row": i, "end_row": min(i+batch_size, total_rows)}
            })
        return chunks

    @staticmethod
    def _parse_excel(file_path: Path) -> List[Dict[str, Any]]:
        """
        Chunks Excel sheets with headers, column schemas, and row batches.
        """
        excel_file = pd.ExcelFile(file_path)
        chunks = []
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            batch_size = 15
            total_rows = len(df)
            
            summary = f"[FILE: {file_path.name} | SHEET: {sheet_name} OVERVIEW]\nColumns: {', '.join(df.columns.astype(str))}\nTotal Rows: {total_rows}\nPreview:\n{df.head(3).to_string(index=False)}"
            chunks.append({
                "source": file_path.name,
                "content": summary,
                "meta": {"doc_type": "excel_summary", "sheet": sheet_name}
            })

            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i : i + batch_size]
                content = f"[FILE: {file_path.name} | SHEET: {sheet_name} | ROWS {i+1}-{min(i+batch_size, total_rows)}]:\n"
                content += batch.to_string(index=False)
                chunks.append({
                    "source": file_path.name,
                    "content": content,
                    "meta": {"doc_type": "excel_data", "sheet": sheet_name, "start_row": i}
                })
        return chunks
