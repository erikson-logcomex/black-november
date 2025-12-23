const GOAL = 1500000; // Meta de R$ 1.5M
const MILESTONES = [
    { value: 300000, position: 80 },
    { value: 600000, position: 60 },
    { value: 900000, position: 40 },
    { value: 1200000, position: 20 },
    { value: 1500000, position: 0 }
];

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function animateValue(element, start, end, duration) {
    const startTime = performance.now();
    const difference = end - start;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = start + (difference * easeOutQuart);
        
        element.textContent = formatCurrency(current);

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = formatCurrency(end);
        }
    }

    requestAnimationFrame(update);
}

function getColorForValue(value) {
    // Determina a cor baseada no valor atual
    if (value >= 1200000) {
        return '#7B2FDD'; // Roxo médio - seção R$ 1.200.000
    } else if (value >= 900000) {
        return '#9D4EDD'; // Roxo claro - seção R$ 900.000
    } else if (value >= 600000) {
        return '#E07A3C'; // Laranja-escuro - seção R$ 600.000
    } else if (value >= 300000) {
        return '#FE8F1C'; // Laranja - seção R$ 300.000
    } else {
        return '#FE8F1C'; // Laranja na base
    }
}

function updateFunnel(currentValue) {
    const funnelFill = document.getElementById('funnelFill');
    const currentIndicator = document.getElementById('currentIndicator');
    
    // Calcula a porcentagem do goal
    const percentage = Math.min((currentValue / GOAL) * 100, 100);
    const heightPercentage = Math.max(percentage, 0.5); // Mínimo 0.5% para ser visível
    
    // Determina a cor baseada no valor atual e calcula o gradiente
    // O preenchimento sempre começa com laranja na base e vai até a cor correspondente
    let gradientColor;
    if (currentValue >= 1200000) {
        // Valor alto: gradiente completo do roxo ao laranja
        gradientColor = `linear-gradient(180deg, #7B2FDD 0%, #9D4EDD 25%, #E07A3C 50%, #FE8F1C 100%)`;
    } else if (currentValue >= 900000) {
        // Valor médio-alto: roxo claro ao laranja
        gradientColor = `linear-gradient(180deg, #9D4EDD 0%, #E07A3C 40%, #FE8F1C 100%)`;
    } else if (currentValue >= 600000) {
        // Valor médio: laranja escuro ao laranja claro
        gradientColor = `linear-gradient(180deg, #E07A3C 0%, #FE8F1C 100%)`;
    } else {
        // Valor baixo: apenas laranja
        gradientColor = `linear-gradient(180deg, #FE8F1C 0%, #FE8F1C 100%)`;
    }
    
    // Atualiza a cor do preenchimento
    funnelFill.style.background = gradientColor;
    
    // Atualiza a altura do preenchimento (de baixo para cima)
    funnelFill.style.height = `${heightPercentage}%`;
    
    // Atualiza indicador de valor atual - posicionado à esquerda do funil, seguindo a inclinação
    if (currentValue > 0) {
        const funnelWrapper = document.getElementById('funnelWrapper');
        const funnelContainer = document.querySelector('.funnel-container');
        const isMobile = window.innerWidth <= 768;
        
        currentIndicator.style.display = 'block';
        currentIndicator.textContent = formatCurrency(currentValue);
        
        // Em mobile, posiciona o indicador ao lado direito do funil, na altura do preenchimento
        if (isMobile) {
            // Calcula a posição Y do topo do preenchimento
            requestAnimationFrame(() => {
                const containerRect = funnelContainer.getBoundingClientRect();
                const wrapperRect = funnelWrapper.getBoundingClientRect();
                
                const wrapperHeight = funnelWrapper.offsetHeight;
                const wrapperTop = wrapperRect.top - containerRect.top;
                const fillTopY = wrapperTop + ((100 - heightPercentage) / 100 * wrapperHeight);
                
                // Garante que o indicador não fique cortado no topo (mínimo 60px do topo do container)
                const minTop = 60;
                const indicatorTop = Math.max(minTop, fillTopY - 15);
                
                // Posiciona o indicador à direita do funil, na mesma altura do topo do preenchimento
                currentIndicator.style.top = `${indicatorTop}px`;
                currentIndicator.style.right = '10px';
                currentIndicator.style.left = 'auto';
                currentIndicator.style.bottom = 'auto';
                currentIndicator.style.transform = 'none';
            });
        } else {
            // Desktop: posicionamento à esquerda do funil
            // O funil tem clip-path: polygon(0% 0%, 100% 0%, 70% 100%, 30% 100%)
            // Lado esquerdo: vai de 0% no topo até 30% na base
            const positionFromTop = 100 - heightPercentage;
            const funnelLeftX = 30 * (positionFromTop / 100);
            
            if (funnelWrapper) {
                const wrapperWidth = funnelWrapper.offsetWidth;
                const leftX = wrapperWidth * (funnelLeftX / 100);
                currentIndicator.style.left = `${leftX - 250}px`;
            } else {
                currentIndicator.style.left = `calc(${funnelLeftX}% - 250px)`;
            }
            
            currentIndicator.style.transform = 'none';
            
            // Desenha linha HORIZONTAL conectando o indicador ao topo do preenchimento
            const connectionLine = document.getElementById('connectionLine');
            const linePath = document.getElementById('connectionLinePath');
            
            if (connectionLine && linePath && funnelWrapper && funnelContainer && funnelWrapper.offsetWidth > 0) {
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
            } else {
                if (connectionLine) connectionLine.style.display = 'none';
            }
        }
    } else {
        currentIndicator.style.display = 'none';
        const connectionLine = document.getElementById('connectionLine');
        if (connectionLine) connectionLine.style.display = 'none';
    }
    
    // Destaca marcos alcançados e dispara chuva de dinheiro
    MILESTONES.forEach(milestone => {
        // Pula o marco da meta (1500000) pois não está mais no funil e terá animação especial
        if (milestone.value === 1500000) return;
        
        const milestoneEl = document.querySelector(`[data-value="${milestone.value}"]`);
        if (milestoneEl) {
            const storageKey = `milestone_reached_${milestone.value}`;
            const wasReachedInStorage = localStorage.getItem(storageKey) === 'true';
            const wasReachedInDOM = milestoneEl.classList.contains('reached');
            
            if (currentValue >= milestone.value) {
                milestoneEl.classList.add('reached');
                
                // Se acabou de atingir o marco (não estava alcançado antes E não foi salvo no localStorage)
                if (!wasReachedInDOM && !wasReachedInStorage) {
                    console.log(`🎯 Marco R$ ${milestone.value.toLocaleString('pt-BR')} alcançado pela primeira vez!`);
                    triggerMoneyRain();
                    // Ativa o vídeo do Allan junto com a chuva de dinheiro
                    activateAllanVideo();
                    // Salva no localStorage para não repetir
                    localStorage.setItem(storageKey, 'true');
                } else if (wasReachedInStorage) {
                    console.log(`✅ Marco R$ ${milestone.value.toLocaleString('pt-BR')} já foi alcançado anteriormente (salvo no localStorage)`);
                }
            } else {
                milestoneEl.classList.remove('reached');
                // Se o valor caiu abaixo do marco, remove do localStorage para permitir nova celebração
                if (wasReachedInStorage) {
                    localStorage.removeItem(storageKey);
                    console.log(`🔄 Marco R$ ${milestone.value.toLocaleString('pt-BR')} foi resetado (valor caiu)`);
                }
            }
        }
    });
}

