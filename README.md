# Black November Logcomex 2025 🎯

Sistema completo de gamificação e visualização de vendas em tempo real para a campanha Black November da Logcomex. O que começou como um simples funil animado evoluiu para um ecossistema integrado com painéis de TV, notificações WhatsApp, celebrações automáticas e rankings em tempo real.

## 🌟 Visão Geral

Sistema composto por:
- **Painel 1 - Dashboard Principal** (`/`): Funil animado com rankings rotativos (4 slides: EVs, SDRs NEW, SDRs Expansão, LDRs)
- **Painel 2 - Metas & Progresso** (`/metas`): Meta do dia, pipeline previsto, contagem regressiva e status inteligente
- **Painel de Rotação** (`/aleatorio`): Alterna automaticamente entre painéis a cada 1 minuto
- **Webhooks HubSpot**: Integração em tempo real com o CRM
- **Notificações WhatsApp**: Imagens de celebração + mensagens via Evolution API
- **Sistema de Celebração**: Animações visuais e sonoras quando deals são fechados
- **Banco de Dados**: Persistência de notificações e histórico (PostgreSQL Cloud SQL)
- **PWA**: Progressive Web App com notificações push

## 📋 Requisitos

- Python 3.11+
- PostgreSQL (banco `hubspot-sync` espelhado do HubSpot)
- Docker e Docker Compose (opcional)
- Playwright + Chromium (para geração de imagens)
- Evolution API (para WhatsApp)
- Google Cloud Run (produção)

## 🚀 Instalação Local

### 1. Clone o repositório:

```bash
git clone https://github.com/erikson-logcomex/black-november.git
cd black-november
```

### 2. Configure as variáveis de ambiente:

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e preencha com suas credenciais
# O arquivo .env.example contém todas as variáveis necessárias com explicações
```

**Arquivo `.env.example` contém todas as variáveis necessárias organizadas por categoria:**

- **Aplicação**: `PORT`, `SECRET_KEY`, `API_BASE_URL`
- **PostgreSQL**: `PG_HOST`, `PG_PORT`, `PG_DATABASE_HUBSPOT`, `PG_USER`, `PG_PASSWORD`
- **HubSpot API**: `HUBSPOT_PRIVATE_APP_TOKEN`, `HUBSPOT_WEBHOOK_SECRET`
- **Looker**: `LOOKER_USERNAME`, `LOOKER_PASSWORD`, `GCS_BUCKET_NAME` (opcional)
- **Evolution API (WhatsApp)**: `EVOLUTION_API_URL`, `EVOLUTION_API_KEY`, `EVOLUTION_INSTANCE_NAME`, `ID_GRUPO_REVOPS`
- **Google OAuth**: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`

**⚠️ IMPORTANTE - Configuração do Looker:**

Após configurar `LOOKER_USERNAME` e `LOOKER_PASSWORD` no `.env`, execute:

```bash
python setup_looker_session.py
```

Este script abrirá um navegador para você fazer login manualmente no Looker (incluindo 2FA). **Marque o checkbox "Confiar neste navegador"** para evitar precisar fazer 2FA em todas as requisições. Os cookies serão salvos automaticamente.

### 3. Instale as dependências:

```bash
pip install -r requirements.txt

# Instala Chromium para geração de imagens
playwright install --with-deps chromium
```

### 4. Execute a aplicação:

```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## � Deploy com Docker

### Build da imagem:

```bash
docker build -t black-november .
```

### Executar localmente:

```bash
docker run -d \
  --name black-november \
  -p 5000:5000 \
  --env-file .env \
  black-november
