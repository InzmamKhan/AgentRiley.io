# 💀 AgentRiley.io — Tactical Call of Duty RAG Intelligence Agent

> **"Bravo 0-7, standing by for intel ingestion and debrief."**  
> An autonomous, local-first Tactical Retrieval-Augmented Generation (RAG) system engineered for rapid document intelligence, multi-format file parsing, and zero-leakage local vector retrieval—personified as Simon "Ghost" Riley (Call of Duty: Modern Warfare).
>
> **Project Status:** 🟢 **Working Prototype / In Active Development**

---

## 🎯 Project Title & One-Line Value

- **Project:** AgentRiley.io
- **One-Line Value:** AgentRiley.io empowers defense analysts, operations teams, researchers, and technical squads to query mission-critical files (`.pdf`, `.docx`, `.csv`, `.xlsx`) with sub-second in-memory vector search and militarized, hallucination-resistant LLM debriefs.
- **Current Lifecycle State:** Working Prototype (Local Core & REST API fully operational; in-memory vector engine active).

---

## ⚡ Key Features

- **Multi-Format Drop-Zone Parsing:** Ingests unorganized files directly from `documents/` or via UI upload:
  - **PDF (`pypdf`):** Page-by-page text extraction with source tagging and page numbering metadata.
  - **Word Documents (`python-docx`):** Parses headers, paragraphs, and nested table cells into readable Markdown blocks.
  - **Tabular Data (`pandas`, `openpyxl`):** Automatically detects `.csv`, `.xlsx`, and `.xls` files, generates relational schema summaries, and chunks data into rolling row records.
- **Sliding-Window Tactical Chunker:** Configurable chunk sizing (default: 500 words) with sliding window overlap (default: 100 words) to preserve operational context across boundary sentences.
- **Local-Only Embedding Engine:** Uses `FastEmbed` with `BAAI/bge-small-en-v1.5` to generate 384-dimensional dense embeddings locally on CPU without external API calls or latency spikes.
- **Zero-Footprint In-Memory Vector Store:** Powered by `QdrantClient(location=":memory:")` utilizing cosine similarity. No local database servers (Docker/Postgres/Qdrant service) required.
- **NVIDIA NIM LLM Intelligence:** Integrates with `meta/llama-3.1-70b-instruct` via NVIDIA NIM's high-throughput API endpoints for reasoning, extraction, and synthesis.
- **Ghost Riley Tactical Persona Guardrails:** Strict prompt boundaries force the model to answer strictly based on retrieved documents, providing direct citations and explicitly denying requests with military brevity when intel is absent.
- **Dark Neumorphic Tactical HUD:** A custom Streamlit web interface styled with Call of Duty Task Force 141 aesthetics, recessed telemetry panels, live drop-zone metrics, and real-time query logs.

---

## 🏗️ Tech Stack & Architecture

### Technology Stack

| Layer | Component / Library | Purpose & Justification |
| :--- | :--- | :--- |
| **Backend Framework** | **FastAPI** (`0.110+`) | Asynchronous, OpenAPI-compliant REST API with Pydantic validation for high-speed endpoints. |
| **Server Engine** | **Uvicorn** (`0.28+`) | Lightning-fast ASGI web server implementation for production & local development. |
| **User Interface** | **Streamlit** (`1.32+`) | Rapid interactive web HUD styled with custom CSS (Neumorphic tactical theme). |
| **Embedding Generation** | **FastEmbed** (`BAAI/bge-small-en-v1.5`) | Ultra-fast ONNX-runtime CPU embeddings; eliminates PyTorch dependency overhead. |
| **Vector Database** | **Qdrant Client** (`:memory:`) | In-memory HNSW index & cosine similarity search with zero database infrastructure. |
| **LLM Inference** | **NVIDIA NIM API** (`llama-3.1-70b-instruct`) | High-tier reasoning and contextual synthesis running on NVIDIA's accelerated cloud. |
| **Document Parsers** | `pypdf`, `python-docx`, `pandas`, `openpyxl` | Native multi-format parsing for PDFs, Word briefs, and Excel/CSV spreadsheets. |
| **Environment & Config** | `pydantic-settings`, `python-dotenv` | Strictly validated environment variables with fail-fast loading. |

