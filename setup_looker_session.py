"""
Script para configurar sessão do Looker pela primeira vez
Abre navegador para login manual com 2FA e marca "confiar no navegador"
Execute este script UMA VEZ para configurar a sessão
"""

import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

# Configurações
LOOKER_URL = "https://logcomex.looker.com/dashboards/1197"
LOOKER_USERNAME = os.getenv('LOOKER_USERNAME', '')
LOOKER_PASSWORD = os.getenv('LOOKER_PASSWORD', '')

def setup_looker_session():
    """
    Configura sessão do Looker pela primeira vez
    Abre navegador para login manual, incluindo 2FA
    """
    if not LOOKER_USERNAME or not LOOKER_PASSWORD:
        print("⚠️ Credenciais do Looker não configuradas no .env")
        return False
    
    print("="*60)
    print("🔐 CONFIGURAÇÃO INICIAL DA SESSÃO DO LOOKER")
    print("="*60)
    print("\n📋 INSTRUÇÕES:")
    print("   1. O navegador será aberto automaticamente")
    print("   2. Faça login normalmente (email e senha)")
    print("   3. Quando pedir o código do Google Authenticator:")
    print("      - Insira o código no navegador")
    print("      - MARQUE o checkbox 'Confiar neste navegador' ou 'Remember this device'")
    print("      - Clique em continuar/verificar")
    print("   4. Aguarde o dashboard carregar completamente")
    print("   5. Pressione ENTER aqui no terminal quando tudo estiver pronto")
    print("\n" + "="*60)
    
    input("\n⏳ Pressione ENTER para abrir o navegador...\n")
    
    with sync_playwright() as p:
        try:
            # Abre navegador VISÍVEL (não headless) para login manual
            print("🌐 Abrindo navegador...")
            browser = p.chromium.launch(headless=False)  # VISÍVEL para interação manual
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # Acessa o Looker
            print(f"🌐 Acessando {LOOKER_URL}...")
            page.goto(LOOKER_URL, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # Verifica se já está logado
            current_url = page.url
            if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                print("✅ Parece que você já está logado!")
            else:
                print("🔐 Fazendo login...")
                
                # Preenche email
                try:
                    email_field = page.wait_for_selector('input[name="email"], input[type="email"], input#email', timeout=10000)
                    email_field.fill(LOOKER_USERNAME)
                    print(f"✅ Email preenchido: {LOOKER_USERNAME}")
                    time.sleep(1)
                except Exception as e:
                    print(f"⚠️ Erro ao preencher email: {e}")
                
                # Preenche senha
                try:
                    password_field = page.wait_for_selector('input[name="password"], input[type="password"], input#password', timeout=10000)
                    password_field.fill(LOOKER_PASSWORD)
                    print("✅ Senha preenchida")
                    time.sleep(1)
                except Exception as e:
                    print(f"⚠️ Erro ao preencher senha: {e}")
                
                # Clica no botão de login
                try:
                    login_button = page.wait_for_selector('input[type="submit"], button[type="submit"]', timeout=10000)
                    login_button.click()
                    print("✅ Botão de login clicado")
                    time.sleep(3)
                except Exception as e:
                    print(f"⚠️ Erro ao clicar no botão de login: {e}")
            
            # Aguarda possível tela de 2FA
            print("\n" + "="*60)
            print("⏳ AGUARDANDO AÇÃO MANUAL:")
            print("="*60)
            print("💡 Se aparecer tela de verificação 2FA:")
            print("   1. Insira o código do Google Authenticator")
            print("   2. MARQUE o checkbox 'Confiar neste navegador' / 'Remember this device'")
            print("   3. Clique em continuar/verificar")
            print("   4. Aguarde o dashboard carregar completamente")
            print("\n⏳ Aguardando você completar o login e o dashboard carregar...")
            print("   (O navegador ficará aberto)")
            
            # Aguarda o usuário completar o processo manualmente
            input("\n✅ Pressione ENTER quando o dashboard estiver totalmente carregado...\n")
            
            # Verifica se está no dashboard ou se foi redirecionado para login
            current_url = page.url
            print(f"\n📍 URL atual: {current_url}")
            
            # Verifica se foi redirecionado para login (isso seria um problema)
            if 'login' in current_url.lower() or 'signin' in current_url.lower():
                print("❌ ERRO: Você foi redirecionado para a página de login!")
                print("   Isso significa que a sessão não está válida.")
                print("   Verifique se você completou o login corretamente.")
                response = input("   Continuar mesmo assim? (s/n): ")
                if response.lower() != 's':
                    print("❌ Cancelado pelo usuário")
                    return False
            elif 'dashboard' in current_url.lower() or 'dashboards' in current_url.lower():
                print(f"✅ Dashboard detectado: {current_url}")
            else:
                # Se não está em login nem em dashboard, pode ser outra página válida do Looker
                if 'looker.com' in current_url.lower():
                    print(f"⚠️ Você está em uma página do Looker, mas não no dashboard.")
                    print(f"   URL: {current_url}")
                    print("   Isso pode funcionar, mas é recomendado estar no dashboard.")
                    response = input("   Continuar mesmo assim? (s/n): ")
                    if response.lower() != 's':
                        print("❌ Cancelado pelo usuário")
                        return False
                else:
                    print(f"⚠️ URL não reconhecida: {current_url}")
                    response = input("   Continuar mesmo assim? (s/n): ")
                    if response.lower() != 's':
                        print("❌ Cancelado pelo usuário")
                        return False
            
            # Salva o storage state completo (cookies + localStorage + sessionStorage)
            print("\n💾 Salvando storage state da sessão (cookies + localStorage + sessionStorage)...")
            storage_state = context.storage_state()
            
            from utils.looker_storage import save_storage_state, save_cookies
            save_storage_state(storage_state)
            
            # Também salva apenas cookies para compatibilidade
            cookies = context.cookies()
            save_cookies(cookies)
            
            print(f"✅ Cookies salvos com sucesso!")
            print("\n" + "="*60)
            print("✅ CONFIGURAÇÃO CONCLUÍDA!")
            print("="*60)
            print("💡 Agora o sistema pode usar esses cookies automaticamente")
            print("   Os cookies serão reutilizados até expirarem")
            print("   Se expirarem, execute este script novamente")
            print("="*60)
            
            # Mantém navegador aberto por alguns segundos
            print("\n⏳ Fechando navegador em 5 segundos...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            try:
                browser.close()
            except:
                pass

if __name__ == "__main__":
    success = setup_looker_session()
    if success:
        print("\n✅ Sessão configurada com sucesso!")
    else:
        print("\n❌ Falha ao configurar sessão")

