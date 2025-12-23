/**
 * JavaScript para página de Logos Supply - Natal
 */
let logosChart = null;
const REFRESH_INTERVAL = 30000; // 30 segundos

// Registra o plugin de datalabels quando disponível
if (typeof Chart !== 'undefined' && typeof ChartDataLabels !== 'undefined') {
    Chart.register(ChartDataLabels);
}

/**
 * Carrega dados da API
 */
async function loadSupplyLogosData() {
    try {
        const response = await fetch('/api/supply-logos');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Log informativo sobre a fonte dos dados
        if (data.from_looker) {
            console.log('✅ Usando valor do Looker (considera churns):', data.total_current);
        } else {
            console.log('⚠️ Usando valor calculado do banco:', data.total_current);
        }
        
        updateGauge(data);
        updateChart(data);
        updateStats(data);
        
        // Mostra o gauge, cards, gráfico e oculta o loading após os dados carregarem
        const gaugeContainer = document.getElementById('gaugeContainer');
        if (gaugeContainer) {
            gaugeContainer.style.display = 'flex';
        }
        const statsContainer = document.getElementById('statsContainer');
        if (statsContainer) {
            statsContainer.style.display = 'flex';
        }
        const chartContainer = document.getElementById('chartContainer');
        if (chartContainer) {
            chartContainer.style.display = 'block';
        }
        document.getElementById('loading').style.display = 'none';
    } catch (error) {
        console.error('Erro ao carregar dados de logos Supply:', error);
        document.getElementById('loading').innerHTML = '<div>Erro ao carregar dados</div>';
    }
}

/**
 * Atualiza o gauge circular
 */
function updateGauge(data) {
    const percentage = data.percentage || 0;
    const circumference = 2 * Math.PI * 90; // raio = 90
    const offset = circumference - (percentage / 100) * circumference;
    
    const progressCircle = document.getElementById('gaugeProgress');
    if (progressCircle) {
        progressCircle.style.strokeDashoffset = offset;
    }
    
    // Atualiza valores
    document.getElementById('gaugeValue').textContent = data.total_current || 0;
    document.getElementById('gaugeTarget').textContent = data.target || 800;
    document.getElementById('gaugePercentage').textContent = `${percentage.toFixed(1)}%`;
    document.getElementById('gaugeRemaining').textContent = `Faltam: ${data.remaining || 0}`;
}

/**
 * Atualiza estatísticas abaixo do gauge
 */
function updateStats(data) {
    document.getElementById('statNew').textContent = data.new_logos_december || 0;
    document.getElementById('statExpansion').textContent = data.expansion_logos_december || 0;
    document.getElementById('statTotal').textContent = data.total_december || 0;
}

/**
 * Atualiza o gráfico de barras agrupadas
 */
function updateChart(data) {
    const ctx = document.getElementById('logosChart');
    if (!ctx) return;
    
    const products = data.by_product || [];
    const productNames = products.map(p => p.product || 'N/A');
    const newValues = products.map(p => p.new || 0);
    const expansionValues = products.map(p => p.expansion || 0);
    
    // Destrói gráfico anterior se existir
    if (logosChart) {
        logosChart.destroy();
    }
    
    logosChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: productNames,
            datasets: [
                {
                    label: 'New',
                    data: newValues,
                    backgroundColor: 'rgba(102, 19, 208, 0.8)', // Roxo Logcomex #6613D0
                    borderColor: 'rgba(102, 19, 208, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Expansão',
                    data: expansionValues,
                    backgroundColor: 'rgba(254, 143, 28, 0.8)', // Laranja Logcomex #FE8F1C
                    borderColor: 'rgba(254, 143, 28, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            indexAxis: 'y', // Barras horizontais
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 10,
                    top: 10,
                    bottom: 10
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#fff',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    enabled: false // Desabilita tooltip já que valores estão nas barras
                },
                datalabels: {
                    anchor: 'center', // Posiciona o label no centro da barra
                    align: 'center', // Alinha ao centro
                    color: '#fff', // Cor branca para contraste
                    font: {
                        size: 12,
                        weight: 'bold'
                    },
                    formatter: function(value) {
                        // Mostra o valor apenas se for maior que 0
                        return value > 0 ? value : '';
                    },
                    padding: {
                        left: 0,
                        right: 0
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        color: '#fff',
                        font: {
                            size: 11,
                            weight: 'bold'
                        },
                        stepSize: 1,
                        maxRotation: 0,
                        padding: 5
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.2)',
                        lineWidth: 1
                    }
                },
                y: {
                    ticks: {
                        color: '#fff',
                        font: {
                            size: 11,
                            weight: 'bold'
                        },
                        padding: 8
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.2)',
                        lineWidth: 1
                    }
                }
            }
        }
    });
}

/**
 * Inicializa a página
 */
function init() {
    loadSupplyLogosData();
    
    // Atualiza a cada 30 segundos
    setInterval(loadSupplyLogosData, REFRESH_INTERVAL);
}

// Inicia quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

