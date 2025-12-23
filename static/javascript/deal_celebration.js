/**
 * Sistema de Celebração de Deals Ganhos
 * Verifica novas notificações e exibe animações comemorativas
 */

// Intervalo de verificação de novas notificações (em milissegundos)
const CHECK_INTERVAL = 3000; // 3 segundos

// Duração da animação na tela (em milissegundos)
const ANIMATION_DURATION = 30000; // 30 segundos

// Notificações já processadas (para evitar duplicatas)
const processedNotifications = new Set();

// Fila de notificações pendentes para exibição sequencial
const notificationQueue = [];

// Flag para controlar se uma animação está sendo exibida
let isAnimationPlaying = false;

// Intervalo de polling
let pollingInterval = null;

// Identificador único deste painel/cliente. Usado para marcar visualizações por cliente
function getPanelClientId() {
    try {
        const key = 'bn_panel_client_id';
        let id = localStorage.getItem(key);
        if (!id) {
            id = 'panel-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
            localStorage.setItem(key, id);
        }
        return id;
    } catch (e) {
        // Se localStorage não estiver disponível, gera um id temporário
        return 'panel-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
    }
}

const CLIENT_ID = getPanelClientId();

/**
 * Verifica se o ID do deal parece ser um ID real do backend
 * - IDs de teste (ex: 'test-...') não devem fazer chamadas ao backend
 */
function isRealDealId(id) {
    if (id === null || id === undefined) return false;
    // Considera real se for número ou string apenas com dígitos
    if (typeof id === 'number') return Number.isFinite(id);
    return /^\d+$/.test(String(id));
}

/**
 * Envia notificação push local para um deal
 */
async function sendPushNotification(deal) {
    // Verifica se notificações estão habilitadas
    if (!pushNotificationsEnabled || !serviceWorkerRegistration) {
        console.log('Notificações push não estão habilitadas');
        return;
    }
    
    // Verifica se o documento está oculto (usuário não está vendo a página)
    const isPageHidden = document.hidden || document.visibilityState === 'hidden';
    
    // Só envia notificação push se a página estiver oculta (não está ativa)
    if (!isPageHidden) {
        console.log('Página está ativa, não enviando notificação push');
        return;
    }
    
    try {
        const title = '🎉 Novo Deal Ganho!';
        const body = formatNotificationBody(deal);
        
        await serviceWorkerRegistration.showNotification(title, {
            body: body,
            icon: '/static/img/icon-192.png',
            badge: '/static/img/icon-192.png',
            tag: `deal-${deal.id}`,
            requireInteraction: true,
            vibrate: [200, 100, 200, 100, 200],
            data: deal,
            actions: [
                {
                    action: 'view',
                    title: 'Ver Detalhes'
                },
                {
                    action: 'close',
                    title: 'Fechar'
                }
            ]
        });
        
        console.log(`📱 Notificação push enviada para deal: ${deal.dealName}`);
    } catch (error) {
        console.error('Erro ao enviar notificação push:', error);
    }
}

/**
 * Formata o corpo da notificação
 */
function formatNotificationBody(deal) {
    let message = `${deal.dealName}\n`;
    message += `💰 Valor: ${formatCurrency(deal.amount)}\n`;
    
    // Adiciona informações do time
    const team = [];
    if (deal.ownerName) {
        team.push(`👔 EV: ${deal.ownerName}`);
    }
    if (deal.sdrName) {
        team.push(`📞 SDR: ${deal.sdrName}`);
    }
    if (deal.ldrName) {
        team.push(`🎯 LDR: ${deal.ldrName}`);
    }
    
    if (team.length > 0) {
        message += team.join('\n') + '\n';
    }
    
    // Mostra produto principal se disponível, senão mostra empresa
    if (deal.productName) {
        message += `📦 Produto: ${deal.productName}`;
    } else if (deal.companyName) {
        message += `🏢 Empresa: ${deal.companyName}`;
    }
    
    return message;
}

/**
 * Normaliza nome para buscar foto do time
 * Remove acentos, espaços, caracteres especiais
 */
