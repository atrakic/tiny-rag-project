import argparse
import os

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

DEFAULT_HOST = os.getenv("QDRANT_HOST", "localhost")
DEFAULT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
DEFAULT_COLLECTION = os.getenv("QDRANT_COLLECTION") or os.getenv("COLLECTION_NAME", "example_demo")
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DEFAULT_VECTOR_SIZE = int(os.getenv("QDRANT_VECTOR_SIZE") or os.getenv("VECTOR_SIZE", "384"))
EMBEDDING_MODEL = TextEmbedding(model_name=DEFAULT_EMBEDDING_MODEL)


def parse_args():
    parser = argparse.ArgumentParser(description="Create and seed a Qdrant collection.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Qdrant host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Qdrant port")
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        help="Collection name to create or use",
    )
    parser.add_argument(
        "--vector-size",
        type=int,
        default=DEFAULT_VECTOR_SIZE,
        help="Embedding dimension for the collection",
    )
    parser.add_argument(
        "--action",
        choices=["setup", "seed", "reset"],
        default="setup",
        help="setup: ensure collection exists; seed: create and insert demo data; reset: recreate collection then seed",
    )
    return parser.parse_args()


def get_client(host: str, port: int) -> QdrantClient:
    return QdrantClient(host=host, port=port, check_compatibility=False)


def ensure_collection(client: QdrantClient, collection_name: str, vector_size: int):
    try:
        client.get_collection(collection_name=collection_name)
        print(f"Collection {collection_name} already exists")
    except Exception:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
        print(f"Collection {collection_name} created successfully")


def delete_collection(client: QdrantClient, collection_name: str):
    try:
        client.delete_collection(collection_name=collection_name)
        print(f"Collection {collection_name} deleted")
    except Exception:
        print(f"Collection {collection_name} did not exist or could not be deleted")


def demo_points():
    city_texts = [
        ("Berlin", "Berlin is the capital city of Germany and a major European hub."),
        ("London", "London is the capital of the United Kingdom and a global financial center."),
        ("Moscow", "Moscow is the capital city of Russia and a major political and cultural center."),
        ("New York", "New York is a large city in the United States known for business and culture."),
        ("Beijing", "Beijing is the capital of China and a major center for government and technology."),
        ("Mumbai", "Mumbai is a major Indian city on the west coast with a large economy and port."),
    ]

    vectors = list(EMBEDDING_MODEL.embed([text for _, text in city_texts]))
    points = []
    for index, ((city, text), vector) in enumerate(zip(city_texts, vectors), start=1):
        points.append(
            PointStruct(
                id=index,
                vector=[float(value) for value in vector],
                payload={"city": city, "text": text},
            )
        )
    return points


def seed_demo_data(client: QdrantClient, collection_name: str):
    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=demo_points(),
    )
    print(operation_info)


def main():
    args = parse_args()
    client = get_client(args.host, args.port)

    if args.action == "reset":
        delete_collection(client, args.collection)
        ensure_collection(client, args.collection, args.vector_size)
        seed_demo_data(client, args.collection)
        return

    ensure_collection(client, args.collection, args.vector_size)

    if args.action == "seed":
        seed_demo_data(client, args.collection)


if __name__ == "__main__":
    main()
