# 📸 Fotos do Time Comercial

Esta pasta contém as fotos dos membros do time comercial que aparecem nas animações de celebração de deals.

## 📋 Formato dos Arquivos

### Nomenclatura
As fotos devem ser nomeadas seguindo o padrão:
- **Nome do arquivo**: `nome_completo_normalizado.png`
- **Exemplo**: `joao_silva.png`, `maria_santos.png`

### Normalização de Nomes
O sistema normaliza os nomes recebidos do HubSpot:
1. Converte para minúsculas
2. Remove acentos (á → a, ç → c)
3. Substitui espaços por underscore
4. Remove caracteres especiais

**Exemplos:**
- "João Silva" → `joao_silva.png`
- "Maria Santos" → `maria_santos.png`
- "Carlos José" → `carlos_jose.png`
- "Ana Paula" → `ana_paula.png`

### Formato da Imagem
- **Extensão**: `.png` (recomendado) ou `.jpg`
- **Tamanho**: 300x300px ou maior (será redimensionado para 150x150px na animação)
- **Formato**: Quadrado (1:1) funciona melhor
- **Background**: Transparente ou fundo branco

## 🖼️ Imagem Padrão

Se uma foto não for encontrada, o sistema usará:
- `/static/img/team/default.png`

**Importante**: Crie uma imagem `default.png` como fallback para membros do time sem foto.

## 📝 Como Adicionar Fotos

1. Obtenha a foto do membro do time
2. Normalize o nome conforme as regras acima
3. Salve na pasta `static/img/team/` com o nome normalizado
4. Exemplo: Se o nome no HubSpot é "João Silva", salve como `joao_silva.png`

## ✅ Checklist

- [ ] Criar imagem `default.png` para fallback
- [ ] Adicionar fotos de todos os executivos de vendas
- [ ] Adicionar fotos de todos os SDRs
- [ ] Adicionar fotos de todos os LDRs
- [ ] Testar se os nomes estão sendo normalizados corretamente








