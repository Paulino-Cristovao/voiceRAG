#!/bin/bash

echo "🚀 Starting Mozaitelecomunicação Voice Assistant..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env from .env.example and add your OpenAI API key"
    exit 1
fi

# Check if FAISS index exists
if [ ! -f data/index.faiss ]; then
    echo "📚 Building knowledge base index..."
    python ingest_pdfs.py
    echo ""
fi

# Start the server
echo "🌐 Starting web server..."
echo "Open http://localhost:8000 in your browser"
echo ""

python app.py
