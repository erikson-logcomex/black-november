"""
Script de teste para extrair dados do Looker usando cookies salvos
Solução alternativa quando a API não está disponível
Requer login manual uma vez para salvar os cookies
"""

import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import json

# Carrega variáveis do .env
load_dotenv()

# Configurações
LOOKER_URL = "https://logcomex.looker.com/dashboards/1197"
COOKIES_FILE = 'looker_cookies.pkl'

def setup_driver(headless=True):
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

def save_cookies(driver, filename):
    """Salva os cookies do navegador"""
    try:
        cookies = driver.get_cookies()
        with open(filename, 'wb') as f:
            pickle.dump(cookies, f)
        print(f"✅ Cookies salvos em {filename}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar cookies: {e}")
        return False

def load_cookies(driver, filename):
    """Carrega cookies salvos no navegador"""
    try:
        if not os.path.exists(filename):
            print(f"⚠️ Arquivo de cookies {filename} não encontrado")
            return False
        
        driver.get(LOOKER_URL.split('/dashboards')[0])  # Vai para a página base primeiro
        time.sleep(2)
        
        with open(filename, 'rb') as f:
            cookies = pickle.load(f)
        
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"⚠️ Erro ao adicionar cookie: {e}")
                continue
        
        print(f"✅ Cookies carregados de {filename}")
        return True
    except Exception as e:
        print(f"❌ Erro ao carregar cookies: {e}")
        return False

def extract_gauge_value(driver):
    """Extrai o valor do gauge do dashboard"""
    try:
        print("🔍 Procurando pelo valor do gauge...")
        time.sleep(5)
        
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"📊 Encontrados {len(iframes)} iframes na página")
        
        values_found = []
        
        for i, iframe in enumerate(iframes):
            try:
                print(f"🔍 Verificando iframe {i+1}...")
                driver.switch_to.frame(iframe)
                
                text_elements = driver.find_elements(By.XPATH, "//*[text()]")
                for elem in text_elements:
                    text = elem.text.strip()
                    if text and text.isdigit():
                        value = int(text)
                        if value not in values_found and 0 <= value <= 1000:
                            values_found.append(value)
                            print(f"🔢 Valor encontrado: {value}")
                
                driver.switch_to.default_content()
            except Exception as e:
                print(f"⚠️ Erro ao acessar iframe {i+1}: {e}")
                driver.switch_to.default_content()
        
        return values_found
        
    except Exception as e:
        print(f"❌ Erro ao extrair valor do gauge: {e}")
        return []

def get_dashboard_data_with_cookies():
    """Obtém dados do dashboard usando cookies salvos"""
    driver = None
    try:
        driver = setup_driver(headless=True)
        
        # Tenta carregar cookies salvos
        if load_cookies(driver, COOKIES_FILE):
            # Recarrega a página para aplicar os cookies
            driver.get(LOOKER_URL)
            time.sleep(5)
            
            # Verifica se está autenticado (não está na página de login)
            current_url = driver.current_url
            if 'login' in current_url.lower() or 'signin' in current_url.lower():
                print("❌ Cookies expirados ou inválidos. É necessário fazer login manual novamente.")
                print("💡 Execute o script save_looker_cookies.py para salvar novos cookies")
                return None
        else:
            print("❌ Não foi possível carregar cookies. É necessário fazer login manual primeiro.")
            print("💡 Execute o script save_looker_cookies.py para salvar cookies")
            return None
        
        # Extrai os valores
        values_found = extract_gauge_value(driver)
        
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
        
        return {
            'gauge_value': gauge_value,
            'gauge_target': gauge_target,
            'remaining': gauge_target - gauge_value if gauge_value else None,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if driver:
            driver.quit()

def main():
    """Função principal"""
    print("🚀 Iniciando extração de dados do Looker usando cookies...")
    
    data = get_dashboard_data_with_cookies()
    
    if data:
        output_file = 'looker_cookies_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*50)
        print("📊 RESULTADOS:")
        print("="*50)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*50)
        print(f"💾 Dados salvos em: {output_file}")
    else:
        print("❌ Não foi possível obter os dados")

if __name__ == "__main__":
    main()

