# 🚀 Roadmap - Próximas Melhorias Black November

Este documento contém as sugestões de evolução do sistema para maximizar engajamento, gamificação e visualização de dados.

## 📊 Status Atual

### ✅ Implementado

- [x] **Painel 1 - Dashboard Principal** (`/`)
  - [x] Funil animado com gradiente dinâmico
  - [x] Sistema de rankings rotativos (4 slides: EVs, SDRs NEW, SDRs Expansão, LDRs)
  - [x] Sincronização de dados em tempo real
  - [x] Layout responsivo e TV-friendly
  - [x] CSO Allan Santos com animação de boca
  - [x] Chuva de dinheiro e roleta
  
- [x] **Painel 2 - Dashboard de Metas & Progresso** (`/metas`) ✅ CONCLUÍDO (12/11/2025)
  - [x] Meta do dia dinâmica (R$ 107.142,86)
  - [x] Barra de progresso gigante com cores dinâmicas
  - [x] Pipeline previsto em tempo real
  - [x] Status inteligente (Crítico/Acelerar/No Caminho)
  - [x] Timezone corrigido (GMT-3)
  - [x] **CORREÇÃO CRÍTICA**: Lógica SQL de filtros (OR → AND)
  - [x] Filtro de deals perdidos/churn adicionado
  - [x] Redução de 70% de falsos positivos (37 → 11 deals)
  - [x] Contagem regressiva até fim do dia
  - [x] Cards de estatísticas do mês
  - [x] Imagem motivacional (Bruno megafone)
  
- [x] **Sistema de Rotação Automática** (`/aleatorio`) ✅ IMPLEMENTADO (11/11/2025)
  - [x] Rotação entre painéis a cada 1 minuto
  - [x] Sincronização via localStorage
  - [x] Suporte a múltiplas TVs
  - [x] Auto-unlock de áudio para celebrações
  - [x] URL param `?aleatorio=1` para controle
  
- [x] **Infraestrutura e Integrações**
  - [x] Integração com HubSpot via webhooks
  - [x] Celebrações automáticas com animações
  - [x] Notificações WhatsApp com imagens geradas (1920x1080)
  - [x] PWA com notificações push
  - [x] Banco de dados PostgreSQL Cloud SQL para persistência
  - [x] Deploy automatizado no Google Cloud Run
  - [x] Sistema de múltiplas TVs (controle por `client_id`)
  - [x] Correção de timezone em todas as queries (América/São Paulo)
  - [x] Scripts de teste e validação (HubSpot vs Banco)

---

## ✅ Fase 1 - Painel 2: Dashboard de Metas & Progresso (ENTREGUE)

**Status:** ✅ 100% implementado e validado em produção  
**Data de conclusão:** 12/11/2025

### Funcionalidades Implementadas
- ✅ Barra de progresso gigante e responsiva, com cores dinâmicas (crítico, atenção, perto, meta batida)
- ✅ Exibição da meta do dia, valor atual, valor faltante e pipeline previsto (com número de deals)
- ✅ Progresso em tempo real (atualiza a cada 30s)
- ✅ Contagem regressiva até o fim do dia (24h, considera trabalho além do expediente)
- ✅ Cálculo de dias úteis restantes (considerando feriados: 20/11 Consciência Negra)
- ✅ Ritmo atual: média/hora e projeção do dia (faturado + pipeline previsto)
- ✅ Status inteligente: considera tempo restante, progresso real e projeção (🚨 Crítico, ⚡ Acelerar, ✅ No Caminho)
- ✅ Cards de estatísticas do mês (faturado, meta, falta, dias úteis)
- ✅ Pipeline previsto busca apenas deals com previsão de fechamento hoje e ainda não ganhos
- ✅ Correção de timezone: sempre considera horário de Brasília (GMT-3) em todas as queries
- ✅ Imagem motivacional fixa no canto inferior direito (bruno_megafone.png)
- ✅ Layout 100% TV-friendly, sem scroll, responsivo

### Endpoints/API
- ✅ `/api/revenue` — Faturamento acumulado do mês
- ✅ `/api/revenue/today` — Faturamento do dia (timezone Brasil)
- ✅ `/api/pipeline/today` — Pipeline previsto para fechar hoje (timezone Brasil)

### Lógica/SQL
- **Faturado hoje**: `deals` ganhos hoje, excluindo receitas pontuais e variação cambial
  - Timezone: `DATE(closedate - INTERVAL '3 hour') = DATE(CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')`
  - Stage: ganho/faturamento/aguardando
  - Coluna usada: `valor_ganho`
  
