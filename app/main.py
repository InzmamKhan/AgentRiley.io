from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.api import router as api_router, controller
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-scan documents on startup so the in-memory vector store is ready immediately
    print("[TACTICAL BOOT] Auto-indexing files from drop zone into In-Memory Qdrant...")
    try:
        controller.scan_and_ingest()
    except Exception as e:
        print(f"[TACTICAL BOOT ERROR] Startup indexing error: {e}")
    yield

app = FastAPI(
    title="AgentRiley [Bravo 0-7] Tactical RAG Backend",
    version="1.0.0",
    description="Military-grade tactical RAG backend powered by NVIDIA NIM & In-Memory Qdrant.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def tactical_sitrep():
    return {
        "callsign": "Agent Riley [Bravo 0-7]",
        "system": "Operational",
        "nvidia_endpoint": settings.NVIDIA_BASE_URL,
        "llm_model": settings.NVIDIA_LLM_MODEL,
        "embed_model": settings.NVIDIA_EMBED_MODEL,
        "docs_directory": settings.DOCUMENTS_DIR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
