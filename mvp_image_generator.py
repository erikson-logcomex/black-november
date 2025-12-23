"""
Módulo para gerar imagens dos destaques do dia do Hall da Fama usando Playwright
Usa o CSS e estrutura HTML EXATOS do Hall da Fama
"""
from playwright.sync_api import sync_playwright
import base64
import os
import unicodedata
import re


def normalize_name(name):
    """Normaliza nome para buscar foto do time"""
    if not name:
        return ''
    
    # Remove acentos
    name_normalized = unicodedata.normalize('NFD', name)
    name_normalized = ''.join(c for c in name_normalized if unicodedata.category(c) != 'Mn')
    
    # Converte para lowercase e substitui espaços/hífens
    name_normalized = name_normalized.lower().replace(' ', '_').replace('-', '_')
    
    # Remove caracteres especiais (mantém apenas letras, números e underscore)
    name_normalized = re.sub(r'[^a-z0-9_]', '', name_normalized)
    
    return name_normalized


def get_photo_base64(name):
    """Obtém foto em base64 do membro do time"""
    if not name:
        return None
    
    normalized = normalize_name(name)
    photo_path = os.path.join(os.path.dirname(__file__), 'static', 'img', 'team', f'{normalized}.png')
    
    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as f:
            photo_bytes = f.read()
            photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
            return f'data:image/png;base64,{photo_base64}'
    
    return None


def get_crown_base64():
    """Obtém coroa em base64"""
    crown_path = os.path.join(os.path.dirname(__file__), 'static', 'img', 'coroa.png')
    
    if os.path.exists(crown_path):
        with open(crown_path, 'rb') as f:
            crown_bytes = f.read()
            crown_base64 = base64.b64encode(crown_bytes).decode('utf-8')
            return f'data:image/png;base64,{crown_base64}'
    
    return None