### Component Connection Flow

```
[ Tactical File Drop ] ──> documents/
                               │
                       [ Document Parser ] (PDF / DOCX / CSV / XLSX)
                               │
                       [ Tactical Chunker ] (Sliding window: 500w / 100w overlap)
                               │
                       [ FastEmbed Model ] (BAAI/bge-small-en-v1.5)
                               │ (384-dim dense vectors)
                               ▼
                   [ In-Memory Qdrant Engine ]
                               ▲
                               │ Cosine Similarity Search (Top-K)
                               │
[ Operator Query ] ──> [ Tactical Controller ]
                               │
                               ▼
                   [ RAG Synthesis Engine ]
                               │ (Context Chunks + Ghost Persona)
                               ▼
                     [ NVIDIA NIM API ]
                 (meta/llama-3.1-70b-instruct)
                               │
                               ▼
                  [ Declassified Field Sitrep ]
```

---

## 🏛️ MVC Structure

The project implements a clean separation of concerns following the **Model-View-Controller (MVC)** architectural pattern:

```
                  ┌────────────────────────────────────────┐
                  │              VIEW LAYER                │
                  │   app/views/streamlit_app.py (HUD)     │
                  └──────────────────┬─────────────────────┘
                                     │ HTTP (REST API)
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                             CONTROLLER LAYER                             │
│   app/routes/api.py           <──>  app/controllers/rag_controller.py    │
│   (HTTP Endpoint Routing)           (RAG Pipeline Orchestration)         │
└───────────────────────┬──────────────────────────┬───────────────────────┘
                        │                          │
                        ▼                          ▼
┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│          MODEL LAYER            │      │         SERVICES LAYER          │
│   app/models/schemas.py         │      │   app/services/document_parser  │
│   (Pydantic Request/Response)   │      │   app/services/vector_store     │
│   - QueryRequest / Response     │      │   app/services/rag_engine       │
│   - IndexStats / DocumentSource │      │   (Parsing, Embedding, Qdrant)  │
└─────────────────────────────────┘      └─────────────────────────────────┘
```

1. **Models (`app/models/schemas.py`):** Define the structural data contracts using Pydantic (`QueryRequest`, `QueryResponse`, `DocumentSource`, `IndexStatsResponse`, `IngestResponse`).
2. **Views (`app/views/streamlit_app.py`):** Presentation layer providing a Call of Duty Tactical HUD, rendering debriefs, telemetry stats, and drop-zone uploads.
3. **Controllers (`app/controllers/rag_controller.py` & `app/routes/api.py`):** Mediate between HTTP requests and business logic; coordinate ingestion sweeps, vector searches, and response packaging.
4. **Services (`app/services/`):** Pure domain logic handling document parsing, ONNX embedding generation, Qdrant in-memory operations, and NVIDIA NIM LLM communication.

---

## 📂 Project Structure

