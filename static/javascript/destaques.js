/**
 * Destaques da Semana e do Mês - Black November
 * Página de MVPs acumulados (sem badges)
 */

// Estado Global
let currentSlide = 0;
const totalSlides = 12; // 6 da semana + 6 do mês (EV NEW, EV Expansão, SDR NEW, SDR Expansão, LDR NEW, LDR Expansão)
let slideInterval = null;
// Armazena dados de cada slide para atualizar a imagem do troféu
const slideDataMap = {
    0: null, // EvNew (Semana)
    1: null, // EvExpansao (Semana)
    2: null, // SdrNew (Semana)
    3: null, // SdrExpansao (Semana)
    4: null, // LdrNew (Semana)
    5: null, // LdrExpansao (Semana)
    6: null, // EvNewMes
    7: null, // EvExpansaoMes
    8: null, // SdrNewMes
    9: null, // SdrExpansaoMes
    10: null, // LdrNewMes
    11: null  // LdrExpansaoMes
};

// Configurações
const SLIDE_DURATION = 10000; // 10 segundos por slide
const REFRESH_INTERVAL = 300000; // Atualiza dados a cada 5 minutos

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('⭐ Destaques inicializado');
    
    // Verifica modo aleatório
    const urlParams = new URLSearchParams(window.location.search);
    const isRandomMode = urlParams.has('aleatorio');
    console.log('🎲 Modo aleatório:', isRandomMode ? 'ATIVO' : 'INATIVO');
    
    // Event listeners para indicadores
    setupIndicators();
    
    // Configura vídeo do Paty Rifiski com chromakey
    setupPatyRifiskiVideo();
    
    // Carrega dados iniciais (startSlideRotation e startNavigationTimer são chamados dentro de loadAllData)
    const loadSuccess = await loadAllData();
    
    if (!loadSuccess) {
        console.warn('⚠️ Falha ao carregar dados, mas continuando...');
        // Mesmo com erro, tenta iniciar navegação se estiver no modo aleatório
        if (isRandomMode) {
            startNavigationTimer();
        }
    }
    
    // Atualização periódica dos dados (apenas se NÃO estiver no modo aleatório)
    if (!isRandomMode) {
    setInterval(loadAllData, REFRESH_INTERVAL);
    } else {
        console.log('📦 Modo aleatório: atualizações periódicas desabilitadas (usando cache centralizado)');
    }
});

// ============================================================================
// CARREGAMENTO DE DADOS
// ============================================================================

