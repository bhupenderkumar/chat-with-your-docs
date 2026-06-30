import os
import math
import re
from typing import List, Dict, Any
from io import BytesIO

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

app = FastAPI(title="Chat With Your Docs API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.documents: List[Dict[str, Any]] = []


class ChatRequest(BaseModel):
    question: str


def split_text(text: str, max_chars: int = 1000) -> List[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []

    chunks: List[str] = []
    while len(cleaned) > max_chars:
        split_at = cleaned.rfind(".", 0, max_chars)
        if split_at == -1 or split_at < max_chars // 2:
            split_at = max_chars
        chunk = cleaned[:split_at].strip()
        if chunk:
            chunks.append(chunk)
        cleaned = cleaned[split_at:].strip()
    if cleaned:
        chunks.append(cleaned)
    return chunks


def embed_text(text: str) -> List[float]:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    response = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Chat With Your Docs",
        },
        json={
            "model": "openai/text-embedding-3-small",
            "input": text,
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["data"][0]["embedding"]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


async def extract_text_from_upload(file: UploadFile) -> str:
    content = await file.read()
    if file.filename and file.filename.lower().endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    return content.decode("utf-8", errors="ignore")


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    if not files:
        raise ValueError("No files uploaded")

    uploaded_files: List[Dict[str, Any]] = []

    for file in files:
        text = await extract_text_from_upload(file)
        chunks = split_text(text)
        if not chunks:
            continue

        for index, chunk in enumerate(chunks):
            embedding = embed_text(chunk)
            app.state.documents.append(
                {
                    "filename": file.filename or "unknown",
                    "chunk_index": index,
                    "content": chunk,
                    "embedding": embedding,
                }
            )

        uploaded_files.append({"filename": file.filename, "chunks": len(chunks)})

    return {"message": "Documents indexed successfully", "files": uploaded_files}


@app.post("/api/chat")
def chat(request: ChatRequest) -> Dict[str, Any]:
    if not app.state.documents:
        return {
            "answer": "I do not have any uploaded documents to answer from yet. Please upload a document first.",
            "sources": [],
        }

    try:
        question_embedding = embed_text(request.question)
    except Exception as exc:
        return {"answer": f"Embedding service is unavailable: {exc}", "sources": []}

    scored_chunks = []
    for item in app.state.documents:
        score = cosine_similarity(item["embedding"], question_embedding)
        scored_chunks.append((score, item))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    top_matches = [item for score, item in scored_chunks[:3] if score > 0.1]

    if not top_matches:
        return {
            "answer": "I do not have enough relevant information in the uploaded documents to answer that accurately.",
            "sources": [],
        }

    context = "\n\n".join(
        f"Source: {item['filename']}\n{item['content']}"
        for item in top_matches
    )

    if not GROQ_API_KEY:
        return {
            "answer": "I found relevant context, but the Groq API key has not been configured.",
            "sources": [{"filename": item["filename"]} for item in top_matches],
        }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You answer only from the provided context. "
                            "If the answer is not in the context, say exactly: "
                            "I do not have enough relevant information in the uploaded documents to answer that accurately."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Question: {request.question}\n\nContext:\n{context}",
                    },
                ],
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        answer = payload["choices"][0]["message"]["content"]
    except Exception as exc:
        answer = f"I could not generate a reply right now: {exc}"

    return {
        "answer": answer,
        "sources": [{"filename": item["filename"], "chunk": item["chunk_index"]} for item in top_matches],
    }
