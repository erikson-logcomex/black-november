# 🔒 Guia: Habilitar SSL no Cloud SQL (Sem Tornar Obrigatório)

**Data:** 28 de Novembro de 2025  
**Instância:** `comercial-db`  
**Projeto:** `datatoopenai`

---

## 📋 Visão Geral

No Google Cloud SQL, o SSL já está **habilitado por padrão**, mas **não é obrigatório**. Isso significa que:
- ✅ Conexões SSL são aceitas
- ✅ Conexões sem SSL também são aceitas (para não quebrar aplicações existentes)
- ⚠️ Para segurança máxima, devemos configurar as aplicações para **usar SSL**

## ⚠️ IMPORTANTE: Estratégia de Migração Gradual

**NÃO habilite "Permitir somente conexões SSL" no Cloud SQL até que TODAS as aplicações estejam configuradas!**

Se você habilitar agora, as seguintes aplicações vão parar de funcionar:
- ❌ Metabase
- ❌ Grafana  
- ❌ n8n
- ❌ Vaultwarden
- ❌ Black November (nossa aplicação)
- ❌ Outras aplicações conectadas

### 🎯 Plano de Migração Seguro

**Fase 1: Configurar Aplicações (AGORA)**
1. Atualizar cada aplicação para usar SSL (`sslmode=require`)
2. Testar cada aplicação individualmente
3. Manter Cloud SQL permitindo conexões não criptografadas

**Fase 2: Validação (Após todas configuradas)**
1. Verificar logs do Cloud SQL para confirmar uso de SSL
2. Monitorar por alguns dias
3. Confirmar que todas funcionam com SSL

**Fase 3: Habilitar SSL Obrigatório (Por último)**
1. Apenas quando TODAS as aplicações estiverem usando SSL
2. Habilitar "Permitir somente conexões SSL" no Cloud SQL
3. Monitorar por problemas

---

## 🎯 Opção 1: Via Console GCP (Mais Fácil)

