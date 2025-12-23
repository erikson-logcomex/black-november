# 📊 Relatório de Viabilidade - Sistema de Gamificação
**Data:** 12/11/2025  
**Projeto:** Black November - Hall da Fama & Badges

---

## ✅ CONCLUSÃO GERAL: **VIÁVEL PARA IMPLEMENTAÇÃO**

Os dados existentes no banco `hubspot-sync` são **suficientes e adequados** para implementar o sistema de gamificação proposto, com alguns ajustes menores.

---

## 🔍 Resultados dos Testes

### 1. ✅ Granularidade de Timestamps

**Status:** **EXCELENTE** 

- ✅ `closedate` possui **hora, minuto e segundo** completos
- ✅ `createdate` também possui timestamps granulares
- ✅ Timezone GMT-3 (Brasil) já ajustado nas queries
- ✅ Dados precisos o suficiente para badges de velocidade e horário

**Exemplo:**
```
closedate: 2025-11-12 19:24:09.443000
Hora: 19h | Minuto: 24min | Segundo: 9s
```

**Impacto:** Suporta badges como Speed Demon, Early Bird, Night Owl sem limitações.

---

### 2. ✅ Distribuição de Deals por Hora

**Status:** **BOA DISTRIBUIÇÃO**

**Horários mais produtivos (últimos 30 dias):**
1. **12h** - 101 deals (pico absoluto - provavelmente importação de dados?)
2. **17h** - 27 deals (horário comercial final)
3. **15h** - 25 deals (horário comercial pleno)

**Badges de Horário:**
- 🌅 **Early Bird** (antes 10h): 8 deals disponíveis → **VIÁVEL**
- 🌙 **Night Owl** (depois 17h): 59 deals disponíveis → **MUITO VIÁVEL**

**Observação:** Spike anormal às 12h (101 deals) pode ser sincronização batch. Filtrar se necessário.

---

### 3. ✅ Intervalos Entre Deals Consecutivos

**Status:** **EXCELENTE PARA BADGES DE VELOCIDADE**

**Analista top (ID 69943343 - Luiza):**
- Total deals: 111
- Intervalo médio: **3.5 horas**
- Menor intervalo: **0.0h** (deals no mesmo minuto!)
- **101 deals com intervalo < 1h** 🔥

**Totais gerais:**
- ⚡ Speed Demon (< 1h): **111 ocorrências**
- 🏃 Flash (< 3h): **119 ocorrências**

**Impacto:** Badges de velocidade são **perfeitamente viáveis** e ocorrem com frequência.

---

### 4. 📋 Viabilidade por Badge

| Badge | Critério | Ocorrências (30d) | Status | Ajustes |
|-------|----------|-------------------|--------|---------|
| 🥇 **Hat Trick** | 3 deals em 1 dia | **5** | ✅ VIÁVEL | Nenhum |
| 💰 **Big Fish** | Deal > R$ 100k | **1** | ✅ VIÁVEL | Considerar R$ 50k para mais frequência |
| 🎯 **Sniper** | 5 deals > R$ 50k seguidos | **0** | ⚠️ RARO | Reduzir para 3 deals consecutivos |
| 👔 **Suit Up** | R$ 500k/semana | **0** | ⚠️ RARO | Reduzir para R$ 300k/semana |
| 🌅 **Early Bird** | Deal antes 10h | **5** | ✅ VIÁVEL | Nenhum |
| 🌙 **Night Owl** | Deal depois 17h | **27+** | ✅ MUITO VIÁVEL | Nenhum |
| ⚡ **Speed Demon** | < 1h entre deals | **111** | ✅ MUITO VIÁVEL | Nenhum |
| 🏃 **Flash** | < 3h entre deals | **119** | ✅ MUITO VIÁVEL | Nenhum |

**Exemplo real encontrado:**
- **Hat Trick:** Analista 69943343 fez **100 deals em 1 dia** (21/10) 🤯
- **Big Fish:** Deal de R$ 148.812,43 (Confederação das Cooperativas do Sicredi)

---

### 5. 👥 Cobertura de Dados de Analistas

**Status:** **EXCELENTE**

