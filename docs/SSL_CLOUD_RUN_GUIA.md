# 🔒 Guia: Habilitar SSL em Aplicações Cloud Run

**Data:** 28 de Novembro de 2025  
**Aplicação:** Black November (Cloud Run)  
**Banco:** Cloud SQL via VPC

---

## 📋 Como Funciona SSL no Cloud Run

### 🔍 Situação Atual da Aplicação

Sua aplicação **Black November** está configurada assim:

```yaml
# cloudbuild.yaml
--vpc-connector vpc-meetrox-webhook
--vpc-egress private-ranges-only
PG_HOST=172.23.64.3  # IP privado do Cloud SQL
```

**O que isso significa:**
- ✅ Aplicação usa **VPC Connector** para acessar recursos privados
- ✅ Conecta ao Cloud SQL via **IP privado** (`172.23.64.3`)
- ✅ Tráfego fica **dentro da rede privada do Google Cloud**

### 🌐 Tipos de Conexão com Cloud SQL

| Tipo | Como Funciona | SSL Necessário? | Segurança |
|------|---------------|-----------------|----------|
| **IP Público** | Via internet pública | ✅ **SIM** (obrigatório) | ⚠️ Média |
| **IP Privado (VPC)** | Via rede privada do GCP | ✅ **Recomendado** | ✅ Alta |
| **Cloud SQL Proxy** | Via proxy gerenciado | ✅ Automático | ✅ Máxima |

**Sua aplicação usa IP Privado via VPC** → Tráfego já está mais seguro, mas SSL ainda é recomendado!

---

## 🎯 Por Que Usar SSL Mesmo com VPC?

1. **Defense in Depth**: Múltiplas camadas de segurança
2. **Compliance**: Requisitos de segurança/auditoria
3. **Futuro**: Se migrar para IP público, já estará pronto
4. **Best Practice**: Google recomenda SSL sempre

---

## 🚀 Como Habilitar SSL em Cloud Run

### Opção 1: SSL Simples (Recomendado para Começar)

**Não precisa de certificado CA!** O Cloud SQL aceita SSL sem verificação de certificado.

#### Passo 1: Atualizar `app.py` (JÁ FEITO ✅)

O código já está atualizado:

```python
ssl_params = {
    'sslmode': 'require'  # Força SSL sem verificar certificado
}
```

#### Passo 2: Fazer Deploy

```powershell
# Fazer commit e push
git add app.py
git commit -m "feat: adiciona suporte SSL para conexões PostgreSQL"
git push

# O Cloud Build vai fazer o deploy automaticamente
```

**Pronto!** A aplicação já está usando SSL. ✅

---

### Opção 2: SSL com Verificação de Certificado (Mais Seguro)

Se quiser verificar o certificado do servidor (mais seguro):

#### Passo 1: Baixar Certificado CA do Cloud SQL

**Via Console:**
1. Console GCP → SQL → `comercial-db` → Conexões
2. Role até **Certificados SSL**
3. Clique em **Baixar certificado do servidor**
4. Salve como `server-ca.pem`

**Via CLI:**
```powershell
# Criar diretório
mkdir certs

# Baixar certificado
gcloud sql instances describe comercial-db --format="get(serverCaCert.cert)" > certs/server-ca.pem
```

#### Passo 2: Adicionar Certificado ao Secret Manager

```powershell
# Criar secret com o certificado
gcloud secrets create cloud-sql-ca-cert --data-file=certs/server-ca.pem --project=datatoopenai
```

#### Passo 3: Atualizar `cloudbuild.yaml`

```yaml
- '--set-secrets'
- 'PG_PASSWORD=PG_PASSWORD:latest,CLOUD_SQL_CA_CERT=cloud-sql-ca-cert:latest,HUBSPOT_PRIVATE_APP_TOKEN=HUBSPOT_PRIVATE_APP_TOKEN:latest,GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest,SECRET_KEY=SECRET_KEY:latest'
```

#### Passo 4: Atualizar `app.py`

```python
def init_db_pool():
    """Inicializa o pool de conexões PostgreSQL com SSL"""
    global _db_pool
    if _db_pool is None:
        try:
            # Configuração SSL
            ssl_params = {
                'sslmode': 'require'  # Padrão: SSL sem verificação
            }
            
            # Se tiver certificado CA no Secret Manager, usar verificação
            ssl_cert_content = os.getenv('CLOUD_SQL_CA_CERT')
            if ssl_cert_content:
                # Escrever certificado em arquivo temporário
                ssl_cert_path = '/tmp/server-ca.pem'
                with open(ssl_cert_path, 'w') as f:
                    f.write(ssl_cert_content)
                ssl_params = {
                    'sslmode': 'verify-ca',  # Verifica certificado do servidor
                    'sslrootcert': ssl_cert_path
                }
                print("🔒 SSL configurado com verificação de certificado CA")
            else:
                print("🔒 SSL configurado sem verificação de certificado (sslmode=require)")
            
            _db_pool = pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=50,
                host=os.getenv('PG_HOST'),
                port=os.getenv('PG_PORT'),
                database=os.getenv('PG_DATABASE_HUBSPOT'),
                user=os.getenv('PG_USER'),
                password=os.getenv('PG_PASSWORD'),
                **ssl_params
            )
            print("✅ Pool de conexões PostgreSQL inicializado com SSL (min: 2, max: 50)")
        except Exception as e:
            print(f"❌ Erro ao inicializar pool de conexões: {e}")
            _db_pool = None
    return _db_pool
```

