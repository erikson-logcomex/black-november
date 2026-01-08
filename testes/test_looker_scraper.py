"""
Script de teste para extrair dados do Looker Dashboard
Extrai o valor do gauge de "Logos Supply" que considera churns
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
import json

# Carrega variáveis do .env
load_dotenv()

# Configurações
LOOKER_URL = "https://logcomex.looker.com/dashboards/1197"
LOOKER_USERNAME = os.getenv('LOOKER_USERNAME', '')
LOOKER_PASSWORD = os.getenv('LOOKER_PASSWORD', '')

def setup_driver(headless=False):
    """Configura o driver do Selenium"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent para parecer um navegador real
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_looker(driver, username, password):
    """Faz login no Looker"""
    try:
        print("🔐 Tentando fazer login no Looker...")
        time.sleep(3)  # Aguarda a página carregar completamente
        
        # Tira screenshot para debug
        driver.save_screenshot('looker_login_page.png')
        print("📸 Screenshot salvo: looker_login_page.png")
        
        # Tenta diferentes seletores para o campo de email
        email_field = None
        selectors_email = [
            (By.ID, "email"),
            (By.NAME, "email"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[name='email']"),
            (By.CSS_SELECTOR, "input[placeholder*='email' i]"),
            (By.XPATH, "//input[@type='email']"),
            (By.XPATH, "//input[contains(@placeholder, 'email') or contains(@placeholder, 'Email')]")
        ]
        
        for selector_type, selector_value in selectors_email:
            try:
                email_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                print(f"✅ Campo de email encontrado com seletor: {selector_type} = {selector_value}")
                break
            except:
                continue
        
        if not email_field:
            print("❌ Campo de email não encontrado. Tentando encontrar todos os inputs...")
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"📝 Encontrados {len(all_inputs)} campos de input na página")
            for i, inp in enumerate(all_inputs):
                print(f"   Input {i+1}: type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, id={inp.get_attribute('id')}, placeholder={inp.get_attribute('placeholder')}")
            return False
        
        email_field.clear()
        email_field.send_keys(username)
        print(f"✅ Email preenchido: {username}")
        time.sleep(1)
        
        # Tenta diferentes seletores para o campo de senha
        password_field = None
        selectors_password = [
            (By.ID, "password"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input[name='password']"),
            (By.XPATH, "//input[@type='password']")
        ]
        
        for selector_type, selector_value in selectors_password:
            try:
                password_field = driver.find_element(selector_type, selector_value)
                print(f"✅ Campo de senha encontrado com seletor: {selector_type} = {selector_value}")
                break
            except:
                continue
        
        if not password_field:
            print("❌ Campo de senha não encontrado")
            return False
        
        password_field.clear()
        password_field.send_keys(password)
        print("✅ Senha preenchida")
        time.sleep(1)
        
        # Tenta encontrar o botão de login
        login_button = None
        selectors_button = [
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "button.btn-primary"),
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Sign') or contains(text(), 'Login') or contains(text(), 'Entrar')]"),
            (By.XPATH, "//button[@type='submit']")
        ]
        
        for selector_type, selector_value in selectors_button:
            try:
                login_button = driver.find_element(selector_type, selector_value)
                print(f"✅ Botão de login encontrado com seletor: {selector_type} = {selector_value}")
                break
            except:
                continue
        
        if not login_button:
            print("❌ Botão de login não encontrado")
            return False
        
        login_button.click()
        print("✅ Botão de login clicado")
        time.sleep(5)  # Aguarda o redirecionamento
        
        # Aguarda o dashboard carregar (procura por algum elemento específico do dashboard)
        print("⏳ Aguardando dashboard carregar...")
        try:
            WebDriverWait(driver, 60).until(
                lambda d: 'dashboard' in d.current_url.lower() or 'dashboards' in d.current_url.lower()
            )
            print("✅ Dashboard carregado!")
            time.sleep(5)  # Aguarda mais um pouco para garantir que tudo carregou
            return True
        except TimeoutException:
            print(f"⚠️ Timeout, mas URL atual é: {driver.current_url}")
            # Tira screenshot para ver o estado atual
            driver.save_screenshot('looker_after_login.png')
            print("📸 Screenshot salvo: looker_after_login.png")
            # Mesmo assim tenta continuar
            return True
        
    except TimeoutException as e:
        print(f"❌ Timeout ao fazer login: {e}")
        driver.save_screenshot('looker_error.png')
        print("📸 Screenshot do erro salvo: looker_error.png")
        return False
    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot('looker_error.png')
        print("📸 Screenshot do erro salvo: looker_error.png")
        return False