- **Pipeline previsto**: `deals` com closedate hoje, ainda não ganhos
  - Timezone: `DATE(closedate - INTERVAL '3 hour') = DATE(CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')`
  - **Filtros CORRIGIDOS (12/11/2025)**:
    - `(deal_isclosed = FALSE OR deal_isclosed IS NULL)`
    - `AND LOWER(stage_label) NOT LIKE '%ganho%'`
    - `AND LOWER(stage_label) NOT LIKE '%faturamento%'`
    - `AND LOWER(stage_label) NOT LIKE '%aguardando%'`
    - `AND LOWER(stage_label) NOT LIKE '%perdido%'` ← **NOVO!**
  - Coluna usada: `amount`
  - **Resultado**: Redução de 37 para 11 deals (-70% falsos positivos)
  
- **Dias úteis**: Sábados, domingos e feriados (20/11) excluídos
- **Projeção**: Faturado hoje + Pipeline previsto hoje

### Frontend
- ✅ `templates/metas.html` — Estrutura da página (144 linhas)
- ✅ `static/css/metas.css` — Estilos otimizados para TV (595 linhas)
- ✅ `static/javascript/metas.js` — Lógica de atualização (271 linhas)
- ✅ Imagem: `static/img/bruno_megafone.png` posicionada, grande, atrás da faixa roxa

### Backend
- ✅ `app.py` - Funções `get_today_revenue()` e `get_pipeline_today()`
- ✅ Debug logs para troubleshooting
- ✅ Mesma lógica de timezone aplicada em todas as queries

### Correções e Melhorias Aplicadas
1. ✅ **Correção de Timezone**: Todas as queries agora usam `DATE(CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')` para garantir consistência (resolveu problema de deals não aparecerem depois das 21h)
2. ✅ **Feriado Nacional**: 20/11 (Dia da Consciência Negra) incluído nos dias não úteis
3. ✅ **Campo Correto**: Pipeline previsto usa `closedate` (data de fechamento prevista), não mais `data_prevista_reuniao` (data da reunião)
4. ✅ **Sincronização com Ranking**: Corrigido endpoint `/api/top-evs-today` para usar mesma lógica de timezone e filtros da página de metas (valores agora batem!)
5. ✅ **Layout Otimizado**: Cards aumentados, grid de 3 colunas no progress-info, tamanhos ajustados para TV
6. ✅ **Status Realista**: Lógica inteligente que considera hora do dia, progresso esperado e projeção
7. ✅ **CORREÇÃO CRÍTICA (12/11/2025)**: Lógica SQL de filtros do pipeline previsto
   - **Problema identificado**: Lógica `OR` permitia deals perdidos/fechados passarem no filtro
   - **Solução implementada**: Mudou para `AND` e adicionou `NOT LIKE '%perdido%'`
   - **Impacto**: Redução de 70% de falsos positivos (de 37 para 11 deals, de R$ 115k para R$ 41k)
   - **Validação**: Scripts criados para comparar HubSpot API vs Banco (divergência agora < 10%)
   - **Deploy**: Corrigido em produção (app.py + test_pipeline_hubspot_vs_db.py)

### Testes/Validação
- ✅ Testado com diferentes horários (antes/depois das 21h UTC = meia-noite Brasil)
- ✅ Debug SQL implementado para rastrear deals encontrados
- ✅ Valores validados contra ranking de EVs - dados consistentes
- ✅ Validação visual em ambiente real (TV)
- ✅ Timezone verificado em produção
- ✅ **Script de comparação HubSpot vs Banco** (`test_pipeline_hubspot_vs_db.py`):
  - Compara pipeline previsto entre HubSpot API e PostgreSQL
  - Identifica divergências e deals fora de sincronia
  - Valida filtros de stage_label (ganho/perdido/fechado)
  - Resultado: 9 deals HubSpot vs 11 banco (divergência < 10% ✅)
- ✅ **Script de validação SQL** (`test_query_corrigida.py`):
  - Compara query antiga (OR) vs nova (AND)
  - Validou redução de 37 → 11 deals (-70%)
  - Confirmou correção em produção

---

## 🏆 Fase 2 - Painel 3: Hall da Fama & Conquistas

**Prioridade:** MÉDIA  
**Tempo estimado:** 2-3 dias  
**Impacto:** ALTO (gamificação + reconhecimento)

### Objetivos

Sistema completo de **gamificação** com badges, conquistas e reconhecimento público para aumentar engajamento.

