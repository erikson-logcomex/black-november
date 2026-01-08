"""
Módulo para gerar imagens de celebração de deals usando Playwright
Usa o CSS e estrutura HTML EXATOS do painel de celebração
"""
from playwright.sync_api import sync_playwright
import base64
import os
import unicodedata
import re


def normalize_name(name):
    """Normaliza nome para buscar foto do time (mesma lógica do JavaScript)"""
    if not name:
        return ''
    
    # Converte para lowercase
    name_normalized = name.lower()
    
    # Remove acentos
    name_normalized = unicodedata.normalize('NFD', name_normalized)
    name_normalized = ''.join(c for c in name_normalized if unicodedata.category(c) != 'Mn')
    
    # PRIMEIRO: Substitui espaços por underscore
    name_normalized = re.sub(r'\s+', '_', name_normalized)
    
    # DEPOIS: Remove caracteres especiais (incluindo hífens, mantém apenas letras, números e underscore)
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


def get_logo_base64():
    """Obtém logo da Logcomex em base64"""
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'img', 'logo_logcomex.png')
    
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            logo_bytes = f.read()
            logo_base64 = base64.b64encode(logo_bytes).decode('utf-8')
            return f'data:image/png;base64,{logo_base64}'
    
    return None


def get_hat_base64():
    """Obtém touca de Natal em base64"""
    hat_path = os.path.join(os.path.dirname(__file__), 'static', 'img', 'touca_natal.png')
    
    if os.path.exists(hat_path):
        with open(hat_path, 'rb') as f:
            hat_bytes = f.read()
            hat_base64 = base64.b64encode(hat_bytes).decode('utf-8')
            return f'data:image/png;base64,{hat_base64}'
    
    return None


def get_lights_base64():
    """Obtém luzes de Natal em base64"""
    lights_path = os.path.join(os.path.dirname(__file__), 'static', 'img', 'luzes_natal.png')
    
    if os.path.exists(lights_path):
        with open(lights_path, 'rb') as f:
            lights_bytes = f.read()
            lights_base64 = base64.b64encode(lights_bytes).decode('utf-8')
            return f'data:image/png;base64,{lights_base64}'
    
    return None


