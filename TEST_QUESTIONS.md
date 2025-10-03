# 🎤 Perguntas de Teste - Assistente de Voz

## 📋 Guia de Testes Completo

Este documento contém perguntas para testar todas as funcionalidades do sistema.

---

## 🎯 FASE 1: Autenticação (Nome)

### ✅ Casos de Sucesso

**Teste 1.1: Nome simples**
```
Você: "Paulino"
Esperado: ✅ Encontra "Paulino Santos" → Pede confirmação
```

**Teste 1.2: Nome completo**
```
Você: "João Silva"
Esperado: ✅ Encontra "João Silva" → Pede confirmação
```

**Teste 1.3: Nome + contexto (IMPORTANTE!)**
```
Você: "Chamam-me Paulino, como posso pagar a minha fatura?"
Esperado: ✅ Extrai "Paulino" → Encontra cliente → Pede confirmação
```

**Teste 1.4: Variação de introdução**
```
Você: "Meu nome é Maria Santos"
Esperado: ✅ Extrai "Maria Santos" → Encontra → Confirma
```

**Teste 1.5: Sem acento**
```
Você: "Joao Silva"
Esperado: ✅ Fuzzy match → Encontra "João Silva" (score alto)
```

**Teste 1.6: Nome parcial**
```
Você: "Maria"
Esperado: ✅ Encontra "Maria Santos" → Pede confirmação
```

### ❌ Casos de Falha (Esperados)

**Teste 1.7: Nome inexistente**
```
Você: "Pedro Gonçalves"
Esperado: ❌ "Não encontrei conta com esse nome. Contacte apoio@..."
```

**Teste 1.8: Profanidade**
```
Você: "Merda"
Esperado: ❌ "Esse nome não parece válido. Diga seu nome verdadeiro."
```

**Teste 1.9: Gibberish**
```
Você: "xxxyyy"
Esperado: ❌ "Não consegui entender. Diga seu nome claramente."
```

**Teste 1.10: Muito curto**
```
Você: "A"
Esperado: ❌ "Nome muito curto. Forneça nome completo."
```

---

## 💬 FASE 2: Perguntas sobre Faturação

### ✅ Perguntas na Base de Conhecimento

**Teste 2.1: Como pagar**
```
Pergunta: "Como posso pagar a minha fatura?"
Esperado: ✅ Lista métodos: Online, App, Local físico, USSD (*123#)
Deve mencionar: "{Seu Nome}, pode pagar através de..."
```

**Teste 2.2: Ciclo de faturação**
```
Pergunta: "Quando é emitida a fatura?"
Esperado: ✅ "Dia 1 de cada mês, pagamento em 15 dias"
```

**Teste 2.3: Pagamento atrasado**
```
Pergunta: "O que acontece se atrasar o pagamento?"
Esperado: ✅ Taxa de 50 MZN após 15 dias, suspensão após 30 dias
```

**Teste 2.4: Débito automático**
```
Pergunta: "Posso configurar pagamento automático?"
Esperado: ✅ Sim, via App Mozaitel, débito automático
```

**Teste 2.5: Fatura eletrónica**
```
Pergunta: "Recebo a fatura por email?"
Esperado: ✅ Sim, PDF enviado por email cadastrado
```

---

## 📱 FASE 3: Perguntas sobre Planos

### ✅ Informações de Planos

**Teste 3.1: Meu plano atual**
```
Pergunta: "Qual é o meu plano?"
Esperado: ✅ "{Nome}, você está no plano {Plano do cliente}"
Exemplo: "Paulino, você está no Premium 5G"
```

**Teste 3.2: Detalhes do Premium 5G**
```
Pergunta: "O que tem no plano Premium 5G?"
Esperado: ✅ 50GB, chamadas ilimitadas, roaming, 1.500 MZN/mês
```

**Teste 3.3: Plano Básico**
```
Pergunta: "Quanto custa o plano básico?"
Esperado: ✅ 500 MZN/mês, 10GB, 500 minutos
```

**Teste 3.4: Plano Familiar**
```
Pergunta: "O plano familiar tem quantas linhas?"
Esperado: ✅ Até 4 linhas, 100GB compartilhados, 2.500 MZN/mês
```