function normalizeName(name) {
    if (!name) return '';
    
    return name
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Remove acentos
        .replace(/\s+/g, '_') // Espaços vira underscore
        .replace(/[^a-z0-9_]/g, ''); // Remove caracteres especiais
}

/**
 * Obtém o caminho da foto do membro do time
 */
function getTeamPhotoPath(name) {
    if (!name) return null;
    
    // Ignora valores de teste do HubSpot
    if (name.toLowerCase().includes('valor de teste') || 
        name.toLowerCase().includes('test value') ||
        name === 'teste' ||
        name === 'test') {
        return null; // Não tenta buscar foto para valores de teste
    }
    
    const normalizedName = normalizeName(name);
    return `/static/img/team/${normalizedName}.png`;
}

/**
 * Verifica se a imagem existe
 */
function checkImageExists(url) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = url;
    });
}

/**
 * Cria elemento de foto do membro do time
 */
async function createMemberPhoto(name, role) {
    const memberDiv = document.createElement('div');
    memberDiv.className = 'deal-celebration-member';
    
    // Cria container para foto e badge (separado do nome)
    const photoContainer = document.createElement('div');
    photoContainer.className = 'deal-celebration-photo-container';
    
    // Cria badge com sigla do cargo
    const roleBadge = document.createElement('div');
    roleBadge.className = 'deal-celebration-role-badge';
    
    // Define a sigla baseada no role
    let roleAbbr = '';
    if (role === 'Executivo') {
        roleAbbr = 'EV';
    } else if (role === 'SDR') {
        roleAbbr = 'SDR';
    } else if (role === 'LDR') {
        roleAbbr = 'LDR';
    }
    
    roleBadge.textContent = roleAbbr;
    photoContainer.appendChild(roleBadge);
    
    // Adiciona container da foto ao membro
    memberDiv.appendChild(photoContainer);
    
    const photoPath = getTeamPhotoPath(name);
    let photoExists = false;
    
    if (photoPath) {
        photoExists = await checkImageExists(photoPath);
    }
    
    const img = document.createElement('img');
    img.className = 'deal-celebration-photo';
    
    // Se não tem nome válido ou é valor de teste, não mostra foto
    if (!name || !photoPath || name.toLowerCase().includes('valor de teste')) {
        // Cria placeholder visual (círculo com inicial)
        const placeholder = document.createElement('div');
        placeholder.className = 'deal-celebration-photo';
        placeholder.style.backgroundColor = '#FFD700';
        placeholder.style.display = 'flex';
        placeholder.style.alignItems = 'center';
        placeholder.style.justifyContent = 'center';
        placeholder.style.fontSize = '3rem';
        placeholder.style.color = '#fff';
        placeholder.style.fontWeight = 'bold';
        placeholder.textContent = name ? name.charAt(0).toUpperCase() : '?';
        placeholder.title = name || 'Não informado';
        
        const nameDiv = document.createElement('div');
        nameDiv.className = 'deal-celebration-name';
        nameDiv.textContent = name || 'Não informado';
        
        photoContainer.appendChild(placeholder);
        memberDiv.appendChild(nameDiv);
        
        return memberDiv;
    }
    
    if (photoExists) {
        img.src = photoPath;
        img.alt = name;
        img.onerror = () => {
            // Fallback: cria placeholder se imagem falhar
            const placeholder = document.createElement('div');
            placeholder.className = 'deal-celebration-photo';
            placeholder.style.backgroundColor = '#FFD700';
            placeholder.style.display = 'flex';
            placeholder.style.alignItems = 'center';
            placeholder.style.justifyContent = 'center';
            placeholder.style.fontSize = '3rem';
            placeholder.style.color = '#fff';
            placeholder.style.fontWeight = 'bold';
            placeholder.textContent = name.charAt(0).toUpperCase();
            img.replaceWith(placeholder);
        };
    } else {
        // Cria placeholder visual se não encontrar foto
        const placeholder = document.createElement('div');
        placeholder.className = 'deal-celebration-photo';
        placeholder.style.backgroundColor = '#FFD700';
        placeholder.style.display = 'flex';
        placeholder.style.alignItems = 'center';
        placeholder.style.justifyContent = 'center';
        placeholder.style.fontSize = '3rem';
        placeholder.style.color = '#fff';
        placeholder.style.fontWeight = 'bold';
        placeholder.textContent = name.charAt(0).toUpperCase();
        placeholder.title = name;
        
        const nameDiv = document.createElement('div');
        nameDiv.className = 'deal-celebration-name';
        nameDiv.textContent = name;
        
        photoContainer.appendChild(placeholder);
        memberDiv.appendChild(nameDiv);
        
        return memberDiv;
    }
    
    const nameDiv = document.createElement('div');
    nameDiv.className = 'deal-celebration-name';
    nameDiv.textContent = name;
    
    photoContainer.appendChild(img);
    memberDiv.appendChild(nameDiv);
    
    return memberDiv;
}