> **Nota:** Este painel será exibido em **rotação automática** nas 3 TVs do escritório, alternando com os outros painéis a cada 2 minutos.

### Layout Proposto

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│            👑 MVP DA SEMANA 👑                          │
│                                                         │
│     ┌───────────────────────────────────┐              │
│     │                                    │              │
│     │     [FOTO GRANDE 400x400]          │              │
│     │                                    │              │
│     │       BIANCA AGUIAR                │              │
│     │                                    │              │
│     │   💰 R$ 420.000 | 15 deals         │              │
│     │   📈 Média: R$ 28k por deal        │              │
│     │                                    │              │
│     └───────────────────────────────────┘              │
│                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                         │
│  🏆 CONQUISTAS DESBLOQUEADAS HOJE                       │
│                                                         │
│  ✨ HAT TRICK                                           │
│     Marilon Rodrigues - 3 deals em 1 dia              
- Visualização clara da trajetória do dia
- Biblioteca: Chart.js ou similar

### Endpoints Necessários

**Backend** (`app.py`):

```python
@app.route('/api/meta-do-dia', methods=['GET'])
def get_meta_do_dia():
    """
    Retorna:
    - Meta do dia
    - Receita atual
    - Porcentagem
    - Tempo restante
    - Projeção
    - Hot streaks
    """
    pass

@app.route('/api/evolucao-hora', methods=['GET'])
def get_evolucao_hora():
    """
    Retorna array:
    [
      {hora: "09:00", receita: 45000},
      {hora: "10:00", receita: 89000},
      ...
    ]
    """
    pass
```

### Arquivos a Criar

```
templates/
  └── metas.html              # Nova página da TV 2

static/
  ├── css/
  │   └── metas.css           # Estilos da página de metas
  └── javascript/
      └── metas.js            # Lógica de metas e gráficos
```

### Critérios de Sucesso

- ✅ Barra de progresso visível de longe (TV)
- ✅ Atualização em tempo real (< 30s)
- ✅ Hot streaks detectados automaticamente
- ✅ Gráfico responsivo e legível
- ✅ Cores impactantes e motivacionais

---

## 🏆 Fase 2 - Painel 3: Hall da Fama & Conquistas

**Prioridade:** MÉDIA  
**Tempo estimado:** 2-3 dias  
**Impacto:** ALTO (gamificação + reconhecimento)

### Objetivos

Sistema completo de **gamificação** com badges, conquistas e reconhecimento público para aumentar engajamento.

> **Nota:** Este painel será exibido em **rotação automática** nas 3 TVs do escritório, alternando com os outros painéis a cada 2 minutos.

### Layout Proposto

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│            👑 MVP DA SEMANA 👑                          │
│                                                         │
│     ┌───────────────────────────────────┐              │
│     │                                    │              │
│     │     [FOTO GRANDE 400x400]          │              │
│     │                                    │              │
│     │       BIANCA AGUIAR                │              │
│     │                                    │              │
│     │   💰 R$ 420.000 | 15 deals         │              │
│     │   📈 Média: R$ 28k por deal        │              │
│     │                                    │              │
│     └───────────────────────────────────┘              │
│                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                         │
│  🏆 CONQUISTAS DESBLOQUEADAS HOJE                       │
│                                                         │
│  ✨ HAT TRICK                                           │
│     Marilon Rodrigues - 3 deals em 1 dia               │
│                                                         │
│  ⚡ SPEED DEMON                                         │
│     Gustavo Modesto - Deal fechado em < 1 hora         │
│                                                         │
│  💎 BIG FISH                                            │
│     Bianca Aguiar - Deal acima de R$ 100k              │
│                                                         │
│  🎯 SNIPER                                              │
│     Adolfo Monteiro - 5 deals > R$ 50k                 │
│                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                         │
│  📜 RECORDES DA BLACK NOVEMBER 2025                     │
│                                                         │
│  • Maior dia: R$ 687.000 (07/11) - Marilon             │
│  • Maior deal: R$ 180.000 (10/11) - Adolfo             │
│  • Melhor streak: 5 deals (08/11) - Marilon            │
│  • Mais deals 1 dia: 8 deals (09/11) - Gustavo         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Sistema de Badges/Conquistas

#### Conquistas de Volume