// Função para disparar chuva de dinheiro
function triggerMoneyRain() {
    const video = document.getElementById('moneyRainVideo');
    if (!video) {
        console.error('Vídeo não encontrado!');
        return;
    }
    
    console.log('Disparando chuva de dinheiro...');
    
    // Configura o vídeo para processar chroma key na primeira vez
    if (video.dataset.chromakeySetup !== 'true') {
        console.log('Configurando chroma key pela primeira vez...');
        setupChromaKey(video);
    }
    
    // Garante que o vídeo está carregado
    const tryPlay = () => {
        if (video.readyState >= 2) { // HAVE_CURRENT_DATA ou superior
            // Aguarda um frame para garantir que o canvas foi criado
            requestAnimationFrame(() => {
                const canvas = document.getElementById('moneyRainCanvas');
                if (canvas) {
                    console.log('Mostrando canvas...');
                    canvas.classList.add('show');
                    canvas.style.opacity = '1';
                } else {
                    console.error('Canvas não encontrado!');
                    return;
                }
                
                // Toca o vídeo do início
                video.currentTime = 0;
                
                // Prepara o áudio
                const audio = document.getElementById('moneyRainAudio');
                
                // Aguarda um pouco antes de tentar play para garantir que tudo está pronto
                setTimeout(() => {
                    // Toca o áudio junto com o vídeo
                    if (audio) {
                        audio.currentTime = 0;
                        const audioPlayPromise = audio.play();
                        
                        if (audioPlayPromise !== undefined) {
                            audioPlayPromise
                                .then(() => {
                                    console.log('Áudio iniciado com sucesso!');
                                })
                                .catch(e => {
                                    console.error('Erro ao reproduzir áudio:', e);
                                });
                        }
                    }
                    
                    const playPromise = video.play();
                    
                    if (playPromise !== undefined) {
                        playPromise
                            .then(() => {
                                console.log('Vídeo iniciado com sucesso!');
                                
                                // Esconde o vídeo e para o áudio após 16 segundos
                                setTimeout(() => {
                                    if (canvas) {
                                        console.log('Escondendo canvas...');
                                        canvas.classList.remove('show');
                                        canvas.style.opacity = '0';
                                    }
                                    // Fade out no áudio
                                    if (audio) {
                                        fadeOutAudio(audio, 500); // 500ms de fade out
                                    }
                                    setTimeout(() => {
                                        video.pause();
                                    }, 500); // Aguarda a transição de fade out
                                }, 16000);
                            })
                            .catch(e => {
                                console.error('Erro ao reproduzir vídeo:', e);
                                // Se o vídeo falhar, para o áudio também
                                if (audio) {
                                    audio.pause();
                                    audio.currentTime = 0;
                                }
                            });
                    }
                }, 100);
            });
        } else {
            // Aguarda o vídeo carregar
            console.log('Aguardando vídeo carregar...', video.readyState);
            
            // Remove listeners anteriores para evitar múltiplos
            const handler = () => {
                video.removeEventListener('loadeddata', handler);
                video.removeEventListener('canplay', handler);
                video.removeEventListener('loadedmetadata', handler);
                tryPlay();
            };
            
            video.addEventListener('loadeddata', handler, { once: true });
            video.addEventListener('canplay', handler, { once: true });
            video.addEventListener('loadedmetadata', handler, { once: true });
            
            // Força o carregamento
            if (video.readyState === 0) {
                video.load();
            }
        }
    };
    
    tryPlay();
}

// Função para fazer fade out no áudio
function fadeOutAudio(audio, duration) {
    if (!audio) return;
    
    const startVolume = audio.volume;
    const startTime = Date.now();
    
    // Garante que o volume inicial seja 1.0 se não estiver definido
    if (audio.volume === 0 || audio.volume === undefined) {
        audio.volume = 1.0;
    }
    
    const fadeOutInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1); // 0 a 1
        
        // Aplica curva de fade out suave (ease-out)
        const easeOut = 1 - Math.pow(1 - progress, 3);
        audio.volume = startVolume * (1 - easeOut);
        
        if (progress >= 1) {
            clearInterval(fadeOutInterval);
            audio.pause();
            audio.currentTime = 0;
            audio.volume = startVolume; // Restaura o volume original para próxima vez
        }
    }, 16); // ~60fps para fade suave
}