/**
 * Formata valor monetário
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Variável global para controlar se o áudio foi desbloqueado
let audioUnlocked = false;

/**
 * Desbloqueia o áudio para permitir reprodução automática
 * Necessário porque navegadores bloqueiam áudio sem interação do usuário
 */
function unlockAudio() {
    const audio = document.getElementById('cornetAudio');
    
    if (!audio) {
        // Aguarda o elemento ser criado
        setTimeout(unlockAudio, 100);
        return;
    }
    
    if (audioUnlocked) {
        // Já foi desbloqueado anteriormente
        return;
    }
    
    // Função para tentar desbloquear
    const tryUnlock = () => {
        // Verifica se o áudio está pronto
        if (audio.readyState < 2) { // HAVE_CURRENT_DATA
            // Aguarda o áudio carregar
            audio.addEventListener('canplaythrough', tryUnlock, { once: true });
            audio.load(); // Força o carregamento
            return;
        }
        
        // Tenta tocar o áudio em volume muito baixo para desbloquear
        const originalVolume = audio.volume;
        audio.volume = 0.01; // Volume muito baixo, praticamente inaudível
        
        const playPromise = audio.play();
        
        if (playPromise !== undefined) {
            playPromise
                .then(() => {
                    // Áudio desbloqueado com sucesso
                    audio.pause();
                    audio.currentTime = 0;
                    audio.volume = originalVolume;
                    audioUnlocked = true;
                    console.log('Áudio desbloqueado com sucesso');
                })
                .catch(error => {
                    // Se falhar, registra mas não bloqueia - tentará novamente quando necessário
                    console.log('Primeira tentativa de desbloqueio falhou, será tentado novamente quando necessário:', error);
                });
        }
    };
    
    // Tenta desbloquear imediatamente ou quando o áudio carregar
    if (audio.readyState >= 2) {
        tryUnlock();
    } else {
        audio.addEventListener('canplaythrough', tryUnlock, { once: true });
        audio.load(); // Força o carregamento
    }
}

// Tenta desbloquear quando a janela recebe foco (útil para painéis de TV)
window.addEventListener('focus', unlockAudio);
window.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        unlockAudio();
    }
});

// Desbloqueia áudio quando houver qualquer interação do usuário (clique, toque, etc.)
// Isso é útil para painéis de TV onde alguém pode tocar a tela uma vez para desbloquear
document.addEventListener('click', unlockAudio, { once: true });
document.addEventListener('touchstart', unlockAudio, { once: true });
document.addEventListener('keydown', unlockAudio, { once: true });

// Também tenta desbloquear quando o botão de teste de chuva de dinheiro for usado
function setupAudioUnlockListeners() {
    const oldBtn = document.getElementById('testMoneyRainBtn'); // botão antigo (marcos)
    if (oldBtn) oldBtn.addEventListener('click', unlockAudio);
}

// Configura listeners quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAudioUnlockListeners);
} else {
    setupAudioUnlockListeners();
}

/**
 * Dispara uma celebração de teste (sem envolver backend/webhook)
 * Gera um deal falso e usa o mesmo fluxo da fila
 */
