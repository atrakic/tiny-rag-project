# Tiny Local RAG

A lightweight local RAG app for chatting with your own documents. Place files in the `data/` directory, index them locally with FastEmbed, store the vectors in Qdrant, and ask questions about the content through a simple chat interface.


## What this app does

- Reads all supported files from `data/`
- Embeds document text locally
- Stores vectors in Qdrant
- Answers questions about your documents through a chat-style UI
- Stays generic and works with your own data, not a fixed demo dataset

## Supported data types

The ingestion script handles common text-based and document files, including:

- `.txt`
- `.md`
- `.csv`
- `.json`
- `.log`
- `.pdf`

## Run the app

### Prerequisite

Add your files to the `data/` directory before starting the app.

### Start the app

```bash
docker compose up --build
```

Then open:

- http://localhost:3000 for the React client
- http://localhost:8000/docs read API docs
- http://localhost:6333/dashboard for the Qdrant dashboard


## Architecture

- React frontend on port 3000
- FastAPI backend on port 8000
- Qdrant vector database on port 6333
- Local embeddings using `fastembed`
- User content mounted from `./data` into the server container

## Reindex manually

If you change files in `data/` and want to refresh the index:

```bash
docker compose exec server python scripts/load_user_data.py
```

## Example questions

Try asking things like:

- "What are the main topics in this data?"
- "Summarize contents in these documents."

## Notes

- No OpenAI or external API key is required
- The app is intentionally generic and works for user-owned files, not a fixed demo dataset
- The app only indexes the files in `data/`; it does not rely on sample/default content