| Badge | Nome | Requisito |
|-------|------|-----------|
| 🥉 | **First Blood** | Primeiro deal do dia |
| 🥈 | **Double Kill** | 2 deals em 1 dia |
| 🥇 | **Hat Trick** | 3 deals em 1 dia |
| 🏆 | **Unstoppable** | 5+ deals em 1 dia |
| 👑 | **Godlike** | 10+ deals em 1 dia |

#### Conquistas de Valor

| Badge | Nome | Requisito |
|-------|------|-----------|
| 💰 | **Big Fish** | Deal > R$ 100k |
| 💎 | **Whale Hunter** | Deal > R$ 200k |
| 👔 | **Suit Up** | R$ 500k acumulado na semana |
| 🚀 | **To The Moon** | R$ 1M acumulado no mês |

#### Conquistas de Velocidade

| Badge | Nome | Requisito |
|-------|------|-----------|
| ⚡ | **Speed Demon** | Deal fechado em < 1 hora |
| 🏃 | **Flash** | 3 deals em < 3 horas |
| ⏱️ | **Early Bird** | Deal antes das 10h |
| 🌙 | **Night Owl** | Deal depois das 17h |

#### Conquistas de Precisão

| Badge | Nome | Requisito |
|-------|------|-----------|
| 🎯 | **Sniper** | 5 deals consecutivos > R$ 50k |
| 🔥 | **On Fire** | 3 deals seguidos sem intervalo > 2h |
| 💯 | **Perfect Week** | 100% da meta semanal |

### Rotação de Conteúdo

A TV 3 deve alternar a cada **20 segundos** entre:
1. MVP da Semana (foto grande)
2. Conquistas Desbloqueadas Hoje
3. Recordes da Black November

### Funcionalidades

#### 1. Sistema de Detecção Automática
- Backend analisa deals fechados
- Detecta padrões que correspondem a badges
- Notifica quando badge é desbloqueado

#### 2. Notificação de Conquista
- Quando badge é desbloqueado:
  - Animação especial no painel
  - Mensagem no WhatsApp
  - Notificação push

#### 3. Histórico de Conquistas
- Banco de dados registra todas as badges
- Cada analista tem perfil de conquistas
- Consulta via API

### Endpoints Necessários

```python
@app.route('/api/badges/check', methods=['POST'])
def check_badges():
    """Verifica se algum badge foi desbloqueado"""
    pass

@app.route('/api/badges/user/<user_id>', methods=['GET'])
def get_user_badges(user_id):
    """Retorna badges de um usuário"""
    pass

@app.route('/api/recordes', methods=['GET'])
def get_recordes():
    """Retorna recordes da Black November"""
    pass

@app.route('/api/mvp-semana', methods=['GET'])
def get_mvp_semana():
    """Retorna MVP da semana"""
    pass
```

### Tabela do Banco

```sql
CREATE TABLE badges_desbloqueados (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(255),
    badge_name VARCHAR(100),
    badge_type VARCHAR(50),
    deal_id VARCHAR(255),
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context JSONB
);
```

### Arquivos a Criar

```
templates/
  └── hall_da_fama.html       # TV 3

static/
  ├── css/
  │   └── hall_da_fama.css
  ├── javascript/
  │   └── hall_da_fama.js
  └── img/
      └── badges/
          ├── hat_trick.png
          ├── big_fish.png
          ├── speed_demon.png
          └── ... (outros badges)
```

---

## ⏱️ Fase 3 - Painel 4: Timeline & Atividade ao Vivo

**Prioridade:** MÉDIA  
**Tempo estimado:** 1-2 dias  
**Impacto:** MÉDIO (transparência + momentum)

### Objetivos

Mostrar **timeline de deals** em tempo real e criar senso de **momentum** constante.

> **Nota:** Este painel será exibido em **rotação automática** nas 3 TVs do escritório, alternando com os outros painéis a cada 2 minutos.

### Layout Proposto