```

### Deploy no Google Cloud Run:

```bash
gcloud builds submit --config cloudbuild.yaml .
```

**URL de Produção**: https://black-november-funnel-998985848998.southamerica-east1.run.app

## 🎨 Funcionalidades Principais

### 🖥️ Painéis Disponíveis

### Estrutura de Rotas Temáticas

O sistema suporta múltiplos temas (Natal e Black November) com rotas separadas:

**Rotas de Natal:**
- `/natal` - Dashboard principal (Natal)
- `/natal/metas` - Painel de metas (Natal)
- `/natal/hall-da-fama` - Hall da Fama (Natal)
- `/natal/destaques` - Destaques (Natal)
- `/natal/logos-supply` - Logos Supply (Natal)
- `/natal/arr` - ARR (Natal)

**Rotas Black November:**
- `/black-november` - Dashboard principal (Black November)
- `/black-november/metas` - Painel de metas (Black November)
- `/black-november/hall-da-fama` - Hall da Fama (Black November)
- `/black-november/destaques` - Destaques (Black November)

**Rotas Legadas (Redirecionam para Natal):**
- `/` - Redireciona para seleção de painéis
- `/metas` - Redireciona para `/natal/metas`
- `/hall-da-fama` - Redireciona para `/natal/hall-da-fama`
- `/destaques` - Redireciona para `/natal/destaques`

**Outras Rotas:**
- `/aleatorio` - Rotação automática entre painéis
- `/demo` - Página de demonstração com controles
- `/webhook-debug` - Interface de debug de webhooks

### Painel 1 - Dashboard Principal (`/natal` ou `/black-november`)

**Centro:**
- Funil animado com receita atual da Black November
- Meta: R$ 1.500.000
- Marcos: R$ 300k, R$ 600k, R$ 900k, R$ 1.200k
- CSO Allan Santos com animação de boca (fala "MAÔEEEEEE")
- Roleta girando
- Chuva de dinheiro com música do Silvio Santos

**Lado Esquerdo - Rankings Rotativos (slider automático a cada 12s):**

1. **Slide 1 - Top 5 EVs (Executivos de Vendas)**
   - Receita do dia (deals assinados)
   - Medalhas 🥇🥈🥉 para top 3
   - Fotos dos analistas
   - Atualização a cada 30 segundos

2. **Slide 2 - Top 5 SDRs NEW**
   - Agendamentos do pipeline NEW (ID: 6810518)
   - Quantidade de agendamentos do dia

3. **Slide 3 - Top 5 SDRs Expansão**
   - Agendamentos do pipeline Expansão (ID: 4007305)
   - Quantidade de agendamentos do dia

4. **Slide 4 - Top 5 LDRs**
   - Conversão MQL → Deal Ganho
   - Performance de geração de leads

### 🎯 Painel 2 - Metas & Progresso (`/natal/metas` ou `/black-november/metas`)

**Status:** ✅ **100% Implementado** (12/11/2025)

**Funcionalidades:**
- **Barra de progresso gigante** com cores dinâmicas:
  - 🔴 Crítico (< 50%)
  - 🟡 Atenção (50-80%)
  - 🟢 Perto (80-100%)
  - ✅ Meta batida (> 100%)
- **Meta do dia dinâmica**: R$ 107.142,86 (meta mensal / dias úteis restantes)
- **Faturamento atual**: Atualizado em tempo real (a cada 30s)
- **Pipeline previsto**: Deals com previsão de fechamento HOJE que ainda não foram ganhos
- **Projeção do dia**: Faturado + Pipeline previsto
- **Contagem regressiva**: Até o fim do dia (23:59:59)
- **Status inteligente**: Considera tempo restante, progresso real e projeção
  - 🚨 **Crítico**: Longe da meta e pouco tempo
  - ⚡ **Acelerar**: Ritmo bom mas precisa manter
  - ✅ **No Caminho**: Projeção indica meta será batida
- **Cards de estatísticas**:
  - Faturado no mês
  - Meta da Black November (R$ 1.500.000)
  - Falta para meta mensal
  - Dias úteis restantes (considera feriados)
- **Ritmo atual**: Média/hora e projeção baseada no ritmo
- **Imagem motivacional**: Bruno com megafone (canto inferior direito)

**Lógica de Dados:**
- **Timezone Brasil** (GMT-3) em todas as queries
- **Faturado hoje**: Deals ganhos com `closedate = hoje` (timezone ajustado)
  - Usa campo `valor_ganho`
  - Stages: ganho/faturamento/aguardando
  - Exclui: Pontual e Variação Cambial
- **Pipeline previsto**: Deals com `closedate = hoje` ainda não ganhos
  - Usa campo `amount`
  - **Filtro CORRIGIDO** (12/11/2025): 
    - `deal_isclosed = FALSE OR deal_isclosed IS NULL`
    - `stage_label NOT LIKE '%ganho%'`
    - `stage_label NOT LIKE '%faturamento%'`
    - `stage_label NOT LIKE '%aguardando%'`
    - `stage_label NOT LIKE '%perdido%'` ← **NOVO!**
  - Redução de 70% de falsos positivos (37 → 11 deals)
- **Dias úteis**: Exclui sábados, domingos e feriados (20/11 - Consciência Negra)

**Correções Implementadas:**
1. ✅ Lógica SQL corrigida: mudou de `OR` para `AND` nos filtros
2. ✅ Adicionado filtro `NOT LIKE '%perdido%'` para excluir deals perdidos/churn
3. ✅ Teste de comparação HubSpot vs Banco criado (`test_pipeline_hubspot_vs_db.py`)
4. ✅ Script de validação SQL (`test_query_corrigida.py`)
5. ✅ Deploy em produção com correções validadas

### 🔄 Painel de Rotação Automática (`/aleatorio`)

**Nota:** A rota `/aleatorio` alterna entre os painéis principais. Por padrão, usa as versões temáticas configuradas.

**Status:** ✅ **Implementado** (11/11/2025)

**Funcionalidades:**
- Rotação automática entre `/` e `/metas` a cada **1 minuto**
- Sincronização via `localStorage` (key: `bn_panel_index`)
- Suporta múltiplas TVs sincronizadas
- URL param `?aleatorio=1` indica modo rotação ativo
- **Auto-unlock de áudio**: Tenta desbloquear áudio automaticamente para permitir sons de celebração
- Redirecionamento instantâneo ao acessar `/aleatorio`

### � Sistema de Celebração

Quando um deal é fechado:

1. **Animação no Painel:**
   - Card de celebração com fotos do time (EV, SDR, LDR)
   - Badges coloridos por função
   - Valor do deal e nome da empresa
   - Confetes animados
   - Som de corneta

2. **Notificação WhatsApp Automática:**
   - Imagem gerada em 1920x1080 (landscape)
   - Design idêntico ao painel de TV
   - Fotos dos analistas incluídas
   - Mensagem de texto com detalhes
   - Enviado para o grupo RevOps

3. **Notificação Push (PWA):**
   - Notificação no navegador
   - Funciona mesmo com aba fechada (via Service Worker)

### 📱 Integração WhatsApp

**Evolution API** gerencia as comunicações:

- Envio automático de imagens de celebração
- Mensagens formatadas com emojis
- Suporte a grupos do WhatsApp
- Base64 para imagens inline

**Formato da Mensagem:**
```
🎉 DEAL GANHO!

