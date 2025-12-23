/**
 * Hall da Fama - Black November
 * Sistema de badges e conquistas em tempo real
 */

// Estado Global
let currentSlide = 0;
const totalSlides = 4;
let slideInterval = null;
let dataCache = {
    evs: null,
    sdrsNew: null,
    sdrsExpansao: null,
    ldrs: null
};

// Configurações
const SLIDE_DURATION = 20000; // 20 segundos por slide
const REFRESH_INTERVAL = 120000; // Atualiza dados a cada 2 minutos

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎮 Hall da Fama inicializado');
    
    // Carrega dados iniciais e aguarda conclusão
    await loadAllData();
    
    // Só inicia rotação APÓS os dados estarem carregados
    console.log('✅ Dados carregados, iniciando rotação de slides...');
    startSlideRotation();
    
    // Atualização periódica dos dados (apenas se NÃO estiver no modo aleatório)
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('aleatorio')) {
    setInterval(loadAllData, REFRESH_INTERVAL);
    } else {
        console.log('📦 Modo aleatório: atualizações periódicas desabilitadas (usando cache centralizado)');
    }
    
    // Event listeners para indicadores
    setupIndicators();
});

// ============================================================================
// CARREGAMENTO DE DADOS
// ============================================================================

// Função auxiliar para fetch com timeout
async function fetchWithTimeout(url, timeout = 30000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error(`Timeout: requisição demorou mais de ${timeout/1000}s`);
        }
        throw error;
    }
}

async function loadAllData() {
    console.log('🔄 Atualizando dados do Hall da Fama...');
    
    // Verifica se está no modo aleatório (fora do try/catch para evitar redeclaração)
    const urlParams = new URLSearchParams(window.location.search);
    const isRandomMode = urlParams.has('aleatorio');
    
    try {
        // Cache busting: adiciona timestamp para evitar cache do navegador
        const timestamp = new Date().getTime();
        
        // Usa cache se estiver no modo aleatório
        const useCacheParam = isRandomMode ? '&use_cache=true' : '';
        
        // Carrega dados de todos os perfis em paralelo com timeout de 30s cada
        const [evsData, sdrsNewData, sdrsExpansaoData, ldrsData] = await Promise.all([
            fetchWithTimeout(`/api/hall-da-fama/evs-realtime?_=${timestamp}${useCacheParam}`, 30000).then(r => r.json()),
            fetchWithTimeout(`/api/hall-da-fama/sdrs-realtime?pipeline=6810518&_=${timestamp}${useCacheParam}`, 30000).then(r => r.json()),
            fetchWithTimeout(`/api/hall-da-fama/sdrs-realtime?pipeline=4007305&_=${timestamp}${useCacheParam}`, 30000).then(r => r.json()),
            fetchWithTimeout(`/api/hall-da-fama/ldrs-realtime?_=${timestamp}${useCacheParam}`, 30000).then(r => r.json())
        ]);
        
        // Atualiza cache
        dataCache.evs = evsData;
        dataCache.sdrsNew = sdrsNewData;
        dataCache.sdrsExpansao = sdrsExpansaoData;
        dataCache.ldrs = ldrsData;
        
        // Renderiza slides
        renderEvs(evsData);
        renderSdrs(sdrsNewData, 'New');
        renderSdrs(sdrsExpansaoData, 'Expansao');
        renderLdrs(ldrsData);
        
        // Esconde loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('hallSlides').style.display = 'block';
        document.getElementById('slideIndicators').style.display = 'flex';
        
        console.log('✅ Dados atualizados com sucesso');
        
        // Inicia timer de navegação após dados carregados (apenas no modo aleatório)
        if (isRandomMode) {
            startNavigationTimer();
        }
        
        return true; // Indica sucesso no carregamento
        
    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        
        // Mesmo com erro, mostra a página com estado vazio para não travar
        document.getElementById('loading').style.display = 'none';
        document.getElementById('hallSlides').style.display = 'block';
        document.getElementById('slideIndicators').style.display = 'flex';
        
        // Mostra mensagem de erro em todos os slides
        showEmptyState('slideEvs');
        showEmptyState('slideSdrsNew');
        showEmptyState('slideSdrsExpansao');
        showEmptyState('slideLdrs');
        
        // Inicia timer de navegação mesmo com erro (apenas no modo aleatório)
        if (isRandomMode) {
            startNavigationTimer();
        }
        
        return false; // Indica falha no carregamento
    }
}