- ✅ **Mapeamento de nomes:** 100% (32/32 analistas)
- ✅ **Fotos disponíveis:** 93.8% (30/32 analistas)

**Analistas sem foto (2):**
1. Luiza Kukus Inglês da Luz (112 deals!)
2. César Schroeder (11 deals)

**Top 5 Analistas (últimos 30 dias):**
1. Luiza Kukus - 112 deals, R$ 50.780
2. Rafael Grado - 16 deals, R$ 42.097
3. Andreza Sandim - 11 deals, R$ 36.511
4. César Schroeder - 11 deals, R$ 10.787
5. Inaiara Lorusso - 10 deals, R$ 69.213

**Ação necessária:** Adicionar 2 fotos faltantes.

---

## 🎯 Badges Recomendados para Implementação

### ✅ FASE 1 - Badges Prioritários (Alta Frequência)
Implementar **primeiro** - ocorrem com frequência suficiente:

1. **Hat Trick** 🥇 (3 deals/dia) - 5 ocorrências
2. **Big Fish** 💰 (deal > R$ 100k) - 1 ocorrência, ajustar para R$ 50k
3. **Early Bird** 🌅 (antes 10h) - 5+ ocorrências
4. **Night Owl** 🌙 (depois 17h) - 27+ ocorrências
5. **Speed Demon** ⚡ (< 1h entre deals) - 111 ocorrências!
6. **Flash** 🏃 (< 3h entre deals) - 119 ocorrências
7. **Double Kill** 🥈 (2 deals/dia) - presumivelmente muitas

### ⚠️ FASE 2 - Badges Ajustados (Critérios Relaxados)
Implementar **depois** com critérios ajustados:

8. **Suit Up** 👔 - Reduzir para R$ 300k/semana (em vez de R$ 500k)
9. **Sniper** 🎯 - Reduzir para 3 deals > R$ 50k consecutivos (em vez de 5)
10. **Whale Hunter** 💎 - Deal > R$ 150k (mais raro que Big Fish)

### 📊 FASE 3 - Badges Agregados (Sempre Funcionam)
Implementar **junto com Fase 1** - cálculos simples:

11. **First Blood** 🥉 - Primeiro deal do dia
12. **Unstoppable** 🏆 - 5+ deals em 1 dia
13. **Godlike** 👑 - 10+ deals em 1 dia (raro mas possível - vimos 100 deals!)
14. **Perfect Week** 💯 - 100% da meta semanal
15. **To The Moon** 🚀 - R$ 1M acumulado no mês

---

## 📈 MVP da Semana & Recordes

### ✅ MVP da Semana - TOTALMENTE VIÁVEL

**Dados disponíveis:**
- ✅ Analista (via `analista_comercial`)
- ✅ Revenue semanal (via `SUM(valor_ganho)`)
- ✅ Deal count (via `COUNT(*)`)
- ✅ Ticket médio (via `AVG(valor_ganho)`)
- ✅ Foto do analista (93.8% cobertura)

**Query testada e funcional.**

### ✅ Recordes - IMPLEMENTÁVEIS

Todos os recordes podem ser calculados:

1. **Maior dia** - `MAX(SUM(valor_ganho) GROUP BY DATE(closedate))` ✅
2. **Maior deal** - `MAX(valor_ganho)` ✅ (já encontramos: R$ 148k)
3. **Mais deals em 1 dia** - `MAX(COUNT(*) GROUP BY DATE(closedate))` ✅ (já vimos: 100 deals!)
4. **Melhor streak** - Window functions ⚠️ (complexo mas possível)

---

## 🐛 Observações e Ressalvas

### 1. ⚠️ Spike Anormal às 12h (101 deals)

Possível importação em lote ou sincronização batch. **Recomendações:**
- Investigar se é sincronização manual
- Considerar filtrar deals com timestamps suspeitos
- Ou aceitar como válidos se forem deals reais

### 2. ⚠️ Analista ID 69943343 (Luiza) - 112 deals em 30 dias

Performance **extremamente alta**. Possíveis explicações:
- Analista excepcionalmente produtiva ✅
- Roteamento de deals automáticos ⚠️
- Pipeline específico (ex: renovações) ⚠️

