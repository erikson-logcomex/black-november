# Integração com Looker - Guia de Configuração

## 📋 Visão Geral

Este sistema extrai dados do Looker Dashboard usando um navegador headless no backend (Cloud Run). A sessão é mantida através de cookies salvos, evitando a necessidade de fazer login a cada requisição.

## 🔧 Como Funciona

### 1. **Configuração Inicial (Uma Vez)**

Execute o script `setup_looker_session.py` **LOCALMENTE** (não no Cloud Run):

```bash
python setup_looker_session.py
```

**O que acontece:**
- Abre um navegador (visível)
- Você faz login manualmente (email, senha, código 2FA)
- **IMPORTANTE:** Marque o checkbox "Confiar neste navegador" / "Remember this device"
- Os cookies são salvos:
  - Localmente em `data/looker_cookies/looker_session.pkl`
  - No Cloud Storage (se `GCS_BUCKET_NAME` estiver configurado)

### 2. **Uso Automático**

Depois da configuração inicial:
- **Localmente:** O código lê os cookies do arquivo local
- **Cloud Run:** O código lê os cookies do Cloud Storage automaticamente
- Não precisa fazer login novamente até os cookies expirarem

### 3. **Quando os Cookies Expirarem**

Execute `setup_looker_session.py` novamente localmente para renovar os cookies.

## 🌐 Configuração para Cloud Run

### Opção 1: Com Cloud Storage (Recomendado)

1. **Crie um bucket no Google Cloud Storage:**
   ```bash
   gsutil mb gs://seu-bucket-looker-cookies
   ```

2. **Adicione ao `.env`:**
   ```
   GCS_BUCKET_NAME=seu-bucket-looker-cookies
   ```

3. **Configure permissões no Cloud Run:**
   - O Cloud Run precisa ter permissão para ler/escrever no bucket
   - Isso geralmente é automático se o Cloud Run usa a mesma conta de serviço do projeto

### Opção 2: Sem Cloud Storage (Apenas Local)

- Não configure `GCS_BUCKET_NAME`
- Os cookies serão salvos apenas localmente
- **Limitação:** Não funcionará no Cloud Run (só localmente)

## 📝 Passo a Passo Completo

### Passo 1: Configurar Credenciais

Adicione ao `.env`:
```
LOOKER_USERNAME=seu_email@logcomex.com
LOOKER_PASSWORD=sua_senha
GCS_BUCKET_NAME=seu-bucket-looker-cookies  # Opcional, mas recomendado
```

### Passo 2: Executar Setup Inicial (Localmente)

```bash
python setup_looker_session.py
```

Siga as instruções na tela:
1. Faça login no navegador que abrir
2. Quando pedir código 2FA, insira o código
3. **MARQUE o checkbox "Confiar neste navegador"**
4. Aguarde o dashboard carregar
5. Pressione ENTER no terminal

### Passo 3: Testar Localmente

```bash
python utils/looker_scraper.py
```

Ou teste o endpoint da API:
```bash
curl http://localhost:5000/api/looker/gauge-value
```

### Passo 4: Deploy para Cloud Run

```bash
# O código já está pronto, apenas faça o deploy normal
# Os cookies no Cloud Storage serão usados automaticamente
```

## 🔍 Endpoints da API

### GET `/api/looker/gauge-value`

Retorna o valor atual do gauge do Looker:

```json
{
  "gauge_value": 733,
  "gauge_target": 800,
  "remaining": 67,
  "timestamp": "2025-12-11 13:23:50"
}
```

## ⚠️ Troubleshooting

### Cookies Expirados

Se receber erro "Cookies expirados ou inválidos":
1. Execute `setup_looker_session.py` novamente localmente
2. Os novos cookies serão salvos e usados automaticamente

### Cloud Storage Não Funciona

Se `GCS_BUCKET_NAME` não estiver configurado:
- O sistema funciona apenas localmente
- Para usar no Cloud Run, configure o Cloud Storage

### Erro de Permissões no Cloud Storage

Verifique se a conta de serviço do Cloud Run tem permissão:
```bash
gcloud projects add-iam-policy-binding SEU_PROJECT_ID \
  --member="serviceAccount:SEU_SERVICE_ACCOUNT@SEU_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

## 📌 Notas Importantes

1. **O setup deve ser feito LOCALMENTE** (não no Cloud Run), pois precisa de navegador visível para login manual
2. **Marque sempre o checkbox "Confiar neste navegador"** para evitar 2FA em futuras requisições
3. **Os cookies expiram** após alguns dias/semanas - será necessário executar o setup novamente
4. **Cloud Storage é opcional** mas recomendado para funcionar no Cloud Run

