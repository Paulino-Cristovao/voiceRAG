# ⚙️ Configuração do Sistema - Voice RAG

## 📋 Modelos e Configurações Atuais

### 🤖 Modelos OpenAI

| Componente | Modelo | Dimensões/Capacidade |
|------------|--------|---------------------|
| **Embeddings** | `text-embedding-3-large` | 3072 dimensões (melhor qualidade) |
| **Chat/LLM** | `gpt-4o-mini` | Conversação e geração de respostas |
| **STT** | `whisper-1` | Transcrição de voz (português) |
| **TTS** | `tts-1` | Síntese de voz |

### 📊 Configurações RAG

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `TOP_K` | 5 | Número de chunks retornados do FAISS |
| `CHUNK_SIZE` | 400 tokens | Tamanho de cada chunk de texto |
| `CHUNK_OVERLAP` | 50 tokens | Sobreposição entre chunks |
| `TEMPERATURE` | 0.3 | Temperatura do LLM (mais determinístico) |
| `MAX_TOKENS` | 400 | Máximo de tokens na resposta |

## 🔧 Arquivo .env

Todas as configurações são lidas do arquivo `.env`:

```bash
# API Key (OBRIGATÓRIO)
OPENAI_API_KEY=sk-proj-...

# Modelos (Opcional - usa defaults se não especificado)
EMBEDDING_MODEL=text-embedding-3-large
CHAT_MODEL=gpt-4o-mini
TTS_MODEL=tts-1
WHISPER_MODEL=whisper-1

# RAG (Opcional)
TOP_K=5
CHUNK_SIZE=400
CHUNK_OVERLAP=50
```

## 🔍 Como Funciona o RAG

### 1. Ingestão (ingest_pdfs.py)

```
PDFs/TXTs → Extração de Texto → Chunking
                                    ↓
                            Embeddings (3072-dim)
                                    ↓
                            FAISS Index (L2)
```

### 2. Consulta (app.py)

```
Pergunta do Usuário
        ↓
Embedding da Pergunta (3072-dim)
        ↓
Busca FAISS (L2 distance)
        ↓
Top 5 Chunks Mais Relevantes
        ↓
Contexto + Informação Cliente → LLM
        ↓
Resposta Personalizada
```

## 📈 Melhorias Implementadas

### ✅ Embedding Model Upgrade

**Antes:** `text-embedding-3-small` (1536 dimensões)
**Agora:** `text-embedding-3-large` (3072 dimensões)

**Benefícios:**
- ✅ Melhor qualidade de embeddings
- ✅ Busca semântica mais precisa
- ✅ Melhor compreensão de português
- ✅ Menos falsos positivos

### ✅ Retrieval Melhorado

**Antes:** Top-3 chunks
**Agora:** Top-5 chunks

**Benefícios:**
- ✅ Mais contexto para o LLM
- ✅ Respostas mais completas
- ✅ Melhor cobertura de informação

### ✅ Prompt Engineering

**Mudanças:**
- ✅ Prompt mais restritivo (USE APENAS BASE DE CONHECIMENTO)
- ✅ Temperatura reduzida (0.7 → 0.3) = mais determinístico
- ✅ Instruções explícitas para citar fontes
- ✅ Fallback claro quando informação não existe

### ✅ Logging e Debug

O sistema agora mostra nos logs:

```
🔍 Query: Como posso pagar a minha fatura?
📚 Retrieved 5 chunks from knowledge base
  [1] sample_support.txt (chunk 1): MOZAITELECOMUNICAÇÃO - GUIA DE APOIO...
  [2] sample_support.txt (chunk 2): Como Pagar a Sua Fatura...
  ...
💬 Response: Paulino, pode pagar a sua fatura de várias formas...
```

## 🎯 Garantias de Qualidade

### 1. Usa APENAS Dados Fornecidos

O sistema foi configurado para:
- ✅ Responder APENAS com informação da base de conhecimento
- ✅ Indicar claramente quando não sabe algo
- ✅ Não inventar ou assumir informações
- ✅ Citar fontes quando relevante

### 2. Lê API Key do .env

```python
# app.py e ingest_pdfs.py
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")
```

**Verificação:**
```bash
# Ver logs ao iniciar
python app.py

# Saída:
📋 Configuration:
  - Embedding Model: text-embedding-3-large
  - Chat Model: gpt-4o-mini
  - Top K Results: 5
  - API Key: sk-proj-...q00A
```

### 3. Contexto Sempre Incluído

Cada resposta inclui:
- ✅ 5 chunks mais relevantes do FAISS
- ✅ Informação do cliente (nome, plano, status)
- ✅ Instruções rígidas de uso apenas da base de conhecimento

## 🧪 Como Testar

### Teste 1: Pergunta na Base de Conhecimento

```
Pergunta: "Como posso pagar a minha fatura?"
Esperado: Resposta com métodos de pagamento do guia
```

### Teste 2: Pergunta Fora da Base

```
Pergunta: "Qual é a capital de França?"
Esperado: "{Nome}, não tenho essa informação na minha base de dados..."
```

### Teste 3: Verificar Logs

```bash
# Terminal do servidor mostra:
🔍 Query: Como posso pagar?
📚 Retrieved 5 chunks from knowledge base
  [1] sample_support.txt (chunk 1): ...
  [2] sample_support.txt (chunk 2): ...
💬 Response: ...
```

## 🔄 Reconstruir Índice

Quando adicionar/modificar PDFs:

```bash
# Apagar índice antigo
rm -rf data/index.faiss data/metadata.pkl

# Reconstruir com novo modelo
python ingest_pdfs.py

# Reiniciar servidor
python app.py
```

## 📊 Comparação de Modelos

### text-embedding-3-small vs text-embedding-3-large

| Métrica | Small | Large |
|---------|-------|-------|
| Dimensões | 1536 | 3072 |
| Qualidade | Boa | Excelente |
| Custo/1M tokens | $0.02 | $0.13 |
| Velocidade | Rápida | Média |
| **Recomendação** | Produção grande escala | **Qualidade máxima** ✅ |

Para este projeto, usamos **large** porque:
- ✅ Melhor compreensão de português
- ✅ Base pequena (8 chunks) = custo baixo
- ✅ Qualidade é prioridade

## 🆘 Troubleshooting

### Respostas Genéricas?

1. Verificar se chunks corretos estão sendo recuperados (ver logs)
2. Aumentar `TOP_K` para 7-10
3. Reduzir `CHUNK_SIZE` para 300 (chunks menores = mais específicos)

### Informação Incorreta?

1. Verificar conteúdo dos PDFs em `pdfs/`
2. Reconstruir índice: `python ingest_pdfs.py`
3. Verificar logs: chunks recuperados correspondem à pergunta?

### Custo Alto?

1. Downgrade para `text-embedding-3-small`
2. Reduzir `TOP_K` para 3
3. Cache de embeddings (implementar)

---

**Última Atualização:** 2025-10-03
**Versão:** 2.0.0 (Upgrade para text-embedding-3-large)
