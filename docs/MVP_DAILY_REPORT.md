# Relatório Diário de MVPs - Black November

## 📋 Visão Geral

Sistema automático que envia diariamente às 20h (GMT-3) um relatório com as imagens dos MVPs (Destaques do Dia) do Hall da Fama para o grupo WhatsApp.

## 🎯 Funcionalidades

- Gera imagens dos MVPs usando o mesmo CSS/HTML do Hall da Fama
- Envia para grupo de TESTE ou PRODUÇÃO
- Agendamento automático via Cloud Scheduler
- Endpoint manual para testes

## 📁 Arquivos Criados

### 1. `mvp_image_generator.py`
Gera imagens PNG dos cards MVP usando Playwright.

**Funcionalidades:**
- Usa CSS/HTML idêntico ao `hall_da_fama.html`
- Busca fotos dos membros em `static/img/team/`
- Inclui badges (emojis ou imagens personalizadas)
- Gera imagens para: EVs, SDRs NEW, SDRs Expansão, LDRs

### 2. `send_daily_mvp_report.py`
Script principal que busca dados e envia para WhatsApp.

**Funcionalidades:**
- Busca dados via APIs do Hall da Fama
- Gera imagens dos 4 MVPs
- Envia para WhatsApp via Evolution API
- Suporta modo TESTE e PRODUÇÃO

### 3. Endpoint no `app.py`
`POST /api/send-daily-mvp-report?env=test|prod`

**Autenticação:** Requer auth (IP permitido ou login Google)

## 🚀 Como Usar

### Teste Manual (Local)

1. **Rode o servidor:**
```bash
python app.py
```

2. **Chame o endpoint de teste:**
```bash
# Grupo de TESTE
curl -X POST http://localhost:5000/api/send-daily-mvp-report?env=test

# Grupo de PRODUÇÃO (quando validado)
curl -X POST http://localhost:5000/api/send-daily-mvp-report?env=prod
```

### Teste via Script Python

```bash
# Grupo de TESTE
python send_daily_mvp_report.py

# Grupo de PRODUÇÃO
python send_daily_mvp_report.py --prod
```

## ⚙️ Configuração do Cloud Scheduler

### Criar Job no Cloud Scheduler

```bash
gcloud scheduler jobs create http mvp-daily-report \
  --schedule="0 20 * * *" \
  --time-zone="America/Sao_Paulo" \
  --uri="https://black-november-funnel-998985848998.southamerica-east1.run.app/api/send-daily-mvp-report?env=test" \
  --http-method=POST \
  --oidc-service-account-email=YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com \
  --location=southamerica-east1
```

**Importante:** 
- Inicialmente usa `env=test` para validação
- Após validar, mudar para `env=prod`

### Atualizar Job (quando validar)

```bash
gcloud scheduler jobs update http mvp-daily-report \
  --uri="https://black-november-funnel-998985848998.southamerica-east1.run.app/api/send-daily-mvp-report?env=prod" \
  --location=southamerica-east1
```

## 📱 Grupos WhatsApp

### Grupo de TESTE
- **ID:** `120363405303439862@g.us`
- **Uso:** Validação e testes

### Grupo de PRODUÇÃO
- **ID:** `554191877530-1510578382@g.us`
- **Uso:** Envio oficial após validação

## 🔄 Fluxo de Envio

1. **20h (GMT-3)** → Cloud Scheduler dispara webhook
2. **Endpoint** → Busca dados das APIs do Hall da Fama
3. **Gerador** → Cria imagens PNG dos 4 MVPs
4. **WhatsApp** → Envia imagens com legendas para o grupo

**Formato das mensagens:**
```
🏆 HALL DA FAMA - DESTAQUES DO DIA

📅 Data: 14/11/2025

Confira os MVPs de hoje! 🎉👇

[Imagem EV]
[Imagem SDR NEW]
[Imagem SDR Expansão]
[Imagem LDR]

---
✨ Parabéns aos destaques! 🎊
Continue assim, time! 💪🚀

Black November 2025
```

## 🧪 Checklist de Validação

Antes de mudar para PRODUÇÃO, validar:

- [ ] Imagens estão sendo geradas corretamente
- [ ] Fotos dos membros aparecem
- [ ] Badges estão visíveis (emojis ou imagens)
- [ ] Estatísticas corretas (deals, agendamentos, faturamento)
- [ ] Formatação idêntica ao Hall da Fama
- [ ] Envio para grupo de teste funcionando
- [ ] Horário correto (20h GMT-3)

## 🛠️ Troubleshooting

### Imagens não aparecem
- Verificar se Playwright está instalado: `pip install playwright`
- Instalar browsers: `playwright install chromium`

### Fotos não aparecem
- Verificar se as fotos estão em `static/img/team/`
- Nome do arquivo deve ser normalizado: `nome_sobrenome.png`

### WhatsApp não envia
- Verificar variáveis de ambiente:
  - `EVOLUTION_API_URL`
  - `EVOLUTION_API_KEY`
  - `EVOLUTION_INSTANCE_NAME`

### Badges não aparecem
- Verificar imagens em `static/img/badges/`
- Fallback para emojis se imagem não existir

## 📊 Monitoramento

Logs importantes:
```
🏆 INICIANDO ENVIO DO RELATÓRIO DIÁRIO DE MVPs
📍 Ambiente: TESTE
📱 Grupo: 120363405303439862@g.us
📡 Buscando dados do Hall da Fama...
✅ Dados do Hall da Fama obtidos com sucesso
🎨 Gerando imagens dos MVPs...
✅ Imagem do MVP EV gerada
✅ Imagem do MVP SDR NEW gerada
✅ Imagem do MVP SDR Expansão gerada
✅ Imagem do MVP LDR gerada
📤 Enviando imagem 'mvp_evs_20251114.png' para grupo...
✅ Imagem 'mvp_evs_20251114.png' enviada com sucesso!
✅ RELATÓRIO ENVIADO COM SUCESSO (4/4)
```

## 🔐 Segurança

- Endpoint requer autenticação (`@require_auth`)
- Apenas IPs permitidos ou usuários autenticados
- Variáveis sensíveis em Secret Manager

## 📅 Próximos Passos

1. ✅ Testar envio manual
2. ✅ Validar imagens no grupo de teste
3. ⏳ Configurar Cloud Scheduler
4. ⏳ Monitorar primeiro envio automático
5. ⏳ Migrar para produção após validação