// Função para configurar chroma key (remover fundo verde)
function setupChromaKey(video) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
    canvas.style.zIndex = '9999';
    canvas.style.pointerEvents = 'none';
    canvas.style.opacity = '0';
    canvas.style.transition = 'opacity 0.5s ease-in-out';
    canvas.id = 'moneyRainCanvas';
    canvas.classList.add('money-rain-canvas');
    document.body.appendChild(canvas);
    
    // Esconde o vídeo original (mostra apenas o canvas processado)
    video.style.display = 'none';
    
    let animationFrameId = null;
    
    function processFrame() {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            // Ajusta o tamanho do canvas ao tamanho do vídeo
            if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            }
            
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;
            
            // Remove fundo verde (chroma key)
            // Detecta verde (RGB: 0, 255, 0 ou similar) e torna transparente
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                
                // Detecta verde brilhante (chroma key)
                // Ajusta os valores conforme a cor verde do seu vídeo
                const greenThreshold = 100; // Limiar mínimo de verde (reduzido)
                const greenDominance = g - Math.max(r, b); // Quanto mais verde que vermelho/azul
                
                // Detecta verde mais agressivamente
                if (g > greenThreshold && greenDominance > 30) {
                    // Calcula transparência baseada na intensidade do verde
                    const greenRatio = Math.min(1, (g - greenThreshold) / 80);
                    const alpha = Math.max(0, 1 - greenRatio * 2); // Torna mais transparente quanto mais verde
                    data[i + 3] = alpha * 255;
                }
            }
            
            ctx.putImageData(imageData, 0, 0);
        }
        
        if (!video.paused && !video.ended) {
            animationFrameId = requestAnimationFrame(processFrame);
        } else if (video.ended) {
            // Se o vídeo terminou, reinicia
            video.currentTime = 0;
            video.play();
        }
    }
    
    video.addEventListener('play', () => {
        processFrame();
    });
    
    video.addEventListener('pause', () => {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
    });
    
    // Sincroniza opacidade do canvas com a classe show
    const observer = new MutationObserver(() => {
        const canvas = document.getElementById('moneyRainCanvas');
        if (canvas) {
            canvas.style.opacity = canvas.classList.contains('show') ? '1' : '0';
        }
    });
    
    const canvasElement = document.getElementById('moneyRainCanvas');
    if (canvasElement) {
        observer.observe(canvasElement, { attributes: true, attributeFilter: ['class'] });
    }
    
    video.dataset.chromakeySetup = 'true';
}

