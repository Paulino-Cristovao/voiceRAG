# 🎙️ Mozaitelecomunicação - Assistente de Voz com IA

Sistema de atendimento ao cliente com voz usando RAG (Retrieval-Augmented Generation) com **LangChain**, permitindo conversas naturais sobre serviços da empresa através de voz.

## ✨ Funcionalidades

✅ **Sem Autenticação**: Qualquer usuário pode fazer perguntas imediatamente
✅ **Memória de Conversa**: Lembra os últimos 10 intercâmbios (contexto)
✅ **LangChain RAG**: Sistema aprimorado com melhor precisão
✅ **Streaming Ready**: Respostas aparecem palavra por palavra (rápido)
✅ **Base de Conhecimento**: Respostas apenas da documentação PDF
✅ **Filtro de Profanidade**: Bloqueia linguagem inapropriada
✅ **Interrupção**: Pode parar o AI e fazer nova pergunta
✅ **Voz Bidirecional**: Entrada e saída por voz (Whisper + TTS)
✅ **WebSocket Real-time**: Comunicação instantânea
✅ **Português Moçambicano**: Totalmente em Português de Moçambique

## 📋 Requisitos

- Python 3.10+
- MacOS (ou Linux com ajustes)
- Navegador moderno (Chrome, Firefox, Safari)
- Microfone e alto-falantes
- OpenAI API Key

## 🚀 Instalação Rápida

### 1. Clonar e Configurar

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar API Key

```bash
# Copiar exemplo
cp .env.example .env

# Editar .env e adicionar sua chave
# OPENAI_API_KEY=sk-sua-chave-aqui
```

### 3. Iniciar o Sistema

```bash
# Opção 1: Usar script automático
./start.sh

# Opção 2: Manualmente
python ingest_pdfs.py  # Primeira vez apenas
python app.py
```

### 4. Abrir no Navegador

```
http://localhost:8000
```

## 🎯 Como Usar

### Primeira Vez (Autenticação)

1. **Abrir a interface** - O assistente saúda você
2. **Clicar no círculo azul** - Começa a gravar (vira vermelho)
3. **Dizer seu nome** - Ex: "João Silva", "Maria Santos"
4. **Confirmar** - Sistema encontra e pede confirmação
5. **Autenticado!** - Pronto para fazer perguntas

### Fazer Perguntas

1. **Clicar no círculo** - Grava por 5 segundos
2. **Fazer pergunta** - Ex: "Como pago a minha fatura?"
3. **Ouvir resposta** - Sistema responde com seu nome
4. **Repetir** - Fazer mais perguntas

### Exemplos de Perguntas

- "Como posso pagar a minha fatura?"
- "Qual é o meu plano atual?"
- "Como consultar o saldo de dados?"
- "O que acontece se ultrapassar o limite?"
- "Como posso mudar de plano?"

## 🛡️ Validações de Segurança

O sistema inclui múltiplas camadas de validação:

| Validação | Descrição |
|-----------|-----------|
| **Profanidade** | Rejeita palavras inapropriadas |
| **Gibberish** | Verifica vogais e variedade de caracteres |
| **Comprimento** | Mínimo 2, máximo 50 caracteres |
| **Caracteres** | Apenas letras, espaços, hífens, apóstrofos |
| **Palavras Sistema** | Rejeita "quit", "admin", "test", etc. |
| **Tentativas** | Máximo 3 tentativas |
| **Fuzzy Match** | 60% de similaridade para encontrar cliente |

## 👥 Clientes de Teste

O sistema inclui 3 clientes em `customers/customers.json`:

1. **João Silva** - Plano Premium 5G
2. **Maria Santos** - Plano Básico 4G
3. **Carlos Machel** - Plano Familiar 5G

## 📁 Estrutura do Projeto

```
.
├── app.py                    # FastAPI + WebSocket server
├── static/
│   └── index.html           # Interface web com gradiente
├── ingest_pdfs.py           # Criar índice FAISS
├── customers/
│   └── customers.json       # Base de clientes
├── pdfs/
│   └── sample_support.txt   # Documentação da empresa
├── data/
│   ├── index.faiss         # Índice vetorial
│   └── metadata.pkl        # Metadados dos chunks
├── requirements.txt
├── .env
└── start.sh                # Script de inicialização
```

## 🎨 Interface Visual

### Círculo Gradiente
- **Azul (Idle)**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Vermelho (Gravando)**: `linear-gradient(135deg, #f093fb 0%, #f5576c 100%)`
- **Animação Pulse**: Quando gravando
- **Hover**: Aumenta 5%

### Estados
- `idle` - Pronto para gravar
- `recording` - Gravando áudio
- `processing` - Processando resposta

## 🔧 Arquitetura Técnica

### Backend (FastAPI)

```python
WebSocket /ws
├── Autenticação por voz
│   ├── Whisper STT (português)
│   ├── Validação de nome
│   ├── Fuzzy matching cliente
│   └── Confirmação
└── Loop de conversa
    ├── Whisper STT
    ├── RAG search (FAISS)
    ├── GPT-4o-mini resposta
    └── TTS (voz)
```

### Frontend (Vanilla JS)

```javascript
WebSocket conecta → Recebe greeting
↓
Grava áudio → Envia base64
↓
Recebe transcrição → Mostra
↓
Recebe resposta + áudio → Reproduz
↓
Loop
```

### Modelos OpenAI

| Componente | Modelo |
|------------|--------|
| STT | whisper-1 (pt) |
| Embeddings | text-embedding-3-small |
| Chat | gpt-4o-mini |
| TTS | tts-1 (voz nova) |

## 📝 Adicionar Mais Documentação

```bash
# Adicionar PDFs ou TXTs em pdfs/
cp seu_documento.pdf pdfs/

# Reconstruir índice
python ingest_pdfs.py

# Reiniciar servidor
python app.py
```

## 🔍 Debug

### Erro: "FAISS index not found"
```bash
python ingest_pdfs.py
```

### Erro: "No microphone access"
- Permitir acesso ao microfone no navegador
- Verificar configurações do sistema

### Áudio não toca
- Verificar volume
- Testar em outro navegador

### WebSocket desconecta
- Verificar firewall
- Usar `localhost` ao invés de `127.0.0.1`

## 🌐 Deploy em Produção

### Usando Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
```

### Variáveis de Ambiente

```bash
OPENAI_API_KEY=sk-...
HOST=0.0.0.0
PORT=8000
```

### HTTPS Obrigatório

Para produção, use HTTPS (microfone requer contexto seguro):

```bash
# Com Caddy
caddy reverse-proxy --from https://seu-dominio.com --to localhost:8000

# Ou nginx + certbot
```

## 📊 Melhorias Futuras

- [ ] Histórico de conversas
- [ ] Dashboard de analytics
- [ ] Suporte a múltiplos idiomas
- [ ] Sentiment analysis
- [ ] Transfer para humano
- [ ] Gravação de chamadas
- [ ] Métricas de satisfação

## 🔒 Segurança

- API key apenas no servidor
- Validação de input rigorosa
- Rate limiting (adicionar)
- Sanitização de logs
- CORS configurável

## 📄 Licença

MIT License

## 🆘 Suporte

Para problemas:
1. Verificar logs do servidor
2. Testar com cliente de exemplo
3. Validar API key OpenAI
4. Verificar saldo de créditos

---

**Desenvolvido para Mozaitelecomunicação 🇲🇿**
