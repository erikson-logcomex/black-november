/**
 * Sistema de Ranking de Top 5 EVs e SDRs com SLIDER
 * Alterna automaticamente entre rankings e atualiza dados
 */

// Intervalo de atualização dos dados (30 segundos)
const RANKING_UPDATE_INTERVAL = 30000;

// Intervalo de troca de slides (12 segundos)
const SLIDE_CHANGE_INTERVAL = 12000;

// Mapeamento de medalhas por posição (apenas top 3)
const MEDALS = {
    1: '🥇',
    2: '🥈',
    3: '🥉',
    4: '4º',
    5: '5º'
};

// Estado do slider
let currentSlide = 0;
let slideInterval = null;

// Estado anterior dos rankings para detectar mudanças
let previousEVsRanking = [];
let previousSDRsNewRanking = [];
let previousSDRsExpansaoRanking = [];
let previousLDRsRanking = [];

/**
 * Busca o ranking de EVs do backend
 */
async function fetchTopEVsRanking() {
    try {
        const response = await fetch('/api/top-evs-today');
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.data || [];
        } else {
            console.error('Erro ao buscar ranking de EVs:', data.error);
            return [];
        }
    } catch (error) {
        console.error('Erro ao buscar ranking de EVs:', error);
        return [];
    }
}

/**
 * Busca o ranking de SDRs NEW do backend
 */
async function fetchTopSDRsNewRanking() {
    try {
        const response = await fetch('/api/top-sdrs-today?pipeline=6810518');
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.data || [];
        } else {
            console.error('Erro ao buscar ranking de SDRs NEW:', data.error);
            return [];
        }
    } catch (error) {
        console.error('Erro ao buscar ranking de SDRs NEW:', error);
        return [];
    }
}

/**
 * Busca o ranking de SDRs Expansão do backend
 */
async function fetchTopSDRsExpansaoRanking() {
    try {
        const response = await fetch('/api/top-sdrs-today?pipeline=4007305');
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.data || [];
        } else {
            console.error('Erro ao buscar ranking de SDRs Expansão:', data.error);
            return [];
        }
    } catch (error) {
        console.error('Erro ao buscar ranking de SDRs Expansão:', error);
        return [];
    }
}

/**
 * Busca o ranking de LDRs do backend
 */
async function fetchTopLDRsRanking() {
    try {
        const response = await fetch('/api/top-ldrs-today');
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.data || [];
        } else {
            console.error('Erro ao buscar ranking de LDRs:', data.error);
            return [];
        }
    } catch (error) {
        console.error('Erro ao buscar ranking de LDRs:', error);
        return [];
    }
}

/**
 * Verifica se houve mudança de posição no ranking de EVs
 */
function detectEVPositionChanges(newRanking) {
    const changes = [];
    
    newRanking.forEach((newEv) => {
        const oldEv = previousEVsRanking.find(ev => ev.ownerName === newEv.ownerName);
        
        if (oldEv && oldEv.position !== newEv.position) {
            changes.push({
                ownerId: newEv.ownerId,
                oldPosition: oldEv.position,
                newPosition: newEv.position,
                moved: oldEv.position > newEv.position ? 'up' : 'down'
            });
        }
    });
    
    return changes;
}

/**
 * Formata valor monetário com centavos (específico para o ranking)
 */
function formatCurrencyWithCents(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

/**
 * Verifica se existe foto para o analista
 */
function getPhotoPath(ownerName) {
    if (!ownerName) return null;
    
    // Remove acentos e normaliza o nome
    const normalized = ownerName
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '_');
    
    return `/static/img/team/${normalized}.png`;
}

/**
 * Cria elemento HTML para um EV no ranking
 */
