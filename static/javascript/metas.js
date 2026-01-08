// Configurações
const META_MENSAL_DEFAULT = 1500000; // R$ 1.500.000 (valor padrão)
const HORA_INICIO_EXPEDIENTE = 9; // 09:00
const HORA_FIM_EXPEDIENTE = 18; // 18:00
const UPDATE_INTERVAL = 300000; // Atualiza a cada 5 minutos

// Variável global para armazenar a meta mensal (pode ser alterada pela meta manual)
let META_MENSAL = META_MENSAL_DEFAULT;

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

// Feriados nacionais brasileiros (formato: [mês, dia])
// Mês: 0-11 (janeiro = 0, dezembro = 11)
const FERIADOS_NACIONAIS = [
    [0, 1],   // 1º de Janeiro - Ano Novo
    [2, 21],  // 21 de Março - Tiradentes (corrigido: abril é mês 3)
    [3, 21],  // 21 de Abril - Tiradentes
    [4, 1],   // 1º de Maio - Dia do Trabalho
    [8, 7],   // 7 de Setembro - Independência
    [9, 12],  // 12 de Outubro - Nossa Senhora Aparecida
    [10, 2],  // 2 de Novembro - Finados
    [10, 15], // 15 de Novembro - Proclamação da República
    [10, 20], // 20 de Novembro - Dia da Consciência Negra
    [11, 25], // 25 de Dezembro - Natal
];

// Verifica se uma data é feriado
function isFeriado(date) {
    const mes = date.getMonth();
    const dia = date.getDate();
    return FERIADOS_NACIONAIS.some(([m, d]) => m === mes && d === dia);
}

// Verifica se uma data é fim de semana
function isWeekend(date) {
    const diaSemana = date.getDay();
    return diaSemana === 0 || diaSemana === 6; // 0 = domingo, 6 = sábado
}

// Verifica se uma data é dia útil
function isDiaUtil(date) {
    return !isWeekend(date) && !isFeriado(date);
}

// Calcula o total de dias úteis do mês atual
function getTotalDiasUteisMes() {
    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = hoje.getMonth();
    
    // Primeiro dia do mês
    const primeiroDia = new Date(ano, mes, 1);
    // Último dia do mês
    const ultimoDia = new Date(ano, mes + 1, 0);
    
    let totalDiasUteis = 0;
    for (let dia = primeiroDia.getDate(); dia <= ultimoDia.getDate(); dia++) {
        const data = new Date(ano, mes, dia);
        if (isDiaUtil(data)) {
            totalDiasUteis++;
        }
    }
    
    return totalDiasUteis;
}

// Calcula quantos dias úteis já passaram no mês atual (NÃO inclui o dia atual)
function getDiasUteisPassados() {
    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = hoje.getMonth();
    const diaAtual = hoje.getDate();
    
    let diasUteisPassados = 0;
    // Conta apenas os dias anteriores ao dia atual (dia < diaAtual)
    for (let dia = 1; dia < diaAtual; dia++) {
        const data = new Date(ano, mes, dia);
        if (isDiaUtil(data)) {
            diasUteisPassados++;
        }
    }
    
    return diasUteisPassados;
}

// Calcula dias úteis restantes no mês atual
function getDiasUteisRestantes() {
    const totalDiasUteis = getTotalDiasUteisMes();
    const diasUteisPassados = getDiasUteisPassados();
    return Math.max(0, totalDiasUteis - diasUteisPassados);
}

// Carrega a meta manual se configurada
async function loadManualGoal() {
    try {
        const response = await fetch('/api/revenue/manual-goal/config');
        if (response.ok) {
            const config = await response.json();
            // O campo correto é goalValue (conforme API)
            const goalValue = config.goalValue;
            if (config.enabled && goalValue && goalValue > 0) {
                META_MENSAL = goalValue;
                console.log('✅ Meta manual carregada:', formatCurrency(goalValue));
                return goalValue;
            } else {
                console.log('ℹ️ Meta manual desabilitada ou não configurada');
            }
        }
    } catch (error) {
        console.error('Erro ao carregar meta manual:', error);
    }
    // Se não houver meta manual, usa a meta da API ou o padrão
    META_MENSAL = META_MENSAL_DEFAULT;
    console.log('ℹ️ Usando meta padrão:', formatCurrency(META_MENSAL_DEFAULT));
    return META_MENSAL_DEFAULT;
}