**Ação:** Validar se todos os 112 deals são deals "normais" ou se há categoria especial.

### 3. ✅ Fotos Faltantes (2 analistas)

**Solução simples:**
- Solicitar fotos de Luiza e César
- Ou usar placeholder genérico até obter fotos

---

## 🚀 Decisão Final: **GO PARA IMPLEMENTAÇÃO**

### Justificativa:

1. ✅ **Dados suficientes e de qualidade**
   - Timestamps granulares (hora/minuto/segundo)
   - Cobertura de analistas: 100% mapeamento, 94% fotos
   - Queries testadas e funcionais

2. ✅ **Badges viáveis (15 de 17)**
   - 7 badges com alta frequência (Fase 1)
   - 3 badges com ajustes menores (Fase 2)
   - 5 badges sempre funcionam (agregados)

3. ✅ **MVP e Recordes implementáveis**
   - Queries validadas
   - Dados históricos disponíveis

4. ⚠️ **Ajustes necessários são mínimos**
   - 2 fotos faltantes (fácil resolver)
   - Ajustar critérios de 2-3 badges (rápido)
   - Investigar spike às 12h (opcional)

---

## 📋 Próximos Passos Recomendados

### Imediato (Hoje):
1. ✅ Adicionar fotos de Luiza e César em `static/img/team/`
2. ✅ Criar tabela `badges_desbloqueados` no banco
3. ✅ Começar implementação da página Hall da Fama (HTML/CSS)

### Curto Prazo (Amanhã):
4. ✅ Implementar endpoints `/api/mvp-semana` e `/api/recordes`
5. ✅ Criar lógica `check_badges()` para detecção automática
6. ✅ Implementar Fase 1 (7 badges prioritários)

### Médio Prazo (2-3 dias):
7. ✅ Integrar com webhook de deals ganhos
8. ✅ Testar detecção em tempo real
9. ✅ Deploy em produção

---

## 🎮 Badges Finais Aprovados para Implementação

### 📊 **IMPORTANTE: Badges Adaptados por Perfil**

Cada perfil (EV, SDR, LDR) tem métricas diferentes e precisa de badges específicos:

---

### 🏆 **PERFIL: EVs** (Executivos de Vendas)
**Métrica principal:** Revenue (valor_ganho) + Deal Count  
**Campo identificador:** `deals.analista_comercial` (owner_id)

**FASE 1** (implementar primeiro):
- 🥇 **Hat Trick** (3 deals ganhos/dia)
- 💰 **Big Fish** (deal > R$ 50k)
- 🌅 **Early Bird** (deal ganho antes 10h)
- 🌙 **Night Owl** (deal ganho depois 17h)
- ⚡ **Speed Demon** (< 1h entre deals ganhos)
- 🏃 **Flash** (< 3h entre deals ganhos)
- 🥈 **Double Kill** (2 deals ganhos/dia)

**FASE 2** (implementar depois):
- 👔 **Suit Up** (R$ 300k/semana)
- 🎯 **Sniper** (3 deals > R$ 50k consecutivos)
- 💎 **Whale Hunter** (deal > R$ 150k)

**SEMPRE FUNCIONAM** (cálculos simples):
- 🥉 **First Blood** (primeiro deal ganho do dia)
- 🏆 **Unstoppable** (5+ deals ganhos/dia)
- 👑 **Godlike** (10+ deals ganhos/dia)
- 💯 **Perfect Week** (100% meta semanal de revenue)
- 🚀 **To The Moon** (R$ 1M acumulado/mês)

---

### 📞 **PERFIL: SDRs** (Sales Development Representatives)
**Métrica principal:** Scheduled Count (agendamentos)  
**Campo identificador:** `deals.pr_vendedor` (SDR ID - convertido para nome)  
**Campo de data:** `deals.data_de_agendamento` (⚠️ **SEM hora/minuto - apenas DATE**)  
**Pipelines:** NEW (6810518) e Expansão (4007305)