function createEVElement(ev, isNew = false) {
    const li = document.createElement('li');
    li.className = 'top-ev-item';
    li.dataset.ownerId = ev.ownerId;
    
    if (isNew) {
        li.style.opacity = '0';
        setTimeout(() => {
            li.style.transition = 'opacity 0.5s ease';
            li.style.opacity = '1';
        }, 50);
    }
    
    // Medal/Posição
    const medal = MEDALS[ev.position] || ev.position;
    
    // Foto
    const photoPath = getPhotoPath(ev.ownerName);
    const photoHtml = photoPath 
        ? `<img src="${photoPath}" alt="${ev.ownerName}" class="ev-photo" onerror="this.parentNode.innerHTML='<div class=\\'ev-photo-placeholder\\'>${ev.ownerName.charAt(0).toUpperCase()}</div><div class=\\'ev-position\\'>${medal}</div>'">` 
        : `<div class="ev-photo-placeholder">${ev.ownerName.charAt(0).toUpperCase()}</div>`;
    
    li.innerHTML = `
        <div class="ev-photo-wrapper">
            ${photoHtml}
            ${medal ? `<div class="ev-position">${medal}</div>` : ''}
        </div>
        <div class="ev-info">
            <p class="ev-name">${ev.ownerName}</p>
            <p class="ev-revenue">${formatCurrencyWithCents(ev.revenue)}</p>
            <p class="ev-deals">${ev.dealCount} deal${ev.dealCount !== 1 ? 's' : ''}</p>
        </div>
    `;
    
    return li;
}

/**
 * Renderiza o ranking de EVs na tela
 */
