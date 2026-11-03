import csv
import json
import os
import time
from pathlib import Path

from fastembed import TextEmbedding
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "docs")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, check_compatibility=False)
embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL)


def wait_for_qdrant() -> None:
    for attempt in range(30):
        try:
            client.get_collections()
            return
        except Exception:
            if attempt == 29:
                raise
            time.sleep(2)


def ensure_collection() -> None:
    collections = client.get_collections().collections
    if any(collection.name == COLLECTION_NAME for collection in collections):
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )


def read_csv_documents(path: Path):
    with path.open("r", encoding="utf-8", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            values = [str(value).strip() for value in row.values() if value and str(value).strip()]
            if values:
                yield {"source": path.name, "text": " ".join(values)}


def read_text_documents(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if text:
        yield {"source": path.name, "text": text}


def read_json_documents(path: Path):
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (json.JSONDecodeError, OSError, ValueError):
        return

    chunks = []

    def walk(value):
        if isinstance(value, dict):
            for key, nested in value.items():
                walk(key)
                walk(nested)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, (str, int, float, bool)):
            text = str(value).strip()
            if text:
                chunks.append(text)

    walk(payload)
    if chunks:
        yield {"source": path.name, "text": " ".join(chunks)}


def read_pdf_documents(path: Path):
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if text.strip():
        yield {"source": path.name, "text": text.strip()}


def iter_documents(data_root: Path):
    for file_path in sorted(data_root.rglob("*")):
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()
        if suffix == ".csv":
            yield from read_csv_documents(file_path)
        elif suffix in {".txt", ".md", ".rst", ".log"}:
            yield from read_text_documents(file_path)
        elif suffix == ".json":
            yield from read_json_documents(file_path)
        elif suffix == ".pdf":
            yield from read_pdf_documents(file_path)


def load_documents() -> list[dict]:
    if not DATA_DIR.exists():
        print(f"No data directory found at {DATA_DIR}.")
        return []

    documents = list(iter_documents(DATA_DIR))
    if not documents:
        print(f"No user data found in {DATA_DIR}. Nothing to index.")
    return documents


def upsert_documents(documents: list[dict]) -> None:
    if not documents:
        print(f"No documents found in {DATA_DIR}.")
        return

    texts = [document["text"] for document in documents]
    embeddings = list(embedding_model.embed(texts))
    points = []

    for index, (document, vector) in enumerate(zip(documents, embeddings)):
        points.append(
            PointStruct(
                id=index + 1,
                vector=[float(value) for value in vector],
                payload={"source": document["source"], "text": document["text"]},
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
    print(f"Indexed {len(points)} documents into Qdrant collection '{COLLECTION_NAME}'.")


def main() -> None:
    wait_for_qdrant()
    ensure_collection()
    upsert_documents(load_documents())


if __name__ == "__main__":
    main()
