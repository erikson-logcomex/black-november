# 🔍 Análise: pgbouncer no Cluster n8n

**Data:** 28 de Novembro de 2025  
**Cluster:** n8n-cluster  
**Namespace:** n8n

---

## 📊 Status Atual

### pgbouncer Deployment
- **Status:** ⚠️ 0/1 (não está rodando)
- **Erro:** `ImagePullBackOff` - não consegue baixar a imagem `pgbouncer/pgbouncer:1.21.0`
- **Criado em:** 30 de Setembro de 2025
- **Última tentativa:** 8 de Novembro de 2025 (timeout)

### Service pgbouncer
- **Tipo:** ClusterIP
- **Porta:** 6432/TCP
- **IP:** 34.118.225.64
- **Status:** Criado, mas não está sendo usado

---

## ❓ O que é pgbouncer?

**pgbouncer NÃO é uma instância do PostgreSQL!**

É um **connection pooler** (pool de conexões) que funciona como um **proxy** entre aplicações e o banco de dados:

```
Aplicação → pgbouncer → PostgreSQL
```

**Vantagens:**
- Reduz número de conexões ao banco
- Reutiliza conexões
- Melhora performance em alta concorrência

---

## 🔍 Verificação: n8n está usando pgbouncer?

### ❌ NÃO! O n8n está conectando DIRETAMENTE ao Cloud SQL

**Configuração do n8n:**
```yaml
DB_POSTGRESDB_HOST: 172.23.64.3  # ← IP do Cloud SQL (direto!)
DB_POSTGRESDB_PORT: 5432
DB_POSTGRESDB_DATABASE: n8n-postgres-db
```

**Se estivesse usando pgbouncer, seria:**
```yaml
DB_POSTGRESDB_HOST: pgbouncer-service.n8n.svc.cluster.local  # ← Service do pgbouncer
DB_POSTGRESDB_PORT: 6432  # ← Porta do pgbouncer (não 5432)
```

---

## ✅ Conclusão

1. **pgbouncer foi configurado** mas **nunca funcionou** (erro ao baixar imagem)
2. **n8n está usando Cloud SQL diretamente** (não precisa do pgbouncer)
3. **pgbouncer não está causando problemas** (só está ocupando espaço)

---

## 🎯 Recomendações

### Opção 1: Remover pgbouncer (Recomendado)

Se não está sendo usado e nunca funcionou, pode ser removido:

```powershell
# Remover deployment
kubectl delete deployment pgbouncer -n n8n

# Remover service (se não for usado por outras aplicações)
kubectl delete service pgbouncer-service -n n8n
```

### Opção 2: Corrigir e usar pgbouncer

Se quiser usar pgbouncer para otimizar conexões:

1. **Corrigir erro de imagem:**
   - Verificar se a imagem `pgbouncer/pgbouncer:1.21.0` existe
   - Ou usar outra tag/versão

2. **Configurar n8n para usar pgbouncer:**
   ```powershell
   kubectl set env deployment/n8n \
     DB_POSTGRESDB_HOST=pgbouncer-service.n8n.svc.cluster.local \
     DB_POSTGRESDB_PORT=6432 \
     -n n8n
   ```

3. **Adicionar SSL no pgbouncer:**
   - Configurar pgbouncer para usar SSL ao conectar no Cloud SQL
   - Configurar n8n para usar SSL ao conectar no pgbouncer

---

## 📋 Para SSL

**Como o n8n conecta diretamente ao Cloud SQL:**
- ✅ Configure SSL **diretamente no n8n** (não precisa do pgbouncer)
- ✅ Use `DB_POSTGRESDB_SSL=true` no deployment do n8n

**Se decidir usar pgbouncer no futuro:**
- Configure SSL no pgbouncer → Cloud SQL
- Configure SSL no n8n → pgbouncer

---

## ⚠️ Importante

**O pgbouncer NÃO afeta a configuração de SSL do n8n!**

Como o n8n está conectando diretamente ao Cloud SQL, você só precisa configurar SSL no n8n, ignorando o pgbouncer.

