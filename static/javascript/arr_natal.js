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
    const percentage = data.percentage || 0;
    // Para um semicírculo, o comprimento é π * raio (raio = 500 no SVG atualizado)
    const semicircleLength = Math.PI * 500; // ≈ 1570.8
    const offset = semicircleLength - (percentage / 100) * semicircleLength;
    
    const progressPath = document.getElementById('gaugeProgress');
    if (progressPath) {
        progressPath.style.strokeDashoffset = offset;
    }
    
    // Atualiza valores no container de métricas
    const arrValue = document.getElementById('arrValue');
    if (arrValue) {
        arrValue.textContent = formatCurrency(data.arr_value || 0);
    }
    
    const arrTarget = document.getElementById('arrTarget');
    if (arrTarget) {
        arrTarget.textContent = formatCurrency(data.arr_target || 225000000);
    }
    
    const arrPercentage = document.getElementById('arrPercentage');
    if (arrPercentage) {
        arrPercentage.textContent = `${percentage.toFixed(1)}%`;
    }
    
    const arrRemaining = document.getElementById('arrRemaining');
    if (arrRemaining) {
        if (data.remaining && data.remaining > 0) {
            arrRemaining.textContent = formatCurrency(data.remaining);
        } else {
            arrRemaining.textContent = 'Meta alcançada! 🎉';
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

