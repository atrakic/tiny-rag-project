import argparse
import os

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

DEFAULT_HOST = os.getenv("QDRANT_HOST", "localhost")
DEFAULT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
DEFAULT_COLLECTION = os.getenv("COLLECTION_NAME", "demo")
DEFAULT_VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "4"))


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
    return QdrantClient(host=host, port=port)


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
    return [
        PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
        PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
        PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
        PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}),
        PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}),
        PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}),
    ]


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
