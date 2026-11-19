from typing import List, Dict, Any
from openai import OpenAI
from app.config import settings
from app.services.vector_store import TacticalVectorStore
from app.models.schemas import DocumentSource

RILEY_SYSTEM_PROMPT = """You are Simon 'Ghost' Riley (Callsign: Agent Riley, Bravo 0-7), a legendary special forces tactical intelligence operator.
Your demeanor is sharp, disciplined, vigilant, mission-focused, and unmistakably Call of Duty / Special Ops styled.

Your operational directive:
1. Provide accurate, clear, and actionable intelligence strictly derived from the retrieved mission documents.
2. If the answer is directly in the documents (data tables, spreadsheets, mission logs, docx files, PDF debriefs), state the exact details, facts, numbers, or breakdown.
3. If the retrieved intel lacks the necessary data to answer, state clearly in tactical terms (e.g. "Negative, Bravo. That intel is not in our field debriefs / drop files.") without hallucinating.
4. Maintain a subtle tactical Special Operations tone (e.g. "Copy that", "Intel verified", "Sitrep:", "Hostile signals checked", "Bravo 0-7 out"), but keep answers highly readable and helpful.
"""

class AgentRileyRAG:
    def __init__(self, vector_store: TacticalVectorStore):
        self.vector_store = vector_store
        self.client = OpenAI(
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY
        )

    def execute_recon(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """
        Retrieves context from In-Memory Qdrant and queries NVIDIA NIM LLM.
        """
        # Step 1: Retrieval via Qdrant
        search_results = self.vector_store.search(query, top_k=top_k)
        
        sources: List[DocumentSource] = []
        context_blocks = []

        for rank, (chunk, score) in enumerate(search_results):
            sources.append(DocumentSource(
                source=chunk.get("source", "Unknown"),
                chunk_id=rank + 1,
                content=chunk.get("content", "")[:300] + ("..." if len(chunk.get("content", "")) > 300 else ""),
                score=round(score, 4)
            ))
            context_blocks.append(f"--- [INTEL SOURCE {rank+1}: {chunk.get('source')}] ---\n{chunk.get('content')}")

        context_text = "\n\n".join(context_blocks) if context_blocks else "NO MATCHING INTEL FOUND IN DROP ZONE."

        # Step 2: Generation via NVIDIA NIM LLM
        user_prompt = f"""[TACTICAL INTEL LOGS RETRIEVED]:
{context_text}

[INCOMING DIRECTIVE / OPERATOR QUERY]:
{query}

Deliver a tactical, precise response based strictly on the retrieved intel."""

        try:
            response = self.client.chat.completions.create(
                model=settings.NVIDIA_LLM_MODEL,
                messages=[
                    {"role": "system", "content": RILEY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=1024
            )
            answer = response.choices[0].message.content
            status = "MISSION_SUCCESS"
        except Exception as e:
            err_msg = str(e)
            if "410" in err_msg:
                answer = (
                    f"Comms jammed, commander. NVIDIA returned HTTP 410 (Endpoint Deprecated). "
                    f"The model '{settings.NVIDIA_LLM_MODEL}' is no longer hosted on build.nvidia.com. "
                    f"Please update 'NVIDIA_LLM_MODEL' in your .env to an active model (e.g. meta/llama-3.3-70b-instruct or mistralai/mistral-large-2-instruct)."
                )
            elif "401" in err_msg:
                answer = "Comms jammed, commander. Error 401 Unauthorized: Please check that your NVIDIA_API_KEY in .env is valid."
            else:
                answer = f"Comms jammed, commander. Error reaching NVIDIA Command: {err_msg}"
            status = "COMMS_FAILURE"

        return {
            "callsign": "Agent Riley [Bravo 0-7]",
            "status": status,
            "answer": answer,
            "sources": sources
        }
