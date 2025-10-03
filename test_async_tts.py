"""
Test async TTS with ElevenLabs integration
"""
import asyncio
import time
from app import rag_service

async def test_tts_speed():
    """Test TTS response speed with both languages"""

    # Test 1: Portuguese
    print("🇵🇹 Testing Portuguese TTS...")
    text_pt = "Olá! O plano Premium 5G custa 1.500 meticais por mês e inclui 50 GB de dados."

    start = time.time()
    audio_pt = await rag_service.text_to_speech(text_pt, language='pt')
    pt_time = time.time() - start

    print(f"  ✓ Generated {len(audio_pt)} bytes in {pt_time:.2f}s")

    # Test 2: English
    print("\n🇬🇧 Testing English TTS...")
    text_en = "Hello! The Premium 5G plan costs 1,500 meticais per month and includes 50 GB of data."

    start = time.time()
    audio_en = await rag_service.text_to_speech(text_en, language='en')
    en_time = time.time() - start

    print(f"  ✓ Generated {len(audio_en)} bytes in {en_time:.2f}s")

    # Test 3: Parallel generation
    print("\n⚡ Testing parallel TTS generation...")
    start = time.time()

    results = await asyncio.gather(
        rag_service.text_to_speech(text_pt, language='pt'),
        rag_service.text_to_speech(text_en, language='en')
    )

    parallel_time = time.time() - start

    print(f"  ✓ Generated both in {parallel_time:.2f}s (vs {pt_time + en_time:.2f}s sequential)")
    print(f"  🚀 Speedup: {((pt_time + en_time) / parallel_time):.2f}x faster")

    # Test 4: Full RAG pipeline
    print("\n🧠 Testing full RAG pipeline with TTS...")
    query = "What are the student plans?"

    start = time.time()

    # Detect language
    lang = rag_service.detect_language(query)
    print(f"  📝 Query: {query}")
    print(f"  🌐 Language: {lang}")

    # Search
    context = rag_service.search_knowledge_base(query)
    print(f"  📚 Found {len(context)} chunks")

    # Generate response
    response = rag_service.generate_response(query, context, [])
    print(f"  💬 Response: {response[:100]}...")

    # Convert to speech
    audio = await rag_service.text_to_speech(response, language=lang)

    total_time = time.time() - start

    print(f"  ✓ Full pipeline: {total_time:.2f}s")
    print(f"  🎤 Audio size: {len(audio)} bytes")

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_tts_speed())