```
┌─────────────────────────────────────────────────────────┐
│  ⏰ TIMELINE DO DIA - Black November                    │
│                                                         │
│  14:32  💰 Gustavo Modesto fechou R$ 45.000 ✅         │
│         Empresa: TechCorp Brasil                        │
│                                                         │
│  14:18  💰 Marilon Rodrigues fechou R$ 28.000 ✅        │
│         Empresa: LogiSmart Solutions                    │
│                                                         │
│  13:55  💰 Bianca Aguiar fechou R$ 67.000 ✅            │
│         Empresa: DataFlow Analytics                     │
│                                                         │
│  13:12  💰 Adolfo Monteiro fechou R$ 92.000 ✅          │
│         Empresa: CloudSync Enterprise                   │
│                                                         │
│  12:48  💰 Marilon Rodrigues fechou R$ 33.000 ✅        │
│         Empresa: SmartChain Logistics                   │
│                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                         │
│  📊 ESTATÍSTICAS EM TEMPO REAL                          │
│                                                         │
│  • ⏱️ Último deal: há 14 minutos                        │
│  • 📈 Média entre deals: 32 minutos                     │
│  • 🎲 Próximo esperado: em ~18 minutos                  │
│  • 🔥 Deals hoje: 23 fechados                           │
│  • 💰 Ticket médio: R$ 38.500                           │
│                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                         │
│  💬 MOTIVAÇÃO DO MOMENTO                                │
│                                                         │
│  "Faltam só R$ 124k para a meta! 🎯                     │
│   Vamos fechar mais 4 deals e batemos o recorde! 🚀"   │
│                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                         │
│  ⏱️ CONTAGEM REGRESSIVA PARA FIM DO EXPEDIENTE          │
│                                                         │
│            05:23:45                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Funcionalidades

#### 1. Timeline Automática
- Scroll automático (novos deals aparecem no topo)
- Limite de 10 deals mais recentes
- Auto-refresh a cada 10 segundos

#### 2. Cálculo de Previsões
- Média de tempo entre deals
- Projeção de próximo deal
- Baseado em histórico do dia

#### 3. Mensagens Motivacionais Dinâmicas
- Troca a cada 30 segundos
- Contextuais:
  - Perto da meta: "Só mais R$ XXk!"
  - Longe da meta: "Vamos acelerar!"
  - Meta batida: "RECORDE! Continue assim!"

#### 4. Contagem Regressiva
- Até 18h (fim do expediente)
- Formato: HH:MM:SS
- Atualiza a cada segundo

---

## 🤖 Fase 4 - Bot WhatsApp Inteligente

**Prioridade:** ALTA 🔥  
**Tempo estimado:** 2-3 dias  
**Impacto:** MUITO ALTO (interatividade + engajamento)

### Objetivos

Bot interativo no grupo WhatsApp que responde a comandos quando **mencionado**, sem poluir o grupo.

### Sistema de Menção

O bot **só responde** quando for explicitamente chamado:

```
# ✅ Bot RESPONDE
@BlackNovemberBot /ranking
@BNBot metas
!bn streak
/bn proximo

# ❌ Bot IGNORA
Alguém viu o relatório?
Marilon fechou outro deal!
```

### Comandos Disponíveis

#### `/ranking` ou `/top`
```
🏆 TOP 5 DO DIA - EVs

1º 🥇 Marilon - R$ 145.000 (5 deals)
2º 🥈 Bianca - R$ 132.000 (4 deals)
3º 🥉 Gustavo - R$ 98.000 (3 deals)
4º Adolfo - R$ 76.000 (2 deals)
5º Paulo - R$ 54.000 (2 deals)

Atualizado às 14:35 ⏰
```

#### `/meta` ou `/goal`
```
🎯 META DO DIA

💰 Atual: R$ 312.000 (62.4%)
🎯 Meta: R$ 500.000
📊 Faltam: R$ 188.000

⏱️ Tempo restante: 5h 23min
📈 Projeção: R$ 487.000 ⚠️

Status: ACELERAR! ⚡
```

#### `/streak` ou `/sequencia`
```
🔥 HOT STREAKS

1º 🔥🔥🔥 Marilon - 3 deals seguidos
   Última 2h 14min

2º 🔥🔥 Bianca - 2 deals seguidos
   Última 47min

3º 🔥 Gustavo - 2 deals seguidos
   Última 1h 05min
```

#### `/eu` ou `/stats`
```
📊 SUAS ESTATÍSTICAS - Marilon

💰 Hoje:
   • R$ 145.000 (5 deals)
   • Ticket médio: R$ 29.000
   • Posição: #1 🥇

📅 Esta Semana:
   • R$ 687.000 (24 deals)
   • Ticket médio: R$ 28.625
   
🏆 Badges Desbloqueados:
   • Hat Trick ✨
   • Big Fish 💎
   • Speed Demon ⚡
```

#### `/proximo` ou `/next`
```
⏰ PREVISÃO PRÓXIMO DEAL

• Último deal: há 18 min
• Média entre deals: 32 min
• Próximo esperado: em ~14 min

📈 Ritmo está BOM! Continue assim! 🚀
```

#### `/tv` ou `/paineis`
```
📺 STATUS DAS TVs

