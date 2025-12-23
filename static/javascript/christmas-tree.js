// Processa a árvore de Natal para remover fundo verde (chromakey)
// Usa EXATAMENTE a mesma função da página de destaques
(function() {
    'use strict';

    // Função IDÊNTICA à de destaques.js
    function processChromaKeyImage(img) {
        // Cria canvas para processar a imagem e remover fundo chromakey
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Define tamanho do canvas igual à imagem
        canvas.width = img.naturalWidth || img.width;
        canvas.height = img.naturalHeight || img.height;
        
        // Desenha a imagem no canvas
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        
        // Obtém dados da imagem
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        const width = canvas.width;
        const height = canvas.height;
        
        // Primeira passagem: identifica pixels claramente chromakey VERDE
        // Focamos APENAS em verde, não em azul (para preservar azuis e roxos da imagem)
        const isChromaKey = new Array(data.length / 4).fill(false);
        
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            
            const max = Math.max(r, g, b);
            const min = Math.min(r, g, b);
            const brightness = max;
            const saturation = max === 0 ? 0 : (max - min) / max;
            
            // Foco APENAS em verde chromakey
            const greenDominance = g - Math.max(r, b);
            const greenRatio = (r + g + b) > 0 ? g / (r + g + b) : 0;
            
            // Detecta chromakey VERDE - apenas verde muito saturado e brilhante
            // Verde chromakey típico: g muito alto, r e b baixos
            const isPureGreen = g > 100 && greenDominance > 40 && saturation > 0.4 && r < 100 && b < 100;
            const isMediumGreen = g > 80 && greenDominance > 30 && saturation > 0.3 && r < 120 && b < 120 && brightness > 150;
            const isLightGreen = g > 60 && greenDominance > 25 && greenRatio > 0.4 && r < 80 && b < 80;
            
            const pixelIndex = i / 4;
            if (isPureGreen || isMediumGreen || isLightGreen) {
                isChromaKey[pixelIndex] = true;
            }
        }
        
        // Segunda passagem: remove chromakey VERDE e processa halos
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
            
            // Se é chromakey verde puro, remove completamente
            if (isChromaKey[pixelIndex]) {
                data[i + 3] = 0;
                continue;
            }
            
            // Verifica se está próximo de chromakey verde (halos)
            const x = (pixelIndex % width);
            const y = Math.floor(pixelIndex / width);
            
            // Conta pixels chromakey verde ao redor (3x3)
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
            
            // Se está rodeado de chromakey verde ou próximo, reduz opacidade
            // Mas APENAS se o pixel também for verde (não azul/roxo)
            if (nearbyChromaKey > 0 && greenDominance > 10) {
                // Quanto mais chromakey verde ao redor, mais transparente
                const chromaRatio = nearbyChromaKey / 9;
                if (chromaRatio > 0.3) {
                    // Área muito próxima ao chromakey verde - remove quase tudo
                    data[i + 3] = Math.max(0, data[i + 3] * (1 - chromaRatio * 0.9));
                } else if (chromaRatio > 0.1) {
                    // Halo verde - reduz opacidade
                    data[i + 3] = Math.max(0, data[i + 3] * (1 - chromaRatio * 0.5));
                }
            }
            
            // Remove pixels que são claramente verde chromakey mesmo que não detectados antes
            // Mas preserva azuis e roxos (b alto com r alto = roxo, b alto com r baixo = azul)
            const isGreenish = g > 60 && greenDominance > 15 && saturation > 0.2 && brightness > 100 && r < 100 && b < 100;
            
            if (isGreenish && nearbyChromaKey > 2) {
                // Se é verde e está próximo de chromakey verde, provavelmente é resíduo
                data[i + 3] = Math.max(0, data[i + 3] * 0.2);
            }
        }
        
        // Aplica os dados processados de volta ao canvas
        ctx.putImageData(imageData, 0, 0);
        
        // Retorna a URL do canvas processado
        return canvas.toDataURL();
    }

    // Função removida - não ajusta tamanho dinamicamente
    // O CSS já define tamanhos fixos que não mudam com zoom ou fullscreen

    function initChristmasTree() {
        const treeImg = document.getElementById('christmasTree');
        
        if (!treeImg) {
            console.warn('⚠️ Árvore de Natal não encontrada');
            return;
        }
        
        console.log('🎄 Árvore de Natal encontrada');
        
        // Função para processar quando a imagem carregar
        function processTree() {
            // Verifica se a imagem tem dimensões válidas
            if ((treeImg.naturalWidth === 0 && treeImg.width === 0) || 
                (treeImg.naturalHeight === 0 && treeImg.height === 0)) {
                console.warn('⚠️ Imagem ainda não carregou completamente, tentando novamente...');
                setTimeout(processTree, 100);
                return;
            }
            
            try {
                console.log('🎄 Processando árvore de Natal para remover fundo verde...');
                const processedDataUrl = processChromaKeyImage(treeImg);
                treeImg.src = processedDataUrl;
                treeImg.style.filter = 'none'; // Remove o filtro SVG já que processamos via canvas
                
                // Não ajusta tamanho dinamicamente - usa tamanhos fixos do CSS
                
                console.log('✅ Árvore de Natal processada com sucesso!');
            } catch (error) {
                console.error('❌ Erro ao processar árvore de Natal:', error);
            }
        }
        
        // Verifica se a imagem já está carregada
        if (treeImg.complete && treeImg.naturalWidth > 0) {
            processTree();
        } else {
            treeImg.addEventListener('load', processTree);
            treeImg.addEventListener('error', () => {
                console.error('❌ Erro ao carregar imagem da árvore de Natal');
            });
        }
        
        // Não ajusta tamanho quando redimensiona - usa tamanhos fixos do CSS
    }

    // Inicia quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChristmasTree);
    } else {
        // Se o DOM já está pronto, aguarda um pouco para garantir que a imagem está no DOM
        setTimeout(initChristmasTree, 100);
    }
})();