// Função para configurar chromakey específica para o vídeo do Allan (baseada na chuva de dinheiro)
function setupAllanVideoChromaKey(video) {
    // Remove canvas anterior se existir
    const existingCanvas = document.getElementById('allanVideoCanvas');
    if (existingCanvas) {
        existingCanvas.remove();
    }
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    
    // Canvas com position fixed para aparecer acima da chuva de dinheiro
    const container = video.parentElement;
    
    canvas.id = 'allanVideoCanvas';
    canvas.className = 'cso-video-canvas';
    
    // Função para atualizar a posição do canvas baseada na imagem estática do Allan
    const updateCanvasPosition = () => {
        // Busca a imagem estática do Allan para ancorar o vídeo nela
        const csoImage = document.getElementById('csoImage');
        if (!csoImage) {
            console.warn('⚠️ Imagem estática do Allan não encontrada, usando container como fallback');
            const rect = container.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                canvas.style.position = 'fixed';
                canvas.style.top = `${rect.top}px`;
                canvas.style.left = `${rect.left}px`;
                canvas.style.width = `${rect.width}px`;
                canvas.style.height = `${rect.height}px`;
            }
            return;
        }
        
        // Obtém a posição da imagem estática (que está com position: absolute, right: -280px, bottom: 0)
        const imageRect = csoImage.getBoundingClientRect();
        
        // Usa as dimensões do vídeo se disponíveis
        if (video.videoWidth > 0 && video.videoHeight > 0) {
            const videoAspectRatio = video.videoWidth / video.videoHeight;
            const maxWidth = 370; // Largura ligeiramente reduzida do vídeo
            const calculatedHeight = maxWidth / videoAspectRatio;
            
            // Posiciona o canvas exatamente onde a imagem estática está (ancorado)
            canvas.style.position = 'fixed';
            canvas.style.top = `${imageRect.top}px`; // Mesma posição da imagem
            canvas.style.left = `${imageRect.left}px`; // Mesma posição da imagem
            canvas.style.width = `${maxWidth}px`;
            canvas.style.height = `${calculatedHeight}px`;
        } else {
            // Fallback: usa as dimensões da imagem estática
            canvas.style.position = 'fixed';
            canvas.style.top = `${imageRect.top}px`;
            canvas.style.left = `${imageRect.left}px`;
            canvas.style.width = `${imageRect.width}px`;
            canvas.style.height = `${imageRect.height}px`;
        }
    };
    
    // Atualiza posição inicial (com delay para garantir que o container está visível)
    setTimeout(() => {
        updateCanvasPosition();
    }, 100);
    
    // Atualiza posição quando a janela redimensiona, scrolla ou zoom muda
    // Como o vídeo está ancorado na imagem estática, qualquer mudança na imagem será refletida
    window.addEventListener('resize', updateCanvasPosition);
    window.addEventListener('scroll', updateCanvasPosition);
    
    // Monitora mudanças no devicePixelRatio (zoom) para atualizar posição
    let lastDevicePixelRatio = window.devicePixelRatio;
    const checkZoom = () => {
        if (window.devicePixelRatio !== lastDevicePixelRatio) {
            lastDevicePixelRatio = window.devicePixelRatio;
            console.log('🔍 Zoom mudou, atualizando posição do vídeo...');
            updateCanvasPosition();
        }
    };
    
    // Verifica zoom periodicamente durante o processamento do vídeo
    const zoomCheckInterval = setInterval(() => {
        if (video.paused || video.ended) {
            clearInterval(zoomCheckInterval);
        } else {
            checkZoom();
        }
    }, 500); // Verifica a cada 500ms
    
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '10000'; /* Acima da chuva de dinheiro (z-index 9999) */
    canvas.style.opacity = '0';
    canvas.style.transition = 'opacity 0.5s ease-in-out';
    
    // Esconde o vídeo original
    video.style.display = 'none';
    
    // Adiciona canvas ao body (como a chuva de dinheiro)
    document.body.appendChild(canvas);
    
    console.log('✅ Canvas criado para vídeo do Allan (position: fixed)');
    
    let animationFrameId = null;
    
    function processFrame() {
        // Atualiza posição do canvas a cada frame (caso o container se mova ou zoom mude)
        updateCanvasPosition();
        
        // Garante que o canvas está visível
        if (canvas.style.opacity === '0' && canvas.classList.contains('show')) {
            canvas.style.opacity = '1';
        }
        
        if (video.readyState >= video.HAVE_CURRENT_DATA && video.videoWidth > 0 && video.videoHeight > 0) {
            // Ajusta o tamanho do canvas ao tamanho do vídeo
            if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                console.log(`📐 Canvas redimensionado: ${canvas.width}x${canvas.height}`);
            }
            
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;
            
            // Remove fundo verde (chroma key) - mesma lógica da chuva de dinheiro
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                
                // Detecta verde brilhante (chroma key) - mesma lógica da chuva de dinheiro
                const greenThreshold = 100;
                const greenDominance = g - Math.max(r, b);
                
                // Detecta verde mais agressivamente
                if (g > greenThreshold && greenDominance > 30) {
                    // Calcula transparência baseada na intensidade do verde
                    const greenRatio = Math.min(1, (g - greenThreshold) / 80);
                    const alpha = Math.max(0, 1 - greenRatio * 2); // Torna mais transparente quanto mais verde
                    data[i + 3] = alpha * 255;
                }
            }
            
            ctx.putImageData(imageData, 0, 0);
        }
        
        if (!video.paused && !video.ended) {
            animationFrameId = requestAnimationFrame(processFrame);
        }
        // Removido o loop automático - o vídeo será controlado externamente
    }
    
    // Sincroniza opacidade do canvas (como a chuva de dinheiro)
    const observer = new MutationObserver(() => {
        const canvasEl = document.getElementById('allanVideoCanvas');
        if (canvasEl) {
            canvasEl.style.opacity = canvasEl.classList.contains('show') ? '1' : '0';
        }
    });
    
    const canvasElement = document.getElementById('allanVideoCanvas');
    if (canvasElement) {
        observer.observe(canvasElement, { attributes: true, attributeFilter: ['class'] });
    }
    
    video.addEventListener('play', () => {
        processFrame();
    });
    
    video.addEventListener('pause', () => {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
    });
    
    video.dataset.chromakeySetup = 'true';
    console.log('✅ Chromakey configurado para vídeo do Allan');
}