// ============================================================================
// RENDERIZAÇÃO - EVs
// ============================================================================

function renderEvs(data) {
    console.log('🎨 Renderizando EVs...', data);
    
    if (!data || !data.data || data.data.length === 0) {
        console.warn('⚠️ Dados de EVs vazios ou inválidos');
        showEmptyState('slideEvs');
        return;
    }
    
    const ranking = data.data;
    console.log(`✅ ${ranking.length} EVs para renderizar`);
    const mvp = ranking[0]; // Primeiro colocado
    
    // Renderiza MVP
    const mvpName = mvp.userName || `EV ${mvp.userId}`;
    const photoPath = getPhotoPath(mvpName);
    
    document.getElementById('mvpEvsPhoto').src = photoPath;
    document.getElementById('mvpEvsName').textContent = mvpName;
    document.getElementById('mvpEvsDeals').textContent = mvp.dealCount;
    document.getElementById('mvpEvsRevenue').textContent = formatCurrency(mvp.revenue);
    
    // Renderiza badges do MVP (apenas emojis empilhados)
    const mvpCard = document.getElementById('mvpEvs');
    renderMvpBadgesStack(mvpCard, mvp.badges);
    
    // Renderiza Top 5
    const listContainer = document.getElementById('topEvsList');
    listContainer.innerHTML = '';
    
    console.log('📝 Adicionando EVs ao ranking:');
    ranking.forEach((ev, index) => {
        console.log(`   ${index + 1}. ${ev.userName} - ${ev.dealCount} deals`);
        const li = createRankingItem({
            position: ev.position,
            name: ev.userName || `EV ${ev.userId}`,
            photo: getPhotoPath(ev.userName || ''),
            stats: `${ev.dealCount} deals • ${formatCurrency(ev.revenue)}`,
            badges: ev.badges
        });
        listContainer.appendChild(li);
    });
    
    console.log(`✅ ${listContainer.children.length} itens renderizados no DOM`);
    
    // Aplica Twemoji após renderizar EVs
    if (typeof twemoji !== 'undefined') {
        twemoji.parse(document.body, {
            base: 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/'
        });
    }
}

// ============================================================================
// RENDERIZAÇÃO - SDRs
// ============================================================================

function renderSdrs(data, pipeline) {
    const slideId = `slideSdrs${pipeline}`;
    
    if (!data || !data.data || data.data.length === 0) {
        showEmptyState(slideId);
        return;
    }
    
    const ranking = data.data;
    const mvp = ranking[0];
    
    // Renderiza MVP
    const mvpName = mvp.userName || `SDR ${mvp.userId}`;
    const photoPath = getPhotoPath(mvpName);
    
    document.getElementById(`mvpSdrs${pipeline}Photo`).src = photoPath;
    document.getElementById(`mvpSdrs${pipeline}Name`).textContent = mvpName;
    document.getElementById(`mvpSdrs${pipeline}Scheduled`).textContent = mvp.scheduledCount;
    
    // Renderiza badges do MVP (apenas emojis empilhados)
    const mvpCard = document.getElementById(`mvpSdrs${pipeline}`);
    renderMvpBadgesStack(mvpCard, mvp.badges);
    
    // Renderiza Top 5
    const listContainer = document.getElementById(`topSdrs${pipeline}List`);
    listContainer.innerHTML = '';
    
    ranking.forEach((sdr, index) => {
        const li = createRankingItem({
            position: sdr.position,
            name: sdr.userName || `SDR ${sdr.userId}`,
            photo: getPhotoPath(sdr.userName || ''),
            stats: `${sdr.scheduledCount} agendamento${sdr.scheduledCount > 1 ? 's' : ''}`,
            badges: sdr.badges
        });
        listContainer.appendChild(li);
    });
    
    // Aplica Twemoji após renderizar SDRs
    if (typeof twemoji !== 'undefined') {
        twemoji.parse(document.body, {
            base: 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/'
        });
    }
}

