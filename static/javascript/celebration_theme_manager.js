/**
 * Gerenciador de Temas para Celebração de Deals
 * Permite alternar entre diferentes temas visuais para as celebrações
 */

const CELEBRATION_THEMES = {
    'black-november': {
        name: 'Black November',
        description: 'Tema clássico dourado e laranja'
    },
    'natal': {
        name: 'Natal',
        description: 'Tema natalino verde e dourado'
    },
    'padrao': {
        name: 'Padrão',
        description: 'Tema padrão Logcomex - roxo e laranja'
    }
};

const THEME_STORAGE_KEY = 'deal_celebration_theme';
const DEFAULT_THEME = 'black-november';

/**
 * Obtém o tema atual salvo (ou retorna o padrão)
 * Primeiro tenta carregar do servidor, depois do localStorage como fallback
 */
async function getCurrentTheme() {
    try {
        // Tenta carregar do servidor
        const response = await fetch('/api/revenue/celebration-theme/config');
        if (response.ok) {
            const config = await response.json();
            if (config.theme && CELEBRATION_THEMES[config.theme]) {
                // Sincroniza com localStorage como cache
                try {
                    localStorage.setItem(THEME_STORAGE_KEY, config.theme);
                } catch (e) {
                    // Ignora erro de localStorage
                }
                return config.theme;
            }
        }
    } catch (error) {
        console.warn('Erro ao carregar tema do servidor, usando localStorage:', error);
    }
    
    // Fallback para localStorage
    try {
        const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
        if (savedTheme && CELEBRATION_THEMES[savedTheme]) {
            return savedTheme;
        }
    } catch (error) {
        console.warn('Erro ao ler tema do localStorage:', error);
    }
    
    return DEFAULT_THEME;
}

/**
 * Salva o tema selecionado no servidor e localStorage
 */
async function saveTheme(themeName) {
    if (!CELEBRATION_THEMES[themeName]) {
        return false;
    }
    
    try {
        // Salva no servidor
        const response = await fetch('/api/revenue/celebration-theme/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ theme: themeName })
        });
        
        if (response.ok) {
            // Também salva no localStorage como cache
            try {
                localStorage.setItem(THEME_STORAGE_KEY, themeName);
            } catch (e) {
                // Ignora erro de localStorage, mas continua
            }
            return true;
        } else {
            console.error('Erro ao salvar tema no servidor:', await response.text());
            // Tenta salvar apenas no localStorage como fallback
            try {
                localStorage.setItem(THEME_STORAGE_KEY, themeName);
                return true;
            } catch (e) {
                return false;
            }
        }
    } catch (error) {
        console.error('Erro ao salvar tema:', error);
        // Tenta salvar apenas no localStorage como fallback
        try {
            localStorage.setItem(THEME_STORAGE_KEY, themeName);
            return true;
        } catch (e) {
            return false;
        }
    }
}

/**
 * Aplica o tema a um elemento de celebração
 */
function applyThemeToElement(element, themeName) {
    if (!element || !CELEBRATION_THEMES[themeName]) {
        return;
    }
    
    // Remove todos os temas
    Object.keys(CELEBRATION_THEMES).forEach(theme => {
        element.classList.remove(`theme-${theme}`);
    });
    
    // Adiciona o tema selecionado
    element.classList.add(`theme-${themeName}`);
}

/**
 * Aplica o tema atual a todos os elementos de celebração existentes
 * Usa cache do localStorage para resposta imediata
 */
function applyCurrentThemeToAll() {
    let currentTheme = DEFAULT_THEME;
    try {
        const cachedTheme = localStorage.getItem(THEME_STORAGE_KEY);
        if (cachedTheme && CELEBRATION_THEMES[cachedTheme]) {
            currentTheme = cachedTheme;
        }
    } catch (e) {
        // Usa default
    }
    
    const celebrationElements = document.querySelectorAll('.deal-celebration');
    
    celebrationElements.forEach(element => {
        applyThemeToElement(element, currentTheme);
    });
}

/**
 * Obtém a lista de temas disponíveis
 */
function getAvailableThemes() {
    return Object.keys(CELEBRATION_THEMES).map(key => ({
        id: key,
        ...CELEBRATION_THEMES[key]
    }));
}

/**
 * Inicializa o gerenciador de temas
 * Deve ser chamado quando a página carregar
 */
async function initThemeManager() {
    // Carrega e aplica o tema atual a elementos existentes
    const currentTheme = await getCurrentTheme();
    applyCurrentThemeToAll();
    
    // Observa novos elementos de celebração sendo adicionados
    const observer = new MutationObserver(async (mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1 && node.classList && node.classList.contains('deal-celebration')) {
                    // Usa tema do cache (localStorage) para resposta imediata
                    try {
                        const cachedTheme = localStorage.getItem(THEME_STORAGE_KEY) || DEFAULT_THEME;
                        applyThemeToElement(node, cachedTheme);
                    } catch (e) {
                        applyThemeToElement(node, DEFAULT_THEME);
                    }
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Exporta funções para uso em outros módulos
if (typeof window !== 'undefined') {
    window.CelebrationThemeManager = {
        getCurrentTheme,
        saveTheme,
        applyThemeToElement,
        applyCurrentThemeToAll,
        getAvailableThemes,
        initThemeManager,
        CELEBRATION_THEMES
    };
}