def generate_mvp_card_html(mvp_data, profile_type):
    """
    Gera HTML do card do destaque do dia
    
    Args:
        mvp_data: Dict com dados do destaque (userName, dealCount/scheduledCount, revenue, badges)
        profile_type: 'EVs', 'SDRs-New', 'SDRs-Expansao', 'LDRs'
    
    Returns:
        str: HTML do card do destaque
    """
    
    # Lê o CSS real do arquivo
    css_path = os.path.join(os.path.dirname(__file__), 'static', 'css', 'hall_da_fama.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        hall_css = f.read()
    
    # Dados do MVP
    mvp_name = mvp_data.get('userName', 'Desconhecido')
    mvp_photo_b64 = get_photo_base64(mvp_name)
    crown_b64 = get_crown_base64()
    badges = mvp_data.get('badges', [])
    
    # Define estatísticas baseado no tipo de perfil
    if profile_type == 'EVs':
        title = '🏆 HALL DA FAMA - EVs'
        subtitle = 'Executivo de Vendas - Destaque do Dia'
        stat1_value = mvp_data.get('dealCount', 0)
        stat1_label = 'Deals'
        stat2_value = f"R$ {mvp_data.get('revenue', 0):,.0f}"
        stat2_label = 'Faturamento'
    elif profile_type == 'LDRs':
        title = '🎓 HALL DA FAMA - LDRs'
        subtitle = 'MQL → Ganho - Destaque do Dia'
        stat1_value = mvp_data.get('wonDealsCount', 0)
        stat1_label = 'Deals Ganhos'
        stat2_value = f"R$ {mvp_data.get('revenue', 0):,.0f}"
        stat2_label = 'Faturamento'
    else:  # SDRs
        if 'New' in profile_type:
            title = '📞 HALL DA FAMA - SDRs NEW'
            subtitle = 'Sales Development Representative - Pipeline NEW'
        else:
            title = '📞 HALL DA FAMA - SDRs Expansão'
            subtitle = 'Sales Development Representative - Pipeline Expansão'
        stat1_value = mvp_data.get('scheduledCount', 0)
        stat1_label = 'Agendamentos'
        stat2_value = ''
        stat2_label = ''
    
    # Foto ou placeholder
    if mvp_photo_b64:
        photo_html = f'<img class="mvp-photo" src="{mvp_photo_b64}" alt="{mvp_name}">'
    else:
        initial = mvp_name[0].upper() if mvp_name else '?'
        photo_html = f'''
        <div class="mvp-photo" style="display:flex; background:#FFD700; justify-content:center; align-items:center; font-size:8rem; color:#000; font-weight:bold; width:100%; height:100%; border-radius:50%;">
            {initial}
        </div>
        '''
    
    # Coroa
    crown_html = ''
    if crown_b64:
        crown_html = f'<img src="{crown_b64}" alt="Coroa" class="mvp-crown">'
    
    # Badges empilhados (apenas emojis ou imagens)
    badges_html = ''
    for badge in badges:
        badge_code = badge.get('code', '')
        badge_name = badge.get('name', '')
        emoji = badge_name.split(' ')[0] if badge_name else '🏆'
        
        # Tenta usar imagem do badge
        badge_image_path = os.path.join(os.path.dirname(__file__), 'static', 'img', 'badges', f'{badge_code}.png')
        
        if os.path.exists(badge_image_path):
            # Converte imagem para base64
            with open(badge_image_path, 'rb') as f:
                badge_bytes = f.read()
                badge_base64 = base64.b64encode(badge_bytes).decode('utf-8')
                badges_html += f'<img class="mvp-badge-emoji mvp-badge-image" src="data:image/png;base64,{badge_base64}" alt="{badge_name}" title="{badge_name}">'
        else:
            # Usa emoji como fallback
            badges_html += f'<span class="mvp-badge-emoji" title="{badge_name}">{emoji}</span>'
    
    # Estatísticas
    stats_html = f'<div class="mvp-stat"><span class="mvp-stat-value">{stat1_value}</span><span class="mvp-stat-label">{stat1_label}</span></div>'
    if stat2_label:
        stats_html += f'<div class="mvp-stat"><span class="mvp-stat-value">{stat2_value}</span><span class="mvp-stat-label">{stat2_label}</span></div>'
    
    # HTML completo - formato QUADRADO 600x600px
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=600, initial-scale=1.0">
        <title>Destaque do Dia</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #000000;
                color: #ffffff;
                width: 600px;
                height: 600px;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 0;
                overflow: hidden;
            }}
            
            /* CSS do Hall da Fama com ajustes para screenshot */
            .mvp-card {{
                background: linear-gradient(135deg, rgba(123, 47, 221, 0.2) 0%, rgba(254, 143, 28, 0.2) 100%);
                border: 3px solid rgba(254, 143, 28, 0.5);
                border-radius: 25px;
                padding: 25px 20px;
                text-align: center;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 0 0 40px rgba(254, 143, 28, 0.6);
                position: relative;
                overflow: visible;
                width: 600px;
                height: 600px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }}
            
            .mvp-badge {{
                position: absolute;
                top: 15px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, #FFD700, #FFA500);
                color: #000;
                padding: 8px 25px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 0.85rem;
                letter-spacing: 2px;
                box-shadow: 0 4px 15px rgba(255, 215, 0, 0.5);
                z-index: 100;
            }}
            
            .mvp-photo-wrapper {{
                position: relative;
                width: 250px;
                height: 250px;
                margin: 60px auto 15px;
                border-radius: 50%;
                background: linear-gradient(135deg, #8B6914, #DAA520, #FFD700, #FFA500, #8B6914);
                padding: 5px;
                box-shadow: 
                    0 0 30px rgba(218, 165, 32, 0.8),
                    0 0 50px rgba(255, 215, 0, 0.5);
            }}
            
            .mvp-photo {{
                width: 100%;
                height: 100%;
                border-radius: 50%;
                object-fit: cover;
                border: none;
                display: block;
            }}
            
            .mvp-crown {{
                position: absolute;
                top: -65px;
                left: 50%;
                transform: translateX(-50%);
                width: 100px;
                height: auto;
                filter: drop-shadow(0 5px 15px rgba(255, 215, 0, 0.8));
                z-index: 10;
            }}
            
            .mvp-name {{
                font-size: 1.8rem;
                font-weight: bold;
                color: #FFD700;
                margin: 10px 0 5px;
                text-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
            }}
            
            .mvp-stats {{
                display: flex;
                justify-content: center;
                gap: 25px;
                margin: 5px 0 10px;
            }}
            
            .mvp-stat {{
                text-align: center;
            }}
            
            .mvp-stat-value {{
                display: block;
                font-size: 2.2rem;
                font-weight: bold;
                color: #FE8F1C;
                text-shadow: 0 0 15px rgba(254, 143, 28, 0.5);
            }}
            
            .mvp-stat-label {{
                display: block;
                font-size: 0.85rem;
                color: rgba(255, 255, 255, 0.7);
                text-transform: uppercase;
                margin-top: 3px;
            }}
            
            .mvp-badges-emoji-stack {{
                position: absolute;
                left: 15px;
                top: 50%;
                transform: translateY(-50%);
                display: flex;
                flex-direction: column;
                gap: 8px;
                z-index: 50;
            }}
            
            .mvp-badge-emoji {{
                font-size: 2.2rem;
                filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.5));
            }}
            
            .mvp-badge-image {{
                width: 60px;
                height: 60px;
                object-fit: contain;
                filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.6));
            }}
        </style>
    </head>
    <body>
        <div class="mvp-card">
            <div class="mvp-badge">DESTAQUE DO DIA</div>
            <div class="mvp-photo-wrapper">
                {crown_html}
                {photo_html}
            </div>
            <h2 class="mvp-name">{mvp_name}</h2>
            <div class="mvp-stats">
                {stats_html}
            </div>
            <div class="mvp-badges-emoji-stack">
                {badges_html}
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template