// Função para ativar vídeo do Allan (reutilizável para marcos e meta)
function activateAllanVideo() {
    const csoImage = document.getElementById('csoImage');
    const videoContainer = document.getElementById('csoVideoContainer');
    const csoVideo = document.getElementById('csoVideo');
    const silvioMusic = document.getElementById('silvioMusic');
    
    // Elementos removidos da página de Natal - retorna silenciosamente
    if (!videoContainer || !csoVideo) {
        console.log('ℹ️ Elementos do vídeo não encontrados (removidos da página de Natal)');
        return;
    }
    
    console.log('🎯 Ativando vídeo do Allan...');
    
    // Garante que a imagem estática está escondida (em todas as vezes)
    if (csoImage) {
        csoImage.style.display = 'none';
        csoImage.style.visibility = 'hidden';
        csoImage.style.opacity = '0';
        console.log('✅ Imagem estática escondida');
    }
    
    // Pausa o ciclo de fala e esconde os balões enquanto o vídeo estiver rodando
    isVideoPlaying = true;
    clearTimeout(animationTimeout);
    if (mouthAnimationInterval) clearInterval(mouthAnimationInterval);
    isSpeaking = false;
    
    const speechBubble = document.getElementById('speechBubble');
    if (speechBubble) {
        speechBubble.style.display = 'none';
        speechBubble.classList.remove('show');
        console.log('✅ Balões de mensagens escondidos durante o vídeo');
    }
    
    // Mostra o container do vídeo instantaneamente (sem transição)
    videoContainer.style.display = 'block';
    videoContainer.style.visibility = 'visible';
    videoContainer.style.opacity = '1';
    
    // Configura chromakey se ainda não foi configurado
    if (csoVideo.dataset.chromakeySetup !== 'true') {
        console.log('🔧 Configurando chromakey pela primeira vez...');
        setupAllanVideoChromaKey(csoVideo);
    }
    
    // Garante que o vídeo está carregado
    const tryPlay = () => {
        if (csoVideo.readyState >= 2) {
            requestAnimationFrame(() => {
                const canvas = document.getElementById('allanVideoCanvas');
                if (canvas) {
                    console.log('✅ Mostrando canvas do Allan...');
                    
                    const waitForVideoDimensions = () => {
                        if (csoVideo.videoWidth > 0 && csoVideo.videoHeight > 0) {
                            const videoAspectRatio = csoVideo.videoWidth / csoVideo.videoHeight;
                            const maxWidth = 370;
                            const calculatedHeight = maxWidth / videoAspectRatio;
                            
                            // Usa a imagem estática como referência (ancoragem)
                            const csoImage = document.getElementById('csoImage');
                            if (csoImage) {
                                const imageRect = csoImage.getBoundingClientRect();
                                
                                // Posiciona o canvas exatamente onde a imagem estática está (ancorado)
                                canvas.style.position = 'fixed';
                                canvas.style.top = `${imageRect.top}px`; // Mesma posição da imagem
                                canvas.style.left = `${imageRect.left}px`; // Mesma posição da imagem
                                canvas.style.width = `${maxWidth}px`;
                                canvas.style.height = `${calculatedHeight}px`;
                            } else {
                                // Fallback: usa o container
                                const container = csoVideo.parentElement;
                                const rect = container.getBoundingClientRect();
                                canvas.style.position = 'fixed';
                                canvas.style.top = `${rect.top}px`;
                                canvas.style.left = `${rect.left}px`;
                                canvas.style.width = `${maxWidth}px`;
                                canvas.style.height = `${calculatedHeight}px`;
                            }
                            canvas.style.zIndex = '10000';
                            canvas.style.opacity = '1';
                            canvas.style.display = 'block';
                            canvas.style.visibility = 'visible';
                            
                            canvas.classList.add('show');
                        } else {
                            setTimeout(waitForVideoDimensions, 50);
                        }
                    };
                    
                    waitForVideoDimensions();
                } else {
                    console.error('❌ Canvas não encontrado!');
                    return;
                }
                
                csoVideo.currentTime = 0;
                
                setTimeout(() => {
                    if (silvioMusic) {
                        silvioMusic.currentTime = 0;
                        silvioMusic.play().then(() => {
                            console.log('✅ Áudio do Silvio iniciado!');
                        }).catch(e => {
                            console.error('❌ Erro ao reproduzir áudio:', e);
                        });
                    }
                    
                    let videoLoopCount = 0;
                    const maxLoops = 2;
                    
                    const returnToStaticImage = () => {
                        console.log('🔄 Voltando para imagem estática do Allan...');
                        
                        csoVideo.pause();
                        csoVideo.currentTime = 0;
                        if (silvioMusic) {
                            silvioMusic.pause();
                            silvioMusic.currentTime = 0;
                        }
                        
                        const canvas = document.getElementById('allanVideoCanvas');
                        if (canvas) {
                            canvas.classList.remove('show');
                            canvas.style.opacity = '0';
                            canvas.style.display = 'none';
                        }
                        
                        videoContainer.style.opacity = '0';
                        videoContainer.style.display = 'none';
                        
                        // Mostra a imagem estática novamente (em todas as vezes que o vídeo terminar)
                        if (csoImage) {
                            // Remove qualquer animação CSS antes de mostrar
                            csoImage.style.animation = 'none';
                            // Mostra a imagem estática instantaneamente (sem transição)
                            csoImage.style.display = 'block';
                            csoImage.style.visibility = 'visible';
                            csoImage.style.opacity = '1';
                            // Força um reflow para garantir que a animação foi removida
                            csoImage.offsetHeight;
                            // Remove a animação novamente após o reflow
                            csoImage.style.animation = 'none';
                            console.log('✅ Imagem estática do Allan restaurada (sem animação)');
                        }
                        
                        isVideoPlaying = false;
                        
                        const speechBubble = document.getElementById('speechBubble');
                        if (speechBubble) {
                            speechBubble.style.display = 'block';
                            console.log('✅ Balões de mensagens restaurados após o vídeo');
                        }
                        
                        setTimeout(() => {
                            startSpeakingCycle();
                        }, 1000);
                    };
                    
                    const handleVideoEnd = () => {
                        videoLoopCount++;
                        console.log(`🔄 Vídeo completou loop ${videoLoopCount}/${maxLoops}`);
                        
                        if (videoLoopCount >= maxLoops) {
                            csoVideo.removeEventListener('ended', handleVideoEnd);
                            console.log('🔄 Voltando para imagem estática do Allan...');
                            returnToStaticImage();
                        } else {
                            csoVideo.currentTime = 0;
                            csoVideo.play();
                        }
                    };
                    
                    csoVideo.addEventListener('ended', handleVideoEnd);
                    
                    const playPromise = csoVideo.play();
                    
                    if (playPromise !== undefined) {
                        playPromise
                            .then(() => {
                                console.log('✅ Vídeo do Allan iniciado com sucesso!');
                                console.log(`⏱️ Vídeo rodará ${maxLoops} vezes em loop`);
                            })
                            .catch(e => {
                                console.error('❌ Erro ao reproduzir vídeo:', e);
                                if (silvioMusic) {
                                    silvioMusic.pause();
                                    silvioMusic.currentTime = 0;
                                }
                                csoVideo.removeEventListener('ended', handleVideoEnd);
                            });
                    }
                }, 100);
            });
        } else {
            console.log('⏳ Aguardando vídeo carregar...', csoVideo.readyState);
            
            const handler = () => {
                csoVideo.removeEventListener('loadeddata', handler);
                csoVideo.removeEventListener('canplay', handler);
                csoVideo.removeEventListener('loadedmetadata', handler);
                tryPlay();
            };
            
            csoVideo.addEventListener('loadeddata', handler, { once: true });
            csoVideo.addEventListener('canplay', handler, { once: true });
            csoVideo.addEventListener('loadedmetadata', handler, { once: true });
            
            if (csoVideo.readyState === 0) {
                csoVideo.load();
            }
        }
    };
    
    tryPlay();
}