function triggerTestCelebration(options = {}) {
    const now = new Date();
    const randomAmount = options.amount ?? (Math.floor(Math.random() * 10) + 3) * 1000; // 3k a 13k
    const fakeId = `test-${now.getTime()}-${Math.random().toString(36).slice(2,8)}`;
    const fakeDeal = {
        id: fakeId,
        dealName: options.dealName ?? 'Teste Integração - Celebração',
        amount: randomAmount,
        ownerName: options.ownerName ?? 'Bruno',
        sdrName: options.sdrName ?? 'Gabriela',
        ldrName: options.ldrName ?? 'Marcelo',
        productName: options.productName ?? 'Rastreio Premium',
        companyName: options.companyName ?? 'Empresa Exemplo S.A.'
    };
    console.log('🚀 Disparando celebração de TESTE (sem backend):', fakeDeal);
    enqueueNotification(fakeDeal);
}

/**
 * Configura ganchos de teste: botão 💰 e parâmetros de URL
 * - Botão: dispara uma celebração falsa ao clicar
 * - URL: ?test=1 ou ?test-celebration=1 para auto disparo ao carregar
 */
function setupTestHooks() {
    const testBtn = document.getElementById('testDealCelebrationBtn');
    // Parâmetros de URL
    let params;
    try { params = new URLSearchParams(window.location.search); } catch (_) {}
    
    // Mostra botão se: tem parâmetro de teste OU está em localhost
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const hasTestParam = params && (params.has('test') || params.has('test-celebration') || params.has('celebrar') || params.has('celebration'));
    const showButton = hasTestParam || isLocalhost;
    
    if (testBtn && showButton) {
        testBtn.style.display = 'block'; // mostra o botão dedicado para deals
        testBtn.title = 'Disparar celebração de DEAL (teste, sem banco)';
        testBtn.addEventListener('click', () => triggerTestCelebration());
    }
    // Auto disparo
    try {
        const shouldAutoTest = params && (params.has('test') || params.has('test-celebration') || params.has('celebrar') || params.has('celebration'));
        if (shouldAutoTest) {
            const count = Math.max(1, Math.min(5, parseInt(params.get('n') || '1', 10) || 1));
            const delay = Math.max(0, parseInt(params.get('delay') || '800', 10) || 800);
            // Dispara 1..5 celebrações de teste espaçadas
            for (let i = 0; i < count; i++) {
                setTimeout(() => triggerTestCelebration(), i * (ANIMATION_DURATION + 600));
            }
            // Primeira começa um pouco após o load para garantir áudio desbloqueado
            setTimeout(() => triggerTestCelebration(), delay);
        }
    } catch (_) { /* ignore */ }
}

/**
 * Toca som de corneta
 */
function playCornetSound() {
    const audio = document.getElementById('cornetAudio');
    if (!audio) {
        console.warn('Áudio da corneta não encontrado');
        return;
    }
    
    // Função auxiliar para tentar tocar o áudio
    const tryPlay = () => {
        // Pausa qualquer reprodução anterior para evitar conflitos
        if (!audio.paused) {
            audio.pause();
        }
        
        // Aguarda um pouco para garantir que o pause() terminou
        setTimeout(() => {
            // Verifica se o áudio está pronto para tocar
            if (audio.readyState < 2) { // HAVE_CURRENT_DATA
                // Aguarda o áudio carregar
                audio.addEventListener('canplaythrough', tryPlay, { once: true });
                audio.load(); // Força o carregamento se necessário
                return;
    }
    
    // Garante que o volume está correto
    if (audio.volume < 0.1) {
        audio.volume = 1.0;
    }
    
            // Reseta para o início
    audio.currentTime = 0;
            
            // Tenta tocar
    const playPromise = audio.play();
    
    if (playPromise !== undefined) {
        playPromise
            .then(() => {
                console.log('Corneta tocando com sucesso');
                audioUnlocked = true; // Marca como desbloqueado
            })
            .catch(error => {
                        // Ignora AbortError (interrupção normal)
                        if (error.name === 'AbortError') {
                            console.log('Reprodução interrompida (normal)');
                            return;
                        }
                        
                console.error('Erro ao tocar som de corneta:', error);
                        
                        // Se ainda não foi desbloqueado, tenta desbloquear
                        if (!audioUnlocked) {
                unlockAudio();
                            // Tenta novamente após desbloquear
                            setTimeout(tryPlay, 500);
                        }
                    });
            }
        }, 50); // Pequeno delay para garantir que pause() terminou
    };
    
    // Se ainda não foi desbloqueado, tenta desbloquear primeiro
    if (!audioUnlocked) {
        unlockAudio();
        // Aguarda um pouco para o desbloqueio acontecer
        setTimeout(tryPlay, 300);
    } else {
        // Já está desbloqueado, tenta tocar diretamente
        tryPlay();
    }
}

