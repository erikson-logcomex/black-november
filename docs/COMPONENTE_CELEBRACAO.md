# 🎉 Componente Universal de Celebração de Deals

## 📖 Visão Geral

O componente de celebração é um sistema modular que exibe animações comemorativas quando um deal é ganho. Ele funciona em **todas as páginas** do sistema simultaneamente através de:

- **Server-Sent Events (SSE)** - Notificações em tempo real do backend
- **Componente HTML reutilizável** - Snippet que pode ser incluído em qualquer página
- **JavaScript independente** - Lógica que funciona em qualquer contexto
- **CSS isolado** - Estilos que não interferem com outras páginas

---

## 🚀 Como Usar em uma Nova Página

### Passo 1: Incluir o CSS no `<head>`

```html
<head>
    <!-- ... outros links ... -->
    <link rel="stylesheet" href="/static/css/deal_celebration.css">
</head>
```

### Passo 2: Incluir o Componente HTML no `<body>`

```html
<body>
    <!-- Logo confidencial e outras imagens fixas -->
    <img src="/static/img/confidencial.png" alt="Confidencial" class="confidencial-logo">
    
    <!-- ✅ COMPONENTE DE CELEBRAÇÃO - Inclua logo após as imagens fixas -->
    {% include 'includes/celebration_component.html' %}
    
    <!-- Resto do conteúdo da página -->
    <div class="container">
        <!-- ... seu conteúdo ... -->
    </div>
</body>
```

### Passo 3: Incluir o JavaScript antes de `</body>`

```html
    <!-- Seus scripts -->
    <script src="/static/javascript/sua_pagina.js"></script>
    
    <!-- ✅ SCRIPT DE CELEBRAÇÃO - Inclua por último -->
    <script src="/static/javascript/deal_celebration.js"></script>
</body>
</html>
```

---

## 📁 Estrutura de Arquivos

```
templates/
  └── includes/
      └── celebration_component.html  ← Snippet HTML reutilizável

static/
  ├── css/
  │   └── deal_celebration.css        ← Estilos da celebração
  ├── javascript/
  │   └── deal_celebration.js         ← Lógica do sistema
  └── media/
      ├── chuva_dinheiro.mp4          ← Vídeo de celebração
      ├── musica_silvio_santos.mp3    ← Música de fundo
      └── corneta.mp3                  ← Som de notificação
```

---

## ⚙️ Como Funciona

### 1. Polling Automático
O JavaScript verifica novos deals a cada **3 segundos** através do endpoint:
```javascript
GET /api/deals/pending?client_id={ID}&since={TIMESTAMP}
```

### 2. Filtro de Timestamp
- Sistema armazena timestamp de inicialização da página
- Apenas deals criados **APÓS** esse momento são exibidos
- Evita exibir deals antigos ao recarregar a página

### 3. Fila de Notificações
- Se múltiplos deals chegam ao mesmo tempo, são enfileirados
- Celebrações são exibidas **sequencialmente** (uma por vez)
- Cada celebração dura **30 segundos**

### 4. Sincronização entre TVs
- Cada TV/painel tem um `client_id` único
- Sistema marca deals como "visualizados" por client
- Todas as TVs recebem as mesmas notificações simultaneamente

---

## 🎨 Elementos da Celebração

A celebração exibe:

1. **🎉 Título**: "DEAL GANHO!"
2. **👥 Fotos do Time**: EV, SDR, LDR (se existirem)
3. **💰 Valor**: Formatado em R$
4. **📝 Nome do Deal**: Nome do negócio
5. **🏢 Empresa**: Nome da empresa cliente
6. **🎵 Efeitos**: Som de corneta + vídeo de chuva de dinheiro

---

## 🔧 Configurações

### Intervalos (deal_celebration.js)

```javascript
const CHECK_INTERVAL = 3000;        // 3s - Intervalo de verificação
const ANIMATION_DURATION = 30000;   // 30s - Duração da celebração
```

### Client ID (Identificação do Painel)

O sistema gera automaticamente um ID único para cada painel/TV:
```javascript
const CLIENT_ID = getPanelClientId(); // Ex: "panel-1234567890-abc123"
```

---

## 🎯 Páginas Já Implementadas

- ✅ **Painel 1** - Dashboard Principal (`funnel.html`)
- ✅ **Painel 2** - Metas & Progresso (`metas.html`)

---

## 📋 Checklist para Nova Página

Ao criar uma nova página (ex: Hall da Fama, Timeline):

- [ ] Adicionar `<link rel="stylesheet" href="/static/css/deal_celebration.css">` no `<head>`
- [ ] Incluir `{% include 'includes/celebration_component.html' %}` após imagens fixas
- [ ] Adicionar `<script src="/static/javascript/deal_celebration.js"></script>` antes de `</body>`
- [ ] Testar celebração usando botão 💰 (canto superior esquerdo)

---

## 🐛 Troubleshooting

### Celebração não aparece
1. Verifique o console do navegador para erros
2. Confirme que o endpoint `/api/deals/pending` está respondendo
3. Teste manualmente com o botão 💰

### Áudio não toca
1. Navegadores bloqueiam áudio sem interação do usuário
2. Sistema tenta desbloquear automaticamente
3. Se necessário, toque na tela uma vez para desbloquear

### Celebração aparece múltiplas vezes
1. Verifique se não há múltiplas inclusões do script
2. Confirme que o `client_id` está sendo gerado corretamente
3. Verifique logs no console: "Notificação já foi processada"

---

## 🔮 Futuras Melhorias

- [ ] **SSE (Server-Sent Events)**: Substituir polling por conexão persistente
- [ ] **Badges/Conquistas**: Integrar com sistema de gamificação
- [ ] **Som Personalizado**: Sons diferentes por tipo de deal
- [ ] **Animações Variadas**: Múltiplos estilos de celebração

---

## 📞 Suporte

Em caso de dúvidas ou problemas, consulte:
- Arquivo: `static/javascript/deal_celebration.js` (código comentado)
- Logs do console do navegador (F12)
- Documentação do backend: `/api/deals/pending`

---

**Última atualização:** 12/11/2025  
**Versão:** 2.0 (Componente Universal)