// Função para verificar quando meta de 1.5M for atingida (sem animações, preparação para animação especial)
function checkMetaAtingida(currentValue, goal) {
    // Se não houver meta definida, não verifica
    if (!goal || goal <= 0) {
        return;
    }
    const metaAtingida = currentValue >= goal;
    const csoImage = document.getElementById('csoImage');
    const videoContainer = document.getElementById('csoVideoContainer');
    const csoVideo = document.getElementById('csoVideo');
    const silvioMusic = document.getElementById('silvioMusic');
    
    // Elementos removidos da página de Natal - retorna silenciosamente
    if (!csoImage && !videoContainer) {
        return;
    }
    
    if (metaAtingida) {
        // Meta de 1.5M atingida - sem animações (chuva de dinheiro e vídeo do Allan)
        // A animação especial será implementada depois
        console.log('🎉 Meta de R$ 1.500.000 atingida! (Animação especial será implementada)');
        
        // Garante que a imagem estática está visível
        if (csoImage) {
            csoImage.style.display = 'block';
            csoImage.style.visibility = 'visible';
            csoImage.style.opacity = '1';
        }
        
        // Garante que o vídeo está escondido
        if (videoContainer) {
            videoContainer.style.display = 'none';
        }
        
        // Pausa vídeo e música se estiverem tocando
        if (csoVideo) {
            csoVideo.pause();
            csoVideo.currentTime = 0;
        }
        if (silvioMusic) {
            silvioMusic.pause();
            silvioMusic.currentTime = 0;
        }
        
        // Reinicia ciclo de animação de fala
        if (!isSpeaking && !isVideoPlaying) {
            startSpeakingCycle();
        }
    } else if (!metaAtingida && csoImage && videoContainer) {
        // Meta não atingida: mostra imagem estática
        csoImage.style.display = 'block';
        videoContainer.style.display = 'none';
        
        // Pausa vídeo e música
        if (csoVideo) {
            csoVideo.pause();
            csoVideo.currentTime = 0;
        }
        if (silvioMusic) {
            silvioMusic.pause();
            silvioMusic.currentTime = 0;
        }
        
        // Reinicia ciclo de animação de fala
        if (!isSpeaking) {
            startSpeakingCycle();
        }
    }
}

async function loadRevenueData() {
    try {
        // Verifica se está no modo aleatório para usar cache
        const urlParams = new URLSearchParams(window.location.search);
        const isRandomMode = urlParams.has('aleatorio');
        const useCacheParam = isRandomMode ? '?use_cache=true' : '';
        
        const response = await fetch(`/api/revenue${useCacheParam}`);
        const data = await response.json();

        if (data.error) {
            console.error('Erro:', data.error);
            return;
        }

        // Esconde loading e mostra funil
        document.getElementById('loading').style.display = 'none';
        document.getElementById('funnelWrapper').style.display = 'block';
        const rouletteContainer = document.getElementById('rouletteContainer');
        if (rouletteContainer) {
            rouletteContainer.style.display = 'block';
        }

        // O valor adicional já é aplicado pelo backend se o modo manual estiver ativo
        const currentValue = data.total || 0;
        const goal = data.goal || 739014.83;

        // Define a meta no topo
        const mainValueEl = document.getElementById('mainValue');
        if (goal && goal > 0) {
        mainValueEl.textContent = formatCurrency(goal);
        } else {
            mainValueEl.textContent = formatCurrency(739014.83);
        }

        // Salva o valor atual no wrapper para uso no resize
        const wrapperEl = document.getElementById('funnelWrapper');
        if (wrapperEl) {
            wrapperEl.dataset.currentValue = currentValue;
        }

        // Atualiza funil com animação
        setTimeout(() => {
            updateFunnel(currentValue);
            // Verifica se a meta foi atingida após atualizar o funil
            checkMetaAtingida(currentValue, goal);
        }, 500);
        
        // Inicia timer de navegação após dados carregados (apenas no modo aleatório)
        if (isRandomMode) {
            startNavigationTimer();
        }

    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        document.getElementById('loading').innerHTML = 
            '<div style="color: #ff6b6b;">Erro ao carregar dados. Tente novamente.</div>';
        
        // Inicia timer de navegação mesmo com erro (apenas no modo aleatório)
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('aleatorio')) {
            startNavigationTimer();
        }
    }
}

// Função para animação de fala do CSO com ciclos separados por frase
const phrases = [
    { text: 'MAÔEEEEEE', syllables: 3 }, // MA O E
    { text: 'Quem quer dinheiroooo?', syllables: 5 } // QUEM QUER DI NHEI RO
];
let currentPhraseIndex = 0;
let animationTimeout = null;
let mouthAnimationInterval = null;
let isSpeaking = false;
let isVideoPlaying = false; // Flag para controlar se o vídeo está rodando