### Passo 1: Acessar a Instância
1. Acesse o [Console do Google Cloud](https://console.cloud.google.com)
2. Navegue até **SQL** → **Instâncias**
3. Clique na instância `comercial-db`

### Passo 2: Configurar Modo SSL ⚠️ NÃO FAÇA ISSO AGORA!

**⚠️ ATENÇÃO:** Não habilite "Permitir somente conexões SSL" até que TODAS as aplicações estejam configuradas para usar SSL!

**Quando estiver pronto (após configurar todas as aplicações):**
1. No menu lateral, clique em **Conexões**
2. Role até a seção **Gerenciar modo SSL**
3. Selecione a opção: **"Permitir somente conexões SSL"**
   - ✅ Esta opção força todas as conexões a usarem SSL/TLS
   - ✅ Não exige certificados de cliente (mais simples)
4. Clique em **Salvar**

**⚠️ Importante:** Esta opção força SSL. Certifique-se de que todas as aplicações já estão usando SSL antes de habilitar!

### Passo 3: Baixar Certificado CA
1. Na mesma página, role até **Certificados SSL**
2. Clique em **Baixar certificado do servidor**
3. Salve o arquivo `server-ca.pem` em local seguro

---

## 🖥️ Opção 2: Via CLI (gcloud)

### Passo 1: Verificar Status Atual
```powershell
gcloud sql instances describe comercial-db --format="yaml(settings.ipConfiguration.requireSsl)"
```

**Resultado atual:** `requireSsl: false` (tráfego não criptografado permitido)

### Passo 1.5: Habilitar SSL Obrigatório (Opção 2) ⚠️ NÃO EXECUTE AGORA!

**⚠️ ATENÇÃO:** Execute este comando APENAS após configurar TODAS as aplicações para usar SSL!

```powershell
# Habilitar SSL obrigatório (sem exigir certificados de cliente)
# ⚠️ NÃO EXECUTE até que todas as aplicações estejam usando SSL!
gcloud sql instances patch comercial-db --require-ssl
```

**Resultado esperado:** `requireSsl: true` (apenas conexões SSL permitidas)

**⚠️ Este comando vai quebrar todas as aplicações que não estão usando SSL!**

### Passo 2: Baixar Certificado CA
```powershell
# Criar diretório para certificados
mkdir -p certs

# Baixar certificado CA do Cloud SQL
gcloud sql ssl-certs create client-cert --instance=comercial-db --format=get-server-ca-cert > certs/server-ca.pem
```

**OU** baixar diretamente do Console (mais fácil):
```powershell
# O certificado pode ser baixado do Console ou via:
gcloud sql instances describe comercial-db --format="get(serverCaCert.cert)"
```

### Passo 3: Verificar Certificado
```powershell
# Verificar se o certificado foi baixado corretamente
Get-Content certs/server-ca.pem
```

---

## 🔧 Configurar Aplicação para Usar SSL

### Passo 1: Adicionar Certificado ao Projeto

1. Criar diretório para certificados:
```powershell
mkdir certs
```

2. Copiar o certificado `server-ca.pem` para `certs/server-ca.pem`

3. Adicionar ao `.gitignore`:
```
certs/*.pem
!certs/.gitkeep
```

### Passo 2: Atualizar `app.py`

Modificar a função `init_db_pool()` para incluir parâmetros SSL:

```python
def init_db_pool():
    """Inicializa o pool de conexões PostgreSQL"""
    global _db_pool
    if _db_pool is None:
        try:
            # Caminho para o certificado CA
            ssl_cert_path = os.path.join(BASE_DIR, 'certs', 'server-ca.pem')
            
            # Parâmetros SSL
            ssl_params = {}
            if os.path.exists(ssl_cert_path):
                ssl_params = {
                    'sslmode': 'verify-ca',  # Verifica o certificado do servidor
                    'sslcert': None,  # Não necessário para Cloud SQL
                    'sslkey': None,   # Não necessário para Cloud SQL
                    'sslrootcert': ssl_cert_path  # Certificado CA do Cloud SQL
                }
                print("🔒 SSL configurado com certificado CA")
            else:
                # Fallback: SSL sem verificação (menos seguro, mas funciona)
                ssl_params = {
                    'sslmode': 'require'  # Exige SSL mas não verifica certificado
                }
                print("⚠️ SSL configurado sem verificação de certificado (modo require)")
            
            _db_pool = pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=50,
                host=os.getenv('PG_HOST'),
                port=os.getenv('PG_PORT'),
                database=os.getenv('PG_DATABASE_HUBSPOT'),
                user=os.getenv('PG_USER'),
                password=os.getenv('PG_PASSWORD'),
                **ssl_params  # Adiciona parâmetros SSL
            )
            print("✅ Pool de conexões PostgreSQL inicializado com SSL (min: 2, max: 50)")
        except Exception as e:
            print(f"❌ Erro ao inicializar pool de conexões: {e}")
            _db_pool = None
    return _db_pool
```

### Passo 3: Modos SSL Disponíveis

| Modo | Descrição | Segurança | Uso |
|------|-----------|-----------|-----|
| `disable` | Sem SSL | ❌ Nenhuma | Não recomendado |
| `allow` | SSL opcional | ⚠️ Baixa | Testes |
| `prefer` | SSL preferido | ⚠️ Média | Transição |
| `require` | SSL obrigatório | ✅ Boa | **Recomendado inicialmente** |
| `verify-ca` | Verifica CA | ✅ Alta | **Recomendado com certificado** |
| `verify-full` | Verifica CA + hostname | ✅ Máxima | Produção |

**Recomendação:** Começar com `require` e depois migrar para `verify-ca` quando o certificado estiver configurado.

---

## 🧪 Testar Conexão SSL

### Via psql (linha de comando)
```powershell
# Instalar psql se não tiver
# Windows: https://www.postgresql.org/download/windows/

# Testar conexão com SSL
$env:PGPASSWORD="sua_senha"
psql -h 35.239.64.56 -p 5432 -U meetrox_user -d hubspot-sync -c "SELECT version();" --set=sslmode=require
```

### Via Python (teste rápido)
```python
import psycopg2
import os

conn = psycopg2.connect(
    host=os.getenv('PG_HOST'),
    port=os.getenv('PG_PORT'),
    database=os.getenv('PG_DATABASE_HUBSPOT'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
    sslmode='require'  # Teste inicial
)

print("✅ Conexão SSL estabelecida com sucesso!")
conn.close()
```

---

## 📝 Checklist de Implementação (Ordem Correta!)

### Fase 1: Configurar Aplicação Black November (FAZER AGORA)
- [ ] 1. Atualizar `init_db_pool()` em `app.py` para usar `sslmode=require`
- [ ] 2. Testar conexão localmente
- [ ] 3. Fazer deploy e testar em produção
- [ ] 4. Verificar logs para confirmar uso de SSL

### Fase 2: Configurar Outras Aplicações (Coordenar com equipe)
- [ ] 5. Metabase - Configurar SSL
- [ ] 6. Grafana - Configurar SSL
- [ ] 7. n8n - Configurar SSL
- [ ] 8. Vaultwarden - Configurar SSL
- [ ] 9. Outras aplicações - Configurar SSL

### Fase 3: Validação (Após todas configuradas)
- [ ] 10. Verificar logs do Cloud SQL (todas usando SSL?)
- [ ] 11. Monitorar por alguns dias
- [ ] 12. Confirmar que nenhuma aplicação está usando conexão não criptografada

### Fase 4: Habilitar SSL Obrigatório (Por último!)
- [ ] 13. **SOMENTE AGORA:** Habilitar "Permitir somente conexões SSL" no Cloud SQL
- [ ] 14. Monitorar por problemas
- [ ] 15. Verificar que todas as aplicações continuam funcionando

---

## 🚀 Deploy no Cloud Run

### Opção 1: Incluir Certificado na Imagem Docker

Adicionar ao `Dockerfile`:
```dockerfile
# Copiar certificado SSL
COPY certs/server-ca.pem /app/certs/server-ca.pem
```

### Opção 2: Usar Secret Manager (Recomendado)

1. Criar secret com o certificado:
```powershell
gcloud secrets create cloud-sql-ca-cert --data-file=certs/server-ca.pem
```

2. Atualizar `cloudbuild.yaml`:
```yaml
- '--set-secrets'
- 'PG_PASSWORD=PG_PASSWORD:latest,CLOUD_SQL_CA_CERT=cloud-sql-ca-cert:latest,...'
```

3. Modificar `app.py` para ler do secret:
```python
ssl_cert_content = os.getenv('CLOUD_SQL_CA_CERT')
if ssl_cert_content:
    # Escrever certificado em arquivo temporário
    ssl_cert_path = '/tmp/server-ca.pem'
    with open(ssl_cert_path, 'w') as f:
        f.write(ssl_cert_content)
    ssl_params['sslrootcert'] = ssl_cert_path
```

---

## ⚠️ Importante

1. **Opções de SSL no Cloud SQL:**
   - **Opção 1 (Atual):** "Permitir tráfego não criptografado" ❌ Não recomendado
   - **Opção 2 (Recomendada):** "Permitir somente conexões SSL" ✅ **Use esta!**
     - Força SSL em todas as conexões
     - Não exige certificados de cliente
     - Permite migração gradual
   - **Opção 3:** "Exigir certificados do cliente confiáveis" ⚠️ Mais complexo
     - Exige certificados de cliente
     - Requer Cloud SQL Proxy ou bibliotecas específicas

2. **Migração gradual recomendada:**
   - **Fase 1:** Configurar Cloud SQL para "Permitir somente conexões SSL" (Opção 2)
   - **Fase 2:** Atualizar aplicações para usar `sslmode=require`
   - **Fase 3 (Opcional):** Migrar para `sslmode=verify-ca` com certificado CA
   - **Fase 4 (Futuro):** Considerar Opção 3 se necessário maior segurança

3. **Monitoramento**:
   - Verificar logs do Cloud SQL para conexões SSL
   - Monitorar erros de conexão após deploy
   - Ter rollback plan caso algo quebre

---

## 📚 Referências

- [Documentação Cloud SQL SSL](https://cloud.google.com/sql/docs/postgres/configure-ssl-instance)
- [psycopg2 SSL](https://www.psycopg.org/docs/module.html#psycopg2.connect)
- [PostgreSQL SSL Modes](https://www.postgresql.org/docs/current/libpq-ssl.html)

