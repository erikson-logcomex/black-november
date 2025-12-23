/**
 * JavaScript para vídeo do Bruno Grinch com chromakey
 * Similar ao vídeo da Patrícia na página de destaques
 */

function setupBrunoGrinchVideo() {
    const video = document.getElementById('brunoGrinchVideo');
    const canvas = document.getElementById('brunoGrinchVideoCanvas');
    
    if (!video || !canvas) {
        console.warn('⚠️ Elementos do vídeo do Bruno Grinch não encontrados');
        return;
    }
    
    // Verifica se o vídeo existe
    video.addEventListener('loadeddata', () => {
        console.log('✅ Vídeo do Bruno Grinch encontrado, configurando chromakey...');
        
        // Configura chromakey
        const ctx = canvas.getContext('2d', { willReadFrequently: true });
        
        // Posiciona o canvas no canto inferior direito (valores fixos para evitar desalinhamento com zoom)
        canvas.style.position = 'fixed';
        canvas.style.bottom = '0px'; // Movido mais para baixo (era 20px)
        canvas.style.right = '30px';
        canvas.style.maxWidth = '500px';
        canvas.style.height = 'auto';
        canvas.style.zIndex = '101';
        canvas.style.filter = 'drop-shadow(0 4px 12px rgba(0, 0, 0, 0.6))';
        
        // Esconde o vídeo original
        video.style.display = 'none';
        
        // Mostra o canvas
        canvas.style.display = 'block';
        
        let animationFrameId = null;
        
        function processFrame() {
            if (video.readyState >= video.HAVE_CURRENT_DATA && video.videoWidth > 0 && video.videoHeight > 0) {
                // Ajusta o tamanho do canvas ao tamanho do vídeo
                if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                }
                
                // Desenha o frame atual do vídeo (mesmo se estiver pausado, mostra o último frame)
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                
                // Remove fundo azul (chroma key) - cor #1a97f1 (RGB: 26, 151, 241)
                const targetR = 26;
                const targetG = 151;
                const targetB = 241;
                const tolerance = 40; // Tolerância para variações de cor e iluminação
                
                for (let i = 0; i < data.length; i += 4) {
                    const r = data[i];
                    const g = data[i + 1];
                    const b = data[i + 2];
                    
                    // Calcula a distância da cor atual até a cor alvo
                    const distance = Math.sqrt(
                        Math.pow(r - targetR, 2) +
                        Math.pow(g - targetG, 2) +
                        Math.pow(b - targetB, 2)
                    );
                    
                    // Detecta se a cor está próxima o suficiente da cor alvo
                    if (distance <= tolerance) {
                        data[i + 3] = 0; // Torna transparente
                    }
                }
                
                ctx.putImageData(imageData, 0, 0);
            }
            
            // Continua processando mesmo quando pausado (para manter o último frame visível)
            // Mas só continua o loop se o vídeo não terminou completamente
            if (!video.ended) {
                animationFrameId = requestAnimationFrame(processFrame);
            }
        }
        
        video.addEventListener('play', () => {
            processFrame();
        });
        
        video.addEventListener('pause', () => {
            // Não cancela o animationFrame quando pausa, para manter o último frame visível
            // O processFrame continuará rodando e desenhando o frame atual
            // Só cancela se o vídeo realmente terminou e não vai reiniciar
        });
        
        // Inicia processamento se o vídeo já está pronto
        if (video.readyState >= video.HAVE_CURRENT_DATA) {
            processFrame();
        } else {
            video.addEventListener('loadeddata', () => {
                processFrame();
            }, { once: true });
        }
        
        // Configura delay entre repetições
        const DELAY_BETWEEN_LOOPS = 8000; // 8 segundos de delay
        let delayTimeout = null;
        
        const playVideo = () => {
            // Verifica se a página está visível antes de tentar tocar
            if (document.hidden || document.visibilityState === 'hidden') {
                console.log('⏸️ Página não está visível, aguardando para tocar vídeo do Bruno Grinch...');
                // Aguarda a página ficar visível
                const handleVisibilityChange = () => {
                    if (!document.hidden) {
                        document.removeEventListener('visibilitychange', handleVisibilityChange);
                        setTimeout(() => playVideo(), 100); // Pequeno delay para garantir
                    }
                };
                document.addEventListener('visibilitychange', handleVisibilityChange);
                return;
            }
            
            const playPromise = video.play();
            
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    console.log('✅ Vídeo do Bruno Grinch iniciado');
                    // Mostra o canvas quando o vídeo começa
                    canvas.style.opacity = '1';
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
                        console.error('❌ Erro ao tocar vídeo do Bruno Grinch:', e);
                    }
                });
            }
        };
        
        // Quando o vídeo terminar, pausa e espera antes de reiniciar
        video.addEventListener('ended', () => {
            console.log('⏸️ Vídeo do Bruno Grinch finalizado, aguardando delay...');
            
            // Pausa o vídeo (mas mantém o canvas visível)
            video.pause();
            
            // Limpa timeout anterior se existir
            if (delayTimeout) {
                clearTimeout(delayTimeout);
            }
            
            // Aguarda o delay antes de reiniciar
            delayTimeout = setTimeout(() => {
                console.log('▶️ Reiniciando vídeo do Bruno Grinch após delay...');
                
                // Reinicia o vídeo do início (canvas já está visível)
                video.currentTime = 0;
                playVideo();
            }, DELAY_BETWEEN_LOOPS);
        }, { once: false }); // Permite múltiplas execuções
        
        // Toca o vídeo inicialmente (apenas se a página estiver visível)
        if (!document.hidden) {
            playVideo();
        } else {
            // Se a página não estiver visível, aguarda ficar visível
            const handleVisibilityChange = () => {
                if (!document.hidden) {
                    document.removeEventListener('visibilitychange', handleVisibilityChange);
                    playVideo();
                }
            };
            document.addEventListener('visibilitychange', handleVisibilityChange);
        }
    });
    
    video.addEventListener('error', () => {
        console.log('📷 Vídeo do Bruno Grinch não encontrado');
        canvas.style.display = 'none';
    });
    
    // Carrega o vídeo
    video.load();
}

// Inicializa quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setupBrunoGrinchVideo();
    });
} else {
    setupBrunoGrinchVideo();
}

