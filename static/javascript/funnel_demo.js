const GOAL = 1500000;
const MILESTONES = [
    { value: 300000, position: 80 },
    { value: 600000, position: 60 },
    { value: 900000, position: 40 },
    { value: 1200000, position: 20 },
    { value: 1500000, position: 0 }
];

let currentValue = 49036;
let simulationInterval = null;
let simulationDirection = 1; // 1 = subindo, -1 = descendo

const phrases = [
    { text: 'MAÔEEEEEE', syllables: 3 },
    { text: 'Quem quer dinheiroooo?', syllables: 5 }
];
let currentPhraseIndex = 0;
let animationTimeout = null;
let mouthAnimationInterval = null;
let isSpeaking = false;

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function getColorForValue(value) {
    if (value >= 1200000) {
        return '#7B2FDD';
    } else if (value >= 900000) {
        return '#9D4EDD';
    } else if (value >= 600000) {
        return '#E07A3C';
    } else if (value >= 300000) {
        return '#FE8F1C';
    } else {
        return '#FE8F1C';
    }
}

function updateFunnel(value) {
    currentValue = value;
    const funnelFill = document.getElementById('funnelFill');
    const currentIndicator = document.getElementById('currentIndicator');
    const connectionLine = document.getElementById('connectionLine');
    const linePath = document.getElementById('connectionLinePath');
    const funnelContainer = document.querySelector('.funnel-container');
    const funnelWrapper = document.getElementById('funnelWrapper');
    
    const percentage = Math.min((value / GOAL) * 100, 100);
    const heightPercentage = Math.max(percentage, 0.5);

    const gradientColor = getColorForValue(value);
    funnelFill.style.background = `linear-gradient(180deg, 
        ${gradientColor} 0%, 
        ${gradientColor} ${heightPercentage - 0.1}%,
        #FE8F1C ${heightPercentage}%, 
        #FE8F1C 100%
    )`;
    funnelFill.style.height = `${heightPercentage}%`;
    
    // Atualiza indicador
    if (value > 0) {
        const positionFromTop = 100 - heightPercentage;
        const funnelLeftX = 30 * (positionFromTop / 100);
        
        requestAnimationFrame(() => {
            const containerRect = funnelContainer.getBoundingClientRect();
            const indicatorRect = currentIndicator.getBoundingClientRect();
            const wrapperRect = funnelWrapper.getBoundingClientRect();
            
            const wrapperHeight = funnelWrapper.offsetHeight;
            const wrapperTop = wrapperRect.top - containerRect.top;
            const fillTopY = wrapperTop + ((100 - heightPercentage) / 100 * wrapperHeight);
            
            const indicatorX = indicatorRect.left - containerRect.left + (indicatorRect.width / 2);
            const wrapperWidth = funnelWrapper.offsetWidth;
            const wrapperLeft = wrapperRect.left - containerRect.left;
            const fillTopX = wrapperLeft + (wrapperWidth * funnelLeftX / 100);
            
            connectionLine.style.width = `${containerRect.width}px`;
            connectionLine.style.height = `${containerRect.height}px`;
            connectionLine.style.position = 'absolute';
            connectionLine.style.top = '0';
            connectionLine.style.left = '0';
            connectionLine.style.display = 'block';
            connectionLine.setAttribute('viewBox', `0 0 ${containerRect.width} ${containerRect.height}`);
            
            linePath.setAttribute('x1', indicatorX.toString());
            linePath.setAttribute('y1', fillTopY.toString());
            linePath.setAttribute('x2', fillTopX.toString());
            linePath.setAttribute('y2', fillTopY.toString());
            
            const indicatorBottom = containerRect.height - fillTopY;
            const indicatorBottomPercent = (indicatorBottom / containerRect.height) * 100;
            const indicatorHeight = indicatorRect.height;
            currentIndicator.style.bottom = `${indicatorBottomPercent - (indicatorHeight / containerRect.height * 50)}%`;
        });
        
        currentIndicator.style.display = 'block';
        currentIndicator.textContent = formatCurrency(value);
    } else {
        currentIndicator.style.display = 'none';
        connectionLine.style.display = 'none';
    }
    
    // Destaca marcos alcançados
    MILESTONES.forEach(milestone => {
        if (milestone.value === 1500000) return;
        const milestoneEl = document.querySelector(`[data-value="${milestone.value}"]`);
        if (milestoneEl) {
            if (value >= milestone.value) {
                milestoneEl.classList.add('reached');
            } else {
                milestoneEl.classList.remove('reached');
            }
        }
    });

    // Atualiza animação do CSO baseado no valor
    updateCSOAnimation(value);
}

function setValue(value) {
    stopSimulation();
    document.getElementById('valueSlider').value = value;
    document.getElementById('valueDisplay').textContent = formatCurrency(value);
    updateFunnel(value);
}

