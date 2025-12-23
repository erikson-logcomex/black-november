# 🔒 Guia: Habilitar SSL em Todas as Aplicações GCP

**Data:** 28 de Novembro de 2025  
**Projeto:** datatoopenai  
**Banco:** Cloud SQL `comercial-db`

---

## 📊 Inventário de Aplicações

### ☁️ Cloud Run (7 serviços)

| Serviço | Status | SSL Configurado? |
|---------|--------|------------------|
| **black-november-funnel** | ✅ Running | ✅ **SIM** (já feito) |
| fup-automatico | ✅ Running | ❌ Pendente |
| logcortex-api | ✅ Running | ❌ Pendente |
| logcortex-api-dev | ✅ Running | ❌ Pendente |
| meetrox-data-capture | ✅ Running | ❌ Pendente |
| portal-log-cortx-backend-v3 | ✅ Running | ❌ Pendente |
| portal-log-cortx-frontend-v3 | ✅ Running | ❌ Pendente |

### 🎯 Kubernetes (2 clusters)

#### Cluster: `metabase-cluster`
| Aplicação | Namespace | Status | SSL Configurado? |
|-----------|-----------|--------|------------------|
| **Metabase** | `metabase` | ✅ Running | ❌ Pendente |

#### Cluster: `n8n-cluster`
| Aplicação | Namespace | Status | SSL Configurado? | Observação |
|-----------|-----------|--------|------------------|------------|
| **n8n** | `n8n` | ✅ Running | ❌ Pendente | Conecta **diretamente** ao Cloud SQL (172.23.64.3) |
| **evolution-api** | `n8n` | ✅ Running | ❌ Pendente | - |
| **n8n-worker** | `n8n` | ✅ Running | ❌ Pendente | - |
| **pgbouncer** | `n8n` | ⚠️ 0/1 (erro) | ❌ N/A | **NÃO está sendo usado** - erro `ImagePullBackOff`. Pode ser removido. |

---

## 🎯 Como Configurar SSL


## ☁️ Cloud Run: Como Configurar

### Método 1: Adicionar `?sslmode=require` na Connection String

**Para aplicações que usam connection string (ex: Python, Node.js):**

#### Exemplo Python (psycopg2):
```python
# ANTES
conn = psycopg2.connect(
    host=os.getenv('PG_HOST'),
    database=os.getenv('PG_DATABASE'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD')
)

# DEPOIS
conn = psycopg2.connect(
    host=os.getenv('PG_HOST'),
    database=os.getenv('PG_DATABASE'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
    sslmode='require'  # ✅ Adicionar esta linha
)
```

#### Exemplo Node.js (pg):
```javascript
// ANTES
const connectionString = `postgresql://${user}:${password}@${host}:${port}/${database}`;

// DEPOIS
const connectionString = `postgresql://${user}:${password}@${host}:${port}/${database}?sslmode=require`;
```

#### Exemplo Java (JDBC):
```java
// ANTES
String url = "jdbc:postgresql://host:port/database";

// DEPOIS
String url = "jdbc:postgresql://host:port/database?sslmode=require";
```

### Método 2: Variável de Ambiente

**Para aplicações que usam variáveis de ambiente:**

Adicionar no `cloudbuild.yaml` ou via Console:
```yaml
- '--set-env-vars'
- 'PGSSLMODE=require'
```

Ou na connection string:
```env
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

---

## 🎯 Kubernetes: Como Configurar


### Metabase (Kubernetes)

#### Opção 1: Via ConfigMap/Secret (Recomendado)

1. **Verificar ConfigMap atual:**
```powershell
kubectl get configmap -n metabase
kubectl get secret -n metabase
```

2. **Atualizar connection string no ConfigMap ou Secret:**
```powershell
# Se usar ConfigMap
kubectl edit configmap metabase-config -n metabase

# Adicionar/modificar:
# DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

3. **Ou criar/atualizar Secret:**
```powershell
kubectl create secret generic metabase-db \
  --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require" \
  -n metabase --dry-run=client -o yaml | kubectl apply -f -
```

4. **Reiniciar deployment:**
```powershell
kubectl rollout restart deployment metabase-app -n metabase
```

#### Opção 2: Via Interface do Metabase

1. Acessar Metabase → Admin → Database
2. Editar conexão do banco
3. Adicionar `?sslmode=require` na connection string
4. Salvar

### n8n (Kubernetes)

#### Opção 1: Via ConfigMap/Secret

1. **Verificar configuração atual:**
```powershell
kubectl get configmap -n n8n
kubectl get secret -n n8n
kubectl get deployment n8n -n n8n -o yaml | Select-String -Pattern "DB_|DATABASE"
```

2. **Atualizar variável de ambiente:**
```powershell
# n8n usa DB_POSTGRESDB_HOST, DB_POSTGRESDB_PORT, etc.
# Adicionar SSL na connection string ou variável específica

kubectl set env deployment/n8n \
  DB_POSTGRESDB_SSL=true \
  -n n8n