💰 Valor: R$ 1.500,00
📝 Deal: Nome do Deal

👥 Time Vencedor:
👔 EV: Marllon Rodrigues
📞 SDR: Gustavo Modesto
🎯 LDR: Bianca Aguiar

🏢 Empresa: Empresa XYZ
📅 Data: 11/11/2025 14:30

---
Black November 2025 🚀
```

### 🎯 Sistema de Webhooks

**Endpoint:** `/api/webhook/deal-won`

Recebe notificações do HubSpot quando deals são fechados:

```json
{
  "dealId": "123456",
  "dealName": "Empresa ABC - Plano Premium",
  "amount": 150000.00,
  "ownerName": "12345678",  // ID do HubSpot
  "sdrName": "87654321",    // ID do HubSpot
  "ldrName": "11223344",    // ID do HubSpot
  "companyName": "Empresa ABC",
  "closedDate": "2025-11-11"
}
```

**Processamento:**
1. Converte IDs do HubSpot para nomes (via `analistas_mapeamento.json`)
2. Salva no banco de dados PostgreSQL
3. Adiciona à fila de notificações
4. Gera imagem de celebração
5. Envia WhatsApp
6. Disponibiliza para animação no painel

### 🗄️ Banco de Dados

**Tabela: `deal_notifications`**

```sql
CREATE TABLE deal_notifications (
    id VARCHAR(255) PRIMARY KEY,
    deal_name TEXT,
    amount DECIMAL(15, 2),
    owner_name VARCHAR(255),
    sdr_name VARCHAR(255),
    ldr_name VARCHAR(255),
    company_name VARCHAR(255),
    closed_date VARCHAR(50),
    pipeline VARCHAR(100),
    deal_stage VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    viewed_by JSONB DEFAULT '[]'::jsonb
);
```

Armazena todas as notificações com controle de visualização por client_id (suporta múltiplas TVs).

## 🌐 API Endpoints

### Dados de Receita

**GET** `/api/revenue`
- Retorna receita total da Black November
- Usado pelo funil principal
- Resposta: `{total: 1234567.89, goal: 1500000, has_data: true}`

**GET** `/api/revenue/today`
- Retorna faturamento APENAS DO DIA ATUAL
- Timezone: América/São Paulo (GMT-3)
- Resposta: `{total_today: 123456.78, date: "2025-11-12"}`

**GET** `/api/revenue/until-yesterday`
- Retorna receita acumulada até ontem
- Útil para cálculos de progresso mensal

**GET** `/api/pipeline/today`
- Retorna pipeline previsto para fechar HOJE
- **Filtro corrigido**: exclui deals ganhos/perdidos/fechados
- Timezone: América/São Paulo (GMT-3)
- Resposta: `{total_deals: 11, total_pipeline: 41100.66, avg_deal_value: 3736.42, date: "2025-11-12"}`

**GET** `/api/revenue/manual-revenue/config`
- Retorna configuração de receita manual (GET)
- Permite atualizar configuração (POST)

**GET/POST** `/api/revenue/celebration-theme/config`
- Retorna/configura tema de celebração (natal/black-november)
- Resposta: `{theme: "natal"}` ou `{theme: "black-november"}`

### Rankings

**GET** `/api/top-evs-today`
- Top 5 EVs por receita do dia
- Atualizado em tempo real (a cada 30s)
- Timezone sincronizado com `/api/revenue/today`

**GET** `/api/top-sdrs-today?pipeline={id}`
- Top 5 SDRs por pipeline
- Parâmetros: `pipeline=6810518` (NEW) ou `4007305` (Expansão)

**GET** `/api/top-ldrs-today`
- Top 5 LDRs por conversão MQL → Ganho

### Hall da Fama (com Badges)

**GET** `/api/hall-da-fama/evs-realtime?use_cache={true|false}`
- Top 5 EVs com badges em tempo real
- Detecta e salva badges automaticamente
- Parâmetro `use_cache`: usar cache (padrão: false)

**GET** `/api/hall-da-fama/sdrs-realtime?pipeline={id}&use_cache={true|false}`
- Top 5 SDRs com badges por pipeline
- Parâmetros: `pipeline=6810518` (NEW) ou `4007305` (Expansão)

**GET** `/api/hall-da-fama/ldrs-realtime?use_cache={true|false}`
- Top 5 LDRs com badges em tempo real

### Badges e Conquistas

**GET** `/api/badges/user/<user_type>/<user_id>?filter={today|week|month}`
- Retorna badges de um usuário específico
- Parâmetros:
  - `user_type`: EV, SDR ou LDR
  - `user_id`: ID do HubSpot
  - `filter`: Filtro opcional por período

**GET** `/api/recordes`
- Retorna recordes da Black November
- Maior dia, maior deal, melhor streak, etc.

**GET** `/api/mvp-semana`
- Retorna MVP da semana (últimos 7 dias)
- Separa por tipo: EV, SDR, LDR

**GET** `/api/badges/stats`
- Estatísticas gerais de badges
- Total hoje, semana, por categoria, top usuários

### Destaques

**GET** `/api/destaques/evs?periodo={semana|mes}&pipeline={id}`
- Destaques de EVs por período
- Parâmetros: `periodo=semana|mes`, `pipeline=6810518|4007305`

**GET** `/api/destaques/sdrs?periodo={semana|mes}&pipeline={id}`
- Destaques de SDRs por período

**GET** `/api/destaques/ldrs?periodo={semana|mes}&pipeline={id}`
- Destaques de LDRs por período

### Notificações

**GET** `/api/deals/pending?client_id={id}&since={timestamp}`
- Retorna deals pendentes de visualização
- Parâmetros:
  - `client_id`: Identificador da TV/cliente
  - `since`: ISO 8601 timestamp para filtro incremental

**POST** `/api/deals/mark-viewed/{deal_id}?client_id={id}`
- Marca deal como visualizado
- Evita re-exibição da mesma animação

### Webhooks

**POST** `/api/webhook/deal-won`
- Recebe notificações do HubSpot
- Processa automaticamente
- Salva no banco, envia WhatsApp, gera imagem

**GET** `/api/webhook/logs`
- Retorna logs de webhooks recebidos
- Últimas 50 notificações

**GET/POST** `/api/webhook/test`
- Endpoint de teste para simular webhook
- Interface HTML para testes manuais

**GET** `/webhook-debug`
- Interface de debug para visualizar webhooks recebidos
- Página HTML com logs e notificações

### Outros Endpoints

**GET** `/api/arr`
- Retorna dados de ARR (Annual Recurring Revenue)

**GET** `/api/looker/gauge-value`
- Retorna valor do gauge do Looker Dashboard
- Requer sessão ativa (cookies salvos)

**POST** `/api/reports/send-daily-mvp-report`
- Envia relatório diário de MVP via WhatsApp
- Gera imagens e envia para grupo

**GET** `/api/debug/pool-status`
- Status do pool de conexões do banco de dados
- Útil para monitoramento e troubleshooting

## 🎨 Geração de Imagens

**Módulo:** `celebration_image_generator.py`

Usa **Playwright** para renderizar HTML/CSS como PNG:

```python
from celebration_image_generator import generate_celebration_image

