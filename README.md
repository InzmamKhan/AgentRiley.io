# 💀 AgentRiley.io — Tactical Call of Duty RAG Agent

Agent Riley (Simon "Ghost" Riley / Callsign: Bravo 0-7) is a military-grade local RAG (Retrieval-Augmented Generation) agent powered by:
- **FastEmbed (`BAAI/bge-small-en-v1.5`)**: Local ultra-fast embedding model.
- **In-Memory Qdrant Vector Engine (`QdrantClient(location=":memory:")`)**: Blazing fast in-memory similarity search.
- **NVIDIA NIM API (`meta/llama-3.1-70b-instruct`)**: Elite LLM reasoning & response generation.
- **FastAPI MVC Backend**: Clean Model-View-Controller architecture.
- **Streamlit Tactical HUD**: Dark Neumorphic Call of Duty styled interface.

---

## 🗂️ Architecture (MVC Pattern)

```
AgentRiley.io/
├── app/
│   ├── config.py                 # System configurations, chunk size/overlap & settings
│   ├── main.py                   # FastAPI application initialization & server
│   ├── models/                   # [Model] Pydantic schemas (Query, Source, Stats)
│   │   └── schemas.py
│   ├── controllers/              # [Controller] RAG orchestration & drop-zone ingestion
│   │   └── rag_controller.py
│   ├── services/                 # Business logic, Embeddings & In-Memory Vector Store
│   │   ├── document_parser.py    # Multi-format parser & TacticalChunker (.pdf, .docx, .csv, .xlsx)
│   │   ├── vector_store.py       # In-Memory QdrantClient + FastEmbed implementation
│   │   └── rag_engine.py         # Simon Ghost Riley persona & NVIDIA NIM LLM synthesis
│   ├── routes/
│   │   └── api.py                # REST API endpoints (/query, /ingest, /stats, /upload)
│   └── views/                    # [View] Tactical Dark Neumorphic Streamlit HUD UI
│       └── streamlit_app.py
├── documents/                    # 🎯 TACTICAL DROP ZONE (Drop PDF, DOCX, CSV, XLSX files here!)
│   ├── mission_briefing_ghost.pdf
│   └── tactical_operations.csv
├── .env                          # Secret keys & NVIDIA credentials
├── .env.example                  # Environment configuration template
├── .gitignore                    # Complete gitignore for secrets, vector caches, and venvs
├── requirements.txt              # Project dependencies (FastEmbed, Qdrant-Client, etc.)
├── run.py                        # Unified tactical runner
└── README.md
```

---

## 🛠️ Tactical Chunking & In-Memory Vector Pipeline

1. **Drop Zone Multi-format Support**:
   - `.pdf` (Page extraction with tagged metadata)
   - `.docx` (Paragraph & table extraction)
   - `.csv` & `.xlsx` / `.xls` (Schema overviews + rolling row batches)
2. **Sliding Window Chunking**:
   - `CHUNK_SIZE`: 500 words
   - `CHUNK_OVERLAP`: 100 words
   - Configurable in `.env` / `app/config.py`
3. **In-Memory Qdrant + FastEmbed**:
   - In-memory vector database: `QdrantClient(location=":memory:")`
   - Local embedding generation: `FastEmbed TextEmbedding(model_name="BAAI/bge-small-en-v1.5")`
   - Zero external vector DB servers required.

---

## 🚀 Quick Setup & Deployment

### 1. Configure NVIDIA API Key
Edit the `.env` file and insert your NVIDIA API key:
```env
NVIDIA_API_KEY=nvapi-your-key-here
```
*(Get your key at [build.nvidia.com](https://build.nvidia.com))*

### 2. Install Dependencies
```bash
# Windows PowerShell
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Deploy Agent Riley
Run both backend and frontend together with the tactical launcher:
```bash
python run.py
```

Or run them individually in separate terminals:
- **FastAPI Tactical Backend**:
  ```bash
  python -m uvicorn app.main:app --reload --port 8000
  ```
- **Streamlit Tactical HUD**:
  ```bash
  streamlit run app/views/streamlit_app.py
  ```

---

## 🎨 Theme & User Interface
- **Dark Neumorphic Aesthetic**: Recessed telemetry panels, raised tactile buttons, dual-shadow dark cards.
- **Call of Duty HUD**: Tactical green and amber telemetry indicators, Task Force 141 branding, and Ghost Riley field briefing outputs.
- **Live Drop Zone Monitor**: Real-time tracking of files in `documents/` and vector chunk indexation status.
- **Direct Air Drop**: Upload files directly via the UI sidebar or drop them directly into the folder on your filesystem.