```

3. **Ou atualizar connection string completa:**
```powershell
kubectl set env deployment/n8n \
  DB_TYPE=postgresdb \
  DB_POSTGRESDB_HOST=172.23.64.3 \
  DB_POSTGRESDB_PORT=5432 \
  DB_POSTGRESDB_DATABASE=hubspot-sync \
  DB_POSTGRESDB_USER=meetrox_user \
  DB_POSTGRESDB_SSL=true \
  -n n8n
```

4. **Reiniciar:**
```powershell
kubectl rollout restart deployment n8n -n n8n
```

### evolution-api (Kubernetes)

**Verificar como está configurado:**
```powershell
kubectl get deployment evolution-api -n n8n -o yaml | Select-String -Pattern "DATABASE|DB_|POSTGRES"
```

**Adicionar SSL na connection string ou variáveis de ambiente específicas.**

---

## 📋 Checklist por Aplicação

### Cloud Run

- [ ] **black-november-funnel** ✅ Já configurado
- [ ] **fup-automatico** - Verificar código e adicionar `sslmode=require`
- [ ] **logcortex-api** - Verificar código e adicionar `sslmode=require`
- [ ] **logcortex-api-dev** - Verificar código e adicionar `sslmode=require`
- [ ] **meetrox-data-capture** - Verificar código e adicionar `sslmode=require`
- [ ] **portal-log-cortx-backend-v3** - Verificar código e adicionar `sslmode=require`
- [ ] **portal-log-cortx-frontend-v3** - Verificar se conecta ao banco (provavelmente não)

### Kubernetes

- [ ] **Metabase** - Adicionar `?sslmode=require` na connection string
- [ ] **n8n** - Adicionar `DB_POSTGRESDB_SSL=true` (conecta diretamente ao Cloud SQL)
- [ ] **evolution-api** - Verificar configuração e adicionar SSL
- [ ] **n8n-worker** - Mesma configuração do n8n
- [ ] ~~**pgbouncer**~~ - **NÃO precisa** - não está sendo usado (pode ser removido)

---

## 🔍 Como Verificar se Está Funcionando

### 1. Verificar Logs da Aplicação

**Cloud Run:**
```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=NOME_DO_SERVICO" --limit=20 --project=datatoopenai
```

**Kubernetes:**
```powershell
kubectl logs deployment/NOME_DEPLOYMENT -n NAMESPACE --tail=50
```

**Procure por:**
- ✅ Conexões SSL estabelecidas
- ✅ `sslmode=require` ou `sslmode=verify-ca`
- ❌ Erros de SSL

### 2. Verificar Logs do Cloud SQL

```powershell
gcloud logging read "resource.type=cloudsql_database AND resource.labels.database_id=datatoopenai:comercial-db" --limit=50 --format="table(timestamp,jsonPayload)" --project=datatoopenai
```

**Procure por conexões com `ssl=true`**

### 3. Teste de Conexão

**Via psql:**
```powershell
psql "host=172.23.64.3 port=5432 dbname=hubspot-sync user=meetrox_user sslmode=require" -c "SELECT version();"
```

---

## 🎯 Ordem Recomendada de Migração

### Fase 1: Cloud Run (Mais Fácil)
1. ✅ black-november-funnel (já feito)
2. fup-automatico
3. logcortex-api
4. meetrox-data-capture
5. portal-log-cortx-backend-v3

### Fase 2: Kubernetes (Requer Acesso)
1. Metabase
2. n8n
3. evolution-api
4. n8n-worker

### Fase 3: Validação
1. Verificar logs de todas as aplicações
2. Confirmar que todas estão usando SSL
3. Monitorar por alguns dias

### Fase 4: Habilitar SSL Obrigatório no Cloud SQL
1. **SOMENTE APÓS** todas as aplicações estiverem usando SSL
2. Habilitar "Permitir somente conexões SSL" no Cloud SQL
3. Monitorar por problemas

---

## 📚 Referências por Tipo de Aplicação

### Python (psycopg2)
```python
ssl_params = {'sslmode': 'require'}
conn = psycopg2.connect(..., **ssl_params)
```

### Node.js (pg)
```javascript
const connectionString = `postgresql://...?sslmode=require`;
```

### Java (JDBC)
```java
String url = "jdbc:postgresql://...?sslmode=require";
```

### Metabase
```
Connection String: postgresql://user:pass@host:5432/db?sslmode=require
```

### n8n
```
DB_POSTGRESDB_SSL=true
```
ou
```
DB_POSTGRESDB_CONNECTION_STRING=postgresql://...?sslmode=require
```

---

## ⚠️ Importante

1. **Não configure no Ingress** - Ingress é para HTTPS externo
2. **Configure dentro da aplicação** - Connection string ou variáveis de ambiente
3. **Teste antes de habilitar SSL obrigatório** no Cloud SQL
4. **Monitore logs** após cada mudança
5. **Tenha plano de rollback** caso algo quebre

