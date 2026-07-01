# Chat With Your Docs

A simple full-stack RAG application that lets users upload documents and chat with them. It uses an in-memory vector store for simplicity, OpenRouter for embeddings, and Groq for chat completions.

## Features
- Upload text, Markdown, and PDF files
- Split documents into chunks and store embeddings in memory
- Ask questions about uploaded documents
- Get grounded answers with source references
- Fallback response when the answer is not present in the uploaded content

## Prerequisites
- Python 3.10+
- Node.js 18+
- Docker and Docker Compose (optional, for containerized setup)

## Required environment variables
Create a `.env` file inside the backend folder with:

```env
OPENAI_API_KEY=
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_API_BASE=https://openrouter.ai
EMBEDDING_MODEL=nvidia/llama-nemotron-embed-vl-1b-v2:free
CHAT_MODEL=gpt-4o-mini
GROQ_API_KEY=your_groq_key
GROQ_PROJECT_ID=
FLASK_ENV=development
```

## Run locally

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --hostname 0.0.0.0 --port 3001
```

Then open http://localhost:3001.

## Run with Docker

### Build and run both services
```bash
docker compose up --build
```

Then open:
- Frontend: http://localhost:3001
- Backend: http://localhost:8000/docs

### Stop the containers
```bash
docker compose down
```

## Project structure
- `backend/` - FastAPI server, document ingestion, and RAG logic
- `frontend/` - Next.js user interface
- `docker-compose.yml` - container orchestration for backend and frontend

## Notes
- This version uses an in-memory vector store, so uploaded documents are stored only for the current runtime.
- If the model or API keys are missing, the app will return a clear message instead of failing silently.
