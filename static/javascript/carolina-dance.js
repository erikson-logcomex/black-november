// Sistema de dança da Carolina - Sequência de vídeos e foto
// Usa chromakey para remover fundo verde
(function() {
    'use strict';

    let currentVideoIndex = 0;
    let isShowingPhoto = true;
    let videoTimeout = null;
    let animationFrameId = null;
    
    const videos = [
        { id: 'carolinaVideo1', src: '/static/img/natal/carol_natal.mp4' },
        { id: 'carolinaVideo2', src: '/static/img/natal/carol_natal1.mp4' },
        { id: 'carolinaVideo3', src: '/static/img/natal/carol_natal2.mp4' }
    ];
    
    const PHOTO_DURATION = 3000; // 3 segundos mostrando a foto
    const VIDEO_DURATION = 5000; // 5 segundos de vídeo (ou até terminar)
    
    const carolinaImage = document.getElementById('carolinaImage');
    const carolinaCanvas = document.getElementById('carolinaVideoCanvas');
    let ctx = null;
    let currentVideo = null;
    let processedImageDataUrl = null;

    // Função para processar chromakey na imagem (mesma lógica de destaques.js)
    function processChromaKeyImage(img) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        canvas.width = img.naturalWidth || img.width;
        canvas.height = img.naturalHeight || img.height;
        
        context.drawImage(img, 0, 0, canvas.width, canvas.height);
        
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        const width = canvas.width;
        const height = canvas.height;
        
        const isChromaKey = new Array(data.length / 4).fill(false);
        
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            
            const max = Math.max(r, g, b);
            const min = Math.min(r, g, b);
            const brightness = max;
            const saturation = max === 0 ? 0 : (max - min) / max;
            
            const greenDominance = g - Math.max(r, b);
            const greenRatio = (r + g + b) > 0 ? g / (r + g + b) : 0;
            
            const isPureGreen = g > 100 && greenDominance > 40 && saturation > 0.4 && r < 100 && b < 100;
            const isMediumGreen = g > 80 && greenDominance > 30 && saturation > 0.3 && r < 120 && b < 120 && brightness > 150;
            const isLightGreen = g > 60 && greenDominance > 25 && greenRatio > 0.4 && r < 80 && b < 80;
            
            const pixelIndex = i / 4;
            if (isPureGreen || isMediumGreen || isLightGreen) {
                isChromaKey[pixelIndex] = true;
            }
        }
        
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            const pixelIndex = i / 4;
            
            const max = Math.max(r, g, b);
            const min = Math.min(r, g, b);
            const brightness = max;
            const saturation = max === 0 ? 0 : (max - min) / max;
            const greenDominance = g - Math.max(r, b);
            
            if (isChromaKey[pixelIndex]) {
                data[i + 3] = 0;
                continue;
            }
            
            const x = (pixelIndex % width);
            const y = Math.floor(pixelIndex / width);
            
            let nearbyChromaKey = 0;
            for (let dy = -1; dy <= 1; dy++) {
                for (let dx = -1; dx <= 1; dx++) {
                    const nx = x + dx;
                    const ny = y + dy;
                    if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                        const neighborIndex = (ny * width + nx) * 4;
                        const neighborPixelIndex = neighborIndex / 4;
                        if (isChromaKey[neighborPixelIndex]) {
                            nearbyChromaKey++;
                        }
                    }
                }
            }
            
            if (nearbyChromaKey > 0 && greenDominance > 10) {
                const chromaRatio = nearbyChromaKey / 9;
                if (chromaRatio > 0.3) {
                    data[i + 3] = Math.max(0, data[i + 3] * (1 - chromaRatio * 0.9));
                } else if (chromaRatio > 0.1) {
                    data[i + 3] = Math.max(0, data[i + 3] * (1 - chromaRatio * 0.5));
                }
            }
            
            const isGreenish = g > 60 && greenDominance > 15 && saturation > 0.2 && brightness > 100 && r < 100 && b < 100;
            
            if (isGreenish && nearbyChromaKey > 2) {
                data[i + 3] = Math.max(0, data[i + 3] * 0.2);
            }
        }
        
        context.putImageData(imageData, 0, 0);
        return canvas.toDataURL();
    }

    // Função para processar chromakey no vídeo (frame a frame)
    function processChromaKeyFrame(video, canvas, context) {
        if (video.readyState < video.HAVE_CURRENT_DATA || video.videoWidth === 0 || video.videoHeight === 0) {
            return;
        }

        if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        }

        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;

        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];

            const max = Math.max(r, g, b);
            const min = Math.min(r, g, b);
            const saturation = max === 0 ? 0 : (max - min) / max;

            const greenDominance = g - Math.max(r, b);
            const greenRatio = (r + g + b) > 0 ? g / (r + g + b) : 0;

            const isPureGreen = g > 100 && greenDominance > 40 && saturation > 0.4 && r < 100 && b < 100;
            const isMediumGreen = g > 80 && greenDominance > 30 && saturation > 0.3 && r < 120 && b < 120;
            const isLightGreen = g > 60 && greenDominance > 25 && greenRatio > 0.4 && r < 80 && b < 80;

            if (isPureGreen || isMediumGreen || isLightGreen) {
                data[i + 3] = 0;
            }
        }

        context.putImageData(imageData, 0, 0);
    }

    // Loop de animação para processar frames do vídeo (mesmo padrão de destaques.js)
    function processFrame() {
        if (currentVideo && carolinaCanvas && ctx) {
            if (currentVideo.readyState >= currentVideo.HAVE_CURRENT_DATA && 
                currentVideo.videoWidth > 0 && currentVideo.videoHeight > 0) {
                
                // Ajusta o tamanho do canvas ao tamanho do vídeo
                if (carolinaCanvas.width !== currentVideo.videoWidth || 
                    carolinaCanvas.height !== currentVideo.videoHeight) {
                    carolinaCanvas.width = currentVideo.videoWidth;
                    carolinaCanvas.height = currentVideo.videoHeight;
                }
                
                processChromaKeyFrame(currentVideo, carolinaCanvas, ctx);
            }
        }
        
        // Continua processando mesmo quando pausado (para manter o último frame visível)
        // Mas só continua o loop se o vídeo não terminou completamente
        if (currentVideo && !currentVideo.ended) {
            animationFrameId = requestAnimationFrame(processFrame);
        }
    }

    // Mostra a foto
    function showPhoto() {
        isShowingPhoto = true;
        
        // Para o vídeo atual
        if (currentVideo) {
            currentVideo.pause();
            currentVideo.currentTime = 0;
            currentVideo.style.display = 'none';
        }
        
        // Cancela animação do canvas
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
        
        // Esconde canvas IMEDIATAMENTE
        if (carolinaCanvas) {
            carolinaCanvas.style.display = 'none';
        }
        
        // Mostra a foto IMEDIATAMENTE (sem transição)
        if (carolinaImage) {
            carolinaImage.style.display = 'block';
        }
        
        // Agenda próximo vídeo
        clearTimeout(videoTimeout);
        videoTimeout = setTimeout(() => {
            showNextVideo();
        }, PHOTO_DURATION);
    }

    // Mostra o próximo vídeo (seguindo padrão de destaques.js)
    function showNextVideo() {
        isShowingPhoto = false;
        
        // Esconde a foto IMEDIATAMENTE (sem transição)
        if (carolinaImage) {
            carolinaImage.style.display = 'none';
        }
        
        // Seleciona o vídeo atual
        const videoConfig = videos[currentVideoIndex];
        currentVideo = document.getElementById(videoConfig.id);
        
        if (!currentVideo || !carolinaCanvas) {
            console.warn('⚠️ Vídeo ou canvas da Carolina não encontrado');
            return;
        }
        
        // Prepara o canvas
        if (!ctx) {
            ctx = carolinaCanvas.getContext('2d', { willReadFrequently: true });
        }
        
        // Não ajusta tamanho dinamicamente - usa tamanhos fixos do CSS
        // O CSS já define tamanhos fixos que não mudam com zoom ou fullscreen
        
        // Esconde o vídeo original (mesmo padrão de destaques.js)
        currentVideo.style.display = 'none';
        
        // Mostra canvas IMEDIATAMENTE
        carolinaCanvas.style.display = 'block';
        
        // Configura o vídeo
        currentVideo.muted = true;
        currentVideo.loop = false;
        currentVideo.currentTime = 0; // Reseta para o início
        
        // Função para quando o vídeo terminar
        const onVideoEnd = () => {
            // Para o vídeo
            if (currentVideo) {
                currentVideo.pause();
                currentVideo.currentTime = 0;
            }
            
            // Cancela animação
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                animationFrameId = null;
            }
            
            // Avança para o próximo vídeo
            currentVideoIndex = (currentVideoIndex + 1) % videos.length;
            
            // Volta para a foto IMEDIATAMENTE
            showPhoto();
        };
        
        // Função para quando o vídeo pausar
        const onPause = () => {
            // Não cancela o animationFrame quando pausa, para manter o último frame visível
            // O processFrame continuará rodando e desenhando o frame atual
            // Só cancela se o vídeo realmente terminou e não vai reiniciar
        };
        
        // Função para quando o vídeo estiver carregado
        const onLoadedData = () => {
            processFrame();
        };
        
        // Remove listeners anteriores (se existirem)
        currentVideo.removeEventListener('play', processFrame);
        currentVideo.removeEventListener('pause', onPause);
        currentVideo.removeEventListener('ended', onVideoEnd);
        currentVideo.removeEventListener('loadeddata', onLoadedData);
        
        // Quando o vídeo começar a reproduzir, inicia o processamento (mesmo padrão de destaques.js)
        currentVideo.addEventListener('play', processFrame);
        
        // Quando o vídeo pausar, cancela a animação
        currentVideo.addEventListener('pause', onPause);
        
        // Quando o vídeo terminar, volta para a foto
        currentVideo.addEventListener('ended', onVideoEnd, { once: true });
        
        // Inicia processamento se o vídeo já está pronto (mesmo padrão de destaques.js)
        if (currentVideo.readyState >= currentVideo.HAVE_CURRENT_DATA) {
            processFrame();
        } else {
            currentVideo.addEventListener('loadeddata', onLoadedData, { once: true });
        }
        
        // Reproduz o vídeo (com tratamento de erro similar ao destaques.js)
        const playVideo = () => {
            // Verifica se a página está visível antes de tentar tocar
            if (document.hidden || document.visibilityState === 'hidden') {
                console.log('⏸️ Página não está visível, aguardando para tocar vídeo da Carolina...');
                // Aguarda a página ficar visível
                const handleVisibilityChange = () => {
                    if (!document.hidden) {
                        document.removeEventListener('visibilitychange', handleVisibilityChange);
                        setTimeout(() => playVideo(), 100);
                    }
                };
                document.addEventListener('visibilitychange', handleVisibilityChange);
                return;
            }
            
            const playPromise = currentVideo.play();
            
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    console.log('✅ Vídeo da Carolina iniciado');
                }).catch(e => {
                    // Ignora erro de "background media paused" - é normal quando a página não está visível
                    if (e.name === 'AbortError' && (e.message.includes('background media') || e.message.includes('interrupted'))) {
                        console.log('⏸️ Vídeo pausado pelo navegador (economia de energia), será retomado quando página ficar visível');
                        // Aguarda a página ficar visível para tentar novamente
                        const handleVisibilityChange = () => {
                            if (!document.hidden) {
                                document.removeEventListener('visibilitychange', handleVisibilityChange);
                                setTimeout(() => playVideo(), 100);
                            }
                        };
                        document.addEventListener('visibilitychange', handleVisibilityChange);
                    } else {
                        console.error('❌ Erro ao tocar vídeo da Carolina:', e);
                    }
                });
            }
        };
        
        playVideo();
        
        // Timeout de segurança caso o vídeo não dispare o evento 'ended'
        clearTimeout(videoTimeout);
        videoTimeout = setTimeout(() => {
            if (!isShowingPhoto && currentVideo && (currentVideo.ended || currentVideo.paused)) {
                onVideoEnd();
            }
        }, VIDEO_DURATION + 1000); // Dá um pouco mais de tempo
    }

    // Inicializa o sistema
    function initCarolinaDance() {
        if (!carolinaImage || !carolinaCanvas) {
            console.warn('⚠️ Elementos da Carolina não encontrados');
            return;
        }
        
        console.log('💃 Inicializando dança da Carolina...');
        
        // Processa a imagem primeiro
        if (carolinaImage.complete && carolinaImage.naturalWidth > 0) {
            processImage();
        } else {
            carolinaImage.addEventListener('load', processImage);
        }
        
        function processImage() {
            try {
                console.log('💃 Processando imagem da Carolina...');
                processedImageDataUrl = processChromaKeyImage(carolinaImage);
                carolinaImage.src = processedImageDataUrl;
                carolinaImage.style.filter = 'none';
                console.log('✅ Imagem da Carolina processada!');
                
                // Inicia a sequência
                showPhoto();
            } catch (error) {
                console.error('❌ Erro ao processar imagem da Carolina:', error);
            }
        }
        
        // Precarrega os vídeos
        videos.forEach(videoConfig => {
            const video = document.getElementById(videoConfig.id);
            if (video) {
                video.preload = 'auto';
                video.muted = true;
            }
        });
    }

    // Inicia quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCarolinaDance);
    } else {
        setTimeout(initCarolinaDance, 500); // Aguarda um pouco para garantir que tudo está carregado
    }
})();