async function loadAllData() {
    console.log('🔄 Atualizando dados dos destaques...');
    
    try {
        // Verifica se está no modo aleatório para usar cache
        const urlParams = new URLSearchParams(window.location.search);
        const isRandomMode = urlParams.has('aleatorio');
        const useCacheParam = isRandomMode ? '&use_cache=true' : '';
        
        const timestamp = new Date().getTime();
        
        // Carrega dados sequencialmente para evitar rate limit
        // SEMANA
        const evNewSemana = await fetch(`/api/destaques/evs?periodo=semana&pipeline=6810518&_=${timestamp}${useCacheParam}`).then(r => r.json());
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const evExpansaoSemana = await fetch(`/api/destaques/evs?periodo=semana&pipeline=4007305&_=${timestamp}${useCacheParam}`).then(r => r.json());
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const sdrNewSemana = await fetch(`/api/destaques/sdrs?periodo=semana&pipeline=6810518&_=${timestamp}${useCacheParam}`).then(r => r.json());
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const sdrExpansaoSemana = await fetch(`/api/destaques/sdrs?periodo=semana&pipeline=4007305&_=${timestamp}${useCacheParam}`).then(r => r.json());
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const ldrNewSemana = await fetch(`/api/destaques/ldrs?periodo=semana&pipeline=6810518&_=${timestamp}${useCacheParam}`).then(r => r.json());
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const ldrExpansaoSemana = await fetch(`/api/destaques/ldrs?periodo=semana&pipeline=4007305&_=${timestamp}${useCacheParam}`).then(r => r.json());
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // MÊS
        const evNewMes = await fetch(`/api/destaques/evs?periodo=mes&pipeline=6810518&_=${timestamp}${useCacheParam}`).then(r => r.json());
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const evExpansaoMes = await fetch(`/api/destaques/evs?periodo=mes&pipeline=4007305&_=${timestamp}${useCacheParam}`).then(r => r.json());
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const sdrNewMes = await fetch(`/api/destaques/sdrs?periodo=mes&pipeline=6810518&_=${timestamp}${useCacheParam}`).then(r => r.json());
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const sdrExpansaoMes = await fetch(`/api/destaques/sdrs?periodo=mes&pipeline=4007305&_=${timestamp}${useCacheParam}`).then(r => r.json());
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const ldrNewMes = await fetch(`/api/destaques/ldrs?periodo=mes&pipeline=6810518&_=${timestamp}${useCacheParam}`).then(r => r.json());
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const ldrExpansaoMes = await fetch(`/api/destaques/ldrs?periodo=mes&pipeline=4007305&_=${timestamp}${useCacheParam}`).then(r => r.json());
        
        // Armazena dados em variável global para atualizar troféu quando slide mudar
        slideDataMap[0] = evNewSemana;
        slideDataMap[1] = evExpansaoSemana;
        slideDataMap[2] = sdrNewSemana;
        slideDataMap[3] = sdrExpansaoSemana;
        slideDataMap[4] = ldrNewSemana;
        slideDataMap[5] = ldrExpansaoSemana;
        slideDataMap[6] = evNewMes;
        slideDataMap[7] = evExpansaoMes;
        slideDataMap[8] = sdrNewMes;
        slideDataMap[9] = sdrExpansaoMes;
        slideDataMap[10] = ldrNewMes;
        slideDataMap[11] = ldrExpansaoMes;
        
        // Renderiza pódios da SEMANA
        renderPodio('EvNew', evNewSemana);
        renderPodio('EvExpansao', evExpansaoSemana);
        renderPodio('SdrNew', sdrNewSemana);
        renderPodio('SdrExpansao', sdrExpansaoSemana);
        renderPodio('LdrNew', ldrNewSemana);
        renderPodio('LdrExpansao', ldrExpansaoSemana);
        
        // Renderiza pódios do MÊS
        renderPodio('EvNewMes', evNewMes);
        renderPodio('EvExpansaoMes', evExpansaoMes);
        renderPodio('SdrNewMes', sdrNewMes);
        renderPodio('SdrExpansaoMes', sdrExpansaoMes);
        renderPodio('LdrNewMes', ldrNewMes);
        renderPodio('LdrExpansaoMes', ldrExpansaoMes);
        
        // Atualiza imagem do troféu para o slide atual
        updateTrophyImage(currentSlide);
        
        // Atualiza subtítulos com datas
        const { startDate: semanaStart, endDate: semanaEnd } = getWeekPeriod();
        const { startDate: mesStart, endDate: mesEnd } = getMonthPeriod();
        
        const semanaDateRange = `${formatDate(semanaStart)} a ${formatDate(semanaEnd)}`;
        const mesDateRange = `${formatDate(mesStart)} a ${formatDate(mesEnd)}`;
        
        // Atualiza subtítulos da SEMANA
        document.getElementById('subtitleEvNew').textContent = semanaDateRange;
        document.getElementById('subtitleEvExpansao').textContent = semanaDateRange;
        document.getElementById('subtitleSdrNew').textContent = semanaDateRange;
        document.getElementById('subtitleSdrExpansao').textContent = semanaDateRange;
        document.getElementById('subtitleLdrNew').textContent = semanaDateRange;
        document.getElementById('subtitleLdrExpansao').textContent = semanaDateRange;
        
        // Atualiza subtítulos do MÊS
        document.getElementById('subtitleEvNewMes').textContent = mesDateRange;
        document.getElementById('subtitleEvExpansaoMes').textContent = mesDateRange;
        document.getElementById('subtitleSdrNewMes').textContent = mesDateRange;
        document.getElementById('subtitleSdrExpansaoMes').textContent = mesDateRange;
        document.getElementById('subtitleLdrNewMes').textContent = mesDateRange;
        document.getElementById('subtitleLdrExpansaoMes').textContent = mesDateRange;
        
        // Esconde loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('destaquesSlides').style.display = 'block';
        document.getElementById('slideIndicators').style.display = 'flex';
        
        console.log('✅ Dados atualizados com sucesso');
        
        // Inicia rotação de slides e timer de navegação após dados carregados
        startSlideRotation();
        startNavigationTimer();
        
        return true; // Indica sucesso no carregamento
        
    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        return false; // Indica falha no carregamento
    }
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
    // Tempo total = 12 slides x 10s = 120 segundos
    const DURATION = 120000; // 120 segundos (soma dos 12 slides)
    
    console.log('⏱️ Timer de navegação iniciado:', DURATION / 1000, 'segundos');
    console.log('📋 Painéis disponíveis:', panels);
    console.log('🔑 Storage key:', STORAGE_KEY);
    
    // Após o tempo definido, avança para o próximo painel
    // MAS aguarda se houver celebração ativa
    const timeoutId = setTimeout(() => {
        let retryCount = 0;
        const MAX_RETRIES = 30; // Máximo de 30 tentativas (60 segundos)
        
        const tryNavigate = () => {
            retryCount++;
            
            // Verifica se há celebração ativa
            const celebrationActive = typeof window.isCelebrationActive === 'function' && window.isCelebrationActive();
            
            if (celebrationActive && retryCount < MAX_RETRIES) {
                console.log(`⏸️ Celebração ativa (tentativa ${retryCount}/${MAX_RETRIES}), aguardando para trocar de painel...`);
                // Tenta novamente em 2 segundos
                setTimeout(tryNavigate, 2000);
                return;
            }
            
            // Se excedeu tentativas ou não há celebração, navega
            if (retryCount >= MAX_RETRIES) {
                console.warn('⚠️ Máximo de tentativas atingido, forçando navegação...');
            }
            
            // Não há celebração ou excedeu tentativas, pode trocar de painel
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
        
        tryNavigate();
    }, DURATION);
    
    // Salva o timeout ID para poder cancelar se necessário
    window._navigationTimeoutId = timeoutId;
    console.log('✅ Timer de navegação configurado com ID:', timeoutId);
}

// ============================================================================
// ATUALIZAÇÃO DE SUBTÍTULOS COM DATAS
// ============================================================================

function updatePeriodSubtitles() {
    // Atualiza subtítulos de todos os slides
    const { startDate: semanaStart, endDate: semanaEnd } = getWeekPeriod();
    const { startDate: mesStart, endDate: mesEnd } = getMonthPeriod();
    
    // Semana NEW
    const semanaNewSubtitle = document.querySelector('#slideSemanaNew .hall-subtitle');
    if (semanaNewSubtitle) {
        semanaNewSubtitle.textContent = `${formatDate(semanaStart)} a ${formatDate(semanaEnd)}`;
    }
    
    // Semana Expansão
    const semanaExpansaoSubtitle = document.querySelector('#slideSemanaExpansao .hall-subtitle');
    if (semanaExpansaoSubtitle) {
        semanaExpansaoSubtitle.textContent = `${formatDate(semanaStart)} a ${formatDate(semanaEnd)}`;
    }
    
    // Mês NEW
    const mesNewSubtitle = document.querySelector('#slideMesNew .hall-subtitle');
    if (mesNewSubtitle) {
        mesNewSubtitle.textContent = `${formatDate(mesStart)} a ${formatDate(mesEnd)}`;
    }
    
    // Mês Expansão
    const mesExpansaoSubtitle = document.querySelector('#slideMesExpansao .hall-subtitle');
    if (mesExpansaoSubtitle) {
        mesExpansaoSubtitle.textContent = `${formatDate(mesStart)} a ${formatDate(mesEnd)}`;
    }
}

function getWeekPeriod() {
    // Calcula o período da semana (domingo a sábado) no timezone do Brasil
    // Mesma lógica do backend Python
    
    // Pega a data/hora atual em UTC
    const now = new Date();
    
    // Converte para horário do Brasil (GMT-3): adiciona 3 horas
    const brazilTime = new Date(now.getTime() + (3 * 60 * 60 * 1000));
    
    // getUTCDay() retorna: 0=domingo, 1=segunda, ..., 6=sábado
    const dayOfWeek = brazilTime.getUTCDay();
    
    // Converte para weekday() do Python: 0=segunda, 1=terça, ..., 6=domingo
    // Python weekday(): 0=segunda, 6=domingo
    // JavaScript getDay(): 0=domingo, 1=segunda, 6=sábado
    const weekday = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
    
    // Calcula quantos dias desde o último domingo (igual ao Python)
    // Python: days_since_sunday = (weekday + 1) % 7
    // Se hoje é domingo (weekday=6), days_since_sunday = (6+1)%7 = 0
    // Se hoje é segunda (weekday=0), days_since_sunday = (0+1)%7 = 1
    // Se hoje é sábado (weekday=5), days_since_sunday = (5+1)%7 = 6
    const daysSinceSunday = (weekday + 1) % 7;
    
    // Cria data de início da semana (domingo 00:00 Brasil)
    const weekStartBrazil = new Date(brazilTime);
    if (daysSinceSunday === 0) {
        // Hoje é domingo, semana começa hoje
        weekStartBrazil.setUTCHours(0, 0, 0, 0);
    } else {
        // Volta para o domingo anterior
        weekStartBrazil.setUTCDate(brazilTime.getUTCDate() - daysSinceSunday);
        weekStartBrazil.setUTCHours(0, 0, 0, 0);
    }
    
    // Fim da semana é sábado (6 dias depois do domingo) 23:59:59
    const weekEndBrazil = new Date(weekStartBrazil);
    weekEndBrazil.setUTCDate(weekStartBrazil.getUTCDate() + 6);
    weekEndBrazil.setUTCHours(23, 59, 59, 999);
    
    // Usa as datas do Brasil diretamente para formatação
    // formatDate() vai usar getUTCDate(), getUTCMonth(), getUTCFullYear()
    return {
        startDate: weekStartBrazil,
        endDate: weekEndBrazil
    };
}

function getMonthPeriod() {
    // Calcula o período do mês (dia 1 até hoje) no timezone do Brasil
    // Mesma lógica do backend Python
    
    // Pega a data/hora atual em UTC
    const now = new Date();
    
    // Converte para horário do Brasil (GMT-3)
    const brazilTime = new Date(now.getTime() + (3 * 60 * 60 * 1000));
    
    // Início do mês é dia 1
    const monthStart = new Date(Date.UTC(
        brazilTime.getUTCFullYear(),
        brazilTime.getUTCMonth(),
        1,
        0, 0, 0, 0
    ));
    
    // Fim do mês é hoje
    const monthEnd = new Date(Date.UTC(
        brazilTime.getUTCFullYear(),
        brazilTime.getUTCMonth(),
        brazilTime.getUTCDate(),
        23, 59, 59, 999
    ));
    
    // Converte de volta para o timezone local para exibição
    return {
        startDate: new Date(monthStart.getTime() - (3 * 60 * 60 * 1000)),
        endDate: new Date(monthEnd.getTime() - (3 * 60 * 60 * 1000))
    };
}

function formatDate(date) {
    // Formata data no formato DD/MM/YYYY
    // Usa UTC para manter as datas do Brasil corretas
    const day = String(date.getUTCDate()).padStart(2, '0');
    const month = String(date.getUTCMonth() + 1).padStart(2, '0');
    const year = date.getUTCFullYear();
    return `${day}/${month}/${year}`;
}

// ============================================================================
// RENDERIZAÇÃO
// ============================================================================

function renderPodio(slideId, data) {
    const container = document.getElementById(`podio${slideId}`);
    if (!container) return;
    
    container.innerHTML = ''; // Limpa container
    
    const top3 = data.top3 || [];
    
    if (top3.length === 0) {
        container.innerHTML = '<div style="text-align: center; color: #fff; font-size: 1.5rem; padding: 3rem;">Nenhum destaque encontrado</div>';
        // Esconde imagem do troféu se não houver dados
        const trophyImage = document.getElementById('trophyImage');
        if (trophyImage) {
            trophyImage.style.display = 'none';
        }
        return;
    }
    
    // Renderiza cada posição do pódio
    top3.forEach((person, index) => {
        const position = person.position || (index + 1);
        const card = createPodioCard(person, position, data);
        container.appendChild(card);
    });
    
    // A imagem do troféu será atualizada quando o slide mudar
    // Não atualizamos aqui para evitar conflitos
}

function truncateName(fullName) {
    if (!fullName || fullName === 'N/A') return 'N/A';
    
    const parts = fullName.trim().split(/\s+/);
    if (parts.length <= 2) {
        return fullName; // Já tem apenas nome + 1 sobrenome ou menos
    }
    
    // Retorna primeiro nome + primeiro sobrenome
    return `${parts[0]} ${parts[1]}`;
}

function createPodioCard(person, position, data) {
    const card = document.createElement('div');
    card.className = `podio-card position-${position}`;
    
    const fullName = person.userName || 'N/A';
    const userName = truncateName(fullName);
    const photoPath = getPhotoPath(fullName); // Usa nome completo para buscar foto
    
    // Determina o tipo de métricas baseado nas propriedades da pessoa
    const isSdr = 'scheduledCount' in person;
    const isLdr = 'wonDealsCount' in person;
    const isEv = !isSdr && !isLdr && ('dealCount' in person || 'revenue' in person);
    
    card.innerHTML = `
        <div class="podio-position position-${position}">${position}º</div>
        <div class="podio-photo-wrapper">
            <img class="podio-photo" src="${photoPath}" alt="${userName}" onerror="this.src='/static/img/team/desativado.png'">
        </div>
        <h2 class="podio-name">${userName}</h2>
        <div class="podio-stats">
            ${isEv ? `
                <div class="podio-stat">
                    <span class="podio-stat-value">${person.dealCount || 0}</span>
                    <span class="podio-stat-label">Deals</span>
                </div>
                <div class="podio-stat">
                    <span class="podio-stat-value">${formatCurrency(person.revenue || 0)}</span>
                    <span class="podio-stat-label">Revenue</span>
                </div>
            ` : ''}
            ${isSdr ? `
                <div class="podio-stat">
                    <span class="podio-stat-value">${person.scheduledCount || 0}</span>
                    <span class="podio-stat-label">Agendamentos</span>
                </div>
            ` : ''}
            ${isLdr ? `
                <div class="podio-stat">
                    <span class="podio-stat-value">${person.wonDealsCount || 0}</span>
                    <span class="podio-stat-label">Deals Ganhos</span>
                </div>
                <div class="podio-stat">
                    <span class="podio-stat-value">${formatCurrency(person.revenue || 0)}</span>
                    <span class="podio-stat-label">Revenue</span>
                </div>
            ` : ''}
        </div>
    `;
    
    return card;
}

function renderMVP(cardId, mvp, stats) {
    const card = document.getElementById(cardId);
    if (!card) return;
    
    const userName = mvp.userName || 'N/A';
    const photoPath = getPhotoPath(userName);
    
    // Atualiza foto (com fallback para placeholder se não existir)
    const photoEl = card.querySelector('.mvp-photo');
    if (photoEl) {
        // Tenta carregar a imagem, se falhar usa placeholder
        const img = new Image();
        img.onload = () => {
            photoEl.src = photoPath;
        };
        img.onerror = () => {
            photoEl.src = '/static/img/team/desativado.png';
        };
        img.src = photoPath;
        photoEl.alt = userName;
    }
    
    // Atualiza nome
    const nameEl = card.querySelector('.mvp-name');
    if (nameEl) {
        nameEl.textContent = userName;
    }
    
    // Atualiza estatísticas
    const statElements = card.querySelectorAll('.mvp-stat');
    
    // Para EVs e LDRs: deals e revenue
    if (stats.deals !== undefined) {
        if (statElements.length > 0) {
            statElements[0].querySelector('.mvp-stat-value').textContent = stats.deals || 0;
        }
    }
    if (stats.revenue !== undefined) {
        if (statElements.length > 1) {
            const revenueValue = stats.revenue || 0;
            statElements[1].querySelector('.mvp-stat-value').textContent = formatCurrency(revenueValue);
        }
    }
    
    // Para SDRs: scheduled
    if (stats.scheduled !== undefined) {
        if (statElements.length > 0) {
            statElements[0].querySelector('.mvp-stat-value').textContent = stats.scheduled || 0;
        }
    }
}

function showEmptyMVP(cardId) {
    const card = document.getElementById(cardId);
    if (!card) return;
    
    const nameEl = card.querySelector('.mvp-name');
    if (nameEl) {
        nameEl.textContent = 'Sem dados';
    }
    
    const statElements = card.querySelectorAll('.mvp-stat-value');
    statElements.forEach(el => {
        el.textContent = '0';
    });
}

// ============================================================================
// UTILITÁRIOS
// ============================================================================

function getPhotoPath(userName) {
    if (!userName) return '/static/img/team/desativado.png';
    
    // Normaliza o nome: lowercase, remove acentos, substitui espaços por _
    const normalized = userName
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Remove acentos
        .replace(/\s+/g, '_') // Espaços para underscores
        .replace(/[^a-z0-9_]/g, ''); // Remove caracteres especiais
    
    return `/static/img/team/${normalized}.png`;
}

function getTrophyPhotoPath(userName) {
    if (!userName) return '';
    
    // Normaliza o nome: lowercase, remove acentos, substitui espaços por _
    const normalized = userName
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Remove acentos
        .replace(/\s+/g, '_') // Espaços para underscores
        .replace(/[^a-z0-9_]/g, ''); // Remove caracteres especiais
    
    return `/static/img/team_trophy/${normalized}.png`;
}

function getTrophyVideoPath(userName) {
    if (!userName) return '';
    
    // Normaliza o nome: lowercase, remove acentos, substitui espaços por _
    const normalized = userName
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Remove acentos
        .replace(/\s+/g, '_') // Espaços para underscores
        .replace(/[^a-z0-9_]/g, ''); // Remove caracteres especiais
    
    return `/static/img/team_trophy/${normalized}.mp4`;
}

function processChromaKeyImage(img) {
    // Cria canvas para processar a imagem e remover fundo chromakey
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Define tamanho do canvas igual à imagem
    canvas.width = img.naturalWidth || img.width;
    canvas.height = img.naturalHeight || img.height;
    
    // Desenha a imagem no canvas
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    
    // Obtém dados da imagem
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    const width = canvas.width;
    const height = canvas.height;
    
    // Primeira passagem: identifica pixels claramente chromakey VERDE
    // Focamos APENAS em verde, não em azul (para preservar azuis e roxos da imagem)
    const isChromaKey = new Array(data.length / 4).fill(false);
    
    for (let i = 0; i < data.length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        const brightness = max;
        const saturation = max === 0 ? 0 : (max - min) / max;
        
        // Foco APENAS em verde chromakey
        const greenDominance = g - Math.max(r, b);
        const greenRatio = (r + g + b) > 0 ? g / (r + g + b) : 0;
        
        // Detecta chromakey VERDE - apenas verde muito saturado e brilhante
        // Verde chromakey típico: g muito alto, r e b baixos
        const isPureGreen = g > 100 && greenDominance > 40 && saturation > 0.4 && r < 100 && b < 100;
        const isMediumGreen = g > 80 && greenDominance > 30 && saturation > 0.3 && r < 120 && b < 120 && brightness > 150;
        const isLightGreen = g > 60 && greenDominance > 25 && greenRatio > 0.4 && r < 80 && b < 80;
        
        const pixelIndex = i / 4;
        if (isPureGreen || isMediumGreen || isLightGreen) {
            isChromaKey[pixelIndex] = true;
        }
    }
    
    // Segunda passagem: remove chromakey VERDE e processa halos
    for (let i = 0; i < data.length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        const pixelIndex = i / 4;
        
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        const brightness = max;
        const saturation = max === 0 ? 0 : (max - min) / max;
        
        const greenDominance = g - Math.max(r, b);
        
        // Se é chromakey verde puro, remove completamente
        if (isChromaKey[pixelIndex]) {
            data[i + 3] = 0;
            continue;
        }
        
        // Verifica se está próximo de chromakey verde (halos)
        const x = (pixelIndex % width);
        const y = Math.floor(pixelIndex / width);
        
        // Conta pixels chromakey verde ao redor (3x3)
        let nearbyChromaKey = 0;
        for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
                const nx = x + dx;
                const ny = y + dy;
                if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                    const neighborIndex = (ny * width + nx) * 4;
                    const neighborPixelIndex = neighborIndex / 4;
                    if (isChromaKey[neighborPixelIndex]) {
                        nearbyChromaKey++;
                    }
                }
            }
        }
        
        // Se está rodeado de chromakey verde ou próximo, reduz opacidade
        // Mas APENAS se o pixel também for verde (não azul/roxo)
        if (nearbyChromaKey > 0 && greenDominance > 10) {
            // Quanto mais chromakey verde ao redor, mais transparente
            const chromaRatio = nearbyChromaKey / 9;
            if (chromaRatio > 0.3) {
                // Área muito próxima ao chromakey verde - remove quase tudo
                data[i + 3] = Math.max(0, data[i + 3] * (1 - chromaRatio * 0.9));
            } else if (chromaRatio > 0.1) {
                // Halo verde - reduz opacidade
                data[i + 3] = Math.max(0, data[i + 3] * (1 - chromaRatio * 0.5));
            }
        }
        
        // Remove pixels que são claramente verde chromakey mesmo que não detectados antes
        // Mas preserva azuis e roxos (b alto com r alto = roxo, b alto com r baixo = azul)
        const isGreenish = g > 60 && greenDominance > 15 && saturation > 0.2 && brightness > 100 && r < 100 && b < 100;
        
        if (isGreenish && nearbyChromaKey > 2) {
            // Se é verde e está próximo de chromakey verde, provavelmente é resíduo
            data[i + 3] = Math.max(0, data[i + 3] * 0.2);
        }
    }
    
    // Aplica os dados processados de volta ao canvas
    ctx.putImageData(imageData, 0, 0);
    
    // Retorna a URL do canvas processado
    return canvas.toDataURL();
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// ============================================================================
// ROTAÇÃO DE SLIDES
// ============================================================================

