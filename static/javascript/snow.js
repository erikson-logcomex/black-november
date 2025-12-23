// Efeito de Neve
(function() {
    'use strict';

    // Configurações
    const SNOWFLAKE_COUNT = 50; // Número máximo de flocos de neve
    const SNOWFLAKES = ['❄', '❅', '❆', '✻', '✼', '✽', '✾', '✿', '❀', '❁'];
    
    let container = null;
    let activeFlakes = 0;
    let isActive = true;
    
    // Cria o container de neve
    function createSnowContainer() {
        if (container) return container;
        container = document.createElement('div');
        container.className = 'snow-container';
        container.id = 'snowContainer';
        document.body.appendChild(container);
        return container;
    }

    // Cria um floco de neve individual
    function createSnowflake() {
        if (!isActive || !container) return;
        
        // Limita o número de flocos ativos
        if (activeFlakes >= SNOWFLAKE_COUNT) {
            return;
        }
        
        const snowflake = document.createElement('div');
        snowflake.className = 'snowflake';
        
        // Escolhe um símbolo aleatório
        const symbol = SNOWFLAKES[Math.floor(Math.random() * SNOWFLAKES.length)];
        snowflake.textContent = symbol;
        
        // Posição inicial aleatória
        const startX = Math.random() * 100;
        snowflake.style.left = startX + '%';
        
        // Tamanho aleatório
        const size = Math.random();
        if (size < 0.33) {
            snowflake.classList.add('snowflake-small');
        } else if (size < 0.66) {
            snowflake.classList.add('snowflake-medium');
        } else {
            snowflake.classList.add('snowflake-large');
        }
        
        // Velocidade de queda (duração da animação)
        const duration = 8 + Math.random() * 4; // Entre 8 e 12 segundos
        snowflake.style.animationDuration = duration + 's';
        
        // Deriva horizontal (movimento lateral)
        const drift = (Math.random() - 0.5) * 100; // Entre -50px e 50px
        snowflake.style.setProperty('--drift', drift + 'px');
        
        // Opacidade aleatória
        snowflake.style.opacity = 0.6 + Math.random() * 0.4;
        
        container.appendChild(snowflake);
        
        // Força o início imediato da animação
        // Usando requestAnimationFrame para garantir que a animação comece
        requestAnimationFrame(() => {
            snowflake.style.animationPlayState = 'running';
        });
        activeFlakes++;
        
        // Remove o floco quando a animação terminar e cria um novo
        const timeoutId = setTimeout(() => {
            if (snowflake.parentNode) {
                snowflake.remove();
                activeFlakes--;
                // Cria um novo floco apenas se ainda estiver ativo
                if (isActive && activeFlakes < SNOWFLAKE_COUNT) {
                    createSnowflake();
                }
            }
        }, (duration + 2) * 1000);
        
        // Limpa o timeout se o elemento for removido manualmente
        snowflake._timeoutId = timeoutId;
    }

    // Inicializa o efeito de neve
    function initSnow() {
        container = createSnowContainer();
        activeFlakes = 0;
        isActive = true;
        
        // Cria os flocos iniciais com espaçamento
        for (let i = 0; i < SNOWFLAKE_COUNT; i++) {
            setTimeout(() => {
                if (isActive) {
                    createSnowflake();
                }
            }, i * 200); // Espaça a criação dos flocos
        }
    }
    
    // Limpa todos os flocos (útil se precisar parar o efeito)
    function clearSnow() {
        isActive = false;
        if (container) {
            const flakes = container.querySelectorAll('.snowflake');
            flakes.forEach(flake => {
                if (flake._timeoutId) {
                    clearTimeout(flake._timeoutId);
                }
                flake.remove();
            });
            activeFlakes = 0;
        }
    }

    // Inicia quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSnow);
    } else {
        initSnow();
    }
    
    // Limpa quando a página for descarregada
    window.addEventListener('beforeunload', clearSnow);
})();