function speakPhrase(phraseIndex) {
    // Não mostra balões se o vídeo estiver rodando
    if (isVideoPlaying) {
        console.log('⏸️ Vídeo rodando, balões pausados');
        return;
    }
    
    const csoImage = document.getElementById('csoImage');
    const speechBubble = document.getElementById('speechBubble');
    const speechText = document.getElementById('speechText');
    
    // Elementos removidos da página de Natal - retorna silenciosamente
    if (!csoImage || !speechBubble || !speechText) {
        return;
    }
    
    const phrase = phrases[phraseIndex];
    const totalDuration = 3000; // 3 segundos total
    const syllableCount = phrase.syllables;
    
    // Calcula durações: primeiras sílabas rápidas, última sílaba prolongada
    // A última sílaba recebe 60% do tempo total, as outras dividem os 40% restantes
    const lastSyllableDuration = totalDuration * 0.6; // 60% para a última (1.8s)
    const remainingDuration = totalDuration * 0.4; // 40% para as outras (1.2s)
    const firstSyllablesDuration = remainingDuration / (syllableCount - 1); // Duração por sílaba das primeiras
    
    // Prepara o balão ANTES de mostrar
    speechText.textContent = phrase.text;
    speechText.style.opacity = '1';
    
    // Em mobile, o balão fica acima do CSO (não precisa posicionar ao lado)
    const isMobile = window.innerWidth <= 768;
    
    // Força um reflow para garantir que o display está aplicado
    if (!isMobile) {
        speechBubble.style.display = 'block';
        speechBubble.offsetHeight;
    } else {
        // Em mobile, garante que o balão está visível no DOM (mas invisível visualmente)
        speechBubble.style.display = 'block';
        speechBubble.style.position = 'relative';
        speechBubble.style.top = 'auto';
        speechBubble.style.left = 'auto';
        speechBubble.style.right = 'auto';
        speechBubble.style.bottom = 'auto';
        speechBubble.style.transform = 'none';
        speechBubble.classList.remove('arrow-left', 'arrow-right');
    }
    
    // EXATAMENTE AO MESMO TEMPO: mostra balão E inicia animação da boca
    requestAnimationFrame(() => {
        // Remove classes de frase anterior
        speechBubble.classList.remove('phrase-mao', 'phrase-dinheiro');
        
        // Adiciona classe específica para a frase atual
        if (phraseIndex === 0) {
            speechBubble.classList.add('phrase-mao');
        } else {
            speechBubble.classList.add('phrase-dinheiro');
        }
        
        // Mostra o balão (sem delay de animação CSS)
        speechBubble.classList.add('show');
        
        // INICIA a animação de boca NO MESMO FRAME
        isSpeaking = true;
        
        // Anima a boca baseado nas sílabas
        if (mouthAnimationInterval) clearInterval(mouthAnimationInterval);
        
        let syllableIndex = 0;
        let currentTime = 0;
        
        const animateMouth = () => {
            if (!isSpeaking) return;
            
            // Determina a duração da sílaba atual
            const isLastSyllable = syllableIndex === syllableCount - 1;
            const syllableDuration = isLastSyllable ? lastSyllableDuration : firstSyllablesDuration;
            
            // Abre a boca
            csoImage.classList.add('speaking');
            
            // Fecha a boca após metade da duração da sílaba (ou mais prolongado na última)
            const closeDelay = isLastSyllable ? syllableDuration * 0.7 : syllableDuration / 2;
            setTimeout(() => {
                if (isSpeaking) {
                    csoImage.classList.remove('speaking');
                }
            }, closeDelay);
            
            syllableIndex++;
            currentTime += syllableDuration;
            
            if (syllableIndex < syllableCount) {
                // Agenda a próxima sílaba
                setTimeout(animateMouth, syllableDuration);
            }
        };
        
        // Inicia a primeira sílaba
        animateMouth();
    });
    
    // Após 3 segundos falando, para e esconde o balão
    setTimeout(() => {
        isSpeaking = false;
        csoImage.classList.remove('speaking');
        speechBubble.classList.remove('show');
        if (mouthAnimationInterval) clearInterval(mouthAnimationInterval);
        
        // Em mobile, não remove o display para manter o espaço reservado
        const isMobile = window.innerWidth <= 768;
        if (!isMobile) {
            // Esconde o balão após a transição (apenas em desktop)
            setTimeout(() => {
                speechBubble.style.display = 'none';
            }, 200);
        }
        // Em mobile, o balão fica invisível mas ocupa espaço (via CSS opacity/visibility)
    }, totalDuration);
}

function startSpeakingCycle() {
    const csoImage = document.getElementById('csoImage');
    if (!csoImage) {
        // Elemento removido da página de Natal - retorna silenciosamente
        return;
    }
    const speechBubble = document.getElementById('speechBubble');
    const isMobile = window.innerWidth <= 768;
    
    // Limpa qualquer animação anterior
    clearTimeout(animationTimeout);
    if (mouthAnimationInterval) clearInterval(mouthAnimationInterval);
    
    // Inicia com boca fechada e balão escondido
    csoImage.classList.remove('speaking');
    speechBubble.classList.remove('show');
    
    // Em mobile, mantém display: block para reservar espaço, apenas esconde visualmente
    if (isMobile) {
        speechBubble.style.display = 'block';
    } else {
        speechBubble.style.display = 'none';
    }
    
    isSpeaking = false;
    
    // Após 4 segundos, fala a primeira frase
    animationTimeout = setTimeout(() => {
        speakPhrase(0);
        
        // Após a primeira frase terminar (3s) + pausa (5s) = 8s, fala a segunda frase
        setTimeout(() => {
            speakPhrase(1);
            
            // Após a segunda frase terminar (3s) + pausa (5s) = 8s, reinicia o ciclo
            setTimeout(() => {
                startSpeakingCycle();
            }, 8000);
        }, 8000);
    }, 4000); // Delay inicial de 4 segundos
}

// Para a animação quando a página não está visível (performance)
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        clearTimeout(animationTimeout);
        if (mouthAnimationInterval) clearInterval(mouthAnimationInterval);
    } else {
        startSpeakingCycle();
    }
});

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