// ============================================================================
// RENDERIZAÇÃO - LDRs
// ============================================================================

function renderLdrs(data) {
    if (!data || !data.data || data.data.length === 0) {
        showEmptyState('slideLdrs');
        return;
    }
    
    const ranking = data.data;
    const mvp = ranking[0];
    
    // Renderiza MVP
    const mvpName = mvp.userName || `LDR ${mvp.userId}`;
    const photoPath = getPhotoPath(mvpName);
    
    document.getElementById('mvpLdrsPhoto').src = photoPath;
    document.getElementById('mvpLdrsName').textContent = mvpName;
    document.getElementById('mvpLdrsDeals').textContent = mvp.wonDealsCount;
    document.getElementById('mvpLdrsRevenue').textContent = formatCurrency(mvp.revenue);
    
    // Renderiza badges do MVP (apenas emojis empilhados)
    const mvpCard = document.getElementById('mvpLdrs');
    renderMvpBadgesStack(mvpCard, mvp.badges);
    
    // Renderiza Top 5
    const listContainer = document.getElementById('topLdrsList');
    listContainer.innerHTML = '';
    
    ranking.forEach((ldr, index) => {
        const li = createRankingItem({
            position: ldr.position,
            name: ldr.userName || `LDR ${ldr.userId}`,
            photo: getPhotoPath(ldr.userName || ''),
            stats: `${ldr.wonDealsCount} deals • ${formatCurrency(ldr.revenue)}`,
            badges: ldr.badges
        });
        listContainer.appendChild(li);
    });
    
    // Aplica Twemoji após renderizar LDRs
    if (typeof twemoji !== 'undefined') {
        twemoji.parse(document.body, {
            base: 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/'
        });
    }
}

// ============================================================================
// COMPONENTES VISUAIS
// ============================================================================

function createBadgeElement(badge) {
    const div = document.createElement('div');
    div.className = `badge-item ${badge.category}`;
    div.textContent = badge.name;
    div.title = `Categoria: ${badge.category}`;
    return div;
}

function renderMvpBadgesStack(mvpCard, badges) {
    // Remove stack anterior se existir
    const existingStack = mvpCard.querySelector('.mvp-badges-emoji-stack');
    if (existingStack) {
        existingStack.remove();
    }
    
    // Cria container de badges empilhados
    const stack = document.createElement('div');
    stack.className = 'mvp-badges-emoji-stack';
    
    // Renderiza cada badge (imagem ou emoji)
    badges.forEach((badge, index) => {
        const badgeCode = badge.code;
        const badgeImagePath = `/static/img/badges/${badgeCode}.png`;
        
        // Verifica se existe imagem personalizada para este badge
        const img = new Image();
        img.src = badgeImagePath;
        
        img.onload = () => {
            // Imagem existe, usa a imagem
            const imgElement = document.createElement('img');
            imgElement.className = 'mvp-badge-emoji mvp-badge-image';
            imgElement.src = badgeImagePath;
            imgElement.alt = badge.name;
            imgElement.title = badge.name; // Tooltip com nome completo
            
            // Substitui o span temporário pela imagem
            const tempSpan = stack.children[index];
            if (tempSpan) {
                stack.replaceChild(imgElement, tempSpan);
            }
        };
        
        img.onerror = () => {
            // Imagem não existe, mantém o emoji (já adicionado abaixo)
            console.log(`Badge ${badgeCode} sem imagem, usando emoji`);
        };
        
        // Adiciona emoji temporariamente (será substituído por imagem se existir)
        const emoji = badge.name.split(' ')[0]; // Pega apenas o emoji
        const emojiSpan = document.createElement('span');
        emojiSpan.className = 'mvp-badge-emoji';
        emojiSpan.textContent = emoji;
        emojiSpan.title = badge.name; // Tooltip com nome completo
        stack.appendChild(emojiSpan);
    });
    
    // Adiciona ao card
    mvpCard.appendChild(stack);
}

