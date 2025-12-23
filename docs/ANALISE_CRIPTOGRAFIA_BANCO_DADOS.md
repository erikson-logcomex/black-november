# Análise de Criptografia - Banco de Dados PostgreSQL (comercial-db)

**Data da Análise:** 27 de Novembro de 2025  
**Instância:** `comercial-db`  
**Projeto:** datatoopenai  
**Região:** us-central1  
**Versão:** PostgreSQL 17

---

## 1. Configurações Atuais

### 1.1. Criptografia em Repouso (At Rest)

| Aspecto | Status | Detalhes |
|---------|--------|----------|
| **Criptografia** | ✅ **Habilitada** | Criptografia automática do Google Cloud |
| **Tipo de Chave** | Google-managed | Chaves gerenciadas pelo Google (padrão) |
| **KMS Customizado** | ❌ Não configurado | `diskEncryptionConfiguration.kmsKeyName` está vazio |
| **Tipo de Disco** | PD_SSD | Persistent Disk SSD |
| **Tamanho do Disco** | 100 GB | - |

**Observação:** O Cloud SQL criptografa automaticamente todos os dados em repouso por padrão usando chaves gerenciadas pelo Google. Esta é uma prática segura e adequada para a maioria dos casos de uso.

### 1.2. Criptografia em Trânsito (In Transit)

| Aspecto | Status | Valor Atual | ⚠️ Risco |
|---------|--------|-------------|----------|
| **SSL Obrigatório** | ❌ **Desabilitado** | `requireSsl: false` | 🔴 **ALTO** |
| **Modo SSL** | ⚠️ Permissivo | `ALLOW_UNENCRYPTED_AND_ENCRYPTED` | 🔴 **ALTO** |
| **CA Mode** | ✅ Google Managed | `GOOGLE_MANAGED_INTERNAL_CA` | - |
| **Rede Privada** | ✅ Configurada | `projects/datatoopenai/global/networks/default` | - |

**⚠️ PROBLEMA CRÍTICO:** O banco de dados está configurado para **aceitar conexões não criptografadas**, o que representa um risco de segurança significativo, especialmente para conexões que não passam pela rede privada do Google Cloud.

### 1.3. Configurações de Backup

| Aspecto | Status | Detalhes |
|---------|--------|----------|
| **Backup Automático** | ✅ Habilitado | Diário às 01:00 |
| **Point-in-Time Recovery** | ✅ Habilitado | - |
| **Retenção de Backups** | ✅ 7 backups | - |
| **Retenção de Logs** | ✅ 7 dias | - |
| **Armazenamento de Logs** | ✅ Cloud Storage | - |

---

## 2. Aplicações Conectadas ao Banco

A instância `comercial-db` possui múltiplas aplicações e serviços conectados através de redes autorizadas:

### 2.1. Aplicações Identificadas

| Aplicação/Serviço | Rede Autorizada | Tipo | Impacto SSL |
|-------------------|-----------------|------|-------------|
| **Metabase** | `35.247.192.0/18` (cloud-run-metabase) | Cloud Run | ⚠️ Requer configuração |
| **Grafana** | `34.95.244.163/32` | GKE/Monitoring | ⚠️ Requer configuração |
| **n8n** | `34.95.247.159/32` | Automação | ⚠️ Requer configuração |
| **Vaultwarden** | `34.143.77.0/24` (cloud-run-vaultwarden) | Cloud Run | ⚠️ Requer configuração |
| **Black November** | `172.23.64.3` (VPC) | Cloud Run | ⚠️ Requer configuração |
| **Looker Studio** | `142.251.74.0/23` | Google Service | ✅ Suporta SSL |
| **GKE Clusters** | `34.95.244.0/24`, `35.247.204.0/24` | Kubernetes | ⚠️ Requer configuração |
| **VPN Logcomex** | `15.229.107.199/32` | VPN | ⚠️ Requer configuração |
| **Acessos Residenciais** | Vários IPs `/32` | Desenvolvimento | ⚠️ Requer configuração |

### 2.2. Configuração Atual da Aplicação Black November

**Arquivo:** `app.py` (linhas 65-73)

```python
_db_pool = pool.ThreadedConnectionPool(
    minconn=2,
    maxconn=50,
    host=os.getenv('PG_HOST'),
    port=os.getenv('PG_PORT'),
    database=os.getenv('PG_DATABASE_HUBSPOT'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD')
    # ❌ SSL não configurado
)
```

**Status:** A aplicação **não está configurada** para usar SSL nas conexões com o banco de dados.

---

## 3. Análise de Riscos

### 3.1. Riscos Identificados