deal_data = {
    'dealName': 'Empresa ABC',
    'amount': 150000.00,
    'ownerName': 'Marilon Rodrigues',
    'sdrName': 'Gustavo Modesto',
    'ldrName': 'Bianca Aguiar',
    'companyName': 'Empresa ABC'
}

image_bytes = generate_celebration_image(deal_data)
# Retorna PNG em bytes (landscape 1920x1080)
```

**Características:**
- Resolução: 1920x1080 (16:9 landscape)
- Formato: PNG (~200KB)
- CSS idêntico ao painel de TV
- Fotos dos analistas embutidas como base64
- Tempo de geração: ~2 segundos

**Sistema de Temas:**
- Suporta temas configuráveis: `'natal'` e `'black-november'`
- Configuração via endpoint: `/api/revenue/celebration-theme/config`
- Tema Natal: Inclui luzes de Natal e touca de Papai Noel
- Tema Black November: Design padrão com cores da campanha

## � Estrutura do Projeto

```
black-november/
├── app.py                               # Aplicação Flask principal
├── celebration_image_generator.py       # Gerador de imagens (Playwright)
├── test_celebration_image.py            # Script de teste (não vai para produção)
├── test_connection.py                   # Teste de conexão DB
├── test_pipeline_hubspot_vs_db.py       # Comparação HubSpot API vs Banco
├── test_query_corrigida.py              # Validação de queries SQL
├── requirements.txt                     # Dependências Python
├── Dockerfile                           # Container Docker
├── cloudbuild.yaml                      # Config Google Cloud Build
├── .dockerignore                        # Arquivos ignorados no build
├── .env                                # Variáveis de ambiente (não versionado)
│
├── data/
│   └── analistas_mapeamento.json        # Mapeamento ID HubSpot → Nome
│
├── static/
│   ├── css/
│   │   ├── funnel.css                  # Estilos do funil principal
│   │   ├── metas.css                   # Estilos do painel de metas (novo)
│   │   ├── deal_celebration.css        # Estilos da celebração
│   │   └── top_evs_ranking.css         # Estilos dos rankings
│   │
│   ├── javascript/
│   │   ├── funnel.js                   # Lógica do funil e animações
│   │   ├── metas.js                    # Lógica do painel de metas (novo)
│   │   ├── deal_celebration.js         # Lógica de celebração
│   │   └── top_evs_ranking.js          # Lógica dos rankings (slider)
│   │
│   ├── img/
│   │   ├── team/                       # Fotos dos analistas (*.png)
│   │   ├── blck_november.png           # Logo Black November
│   │   ├── bruno_megafone.png          # Bruno motivacional (novo)
│   │   ├── allan_santos.png            # CSO (boca fechada)
│   │   ├── allan_santos_boca_aberta.png
│   │   ├── roleta.png                  # Roleta
│   │   ├── ponta_roleta.png            # Ponteiro da roleta
│   │   └── ...
│   │
│   ├── media/
│   │   ├── chuva_dinheiro.mp4          # Vídeo chuva de dinheiro
│   │   ├── musica_silvio_santos.mp3
│   │   └── corneta.mp3                 # Som de celebração
│   │
│   ├── fonts/                          # Fontes customizadas
│   ├── service-worker.js               # PWA Service Worker
│   └── manifest.json                   # PWA Manifest
│
├── templates/
│   ├── funnel.html                     # Template do painel principal
│   ├── metas.html                      # Template do painel de metas (novo)
│   ├── aleatorio.html                  # Template de rotação (novo)
│   ├── funnel_demo.html                # Versão de demonstração
│   └── webhook_debug.html              # Debug de webhooks
│
├── README.md                           # Esta documentação
└── ROADMAP.md                          # Roadmap de melhorias futuras
```

## � Configuração de Analistas

Edite `data/analistas_mapeamento.json` para mapear IDs do HubSpot para nomes:

```json
{
  "12345678": "Marilon Rodrigues",
  "87654321": "Gustavo Modesto",
  "11223344": "Bianca Aguiar"
}
```

As fotos devem estar em `static/img/team/` no formato:
- `marilon_rodrigues.png`
- `gustavo_modesto.png`
- `bianca_aguiar.png`

(Nome normalizado: lowercase, sem acentos, espaços → underscore)

## 🎯 Configuração de Metas

**Meta da Black November:** R$ 1.500.000

Para alterar, edite as constantes no código:

**JavaScript** (`static/javascript/funnel.js`):
```javascript
const TARGET_VALUE = 1500000;
```

**HTML** (`templates/funnel.html`):
```html
<div class="funnel-main-value">R$ 1.500.000</div>
```

## 🐛 Troubleshooting

### Problema: Imagens não são geradas

**Causa:** Playwright/Chromium não instalado
```bash
playwright install --with-deps chromium
```

### Problema: Fotos não aparecem nas celebrações

**Causa:** Nomes normalizados incorretos
- Verifique se o arquivo existe em `static/img/team/`
- Nome deve ser: `nome_sobrenome.png` (lowercase, sem acentos)
- Exemplo: "Marilon Rodrigues" → `marilon_rodrigues.png`

### Problema: WhatsApp não envia

**Causa:** Evolution API offline ou credenciais incorretas
- Verifique `EVOLUTION_API_URL` e `EVOLUTION_API_KEY`
- Teste manualmente: `curl -H "apikey: SUA_KEY" https://seu-servidor/instance/connectionState/SUA_INSTANCIA`