function createRankingItem(data) {
    const li = document.createElement('li');
    li.className = 'ranking-item';
    li.style.animationDelay = `${(data.position - 1) * 0.1}s`;
    
    // Classe especial para top 3
    let positionClass = '';
    if (data.position === 1) positionClass = 'gold';
    else if (data.position === 2) positionClass = 'silver';
    else if (data.position === 3) positionClass = 'bronze';
    
    // Medal emoji para top 3
    let medal = '';
    if (data.position === 1) medal = '🥇';
    else if (data.position === 2) medal = '🥈';
    else if (data.position === 3) medal = '🥉';
    else medal = `${data.position}º`;
    
    li.innerHTML = `
        <div class="ranking-position ${positionClass}">${medal}</div>
        <img class="ranking-photo" src="${data.photo}" alt="${data.name}">
        <div class="ranking-info">
            <div class="ranking-name">${data.name}</div>
            <div class="ranking-stats">${data.stats}</div>
            <div class="ranking-badges" data-ranking-badges></div>
        </div>
    `;
    
    // Renderiza badges com imagens (mesma lógica do MVP)
    const badgesContainer = li.querySelector('[data-ranking-badges]');
    data.badges.forEach((badge, index) => {
        const badgeCode = badge.code;
        const badgeImagePath = `/static/img/badges/${badgeCode}.png`;
        
        // Verifica se existe imagem personalizada para este badge
        const img = new Image();
        img.src = badgeImagePath;
        
        // Adiciona emoji temporariamente (será substituído por imagem se existir)
        const emoji = badge.name.split(' ')[0]; // Pega apenas o emoji
        const emojiSpan = document.createElement('span');
        emojiSpan.className = 'ranking-badge';
        emojiSpan.textContent = emoji;
        emojiSpan.title = badge.name; // Tooltip com nome completo
        badgesContainer.appendChild(emojiSpan);
        
        img.onload = () => {
            // Imagem existe, usa a imagem
            const imgElement = document.createElement('img');
            imgElement.className = 'ranking-badge ranking-badge-image';
            imgElement.src = badgeImagePath;
            imgElement.alt = badge.name;
            imgElement.title = badge.name; // Tooltip com nome completo
            
            // Substitui o span temporário pela imagem
            const tempSpan = badgesContainer.children[index];
            if (tempSpan) {
                badgesContainer.replaceChild(imgElement, tempSpan);
            }
        };
        
        img.onerror = () => {
            // Imagem não existe, mantém o emoji
            console.log(`Badge image not found: ${badgeImagePath}, using emoji fallback`);
        };
    });
    
    return li;
}

