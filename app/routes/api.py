import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.controllers.rag_controller import TacticalController
from app.models.schemas import QueryRequest, QueryResponse, IndexStatsResponse, IngestResponse
from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["Tactical Recon"])
controller = TacticalController()

@router.post("/query", response_model=QueryResponse)
def query_agent_riley(req: QueryRequest):
    """
    Submit a query or mission debrief request to Agent Riley.
    """
    result = controller.process_query(query=req.query, top_k=req.top_k or 4)
    return result

@router.post("/ingest", response_model=IngestResponse)
def reindex_dropzone():
    """
    Forces a fresh sweep of the `documents/` folder and indexes all files.
    """
    res = controller.scan_and_ingest()
    return res

@router.get("/stats", response_model=IndexStatsResponse)
def get_mission_stats():
    """
    Returns current active vector count, indexed documents, and status.
    """
    return controller.get_recon_stats()

@router.post("/upload")
def upload_file_to_dropzone(files: List[UploadFile] = File(...)):
    """
    Quick upload endpoint to directly deposit intel files into `documents/`
    """
    saved_files = []
    doc_dir = Path(settings.DOCUMENTS_DIR)
    doc_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        dest_path = doc_dir / file.filename
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)

    # Trigger indexing after upload
    ingest_result = controller.scan_and_ingest()

    return {
        "status": "UPLOAD_SUCCESS",
        "uploaded_files": saved_files,
        "index_result": ingest_result
    }
