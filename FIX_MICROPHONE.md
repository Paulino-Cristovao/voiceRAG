# 🎤 SOLUÇÃO RÁPIDA - Erro de Microfone

## ⚡ Solução em 30 Segundos

### 1️⃣ Permitir Acesso ao Microfone

Quando abrir `http://localhost:8000`, o navegador vai perguntar:

```
┌─────────────────────────────────────────┐
│ localhost quer usar seu microfone       │
│                                         │
│  [Bloquear]  [Permitir]                │
└─────────────────────────────────────────┘
```

**👉 CLIQUE EM "PERMITIR"**

---

### 2️⃣ Se Já Bloqueou (aparece ícone 🚫)

#### Chrome/Edge:
```
1. Clique no 🔒 (cadeado) antes de "localhost"
2. Veja "Microfone" → Está em "Bloquear"?
3. Mude para "Permitir"
4. Recarregue página (F5)
```

#### Safari:
```
1. Safari → Preferências → Sites
2. Microfone → localhost
3. Mudar para "Permitir"
4. Recarregue página
```

#### Firefox:
```
1. Clique no 🔒 na barra de endereço
2. Seta (>) ao lado de "Conexão segura"
3. "Mais informações" → "Permissões"
4. Microfone → Desmarcar "Bloquear"
5. Recarregue página
```

---

### 3️⃣ Verificação Rápida

**Microfone está funcionando?**

Abra **Preferências → Som** (Mac) ou **Configurações → Som** (Windows)

Fale alto: As barrinhas se movem? 📊

- ✅ **Sim** → Microfone OK, é só permissão do navegador
- ❌ **Não** → Problema no microfone/sistema

---

### 4️⃣ Teste no Console

Pressione **F12** → Console → Cole e aperte Enter:

```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(s => { console.log('✅ OK'); s.getTracks()[0].stop(); })
  .catch(e => console.error('❌', e.name));
```

**Resultado:**
- `✅ OK` → Funciona! Recarregue a página
- `❌ NotAllowedError` → Permissão negada (volte ao passo 2)
- `❌ NotFoundError` → Microfone não encontrado

---

## 🚨 Checklist Rápido

- [ ] Microfone está conectado/funcionando?
- [ ] Navegador moderno? (Chrome, Firefox, Safari recente)
- [ ] Usando `localhost:8000` (não IP)?
- [ ] Clicou em "Permitir" microfone?
- [ ] Outro app usando microfone? (Zoom, Teams, etc)
- [ ] Testou recarregar página?
- [ ] Testou fechar e reabrir navegador?

---

## ✅ Funcionou? Como Usar

1. **Clicar no círculo azul** 🔵
2. **Esperar ficar vermelho** 🔴
3. **Falar seu nome**: "Paulino" ou "João Silva"
4. **Confirmar**: Dizer "sim"
5. **Fazer perguntas!**

---

## 📚 Mais Ajuda

Problema persiste? Veja: **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

---

**Dica:** 90% dos erros são resolvidos clicando em "Permitir" microfone! 🎯
