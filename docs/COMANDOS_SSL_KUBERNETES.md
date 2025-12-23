# 🔧 Comandos para Habilitar SSL no Kubernetes

**Data:** 28 de Novembro de 2025  
**Projeto:** datatoopenai

---

## 🎯 n8n (Kubernetes)

### Verificar Configuração Atual
```powershell
kubectl get deployment n8n -n n8n -o yaml | Select-String -Pattern "DB_POSTGRESDB"
```

### Adicionar SSL

**Opção 1: Adicionar variável DB_POSTGRESDB_SSL (Recomendado)**
```powershell
kubectl set env deployment/n8n DB_POSTGRESDB_SSL=true -n n8n
kubectl rollout restart deployment n8n -n n8n
```

**Opção 2: Usar connection string completa**
```powershell
# Primeiro, obter credenciais do secret
kubectl get secret postgres-secret -n n8n -o jsonpath='{.data.POSTGRES_NON_ROOT_USER}' | ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }
kubectl get secret postgres-secret -n n8n -o jsonpath='{.data.POSTGRES_NON_ROOT_PASSWORD}' | ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }

# Depois, adicionar connection string com SSL
kubectl set env deployment/n8n \
  DB_POSTGRESDB_CONNECTION_STRING="postgresql://USER:PASS@172.23.64.3:5432/n8n-postgres-db?sslmode=require" \
  -n n8n
```

### Verificar se Funcionou
```powershell
kubectl logs deployment/n8n -n n8n --tail=50 | Select-String -Pattern "SSL|database|connection"
```

---

## 🎯 n8n-worker (Kubernetes)

**Mesma configuração do n8n:**
```powershell
kubectl set env deployment/n8n-worker DB_POSTGRESDB_SSL=true -n n8n
kubectl rollout restart deployment n8n-worker -n n8n
```

---

## 🎯 Metabase (Kubernetes)

### Verificar Configuração Atual
```powershell
kubectl get deployment metabase-app -n metabase -o yaml | Select-String -Pattern "DATABASE|DB_|POSTGRES"
kubectl get configmap -n metabase
kubectl get secret -n metabase
```

### Adicionar SSL

**Opção 1: Via ConfigMap (se usar)**
```powershell
# Editar ConfigMap
kubectl edit configmap metabase-config -n metabase

# Adicionar/modificar:
# DATABASE_URL=postgresql://user:pass@172.23.64.3:5432/database?sslmode=require
```

**Opção 2: Via Secret**
```powershell
# Ver secret atual
kubectl get secret metabase-db -n metabase -o yaml

# Criar/atualizar secret com SSL
kubectl create secret generic metabase-db \
  --from-literal=DATABASE_URL="postgresql://user:pass@172.23.64.3:5432/database?sslmode=require" \
  -n metabase --dry-run=client -o yaml | kubectl apply -f -
```

**Opção 3: Via Variáveis de Ambiente no Deployment**
```powershell
kubectl set env deployment/metabase-app \
  MB_DB_CONNECTION_URI="postgresql://user:pass@172.23.64.3:5432/database?sslmode=require" \
  -n metabase
```

### Reiniciar
```powershell
kubectl rollout restart deployment metabase-app -n metabase
```

### Verificar
```powershell
kubectl logs deployment/metabase-app -n metabase --tail=50
```

---

## 🎯 evolution-api (Kubernetes)

### Verificar Configuração
```powershell
kubectl get deployment evolution-api -n n8n -o yaml | Select-String -Pattern "DATABASE|DB_|POSTGRES"
```

### Adicionar SSL
```powershell
# Verificar como está configurado primeiro
# Depois adicionar SSL conforme a configuração encontrada
```

---

## 📋 Resumo: Onde Configurar

| Aplicação | Onde Configurar | Como |
|-----------|-----------------|------|
| **Cloud Run** | No código ou variáveis de ambiente | Adicionar `sslmode=require` |
| **Kubernetes** | **DENTRO do Deployment** (variáveis de ambiente) | **NÃO no Ingress!** |
| **Metabase** | ConfigMap/Secret ou interface web | Connection string com `?sslmode=require` |
| **n8n** | Variáveis de ambiente do Deployment | `DB_POSTGRESDB_SSL=true` |

---

## ⚠️ Lembrete Importante

**Ingress SSL ≠ SSL do Banco**

- **Ingress**: HTTPS entre usuário e aplicação (já configurado)
- **SSL do Banco**: SSL entre aplicação e Cloud SQL (precisa configurar)

**Configure SSL do banco DENTRO da aplicação, não no Ingress!**