// Carrega dados quando a página carrega
window.addEventListener('load', async () => {
    await loadRevenueData();
    
    // Prepara o vídeo para carregar
    const video = document.getElementById('moneyRainVideo');
    if (video) {
        // Precarrega o vídeo
        video.load();
        
        video.addEventListener('canplaythrough', () => {
            console.log('Vídeo pronto para reprodução');
        }, { once: true });
        
        video.addEventListener('error', (e) => {
            console.error('Erro ao carregar vídeo:', e);
            console.error('Vídeo error details:', video.error);
        });
    }
    
    // Prepara o áudio para carregar
    const audio = document.getElementById('moneyRainAudio');
    if (audio) {
        // Precarrega o áudio
        audio.load();
        
        audio.addEventListener('canplaythrough', () => {
            console.log('Áudio pronto para reprodução');
        }, { once: true });
        
        audio.addEventListener('error', (e) => {
            console.error('Erro ao carregar áudio:', e);
            console.error('Áudio error details:', audio.error);
        });
    }
    
    // Botão de teste para chuva de dinheiro
    const testBtn = document.getElementById('testMoneyRainBtn');
    if (testBtn) {
        testBtn.addEventListener('click', () => {
            triggerMoneyRain();
        });
    }
    
    // Atualiza a cada 5 minutos (apenas se NÃO estiver no modo aleatório)
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('aleatorio')) {
        setInterval(loadRevenueData, 300000);
    } else {
        console.log('📦 Modo aleatório: atualizações periódicas desabilitadas (usando cache centralizado)');
    }
});

// Atualiza layout quando a janela é redimensionada (para responsividade)
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        // Recarrega o funil para recalcular posições em mobile/desktop
        const wrapperEl = document.getElementById('funnelWrapper');
        if (wrapperEl && wrapperEl.style.display !== 'none') {
            // Se o funil já está carregado, apenas atualiza as posições
            const currentValue = parseFloat(wrapperEl.dataset.currentValue || 0);
            if (currentValue > 0) {
                updateFunnel(currentValue);
            }
            
            // Se o balão está visível, em mobile apenas garante que está no modo relativo
            const speechBubble = document.getElementById('speechBubble');
            const csoImage = document.getElementById('csoImage');
            if (speechBubble && csoImage && speechBubble.style.display !== 'none') {
                const isMobile = window.innerWidth <= 768;
                if (isMobile) {
                    speechBubble.style.position = 'relative';
                    speechBubble.style.top = 'auto';
                    speechBubble.style.left = 'auto';
                    speechBubble.style.right = 'auto';
                    speechBubble.style.bottom = 'auto';
                    speechBubble.style.transform = 'none';
                    speechBubble.classList.remove('arrow-left', 'arrow-right');
                }
            }
        }
    }, 250);
});

// Permite iframe
if (window.self !== window.top) {
    document.body.style.padding = '10px';
}

// Configurações do Modo Manual
document.addEventListener('DOMContentLoaded', async () => {
    const settingsBtn = document.getElementById('settingsBtn');
    const settingsMenu = document.getElementById('settingsMenu');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const manualModeToggle = document.getElementById('manualModeToggle');
    const additionalValueInput = document.getElementById('additionalValue');
    const manualModeSettings = document.getElementById('manualModeSettings');
    const renewalPipelineToggle = document.getElementById('renewalPipelineToggle');
    
    if (!settingsBtn || !settingsMenu) return; // Elementos não encontrados
    
    // Carrega valores salvos do servidor
    async function loadConfig() {
        try {
            const response = await fetch('/api/manual-revenue/config');
            const config = await response.json();
            manualModeToggle.checked = config.enabled || false;
            additionalValueInput.value = config.additionalValue || '0';
            manualModeSettings.style.display = config.enabled ? 'flex' : 'none';
            renewalPipelineToggle.checked = config.includeRenewalPipeline || false;
        } catch (error) {
            console.error('Erro ao carregar configuração:', error);
        }
    }
    
    // Salva configuração no servidor
    async function saveConfig() {
        try {
            const config = {
                enabled: manualModeToggle.checked,
                additionalValue: parseFloat(additionalValueInput.value) || 0,
                includeRenewalPipeline: renewalPipelineToggle.checked
            };
            
            const response = await fetch('/api/manual-revenue/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            
            if (response.ok) {
                console.log('Configuração salva com sucesso');
                // Recarrega dados para aplicar o valor adicional e pipeline renovação
                loadRevenueData();
            } else {
                console.error('Erro ao salvar configuração');
            }
        } catch (error) {
            console.error('Erro ao salvar configuração:', error);
        }
    }
    
    // Carrega configuração inicial
    await loadConfig();
    
    // Abre/fecha menu
    settingsBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        settingsMenu.style.display = settingsMenu.style.display === 'none' ? 'block' : 'none';
    });
    
    closeSettingsBtn.addEventListener('click', () => {
        settingsMenu.style.display = 'none';
    });
    
    // Fecha menu ao clicar fora
    document.addEventListener('click', (e) => {
        if (!settingsMenu.contains(e.target) && e.target !== settingsBtn) {
            settingsMenu.style.display = 'none';
        }
    });
    
    // Toggle modo manual
    manualModeToggle.addEventListener('change', (e) => {
        manualModeSettings.style.display = e.target.checked ? 'flex' : 'none';
        saveConfig();
    });
    
    // Toggle pipeline renovação
    renewalPipelineToggle.addEventListener('change', () => {
        saveConfig();
    });
    
    // Atualiza valor adicional (debounce para não fazer muitas requisições)
    let saveTimeout;
    additionalValueInput.addEventListener('input', (e) => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            if (manualModeToggle.checked) {
                saveConfig();
            }
        }, 1000); // Aguarda 1 segundo após parar de digitar
    });
    
    // Permite Enter no campo de valor
    additionalValueInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.target.blur();
            clearTimeout(saveTimeout);
            if (manualModeToggle.checked) {
                saveConfig();
            }
        }
    });
    
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
});

