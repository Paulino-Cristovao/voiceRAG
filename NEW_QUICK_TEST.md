# ⚡ Quick Test Guide - Updated System (No Authentication)

**Date:** 2025-10-03
**System:** Voice RAG without Authentication

---

## 🎯 What Changed?

**Old System:**
- Required name authentication
- Customer-specific responses

**New System:**
- **No authentication needed** ✅
- Anyone can ask questions immediately
- Strict knowledge-base grounding
- Profanity filtering
- Interrupt functionality

---

## 🚀 Quick Start (30 seconds)

```bash
# 1. Start server
python app.py

# 2. Open browser
http://localhost:8000

# 3. Click microphone (allow permission)

# 4. System will greet you automatically!
```

---

## 🧪 Test Script (2 minutes)

### Test 1: Basic Question (30s)
```
🎤 You: "Como posso pagar a minha fatura?"

🤖 System: "De acordo com nossa documentação, você pode pagar através de:
   - Online: www.mozaitelecomunicacao.co.mz
   - App Mozaitel via M-Pesa
   - Escritório físico: Av. Julius Nyerere, Maputo
   - USSD: *123#"
```

✅ **Check:**
- [ ] Response mentions payment methods?
- [ ] Information from PDF guide?
- [ ] No authentication required?

---

### Test 2: Technical Question (20s)
```
🎤 You: "Qual é o APN?"

🤖 System: "O APN da Mozaitelecomunicação é apn.mozaitel.mz"
```

✅ **Check:**
- [ ] Correct APN provided?
- [ ] Answer is concise?

---

### Test 3: Out of Scope Question (20s)
```
🎤 You: "Qual é o tempo hoje?"

🤖 System: "Desculpe, só posso ajudar com questões relacionadas
aos serviços da Mozaitelecomunicação. Para outras questões,
por favor contacte apoio@mozaitelecomunicacao.co.mz."
```

✅ **Check:**
- [ ] Rejected politely?
- [ ] Provided email for support?
- [ ] Did not answer the question?

---

### Test 4: Profanity (20s)
```
🎤 You: "Merda de serviço"

🤖 System: "Desculpe, não posso responder a perguntas com
linguagem inapropriada. Por favor, reformule sua pergunta
de forma respeitosa."
```

✅ **Check:**
- [ ] Detected profanity?
- [ ] Asked for rephrasing?
- [ ] Did not provide service info?

---

### Test 5: Interrupt Feature (30s)
```
1. Ask a question: "Como posso pagar a minha fatura?"
2. While AI is speaking, click "🛑 Interromper"
3. Audio should stop immediately
4. Ask new question: "Qual é o APN?"
```

✅ **Check:**
- [ ] Interrupt button appeared?
- [ ] Audio stopped when clicked?
- [ ] Can ask new question after?

---

### Test 6: Administrative Request (20s)
```
🎤 You: "Quero cancelar minha conta"

🤖 System: "Para cancelamento de serviço, por favor entre
em contato com apoio@mozaitelecomunicacao.co.mz ou visite
nosso escritório."
```

✅ **Check:**
- [ ] Redirected to email?
- [ ] Did not process cancellation?

---

## 📊 Results

**6/6 tests passed?** 🎉 System working perfectly!

**4-5/6 passed?** ⚠️ Good, check failed tests

**<4/6 passed?** ❌ Review logs at `SYSTEM_IMPROVEMENTS.md`

---

## 🎤 Additional Test Questions

### Valid Questions (Should Answer)
- "Quanto custa o plano Premium 5G?"
- "Onde fica o escritório?"
- "Como consulto meu saldo de dados?"
- "Qual é o email de apoio?"
- "Posso pagar com M-Pesa?"

### Out of Scope (Should Redirect)
- "Qual é a previsão do tempo?"
- "Quem ganhou o jogo ontem?"
- "Como faço matapa?" (recipe)
- "Quais são as notícias hoje?"

### Profanity (Should Reject)
- "Este serviço é uma merda"
- "Vocês são uns idiotas"
- Any phrase with curse words

### Administrative (Should Redirect to Email)
- "Quero mudar meu plano"
- "Quero fazer uma reclamação"
- "Como peço reembolso?"
- "Preciso cancelar o serviço"

---

## 🔧 Troubleshooting

### If microphone doesn't work:
1. Check browser permissions (click 🔒 in address bar)
2. Use `http://localhost:8000` (not IP address)
3. Try different browser (Chrome, Firefox, Safari)
4. Visit `/diagnostic` page: http://localhost:8000/diagnostic

### If server doesn't start:
```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill -9

# Restart server
python app.py
```

### If responses are wrong:
1. Check `pdfs/sample_support.txt` has correct info
2. Rebuild index: `python ingest_pdfs.py`
3. Restart server: `python app.py`

---

## 🆕 New Features

### ✅ No Authentication
- Old: Had to say your name first
- New: Ask questions immediately

### ✅ Interrupt Button
- Appears while AI is speaking
- Click to stop and ask new question

### ✅ Profanity Filter
- Blocks inappropriate language
- Asks user to rephrase politely

### ✅ Strict Knowledge Grounding
- Only answers from PDF documentation
- Redirects if info not in knowledge base

### ✅ Email Fallback
- All out-of-scope → `apoio@mozaitelecomunicacao.co.mz`
- Administrative tasks → Email support

---

## 📝 What to Report if Something Fails

1. **Exact question** you asked
2. **Response received**
3. **Expected response**
4. **Browser console** errors (F12 → Console tab)
5. **Screenshot** if possible

Send to development team or check `SYSTEM_IMPROVEMENTS.md` for details.

---

## ✅ Success Criteria

Your system is working if:

- ✅ No authentication required
- ✅ Answers questions from PDF correctly
- ✅ Rejects profanity politely
- ✅ Redirects out-of-scope to email
- ✅ Interrupt button works
- ✅ Professional Portuguese responses

---

**Time:** ~2 minutes for full test
**Difficulty:** Easy
**Prerequisites:** Microphone permission

**Ready to test? Start with Test 1! 🚀**
