# Tiny RAG

A very small RAG app that reads sample files from the repo `data/` folder, embeds them locally, stores them in Qdrant, and serves a simple search UI.

## Run

```bash
docker compose up --build
```

Open:
- http://localhost:8000
- http://localhost:6333/dashboard

## Components
- FastAPI backend on port 8000
- Qdrant vector database on port 6333
- Local embeddings with `fastembed`
- User documents from `data/`

## Startup behavior

On container startup, the app reads the files in `/data` and indexes them into Qdrant automatically.

If you want to reindex manually:

```bash
docker compose exec server python scripts/load_sample_data.py
```

## Manual injection from the example folder

You can also seed a small manual Qdrant demo directly from the example directory:

```bash
cd example
python city_demo.py --action seed --collection example_demo
```

The script honors the same `QDRANT_HOST`, `QDRANT_PORT`, and `QDRANT_COLLECTION` environment variables used by the app, so it works reliably from `/example` without assuming a different setup.

## Notes
- No OpenAI API key required
- No extra services beyond FastAPI and Qdrant