---

## 🔍 Verificar se SSL Está Funcionando

### Via Logs do Cloud Run

```powershell
# Ver logs recentes
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=black-november-funnel" --limit=50 --format="table(timestamp,textPayload)" --project=datatoopenai
```

**Procure por:**
- ✅ `Pool de conexões PostgreSQL inicializado com SSL`
- ✅ `SSL configurado`

### Via Logs do Cloud SQL

```powershell
# Ver conexões SSL no Cloud SQL
gcloud logging read "resource.type=cloudsql_database AND resource.labels.database_id=datatoopenai:comercial-db" --limit=50 --format="table(timestamp,jsonPayload)" --project=datatoopenai
```

**Procure por conexões com `ssl=true`**

### Teste Manual (via Python no Cloud Run)

Adicionar endpoint de debug temporário:

```python
@app.route('/api/debug/ssl-test')
def test_ssl():
    """Testa conexão SSL com o banco"""
    try:
        with get_db_connection_context() as conn:
            if conn:
                # Verificar se conexão está usando SSL
                cursor = conn.cursor()
                cursor.execute("SHOW ssl;")
                ssl_status = cursor.fetchone()
                cursor.close()
                
                return jsonify({
                    'ssl_enabled': True,
                    'ssl_status': ssl_status,
                    'connection_info': {
                        'host': os.getenv('PG_HOST'),
                        'database': os.getenv('PG_DATABASE_HUBSPOT')
                    }
                })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## 📊 Comparação: Com vs Sem SSL

| Aspecto | Sem SSL | Com SSL (`require`) | Com SSL (`verify-ca`) |
|---------|---------|---------------------|----------------------|
| **Criptografia** | ❌ Não | ✅ Sim | ✅ Sim |
| **Verifica Certificado** | ❌ Não | ❌ Não | ✅ Sim |
| **Complexidade** | ✅ Simples | ✅ Simples | ⚠️ Média |
| **Segurança** | 🔴 Baixa | 🟡 Média | 🟢 Alta |
| **Recomendado para** | - | ✅ Início | ✅ Produção |

---

## 🎯 Recomendação para Sua Aplicação

### Fase 1: Agora (Já Feito ✅)
- ✅ Usar `sslmode=require` (SSL sem verificação)
- ✅ Funciona imediatamente
- ✅ Não precisa de certificado
- ✅ Seguro o suficiente para VPC privado

### Fase 2: Futuro (Opcional)
- Adicionar certificado CA via Secret Manager
- Migrar para `sslmode=verify-ca`
- Maior segurança

---

## 🔧 Outras Aplicações Cloud Run

### Metabase (Cloud Run)

**Como configurar:**
1. Acessar código/configuração do Metabase
2. Adicionar parâmetro SSL na string de conexão:
   ```
   ?sslmode=require
   ```
3. Fazer deploy

**Exemplo de string de conexão:**
```
postgresql://user:pass@host:5432/database?sslmode=require
```

### Vaultwarden (Cloud Run)

**Similar ao Metabase:**
- Adicionar `?sslmode=require` na DATABASE_URL
- Ou variável de ambiente `DATABASE_SSL_MODE=require`

---

## ⚠️ Importante

1. **Cloud Run via VPC:**
   - Tráfego já está na rede privada (mais seguro)
   - SSL adiciona camada extra de segurança
   - Não é estritamente necessário, mas recomendado

2. **IP Público vs Privado:**
   - **IP Público**: SSL é **obrigatório** (tráfego na internet)
   - **IP Privado (VPC)**: SSL é **recomendado** (defense in depth)

3. **Cloud SQL Proxy:**
   - Se usar Cloud SQL Proxy, SSL é automático
   - Não precisa configurar nada
   - Mas sua aplicação usa conexão direta via VPC

---

## 📚 Referências

- [Cloud Run VPC Connector](https://cloud.google.com/run/docs/configuring/connecting-vpc)
- [Cloud SQL SSL](https://cloud.google.com/sql/docs/postgres/configure-ssl-instance)
- [psycopg2 SSL](https://www.psycopg.org/docs/module.html#psycopg2.connect)