### Problema: Rankings não atualizam

**Causa:** Conexão com banco PostgreSQL
- Verifique credenciais no `.env`
- Teste conexão: `python test_connection.py`

### Problema: Painel fica em branco

**Causa:** JavaScript bloqueado ou erro de CORS
- Abra DevTools (F12) e verifique console
- Certifique-se de que `/static/` está acessível
- Verifique se Service Worker foi registrado

## 📈 Monitoramento

### Logs da Aplicação

**Local:**
```bash
python app.py
# Logs aparecem no terminal
```

**Docker:**
```bash
docker logs -f black-november
```

**Cloud Run:**
```bash
gcloud logs read --service=black-november-funnel --limit=100
```

### Métricas Importantes

- Taxa de atualização dos rankings: 30 segundos
- Rotação de slides: 12 segundos
- Tempo de geração de imagem: ~2 segundos
- Tamanho médio da imagem: 200KB PNG
- Taxa de erro de webhook: < 1%

## 🔐 Segurança

- Variáveis sensíveis em `.env` (não versionado)
- API Key da Evolution protegida
- Banco com SSL habilitado
- CORS configurado apenas para domínios permitidos
- Service Worker com cache versionado

## � Estatísticas do Projeto

- **Total de linhas de código:** 7.864
  - JavaScript: 2.567 linhas (32.6%)
  - CSS: 2.380 linhas (30.3%)
  - Python: 1.671 linhas (21.3%)
  - HTML: 782 linhas (9.9%)
  - SQL: 464 linhas (5.9%)