def get_celebration_theme():
    """Obtém o tema de celebração configurado do arquivo JSON"""
    import json
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    THEME_CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'celebration_theme_config.json')
    
    try:
        if os.path.exists(THEME_CONFIG_FILE):
            with open(THEME_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                theme = config.get('theme', 'black-november')
                # Valida o tema
                valid_themes = ['black-november', 'natal', 'padrao']
                if theme in valid_themes:
                    return theme
    except Exception as e:
        print(f"Erro ao ler configuração de tema: {e}")
    
    return 'black-november'  # Tema padrão


def generate_celebration_image(deal_data):
    """
    Gera uma imagem PNG da celebração do deal usando Playwright
    Usa o CSS e HTML exatos do painel de celebração existente
    
    Args:
        deal_data: Dict com dados do deal (dealName, amount, ownerName, etc.)
    
    Returns:
        bytes: Imagem PNG em bytes
    """
    
    # Obtém o tema configurado
    theme = get_celebration_theme()
    
    # Lê o CSS base do arquivo
    css_path = os.path.join(os.path.dirname(__file__), 'static', 'css', 'deal_celebration.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        celebration_css = f.read()
    
    # Lê o CSS dos temas
    themes_css_path = os.path.join(os.path.dirname(__file__), 'static', 'css', 'deal_celebration_themes.css')
    themes_css = ''
    if os.path.exists(themes_css_path):
        with open(themes_css_path, 'r', encoding='utf-8') as f:
            themes_css = f.read()
    
    # Se o tema for Natal, substitui o caminho da touca por base64
    if theme == 'natal':
        hat_base64 = get_hat_base64()
        if hat_base64:
            # Substitui o caminho da imagem pela versão base64 no CSS
            themes_css = themes_css.replace(
                "url('/static/img/touca_natal.png')",
                f"url('{hat_base64}')"
            )
    
    # Monta o HTML da celebração (estrutura IGUAL ao JavaScript)
    owner_html = ''
    sdr_html = ''
    ldr_html = ''
    
    if deal_data.get('ownerName'):
        owner_name = deal_data.get('ownerName')
        owner_photo_b64 = get_photo_base64(owner_name)
        
        if owner_photo_b64:
            owner_html = f'''
            <div class="deal-celebration-member">
                <div class="deal-celebration-photo-container">
                    <div class="deal-celebration-role-badge">EV</div>
                    <img class="deal-celebration-photo" src="{owner_photo_b64}" alt="{owner_name}">
                </div>
                <div class="deal-celebration-name">{owner_name}</div>
            </div>
            '''
        else:
            owner_html = f'''
            <div class="deal-celebration-member">
                <div class="deal-celebration-photo-container">
                    <div class="deal-celebration-role-badge">EV</div>
                    <div class="deal-celebration-photo" style="display:flex; background:#FFD700; justify-content:center; align-items:center; font-size:3rem; color:#fff; font-weight:bold;">
                        {owner_name[0].upper() if owner_name else '?'}
                    </div>
                </div>
                <div class="deal-celebration-name">{owner_name}</div>
            </div>
            '''
    
    if deal_data.get('sdrName'):
        sdr_name = deal_data.get('sdrName')
        sdr_photo_b64 = get_photo_base64(sdr_name)
        
        if sdr_photo_b64:
            sdr_html = f'''
            <div class="deal-celebration-member">
                <div class="deal-celebration-photo-container">
                    <div class="deal-celebration-role-badge">SDR</div>
                    <img class="deal-celebration-photo" src="{sdr_photo_b64}" alt="{sdr_name}">
                </div>
                <div class="deal-celebration-name">{sdr_name}</div>
            </div>
            '''
        else:
            sdr_html = f'''
            <div class="deal-celebration-member">
                <div class="deal-celebration-photo-container">
                    <div class="deal-celebration-role-badge">SDR</div>
                    <div class="deal-celebration-photo" style="display:flex; background:#FFD700; justify-content:center; align-items:center; font-size:3rem; color:#fff; font-weight:bold;">
                        {sdr_name[0].upper() if sdr_name else '?'}
                    </div>
                </div>
                <div class="deal-celebration-name">{sdr_name}</div>
            </div>
            '''
    
    if deal_data.get('ldrName'):
        ldr_name = deal_data.get('ldrName')
        ldr_photo_b64 = get_photo_base64(ldr_name)
        
        if ldr_photo_b64:
            ldr_html = f'''
            <div class="deal-celebration-member">
                <div class="deal-celebration-photo-container">
                    <div class="deal-celebration-role-badge">LDR</div>
                    <img class="deal-celebration-photo" src="{ldr_photo_b64}" alt="{ldr_name}">
                </div>
                <div class="deal-celebration-name">{ldr_name}</div>
            </div>
            '''
        else:
            ldr_html = f'''
            <div class="deal-celebration-member">
                <div class="deal-celebration-photo-container">
                    <div class="deal-celebration-role-badge">LDR</div>
                    <div class="deal-celebration-photo" style="display:flex; background:#FFD700; justify-content:center; align-items:center; font-size:3rem; color:#fff; font-weight:bold;">
                        {ldr_name[0].upper() if ldr_name else '?'}
                    </div>
                </div>
                <div class="deal-celebration-name">{ldr_name}</div>
            </div>
            '''
    
    # Usa productName se disponível, senão usa companyName
    product_or_company_html = ''
    if deal_data.get('productName'):
        product_or_company_html = f'<div class="deal-celebration-company">{deal_data.get("productName")}</div>'
    elif deal_data.get('companyName'):
        product_or_company_html = f'<div class="deal-celebration-company">{deal_data.get("companyName")}</div>'
    
    # Logo Logcomex em base64
    logo_base64 = get_logo_base64()
    logo_html = ''
    if logo_base64:
        logo_html = f'<img class="deal-celebration-logo" src="{logo_base64}" alt="Logcomex">'
    
    # Luzes de Natal (apenas para tema natal) - duas imagens lado a lado
    lights_html = ''
    if theme == 'natal':
        lights_base64 = get_lights_base64()
        if lights_base64:
            # Duas imagens lado a lado
            lights_html = f'''
            <img class="deal-celebration-lights" src="{lights_base64}" alt="Luzes de Natal">
            <img class="deal-celebration-lights" src="{lights_base64}" alt="Luzes de Natal">
            '''
    
    # HTML completo com CSS embutido
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Deal Celebration</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: transparent;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
            }}
            
            {celebration_css}
            
            {themes_css}
        </style>
    </head>
    <body>
        <div class="deal-celebration theme-{theme}">
            {lights_html}
            <div class="deal-celebration-title">{"🎄 CONTRATO ASSINADO! 🎅🏻" if theme == "natal" else "🎉 CONTRATO ASSINADO! 🎉"}</div>
            
            <div class="deal-celebration-team">
                {owner_html}
                {sdr_html}
                {ldr_html}
            </div>
            
            <div class="deal-celebration-amount">R$ {deal_data.get('amount', 0):,.2f}</div>
            
            <div class="deal-celebration-deal-name">{deal_data.get('dealName', 'N/A')}</div>
            
            {product_or_company_html}
            
            {logo_html}
        </div>
    </body>
    </html>
    """
    
    try:
        with sync_playwright() as p:
            # Inicia navegador headless
            browser = p.chromium.launch(headless=True)
            
            # Cria página com viewport PAISAGEM (landscape) como no painel
            # Proporção 16:9 (1920x1080) para telas de TV/monitores
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Define base URL para carregar imagens locais
            base_url = f'file://{os.path.abspath(os.path.dirname(__file__))}/'
            
            # Define o conteúdo HTML
            page.set_content(html_template, wait_until='networkidle')
            
            # Aguarda um pouco para garantir que tudo foi renderizado (incluindo fontes)
            page.wait_for_timeout(2000)
            
            # Pega o elemento da celebração
            celebration_element = page.locator('.deal-celebration')
            
            # Tira screenshot apenas do elemento (não da página inteira)
            screenshot = celebration_element.screenshot(type='png')
            
            # Fecha navegador
            browser.close()
            
            return screenshot
            
    except Exception as e:
        print(f"Erro ao gerar imagem de celebração: {e}")
        raise


def generate_celebration_image_base64(deal_data):
    """
    Gera uma imagem PNG da celebração em base64
    
    Args:
        deal_data: Dict com dados do deal
    
    Returns:
        str: Imagem PNG em base64
    """
    image_bytes = generate_celebration_image(deal_data)
    return base64.b64encode(image_bytes).decode('utf-8')