/**
 * Cria elemento de celebração
 */
async function createCelebrationElement(deal) {
    const celebrationDiv = document.createElement('div');
    celebrationDiv.className = 'deal-celebration';
    celebrationDiv.id = `celebration-${deal.id}`;
    
    // Aplica o tema atual (usa cache do localStorage para resposta imediata)
    let currentTheme = 'black-november';
    if (window.CelebrationThemeManager) {
        try {
            const cachedTheme = localStorage.getItem('deal_celebration_theme');
            if (cachedTheme && window.CelebrationThemeManager.CELEBRATION_THEMES[cachedTheme]) {
                currentTheme = cachedTheme;
            }
        } catch (e) {
            // Usa default
        }
        window.CelebrationThemeManager.applyThemeToElement(celebrationDiv, currentTheme);
    }
    
    // Luzes de Natal no topo (apenas para tema natal) - duas imagens lado a lado
    if (currentTheme === 'natal') {
        // Primeira imagem de luzes
        const lights1 = document.createElement('img');
        lights1.src = '/static/img/luzes_natal.png';
        lights1.alt = 'Luzes de Natal';
        lights1.className = 'deal-celebration-lights';
        celebrationDiv.appendChild(lights1);
        
        // Segunda imagem de luzes (duplicada)
        const lights2 = document.createElement('img');
        lights2.src = '/static/img/luzes_natal.png';
        lights2.alt = 'Luzes de Natal';
        lights2.className = 'deal-celebration-lights';
        celebrationDiv.appendChild(lights2);
    }
    
    // Título - muda conforme o tema
    const title = document.createElement('div');
    title.className = 'deal-celebration-title';
    if (currentTheme === 'natal') {
        title.textContent = '🎄 CONTRATO ASSINADO! 🎅🏻';
    } else {
    title.textContent = '🎉 CONTRATO ASSINADO! 🎉';
    }
    celebrationDiv.appendChild(title);
    
    // Container do time
    const teamContainer = document.createElement('div');
    teamContainer.className = 'deal-celebration-team';
    
    // Adiciona fotos dos membros do time (se existirem)
    const members = [];
    
    if (deal.ownerName) {
        const ownerPhoto = await createMemberPhoto(deal.ownerName, 'Executivo');
        members.push(ownerPhoto);
    }
    
    if (deal.sdrName) {
        const sdrPhoto = await createMemberPhoto(deal.sdrName, 'SDR');
        members.push(sdrPhoto);
    }
    
    if (deal.ldrName) {
        const ldrPhoto = await createMemberPhoto(deal.ldrName, 'LDR');
        members.push(ldrPhoto);
    }
    
    // Se não houver membros, adiciona pelo menos o executivo
    if (members.length === 0 && deal.ownerName) {
        const ownerPhoto = await createMemberPhoto(deal.ownerName, 'Executivo');
        members.push(ownerPhoto);
    }
    
    members.forEach(member => teamContainer.appendChild(member));
    celebrationDiv.appendChild(teamContainer);
    
    // Valor do deal
    const amount = document.createElement('div');
    amount.className = 'deal-celebration-amount';
    amount.textContent = formatCurrency(deal.amount);
    celebrationDiv.appendChild(amount);
    
    // Nome do deal
    if (deal.dealName) {
        const dealName = document.createElement('div');
        dealName.className = 'deal-celebration-deal-name';
        dealName.textContent = deal.dealName;
        celebrationDiv.appendChild(dealName);
    }
    
    // Produto principal (prioridade) ou nome da empresa (fallback)
    const displayText = deal.productName || deal.companyName;
    if (displayText) {
        const company = document.createElement('div');
        company.className = 'deal-celebration-company';
        company.textContent = displayText;
        celebrationDiv.appendChild(company);
    }
    
    // Logo Logcomex no canto inferior direito
    const logo = document.createElement('img');
    logo.className = 'deal-celebration-logo';
    logo.src = '/static/img/logo_logcomex.png';
    logo.alt = 'Logcomex';
    celebrationDiv.appendChild(logo);
    
    return celebrationDiv;
}

