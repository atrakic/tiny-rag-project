import os
import re
from difflib import SequenceMatcher

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from fastembed import TextEmbedding

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "docs")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, check_compatibility=False)
embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL)

app = FastAPI(title="Document RAG")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str


@app.on_event("startup")
def startup() -> None:
    pass


@app.get("/health")
def health() -> dict:
    try:
        qdrant_client.get_collections()
        return {"status": "ok", "qdrant": "ok"}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "qdrant": "unavailable", "detail": str(exc)},
        )


def fuzzy_search_fallback(query: str) -> list[dict]:
    query_lower = query.strip().lower()
    cleaned_query = re.sub(r"[^a-z0-9]+", "", query_lower)
    if not cleaned_query or len(cleaned_query) < 3:
        return []

    points, _ = qdrant_client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True,
        with_vectors=False,
    )

    matches = []
    for point in points:
        payload = point.payload or {}
        text = payload.get("text", "")
        candidate_text = " ".join(part for part in [payload.get("city", ""), text] if part)
        if not candidate_text:
            continue

        candidate_tokens = [
            token for token in re.split(r"[^a-z0-9]+", candidate_text.lower()) if len(token) > 2
        ]
        if not candidate_tokens:
            continue

        ratio = max(
            SequenceMatcher(None, query_lower, token).ratio()
            for token in candidate_tokens
        )
        if ratio >= 0.7:
            matches.append({
                "id": str(point.id),
                "score": round(ratio, 4),
                "source": payload.get("source", "unknown"),
                "text": text,
            })

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:5]


def build_answer_from_results(query: str, results: list[dict]) -> str:
    if not results:
        return "I could not find enough relevant information in your indexed documents for that question. Try asking about a topic, person, file, or subject that exists in your data."

    snippets = []
    for item in results[:3]:
        text = str(item.get("text", "")).strip()
        if text:
            snippets.append(text[:350].rstrip() + ("..." if len(text) > 350 else ""))

    if not snippets:
        return "I found matching records, but they do not contain readable text to summarize."

    context = "\n\n".join(f"- {snippet}" for snippet in snippets)
    return (
        f"Based on your indexed data, here is what I found for '{query}':\n\n"
        f"{context}\n\n"
        "These passages are the most relevant matches from your documents."
    )


@app.post("/api/search")
def search_documents(payload: SearchRequest = Body(...)) -> dict:
    cleaned_query = re.sub(r"[^a-z0-9]+", "", payload.query.strip().lower())
    if len(cleaned_query) < 3:
        return {"results": []}

    query_vector = next(iter(embedding_model.embed([payload.query])))
    query_vector = [float(value) for value in query_vector]

    hits = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=5,
        with_payload=True,
    )

    results = []
    for hit in hits:
        results.append(
            {
                "id": str(hit.id),
                "score": round(float(hit.score), 4),
                "source": hit.payload.get("source", "unknown"),
                "text": hit.payload.get("text", ""),
            }
        )

    fuzzy_matches = fuzzy_search_fallback(payload.query)
    if fuzzy_matches and (not results or fuzzy_matches[0]["score"] >= max((item["score"] for item in results), default=0.0) + 0.2):
        results = fuzzy_matches

    return {"results": results}


@app.post("/api/chat")
def chat_documents(payload: SearchRequest = Body(...)) -> dict:
    cleaned_query = re.sub(r"[^a-z0-9]+", "", payload.query.strip().lower())
    if len(cleaned_query) < 3:
        return {"answer": "Please ask a more specific question about your documents.", "sources": []}

    search_response = search_documents(payload)
    results = search_response.get("results", [])
    answer = build_answer_from_results(payload.query, results)
    return {
        "answer": answer,
        "sources": [
            {
                "source": item.get("source", "unknown"),
                "score": item.get("score", 0),
                "text": item.get("text", ""),
            }
            for item in results[:3]
        ],
    }
