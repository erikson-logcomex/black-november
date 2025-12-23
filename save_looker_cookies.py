"""
Script para salvar cookies do Looker após login manual
Execute este script UMA VEZ após fazer login manualmente no Looker
Os cookies serão salvos e reutilizados automaticamente
"""

import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Configurações
LOOKER_URL = "https://logcomex.looker.com/dashboards/1197"
COOKIES_FILE = 'looker_cookies.pkl'

def setup_driver():
    """Configura o driver do Selenium"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def save_cookies_manual():
    """Abre o navegador para login manual e salva os cookies"""
    driver = None
    try:
        print("🌐 Abrindo navegador para login manual...")
        print("📋 INSTRUÇÕES:")
        print("   1. Faça login no Looker (incluindo o código do Google Authenticator)")
        print("   2. Aguarde o dashboard carregar completamente")
        print("   3. Pressione ENTER aqui no terminal quando estiver logado")
        
        driver = setup_driver()
        driver.get(LOOKER_URL)
        
        # Aguarda o usuário fazer login manualmente
        input("\n⏳ Pressione ENTER após fazer login e o dashboard carregar...\n")
        
        # Verifica se está autenticado
        current_url = driver.current_url
        if 'login' in current_url.lower() or 'signin' in current_url.lower():
            print("❌ Parece que você ainda não está logado. Tente novamente.")
            return False
        
        # Salva os cookies
        cookies = driver.get_cookies()
        with open(COOKIES_FILE, 'wb') as f:
            pickle.dump(cookies, f)
        
        print(f"✅ Cookies salvos com sucesso em {COOKIES_FILE}!")
        print("💡 Agora você pode usar test_looker_cookies.py para extrair dados automaticamente")
        
        # Mantém o navegador aberto por alguns segundos
        print("\n⏳ Fechando navegador em 5 segundos...")
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    save_cookies_manual()