**Teste 3.5: Mudança de plano**
```
Pergunta: "Como mudo de plano?"
Esperado: ✅ Via App ou escritório, efeito no próximo ciclo
```

**Teste 3.6: Plano Empresarial**
```
Pergunta: "Existe plano para empresa?"
Esperado: ✅ Plano Empresarial PRO, 200GB, 5.000 MZN/mês
```

---

## 🔧 FASE 4: Suporte Técnico

### ✅ Problemas Comuns

**Teste 4.1: Sem internet**
```
Pergunta: "Não tenho internet, o que fazer?"
Esperado: ✅ Reiniciar dispositivo, verificar dados móveis, APN
```

**Teste 4.2: Configuração APN**
```
Pergunta: "Qual é o APN?"
Esperado: ✅ apn.mozaitel.mz
```

**Teste 4.3: Cobertura de rede**
```
Pergunta: "Onde tem 5G?"
Esperado: ✅ Maputo, Matola, Beira (5G). Nacional (4G)
```

**Teste 4.4: SIM perdido**
```
Pergunta: "Perdi meu SIM, o que faço?"
Esperado: ✅ Ligar 840-123-456 para bloquear, novo SIM 100 MZN
```

**Teste 4.5: Configuração manual Android**
```
Pergunta: "Como configurar APN no Android?"
Esperado: ✅ Definições → Redes Móveis → APN → Novo: apn.mozaitel.mz
```

---

## 📊 FASE 5: Dados e Saldo

### ✅ Consultas de Uso

**Teste 5.1: Consultar saldo**
```
Pergunta: "Como vejo meu saldo de dados?"
Esperado: ✅ Discar *124# ou App Mozaitel
```

**Teste 5.2: Exceder limite**
```
Pergunta: "E se acabar os dados?"
Esperado: ✅ Velocidade reduz para 512kbps, comprar pacotes via *125#
```

**Teste 5.3: Pacotes adicionais**
```
Pergunta: "Como compro mais dados?"
Esperado: ✅ *125# ou App Mozaitel
```

**Teste 5.4: Transferir saldo**
```
Pergunta: "Posso transferir saldo?"
Esperado: ✅ Sim, via *126# → Transferir Saldo
```

---

## 📞 FASE 6: Contato e Suporte

### ✅ Informações de Contato

**Teste 6.1: Email de suporte**
```
Pergunta: "Qual é o email de apoio?"
Esperado: ✅ apoio@mozaitelecomunicacao.co.mz
```

**Teste 6.2: Endereço físico**
```
Pergunta: "Onde fica o escritório?"
Esperado: ✅ Av. Julius Nyerere, Nº 2500, Maputo
```

**Teste 6.3: Telefone de suporte**
```
Pergunta: "Qual o número para ligar?"
Esperado: ✅ 840-123-456 (Seg-Sex 8h-18h) ou 843-999-999 (emergência 24/7)
```

**Teste 6.4: Horário de atendimento**
```
Pergunta: "Qual o horário de atendimento?"
Esperado: ✅ Segunda a Sexta, 8h às 18h
```

---

## ⚠️ FASE 7: Perguntas Fora do Escopo

### ❌ Deve Redirecionar para Suporte

**Teste 7.1: Reclamação formal**
```
Pergunta: "Quero fazer uma reclamação"
Esperado: ❌ Redireciona para reclamacoes@mozaitelecomunicacao.co.mz
```

**Teste 7.2: Reembolso**
```
Pergunta: "Como peço reembolso?"
Esperado: ❌ Solicitar via email, 7 dias úteis para processar
```

**Teste 7.3: Cancelamento de serviço**
```
Pergunta: "Quero cancelar minha conta"
Esperado: ❌ Redireciona para email com 30 dias de antecedência
```

**Teste 7.4: Mudança de dados cadastrais**
```
Pergunta: "Como atualizo meu endereço?"
Esperado: ❌ Via App Mozaitel ou balcão físico
```

---

## 🌍 FASE 8: Perguntas Completamente Fora

### ❌ Deve Rejeitar Claramente

**Teste 8.1: Tempo**
```
Pergunta: "Qual é a previsão do tempo?"
Esperado: ❌ "{Nome}, essa pergunta está fora do nosso âmbito..."
```

