import csv
import os
import time
from pathlib import Path

from fastembed import TextEmbedding
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
FALLBACK_DATA_DIR = Path(os.getenv("FALLBACK_DATA_DIR", "/tmp/rag_data"))
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "docs")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, check_compatibility=False)
embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL)

DEFAULT_CSV = """title,role,company,summary,skills
Senior Platform Engineer,Senior Platform Engineer,Northwind Labs,"Builds resilient internal tools and cloud automation with strong focus on developer experience.",Python Docker Kubernetes Azure
Product Engineer,Product Engineer,Signal Harbor,"Designs product-facing features and helps teams turn prototypes into reliable user experiences.",React FastAPI Postgres UX Research
Technical Consultant,Technical Consultant,Open Field Studio,"Advises clients on system architecture, observability, and deployment workflows for modern web products.",Architecture Observability DevOps CI/CD
"""


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
        for index, row in enumerate(reader):
            values = [str(value).strip() for value in row.values() if value and str(value).strip()]
            if not values:
                continue
            yield {
                "id": index,
                "source": path.name,
                "text": " ".join(values),
            }


def read_pdf_documents(path: Path):
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not text.strip():
        return
    yield {
        "id": 0,
        "source": path.name,
        "text": text.strip(),
    }


def ensure_seed_data() -> Path:
    if DATA_DIR.exists() and any(DATA_DIR.iterdir()):
        return DATA_DIR

    FALLBACK_DATA_DIR.mkdir(parents=True, exist_ok=True)
    seed_file = FALLBACK_DATA_DIR / "sample_documents.csv"
    if not seed_file.exists():
        seed_file.write_text(DEFAULT_CSV, encoding="utf-8")
    return FALLBACK_DATA_DIR


def load_documents() -> list[dict]:
    documents = []
    data_root = ensure_seed_data()

    for file_path in sorted(data_root.iterdir()):
        if file_path.suffix.lower() == ".csv":
            documents.extend(read_csv_documents(file_path))
        elif file_path.suffix.lower() == ".pdf":
            documents.extend(read_pdf_documents(file_path))

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
                payload={
                    "source": document["source"],
                    "text": document["text"],
                },
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
    print(f"Indexed {len(points)} documents into Qdrant collection '{COLLECTION_NAME}'.")


def main() -> None:
    wait_for_qdrant()
    ensure_collection()
    documents = load_documents()
    upsert_documents(documents)


if __name__ == "__main__":
    main()