function renderEVsRanking(ranking, positionChanges = []) {
    const container = document.getElementById('topEvsList');
    const emptyState = document.getElementById('topEvsEmpty');
    
    if (!container || !emptyState) {
        console.error('Elementos do ranking de EVs não encontrados no DOM');
        return;
    }
    
    // Se não há dados, mostra estado vazio
    if (!ranking || ranking.length === 0) {
        container.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    // Esconde estado vazio e mostra lista
    emptyState.style.display = 'none';
    container.style.display = 'block';
    
    // Limpa lista atual
    container.innerHTML = '';
    
    // Adiciona cada EV ao ranking
    ranking.forEach((ev) => {
        const evElement = createEVElement(ev);
        
        // Se houve mudança de posição, anima
        const change = positionChanges.find(c => c.ownerName === ev.ownerName);
        if (change) {
            const positionEl = evElement.querySelector('.ev-position');
            positionEl.classList.add('ev-position-change');
            
            setTimeout(() => {
                positionEl.classList.remove('ev-position-change');
            }, 600);
        }
        
        container.appendChild(evElement);
    });
}

/**
 * Cria elemento HTML para um SDR no ranking
 */
function createSDRElement(sdr, isNew = false) {
    const li = document.createElement('li');
    li.className = 'top-ev-item';
    li.dataset.sdrName = sdr.sdrName;
    
    if (isNew) {
        li.style.opacity = '0';
        setTimeout(() => {
            li.style.transition = 'opacity 0.5s ease';
            li.style.opacity = '1';
        }, 50);
    }
    
    // Medal/Posição
    const medal = MEDALS[sdr.position] || sdr.position;
    
    // Foto
    const photoPath = getPhotoPath(sdr.sdrName);
    const photoHtml = photoPath 
        ? `<img src="${photoPath}" alt="${sdr.sdrName}" class="ev-photo" onerror="this.parentNode.innerHTML='<div class=\\'ev-photo-placeholder\\'>${sdr.sdrName.charAt(0).toUpperCase()}</div><div class=\\'ev-position\\'>${medal}</div>'">` 
        : `<div class="ev-photo-placeholder">${sdr.sdrName.charAt(0).toUpperCase()}</div>`;
    
    li.innerHTML = `
        <div class="ev-photo-wrapper">
            ${photoHtml}
            ${medal ? `<div class="ev-position">${medal}</div>` : ''}
        </div>
        <div class="ev-info">
            <p class="ev-name">${sdr.sdrName}</p>
            <p class="ev-revenue">${sdr.scheduledCount} agendamento${sdr.scheduledCount !== 1 ? 's' : ''}</p>
        </div>
    `;
    
    return li;
}

/**
 * Renderiza o ranking de SDRs NEW na tela
 */
function renderSDRsNewRanking(ranking, positionChanges = []) {
    const container = document.getElementById('topSdrsNewList');
    const emptyState = document.getElementById('topSdrsNewEmpty');
    
    if (!container || !emptyState) {
        console.error('Elementos do ranking de SDRs NEW não encontrados no DOM');
        return;
    }
    
    // Se não há dados, mostra estado vazio
    if (!ranking || ranking.length === 0) {
        container.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    // Esconde estado vazio e mostra lista
    emptyState.style.display = 'none';
    container.style.display = 'block';
    
    // Limpa lista atual
    container.innerHTML = '';
    
    // Adiciona cada SDR ao ranking
    ranking.forEach((sdr) => {
        const sdrElement = createSDRElement(sdr);
        
        // Se houve mudança de posição, anima
        const change = positionChanges.find(c => c.sdrName === sdr.sdrName);
        if (change) {
            const positionEl = sdrElement.querySelector('.ev-position');
            positionEl.classList.add('ev-position-change');
            
            setTimeout(() => {
                positionEl.classList.remove('ev-position-change');
            }, 600);
        }
        
        container.appendChild(sdrElement);
    });
}

/**
 * Renderiza o ranking de SDRs Expansão na tela
 */
function renderSDRsExpansaoRanking(ranking, positionChanges = []) {
    const container = document.getElementById('topSdrsExpansaoList');
    const emptyState = document.getElementById('topSdrsExpansaoEmpty');
    
    if (!container || !emptyState) {
        console.error('Elementos do ranking de SDRs Expansão não encontrados no DOM');
        return;
    }
    
    // Se não há dados, mostra estado vazio
    if (!ranking || ranking.length === 0) {
        container.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    // Esconde estado vazio e mostra lista
    emptyState.style.display = 'none';
    container.style.display = 'block';
    
    // Limpa lista atual
    container.innerHTML = '';
    
    // Adiciona cada SDR ao ranking
    ranking.forEach((sdr) => {
        const sdrElement = createSDRElement(sdr);
        
        // Se houve mudança de posição, anima
        const change = positionChanges.find(c => c.sdrName === sdr.sdrName);
        if (change) {
            const positionEl = sdrElement.querySelector('.ev-position');
            positionEl.classList.add('ev-position-change');
            
            setTimeout(() => {
                positionEl.classList.remove('ev-position-change');
            }, 600);
        }
        
        container.appendChild(sdrElement);
    });
}

/**
 * Cria elemento HTML para um LDR no ranking
 */
function createLDRElement(ldr, isNew = false) {
    const li = document.createElement('li');
    li.className = 'top-ev-item';
    li.dataset.ldrName = ldr.ldrName;
    
    if (isNew) {
        li.style.opacity = '0';
        setTimeout(() => {
            li.style.transition = 'opacity 0.5s ease';
            li.style.opacity = '1';
        }, 50);
    }
    
    // Medal/Posição
    const medal = MEDALS[ldr.position] || ldr.position;
    
    // Foto
    const photoPath = getPhotoPath(ldr.ldrName);
    const photoHtml = photoPath 
        ? `<img src="${photoPath}" alt="${ldr.ldrName}" class="ev-photo" onerror="this.parentNode.innerHTML='<div class=\\'ev-photo-placeholder\\'>${ldr.ldrName.charAt(0).toUpperCase()}</div><div class=\\'ev-position\\'>${medal}</div>'">` 
        : `<div class="ev-photo-placeholder">${ldr.ldrName.charAt(0).toUpperCase()}</div>`;
    
    li.innerHTML = `
        <div class="ev-photo-wrapper">
            ${photoHtml}
            ${medal ? `<div class="ev-position">${medal}</div>` : ''}
        </div>
        <div class="ev-info">
            <p class="ev-name">${ldr.ldrName}</p>
            <p class="ev-revenue">${ldr.wonDealsCount} deal${ldr.wonDealsCount !== 1 ? 's' : ''} ganho${ldr.wonDealsCount !== 1 ? 's' : ''}</p>
        </div>
    `;
    
    return li;
}

/**
 * Renderiza o ranking de LDRs na tela
 */
function renderLDRsRanking(ranking, positionChanges = []) {
    const container = document.getElementById('topLdrsList');
    const emptyState = document.getElementById('topLdrsEmpty');
    
    if (!container || !emptyState) {
        console.error('Elementos do ranking de LDRs não encontrados no DOM');
        return;
    }
    
    // Se não há dados, mostra estado vazio
    if (!ranking || ranking.length === 0) {
        container.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    // Esconde estado vazio e mostra lista
    emptyState.style.display = 'none';
    container.style.display = 'block';
    
    // Limpa lista atual
    container.innerHTML = '';
    
    // Adiciona cada LDR ao ranking
    ranking.forEach((ldr) => {
        const ldrElement = createLDRElement(ldr);
        
        // Se houve mudança de posição, anima
        const change = positionChanges.find(c => c.ldrName === ldr.ldrName);
        if (change) {
            const positionEl = ldrElement.querySelector('.ev-position');
            positionEl.classList.add('ev-position-change');
            
            setTimeout(() => {
                positionEl.classList.remove('ev-position-change');
            }, 600);
        }
        
        container.appendChild(ldrElement);
    });
}

/**
 * Troca para um slide específico
 */
function goToSlide(slideIndex) {
    const wrapper = document.getElementById('rankingSlides');
    const bullets = document.querySelectorAll('.ranking-bullet');
    
    if (!wrapper) return;
    
    // Atualiza slide atual
    currentSlide = slideIndex;
    
    // Move o wrapper
    // Calcula o translateX considerando o gap de 15px entre slides
    // Cada slide tem 100% + 15px de gap
    const translateX = slideIndex === 0 ? 0 : -(slideIndex * 100 + (slideIndex * 15 / 260 * 100));
    wrapper.style.transform = `translateX(${translateX}%)`;
    
    // Atualiza bullets
    bullets.forEach((bullet, index) => {
        bullet.classList.toggle('active', index === slideIndex);
    });
    
    const slideNames = ['EVs', 'SDRs NEW', 'SDRs Expansão', 'LDRs'];
    console.log(`Slide alterado para: ${slideNames[slideIndex] || slideIndex}`);
}

/**
 * Inicia rotação automática dos slides
 */
function startSlideRotation() {
    if (slideInterval) {
        clearInterval(slideInterval);
    }
    
    slideInterval = setInterval(() => {
        const nextSlide = (currentSlide + 1) % 4; // Alterna entre 0, 1, 2 e 3
        goToSlide(nextSlide);
    }, SLIDE_CHANGE_INTERVAL);
}

/**
 * Atualiza todos os rankings
 */
async function updateAllRankings() {
    // Atualiza EVs
    const newEVsRanking = await fetchTopEVsRanking();
    const evChanges = detectEVPositionChanges(newEVsRanking);
    
    if (evChanges.length > 0) {
        console.log('Mudanças de posição nos EVs detectadas:', evChanges);
    }
    
    renderEVsRanking(newEVsRanking, evChanges);
    previousEVsRanking = newEVsRanking;
    
    // Atualiza SDRs NEW
    const newSDRsNewRanking = await fetchTopSDRsNewRanking();
    renderSDRsNewRanking(newSDRsNewRanking);
    previousSDRsNewRanking = newSDRsNewRanking;
    
    // Atualiza SDRs Expansão
    const newSDRsExpansaoRanking = await fetchTopSDRsExpansaoRanking();
    renderSDRsExpansaoRanking(newSDRsExpansaoRanking);
    previousSDRsExpansaoRanking = newSDRsExpansaoRanking;
    
    // Atualiza LDRs
    const newLDRsRanking = await fetchTopLDRsRanking();
    renderLDRsRanking(newLDRsRanking);
    previousLDRsRanking = newLDRsRanking;
}

/**
 * Inicializa o sistema de ranking com slider
 */
function initializeRankingSlider() {
    console.log('Sistema de ranking com slider iniciado');
    
    // Primeira atualização imediata de ambos os rankings
    updateAllRankings();
    
    // Atualiza dados periodicamente
    setInterval(updateAllRankings, RANKING_UPDATE_INTERVAL);
    
    // Inicia rotação automática dos slides
    startSlideRotation();
    
    // Adiciona event listeners nos bullets para troca manual
    const bullets = document.querySelectorAll('.ranking-bullet');
    bullets.forEach((bullet, index) => {
        bullet.addEventListener('click', () => {
            goToSlide(index);
            // Reinicia o timer de rotação automática
            startSlideRotation();
        });
    });
}

// Inicia quando a página carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeRankingSlider);
} else {
    initializeRankingSlider();
}