def extract_gauge_value(driver):
    """Extrai o valor do gauge do dashboard - retorna lista de valores encontrados"""
    try:
        print("🔍 Procurando pelo valor do gauge...")
        
        # Aguarda o iframe do gauge carregar
        time.sleep(5)  # Dá tempo para o iframe carregar
        
        # Tenta encontrar o iframe do gauge
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"📊 Encontrados {len(iframes)} iframes na página")
        
        values_found = []
        
        # Procura em diferentes locais possíveis
        # 1. Tenta encontrar diretamente na página
        try:
            # Procura por elementos que possam conter o valor "733" ou similar
            value_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '733') or contains(text(), 'Supply Logos')]")
            for elem in value_elements:
                text = elem.text
                print(f"📝 Texto encontrado: {text}")
                # Tenta extrair número do texto
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    print(f"🔢 Números encontrados: {numbers}")
        except Exception as e:
            print(f"⚠️ Erro ao procurar na página principal: {e}")
        
        # 2. Tenta encontrar dentro dos iframes
        for i, iframe in enumerate(iframes):
            try:
                print(f"🔍 Verificando iframe {i+1}...")
                driver.switch_to.frame(iframe)
                
                # Procura pelo elemento do gauge
                # O gauge pode estar em um SVG ou elemento de texto
                try:
                    # Procura por SVG (gauge visual)
                    svg_elements = driver.find_elements(By.TAG_NAME, "svg")
                    print(f"📊 Encontrados {len(svg_elements)} elementos SVG no iframe")
                    
                    # Procura por texto que contenha números
                    text_elements = driver.find_elements(By.XPATH, "//*[text()]")
                    for elem in text_elements:
                        text = elem.text.strip()
                        if text and text.isdigit():
                            value = int(text)
                            print(f"🔢 Valor encontrado no iframe: {value}")
                            if value not in values_found:
                                values_found.append(value)
                except Exception as e:
                    print(f"⚠️ Erro ao procurar no iframe: {e}")
                
                # Volta para o contexto principal
                driver.switch_to.default_content()
                
            except Exception as e:
                print(f"⚠️ Erro ao acessar iframe {i+1}: {e}")
                driver.switch_to.default_content()
        
        # 3. Tenta encontrar usando seletores CSS específicos do Looker
        try:
            # Procura por elementos com classes comuns do Looker
            looker_elements = driver.find_elements(By.CSS_SELECTOR, 
                "[class*='gauge'], [class*='metric'], [class*='value'], [data-value]"
            )
            for elem in looker_elements:
                text = elem.text.strip()
                value_attr = elem.get_attribute('data-value')
                if value_attr:
                    print(f"📊 Valor encontrado no atributo data-value: {value_attr}")
                    if not gauge_value:
                        try:
                            gauge_value = int(value_attr)
                        except:
                            pass
                if text and text.isdigit():
                    value = int(text)
                    print(f"📊 Valor encontrado no texto: {value}")
                    if value not in values_found:
                        values_found.append(value)
        except Exception as e:
            print(f"⚠️ Erro ao procurar com seletores CSS: {e}")
        
        return values_found
        
    except Exception as e:
        print(f"❌ Erro ao extrair valor do gauge: {e}")
        return None

def extract_dashboard_data(driver):
    """Extrai todos os dados relevantes do dashboard"""
    data = {
        'gauge_value': None,
        'gauge_target': 800,  # Meta conhecida
        'remaining': None,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        print("📊 Extraindo dados do dashboard...")
        
        # Aguarda o dashboard carregar completamente
        time.sleep(10)
        
        # Extrai o valor do gauge (retorna uma lista de valores encontrados)
        values_found = extract_gauge_value(driver)
        
        # O valor atual geralmente é menor que a meta
        # A meta geralmente é 800
        if values_found:
            # Filtra valores válidos (entre 0 e 1000)
            valid_values = [v for v in values_found if 0 <= v <= 1000]
            if valid_values:
                # Remove duplicatas e ordena
                unique_values = sorted(set(valid_values))
                print(f"🔢 Valores únicos encontrados: {unique_values}")
                
                # O valor atual geralmente é o maior que não é 800 (ou o menor se todos forem 800)
                if 800 in unique_values:
                    # Remove 800 da lista para encontrar o valor atual
                    current_values = [v for v in unique_values if v != 800]
                    if current_values:
                        data['gauge_value'] = max(current_values)  # Pega o maior valor que não é a meta
                    else:
                        data['gauge_value'] = 800  # Se só encontrou 800, assume que é o valor atual
                    data['gauge_target'] = 800
                else:
                    # Se não encontrou 800, assume que o maior é o valor atual
                    data['gauge_value'] = max(unique_values)
                    data['gauge_target'] = 800  # Meta conhecida
        
        # Calcula o restante
        if data['gauge_value'] and data['gauge_target']:
            data['remaining'] = data['gauge_target'] - data['gauge_value']
        
        return data
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados do dashboard: {e}")
        return data

def main():
    """Função principal"""
    print("🚀 Iniciando teste de extração de dados do Looker...")
    print(f"📋 URL: {LOOKER_URL}")
    
    if not LOOKER_USERNAME or not LOOKER_PASSWORD:
        print("⚠️ ATENÇÃO: Variáveis de ambiente LOOKER_USERNAME e LOOKER_PASSWORD não configuradas!")
        print("💡 Configure-as antes de executar:")
        print("   export LOOKER_USERNAME='seu_usuario'")
        print("   export LOOKER_PASSWORD='sua_senha'")
        return
    
    driver = None
    try:
        # Configura o driver
        driver = setup_driver(headless=False)  # headless=False para ver o que está acontecendo
        
        # Acessa o Looker
        print(f"🌐 Acessando {LOOKER_URL}...")
        driver.get(LOOKER_URL)
        time.sleep(3)
        
        # Verifica se precisa fazer login
        current_url = driver.current_url
        if 'login' in current_url.lower() or 'signin' in current_url.lower():
            print("🔐 Página de login detectada...")
            if not login_looker(driver, LOOKER_USERNAME, LOOKER_PASSWORD):
                print("❌ Falha ao fazer login")
                return
        else:
            print("✅ Já autenticado ou não requer login")
        
        # Extrai os dados
        data = extract_dashboard_data(driver)
        
        # Salva os resultados
        output_file = 'looker_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*50)
        print("📊 RESULTADOS:")
        print("="*50)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*50)
        print(f"💾 Dados salvos em: {output_file}")
        
        # Mantém o navegador aberto por alguns segundos para inspeção
        print("\n⏳ Mantendo navegador aberto por 30 segundos para inspeção...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("🔒 Fechando navegador...")
            driver.quit()

if __name__ == "__main__":
    main()