/**
 * Processa a próxima notificação da fila
 */
async function processNextNotification() {
    // Se já está processando uma animação, aguarda
    if (isAnimationPlaying) {
        return;
    }
    
    // Se não há notificações na fila, retorna
    if (notificationQueue.length === 0) {
        return;
    }
    
    // Marca que está processando
    isAnimationPlaying = true;
    
    // Remove a primeira notificação da fila
    const deal = notificationQueue.shift();
    
    // Verifica se já foi processada (duplicatas)
    if (processedNotifications.has(deal.id)) {
        // Se já foi processada, processa a próxima
        isAnimationPlaying = false;
        processNextNotification();
        return;
    }
    
    // Marca como processada
    processedNotifications.add(deal.id);
    
    console.log(`Processando animação para deal: ${deal.dealName} (${deal.id})`);
    
    // Cria elemento de celebração
    const celebrationEl = await createCelebrationElement(deal);
    
    // Adiciona à página
    document.body.appendChild(celebrationEl);
    
    // Toca som de corneta
    playCornetSound();
    
    // Remove após animação
    setTimeout(() => {
        celebrationEl.classList.add('hide');
        
        setTimeout(() => {
            if (celebrationEl.parentNode) {
                celebrationEl.remove();
            }
            
            // Marca como visualizada no backend
            markDealAsViewed(deal.id);
            
            // Libera para processar a próxima notificação
            isAnimationPlaying = false;
            
            // Processa a próxima notificação da fila (se houver)
            processNextNotification();
        }, 500); // Aguarda transição de fade out
    }, ANIMATION_DURATION);
}

/**
 * Adiciona uma notificação à fila
 * @returns {boolean} true se foi adicionada, false se já estava processada ou na fila
 */
function enqueueNotification(deal) {
    // Verifica se já foi processada
    if (processedNotifications.has(deal.id)) {
        console.log(`Notificação ${deal.id} já foi processada anteriormente, ignorando`);
        return false; // Já foi processada
    }
    
    // Verifica se já está na fila
    const isInQueue = notificationQueue.some(n => n.id === deal.id);
    if (isInQueue) {
        console.log(`Notificação ${deal.id} já está na fila, ignorando`);
        return false; // Já está na fila
    }
    
    // Adiciona à fila
    notificationQueue.push(deal);
    console.log(`Notificação enfileirada: ${deal.dealName} (${deal.id}). Fila: ${notificationQueue.length} notificação(ões)`);
    
    // Tenta processar imediatamente (se não estiver processando outra)
    processNextNotification();
    
    return true; // Foi adicionada com sucesso
}

/**
 * Exibe animação de celebração (mantida para compatibilidade, mas agora usa a fila)
 */
async function showCelebrationAnimation(deal) {
    enqueueNotification(deal);
}

/**
 * Marca deal como visualizado no backend
 */
