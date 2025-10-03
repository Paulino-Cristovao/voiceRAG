"""
Improved Voice RAG System with LangChain
- Conversation memory (remembers context)
- Streaming responses (faster perceived speed)
- Better retrieval with full context
- Only uses OpenAI API
"""

import os
import io
import base64
import tempfile
import numpy as np
import faiss
import pickle
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from typing import List, Dict
import json

# LangChain imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
TOP_K = int(os.getenv("TOP_K", 5))

print(f"📋 Configuration:")
print(f"  - Embedding Model: {EMBEDDING_MODEL}")
print(f"  - Chat Model: {CHAT_MODEL}")
print(f"  - Top K Results: {TOP_K}")
print(f"  - API Key: {OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:]}")

# Initialize clients
client = OpenAI(api_key=OPENAI_API_KEY)


class LangChainVoiceRAG:
    """Enhanced RAG service with LangChain for conversation memory"""

    def __init__(self):
        # Load FAISS index
        self.index = faiss.read_index("data/index.faiss")

        with open("data/metadata.pkl", "rb") as f:
            self.metadata = pickle.load(f)

        # Initialize LangChain components
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )

        self.llm = ChatOpenAI(
            model=CHAT_MODEL,
            temperature=0.2,
            streaming=True,  # Enable streaming
            openai_api_key=OPENAI_API_KEY
        )

        print(f"✅ LangChain RAG initialized:")
        print(f"  - FAISS index: {self.index.ntotal} vectors")
        print(f"  - Metadata: {len(self.metadata)} chunks")
        print(f"  - Knowledge base ready")

    def search_knowledge_base(self, query: str, k: int = TOP_K) -> List[Dict]:
        """Search FAISS with query"""
        query_embedding = self.embeddings.embed_query(query)
        query_vector = np.array([query_embedding], dtype='float32')

        distances, indices = self.index.search(query_vector, k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                chunk_data = self.metadata[idx]
                results.append({
                    "text": chunk_data["text"],
                    "source": chunk_data["source"],
                    "chunk_id": chunk_data["chunk_id"],
                    "distance": float(dist)
                })

        return results

    def check_profanity(self, text: str):
        """Check for profanity"""
        profanity_words = [
            "fuck", "shit", "damn", "bitch", "ass", "hell", "bastard",
            "idiot", "stupid", "dumb", "moron", "crap",
            "merda", "caralho", "puta", "foda", "burro", "idiota"
        ]

        text_lower = text.lower()
        for word in profanity_words:
            if word in text_lower:
                return True, "Desculpe, não posso responder a perguntas com linguagem inapropriada. Por favor, reformule sua pergunta de forma respeitosa."

        return False, None

    def check_relevance(self, query: str, context_chunks: List[Dict]) -> bool:
        """Check if query is relevant"""
        if not context_chunks:
            return False

        telecom_keywords = {
            'fatura', 'pagar', 'pagamento', 'plano', 'internet', 'dados', 'saldo',
            'apn', '5g', '4g', 'sim', 'chip', 'serviço', 'chamadas', 'minutos',
            'cobertura', 'rede', 'sinal', 'roaming', 'recarga', 'configuração',
            'telefone', 'celular', 'móvel', 'número', 'linha', 'conta', 'suporte',
            'modem', 'router', 'wifi', 'banda', 'velocidade', 'contacto', 'email',
            'escritório', 'app', 'aplicativo', 'mpesa', 'emola', 'banco', 'apoio',
            'recomenda', 'estudante', 'universitário', 'jovem', 'família', 'empresarial'
        }

        query_lower = query.lower()

        # Check for telecom keywords
        if any(keyword in query_lower for keyword in telecom_keywords):
            return True

        # Check overlap with context
        query_words = set(query_lower.split())
        context_text = " ".join([chunk["text"].lower() for chunk in context_chunks])
        context_words = set(context_text.split())

        overlap = len(query_words.intersection(context_words))
        if overlap < max(3, len(query_words) * 0.2):
            return False

        return True

    def create_chain_with_memory(self, conversation_history: List[Dict]):
        """Create LangChain chain with conversation memory"""

        # System prompt
        system_template = """Você é um assistente de atendimento ao cliente da Mozaitelecomunicação.

DOCUMENTAÇÃO DISPONÍVEL:
{context}

REGRAS IMPORTANTES:

1. RESPONDA APENAS com informações da DOCUMENTAÇÃO acima
2. Se a informação NÃO estiver na documentação, diga:
   "Desculpe, não tenho essa informação específica. Por favor, contacte apoio@mozaitelecomunicacao.co.mz ou visite nosso escritório na Av. Julius Nyerere, Nº 2500, Maputo."

3. NUNCA invente informações
4. USE o histórico da conversa para entender contexto e referências como "esse", "qual", "e"
5. Se a pergunta requer ação administrativa (mudança, cancelamento, reclamação), redirecione para apoio@mozaitelecomunicacao.co.mz

6. Seja profissional, prestativo e conciso (2-4 frases)
7. Responda em Português de Moçambique

IMPORTANTE:
- Se o usuário perguntar "E qual você recomenda?" ou "Tem um serviço específico?", use o HISTÓRICO para entender o contexto
- Frases como "esse plano", "essa opção" referem-se ao tópico anterior no histórico
- Para recomendações, sugira o plano mais adequado baseado na documentação disponível"""

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])

        # Convert conversation history to LangChain format
        history_messages = []
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            if msg["role"] == "user":
                history_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                history_messages.append(AIMessage(content=msg["content"]))

        # Create chain
        chain = (
            {
                "context": lambda x: x["context"],
                "question": lambda x: x["question"],
                "history": lambda x: history_messages
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return chain

    async def generate_response_streaming(self, query: str, context_chunks: List[Dict],
                                         conversation_history: List[Dict]):
        """Generate response with streaming (yields tokens as they come)"""

        # Check profanity
        has_profanity, profanity_msg = self.check_profanity(query)
        if has_profanity:
            yield profanity_msg
            return

        # Check relevance
        is_relevant = self.check_relevance(query, context_chunks)

        # Build context
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            # Include FULL chunk text, not truncated
            context_parts.append(f"[Documento {i}]\n{chunk['text']}")

        context = "\n\n".join(context_parts)

        # Log
        print(f"\n🔍 Query: {query}")
        print(f"📚 Retrieved {len(context_chunks)} chunks")
        print(f"🎯 Relevance: {'RELEVANT' if is_relevant else 'NOT RELEVANT'}")
        print(f"💬 Conversation history: {len(conversation_history)} messages")

        # Create chain with memory
        chain = self.create_chain_with_memory(conversation_history)

        # Stream response
        full_response = ""
        try:
            async for chunk in chain.astream({
                "context": context,
                "question": query
            }):
                full_response += chunk
                yield chunk
        except Exception as e:
            print(f"Error streaming: {e}")
            yield "Desculpe, ocorreu um erro. Por favor, tente novamente."

        print(f"✅ Response complete: {len(full_response)} chars")

    def generate_response(self, query: str, context_chunks: List[Dict],
                         conversation_history: List[Dict]) -> str:
        """Non-streaming version for compatibility"""

        # Check profanity
        has_profanity, profanity_msg = self.check_profanity(query)
        if has_profanity:
            return profanity_msg

        # Check relevance
        is_relevant = self.check_relevance(query, context_chunks)

        # Build context with FULL text
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(f"[Documento {i}]\n{chunk['text']}")

        context = "\n\n".join(context_parts)

        # Log
        print(f"\n🔍 Query: {query}")
        print(f"📚 Retrieved {len(context_chunks)} chunks")
        print(f"🎯 Relevance: {'RELEVANT' if is_relevant else 'NOT RELEVANT'}")
        print(f"💬 History: {len(conversation_history)} messages")

        # Create and invoke chain
        chain = self.create_chain_with_memory(conversation_history)

        response = chain.invoke({
            "context": context,
            "question": query
        })

        print(f"✅ Response: {response[:100]}...")
        return response

    def transcribe_audio(self, audio_bytes):
        """Transcribe audio using Whisper"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        try:
            with open(tmp_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="pt"
                )
            return transcript.text
        finally:
            os.unlink(tmp_path)

    def text_to_speech(self, text: str):
        """Convert text to speech"""
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )

        audio_data = io.BytesIO()
        for chunk in response.iter_bytes():
            audio_data.write(chunk)

        return audio_data.getvalue()


# Initialize service
rag_service = LangChainVoiceRAG()


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")


@app.get("/diagnostic")
async def diagnostic():
    return FileResponse("static/diagnostic.html")


@app.get("/favicon.svg")
async def favicon():
    return FileResponse("static/favicon.svg")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket with conversation memory"""
    await websocket.accept()

    conversation_history = []

    try:
        # Send greeting
        greeting = "Olá! Bem-vindo à Mozaitelecomunicação. Como posso ajudá-lo hoje?"
        audio_data = rag_service.text_to_speech(greeting)

        await websocket.send_json({
            "type": "message",
            "text": greeting,
            "audio": base64.b64encode(audio_data).decode()
        })

        # Main conversation loop
        while True:
            data = await websocket.receive_json()

            # Handle interrupt
            if data["type"] == "interrupt":
                interrupt_msg = "Entendo. Por favor, faça a sua pergunta novamente."
                audio_data = rag_service.text_to_speech(interrupt_msg)
                await websocket.send_json({
                    "type": "message",
                    "text": interrupt_msg,
                    "audio": base64.b64encode(audio_data).decode()
                })
                continue

            # Handle audio question
            elif data["type"] == "audio":
                audio_bytes = base64.b64decode(data["audio"])

                # Transcribe
                query = rag_service.transcribe_audio(audio_bytes)

                await websocket.send_json({
                    "type": "transcription",
                    "text": query
                })

                if not query.strip():
                    msg = "Não ouvi nada. Por favor repita a sua pergunta."
                    audio_data = rag_service.text_to_speech(msg)
                    await websocket.send_json({
                        "type": "message",
                        "text": msg,
                        "audio": base64.b64encode(audio_data).decode()
                    })
                    continue

                # Add to history BEFORE generating response
                conversation_history.append({"role": "user", "content": query})

                # Search knowledge base
                context_chunks = rag_service.search_knowledge_base(query)

                # Generate response WITH conversation history
                response = rag_service.generate_response(
                    query,
                    context_chunks,
                    conversation_history
                )

                # Add response to history
                conversation_history.append({"role": "assistant", "content": response})

                # Convert to speech
                audio_data = rag_service.text_to_speech(response)

                await websocket.send_json({
                    "type": "response",
                    "text": response,
                    "audio": base64.b64encode(audio_data).decode()
                })

            # Handle end session
            elif data["type"] == "end":
                goodbye_msg = "Obrigado por contactar a Mozaitelecomunicação. Tenha um bom dia!"
                audio_data = rag_service.text_to_speech(goodbye_msg)
                await websocket.send_json({
                    "type": "goodbye",
                    "text": goodbye_msg,
                    "audio": base64.b64encode(audio_data).decode()
                })
                break

    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            if websocket.client_state.name == "CONNECTED":
                await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
