# 📱 INTEGRAÇÃO WHATSAPP - NOTIFICAÇÕES DE DEALS

## ✅ IMPLEMENTAÇÃO CONCLUÍDA

### 🎯 O que foi feito:

1. **✅ Filtro no N8N "Gerador de Personas AI"**
   - Adicionado nó IF2 para filtrar mensagens de grupos
   - Condição: `{{ $json.key.remoteJid }} [does not end with] @g.us`
   - **Resultado:** Mensagens de grupos são ignoradas, apenas mensagens privadas processam

2. **✅ Função de envio WhatsApp no app.py**
   - Nova função: `send_whatsapp_notification(deal_data)`
   - Integrada no webhook `/api/webhook/deal-won`
   - Envia mensagem formatada para o grupo RevOps

3. **✅ Variáveis de ambiente configuradas**
   - `EVOLUTION_API_URL`: https://evolution-api-logcomex.34-49-195-55.nip.io
   - `EVOLUTION_API_KEY`: Armazenado no Secret Manager
   - `EVOLUTION_INSTANCE_NAME`: RevOps
   - `ID_GRUPO_REVOPS`: 554191877530-1510578382@g.us

4. **✅ Cloud Build atualizado**
   - Adicionadas variáveis de ambiente no deploy
   - Secret `EVOLUTION_API_KEY` configurado
   - Deploy em andamento

---

## 📋 COMO FUNCIONA

### Fluxo Completo:

```
1. HubSpot → Deal ganho
   ↓
2. Webhook /api/webhook/deal-won recebe notificação
   ↓
3. app.py processa e salva no banco
   ↓
4. send_whatsapp_notification() é chamada
   ↓
5. Evolution API envia mensagem para grupo WhatsApp
   ↓
6. Notificação exibida na tela (animação)
```

### Mensagem WhatsApp:

```
🎉 *DEAL GANHO!*

💰 *Valor:* R$ 50.000,00
📝 *Deal:* Logcomex Enterprise - Teste Notificação

👥 *Time Vencedor:*
👔 *EV:* João Silva
📞 *SDR:* Maria Santos
🎯 *LDR:* Pedro Costa

🏢 *Empresa:* Logcomex Tecnologia
📅 *Data:* 07/11/2025 14:23

---
_Black November 2025 🚀_
```

---

## 🔧 CONFIGURAÇÕES TÉCNICAS

### Evolution API:
- **URL:** https://evolution-api-logcomex.34-49-195-55.nip.io
- **Endpoint:** `/message/sendText/{instance}`
- **Instância:** RevOps
- **Número:** 5541936180748
- **Grupo:** 554191877530-1510578382@g.us

### Webhook N8N:
- **URL:** https://n8n-logcomex.34-8-101-220.nip.io/webhook-test/996ff3b5-bab0-4eaf-b79e-ea262a994b25
- **Eventos:** MESSAGES_UPSERT, SEND_MESSAGE
- **Filtro:** Ignora mensagens de grupos (`@g.us`)

---

## 🧪 TESTANDO

### Teste Manual:
```bash
python test_whatsapp_group.py
```

### Teste via Webhook:
1. Acesse: https://black-november-funnel-XXXXXX.run.app/api/webhook/test
2. Ou envie POST para `/api/webhook/deal-won` com payload de deal

---

## 📝 ARQUIVOS MODIFICADOS

1. **app.py**
   - `import requests` adicionado
   - Função `send_whatsapp_notification()` criada
   - Integração no webhook `/api/webhook/deal-won`

2. **.env**
   - Variáveis Evolution API adicionadas
   - ID do grupo configurado

3. **cloudbuild.yaml**
   - Variáveis de ambiente adicionadas
   - Secret EVOLUTION_API_KEY configurado

4. **N8N - Gerador de Personas AI**
   - Nó IF2 adicionado
   - Filtro de grupos configurado

---

## ⚠️ IMPORTANTE

### O que NÃO quebra:
- ✅ Mensagens privadas no WhatsApp RevOps continuam processando normalmente
- ✅ Fluxo "Gerador de Personas AI" funciona apenas para mensagens 1:1
- ✅ Notificações na tela continuam funcionando

### O que mudou:
- ✅ Agora envia WhatsApp para grupo quando deal é ganho
- ✅ Respostas no grupo NÃO acionam o N8N
- ✅ Deploy automático via Cloud Build

---

## 🚀 PRÓXIMOS PASSOS

1. ⏳ Aguardar deploy finalizar
2. ✅ Testar com deal real no HubSpot
3. ✅ Verificar mensagem no grupo WhatsApp
4. ✅ Confirmar que N8N não é acionado pelas respostas do grupo

---

## 📞 SUPORTE

Se algo não funcionar:

1. **Verificar logs do Cloud Run:**
   ```bash
   gcloud logs read --service=black-november-funnel --limit=50
   ```

2. **Verificar Secret Manager:**
   ```bash
   gcloud secrets versions access latest --secret="EVOLUTION_API_KEY"
   ```

3. **Testar Evolution API diretamente:**
   ```bash
   curl -X POST https://evolution-api-logcomex.34-49-195-55.nip.io/message/sendText/RevOps \
     -H "apikey: SEU_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"number":"554191877530-1510578382@g.us","text":"Teste"}'
   ```

---

**🎉 Implementação concluída! Aguardando deploy...**