TV 1 - Dashboard Principal ✅
   • Funil + Rankings
   • Última atualização: 14:35

TV 2 - Metas & Progresso ✅
   • Meta do dia visível
   • Hot streaks ativos

TV 3 - Hall da Fama ✅
   • MVP: Bianca Aguiar
   • 3 badges desbloqueados hoje

TV 4 - Timeline ✅
   • 23 deals hoje
   • Último deal: há 18 min
```

#### `/ajuda` ou `/help`
```
🤖 BLACK NOVEMBER BOT

Me mencione + comando:

📊 Rankings & Stats:
  /ranking - Top 5 do dia
  /eu - Suas estatísticas
  /streak - Sequências quentes

🎯 Metas:
  /meta - Progresso da meta
  /proximo - Próximo deal previsto

📺 Sistema:
  /tv - Status dos painéis
  /ajuda - Esta mensagem

Exemplo: @BNBot /ranking
```

### Resumos Automáticos (Sem Menção)

Bot envia mensagens programadas (não precisa mencionar):

#### 09:00 - Bom Dia
```
☀️ BOM DIA, TIME!

🎯 Meta de hoje: R$ 500.000
📅 Dia 11/30 da Black November

Vamos com tudo! 🚀
```

#### 12:00 - Meio-dia
```
🍽️ MEIO-DIA! HORA DO ALMOÇO

📊 Progresso até agora:
   • R$ 156.000 (31.2%)
   • 7 deals fechados
   • Faltam R$ 344.000

Ritmo: BOM! Continue assim depois do almoço! 💪
```

#### 18:00 - Relatório do Dia
```
📊 RELATÓRIO BLACK NOVEMBER - 11/11/2025

💰 RESULTADO DO DIA
   Total: R$ 523.000 (104.6% da meta!) ✅
   Deals: 23 fechados
   Ticket médio: R$ 22.739

🏆 TOP 3 DO DIA
   🥇 Marilon - R$ 145.000 (5 deals)
   🥈 Bianca - R$ 132.000 (4 deals)
   🥉 Gustavo - R$ 98.000 (3 deals)

🔥 DESTAQUES
   • Maior deal: R$ 92k (Adolfo)
   • Melhor streak: 3 deals (Marilon)
   • Meta batida! 🎉

📈 ACUMULADO DO MÊS
   Total: R$ 3.542.000
   Faltam: R$ 958.000 para meta mensal

Parabéns, time! 🚀
```

### Implementação Técnica

#### 1. Webhook da Evolution API

```python
@app.route('/api/whatsapp/message', methods=['POST'])
def handle_whatsapp_message():
    """
    Recebe TODAS as mensagens do grupo
    Filtra e processa apenas se bot for mencionado
    """
    data = request.json
    message_text = data.get('message', {}).get('text', '')
    sender_name = data.get('senderName', '')
    sender_number = data.get('sender', '')
    
    # Aliases do bot
    BOT_MENTIONS = [
        '@BlackNovemberBot',
        '@BNBot',
        '@Bot',
        '!bn',
        '/bn'
    ]
    
    # Verifica menção
    if not any(m.lower() in message_text.lower() for m in BOT_MENTIONS):
        return jsonify({'status': 'ignored'}), 200
    
    # Remove menção e processa comando
    command = extract_command(message_text, BOT_MENTIONS)
    response = process_command(command, sender_name)
    
    # Envia resposta
    send_whatsapp_text(response)
    
    return jsonify({'status': 'success'}), 200
```

#### 2. Comandos Agendados (Cron)

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=9, minute=0)
def morning_message():
    send_whatsapp_text(get_morning_message())

@scheduler.scheduled_job('cron', hour=12, minute=0)
def noon_message():
    send_whatsapp_text(get_noon_message())

@scheduler.scheduled_job('cron', hour=18, minute=0)
def evening_report():
    send_whatsapp_text(get_evening_report())
    send_whatsapp_image(generate_daily_report_image())

scheduler.start()
```

#### 3. Detecção de Usuário

```python
def detect_user_from_message(sender_name, sender_number):
    """
    Tenta identificar qual analista enviou a mensagem
    Usa mapeamento de números de telefone
    """
    # Mapeamento em data/whatsapp_users.json
    users = load_whatsapp_users_mapping()
    return users.get(sender_number, sender_name)
```

### Arquivos Necessários

```
data/
  └── whatsapp_users.json     # Mapeamento número → nome analista

# Adicionar ao requirements.txt
apscheduler>=3.10.0
```

---

