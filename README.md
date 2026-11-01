# FastAPI RAG Project

A lightweight Retrieval-Augmented Generation (RAG) application that stores text as embeddings in Qdrant and uses OpenAI to answer questions with the most relevant stored context.

## What this project provides

This project gives you a simple full-stack app for:

- storing text snippets as vector embeddings
- retrieving the most relevant documents from Qdrant
- sending those documents as context to an LLM
- generating grounded answers in a web interface

In short, it turns your text data into a mini document search + Q&A system.

## Architecture

- Frontend: React app served on port 3000
- Backend: FastAPI API served on port 8000
- Vector database: Qdrant on port 6333
- AI: OpenAI embeddings + chat completions

## Features

- Web UI for entering your OpenAI API key
- Generate embeddings from text and store them in Qdrant
- Retrieve similar documents using vector similarity search
- Ask questions and get answers grounded in stored content
- Docker Compose setup for running the full stack locally

## Prerequisites

- Docker and Docker Compose
- An OpenAI API key

## Run locally

```bash
docker compose up --build
```

Then open:

- http://localhost:3000 - web client
- http://localhost:6333/dashboard - Qdrant dashboard

## Project flow

1. Enter your OpenAI API key in the web app.
2. Submit text to generate and store embeddings.
3. Ask a question.
4. The backend embeds the question, searches Qdrant for similar content, and sends the matching documents to GPT.
5. The app returns the generated answer and the relevant source documents.

## API endpoints

The backend exposes:

- `POST /api/generate-and-store-embeddings/`
- `POST /api/retrieve-and-generate-response/`

## Notes

- The default Qdrant collection name is `demo`.
- The app uses OpenAI `text-embedding-3-small` for embeddings and `gpt-4-turbo` for generation.
- The frontend currently prompts for the API key in the UI before running the RAG flow.