function markDealAsViewed(dealId) {
    // Evita chamadas ao backend para deals de TESTE (ids não numéricos)
    if (!isRealDealId(dealId)) {
        console.log(`(dev) Ignorando mark-viewed para deal de teste: ${dealId}`);
        return;
    }
    // Marca como visualizada apenas para este client_id
    fetch(`/api/deals/mark-viewed/${dealId}?client_id=${encodeURIComponent(CLIENT_ID)}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log(`Deal ${dealId} marcado como visualizado`);
        }
    })
    .catch(error => {
        console.error('Erro ao marcar deal como visualizado:', error);
    });
}

/**
 * Verifica novas notificações no backend
 * Filtra apenas notificações criadas APÓS o timestamp de inicialização
 */
async function checkForNewDeals() {
    try {
        // Adiciona o timestamp de referência na query para filtrar no backend
        const url = `/api/deals/pending?client_id=${encodeURIComponent(CLIENT_ID)}&since=${encodeURIComponent(SYSTEM_START_TIMESTAMP)}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.notifications && data.notifications.length > 0) {
            console.log(`${data.notifications.length} notificação(ões) pendente(s) encontrada(s)`);
            
            // Log detalhado das notificações encontradas
            data.notifications.forEach(notification => {
                console.log(`  - Deal ID: ${notification.id}, Nome: ${notification.dealName}, Valor: R$ ${notification.amount}`);
            });
            
            // Adiciona todas as notificações pendentes à fila
            // As notificações já vêm ordenadas do backend (mais recentes primeiro)
            // A fila garante que sejam processadas sequencialmente, mesmo se chegar múltiplas ao mesmo tempo
            let addedCount = 0;
            data.notifications.forEach(notification => {
                const wasAdded = enqueueNotification(notification);
                if (wasAdded) {
                    addedCount++;
                }
            });
            
            console.log(`${addedCount} notificação(ões) adicionada(s) à fila. Total na fila: ${notificationQueue.length}`);
        }
    } catch (error) {
        console.error('Erro ao verificar novos deals:', error);
    }
}

/**
 * Armazena o timestamp de inicialização do sistema
 * Usado para filtrar apenas deals criados APÓS a abertura da página
 */
let SYSTEM_START_TIMESTAMP = null;

/**
 * Inicializa o timestamp de referência para filtrar notificações
 * SEMPRE usa o timestamp do momento do carregamento da página
 */
function initializeSystemTimestamp() {
    // SEMPRE usa o timestamp atual (ISO 8601 format)
    SYSTEM_START_TIMESTAMP = new Date().toISOString();
    console.log(`✅ Timestamp de referência criado: ${SYSTEM_START_TIMESTAMP}`);
    console.log('✅ Sistema configurado para exibir apenas deals criados APÓS este momento');
}

/**
 * Inicia o sistema de verificação de deals
 */
async function startDealCelebrationSystem() {
    console.log('Sistema de celebração de deals iniciado');
    
    // Desbloqueia o áudio assim que possível (necessário para painéis de TV)
    unlockAudio();
    
    // PRIMEIRO: Inicializa o timestamp de referência
    // Todas as notificações criadas ANTES desse momento serão ignoradas
    initializeSystemTimestamp();
    
    // Verifica se o polling deve ser desabilitado (modo de teste)
    let disablePolling = false;
    try {
        const params = new URLSearchParams(window.location.search);
        disablePolling = params.has('no-poll') || params.has('nopoll');
    } catch (_) { /* ignore */ }

    if (disablePolling) {
        console.log('🧪 Modo de teste: polling desabilitado por parâmetro de URL');
    } else {
        // SEGUNDO: Inicia a verificação periódica de novos deals
        // Agora só vai pegar deals criados APÓS o timestamp de inicialização
        checkForNewDeals();
        // Configura polling periódico
        pollingInterval = setInterval(checkForNewDeals, CHECK_INTERVAL);
    }

}

/**
 * Para o sistema de celebração
 */
function stopDealCelebrationSystem() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

/**
 * Verifica se há celebração em andamento
 * Esta função é usada pelo sistema de rotação automática
 */
function isCelebrationActive() {
    return isAnimationPlaying;
}

// Exporta para uso global
window.isCelebrationActive = isCelebrationActive;

// Inicia quando a página carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Inicializa o gerenciador de temas se disponível
        if (window.CelebrationThemeManager) {
            window.CelebrationThemeManager.initThemeManager();
        }
        startDealCelebrationSystem();
        setupTestHooks(); // Configura botão de teste
    });
} else {
    // Inicializa o gerenciador de temas se disponível
    if (window.CelebrationThemeManager) {
        window.CelebrationThemeManager.initThemeManager();
    }
    startDealCelebrationSystem();
    setupTestHooks(); // Configura botão de teste
}