## 📊 Fase 5 - Analytics Avançados

**Prioridade:** BAIXA  
**Tempo estimado:** 3-5 dias  
**Impacto:** MÉDIO (insights estratégicos)

### Machine Learning Simples

#### 1. Previsão de Meta
- Modelo linear baseado em histórico
- Considera dia da semana
- Ajusta por feriados

#### 2. Heatmap de Produtividade
- Horários com mais deals
- Dias da semana mais produtivos
- Insights para estratégia

#### 3. Análise de Tendências
- Crescimento/queda de performance
- Comparação semana a semana
- Alertas de desaceleração

---

## 🎯 Matriz de Priorização

| Fase | Feature | Impacto | Esforço | Prioridade | Status |
|------|---------|---------|---------|------------|--------|
| 0 | Sistema de Rotação + Celebração Modal | ⭐⭐⭐⭐⭐ | 🔨 | 🔥 URGENTE | 📋 Planejado |
| 1 | Painel 2 - Metas | ⭐⭐⭐⭐⭐ | 🔨🔨 | 🔥 URGENTE | ✅ CONCLUÍDO |
| 4 | Bot WhatsApp | ⭐⭐⭐⭐⭐ | 🔨🔨🔨 | 🔥 URGENTE | 📋 Planejado |
| 2 | Painel 3 - Hall da Fama | ⭐⭐⭐⭐ | 🔨🔨🔨 | 🟡 ALTA |
| 3 | Painel 4 - Timeline | ⭐⭐⭐ | 🔨🔨 | 🟢 MÉDIA |
| 5 | Analytics ML | ⭐⭐ | 🔨🔨🔨🔨 | 🔵 BAIXA |

---

## 📅 Cronograma (Atualizado)

**Semana 1:** 11/11 - 15/11
- ✅ **Dia 1-2** (11-12/11): Painel 2 - Metas & Progresso **[CONCLUÍDO]**
  - Implementação completa
  - Correção de timezone
  - Sincronização com ranking de EVs
  - Validação em produção
  - **CORREÇÃO CRÍTICA**: Lógica SQL de filtros (redução de 70% de falsos positivos)
  - Scripts de teste e validação criados
  - Deploy em produção com todas as correções

- ✅ **Dia 2** (11/11): Sistema de rotação automática **[IMPLEMENTADO]**
  - Rota `/aleatorio` com rotação de 1 minuto
  - Sincronização via localStorage
  - Auto-unlock de áudio
  
**Próximos Passos:**
- 🔜 Componente modal universal de celebração + SSE (opcional)
- 🔜 Bot WhatsApp com comandos básicos (Fase 4)

**Semana 2:** 18/11 - 22/11
- 📋 Dia 1-3: Painel 3 - Hall da Fama & Badges (gamificação)
- 📋 Dia 4-5: Painel 4 - Timeline & Atividade ao Vivo

**Semana 3:** 25/11 - 29/11
- 📋 Bot WhatsApp interativo (comandos e relatórios)
- 📋 Analytics avançados (se houver tempo)
- 📋 Ajustes finais e otimizações

## 🚨 Fase 0 - Sistema de Rotação + Celebração Universal

**Prioridade:** CRÍTICA 🔥🔥🔥  
**Tempo estimado:** 1 dia  
**Impacto:** ALTÍSSIMO (base para todas as outras fases)

### Por que fazer primeiro?

Antes de criar os novos painéis, precisamos da **infraestrutura** que permite:
1. Rotacionar entre os painéis automaticamente
2. Sincronizar as 3 TVs
3. Celebrações aparecerem em qualquer painel

### Tarefas

#### 1. Sistema de Rotação Automática (4 horas)
- JavaScript para rotação de painéis
- Sincronização via timestamp no localStorage
- Transições suaves entre painéis
- Controle manual opcional (query param `?norotate=true` para debug)

#### 2. Componente Modal Universal (4 horas)
- Arquivo `celebration_modal.js` incluído em todos os painéis
- CSS do modal responsivo e impactante
- Animações de entrada/saída
- Confetes e efeitos visuais

#### 3. Server-Sent Events (SSE) (2 horas)
- Endpoint `/api/events/deals` no backend
- Todas as TVs conectam ao SSE
- Quando deal é fechado, backend envia evento para TODAS as conexões
- Frontend recebe e dispara modal

#### 4. Integração com Sistema Atual (2 horas)
- Modificar `funnel.html` para incluir modal
- Testar celebração em tempo real
- Garantir que não quebra funcionalidades existentes

