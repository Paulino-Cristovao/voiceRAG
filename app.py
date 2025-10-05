"""
Improved Voice RAG System with LangChain + ElevenLabs
- Async/await for maximum performance
- ElevenLabs for human-like voice
- Conversation memory (remembers context)
- Streaming responses (faster perceived speed)
- Bilingual support (Portuguese + English)
- Natural conversational tone
- Response caching for speed
"""

import os
import io
import base64
import tempfile
import pickle
import hashlib
from functools import lru_cache
from typing import List, Dict, Tuple, Optional, Union, AsyncGenerator
import asyncio

import numpy as np
import faiss
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI, AsyncOpenAI
from sklearn.metrics.pairwise import cosine_similarity
from elevenlabs.client import AsyncElevenLabs
from elevenlabs import VoiceSettings

# LangChain imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, BaseMessage

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "")
USE_ELEVENLABS = bool(ELEVEN_API_KEY)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# ElevenLabs configuration
ELEVEN_VOICE_ID_EN = os.getenv("ELEVEN_VOICE_ID_EN", "21m00Tcm4TlvDq8ikWAM")  # Rachel
ELEVEN_VOICE_ID_PT = os.getenv("ELEVEN_VOICE_ID_PT", "21m00Tcm4TlvDq8ikWAM")  # Rachel (multilingual)
ELEVEN_MODEL = os.getenv("ELEVEN_MODEL", "eleven_multilingual_v2")
ELEVEN_STABILITY = float(os.getenv("ELEVEN_STABILITY", "0.5"))
ELEVEN_SIMILARITY_BOOST = float(os.getenv("ELEVEN_SIMILARITY_BOOST", "0.75"))
ELEVEN_STYLE = float(os.getenv("ELEVEN_STYLE", "0.0"))
ELEVEN_USE_SPEAKER_BOOST = os.getenv("ELEVEN_USE_SPEAKER_BOOST", "true").lower() == "true"

# OpenAI TTS (fallback)
TTS_MODEL = os.getenv("TTS_MODEL", "tts-1")
TTS_VOICE = os.getenv("TTS_VOICE", "nova")
TTS_SPEED = float(os.getenv("TTS_SPEED", "1.1"))

TOP_K = int(os.getenv("TOP_K", "5"))

# Performance optimization settings
CACHE_SIZE = int(os.getenv("CACHE_SIZE", "200"))
CONTEXT_MAX_CHARS = int(os.getenv("CONTEXT_MAX_CHARS", "2500"))
SEMANTIC_CACHE_THRESHOLD = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.85"))

print("📋 Configuration:")
print(f"  - Embedding Model: {EMBEDDING_MODEL}")
print(f"  - Chat Model: {CHAT_MODEL}")
if USE_ELEVENLABS:
    print(f"  - TTS: ElevenLabs {ELEVEN_MODEL} (Rachel voice)")
    print(f"  - Voice Settings: stability={ELEVEN_STABILITY}, similarity={ELEVEN_SIMILARITY_BOOST}")
else:
    print(f"  - TTS: OpenAI {TTS_MODEL} ({TTS_VOICE} @ {TTS_SPEED}x)")
print(f"  - Top K Results: {TOP_K}")
print(f"  - API Key: {OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:]}")

# Initialize clients
client = OpenAI(api_key=OPENAI_API_KEY)
async_openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

if USE_ELEVENLABS:
    eleven_client = AsyncElevenLabs(api_key=ELEVEN_API_KEY)
    print("✅ ElevenLabs client initialized")
else:
    eleven_client = None
    print("⚠️  ElevenLabs not configured - using OpenAI TTS")


