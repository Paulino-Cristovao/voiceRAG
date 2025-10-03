#!/usr/bin/env python3
"""Ingest PDFs and create FAISS index"""

import os
import pickle

import numpy as np
import fitz  # PyMuPDF
import tiktoken
from openai import OpenAI
import faiss
from dotenv import load_dotenv

load_dotenv()

# Verify API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file. Please set it.")

client = OpenAI(api_key=api_key)

# Configuration - Match app.py settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))  # tokens
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")  # Faster, smaller

print(f"📋 Ingestion Configuration:")
print(f"  - Embedding Model: {EMBEDDING_MODEL}")
print(f"  - Chunk Size: {CHUNK_SIZE} tokens")
print(f"  - Chunk Overlap: {CHUNK_OVERLAP} tokens")
print(f"  - API Key: {api_key[:8]}...{api_key[-4:]}\n")

def count_tokens(text: str) -> int:
    """Count tokens in text"""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """Split text into chunks with overlap"""
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []

    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        decoded_chunk = enc.decode(chunk_tokens)
        chunks.append(decoded_chunk)
        start += chunk_size - overlap

    return chunks

def get_embeddings(texts: list) -> list:
    """Get embeddings from OpenAI"""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]

def build_index(pdf_dir: str = "pdfs", output_dir: str = "data") -> None:
    """Build FAISS index from PDFs and text files"""

    print("📄 Extracting text from documents...")
    all_chunks = []
    metadata = []

    # Process all PDFs and text files
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            print(f"  Processing {filename}...")

            text = extract_text_from_pdf(pdf_path)
            chunks = chunk_text(text)
        elif filename.endswith('.txt'):
            txt_path = os.path.join(pdf_dir, filename)
            print(f"  Processing {filename}...")

            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
            chunks = chunk_text(text)
        else:
            continue

        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            metadata.append({
                "source": filename,
                "chunk_id": i,
                "text": chunk
            })

    print(f"✓ Extracted {len(all_chunks)} chunks")

    # Get embeddings
    print("🔢 Generating embeddings...")
    embeddings = get_embeddings(all_chunks)
    embeddings_array = np.array(embeddings, dtype=np.float32)

    # Create FAISS index
    print("🗂️  Building FAISS index...")
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)

    # Save index and metadata
    os.makedirs(output_dir, exist_ok=True)
    faiss.write_index(index, os.path.join(output_dir, "index.faiss"))

    with open(os.path.join(output_dir, "metadata.pkl"), "wb") as f:
        pickle.dump(metadata, f)

    print(f"✓ Index saved to {output_dir}/")
    print(f"  - Dimension: {dimension}")
    print(f"  - Total vectors: {index.ntotal}")

if __name__ == "__main__":
    build_index()