**Teste 8.2: Esportes**
```
Pergunta: "Quem ganhou o jogo ontem?"
Esperado: ❌ Redireciona para suporte
```

**Teste 8.3: Receitas**
```
Pergunta: "Como faço matapa?"
Esperado: ❌ Fora do escopo
```

**Teste 8.4: Notícias**
```
Pergunta: "Quais são as notícias de hoje?"
Esperado: ❌ Fora do escopo
```

---

## 🧪 FASE 9: Testes de Personalização

### ✅ Deve SEMPRE Usar o Nome

**Teste 9.1: Verificar menção do nome**
```
Qualquer pergunta válida
Esperado: ✅ Resposta DEVE conter "{Seu Nome}" pelo menos uma vez
Exemplo: "Paulino, você pode pagar através de..."
```

**Teste 9.2: Verificar informação do plano**
```
Pergunta: "Qual meu plano?"
Esperado: ✅ Menciona plano específico do cliente autenticado
```

---

## 🎯 FASE 10: Testes de Contexto

### ✅ Perguntas de Follow-up

**Teste 10.1: Sequência de perguntas**
```
P1: "Como pago a fatura?"
R1: Lista métodos...

P2: "E quanto custa?"
R2: Deve entender contexto (fatura do plano do cliente)
```

**Teste 10.2: Referências**
```
P1: "O que tem no Premium 5G?"
R1: Lista benefícios...

P2: "E quanto custa esse plano?"
R2: Deve saber que "esse plano" = Premium 5G
```

---

## 📊 CHECKLIST DE TESTES

### Autenticação
- [ ] Nome simples funciona
- [ ] Nome + pergunta extrai corretamente
- [ ] Fuzzy matching funciona
- [ ] Rejeita nomes inválidos
- [ ] Confirma antes de autenticar

### Respostas
- [ ] SEMPRE menciona nome do cliente
- [ ] Usa APENAS informação da base
- [ ] Redireciona quando apropriado
- [ ] Rejeita perguntas fora do escopo
- [ ] Respostas em português correto

### Qualidade
- [ ] Respostas concisas (3-4 frases)
- [ ] Informação precisa
- [ ] Tom profissional e prestativo
- [ ] Cita fontes quando relevante

### Funcionalidade
- [ ] Voz para texto funciona
- [ ] Texto para voz funciona
- [ ] WebSocket estável
- [ ] Sem erros no console

---

## 🎤 Script de Teste Completo (5 min)

```
1. AUTENTICAÇÃO
   Dizer: "Paulino"
   Confirmar: "Sim"

2. TESTE BÁSICO
   Perguntar: "Como posso pagar a minha fatura?"
   Verificar: Menciona "Paulino" e lista métodos

3. TESTE PLANO
   Perguntar: "Qual é o meu plano?"
   Verificar: Diz "Premium 5G"

4. TESTE TÉCNICO
   Perguntar: "Qual é o APN?"
   Verificar: Diz "apn.mozaitel.mz"

5. TESTE FORA ESCOPO
   Perguntar: "Qual é o tempo hoje?"
   Verificar: Rejeita educadamente

6. TESTE CONTATO
   Perguntar: "Qual o email de apoio?"
   Verificar: Diz "apoio@mozaitelecomunicacao.co.mz"
```

---

## 🐛 O Que Reportar se Falhar

Se algum teste falhar, anote:

1. **Pergunta exata** que fez
2. **Resposta recebida**
3. **Resposta esperada**
4. **Logs do console** (F12)
5. **Cliente autenticado** (qual nome)
6. **Screenshot** se possível

---

## 📈 Métricas de Sucesso

**Excelente (>90%):**
- Responde corretamente 9 de 10 perguntas
- SEMPRE menciona nome
- Nunca inventa informação

**Bom (70-90%):**
- Responde corretamente 7-9 de 10
- Geralmente menciona nome
- Raramente inventa

**Precisa Melhorar (<70%):**
- Menos de 7 de 10 corretas
- Esquece de mencionar nome
- Inventa informação

---

**Versão:** 1.0
**Data:** 2025-10-03
**Última Atualização:** Após implementação do sistema completo
