// Sistema de receita para página de Natal (Dezembro)
// Similar ao funnel.js mas adaptado para dezembro

const GOAL = 739014.83; // Meta de Natal

// Formata valor em moeda brasileira
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Atualiza a barra de progresso temática de Natal
function updateProgressBar(currentValue, goal) {
    const progressBar = document.getElementById('progressBarFill');
    const progressText = document.getElementById('progressText');
    const progressPercentage = document.getElementById('progressPercentage');
    
    if (!progressBar) return;
    
    // Calcula a porcentagem
    const percentage = Math.min((currentValue / goal) * 100, 100);
    
    // Atualiza a largura da barra
    progressBar.style.width = `${percentage}%`;
    
    // Atualiza o texto
    if (progressText) {
        progressText.textContent = formatCurrency(currentValue);
    }
    
    if (progressPercentage) {
        progressPercentage.textContent = `${percentage.toFixed(1)}%`;
    }
    
    // Muda a cor baseado no progresso
    progressBar.classList.remove('low', 'medium', 'high', 'complete');
    if (percentage >= 100) {
        progressBar.classList.add('complete');
    } else if (percentage >= 70) {
        progressBar.classList.add('high');
    } else if (percentage >= 40) {
        progressBar.classList.add('medium');
    } else {
        progressBar.classList.add('low');
    }
}

// Carrega dados de receita
async function loadRevenueData() {
    try {
        // Verifica se está no modo aleatório para usar cache
        const urlParams = new URLSearchParams(window.location.search);
        const isRandomMode = urlParams.has('aleatorio');
        const useCacheParam = isRandomMode ? '&use_cache=true' : '';
        
        // Chama API com parâmetro month=december para pegar dados de dezembro
        const response = await fetch(`/api/revenue?month=december${useCacheParam}`);
        const data = await response.json();

        if (data.error) {
            console.error('Erro:', data.error);
            return;
        }

        // Esconde loading e mostra barra de progresso
        document.getElementById('loading').style.display = 'none';
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
            progressContainer.style.display = 'block';
        }

        // O valor adicional já é aplicado pelo backend se o modo manual estiver ativo
        const currentValue = data.total || 0;
        const goal = data.goal || GOAL;

        // Define a meta no topo
        const mainValueEl = document.getElementById('mainValue');
        if (goal && goal > 0) {
            mainValueEl.textContent = formatCurrency(goal);
        } else {
            mainValueEl.textContent = formatCurrency(GOAL);
        }

        // Atualiza barra de progresso com animação
        setTimeout(() => {
            updateProgressBar(currentValue, goal);
        }, 500);
        
        // Inicia timer de navegação após dados carregados (apenas no modo aleatório)
        if (isRandomMode) {
            // TODO: Implementar timer de navegação se necessário
        }

    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        document.getElementById('loading').innerHTML = 
            '<div style="color: #ff6b6b;">Erro ao carregar dados. Tente novamente.</div>';
    }
}

// Sistema de configurações manual (similar ao funnel.js)
async function loadConfig() {
    const manualModeToggle = document.getElementById('manualModeToggle');
    const additionalValueInput = document.getElementById('additionalValue');
    const manualModeSettings = document.getElementById('manualModeSettings');
    const renewalPipelineToggle = document.getElementById('renewalPipelineToggle');
    
    if (!manualModeToggle || !additionalValueInput || !manualModeSettings || !renewalPipelineToggle) {
        return; // Elementos não existem, não precisa carregar configuração
    }
    
    try {
        const response = await fetch('/api/revenue/manual-revenue/config');
        if (!response.ok) {
            throw new Error('Erro ao carregar configuração');
        }
        const config = await response.json();
        manualModeToggle.checked = config.enabled || false;
        additionalValueInput.value = config.additionalValue || '0';
        manualModeSettings.style.display = config.enabled ? 'flex' : 'none';
        renewalPipelineToggle.checked = config.includeRenewalPipeline || false;
    } catch (error) {
        console.error('Erro ao carregar configuração:', error);
    }
}

async function saveConfig() {
    const manualModeToggle = document.getElementById('manualModeToggle');
    const additionalValueInput = document.getElementById('additionalValue');
    const renewalPipelineToggle = document.getElementById('renewalPipelineToggle');
    
    if (!manualModeToggle || !additionalValueInput || !renewalPipelineToggle) {
        return;
    }
    
    const config = {
        enabled: manualModeToggle.checked,
        additionalValue: parseFloat(additionalValueInput.value) || 0,
        includeRenewalPipeline: renewalPipelineToggle.checked
    };
    
    try {
        const response = await fetch('/api/revenue/manual-revenue/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            // Recarrega os dados após salvar
            loadRevenueData();
        }
    } catch (error) {
        console.error('Erro ao salvar configuração:', error);
    }
}

// Configura eventos dos controles
function setupSettingsControls() {
    const settingsBtn = document.getElementById('settingsBtn');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const settingsMenu = document.getElementById('settingsMenu');
    const manualModeToggle = document.getElementById('manualModeToggle');
    const manualModeSettings = document.getElementById('manualModeSettings');
    
    if (!settingsBtn || !closeSettingsBtn || !settingsMenu) {
        return; // Elementos não existem
    }
    
    settingsBtn.addEventListener('click', () => {
        settingsMenu.style.display = settingsMenu.style.display === 'none' ? 'block' : 'none';
    });
    
    closeSettingsBtn.addEventListener('click', () => {
        settingsMenu.style.display = 'none';
    });
    
    if (manualModeToggle && manualModeSettings) {
        manualModeToggle.addEventListener('change', () => {
            manualModeSettings.style.display = manualModeToggle.checked ? 'flex' : 'none';
            saveConfig();
        });
    }
    
    const additionalValueInput = document.getElementById('additionalValue');
    const renewalPipelineToggle = document.getElementById('renewalPipelineToggle');
    
    if (additionalValueInput) {
        additionalValueInput.addEventListener('change', saveConfig);
        additionalValueInput.addEventListener('blur', saveConfig);
    }
    
    if (renewalPipelineToggle) {
        renewalPipelineToggle.addEventListener('change', saveConfig);
    }
    
    // Configuração do tema de celebração
    const celebrationThemeSelect = document.getElementById('celebrationThemeSelect');
    if (celebrationThemeSelect && window.CelebrationThemeManager) {
        // Carrega tema salvo do servidor
        async function loadThemeConfig() {
            try {
                const currentTheme = await window.CelebrationThemeManager.getCurrentTheme();
                celebrationThemeSelect.value = currentTheme;
            } catch (error) {
                console.error('Erro ao carregar tema:', error);
                // Usa cache do localStorage como fallback
                try {
                    const cachedTheme = localStorage.getItem('deal_celebration_theme') || 'black-november';
                    celebrationThemeSelect.value = cachedTheme;
                } catch (e) {
                    celebrationThemeSelect.value = 'black-november';
                }
            }
        }
        
        loadThemeConfig();
        
        // Salva quando mudar
        celebrationThemeSelect.addEventListener('change', async (e) => {
            const selectedTheme = e.target.value;
            if (await window.CelebrationThemeManager.saveTheme(selectedTheme)) {
                window.CelebrationThemeManager.applyCurrentThemeToAll();
                console.log('Tema de celebração alterado para:', selectedTheme);
            }
        });
    }
}

// Inicia quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loadConfig();
        setupSettingsControls();
        loadRevenueData();
    });
} else {
    loadConfig();
    setupSettingsControls();
    loadRevenueData();
}

