// Sistema de receita para página padrão
// Versão limpa sem elementos temáticos específicos

const GOAL = 1500000; // Meta padrão (pode ser configurável)

// Nomes dos meses em português
const MONTHS = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

// Atualiza o título com o mês atual
function updateMonthTitle() {
    const currentMonthEl = document.getElementById('currentMonth');
    if (currentMonthEl) {
        const now = new Date();
        const monthName = MONTHS[now.getMonth()];
        currentMonthEl.textContent = monthName;
    }
}

// Formata valor em moeda brasileira
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Atualiza a barra de progresso
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
        
        // Chama API para buscar dados do mês atual
        const response = await fetch(`/api/revenue?month=current${useCacheParam}`);
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
        
        // Verifica se há meta manual configurada
        let goal = data.goal || GOAL;
        try {
            const goalConfigResponse = await fetch('/api/revenue/manual-goal/config');
            if (goalConfigResponse.ok) {
                const goalConfig = await goalConfigResponse.json();
                if (goalConfig.enabled && goalConfig.goalValue) {
                    goal = goalConfig.goalValue;
                }
            }
        } catch (error) {
            console.error('Erro ao carregar configuração de meta manual:', error);
        }

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

    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        document.getElementById('loading').innerHTML = 
            '<div style="color: #ff6b6b;">Erro ao carregar dados. Tente novamente.</div>';
    }
}

// Sistema de configurações manual
async function loadConfig() {
    const manualModeToggle = document.getElementById('manualModeToggle');
    const additionalValueInput = document.getElementById('additionalValue');
    const manualModeSettings = document.getElementById('manualModeSettings');
    const renewalPipelineToggle = document.getElementById('renewalPipelineToggle');
    const manualGoalToggle = document.getElementById('manualGoalToggle');
    const manualGoalValueInput = document.getElementById('manualGoalValue');
    const manualGoalSettings = document.getElementById('manualGoalSettings');
    
    if (!manualModeToggle || !additionalValueInput || !manualModeSettings || !renewalPipelineToggle) {
        return;
    }
    
    try {
        // Carrega configuração de receita manual
        const response = await fetch('/api/revenue/manual-revenue/config');
        if (!response.ok) {
            throw new Error('Erro ao carregar configuração');
        }
        const config = await response.json();
        manualModeToggle.checked = config.enabled || false;
        additionalValueInput.value = config.additionalValue || '0';
        manualModeSettings.style.display = config.enabled ? 'flex' : 'none';
        renewalPipelineToggle.checked = config.includeRenewalPipeline || false;
        
        // Carrega configuração de meta manual
        if (manualGoalToggle && manualGoalValueInput && manualGoalSettings) {
            const goalResponse = await fetch('/api/revenue/manual-goal/config');
            if (goalResponse.ok) {
                const goalConfig = await goalResponse.json();
                manualGoalToggle.checked = goalConfig.enabled || false;
                manualGoalValueInput.value = goalConfig.goalValue || '1500000';
                manualGoalSettings.style.display = goalConfig.enabled ? 'block' : 'none';
            }
        }
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
            loadRevenueData();
        }
    } catch (error) {
        console.error('Erro ao salvar configuração:', error);
    }
}

async function saveGoalConfig() {
    const manualGoalToggle = document.getElementById('manualGoalToggle');
    const manualGoalValueInput = document.getElementById('manualGoalValue');
    
    if (!manualGoalToggle || !manualGoalValueInput) {
        return;
    }
    
    const config = {
        enabled: manualGoalToggle.checked,
        goalValue: parseFloat(manualGoalValueInput.value) || 1500000
    };
    
    try {
        const response = await fetch('/api/revenue/manual-goal/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            loadRevenueData();
        }
    } catch (error) {
        console.error('Erro ao salvar configuração de meta:', error);
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
        return;
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
    
    // Configuração de meta manual
    const manualGoalToggle = document.getElementById('manualGoalToggle');
    const manualGoalValueInput = document.getElementById('manualGoalValue');
    const manualGoalSettings = document.getElementById('manualGoalSettings');
    
    if (manualGoalToggle && manualGoalSettings) {
        manualGoalToggle.addEventListener('change', () => {
            manualGoalSettings.style.display = manualGoalToggle.checked ? 'block' : 'none';
            saveGoalConfig();
        });
    }
    
    if (manualGoalValueInput) {
        manualGoalValueInput.addEventListener('change', saveGoalConfig);
        manualGoalValueInput.addEventListener('blur', saveGoalConfig);
    }
    
    // Configuração do tema de celebração
    const celebrationThemeSelect = document.getElementById('celebrationThemeSelect');
    if (celebrationThemeSelect && window.CelebrationThemeManager) {
        async function loadThemeConfig() {
            try {
                const currentTheme = await window.CelebrationThemeManager.getCurrentTheme();
                celebrationThemeSelect.value = currentTheme;
            } catch (error) {
                console.error('Erro ao carregar tema:', error);
                try {
                    const cachedTheme = localStorage.getItem('deal_celebration_theme') || 'black-november';
                    celebrationThemeSelect.value = cachedTheme;
                } catch (e) {
                    celebrationThemeSelect.value = 'black-november';
                }
            }
        }
        
        loadThemeConfig();
        
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
        updateMonthTitle();
        loadConfig();
        setupSettingsControls();
        loadRevenueData();
    });
} else {
    updateMonthTitle();
    loadConfig();
    setupSettingsControls();
    loadRevenueData();
}
