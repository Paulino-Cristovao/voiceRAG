# 📝 Changelog - Voice RAG Assistant

## Melhorias Implementadas

### ✅ Extração Inteligente de Nome

**Problema:**
- Sistema rejeitava quando cliente dizia: "Chamam-me Paulino, como posso pagar?"
- Validação muito estrita (não permitia pontuação)

**Solução:**
- Novo método `extract_name_from_speech()` que:
  - Reconhece padrões portugueses: "chamam-me X", "meu nome é X", "sou X"
  - Extrai nome antes de vírgulas ou palavras-chave (como, quero, posso)
  - Permite até 3 palavras para nomes completos
  - Para automaticamente ao encontrar verbos/perguntas

**Exemplos que AGORA FUNCIONAM:**

✅ "Chamam-me Paulino, como posso pagar a minha fatura?"
   → Extrai: "Paulino"

✅ "Meu nome é João Silva"
   → Extrai: "João Silva"

✅ "Sou Maria Santos e quero saber..."
   → Extrai: "Maria Santos"

✅ "Carlos Machel, tenho uma pergunta"
   → Extrai: "Carlos Machel"

✅ "Paulino"
   → Extrai: "Paulino"

### ✅ Validação Melhorada

**Antes:**
- Rejeitava qualquer caractere que não fosse letra
- Erro: "Nomes devem conter apenas letras"

**Agora:**
- Aceita vírgulas, pontos, apóstrofos, hífens
- Validação mais inteligente:
  - ✅ Profanidade (PT + EN)
  - ✅ Gibberish (sem vogais, repetição)
  - ✅ Comprimento (2-50 chars)
  - ✅ Números e símbolos especiais bloqueados
  - ✅ Palavras de sistema bloqueadas

### ✅ Mensagens Mais Claras

**Antes:**
- "Qual é o seu nome, por favor?"

**Agora:**
- "Por favor, diga **apenas** o seu nome para começar."
- "Não ouvi nada. Por favor diga **apenas** o seu nome."
- Ênfase em "apenas nome" para evitar perguntas mistas

### ✅ Cliente de Teste Adicionado

Novo cliente: **Paulino Santos**
- ID: 004
- Plano: Premium 5G
- Telefone: +258847001111

## Como Testar

### Cenário 1: Nome + Pergunta (Agora Funciona!)
```
Usuário: "Chamam-me Paulino, como posso pagar?"
Sistema: Extrai "Paulino" → Busca cliente → Confirma
```

### Cenário 2: Nome Completo
```
Usuário: "Meu nome é João Silva"
Sistema: Extrai "João Silva" → Busca cliente → Confirma
```

### Cenário 3: Nome Simples
```
Usuário: "Maria"
Sistema: Extrai "Maria" → Busca "Maria Santos" (fuzzy) → Confirma
```

### Cenário 4: Nome Formal
```
Usuário: "Sou Carlos Machel e tenho dúvida sobre..."
Sistema: Extrai "Carlos Machel" → Busca cliente → Confirma
```

## Testes de Validação

✅ **Profanidade** → Bloqueado
❌ "Me chamo merda"
✅ "Me chamo Paulino"

✅ **Gibberish** → Bloqueado
❌ "xxxyyy"
✅ "Paulino"

✅ **Muito Longo** → Bloqueado
❌ Nome com >50 caracteres
✅ "Paulino Santos"

✅ **Números** → Bloqueado
❌ "João123"
✅ "João Silva"

## Fluxo Atualizado

1. **Conectar** → Assistente: "Diga apenas o seu nome"
2. **Gravar** → Círculo azul → vermelho (5s)
3. **Falar** → "Chamam-me Paulino, ..." ou só "Paulino"
4. **Extrair** → Sistema extrai só o nome
5. **Validar** → Verifica se é nome válido
6. **Buscar** → Fuzzy match no banco (60% similaridade)
7. **Confirmar** → "Encontrei Paulino Santos, correto?"
8. **Autenticar** → "Sim" → Pronto para perguntas!

## Arquitetura Técnica

```python
Áudio → Whisper STT → "Chamam-me Paulino, como posso..."
                           ↓
                extract_name_from_speech()
                           ↓
                      "Paulino"
                           ↓
                    validate_name()
                           ↓
                    fuzzy_match()
                           ↓
                "Paulino Santos" (60% match)
                           ↓
                     Confirmação
```

## Próximas Melhorias

- [ ] Suporte a sobrenomes compostos (e.g., "da Silva")
- [ ] Detecção de títulos (Sr., Sra., Dr.)
- [ ] Cache de reconhecimento por voz
- [ ] Melhor tratamento de sotaques regionais

---

**Data:** 2025-10-03
**Versão:** 1.1.0