| Risco | Severidade | Probabilidade | Impacto |
|-------|------------|---------------|---------|
| **Interceptação de dados em trânsito** | 🔴 **ALTA** | Média | Dados sensíveis podem ser interceptados |
| **Man-in-the-Middle (MITM)** | 🔴 **ALTA** | Baixa (rede privada) | Ataques de interceptação |
| **Não conformidade com regulamentações** | 🟡 **MÉDIA** | Alta | LGPD, PCI-DSS, etc. |
| **Auditoria de segurança** | 🟡 **MÉDIA** | Alta | Falha em auditorias |

### 3.2. Mitigações Atuais

- ✅ **Rede Privada:** A maioria das conexões passa pela VPC privada do Google Cloud
- ✅ **Criptografia em Repouso:** Dados criptografados no disco
- ❌ **Criptografia em Trânsito:** Não obrigatória

**Observação:** Embora a rede privada reduza o risco, a criptografia em trânsito ainda é uma **melhor prática de segurança** e muitas vezes um **requisito de conformidade**.

---

## 4. Recomendações

### 4.1. Recomendação Principal

**Habilitar SSL obrigatório** para todas as conexões com o banco de dados, seguindo uma **abordagem gradual** para evitar interrupções nos serviços.

### 4.2. Recomendações Específicas

#### 🔒 Criptografia em Repouso
- ✅ **Manter configuração atual** (Google-managed encryption)
- 💡 **Opcional:** Considerar KMS customizado para maior controle (se necessário para compliance)

#### 🔐 Criptografia em Trânsito
1. **Fase 1 - Preparação (Sem Impacto):**
   - Configurar aplicações para usar SSL (sem obrigar no banco)
   - Testar cada aplicação individualmente
   - Documentar configurações necessárias

2. **Fase 2 - Migração Gradual:**
   - Migrar aplicações críticas primeiro
   - Validar funcionamento
   - Monitorar logs e erros

3. **Fase 3 - Ativação:**
   - Habilitar `requireSsl=true` no banco
   - Configurar `sslMode=ENCRYPTED_ONLY`
   - Monitorar e resolver problemas imediatamente

#### 📊 Backup e Recuperação
- ✅ **Manter configuração atual** (excelente)
- Considerar aumentar retenção se necessário para compliance

---

## 5. Plano de Ação

### 5.1. Fase 1: Preparação e Testes (Sem Impacto) ⏱️ 1-2 semanas

#### Etapa 1.1: Configurar Black November para SSL
- [ ] Adicionar parâmetros SSL na configuração do pool de conexões
- [ ] Baixar certificado SSL do Cloud SQL (se necessário)
- [ ] Testar conexão com SSL em ambiente de desenvolvimento
- [ ] Validar funcionamento completo da aplicação
- [ ] Documentar mudanças

**Comandos necessários:**
```bash
# Baixar certificado SSL do Cloud SQL
gcloud sql ssl-certs create client-cert client-cert-key.pem --instance=comercial-db
```

#### Etapa 1.2: Inventariar outras aplicações
- [ ] Listar todas as aplicações que se conectam ao banco
- [ ] Verificar documentação de cada ferramenta sobre suporte SSL
- [ ] Identificar aplicações que já suportam SSL nativamente
- [ ] Priorizar aplicações por criticidade

#### Etapa 1.3: Testar aplicações individualmente
- [ ] **Metabase:** Verificar configuração SSL no Cloud Run
- [ ] **Grafana:** Verificar configuração de datasource com SSL
- [ ] **n8n:** Verificar configuração de conexão PostgreSQL com SSL
- [ ] **Vaultwarden:** Verificar configuração de banco com SSL
- [ ] **Outras aplicações:** Testar uma por uma

### 5.2. Fase 2: Migração Gradual (Baixo Risco) ⏱️ 2-3 semanas

#### Etapa 2.1: Migrar aplicações críticas
**Ordem sugerida:**
1. ✅ **Black November** (já em desenvolvimento)
2. **Metabase** (ferramenta de BI crítica)
3. **Grafana** (monitoramento)
4. **n8n** (automações)
5. **Vaultwarden** (gerenciamento de senhas)

#### Etapa 2.2: Validação e Monitoramento
- [ ] Monitorar logs de conexão do banco
- [ ] Verificar métricas de performance
- [ ] Validar funcionamento de cada aplicação
- [ ] Documentar problemas encontrados e soluções

#### Etapa 2.3: Migrar aplicações secundárias
- [ ] Acessos residenciais (desenvolvimento)
- [ ] Outras ferramentas de desenvolvimento
- [ ] Scripts e automações

### 5.3. Fase 3: Ativação Final (Requer Coordenação) ⏱️ 1 dia

#### Etapa 3.1: Preparação Final
- [ ] Confirmar que todas as aplicações estão usando SSL
- [ ] Agendar janela de manutenção (se necessário)
- [ ] Preparar rollback (desabilitar SSL se necessário)
- [ ] Notificar equipe sobre mudança