// Calcula meta do dia baseada no que falta atingir dividido pelos dias úteis restantes
// Meta do dia = (Meta mensal - Faturado até ontem) / Dias úteis restantes
// TOTALMENTE DINÂMICO: Calcula automaticamente baseado no mês e dia atual
function calcularMetaDoDia(faturadoAteOntem, metaMensal = META_MENSAL) {
    // Calcula o que falta para atingir a meta
    const faltaMes = metaMensal - faturadoAteOntem;
    
    // Se já atingiu ou ultrapassou a meta, meta do dia = 0
    if (faltaMes <= 0) {
        return 0;
    }
    
    // Calcula dias úteis restantes DINAMICAMENTE (baseado no mês e dia atual)
    const diasRestantes = getDiasUteisRestantes();
    
    // Log para debug (pode remover depois)
    const hoje = new Date();
    const mesAtual = hoje.getMonth() + 1; // +1 porque getMonth() retorna 0-11
    const anoAtual = hoje.getFullYear();
    console.log(`📅 Cálculo dinâmico - Mês: ${mesAtual}/${anoAtual}, Dias úteis restantes: ${diasRestantes}, Falta: ${formatCurrency(faltaMes)}`);
    
    // Se não há dias restantes, retorna o que falta
    if (diasRestantes === 0) {
        return faltaMes;
    }
    
    // Meta do dia = (Meta mensal - Faturado até ontem) / Dias úteis restantes
    const metaDoDia = faltaMes / diasRestantes;
    console.log(`🎯 Meta do dia calculada: ${formatCurrency(metaDoDia)} (${formatCurrency(faltaMes)} / ${diasRestantes} dias)`);
    
    return metaDoDia;
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
        // Carrega a meta manual primeiro (se configurada)
        await loadManualGoal();
        
        // Usa cache se estiver no modo aleatório
        const useCacheParam = isRandomMode ? '&use_cache=true' : '';
        
        // Busca faturamento do mês atual (para calcular meta do dia), do dia atual E pipeline previsto para hoje em paralelo
        // Usa month=current para garantir que está olhando para o mês atual
        const [responseCurrentMonth, responseToday, responsePipeline] = await Promise.all([
            fetch(`/api/revenue?month=current${useCacheParam}`),
            fetch(`/api/revenue/today${useCacheParam.replace('&', '?')}`),
            fetch(`/api/pipeline/today${useCacheParam.replace('&', '?')}`)
        ]);
        
        const dataCurrentMonth = await responseCurrentMonth.json();
        const dataToday = await responseToday.json();
        const dataPipeline = await responsePipeline.json();
        
        // O valor adicional já é aplicado pelo backend se o modo manual estiver ativo
        // dataCurrentMonth.total = faturamento total do mês atual
        const faturadoMes = dataCurrentMonth.total || 0;
        const faturadoHoje = dataToday.total_today || 0;
        // Faturado até ontem = Total do mês - Faturado hoje
        const faturadoAteOntem = Math.max(0, faturadoMes - faturadoHoje);
        const pipelineHoje = dataPipeline.total_pipeline || 0;
        const totalDealsPrevistos = dataPipeline.total_deals || 0;
        
        // Usa a meta mensal atual (pode ser a manual ou a padrão)
        const metaMensalAtual = META_MENSAL;
        
        // Calcula meta do dia baseado no que falta dividido pelos dias úteis restantes
        // Meta do dia = (Meta mensal - Faturado até ontem) / Dias úteis restantes
        const metaDoDia = calcularMetaDoDia(faturadoAteOntem, metaMensalAtual);
        const faltaMes = Math.max(0, metaMensalAtual - faturadoMes);
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
        
        // Barra mantém cor laranja sólida sempre (sem mudança de cor)
        
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
        document.getElementById('metaMes').textContent = formatCurrency(metaMensalAtual);
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