function startSlideRotation() {
    if (slideInterval) {
        clearInterval(slideInterval);
    }
    
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
    
    // Pausa e limpa vídeo anterior se estiver tocando
    const trophyVideo = document.getElementById('trophyVideo');
    if (trophyVideo && !trophyVideo.paused) {
        trophyVideo.pause();
        trophyVideo.currentTime = 0;
    }
    
    // Atualiza imagem/vídeo do troféu para o slide atual
    updateTrophyImage(index);
    
    console.log(`🔄 Slide alterado para: ${index + 1}/${slides.length}`);
}

// Função para configurar chromakey do vídeo do troféu
function setupTrophyVideoChromaKey(video) {
    const canvas = document.getElementById('trophyVideoCanvas');
    if (!canvas) {
        console.error('❌ Canvas do troféu não encontrado');
        return;
    }
    
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    
    // Esconde o vídeo original
    video.style.display = 'none';
    
    // Posiciona o canvas no mesmo lugar da imagem do troféu
    const trophyImage = document.getElementById('trophyImage');
    if (trophyImage) {
        const imageRect = trophyImage.getBoundingClientRect();
        canvas.style.position = 'fixed';
        canvas.style.bottom = '0px';
        canvas.style.right = '0px';
        canvas.style.maxWidth = '500px';
        canvas.style.height = 'auto';
        canvas.style.zIndex = '101';
    }
    
    // Mostra o canvas
    canvas.style.display = 'block';
    
    let animationFrameId = null;
    
    function processFrame() {
        if (video.readyState >= video.HAVE_CURRENT_DATA && video.videoWidth > 0 && video.videoHeight > 0) {
            // Ajusta o tamanho do canvas ao tamanho do vídeo
            if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            }
            
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;
            
            // Remove fundo verde (chroma key) - mesma lógica das fotos
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                
                const max = Math.max(r, g, b);
                const min = Math.min(r, g, b);
                const saturation = max === 0 ? 0 : (max - min) / max;
                
                const greenDominance = g - Math.max(r, b);
                const greenRatio = (r + g + b) > 0 ? g / (r + g + b) : 0;
                
                // Detecta chromakey verde - mesma lógica das fotos
                const isPureGreen = g > 100 && greenDominance > 40 && saturation > 0.4 && r < 100 && b < 100;
                const isMediumGreen = g > 80 && greenDominance > 30 && saturation > 0.3 && r < 120 && b < 120;
                const isLightGreen = g > 60 && greenDominance > 25 && greenRatio > 0.4 && r < 80 && b < 80;
                
                if (isPureGreen || isMediumGreen || isLightGreen) {
                    data[i + 3] = 0; // Torna transparente
                }
            }
            
            ctx.putImageData(imageData, 0, 0);
        }
        
        if (!video.paused && !video.ended) {
            animationFrameId = requestAnimationFrame(processFrame);
        }
    }
    
    video.addEventListener('play', () => {
        processFrame();
    });
    
    video.addEventListener('pause', () => {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
    });
    
    // Inicia processamento se o vídeo já está pronto
    if (video.readyState >= video.HAVE_CURRENT_DATA) {
        processFrame();
    } else {
        video.addEventListener('loadeddata', () => {
            processFrame();
        }, { once: true });
    }
    
    video.dataset.chromakeySetup = 'true';
    console.log('✅ Chromakey configurado para vídeo do troféu');
}

