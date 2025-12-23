// Configurações
const META_MENSAL = 1500000; // R$ 1.500.000
const HORA_INICIO_EXPEDIENTE = 9; // 09:00
const HORA_FIM_EXPEDIENTE = 18; // 18:00
const NOVEMBRO_2025_DIAS_UTEIS = 20; // Total de dias úteis em novembro 2025
const UPDATE_INTERVAL = 300000; // Atualiza a cada 5 minutos

// Utilitários
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function formatTime(hours, minutes, seconds) {
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// Calcula dias úteis restantes em novembro 2025
function getDiasUteisRestantes() {
    const hoje = new Date();
    const diaAtual = hoje.getDate();
    const mesAtual = hoje.getMonth(); // 0-11 (10 = novembro)
    const anoAtual = hoje.getFullYear();
    
    // Se não estamos em novembro 2025, retorna 0
    if (anoAtual !== 2025 || mesAtual !== 10) {
        return 0;
    }
    
    // Dias úteis em novembro 2025 (considerando apenas sábados e domingos como não úteis)
    // Novembro 2025 tem 30 dias
    // Sábados: 1, 8, 15, 22, 29
    // Domingos: 2, 9, 16, 23, 30
    // Feriado: 20 (Dia da Consciência Negra)
    const diasNaoUteis = [1, 2, 8, 9, 15, 16, 20, 22, 23, 29, 30];
    
    let diasUteisRestantes = 0;
    for (let dia = diaAtual; dia <= 30; dia++) {
        if (!diasNaoUteis.includes(dia)) {
            diasUteisRestantes++;
        }
    }
    
    return diasUteisRestantes;
}

// Calcula meta do dia baseada no que falta atingir
function calcularMetaDoDia(faturadoMes) {
    const faltaMes = META_MENSAL - faturadoMes;
    
    // Se já atingiu ou ultrapassou a meta, meta do dia = 0
    if (faltaMes <= 0) {
        return 0;
    }
    
    const diasRestantes = getDiasUteisRestantes();
    
    // Se não há dias restantes, retorna o que falta
    if (diasRestantes === 0) {
        return faltaMes;
    }
    
    // Meta do dia = (Meta mensal - Faturado) / Dias úteis restantes
    return faltaMes / diasRestantes;
}

// Calcula tempo restante até fim do dia (meia-noite)
function getTempoRestante() {
    const agora = new Date();
    const horaAtual = agora.getHours();
    const minutoAtual = agora.getMinutes();
    const segundoAtual = agora.getSeconds();
    
    // Calcula tempo restante até meia-noite (23:59:59)
    const totalSegundosRestantes = 
        (23 - horaAtual) * 3600 +
        (59 - minutoAtual) * 60 +
        (59 - segundoAtual);
    
    const hours = Math.floor(totalSegundosRestantes / 3600);
    const minutes = Math.floor((totalSegundosRestantes % 3600) / 60);
    const seconds = totalSegundosRestantes % 60;
    
    return { hours, minutes, seconds, totalSeconds: totalSegundosRestantes };
}

// Calcula horas trabalhadas hoje (desde meia-noite)
function getHorasTrabalhadasHoje() {
    const agora = new Date();
    const horaAtual = agora.getHours();
    const minutoAtual = agora.getMinutes();
    
    // Horas desde meia-noite
    const horasTrabalhadas = horaAtual + (minutoAtual / 60);
    
    return horasTrabalhadas;
}

// Atualiza interface com dados
async function atualizarDados() {
    // Verifica se está no modo aleatório (fora do try/catch para evitar redeclaração)
    const urlParams = new URLSearchParams(window.location.search);
    const isRandomMode = urlParams.has('aleatorio');
    
    try {
        // Usa cache se estiver no modo aleatório
        const useCacheParam = isRandomMode ? '?use_cache=true' : '';
        
        // Busca faturamento até ontem (para calcular meta do dia), do dia atual E pipeline previsto para hoje em paralelo
        const [responseUntilYesterday, responseToday, responsePipeline] = await Promise.all([
            fetch(`/api/revenue/until-yesterday${useCacheParam}`),
            fetch(`/api/revenue/today${useCacheParam}`),
            fetch(`/api/pipeline/today${useCacheParam}`)
        ]);
        
        const dataUntilYesterday = await responseUntilYesterday.json();
        const dataToday = await responseToday.json();
        const dataPipeline = await responsePipeline.json();
        
        // O valor adicional já é aplicado pelo backend se o modo manual estiver ativo
        const faturadoAteOntem = dataUntilYesterday.total || 0;
        const faturadoHoje = dataToday.total_today || 0;
        const faturadoMes = faturadoAteOntem + faturadoHoje; // Total do mês (até ontem + hoje)
        const pipelineHoje = dataPipeline.total_pipeline || 0;
        const totalDealsPrevistos = dataPipeline.total_deals || 0;
        
        // Calcula meta do dia baseado no faturado até ontem (não inclui o faturado de hoje)
        // Isso garante que a meta do dia não diminua conforme entram ganhos no dia
        const metaDoDia = calcularMetaDoDia(faturadoAteOntem);
        const faltaMes = Math.max(0, META_MENSAL - faturadoMes);
        const diasRestantes = getDiasUteisRestantes();
        
        // Atualiza meta do dia
        document.getElementById('metaDoDia').textContent = formatCurrency(metaDoDia);
        
        // Progresso: quanto % da meta do dia já foi atingido HOJE
        const progressoPercentual = metaDoDia > 0 ? (faturadoHoje / metaDoDia) * 100 : 0;
        const progressoLimitado = Math.min(progressoPercentual, 100);
        
        // Atualiza barra de progresso
        const progressBar = document.getElementById('progressBar');
        const progressPercentage = document.getElementById('progressPercentage');
        
        progressBar.style.width = `${progressoLimitado}%`;
        progressPercentage.textContent = `${progressoLimitado.toFixed(1)}%`;
        
        // Cores dinâmicas
        progressBar.classList.remove('critical', 'attention', 'close', 'complete');
        if (progressoLimitado >= 100) {
            progressBar.classList.add('complete');
        } else if (progressoLimitado >= 70) {
            progressBar.classList.add('close');
        } else if (progressoLimitado >= 30) {
            progressBar.classList.add('attention');
        } else {
            progressBar.classList.add('critical');
        }
        
        // Atualiza valores (faturado HOJE)
        document.getElementById('valorAtual').textContent = formatCurrency(faturadoHoje);
        document.getElementById('valorFaltante').textContent = formatCurrency(Math.max(0, metaDoDia - faturadoHoje));
        document.getElementById('valorPipeline').textContent = formatCurrency(pipelineHoje);
        document.getElementById('dealsCount').textContent = `(${totalDealsPrevistos} ${totalDealsPrevistos === 1 ? 'deal' : 'deals'})`;
        
        // NOVA LÓGICA DE PROJEÇÃO:
        // Projeção = Faturado Hoje + Pipeline Previsto para Hoje
        // Isso é mais assertivo pois considera deals que estão previstos para fechar hoje
        const projecaoFimDia = faturadoHoje + pipelineHoje;
        
        // Calcula média por hora apenas para exibição (mantém para referência)
        const horasTrabalhadas = getHorasTrabalhadasHoje();
        const mediaPorHora = horasTrabalhadas > 0 ? faturadoHoje / horasTrabalhadas : 0;
        
        document.getElementById('mediaPorHora').textContent = formatCurrency(mediaPorHora);
        document.getElementById('projecaoFimDia').textContent = formatCurrency(projecaoFimDia);
        
        // Status - LÓGICA MELHORADA
        const statusText = document.getElementById('statusText');
        const progressoAtual = (faturadoHoje / metaDoDia) * 100;
        const tempoInfo = getTempoRestante();
        const horasRestantes = tempoInfo.totalSeconds / 3600;
        const progressoEsperado = ((24 - horasRestantes) / 24) * 100; // Quanto % deveria ter ao longo do dia
        
        statusText.classList.remove('on-track', 'speed-up', 'critical');
        
        // Se falta menos de 2 horas E está abaixo de 80% = CRÍTICO
        if (horasRestantes <= 2 && progressoAtual < 80) {
            statusText.textContent = '🚨 CRÍTICO!';
            statusText.classList.add('critical');
        }
        // Se o progresso atual está muito abaixo do esperado para o horário
        else if (progressoAtual < progressoEsperado - 20) {
            statusText.textContent = '⚡ ACELERAR!';
            statusText.classList.add('speed-up');
        }
        // Se a projeção atinge a meta E o progresso está razoável
        else if (projecaoFimDia >= metaDoDia && progressoAtual >= progressoEsperado - 10) {
            statusText.textContent = '✅ NO CAMINHO!';
            statusText.classList.add('on-track');
        }
        // Se a projeção atinge mas o progresso atual está atrasado
        else if (projecaoFimDia >= metaDoDia) {
            statusText.textContent = '⚡ ACELERAR!';
            statusText.classList.add('speed-up');
        }
        // Qualquer outro caso = ATENÇÃO
        else {
            statusText.textContent = '🔥 ATENÇÃO!';
            statusText.classList.add('critical');
        }
        
        // Estatísticas do mês
        document.getElementById('faturadoMes').textContent = formatCurrency(faturadoMes);
        document.getElementById('faltaMes').textContent = formatCurrency(faltaMes);
        document.getElementById('diasUteis').textContent = `${diasRestantes} ${diasRestantes === 1 ? 'dia' : 'dias'}`;
        
        // Log para debug (pode remover depois)
        const faltaAtingirMeta = Math.max(0, metaDoDia - faturadoHoje);
        console.log(`📊 Dados atualizados:
- Faturado hoje: ${formatCurrency(faturadoHoje)}
- Pipeline previsto hoje: ${formatCurrency(pipelineHoje)} (${totalDealsPrevistos} deals)
- Projeção fim do dia: ${formatCurrency(projecaoFimDia)}
- Meta do dia: ${formatCurrency(metaDoDia)}
- Status: ${faltaAtingirMeta > 0 ? 'Faltam ' + formatCurrency(faltaAtingirMeta) : 'Meta atingida!'}`);
        
        // Mostra conteúdo e esconde loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('metasContent').style.display = 'block';
        
        // Inicia timer de navegação após dados carregados (apenas no modo aleatório)
        if (isRandomMode) {
            startNavigationTimer();
        }
        
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        document.getElementById('loading').innerHTML = 
            '<div style="color: #ff6b6b;">Erro ao carregar dados. Tentando novamente...</div>';
        
        // Inicia timer de navegação mesmo com erro (apenas no modo aleatório)
        if (isRandomMode) {
            startNavigationTimer();
        }
    }
}

// Atualiza countdown em tempo real
function atualizarCountdown() {
    const { hours, minutes, seconds } = getTempoRestante();
    document.getElementById('countdown').textContent = formatTime(hours, minutes, seconds);
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
    const DURATION = 60000; // 1 minuto
    
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

// Inicialização
async function init() {
    // Carrega dados iniciais
    await atualizarDados();
    
    // Atualiza countdown a cada segundo
    setInterval(atualizarCountdown, 1000);
    atualizarCountdown();
    
    // Atualiza dados periodicamente (apenas se NÃO estiver no modo aleatório)
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('aleatorio')) {
    setInterval(atualizarDados, UPDATE_INTERVAL);
    } else {
        console.log('📦 Modo aleatório: atualizações periódicas desabilitadas (usando cache centralizado)');
    }
}

// Inicia quando página carrega
window.addEventListener('load', init);