---

## 🔧 Notas de Implementação

### Sistema de Rotação de Painéis

**Arquitetura:**
- **3 TVs físicas** no escritório
- Cada TV exibe **todos os 4 painéis** em rotação automática
- Rotação automática a cada **2 minutos** (120 segundos)
- Todas as 3 TVs **sincronizadas** (mostram o mesmo painel ao mesmo tempo)

**Estrutura:**

```
Painel 1: Dashboard Principal (/) 
  ├── Funil animado
  ├── Meta R$ 1.500.000
  └── Ranking rotativo (EVs, SDRs NEW, SDRs Expansão, LDRs)

Painel 2: Metas & Progresso (/metas)
  ├── Barra de progresso gigante
  ├── Contagem regressiva
  ├── Hot streaks
  └── Gráfico evolução hora

Painel 3: Hall da Fama (/hall-da-fama)
  ├── MVP da semana (foto grande)
  ├── Badges desbloqueados hoje
  └── Recordes da Black November

Painel 4: Timeline (/timeline)
  ├── Feed de deals em tempo real
  ├── Estatísticas do dia
  └── Mensagens motivacionais
```

**Rotação Automática:**

```javascript
// Lógica de rotação (a ser implementada)
const paineis = ['/', '/metas', '/hall-da-fama', '/timeline'];
let currentIndex = 0;
const ROTATION_INTERVAL = 120000; // 2 minutos

function rotatePanel() {
  currentIndex = (currentIndex + 1) % paineis.length;
  window.location.href = paineis[currentIndex];
}

setInterval(rotatePanel, ROTATION_INTERVAL);
```

### Sistema de Celebração Universal

**CRÍTICO:** A celebração de deals ganhos deve aparecer **em todas as TVs simultaneamente**, independente de qual painel está sendo exibido no momento.

**Implementação:**
1. **Modal Universal** - Componente JavaScript incluído em TODOS os painéis
2. **Server-Sent Events (SSE)** - Notificação em tempo real para todas as conexões
3. **Sincronização** - Todas as 3 TVs recebem e exibem a celebração ao mesmo tempo
4. **Overlay** - Modal aparece sobre qualquer painel (não interrompe rotação)

```javascript
// Componente celebration_modal.js (incluído em todos os painéis)
// Quando deal é fechado:
// 1. Backend envia evento SSE → todas as TVs
// 2. Modal de celebração aparece (10 segundos)
// 3. Modal fecha automaticamente
// 4. Rotação de painéis continua normalmente
```

### Sincronização Entre TVs

Todas as 3 TVs devem:
- Mostrar o **mesmo painel** ao **mesmo tempo** (rotação sincronizada)
- Receber **celebrações simultaneamente** via SSE
- Atualizar dados em **tempo real** (< 30 segundos)
- Compartilhar mesmo `client_id` por localização física

---

## 📝 Changelog Recente

### 12/11/2025 - Correção Crítica de Filtros SQL
- 🐛 **BUG CORRIGIDO**: Lógica SQL com `OR` permitia deals perdidos/fechados no pipeline previsto
- ✅ **SOLUÇÃO**: Mudou para `AND` e adicionou filtro `NOT LIKE '%perdido%'`
- 📊 **IMPACTO**: Redução de 70% de falsos positivos (37 → 11 deals, R$ 115k → R$ 41k)
- 🧪 **VALIDAÇÃO**: Scripts de teste criados (`test_pipeline_hubspot_vs_db.py`, `test_query_corrigida.py`)
- 🚀 **DEPLOY**: Correção em produção via Cloud Build
- 📈 **RESULTADO**: Divergência HubSpot vs Banco agora < 10% (9 vs 11 deals)

### 11/11/2025 - Sistema de Rotação Automática
- ✅ Implementado rota `/aleatorio` com rotação de 1 minuto
- ✅ Sincronização via localStorage entre múltiplas TVs
- ✅ Auto-unlock de áudio para celebrações
- ✅ Suporte a URL param `?aleatorio=1`

### 11/11/2025 - Painel 2 - Metas & Progresso
- ✅ Implementação completa do painel de metas
- ✅ Correção de timezone para horário de Brasília (GMT-3)
- ✅ Sincronização com ranking de EVs
- ✅ Status inteligente baseado em tempo e projeção
- ✅ Contagem regressiva e cards de estatísticas

---

**Última atualização:** 12/11/2025  
**Status:** ✅ Fase 1 concluída | 📋 Fase 2-5 planejadas