function showEmptyState(slideId) {
    const slide = document.getElementById(slideId);
    const profileSection = slide.querySelector('.profile-section');
    
    profileSection.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">🏆</div>
            <div class="empty-state-text">
                Nenhum dado disponível hoje.<br>
                <small>Aguardando conquistas...</small>
            </div>
        </div>
    `;
}

// ============================================================================
// SISTEMA DE SLIDES
// ============================================================================

function startSlideRotation() {
    slideInterval = setInterval(() => {
        nextSlide();
    }, SLIDE_DURATION);
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    showSlide(currentSlide);
}

function showSlide(index) {
    // Remove classe active de todos os slides
    document.querySelectorAll('.hall-slide').forEach(slide => {
        slide.classList.remove('active');
    });
    
    // Remove classe active de todos os indicadores
    document.querySelectorAll('.indicator').forEach(indicator => {
        indicator.classList.remove('active');
    });
    
    // Ativa o slide e indicador corretos
    const slides = document.querySelectorAll('.hall-slide');
    const indicators = document.querySelectorAll('.indicator');
    
    if (slides[index]) slides[index].classList.add('active');
    if (indicators[index]) indicators[index].classList.add('active');
    
    currentSlide = index;
}

function setupIndicators() {
    document.querySelectorAll('.indicator').forEach(indicator => {
        indicator.addEventListener('click', (e) => {
            const slideIndex = parseInt(e.target.dataset.slide);
            showSlide(slideIndex);
            
            // Reseta o intervalo de rotação
            clearInterval(slideInterval);
            startSlideRotation();
        });
    });
}

// ============================================================================
// UTILITÁRIOS
// ============================================================================

function getPhotoPath(name) {
    if (!name) return '/static/img/team/placeholder.png';
    
    // Normaliza o nome: lowercase, remove acentos, substitui espaços por _
    const normalized = name
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Remove acentos
        .replace(/\s+/g, '_') // Espaços para underscores
        .replace(/[^a-z0-9_]/g, ''); // Remove caracteres especiais
    
    const photoPath = `/static/img/team/${normalized}.png`;
    
    // Tenta carregar a imagem, se falhar usa placeholder
    const img = new Image();
    img.src = photoPath;
    img.onerror = () => {
        return '/static/img/team/placeholder.png';
    };
    
    return photoPath;
}

function formatCurrency(value) {
    if (!value || value === 0) return 'R$ 0';
    
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// ============================================================================
// TIMER DE NAVEGAÇÃO (para rotação automática)
// ============================================================================

function startNavigationTimer() {
    // Verifica se está no modo de rotação automática
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('aleatorio')) {
        console.log('⏸️ Modo aleatório não ativo, timer de navegação não iniciado');
        return; // Não está no modo aleatório, não inicia timer
    }
    
    // Detecta o tema baseado na URL atual
    const currentPath = window.location.pathname;
    const theme = currentPath.includes('/black-november') ? 'black-november' : 'natal';
    const STORAGE_KEY = `panel_index_${theme}`;
    const panels = theme === 'black-november'
        ? ['/black-november', '/black-november/metas', '/black-november/hall-da-fama', '/black-november/destaques']
        : ['/natal', '/natal/metas', '/natal/hall-da-fama', '/natal/destaques'];
    // Tempo total = 4 slides x 20s = 80 segundos
    const DURATION = totalSlides * SLIDE_DURATION; // 80 segundos (soma dos 4 slides)
    
    console.log('⏱️ Timer de navegação iniciado:', DURATION / 1000, 'segundos');
    console.log('📋 Painéis disponíveis:', panels);
    console.log('🔑 Storage key:', STORAGE_KEY);
    
    let retryCount = 0;
    const MAX_RETRIES = 30; // Max 30 retries (60 seconds)

    const tryNavigate = () => {
        if (typeof window.isCelebrationActive === 'function' && window.isCelebrationActive()) {
            if (retryCount < MAX_RETRIES) {
                console.log(`⏸️ Celebração ativa, aguardando para trocar de painel... Tentativa ${retryCount + 1}/${MAX_RETRIES}`);
                retryCount++;
                setTimeout(tryNavigate, 2000); // Tenta novamente em 2 segundos
                return;
            } else {
                console.warn('⚠️ Máximo de tentativas atingido. Forçando troca de painel mesmo com celebração ativa.');
            }
        }
        
        // Verifica se os dados ainda estão carregando (loading visível)
        const loadingElement = document.getElementById('loading');
        if (loadingElement && loadingElement.style.display !== 'none') {
            console.log('⏸️ Dados ainda carregando, aguardando mais 5 segundos...');
            // Aguarda mais 5 segundos e tenta novamente
            setTimeout(tryNavigate, 5000);
            return;
        }
        
        console.log('✅ Trocando de painel...');
        // Encontra o índice atual baseado na URL, ou usa o do localStorage
        let currentIdx = panels.findIndex(panel => window.location.pathname === panel || window.location.pathname.startsWith(panel + '/'));
        if (currentIdx === -1) {
            currentIdx = parseInt(localStorage.getItem(STORAGE_KEY) || '0', 10);
        }
        console.log('📊 Índice atual:', currentIdx);
        let idx = (currentIdx + 1) % panels.length;
        console.log('📊 Próximo índice:', idx);
        console.log('📊 Próximo painel:', panels[idx]);
        localStorage.setItem(STORAGE_KEY, idx);
        const nextUrl = panels[idx] + '?aleatorio=1';
        console.log('🚀 Navegando para:', nextUrl);
        window.location.href = nextUrl;
    };
    
    setTimeout(() => {
        tryNavigate();
    }, DURATION);
}

// ============================================================================
// EXPORTAÇÕES PARA DEBUG
// ============================================================================

window.hallDaFama = {
    loadAllData,
    showSlide,
    nextSlide,
    dataCache,
    toggleLegend: () => {
        const legend = document.getElementById('badgesLegend');
        legend.classList.toggle('show');
    }
};

console.log('✅ Hall da Fama carregado - Use window.hallDaFama para debug');