function updateTrophyImage(slideIndex) {
    const data = slideDataMap[slideIndex];
    const trophyImage = document.getElementById('trophyImage');
    const trophyVideo = document.getElementById('trophyVideo');
    const trophyVideoCanvas = document.getElementById('trophyVideoCanvas');
    
    if (!trophyImage || !trophyVideo || !trophyVideoCanvas) return;
    
    if (!data || !data.top3 || data.top3.length === 0) {
        trophyImage.style.display = 'none';
        trophyImage.style.opacity = '0';
        trophyVideo.style.display = 'none';
        trophyVideoCanvas.style.display = 'none';
        return;
    }
    
    // Encontra o primeiro lugar
    const firstPlace = data.top3.find(p => (p.position || 1) === 1) || data.top3[0];
    
    if (!firstPlace || !firstPlace.userName) {
        trophyImage.style.display = 'none';
        trophyImage.style.opacity = '0';
        trophyVideo.style.display = 'none';
        trophyVideoCanvas.style.display = 'none';
        return;
    }
    
    const fullName = firstPlace.userName;
    const trophyVideoPath = getTrophyVideoPath(fullName);
    const trophyPhotoPath = getTrophyPhotoPath(fullName);
    
    // Primeiro, tenta carregar o vídeo
    const tempVideo = document.createElement('video');
    tempVideo.muted = true;
    tempVideo.playsInline = true;
    
    // Verifica se o vídeo existe
    tempVideo.addEventListener('loadeddata', () => {
        console.log('✅ Vídeo do troféu encontrado, carregando...');
        
        // Esconde a imagem
        trophyImage.style.display = 'none';
        trophyImage.style.opacity = '0';
        
        // PRÉ-CARREGA E PROCESSA A FOTO enquanto o vídeo está rodando
        // Isso garante que quando o vídeo terminar, a foto já estará pronta
        const preloadPhoto = () => {
            const tempImg = new Image();
            tempImg.onload = function() {
                try {
                    // Processa a imagem para remover chromakey ANTES do vídeo terminar
                    const processedDataUrl = processChromaKeyImage(tempImg);
                    
                    // Armazena a foto processada para uso imediato quando o vídeo terminar
                    trophyImage.dataset.processedPhoto = processedDataUrl;
                    trophyImage.dataset.photoReady = 'true';
                    console.log('✅ Foto pré-processada e pronta para exibição');
                } catch (error) {
                    console.error('Erro ao pré-processar chromakey:', error);
                    // Se falhar, armazena a foto original
                    trophyImage.dataset.processedPhoto = trophyPhotoPath;
                    trophyImage.dataset.photoReady = 'true';
                }
            };
            tempImg.onerror = function() {
                trophyImage.dataset.photoReady = 'false';
            };
            tempImg.src = trophyPhotoPath;
        };
        
        // Inicia pré-carregamento da foto
        preloadPhoto();
        
        // Configura o vídeo real
        trophyVideo.src = trophyVideoPath;
        trophyVideo.loop = false; // Vídeo roda apenas uma vez
        trophyVideo.load();
        
        // Configura chromakey se ainda não foi configurado
        if (trophyVideo.dataset.chromakeySetup !== 'true') {
            setupTrophyVideoChromaKey(trophyVideo);
        }
        
        // Quando o vídeo terminar, mostra a foto IMEDIATAMENTE (já processada)
        const handleVideoEnd = () => {
            console.log('✅ Vídeo do troféu finalizado, mostrando foto...');
            
            // Esconde o canvas do vídeo imediatamente (sem transição)
            trophyVideoCanvas.style.display = 'none';
            trophyVideoCanvas.style.opacity = '0';
            trophyVideo.pause();
            trophyVideo.currentTime = 0;
            
            // Mostra a foto IMEDIATAMENTE (já está processada e pronta)
            if (trophyImage.dataset.photoReady === 'true' && trophyImage.dataset.processedPhoto) {
                // Remove animação para troca imediata
                trophyImage.style.animation = 'none';
                trophyImage.style.opacity = '1'; // Aparece imediatamente
                
                // Define a foto já processada
                trophyImage.src = trophyImage.dataset.processedPhoto;
                trophyImage.style.display = 'block';
                
                console.log('✅ Foto exibida instantaneamente (já estava processada)');
            } else {
                // Fallback: se a foto não foi pré-carregada, carrega agora
                console.warn('⚠️ Foto não estava pré-carregada, carregando agora...');
                loadTrophyPhotoAfterVideo();
            }
        };
        
        // Remove listener anterior se existir
        trophyVideo.removeEventListener('ended', handleVideoEnd);
        trophyVideo.addEventListener('ended', handleVideoEnd, { once: true });
        
        // Mostra o canvas e toca o vídeo
        trophyVideoCanvas.style.display = 'block';
        trophyVideoCanvas.style.opacity = '0';
        trophyVideoCanvas.style.animation = 'none';
        trophyVideoCanvas.offsetHeight;
        trophyVideoCanvas.style.animation = 'fadeInTrophy 0.8s ease-in-out forwards';
        
        // Verifica se a página está visível antes de tentar tocar
        const playTrophyVideo = () => {
            if (document.hidden || document.visibilityState === 'hidden') {
                console.log('⏸️ Página não está visível, aguardando para tocar vídeo do troféu...');
                const handleVisibilityChange = () => {
                    if (!document.hidden) {
                        document.removeEventListener('visibilitychange', handleVisibilityChange);
                        setTimeout(() => playTrophyVideo(), 100);
                    }
                };
                document.addEventListener('visibilitychange', handleVisibilityChange);
                return;
            }
        
        trophyVideo.play().then(() => {
            console.log('✅ Vídeo do troféu iniciado (rodará uma vez)');
        }).catch(e => {
                // Ignora erro de "background media paused"
                if (e.name === 'AbortError' && (e.message.includes('background media') || e.message.includes('interrupted'))) {
                    console.log('⏸️ Vídeo pausado pelo navegador (economia de energia), será retomado quando página ficar visível');
                    const handleVisibilityChange = () => {
                        if (!document.hidden) {
                            document.removeEventListener('visibilitychange', handleVisibilityChange);
                            trophyVideo.play().catch(() => loadTrophyPhoto());
                        }
                    };
                    document.addEventListener('visibilitychange', handleVisibilityChange);
                } else {
            console.error('❌ Erro ao tocar vídeo do troféu:', e);
            // Se falhar, tenta usar a foto
            loadTrophyPhoto();
                }
        });
        };
        
        playTrophyVideo();
    });
    
    tempVideo.addEventListener('error', () => {
        console.log('📷 Vídeo não encontrado, usando foto como fallback');
        // Vídeo não existe, usa a foto
        loadTrophyPhoto();
    });
    
    // Função para carregar a foto (fallback - com animação)
    const loadTrophyPhoto = () => {
        // Esconde vídeo e canvas
        trophyVideo.style.display = 'none';
        trophyVideoCanvas.style.display = 'none';
        trophyVideo.pause();
        trophyVideo.currentTime = 0;
        
        // Carrega a foto
        const tempImg = new Image();
        
        tempImg.onload = function() {
            try {
                // Processa a imagem para remover chromakey
                const processedDataUrl = processChromaKeyImage(tempImg);
                
                // Reseta a animação
                trophyImage.style.opacity = '0';
                trophyImage.style.animation = 'none';
                
                // Força reflow para resetar a animação
                trophyImage.offsetHeight;
                
                // Define a nova imagem e reinicia a animação
                trophyImage.src = processedDataUrl;
                trophyImage.style.display = 'block';
                trophyImage.style.animation = 'fadeInTrophy 0.8s ease-in-out forwards';
            } catch (error) {
                console.error('Erro ao processar chromakey:', error);
                
                // Reseta a animação
                trophyImage.style.opacity = '0';
                trophyImage.style.animation = 'none';
                
                // Força reflow para resetar a animação
                trophyImage.offsetHeight;
                
                // Se houver erro no processamento, usa a imagem original
                trophyImage.src = trophyPhotoPath;
                trophyImage.style.display = 'block';
                trophyImage.style.animation = 'fadeInTrophy 0.8s ease-in-out forwards';
            }
        };
        
        tempImg.onerror = function() {
            // Se a foto do troféu não existir, esconde tudo
            trophyImage.style.display = 'none';
            trophyImage.style.opacity = '0';
        };
        
        tempImg.src = trophyPhotoPath;
    };
    
    // Função para carregar a foto após o vídeo terminar (sem animação, troca imediata)
    const loadTrophyPhotoAfterVideo = () => {
        // Esconde vídeo e canvas
        trophyVideo.style.display = 'none';
        trophyVideoCanvas.style.display = 'none';
        trophyVideo.pause();
        trophyVideo.currentTime = 0;
        
        // Carrega a foto
        const tempImg = new Image();
        
        tempImg.onload = function() {
            try {
                // Processa a imagem para remover chromakey
                const processedDataUrl = processChromaKeyImage(tempImg);
                
                // Remove animação para troca imediata
                trophyImage.style.animation = 'none';
                trophyImage.style.opacity = '1'; // Aparece imediatamente
                
                // Define a nova imagem sem animação
                trophyImage.src = processedDataUrl;
                trophyImage.style.display = 'block';
            } catch (error) {
                console.error('Erro ao processar chromakey:', error);
                
                // Remove animação para troca imediata
                trophyImage.style.animation = 'none';
                trophyImage.style.opacity = '1'; // Aparece imediatamente
                
                // Se houver erro no processamento, usa a imagem original
                trophyImage.src = trophyPhotoPath;
                trophyImage.style.display = 'block';
            }
        };
        
        tempImg.onerror = function() {
            // Se a foto do troféu não existir, esconde tudo
            trophyImage.style.display = 'none';
            trophyImage.style.opacity = '0';
        };
        
        tempImg.src = trophyPhotoPath;
    };
    
    // Tenta carregar o vídeo
    tempVideo.src = trophyVideoPath;
    tempVideo.load();
}