class LangChainVoiceRAG:
    """Enhanced RAG service with LangChain, caching, and bilingual support"""

    def __init__(self):
        # Load FAISS index
        self.index = faiss.read_index("data/index.faiss")

        with open("data/metadata.pkl", "rb") as f:
            self.metadata = pickle.load(f)

        # Enhanced caching: Response + Semantic
        self.response_cache = {}
        self.semantic_cache: Dict[str, Tuple[np.ndarray, List[Dict]]] = {}

        # Initialize LangChain components
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )

        self.llm = ChatOpenAI(
            model=CHAT_MODEL,
            temperature=0.3,  # Slightly higher for more natural responses
            streaming=True,
            openai_api_key=OPENAI_API_KEY
        )

        print("✅ LangChain RAG initialized:")
        print(f"  - FAISS index: {self.index.ntotal} vectors")
        print(f"  - Metadata: {len(self.metadata)} chunks")
        print("  - Knowledge base ready")

    def detect_language(self, text: str) -> str:
        """Strict language detection for English vs Portuguese"""
        text_lower = text.lower()

        # Strong English indicators (words that are ONLY in English)
        strong_english = ['what', 'how', 'when', 'where', 'which', 'does', 'kind', 'service',
                         'student', 'students', 'carpet', 'cost', 'much', 'sure', 'about',
                         'very', 'cheap', 'like', 'have', 'well', 'that', 'this', 'the']

        # Strong Portuguese indicators (words that are ONLY in Portuguese)
        strong_portuguese = ['qual', 'como', 'quando', 'onde', 'onde', 'que', 'qual', 'quais',
                            'estudante', 'estudantes', 'tarifa', 'plano', 'pacote', 'caro',
                            'barato', 'gosto', 'muito', 'tem', 'fale', 'sobre', 'básico',
                            'demorar', 'pagar', 'acontece', 'você', 'meu', 'minha']

        # Count occurrences
        words = text_lower.split()
        english_score = sum(2 if word in strong_english else 0 for word in words)
        portuguese_score = sum(2 if word in strong_portuguese else 0 for word in words)

        # Additional check for common patterns
        if any(pattern in text_lower for pattern in ['do you', 'are you', 'can you', 'i like', 'very cheap']):
            english_score += 5
        if any(pattern in text_lower for pattern in ['você', 'o que', 'qual é', 'fale sobre', 'plano']):
            portuguese_score += 5

        # Default to Portuguese if unclear (since we're in Mozambique)
        if english_score == portuguese_score:
            return 'pt'

        return 'en' if english_score > portuguese_score else 'pt'

    def detect_sentiment(self, text: str) -> str:
        """Detect user sentiment for empathy"""
        negative_words = ['frustrado', 'problema', 'não funciona', 'ruim', 'péssimo', 'horrível',
                         'frustrated', 'problem', 'not working', 'broken', 'issue', 'terrible', 'bad']
        text_lower = text.lower()
        return 'negative' if any(word in text_lower for word in negative_words) else 'neutral'

    @lru_cache(maxsize=CACHE_SIZE)
    def _embed_query_cached(self, query: str):
        """Cached embedding for speed"""
        return self.embeddings.embed_query(query)

    def search_knowledge_base(self, query: str, k: int = TOP_K) -> List[Dict]:
        """Search FAISS with semantic caching"""
        cache_key = hashlib.md5(query.encode()).hexdigest()

        # Exact cache hit
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]

        query_embedding = self._embed_query_cached(query)
        query_vector_array = np.array([query_embedding], dtype='float32')

        # Semantic cache: Check for similar queries
        for cached_key, (cached_emb, cached_results) in self.semantic_cache.items():
            similarity = cosine_similarity([query_embedding], [cached_emb])[0][0]
            if similarity > SEMANTIC_CACHE_THRESHOLD:
                print(f"  ⚡ Semantic cache hit! Similarity: {similarity:.2f}")
                return cached_results

        # FAISS search
        distances, indices = self.index.search(query_vector_array, k)

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

        # Cache both exact and semantic
        self.response_cache[cache_key] = results
        self.semantic_cache[cache_key] = (np.array(query_embedding), results)

        # Limit semantic cache size
        if len(self.semantic_cache) > CACHE_SIZE:
            oldest_key = list(self.semantic_cache.keys())[0]
            del self.semantic_cache[oldest_key]

        return results

    def check_profanity(self, text: str) -> Tuple[bool, Optional[str]]:
        """Check for profanity"""
        profanity_words = [
            "fuck", "shit", "damn", "bitch", "ass", "hell", "bastard",
            "idiot", "stupid", "dumb", "moron", "crap",
            "merda", "caralho", "puta", "foda", "burro", "idiota"
        ]

        text_lower = text.lower()
        for word in profanity_words:
            if word in text_lower:
                lang = self.detect_language(text)
                if lang == 'en':
                    return True, "I'm sorry, I cannot respond to questions with inappropriate language. Please rephrase your question respectfully."
                return True, "Desculpe, não posso responder a perguntas com linguagem inapropriada. Por favor, reformule sua pergunta de forma respeitosa."

        return False, None

    def check_relevance(self, query: str, context_chunks: List[Dict]) -> bool:
        """Check if query is relevant"""
        if not context_chunks:
            return False

        telecom_keywords = {
            # Portuguese
            'fatura', 'pagar', 'pagamento', 'plano', 'dados', 'saldo',
            'apn', '5g', '4g', 'sim', 'chip', 'serviço', 'chamadas', 'minutos',
            'cobertura', 'rede', 'sinal', 'roaming', 'recarga', 'configuração',
            'telefone', 'celular', 'móvel', 'número', 'linha', 'conta', 'suporte',
            'modem', 'router', 'wifi', 'banda', 'velocidade', 'contacto',
            'escritório', 'app', 'aplicativo', 'mpesa', 'emola', 'banco', 'apoio',
            'recomenda', 'estudante', 'universitário', 'jovem', 'família', 'empresarial',
            # English
            'bill', 'pay', 'payment', 'plan', 'internet', 'data', 'balance',
            'network', 'signal', 'call', 'minutes', 'coverage', 'support', 'help',
            'phone', 'mobile', 'account', 'email', 'office', 'price', 'cost'
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

    def create_chain_with_memory(self, conversation_history: List[Dict], language: str = 'pt', sentiment: str = 'neutral'):
        """Create LangChain chain with conversation memory, language, and empathy support"""

        # Empathy injection based on sentiment
        empathy_en = "\n\nEMPATHY: If user seems frustrated, start with: 'I'm sorry to hear that, let's fix this together.'" if sentiment == 'negative' else ""
        empathy_pt = "\n\nEMPATIA: Se o utilizador parece frustrado, comece com: 'Lamento ouvir isso, vamos resolver juntos.'" if sentiment == 'negative' else ""

        # Bilingual system prompts with strict language matching
        if language == 'en':
            system_template = """You are Maria, a warm and friendly customer service agent for Mozaitelecomunicação in Mozambique.

CRITICAL LANGUAGE RULE:
🔴 The user is speaking ENGLISH. You MUST respond ONLY in ENGLISH. Never mix Portuguese!

SPEAK LIKE A REAL HUMAN:
- Talk casually like chatting with a friend over coffee
- Use contractions: "I'm", "you'll", "that's", "it's"
- Add personality: "Oh!", "Well...", "Actually...", "You know what?"
- Vary sentence length - mix short and medium sentences
- Show enthusiasm: "Great choice!", "I'd love to help!"
- Be personal: "I see you're interested in...", "For your needs..."

AVAILABLE INFO:
{context}

STRICT RULES:
1. ONLY use info from documentation above - don't make anything up
2. Missing info? Say: "Hmm, I don't have that detail. Best to email apoio@mozaitelecomunicacao.co.mz or visit us at Av. Julius Nyerere, 2500, Maputo."
3. Keep answers SHORT - max 2-3 sentences
4. For changes/complaints: "You'll need to contact apoio@mozaitelecomunicacao.co.mz for that"
5. Remember context from chat history

NATURAL EXAMPLES:
❌ "The Premium 5G plan costs 1,600 meticais per month."
✅ "Oh, the Premium 5G? That's 1,600 meticais a month - pretty solid deal!"

❌ "I understand. Let me help you with that."
✅ "Got it! So you're looking for student plans, right? I'd suggest..."
""" + empathy_en

        else:  # Portuguese
            system_template = """Você é a Maria, uma agente simpática e calorosa da Mozaitelecomunicação em Moçambique.

REGRA CRÍTICA DE IDIOMA:
🔴 O utilizador está a falar PORTUGUÊS. Você DEVE responder APENAS em PORTUGUÊS. Nunca misture inglês!

FALE COMO UMA PESSOA REAL:
- Converse casualmente como se estivesse a tomar café com um amigo
- Use contrações naturais: "tá", "né", "pra", "tamos"
- Adicione personalidade: "Ah!", "Pois...", "Na verdade...", "Sabes?"
- Varie o comprimento - misture frases curtas e médias
- Mostre entusiasmo: "Boa escolha!", "Adoraria ajudar!"
- Seja pessoal: "Vejo que está interessado em...", "Para o seu caso..."

INFORMAÇÃO DISPONÍVEL:
{context}

REGRAS ESTRITAS:
1. SÓ use informação da documentação acima - não invente nada
2. Info em falta? Diga: "Hmm, não tenho esse detalhe. Melhor enviar email para apoio@mozaitelecomunicacao.co.mz ou visitar-nos na Av. Julius Nyerere, 2500, Maputo."
3. Respostas CURTAS - máximo 2-3 frases
4. Para mudanças/reclamações: "Para isso precisa contactar apoio@mozaitelecomunicacao.co.mz"
5. Lembre-se do contexto da conversa

EXEMPLOS NATURAIS:
❌ "O plano Premium 5G custa 1.600 meticais por mês."
✅ "Ah, o Premium 5G? São 1.600 meticais por mês - ótimo negócio!"

❌ "Entendo. Deixe-me ajudá-lo com isso."
✅ "Entendi! Então procura planos para estudantes, certo? Sugiro..."
""" + empathy_pt

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])

        # Convert conversation history to LangChain format
        history_messages: List[BaseMessage] = []
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
        )

        return chain

    def summarize_context(self, context_chunks: List[Dict], language: str = 'pt') -> str:
        """Summarize and merge context if too large"""
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(f"[Doc {i}]\n{chunk['text']}")

        full_context = "\n\n".join(context_parts)

        # If context is too large, summarize with tighter threshold
        if len(full_context) > CONTEXT_MAX_CHARS:
            prompt = "Summarize and merge these docs concisely, keeping all key facts:" if language == 'en' else "Resume e combine estes documentos de forma concisa, mantendo todos os factos-chave:"

            summary_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": full_context}
                ],
                temperature=0.1,
                max_tokens=800
            )
            return summary_response.choices[0].message.content

        return full_context

    def generate_response(self, query: str, context_chunks: List[Dict],
                         conversation_history: List[Dict]) -> str:
        """Generate response with caching, empathy, and bilingual support"""

        # Detect language and sentiment
        language = self.detect_language(query)
        sentiment = self.detect_sentiment(query)

        # Check profanity
        has_profanity, profanity_msg = self.check_profanity(query)
        if has_profanity:
            return profanity_msg

        # Check relevance
        is_relevant = self.check_relevance(query, context_chunks)

        # Build context (with summarization if needed)
        context = self.summarize_context(context_chunks, language)

        # Log
        print(f"\n🔍 Query: {query}")
        print(f"🌐 Language: {language.upper()}")
        print(f"😊 Sentiment: {sentiment.upper()}")
        print(f"📚 Retrieved {len(context_chunks)} chunks")
        print(f"📏 Context size: {len(context)} chars")
        print(f"🎯 Relevance: {'RELEVANT' if is_relevant else 'NOT RELEVANT'}")
        print(f"💬 History: {len(conversation_history)} messages")

        # Create and invoke chain with empathy
        chain = self.create_chain_with_memory(conversation_history, language, sentiment)

        response_stream = chain.stream({
            "context": context,
            "question": query
        })

        # Collect full response
        full_response = ""
        for chunk in response_stream:
            if hasattr(chunk, 'content'):
                content = chunk.content
                if isinstance(content, str):
                    full_response += content

        print(f"✅ Response: {full_response[:100]}...")
        return full_response

    async def transcribe_audio(self, audio_bytes):
        """Transcribe audio using Whisper (async)"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        try:
            with open(tmp_path, "rb") as audio_file:
                transcript = await async_openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcript.text
        finally:
            os.unlink(tmp_path)

    async def text_to_speech_elevenlabs(self, text: str, language: str = 'en') -> bytes:
        """Convert text to speech using ElevenLabs (ultra-realistic voice)"""
        voice_id = ELEVEN_VOICE_ID_EN if language == 'en' else ELEVEN_VOICE_ID_PT

        voice_settings = VoiceSettings(
            stability=ELEVEN_STABILITY,
            similarity_boost=ELEVEN_SIMILARITY_BOOST,
            style=ELEVEN_STYLE,
            use_speaker_boost=ELEVEN_USE_SPEAKER_BOOST
        )

        # Generate audio using async streaming
        audio_chunks = []
        async for chunk in eleven_client.text_to_speech.stream(
            text=text,
            voice_id=voice_id,
            model_id=ELEVEN_MODEL,
            voice_settings=voice_settings
        ):
            if chunk:
                audio_chunks.append(chunk)

        return b''.join(audio_chunks)

    async def text_to_speech_openai(self, text: str) -> bytes:
        """Convert text to speech using OpenAI (fallback)"""
        response = await async_openai_client.audio.speech.create(
            model=TTS_MODEL,
            voice=TTS_VOICE,
            input=text,
            speed=TTS_SPEED
        )

        audio_data = io.BytesIO()
        async for chunk in response.iter_bytes(chunk_size=4096):
            audio_data.write(chunk)

        return audio_data.getvalue()

    async def text_to_speech(self, text: str, language: str = 'en') -> bytes:
        """Convert text to speech - uses ElevenLabs if available, OpenAI as fallback"""
        if USE_ELEVENLABS:
            return await self.text_to_speech_elevenlabs(text, language)
        else:
            return await self.text_to_speech_openai(text)


# Initialize service
rag_service = LangChainVoiceRAG()


@app.get("/")
async def read_root():
    """Serve main application page"""
    return FileResponse("static/index.html")


@app.get("/diagnostic")
async def diagnostic():
    """Serve diagnostic page for browser/microphone testing"""
    return FileResponse("static/diagnostic.html")


@app.get("/favicon.svg")
async def favicon():
    """Serve favicon"""
    return FileResponse("static/favicon.svg")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket with conversation memory"""
    await websocket.accept()

    conversation_history = []

    try:
        # Send bilingual greeting
        greeting = "Olá! Bem-vindo ao Suporte VoiceAI. Como posso ajudá-lo hoje? / Hello! Welcome to VoiceAI Support. How can I help you today?"
        audio_data = await rag_service.text_to_speech(greeting, language='pt')

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
                interrupt_msg = "Entendo. Por favor, faça a sua pergunta novamente. / I understand. Please ask your question again."
                audio_data = await rag_service.text_to_speech(interrupt_msg, language='pt')
                await websocket.send_json({
                    "type": "message",
                    "text": interrupt_msg,
                    "audio": base64.b64encode(audio_data).decode()
                })
                continue

            # Handle audio question
            elif data["type"] == "audio":
                audio_bytes = base64.b64decode(data["audio"])

                # Transcribe (async now)
                query = await rag_service.transcribe_audio(audio_bytes)

                await websocket.send_json({
                    "type": "transcription",
                    "text": query
                })

                if not query.strip():
                    msg = "Não ouvi nada. Por favor repita a sua pergunta. / I didn't hear anything. Please repeat your question."
                    audio_data = await rag_service.text_to_speech(msg, language='pt')
                    await websocket.send_json({
                        "type": "message",
                        "text": msg,
                        "audio": base64.b64encode(audio_data).decode()
                    })
                    continue

                # Detect language for proper voice
                detected_lang = rag_service.detect_language(query)

                # Add to history BEFORE generating response
                conversation_history.append({"role": "user", "content": query})

                # Search knowledge base (with caching)
                context_chunks = rag_service.search_knowledge_base(query)

                # Generate response WITH conversation history
                response = rag_service.generate_response(
                    query,
                    context_chunks,
                    conversation_history
                )

                # Add response to history
                conversation_history.append({"role": "assistant", "content": response})

                # Convert to speech with proper language voice (async + parallel)
                audio_data = await rag_service.text_to_speech(response, language=detected_lang)

                await websocket.send_json({
                    "type": "response",
                    "text": response,
                    "audio": base64.b64encode(audio_data).decode()
                })

            # Handle end session
            elif data["type"] == "end":
                goodbye_msg = "Obrigado por usar o Suporte VoiceAI. Tenha um bom dia! / Thank you for using VoiceAI Support. Have a great day!"
                audio_data = await rag_service.text_to_speech(goodbye_msg, language='pt')
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
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