#### Etapa 3.2: Ativar SSL Obrigatório
```bash
# Habilitar SSL obrigatório
gcloud sql instances patch comercial-db --require-ssl

# Configurar modo SSL para apenas criptografado
gcloud sql instances patch comercial-db --ssl-mode=ENCRYPTED_ONLY
```

#### Etapa 3.3: Validação Pós-Ativação
- [ ] Verificar todas as aplicações funcionando
- [ ] Monitorar logs por 24-48 horas
- [ ] Validar métricas de performance
- [ ] Documentar conclusão

### 5.4. Fase 4: Melhorias Contínuas (Ongoing)

- [ ] Implementar monitoramento de conexões SSL
- [ ] Configurar alertas para conexões não criptografadas (se possível)
- [ ] Revisar e atualizar documentação
- [ ] Treinar equipe sobre boas práticas de segurança
- [ ] Considerar auditoria de segurança periódica

---

## 6. Configuração Técnica - Black November

### 6.1. Mudanças Necessárias no Código

**Arquivo:** `app.py`

**Antes:**
```python
_db_pool = pool.ThreadedConnectionPool(
    minconn=2,
    maxconn=50,
    host=os.getenv('PG_HOST'),
    port=os.getenv('PG_PORT'),
    database=os.getenv('PG_DATABASE_HUBSPOT'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD')
)
```

**Depois:**
```python
_db_pool = pool.ThreadedConnectionPool(
    minconn=2,
    maxconn=50,
    host=os.getenv('PG_HOST'),
    port=os.getenv('PG_PORT'),
    database=os.getenv('PG_DATABASE_HUBSPOT'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
    sslmode='require'  # ou 'verify-ca' para validação completa
)
```

### 6.2. Variáveis de Ambiente

Adicionar ao `.env` (se necessário para validação de certificado):
```env
PG_SSLMODE=require
# PG_SSLCERT=/path/to/client-cert.pem  # Se usar certificado cliente
# PG_SSLKEY=/path/to/client-key.pem     # Se usar certificado cliente
```

### 6.3. Teste Local

```python
# Teste de conexão com SSL
import psycopg2

conn = psycopg2.connect(
    host=os.getenv('PG_HOST'),
    port=os.getenv('PG_PORT'),
    database=os.getenv('PG_DATABASE_HUBSPOT'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
    sslmode='require'
)
print("✅ Conexão SSL estabelecida com sucesso!")
```

---

## 7. Comandos Úteis

### 7.1. Verificar Status Atual
```bash
# Status geral da instância
gcloud sql instances describe comercial-db --format="table(name,settings.ipConfiguration.requireSsl,settings.ipConfiguration.sslMode)"

# Detalhes de criptografia
gcloud sql instances describe comercial-db --format="get(settings.diskEncryptionConfiguration,settings.ipConfiguration)"
```

### 7.2. Gerenciar Certificados SSL
```bash
# Listar certificados SSL
gcloud sql ssl-certs list --instance=comercial-db

# Criar certificado cliente (se necessário)
gcloud sql ssl-certs create client-cert client-cert-key.pem --instance=comercial-db
```

### 7.3. Ativar SSL (Quando Pronto)
```bash
# Habilitar SSL obrigatório
gcloud sql instances patch comercial-db --require-ssl

# Configurar modo SSL
gcloud sql instances patch comercial-db --ssl-mode=ENCRYPTED_ONLY
```

### 7.4. Rollback (Se Necessário)
```bash
# Desabilitar SSL obrigatório (emergência)
gcloud sql instances patch comercial-db --no-require-ssl
```

---

## 8. Checklist de Conformidade

- [ ] ✅ Criptografia em repouso habilitada
- [ ] ❌ Criptografia em trânsito obrigatória
- [ ] ✅ Backups automáticos configurados
- [ ] ✅ Point-in-Time Recovery habilitado
- [ ] ⚠️ SSL/TLS para todas as conexões (em andamento)
- [ ] ⚠️ Monitoramento de conexões (a implementar)

---

## 9. Referências

- [Google Cloud SQL - Criptografia em Repouso](https://cloud.google.com/sql/docs/postgres/security#encryption-at-rest)
- [Google Cloud SQL - Configurar SSL/TLS](https://cloud.google.com/sql/docs/postgres/configure-ssl-instance)
- [psycopg2 - SSL Connections](https://www.psycopg.org/docs/module.html#psycopg2.connect)
- [LGPD - Lei Geral de Proteção de Dados](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)

---

## 10. Contatos e Responsabilidades

**Responsável pela Implementação:** [A definir]  
**Aprovação Necessária:** [A definir]  
**Data de Revisão:** [A definir]

---

**Documento criado em:** 27 de Novembro de 2025  
**Última atualização:** 27 de Novembro de 2025  
**Versão:** 1.0