// Função para configurar chromakey do vídeo do Paty Rifiski
function setupPatyRifiskiVideo() {
    const video = document.getElementById('patyRifiskiVideo');
    const canvas = document.getElementById('patyRifiskiVideoCanvas');
    const image = document.getElementById('patyRifiskiImage');
    
    if (!video || !canvas) {
        console.warn('⚠️ Elementos do vídeo do Paty Rifiski não encontrados');
        return;
    }
    
    // Verifica se o vídeo existe
    video.addEventListener('loadeddata', () => {
        console.log('✅ Vídeo do Paty Rifiski encontrado, configurando chromakey...');
        
        // Esconde a imagem
        if (image) {
            image.style.display = 'none';
        }
        
        // Configura chromakey
        const ctx = canvas.getContext('2d', { willReadFrequently: true });
        
        // Posiciona o canvas no mesmo lugar da imagem
        canvas.style.position = 'fixed';
        canvas.style.bottom = '1px';
        canvas.style.left = '40px';
        canvas.style.maxWidth = '400px';
        canvas.style.height = 'auto';
        canvas.style.zIndex = '101';
        canvas.style.filter = 'drop-shadow(0 4px 12px rgba(0, 0, 0, 0.6))';
        
        // Esconde o vídeo original
        video.style.display = 'none';
        
        // Mostra o canvas
        canvas.style.display = 'block';
        
        let animationFrameId = null;
        
        function processFrame() {
            if (video.readyState >= video.HAVE_CURRENT_DATA && video.videoWidth > 0 && video.videoHeight > 0) {
                // Ajusta o tamanho do canvas ao tamanho do vídeo
                if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                }
                
                // Desenha o frame atual do vídeo (mesmo se estiver pausado, mostra o último frame)
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                
                // Remove fundo verde (chroma key) - mesma lógica das fotos
                for (let i = 0; i < data.length; i += 4) {
                    const r = data[i];
                    const g = data[i + 1];
                    const b = data[i + 2];
                    
                    const max = Math.max(r, g, b);
                    const min = Math.min(r, g, b);
                    const saturation = max === 0 ? 0 : (max - min) / max;
                    
                    const greenDominance = g - Math.max(r, b);
                    const greenRatio = (r + g + b) > 0 ? g / (r + g + b) : 0;
                    
                    // Detecta chromakey verde - mesma lógica das fotos
                    const isPureGreen = g > 100 && greenDominance > 40 && saturation > 0.4 && r < 100 && b < 100;
                    const isMediumGreen = g > 80 && greenDominance > 30 && saturation > 0.3 && r < 120 && b < 120;
                    const isLightGreen = g > 60 && greenDominance > 25 && greenRatio > 0.4 && r < 80 && b < 80;
                    
                    if (isPureGreen || isMediumGreen || isLightGreen) {
                        data[i + 3] = 0; // Torna transparente
                    }
                }
                
                ctx.putImageData(imageData, 0, 0);
            }
            
            // Continua processando mesmo quando pausado (para manter o último frame visível)
            // Mas só continua o loop se o vídeo não terminou completamente
            if (!video.ended) {
                animationFrameId = requestAnimationFrame(processFrame);
            }
        }
        
        video.addEventListener('play', () => {
            processFrame();
        });
        
        video.addEventListener('pause', () => {
            // Não cancela o animationFrame quando pausa, para manter o último frame visível
            // O processFrame continuará rodando e desenhando o frame atual
            // Só cancela se o vídeo realmente terminou e não vai reiniciar
        });
        
        // Inicia processamento se o vídeo já está pronto
        if (video.readyState >= video.HAVE_CURRENT_DATA) {
            processFrame();
        } else {
            video.addEventListener('loadeddata', () => {
                processFrame();
            }, { once: true });
        }
        
        // Configura delay entre repetições
        const DELAY_BETWEEN_LOOPS = 8000; // 10 segundos de delay
        let delayTimeout = null;
        
        const playVideo = () => {
            // Verifica se a página está visível antes de tentar tocar
            if (document.hidden || document.visibilityState === 'hidden') {
                console.log('⏸️ Página não está visível, aguardando para tocar vídeo...');
                // Aguarda a página ficar visível
                const handleVisibilityChange = () => {
                    if (!document.hidden) {
                        document.removeEventListener('visibilitychange', handleVisibilityChange);
                        setTimeout(() => playVideo(), 100); // Pequeno delay para garantir
                    }
                };
                document.addEventListener('visibilitychange', handleVisibilityChange);
                return;
            }
            
            const playPromise = video.play();
            
            if (playPromise !== undefined) {
                playPromise.then(() => {
                console.log('✅ Vídeo do Paty Rifiski iniciado');
                // Mostra o canvas quando o vídeo começa
                canvas.style.opacity = '1';
            }).catch(e => {
                    // Ignora erro de "background media paused" - é normal quando a página não está visível
                    if (e.name === 'AbortError' && (e.message.includes('background media') || e.message.includes('interrupted'))) {
                        console.log('⏸️ Vídeo pausado pelo navegador (economia de energia), será retomado quando página ficar visível');
                        // Aguarda a página ficar visível para tentar novamente
                        const handleVisibilityChange = () => {
                            if (!document.hidden) {
                                document.removeEventListener('visibilitychange', handleVisibilityChange);
                                setTimeout(() => playVideo(), 100);
                            }
                        };
                        document.addEventListener('visibilitychange', handleVisibilityChange);
                    } else {
                console.error('❌ Erro ao tocar vídeo do Paty Rifiski:', e);
                // Se falhar, mostra a imagem
                if (image) {
                    image.style.display = 'block';
                canvas.style.display = 'none';
                        }
                    }
            });
            }
        };
        
        // Quando o vídeo terminar, pausa e espera antes de reiniciar
        video.addEventListener('ended', () => {
            console.log('⏸️ Vídeo do Paty Rifiski finalizado, aguardando delay...');
            
            // Pausa o vídeo (mas mantém o canvas visível)
            video.pause();
            
            // Mantém o canvas visível durante o delay (não esconde)
            // canvas.style.opacity = '1'; // Já está visível
            
            // Limpa timeout anterior se existir
            if (delayTimeout) {
                clearTimeout(delayTimeout);
            }
            
            // Aguarda o delay antes de reiniciar
            delayTimeout = setTimeout(() => {
                console.log('▶️ Reiniciando vídeo do Paty Rifiski após delay...');
                
                // Reinicia o vídeo do início (canvas já está visível)
                video.currentTime = 0;
                playVideo();
            }, DELAY_BETWEEN_LOOPS);
        }, { once: false }); // Permite múltiplas execuções
        
        // Toca o vídeo inicialmente (apenas se a página estiver visível)
        if (!document.hidden) {
        playVideo();
        } else {
            // Se a página não estiver visível, aguarda ficar visível
            const handleVisibilityChange = () => {
                if (!document.hidden) {
                    document.removeEventListener('visibilitychange', handleVisibilityChange);
                    playVideo();
                }
            };
            document.addEventListener('visibilitychange', handleVisibilityChange);
        }
    });
    
    video.addEventListener('error', () => {
        console.log('📷 Vídeo do Paty Rifiski não encontrado, usando imagem como fallback');
        // Vídeo não existe, mostra a imagem
        if (image) {
            image.style.display = 'block';
        }
        canvas.style.display = 'none';
    });
    
    // Carrega o vídeo
    video.load();
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