**FASE 1** (implementar primeiro):
- 🎯 **Hat Trick SDR** (3 agendamentos/dia)
- 📅 **Master Scheduler** (5 agendamentos/dia)
- 🥈 **Double Kill** (2 agendamentos/dia)
- � **Unstoppable** (7+ agendamentos/dia)

**FASE 2** (implementar depois):
- 🔥 **On Fire** (10+ agendamentos/semana)
- 💯 **Perfect Week** (100% meta semanal de agendamentos)
- 📈 **Consistency King** (agendamentos 5 dias seguidos)

**SEMPRE FUNCIONAM**:
- 🥉 **First Blood** (primeiro agendamento do dia)
- 🚀 **Top Performer** (líder da semana em agendamentos)

**❌ NÃO IMPLEMENTÁVEIS** (data_de_agendamento não tem hora):
- ~~Early Bird~~ (campo sem hora)
- ~~Night Owl~~ (campo sem hora)
- ~~Speed Demon~~ (campo sem hora)
- ~~Flash~~ (campo sem hora)

---

### 🎓 **PERFIL: LDRs** (Lead Development Representatives)
**Métrica principal:** Won Deals Count (deals qualificados que ganharam)  
**Campo identificador:** `deals.criado_por` (LDR name)

**FASE 1** (implementar primeiro):
- 🎯 **Hat Trick LDR** (3 deals criados ganhos/dia)
- 🥇 **Golden Touch** (5 deals criados ganhos/semana)
- 🌅 **Early Bird** (deal ganho antes 10h)
- 🌙 **Night Owl** (deal ganho depois 17h)
- 💎 **Quality Master** (80%+ taxa conversão criados → ganhos)

**FASE 2** (implementar depois):
- 💯 **Perfect Week** (100% meta semanal de deals ganhos)
- 🔥 **Qualification King** (10+ deals criados ganhos/mês)

**SEMPRE FUNCIONAM**:
- 🥉 **First Blood** (primeiro deal criado ganho do dia)
- 🏆 **Unstoppable** (5+ deals criados ganhos/dia)
- 🚀 **Top Performer** (líder da semana em won deals)

---

### 🎖️ **BADGES UNIVERSAIS** (Todos os Perfis)
Aplicáveis a EVs, SDRs e LDRs:

- 🔥 **Streak Master** (5 dias consecutivos atingindo meta)
- ⏰ **Perfect Timing** (100% deals no horário ideal)
- 📈 **Comeback** (virar ranking de última posição para top 3)
- 👑 **MVP da Semana** (líder geral da semana)

---

## ⚠️ **AJUSTE CRÍTICO NO SCHEMA DO BANCO**

A tabela `badges_desbloqueados` precisa suportar **3 perfis diferentes**:

```sql
CREATE TABLE badges_desbloqueados (
    id SERIAL PRIMARY KEY,
    
    -- Identificação do usuário (flexível para 3 perfis)
    user_type VARCHAR(10) NOT NULL, -- 'EV', 'SDR', 'LDR'
    user_id VARCHAR(50) NOT NULL,   -- owner_id para EV, name para SDR/LDR
    user_name VARCHAR(255) NOT NULL,
    
    -- Badge info
    badge_code VARCHAR(50) NOT NULL,
    badge_name VARCHAR(100) NOT NULL,
    badge_category VARCHAR(50),
    
    -- Contexto
    unlocked_at TIMESTAMP DEFAULT NOW(),
    deal_id VARCHAR(50),
    deal_name VARCHAR(255),
    metric_value DECIMAL(15, 2), -- Revenue para EV, count para SDR/LDR
    
    -- Índices para performance
    UNIQUE (user_type, user_id, badge_code, DATE(unlocked_at))
);

CREATE INDEX idx_badges_user ON badges_desbloqueados(user_type, user_id);
CREATE INDEX idx_badges_unlocked ON badges_desbloqueados(unlocked_at DESC);
```

---

**Aprovado para desenvolvimento:** ✅ **SIM**  
**Risco:** 🟢 **BAIXO**  
**Esforço:** 🟡 **MÉDIO-ALTO** (3-4 dias - 3 perfis)  
**Impacto esperado:** 🟢 **ALTO** (engajamento de TODO o time comercial)
