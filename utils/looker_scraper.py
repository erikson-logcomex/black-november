"""
Utilitário para extrair dados do Looker usando navegador headless no backend
Usa Playwright para manter sessão autenticada no servidor
"""

import os
import time
import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv
from utils.looker_storage import save_cookies, load_cookies, load_storage_state

load_dotenv()

# Configurações
LOOKER_URL = "https://logcomex.looker.com/dashboards/1197"
LOOKER_USERNAME = os.getenv('LOOKER_USERNAME', '')
LOOKER_PASSWORD = os.getenv('LOOKER_PASSWORD', '')

# Cache em memória para os dados do Looker
_looker_cache = {
    'data': None,
    'timestamp': None,
    'cache_duration': 300  # 5 minutos em segundos
}

# Login manual deve ser feito via setup_looker_session.py
# Esta função foi removida pois o login com 2FA requer interação manual

def extract_gauge_value(page):
    """Extrai o valor do gauge do dashboard"""
    try:
        print("🔍 Procurando pelo valor do gauge...")
        time.sleep(8)  # Aguarda iframes e conteúdo carregarem completamente
        
        values_found = []
        import re
        
        # Procura em iframes
        iframes = page.query_selector_all('iframe')
        print(f"📊 Encontrados {len(iframes)} iframes na página")
        
        for i, iframe in enumerate(iframes):
            try:
                print(f"🔍 Verificando iframe {i+1}...")
                iframe_content = iframe.content_frame()
                
                if iframe_content:
                    # Aguarda conteúdo do iframe carregar
                    try:
                        iframe_content.wait_for_load_state('networkidle', timeout=10000)
                    except:
                        pass
                    
                    # Procura por todos os elementos de texto
                    try:
                        all_text = iframe_content.inner_text('body')
                        # Procura números de 2-4 dígitos (700-999 para logos)
                        numbers = re.findall(r'\b\d{2,4}\b', all_text)
                        for num_str in numbers:
                            value = int(num_str)
                            if 600 <= value <= 1000 and value not in values_found:
                                values_found.append(value)
                                print(f"🔢 Valor encontrado no iframe {i+1}: {value}")
                    except Exception as e:
                        print(f"⚠️ Erro ao extrair texto do iframe {i+1}: {e}")
                    
                    # Procura em elementos individuais também
                    try:
                        text_elements = iframe_content.query_selector_all('*')
                        for elem in text_elements:
                            try:
                                text = elem.inner_text().strip()
                                if text:
                                    # Procura números no texto
                                    numbers = re.findall(r'\b\d{2,4}\b', text)
                                    for num_str in numbers:
                                        value = int(num_str)
                                        if 600 <= value <= 1000 and value not in values_found:
                                            values_found.append(value)
                                            print(f"🔢 Valor encontrado em elemento do iframe {i+1}: {value}")
                            except:
                                continue
                    except Exception as e:
                        print(f"⚠️ Erro ao procurar elementos no iframe {i+1}: {e}")
            except Exception as e:
                print(f"⚠️ Erro ao acessar iframe {i+1}: {e}")
                continue
        
        # Também procura na página principal
        try:
            all_text = page.inner_text('body')
            # Procura números de 2-4 dígitos
            numbers = re.findall(r'\b\d{2,4}\b', all_text)
            for num_str in numbers:
                value = int(num_str)
                if 600 <= value <= 1000 and value not in values_found:
                    values_found.append(value)
                    print(f"🔢 Valor encontrado na página: {value}")
        except Exception as e:
            print(f"⚠️ Erro ao procurar na página principal: {e}")
        
        # Salva screenshot para debug (opcional)
        try:
            page.screenshot(path='looker_debug.png', full_page=True)
            print("📸 Screenshot salvo: looker_debug.png")
        except:
            pass
        
        return values_found
        
    except Exception as e:
        print(f"❌ Erro ao extrair valor do gauge: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_looker_gauge_value(force_refresh=False):
    """
    Função principal para obter o valor do gauge do Looker
    Usa cookies salvos se disponíveis, caso contrário faz login
    Implementa cache em memória para evitar scraping excessivo
    
    Args:
        force_refresh: Se True, ignora o cache e faz scraping novamente
    
    Returns:
        dict com gauge_value, gauge_target, remaining, timestamp ou None
    """
    # Verifica cache primeiro (a menos que force_refresh seja True)
    if not force_refresh and _looker_cache['data'] and _looker_cache['timestamp']:
        elapsed = time.time() - _looker_cache['timestamp']
        if elapsed < _looker_cache['cache_duration']:
            print(f"✅ Usando cache do Looker (válido por mais {int(_looker_cache['cache_duration'] - elapsed)}s)")
            return _looker_cache['data']
    
    if not LOOKER_USERNAME or not LOOKER_PASSWORD:
        print("⚠️ Credenciais do Looker não configuradas no .env")
        return None
    
    with sync_playwright() as p:
        try:
            # Inicia navegador headless com opções para Cloud Run e anti-detecção
            print("🌐 Iniciando navegador headless...")
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled',  # Remove flag de automação
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-web-security',
                    '--window-size=1920,1080'
                ]
            )
            # Tenta carregar storage state completo (cookies + localStorage + sessionStorage)
            storage_state = load_storage_state()
            
            context_options = {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'viewport': {'width': 1920, 'height': 1080},
                'locale': 'pt-BR',
                'timezone_id': 'America/Sao_Paulo',
                # Remove flags de automação
                'extra_http_headers': {
                    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
                }
            }
            
            # Adiciona script para remover flags de automação
            context_options['java_script_enabled'] = True
            
            if storage_state:
                # Usa storage state completo (melhor - inclui localStorage e sessionStorage)
                context_options['storage_state'] = storage_state
                print(f"✅ Storage state carregado (cookies + localStorage + sessionStorage)")
            else:
                # Fallback: tenta carregar apenas cookies
                cookies = load_cookies()
                if cookies:
                    # Normaliza os cookies
                    normalized_cookies = []
                    for cookie in cookies:
                        if 'domain' not in cookie or not cookie['domain']:
                            cookie['domain'] = 'logcomex.looker.com'
                        if 'path' not in cookie or not cookie['path']:
                            cookie['path'] = '/'
                        cookie_clean = {
                            'name': cookie.get('name', ''),
                            'value': cookie.get('value', ''),
                            'domain': cookie.get('domain', 'logcomex.looker.com'),
                            'path': cookie.get('path', '/'),
                        }
                        if 'secure' in cookie:
                            cookie_clean['secure'] = cookie.get('secure', False)
                        if 'httpOnly' in cookie:
                            cookie_clean['httpOnly'] = cookie.get('httpOnly', False)
                        if 'expires' in cookie and cookie['expires']:
                            cookie_clean['expires'] = cookie['expires']
                        normalized_cookies.append(cookie_clean)
                    
                    context_options['cookies'] = normalized_cookies
                    print(f"✅ {len(normalized_cookies)} cookies carregados (fallback)")
                else:
                    print("⚠️ Nenhum storage state ou cookie encontrado")
            
            context = browser.new_context(**context_options)
            
            page = context.new_page()
            
            # Remove flags de automação via JavaScript (anti-detecção)
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.navigator.chrome = {
                    runtime: {}
                };
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['pt-BR', 'pt', 'en-US', 'en']
                });
            """)
            
            # Acessa o dashboard diretamente
            print(f"🌐 Acessando {LOOKER_URL}...")
            page.goto(LOOKER_URL, wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            # Verifica se precisa fazer login
            current_url = page.url
            needs_login = 'login' in current_url.lower() or 'signin' in current_url.lower()
            
            if needs_login:
                print("❌ Cookies expirados ou inválidos")
                print("💡 Execute 'python setup_looker_session.py' para reconfigurar a sessão")
                print("   (Isso só precisa ser feito quando os cookies expirarem)")
                return None
            else:
                print("✅ Usando sessão autenticada existente")
            
            # Extrai os valores
            values_found = extract_gauge_value(page)
            
            # Processa os valores
            gauge_value = None
            gauge_target = 800
            
            if values_found:
                unique_values = sorted(set([v for v in values_found if 0 <= v <= 1000]))
                print(f"🔢 Valores únicos encontrados: {unique_values}")
                
                if 800 in unique_values:
                    current_values = [v for v in unique_values if v != 800]
                    if current_values:
                        gauge_value = max(current_values)
                else:
                    gauge_value = max(unique_values) if unique_values else None
            
            result = {
                'gauge_value': gauge_value,
                'gauge_target': gauge_target,
                'remaining': gauge_target - gauge_value if gauge_value else None,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Atualiza cache
            _looker_cache['data'] = result
            _looker_cache['timestamp'] = time.time()
            print(f"💾 Cache do Looker atualizado (válido por {_looker_cache['cache_duration']}s)")
            
            return result
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            try:
                browser.close()
            except:
                pass

if __name__ == "__main__":
    # Teste standalone
    result = get_looker_gauge_value()
    if result:
        print("\n" + "="*50)
        print("📊 RESULTADOS:")
        print("="*50)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("="*50)
    else:
        print("❌ Não foi possível obter os dados")