def generate_mvp_image(mvp_data, profile_type):
    """
    Gera uma imagem PNG do card MVP usando Playwright
    
    Args:
        mvp_data: Dict com dados do MVP
        profile_type: 'EVs', 'SDRs-New', 'SDRs-Expansao', 'LDRs'
    
    Returns:
        bytes: Imagem PNG em bytes (600x600px quadrado)
    """
    
    html_content = generate_mvp_card_html(mvp_data, profile_type)
    
    try:
        with sync_playwright() as p:
            # Inicia navegador headless
            browser = p.chromium.launch(headless=True)
            
            # Cria página QUADRADA 600x600px
            page = browser.new_page(viewport={'width': 600, 'height': 600})
            
            # Define o conteúdo HTML
            page.set_content(html_content, wait_until='networkidle')
            
            # Aguarda renderização completa (5 segundos para garantir que imagens carreguem)
            page.wait_for_timeout(5000)
            
            # Tira screenshot da página inteira (já está 600x600)
            screenshot = page.screenshot(type='png', full_page=False)
            
            # Fecha navegador
            browser.close()
            
            return screenshot
            
    except Exception as e:
        print(f"Erro ao gerar imagem do MVP: {e}")
        raise


def generate_mvp_image_base64(mvp_data, profile_type):
    """
    Gera uma imagem PNG do MVP em base64
    
    Args:
        mvp_data: Dict com dados do MVP
        profile_type: 'EVs', 'SDRs-New', 'SDRs-Expansao', 'LDRs'
    
    Returns:
        str: Imagem PNG em base64
    """
    image_bytes = generate_mvp_image(mvp_data, profile_type)
    return base64.b64encode(image_bytes).decode('utf-8')


def generate_all_mvps_images(evs_data, sdrs_new_data, sdrs_expansao_data, ldrs_data):
    """
    Gera imagens de todos os MVPs
    
    Args:
        evs_data: Dados dos EVs (com ranking)
        sdrs_new_data: Dados dos SDRs NEW
        sdrs_expansao_data: Dados dos SDRs Expansão
        ldrs_data: Dados dos LDRs
    
    Returns:
        dict: Dicionário com as imagens em bytes
    """
    images = {}
    
    try:
        # MVP EVs
        if evs_data and evs_data.get('data') and len(evs_data['data']) > 0:
            mvp_ev = evs_data['data'][0]
            images['EVs'] = generate_mvp_image(mvp_ev, 'EVs')
            print("✅ Imagem do MVP EV gerada")
        
        # MVP SDRs NEW
        if sdrs_new_data and sdrs_new_data.get('data') and len(sdrs_new_data['data']) > 0:
            mvp_sdr_new = sdrs_new_data['data'][0]
            images['SDRs-New'] = generate_mvp_image(mvp_sdr_new, 'SDRs-New')
            print("✅ Imagem do MVP SDR NEW gerada")
        
        # MVP SDRs Expansão
        if sdrs_expansao_data and sdrs_expansao_data.get('data') and len(sdrs_expansao_data['data']) > 0:
            mvp_sdr_expansao = sdrs_expansao_data['data'][0]
            images['SDRs-Expansao'] = generate_mvp_image(mvp_sdr_expansao, 'SDRs-Expansao')
            print("✅ Imagem do MVP SDR Expansão gerada")
        
        # MVP LDRs
        if ldrs_data and ldrs_data.get('data') and len(ldrs_data['data']) > 0:
            mvp_ldr = ldrs_data['data'][0]
            images['LDRs'] = generate_mvp_image(mvp_ldr, 'LDRs')
            print("✅ Imagem do MVP LDR gerada")
        
        return images
        
    except Exception as e:
        print(f"❌ Erro ao gerar imagens dos MVPs: {e}")
        raise
