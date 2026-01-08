"""
Utilitário para extrair dados de ARR do Looker
Usa navegador headless no backend para manter sessão autenticada no servidor
"""

import os
import time
import re
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from utils.looker_storage import save_cookies, load_cookies, load_storage_state

load_dotenv()

# Configurações
ARR_LOOKER_URL = "https://logcomex.looker.com/dashboards/837"
LOOKER_USERNAME = os.getenv('LOOKER_USERNAME', '')
LOOKER_PASSWORD = os.getenv('LOOKER_PASSWORD', '')

# Meta fixa de ARR
ARR_TARGET = 276103000  # R$276.103.000

# Cache em memória para os dados de ARR
_arr_cache = {
    'data': None,
    'timestamp': None,
    'cache_duration': 300  # 5 minutos em segundos
}

def extract_arr_value(page):
    """Extrai o valor de ARR do dashboard"""
    try:
        print("🔍 Procurando pelo valor de ARR...")
        time.sleep(8)  # Aguarda iframes e conteúdo carregarem completamente
        
        values_found = []
        
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
                        # Procura valores monetários (R$ seguido de números com pontos e vírgulas)
                        # Exemplo: R$218.888.145 ou R$ 218.888.145
                        money_pattern = r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)'
                        matches = re.findall(money_pattern, all_text)
                        for match in matches:
                            # Remove pontos e converte vírgula para ponto
                            value_str = match.replace('.', '').replace(',', '.')
                            try:
                                value = float(value_str)
                                # Valores de ARR estão entre 100M e 300M
                                if 100000000 <= value <= 300000000:
                                    if value not in values_found:
                                        values_found.append(value)
                                        print(f"💰 Valor de ARR encontrado no iframe {i+1}: R${value:,.2f}")
                            except:
                                continue
                    except Exception as e:
                        print(f"⚠️ Erro ao extrair texto do iframe {i+1}: {e}")
                    
                    # Procura em elementos individuais também
                    try:
                        text_elements = iframe_content.query_selector_all('*')
                        for elem in text_elements:
                            try:
                                text = elem.inner_text().strip()
                                if text:
                                    # Procura valores monetários no texto
                                    money_pattern = r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)'
                                    matches = re.findall(money_pattern, text)
                                    for match in matches:
                                        value_str = match.replace('.', '').replace(',', '.')
                                        try:
                                            value = float(value_str)
                                            if 100000000 <= value <= 300000000:
                                                if value not in values_found:
                                                    values_found.append(value)
                                                    print(f"💰 Valor de ARR encontrado em elemento do iframe {i+1}: R${value:,.2f}")
                                        except:
                                            continue
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
            money_pattern = r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)'
            matches = re.findall(money_pattern, all_text)
            for match in matches:
                value_str = match.replace('.', '').replace(',', '.')
                try:
                    value = float(value_str)
                    if 100000000 <= value <= 300000000:
                        if value not in values_found:
                            values_found.append(value)
                            print(f"💰 Valor de ARR encontrado na página: R${value:,.2f}")
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Erro ao procurar na página principal: {e}")
        
        # Salva screenshot para debug (opcional)
        try:
            page.screenshot(path='arr_looker_debug.png', full_page=True)
            print("📸 Screenshot salvo: arr_looker_debug.png")
        except:
            pass
        
        return values_found
        
    except Exception as e:
        print(f"❌ Erro ao extrair valor de ARR: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_arr_value(force_refresh=False):
    """
    Função principal para obter o valor de ARR do Looker
    Usa cookies salvos se disponíveis
    
    Args:
        force_refresh: Se True, ignora o cache e faz scraping novamente
    
    Returns:
        dict com arr_value, arr_target, remaining, percentage, timestamp ou None
    """
    # Verifica cache primeiro (a menos que force_refresh seja True)
    if not force_refresh and _arr_cache['data'] and _arr_cache['timestamp']:
        elapsed = time.time() - _arr_cache['timestamp']
        if elapsed < _arr_cache['cache_duration']:
            print(f"✅ Usando cache de ARR (válido por mais {int(_arr_cache['cache_duration'] - elapsed)}s)")
            return _arr_cache['data']
    
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
            print(f"🌐 Acessando {ARR_LOOKER_URL}...")
            page.goto(ARR_LOOKER_URL, wait_until='networkidle', timeout=30000)
            time.sleep(5)  # Aguarda mais tempo para carregar
            
            # Verifica se precisa fazer login
            current_url = page.url
            print(f"📍 URL atual após acesso: {current_url}")
            
            # Verifica múltiplas formas de detectar página de login
            needs_login = (
                'login' in current_url.lower() or 
                'signin' in current_url.lower() or
                'auth' in current_url.lower() or
                '/login' in current_url.lower()
            )
            
            # Também verifica pelo conteúdo da página
            if not needs_login:
                try:
                    page_text = page.inner_text('body').lower()
                    # Verifica se há indicadores de página de login
                    login_indicators = ['sign in', 'log in', 'enter your email', 'password', 'authentication']
                    if any(indicator in page_text[:500] for indicator in login_indicators):
                        # Mas verifica se não é apenas um formulário de busca ou outro elemento
                        if 'dashboard' not in page_text[:1000] and 'looker' in page_text[:500]:
                            needs_login = True
                            print("⚠️ Detectado conteúdo de login na página")
                except Exception as e:
                    print(f"⚠️ Erro ao verificar conteúdo da página: {e}")
            
            if needs_login:
                print(f"❌ Cookies expirados ou inválidos (URL: {current_url})")
                print("💡 Execute 'python setup_looker_session.py' para reconfigurar a sessão")
                # Tira screenshot para debug
                try:
                    page.screenshot(path='arr_login_error.png', full_page=True)
                    print("📸 Screenshot salvo: arr_login_error.png")
                except:
                    pass
                return None
            else:
                print("✅ Usando sessão autenticada existente")
            
            # Extrai os valores
            values_found = extract_arr_value(page)
            
            # Processa os valores
            arr_value = None
            
            if values_found:
                unique_values = sorted(set([v for v in values_found if 100000000 <= v <= 300000000]))
                print(f"💰 Valores únicos encontrados: {[f'R${v:,.2f}' for v in unique_values]}")
                
                # O valor atual deve ser o maior valor encontrado (mais próximo da meta)
                if unique_values:
                    arr_value = max(unique_values)
            
            # Calcula remaining e percentage corretamente
            remaining = None
            percentage = 0
            
            if arr_value and ARR_TARGET > 0:
                if arr_value >= ARR_TARGET:
                    # Meta alcançada - remaining é 0
                    remaining = 0
                    # Mostra porcentagem real (pode ser > 100%)
                    percentage = round((arr_value / ARR_TARGET * 100), 2)
                else:
                    # Meta não alcançada - calcula quanto falta
                    remaining = ARR_TARGET - arr_value
                    percentage = round((arr_value / ARR_TARGET * 100), 2)
            
            result = {
                'arr_value': arr_value,
                'arr_target': ARR_TARGET,
                'remaining': remaining,
                'percentage': percentage,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Atualiza cache
            _arr_cache['data'] = result
            _arr_cache['timestamp'] = time.time()
            print(f"💾 Cache de ARR atualizado (válido por {_arr_cache['cache_duration']}s)")
            
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
    result = get_arr_value()
    if result:
        print("\n" + "="*50)
        print("📊 RESULTADOS:")
        print("="*50)
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("="*50)
    else:
        print("❌ Não foi possível obter os dados")