function toggleSimulation() {
    if (simulationInterval) {
        stopSimulation();
    } else {
        startSimulation();
    }
}

function startSimulation() {
    const statusEl = document.getElementById('simulationStatus');
    const statusText = document.getElementById('statusText');
    
    statusEl.classList.add('active');
    statusText.textContent = 'Simulando...';
    
    let value = currentValue;
    simulationInterval = setInterval(() => {
        value += simulationDirection * 50000; // Incremento de R$ 50k
        
        if (value >= GOAL) {
            value = GOAL;
            simulationDirection = -1; // Começa a descer
        } else if (value <= 0) {
            value = 0;
            simulationDirection = 1; // Começa a subir
        }
        
        document.getElementById('valueSlider').value = value;
        document.getElementById('valueDisplay').textContent = formatCurrency(value);
        updateFunnel(value);
    }, 500); // Atualiza a cada 500ms
}

function stopSimulation() {
    if (simulationInterval) {
        clearInterval(simulationInterval);
        simulationInterval = null;
    }
    const statusEl = document.getElementById('simulationStatus');
    const statusText = document.getElementById('statusText');
    statusEl.classList.remove('active');
    statusText.textContent = 'Parado';
}

// Slider control
document.getElementById('valueSlider').addEventListener('input', function(e) {
    const value = parseInt(e.target.value);
    document.getElementById('valueDisplay').textContent = formatCurrency(value);
    stopSimulation();
    updateFunnel(value);
});

// CSO Animation (mesma lógica do funnel.html)
function speakPhrase(phraseIndex) {
    const csoImage = document.getElementById('csoImage');
    const speechBubble = document.getElementById('speechBubble');
    const speechText = document.getElementById('speechText');
    
    const phrase = phrases[phraseIndex];
    const totalDuration = 3000;
    const syllableCount = phrase.syllables;
    const lastSyllableDuration = totalDuration * 0.6;
    const remainingDuration = totalDuration * 0.4;
    const firstSyllablesDuration = remainingDuration / (syllableCount - 1);
    
    speechText.textContent = phrase.text;
    speechBubble.style.display = 'block';
    speechText.style.opacity = '1';
    speechBubble.offsetHeight;
    
    requestAnimationFrame(() => {
        speechBubble.classList.add('show');
        isSpeaking = true;
        
        if (mouthAnimationInterval) clearInterval(mouthAnimationInterval);
        
        let syllableIndex = 0;
        const animateMouth = () => {
            if (!isSpeaking) return;
            
            const isLastSyllable = syllableIndex === syllableCount - 1;
            const syllableDuration = isLastSyllable ? lastSyllableDuration : firstSyllablesDuration;
            
            csoImage.classList.add('speaking');
            
            const closeDelay = isLastSyllable ? syllableDuration * 0.7 : syllableDuration / 2;
            setTimeout(() => {
                if (isSpeaking) {
                    csoImage.classList.remove('speaking');
                }
            }, closeDelay);
            
            syllableIndex++;
            if (syllableIndex < syllableCount) {
                setTimeout(animateMouth, syllableDuration);
            }
        };
        
        animateMouth();
    });
    
    setTimeout(() => {
        isSpeaking = false;
        csoImage.classList.remove('speaking');
        speechBubble.classList.remove('show');
        if (mouthAnimationInterval) clearInterval(mouthAnimationInterval);
        setTimeout(() => {
            speechBubble.style.display = 'none';
        }, 200);
    }, totalDuration);
}

function startSpeakingCycle() {
    const csoImage = document.getElementById('csoImage');
    const speechBubble = document.getElementById('speechBubble');
    
    clearTimeout(animationTimeout);
    if (mouthAnimationInterval) clearInterval(mouthAnimationInterval);
    
    csoImage.classList.remove('speaking');
    speechBubble.style.display = 'none';
    isSpeaking = false;
    
    animationTimeout = setTimeout(() => {
        speakPhrase(0);
        
        setTimeout(() => {
            speakPhrase(1);
            
            setTimeout(() => {
                startSpeakingCycle();
            }, 8000);
        }, 8000);
    }, 4000);
}

function updateCSOAnimation(value) {
    // CSO só anima se o valor estiver acima de um threshold ou durante simulação
    if (value > 0 || simulationInterval) {
        if (!animationTimeout) {
            startSpeakingCycle();
        }
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    updateFunnel(currentValue);
    startSpeakingCycle();
});

// Para a animação quando a página não está visível
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        clearTimeout(animationTimeout);
        if (mouthAnimationInterval) clearInterval(mouthAnimationInterval);
        stopSimulation();
    } else {
        startSpeakingCycle();
    }
});














