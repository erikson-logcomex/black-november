/**
 * JavaScript para página de ARR - Natal
 */
const REFRESH_INTERVAL = 30000; // 30 segundos

/**
 * Formata valor monetário em R$
 */
function formatCurrency(value) {
    if (!value && value !== 0) return '-';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

/**
 * Carrega dados da API
 */
async function loadARRData() {
    try {
        const response = await fetch('/api/arr');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Log informativo sobre a fonte dos dados
        if (data.arr_value) {
            console.log('✅ Dados de ARR carregados:', formatCurrency(data.arr_value));
        } else {
            console.log('⚠️ Dados de ARR não disponíveis');
        }
        
        updateGauge(data);
        
        // Mostra o gauge, métricas e oculta o loading após os dados carregarem
        const gaugeContainer = document.getElementById('gaugeContainer');
        if (gaugeContainer) {
            gaugeContainer.style.display = 'flex';
        }
        const metricsContainer = document.getElementById('metricsContainer');
        if (metricsContainer) {
            metricsContainer.style.display = 'flex';
        }
        document.getElementById('loading').style.display = 'none';
    } catch (error) {
        console.error('Erro ao carregar dados de ARR:', error);
        document.getElementById('loading').innerHTML = '<div>Erro ao carregar dados</div>';
    }
}

/**
 * Atualiza o gauge semicircular e as métricas
 */
function updateGauge(data) {
    const arrValue = data.arr_value || 0;
    const arrTarget = data.arr_target || 276103;
    const percentage = data.percentage || 0;
    
    // Para o gauge, limita a 100% visualmente (gauge completo)
    const gaugePercentage = Math.min(percentage, 100);
    const semicircleLength = Math.PI * 500; // ≈ 1570.8
    const offset = semicircleLength - (gaugePercentage / 100) * semicircleLength;
    
    const progressPath = document.getElementById('gaugeProgress');
    if (progressPath) {
        progressPath.style.strokeDashoffset = offset;
    }
    
    // Atualiza valores no container de métricas
    const arrValueEl = document.getElementById('arrValue');
    if (arrValueEl) {
        arrValueEl.textContent = formatCurrency(arrValue);
    }
    
    const arrTargetEl = document.getElementById('arrTarget');
    if (arrTargetEl) {
        arrTargetEl.textContent = formatCurrency(arrTarget);
    }
    
    // Log para debug
    console.log('ARR Debug:', {
        arrValue: arrValue,
        arrTarget: arrTarget,
        percentage: percentage,
        remaining: data.remaining
    });
    
    const arrPercentageEl = document.getElementById('arrPercentage');
    if (arrPercentageEl) {
        // Mostra porcentagem real (pode ser > 100%)
        arrPercentageEl.textContent = `${percentage.toFixed(1)}%`;
    }
    
    const arrRemainingEl = document.getElementById('arrRemaining');
    if (arrRemainingEl) {
        // Verifica se a meta foi alcançada
        if (arrValue >= arrTarget) {
            arrRemainingEl.textContent = 'Meta alcançada! 🎉';
        } else if (data.remaining !== null && data.remaining !== undefined && data.remaining > 0) {
            arrRemainingEl.textContent = formatCurrency(data.remaining);
        } else {
            // Fallback: calcula remaining se não vier do backend
            const remaining = arrTarget - arrValue;
            arrRemainingEl.textContent = formatCurrency(remaining);
        }
    }
}

/**
 * Inicializa a página
 */
function init() {
    loadARRData();
    
    // Atualiza a cada 30 segundos
    setInterval(loadARRData, REFRESH_INTERVAL);
}

// Inicia quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