- **Arquivos:** 25 arquivos principais
- **Tempo de desenvolvimento:** 12 dias (01/11 - 12/11/2025)
- **Deploy:** Google Cloud Run (automático via Cloud Build)

## 🐛 Troubleshooting Avançado

### Problema: Pipeline previsto com valores incorretos

**Sintoma:** Página `/metas` mostra mais deals do que deveria, incluindo deals perdidos

**Causa:** Lógica SQL com `OR` permitia deals perdidos/fechados passarem

**Solução aplicada (12/11/2025):**
```sql
-- ANTES (incorreto - usava OR):
AND (
    deal_isclosed = FALSE 
    OR deal_isclosed IS NULL
    OR (LOWER(stage_label) NOT LIKE '%ganho%' ...)
)

-- DEPOIS (correto - usa AND):
AND (deal_isclosed = FALSE OR deal_isclosed IS NULL)
AND LOWER(stage_label) NOT LIKE '%ganho%'
AND LOWER(stage_label) NOT LIKE '%faturamento%'
AND LOWER(stage_label) NOT LIKE '%aguardando%'
AND LOWER(stage_label) NOT LIKE '%perdido%'  -- NOVO!
```

**Resultado:** Redução de 70% de falsos positivos (37 → 11 deals)

**Scripts de validação:**
- `test_pipeline_hubspot_vs_db.py` - Compara HubSpot API vs Banco
- `test_query_corrigida.py` - Valida query SQL antiga vs nova

### Problema: Timezone incorreto (deals não aparecem depois das 21h)

**Causa:** Query usando `CURRENT_DATE` UTC em vez de horário de Brasília

**Solução:**
```sql
-- ANTES:
DATE(closedate - INTERVAL '3 hour') = CURRENT_DATE

-- DEPOIS:
DATE(closedate - INTERVAL '3 hour') = DATE(CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
```

## �🚀 Próximas Melhorias

Ver arquivo: `ROADMAP.md`

Próximos passos sugeridos:
- Painel 3 - Hall da Fama & Conquistas (gamificação com badges)
- Painel 4 - Timeline & Atividade ao Vivo
- Bot WhatsApp interativo com comandos
- Analytics avançados com ML

## 📞 Suporte

**Responsável:** Time de RevOps Logcomex  
**Período:** Black November 2025 (01/11 - 30/11)  
**Última atualização:** 12/11/2025

---

**Desenvolvido para a campanha Black November Logcomex 2025** 🚀

