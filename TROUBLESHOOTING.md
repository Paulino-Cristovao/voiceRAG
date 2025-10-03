# 🔧 Guia de Solução de Problemas

## 🎤 Erro: "Erro ao acessar microfone"

### Causa 1: Permissão Negada

**Sintoma:** Navegador bloqueou acesso ao microfone

**Solução:**

#### Chrome/Edge:
1. Clique no ícone **🔒** (cadeado) na barra de endereço
2. Procure por "Microfone"
3. Selecione **"Permitir"**
4. Recarregue a página (F5)

![Chrome Permission](https://via.placeholder.com/400x100/667eea/ffffff?text=Chrome:+Clique+no+cadeado+%E2%86%92+Microfone+%E2%86%92+Permitir)

#### Safari:
1. Menu Safari → **Preferências**
2. Aba **"Sites"**
3. Seção **"Microfone"**
4. Encontre `localhost`
5. Selecione **"Permitir"**
6. Recarregue a página

#### Firefox:
1. Clique no ícone **🔒** na barra de endereço
2. Clique em **"Permissões"** → **"Microfone"**
3. Desmarque **"Bloquear temporariamente"**
4. Marque **"Lembrar desta decisão"**
5. Selecione **"Permitir"**
6. Recarregue a página

---

### Causa 2: Nenhum Microfone Encontrado

**Sintoma:** "Nenhum microfone encontrado"

**Soluções:**

✅ **Verificar conexão física:**
- Microfone externo conectado corretamente?
- Cabo USB bem encaixado?
- Fone de ouvido com microfone conectado?

✅ **Verificar configurações do sistema:**

**macOS:**
1. Preferências do Sistema → **Som**
2. Aba **"Entrada"**
3. Verificar se microfone aparece na lista
4. Testar nível de entrada (barras devem se mover ao falar)

**Windows:**
1. Configurações → **Sistema** → **Som**
2. Seção **"Entrada"**
3. Selecionar microfone correto
4. Testar dispositivo

**Linux:**
1. Abrir terminal
2. `arecord -l` (listar dispositivos)
3. `alsamixer` (verificar volume)

✅ **Testar microfone:**
- Abrir Gravador de Som do sistema
- Fazer teste de gravação
- Se não funcionar → problema no hardware/drivers

---

### Causa 3: Microfone em Uso

**Sintoma:** "Microfone em uso por outro aplicativo"

**Soluções:**

1. **Fechar aplicativos que usam microfone:**
   - Zoom, Google Meet, Teams, Skype
   - Discord, Slack
   - OBS Studio, Audacity
   - Outros navegadores com páginas de vídeo

2. **macOS - Verificar qual app usa microfone:**
   - Ícone 🔴 na barra de menu indica uso de microfone
   - Activity Monitor → Buscar "VDC" ou "Audio"

3. **Windows - Verificar:**
   - Configurações → Privacidade → Microfone
   - Ver quais apps têm permissão

4. **Reiniciar navegador:**
   - Fechar TODAS as abas
   - Sair completamente (Cmd+Q no Mac, Alt+F4 no Windows)
   - Abrir novamente

---

### Causa 4: Erro de Segurança (HTTPS)

**Sintoma:** "Erro de segurança. Use HTTPS ou localhost"

**Soluções:**

✅ **Usar localhost (recomendado para desenvolvimento):**
```
http://localhost:8000  ✅
http://127.0.0.1:8000  ✅
```

❌ **NÃO use IP da rede local sem HTTPS:**
```
http://192.168.1.100:8000  ❌ (bloqueado)
```

✅ **Para acesso externo, use HTTPS:**
```bash
# Com Caddy (automático)
caddy reverse-proxy --from https://seu-dominio.com --to localhost:8000

# Com nginx + certbot
certbot --nginx -d seu-dominio.com
```

---

### Causa 5: Navegador Não Suportado

**Sintoma:** "Navegador não suporta gravação de áudio"

**Navegadores Suportados:**
- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 14+
- ✅ Edge 79+
- ❌ Internet Explorer (não suportado)
- ❌ Navegadores antigos

**Solução:** Atualize ou troque de navegador

---

## 🔊 Áudio Não Toca

### Verificar Volume
1. Volume do sistema não está mudo
2. Volume do navegador não está mudo
3. Testar com outro site (ex: YouTube)

### Testar Saída de Áudio
```bash
# macOS - Testar alto-falante
say "teste de áudio"

# Linux - Testar
speaker-test -t wav -c 2
```

### Safari Específico
Safari pode bloquear autoplay de áudio:
1. Safari → Preferências → Sites → Auto-Reprodução
2. Selecionar "Permitir Tudo Auto-Reprodução"

---

## 🌐 WebSocket Desconecta

### Verificar Firewall
```bash
# Testar se porta 8000 está aberta
curl http://localhost:8000

# Ver se servidor está rodando
lsof -i :8000
```

### Verificar Logs do Servidor
```bash
# Ver erros no terminal onde rodou python app.py
# Procurar por linhas com ERROR ou Exception
```

### Reiniciar Servidor
```bash
# Parar (Ctrl+C)
# Reiniciar
python app.py
```

---

## 🐛 Outros Problemas

### Transcrição Errada
- Fale mais devagar e claro
- Aproxime-se do microfone
- Reduza ruído ambiente
- Verifique se microfone está selecionado corretamente

### Respostas Genéricas
- Base de conhecimento pode estar incompleta
- Adicione mais PDFs em `pdfs/`
- Reconstrua índice: `python ingest_pdfs.py`

### Nome Não Reconhecido
- Adicione cliente em `customers/customers.json`
- Fale apenas o nome (sem perguntas junto)
- Fale claramente

---

## 📞 Teste Rápido de Microfone

Abra console do navegador (F12) e cole:

```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    console.log('✅ Microfone OK!');
    stream.getTracks().forEach(track => track.stop());
  })
  .catch(err => {
    console.error('❌ Erro:', err.name, err.message);
  });
```

**Resultados Esperados:**

✅ `Microfone OK!` → Tudo funcionando
❌ `NotAllowedError` → Permissão negada
❌ `NotFoundError` → Microfone não encontrado
❌ `NotReadableError` → Microfone em uso

---

## 🆘 Ainda Não Funciona?

1. **Teste em outro navegador**
2. **Teste em modo anônimo/privado**
3. **Reinicie o computador**
4. **Verifique drivers de áudio**
5. **Teste com microfone diferente**

Se nada funcionar, abra issue no repositório com:
- Sistema operacional e versão
- Navegador e versão
- Mensagem de erro completa
- Console do navegador (F12 → Console)
- Logs do servidor

---

**Última Atualização:** 2025-10-03
