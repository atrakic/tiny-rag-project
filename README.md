# Tiny RAG

A small RAG app that reads files from the repo `data/` folder, embeds them locally, stores them in Qdrant, and exposes them through a simple search API.

## Run

```bash
docker compose up --build
```

Open:
- http://localhost:3000 for the React client UI
- http://localhost:8000/docs for the FastAPI API docs
- http://localhost:6333/dashboard for Qdrant

## Components
- React client on port 3000
- FastAPI backend on port 8000
- Qdrant vector database on port 6333
- Local embeddings with `fastembed`
- User documents from `data/`

## Startup behavior

On container startup, the server reads the files in `/data` and indexes them into Qdrant automatically.

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
- UI is served by the React app; backend is API-only
- The legacy server-side template is not used in this split architecture