```
AgentRiley.io/
├── .env                              # Secret environment keys (Ignored by Git)
├── .env.example                      # Configuration template
├── .gitignore                        # Git exclusion rules
├── README.md                         # Project documentation and operational guide
├── requirements.txt                  # Python dependencies
├── run.py                            # Dual-process tactical launcher (FastAPI + Streamlit)
├── documents/                        # Drop-zone directory for mission files
│   ├── mission_briefing_ghost.pdf    # Sample operational PDF
│   └── tactical_operations.csv       # Sample tabular intel data
└── app/
    ├── config.py                     # Pydantic BaseSettings & configuration loader
    ├── main.py                       # FastAPI application setup, CORS, and lifecycle
    ├── controllers/
    │   └── rag_controller.py         # Controller orchestrating scan, ingest, and query logic
    ├── models/
    │   └── schemas.py                # Pydantic data models and API schemas
    ├── routes/
    │   └── api.py                    # REST API route handlers (/query, /ingest, /stats, /upload)
    ├── services/
    │   ├── document_parser.py        # File parsers (.pdf, .docx, .csv, .xlsx) & chunker
    │   ├── rag_engine.py             # NVIDIA NIM client & Ghost Riley persona prompting
    │   └── vector_store.py           # FastEmbed + Qdrant in-memory vector store service
    └── views/
        └── streamlit_app.py          # Dark Neumorphic Streamlit HUD interface
```

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.13)
- **NVIDIA NIM API Key:** Obtain a key from [NVIDIA API Catalog](https://build.nvidia.com).

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/AgentRiley.io.git
cd AgentRiley.io
```

### 3. Create & Activate Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy the `.env.example` file to create your `.env`:
```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

Edit `.env` and fill in your credentials:
```env
# NVIDIA NIM API Configuration
NVIDIA_API_KEY=nvapi-your-real-key-here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_LLM_MODEL=meta/llama-3.1-70b-instruct

# FastEmbed Local Model
FASTEMBED_MODEL_NAME=BAAI/bge-small-en-v1.5

# Server & Ingestion Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DOCUMENTS_DIR=./documents

# Tactical Chunking Strategy
CHUNK_SIZE=500
CHUNK_OVERLAP=100
TOP_K=4
```

### 6. Launch the Application

#### Option A: Unified Launcher (Recommended)
Spawns both the FastAPI backend and Streamlit HUD concurrently:
```bash
python run.py
```

#### Option B: Standalone Processes (Separate Terminals)
- **Terminal 1: FastAPI Tactical Backend**
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```
- **Terminal 2: Streamlit Tactical HUD**
  ```bash
  streamlit run app/views/streamlit_app.py --server.port 8501
  ```

- **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Tactical HUD UI:** [http://localhost:8501](http://localhost:8501)

---

## 💻 Usage Examples

### 1. Ingest Documents into Vector Memory
Drop files directly into `documents/` or trigger a sweep via cURL:

```bash
curl -X POST http://localhost:8000/api/v1/ingest
```

**Response:**
```json
{
  "status": "success",
  "message": "Indexed 2 files into 8 tactical chunks.",
  "indexed_files": [
    "mission_briefing_ghost.pdf",
    "tactical_operations.csv"
  ],
  "total_chunks": 8
}
```

### 2. Query Agent Riley
Submit an operational query:

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are our extraction protocols in the briefing document?",
    "top_k": 3
  }'
```

**Response:**
```json
{
  "callsign": "Agent Riley [Bravo 0-7]",
  "status": "success",
  "answer": "Sitrep: According to the mission debriefing, extraction protocol Alpha initiates at coordinates Grid 34-North upon objective completion. Primary LZ is designated LZ Falcon with Exfil Osprey Bravo-2 standing by. Watch your corners.",
  "sources": [
    {
      "source": "mission_briefing_ghost.pdf (Page 2)",
      "chunk_id": 1,
      "content": "Extraction Protocol: LZ Falcon designated at Grid 34-North...",
      "score": 0.8842
    }
  ]
}
```

### 3. Check Recon Telemetry & Stats
```bash
curl -X GET http://localhost:8000/api/v1/stats
```

**Response:**
```json
{
  "total_documents": 2,
  "total_chunks": 8,
  "document_files": [
    "mission_briefing_ghost.pdf",
    "tactical_operations.csv"
  ],
  "vector_dim": 384,
  "indexed_at": "2026-11-25T18:30:00"
}
```

---

## ⚖️ Design Decisions & Trade-offs

| Decision | Selected Approach | Alternative Considered | Trade-off / Rationale |
| :--- | :--- | :--- | :--- |
| **Vector Storage** | In-Memory Qdrant (`location=":memory:"`) | Persistent Qdrant Docker / PostgreSQL pgvector | **Gain:** Zero installation friction, no external service dependencies, ultra-fast for small-to-medium collections.<br>**Trade-off:** Vectors are ephemeral; restarting the application requires re-indexing the `documents/` folder. |
| **Embeddings** | FastEmbed (`bge-small-en-v1.5`) | OpenAI `text-embedding-3-small` / PyTorch HuggingFace | **Gain:** Completely local, free, zero network overhead, runs efficiently on CPU via ONNX Runtime without heavy torch wheels.<br>**Trade-off:** Limited to 384 dimensions; not ideal for extremely large multi-million token corpora. |
| **LLM Inference** | NVIDIA NIM API (`llama-3.1-70b-instruct`) | Local Ollama / vLLM / OpenAI API | **Gain:** Enterprise-grade 70B parameter reasoning at near-zero local VRAM cost with high token throughput.<br>**Trade-off:** Requires an active internet connection and valid NVIDIA API key. |
| **Chunking Strategy** | Word-based Sliding Window (500 words / 100 overlap) | Semantic boundary / Sentence chunking | **Gain:** Predictable chunk shapes, avoids truncation of tabular lines and multi-sentence facts.<br>**Trade-off:** Occasional splitting of semantic paragraphs. |
| **Architecture** | Classic MVC via FastAPI + Streamlit | Monolithic Streamlit script | **Gain:** Decoupled business logic allows headless automated API usage, webhooks, or third-party client integrations alongside the HUD UI.<br>**Trade-off:** Requires running two services (managed transparently via `run.py`). |

---

## 🚦 Current Status, Limitations & Roadmap

### Current Status
- ✅ Multi-format document parser working (`.pdf`, `.docx`, `.csv`, `.xlsx`).
- ✅ FastEmbed CPU embedding pipeline running locally.
- ✅ In-Memory Qdrant cosine vector search working.
- ✅ FastAPI backend endpoints active (`/query`, `/ingest`, `/stats`, `/upload`).
- ✅ Streamlit Neumorphic HUD running with live chat and file uploads.

### Known Limitations & Edge Cases
1. **Volatile Vector Index:** Because Qdrant runs in `:memory:`, restarting the backend wipes vector records until the drop-zone is scanned again on startup or via `/api/v1/ingest`.
2. **Tabular Chunking Limits:** Highly complex spreadsheets with merged cells or multiple nested sheets may flatten into simplified text representations.
3. **Scanned PDF OCR:** Non-selectable / scanned image PDFs are not currently OCR-processed (requires `pytesseract` or external OCR models).
4. **Single-Node Scalability:** In-memory vector allocation is bound to host RAM. Large corpuses (>100,000 pages) require migrating to disk-backed Qdrant.

### Strategic Roadmap
- [ ] **Persistent Vector Storage:** Add an optional configuration flag to persist Qdrant storage to disk (`./data/qdrant_db`) or connect to remote Qdrant clusters.
- [ ] **OCR Ingestion Support:** Integrate local OCR (`Tesseract` or `Surya`) for scanned tactical imagery and mission diagrams.
- [ ] **Hybrid Search:** Implement BM25 keyword search alongside dense vector cosine similarity (Sparse + Dense Reranking).
- [ ] **Streaming Responses:** Enable SSE (Server-Sent Events) on FastAPI and Streamlit for real-time typewriter debrief generation.
- [ ] **Automated Test Suite:** Implement comprehensive unit and integration tests using `pytest` and `httpx`.

---

## 🧪 Testing & Verification

### Current Test Coverage
- **Status:** Currently in manual and smoke-test verification phase. Formal unit and end-to-end test suites are in the roadmap.

### Verification Steps

1. **Verify Backend Health & OpenAPI Schema:**
   Start the backend and check the Swagger docs:
   ```bash
   uvicorn app.main:app --port 8000
   # Open http://localhost:8000/docs in your browser
   ```

2. **Test Document Ingestion Endpoint:**
   Ensure files are present in `documents/`, then run:
   ```bash
   curl -X POST http://localhost:8000/api/v1/ingest
   ```
   *Expected Output:* Status `success` with non-zero `total_chunks`.

3. **Test Retrieval & LLM Generation:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Status report", "top_k": 2}'
   ```
   *Expected Output:* JSON response containing `Agent Riley [Bravo 0-7]` callsign and field debrief.

4. **Code Quality & Linting:**
   You can run static analysis and type checks:
   ```bash
   pip install flake8 mypy
   flake8 app --max-line-length=120
   ```

---

## 📄 License
This project is licensed under the MIT License — see the repository for full license details.
