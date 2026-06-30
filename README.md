# Chat With Your Docs

A simple full-stack RAG application that lets users upload documents and chat with them. It uses an in-memory vector store for simplicity, OpenRouter for embeddings, and Groq for chat completions.

## Features
- Upload text, Markdown, and PDF files
- Split documents into chunks and store embeddings in memory
- Ask questions about uploaded documents
- Get grounded answers with source references
- Fallback response when the answer is not present in the uploaded content

## Required environment variables
Create a `.env` file inside the backend folder with:

```env
OPENROUTER_API_KEY=your_openrouter_key
GROQ_API_KEY=your_groq_key
```

## Run locally

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:3000.
