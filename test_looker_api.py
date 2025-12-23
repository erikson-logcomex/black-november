"""
Script de teste para extrair dados do Looker usando API REST
Esta é a solução recomendada pois não requer 2FA
"""

import os
import requests
from dotenv import load_dotenv
import json

# Carrega variáveis do .env
load_dotenv()

# Configurações
LOOKER_BASE_URL = "https://logcomex.looker.com"
LOOKER_CLIENT_ID = os.getenv('LOOKER_CLIENT_ID', '')
LOOKER_CLIENT_SECRET = os.getenv('LOOKER_CLIENT_SECRET', '')
DASHBOARD_ID = "1197"

def get_looker_access_token():
    """Obtém token de acesso da API do Looker"""
    try:
        print("🔐 Autenticando na API do Looker...")
        
        url = f"{LOOKER_BASE_URL}/api/4.0/login"
        data = {
            'client_id': LOOKER_CLIENT_ID,
            'client_secret': LOOKER_CLIENT_SECRET
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        
        if access_token:
            print("✅ Token de acesso obtido com sucesso!")
            return access_token
        else:
            print("❌ Token de acesso não encontrado na resposta")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao obter token de acesso: {e}")
        if hasattr(e, 'response'):
            print(f"   Resposta: {e.response.text}")
        return None

def get_dashboard_data(access_token, dashboard_id):
    """Obtém dados do dashboard via API"""
    try:
        print(f"📊 Buscando dados do dashboard {dashboard_id}...")
        
        # Busca informações do dashboard
        url = f"{LOOKER_BASE_URL}/api/4.0/dashboards/{dashboard_id}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        dashboard_info = response.json()
        print(f"✅ Dashboard encontrado: {dashboard_info.get('title', 'N/A')}")
        
        # Busca os dados do dashboard (resultados das queries)
        # Nota: Pode ser necessário executar as queries do dashboard
        url_results = f"{LOOKER_BASE_URL}/api/4.0/dashboards/{dashboard_id}/dashboard_filters"
        response_results = requests.get(url_results, headers=headers)
        
        # Tenta buscar os elementos do dashboard
        dashboard_elements = dashboard_info.get('dashboard_elements', [])
        
        gauge_value = None
        gauge_target = 800  # Meta conhecida
        
        # Procura por elementos que possam conter o valor do gauge
        for element in dashboard_elements:
            element_type = element.get('type', '')
            query_id = element.get('query_id')
            
            if query_id:
                # Busca os resultados da query
                try:
                    query_url = f"{LOOKER_BASE_URL}/api/4.0/queries/{query_id}/run/json"
                    query_response = requests.get(query_url, headers=headers)
                    
                    if query_response.status_code == 200:
                        query_data = query_response.json()
                        print(f"📊 Dados da query {query_id}: {query_data}")
                        
                        # Tenta extrair o valor do gauge dos dados
                        # Isso depende da estrutura dos dados retornados
                        if isinstance(query_data, list) and len(query_data) > 0:
                            # Procura por valores numéricos relevantes
                            for row in query_data:
                                for key, value in row.items():
                                    if isinstance(value, (int, float)) and 0 < value < 1000:
                                        if value != 800:  # Ignora a meta
                                            gauge_value = int(value)
                                            break
                except Exception as e:
                    print(f"⚠️ Erro ao buscar dados da query {query_id}: {e}")
                    continue
        
        return {
            'gauge_value': gauge_value,
            'gauge_target': gauge_target,
            'remaining': gauge_target - gauge_value if gauge_value else None,
            'timestamp': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'dashboard_info': dashboard_info
        }
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados do dashboard: {e}")
        if hasattr(e, 'response'):
            print(f"   Resposta: {e.response.text}")
        return None

def main():
    """Função principal"""
    print("🚀 Iniciando teste de extração de dados do Looker via API...")
    
    if not LOOKER_CLIENT_ID or not LOOKER_CLIENT_SECRET:
        print("⚠️ ATENÇÃO: Variáveis de ambiente LOOKER_CLIENT_ID e LOOKER_CLIENT_SECRET não configuradas!")
        print("💡 Para obter essas credenciais:")
        print("   1. Acesse o Looker como administrador")
        print("   2. Vá em Admin > API > API3 Keys")
        print("   3. Crie uma nova chave de API")
        print("   4. Adicione ao .env:")
        print("      LOOKER_CLIENT_ID='seu_client_id'")
        print("      LOOKER_CLIENT_SECRET='seu_client_secret'")
        return
    
    # Obtém token de acesso
    access_token = get_looker_access_token()
    if not access_token:
        print("❌ Falha ao obter token de acesso")
        return
    
    # Busca dados do dashboard
    data = get_dashboard_data(access_token, DASHBOARD_ID)
    
    if data:
        # Salva os resultados
        output_file = 'looker_api_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*50)
        print("📊 RESULTADOS:")
        print("="*50)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*50)
        print(f"💾 Dados salvos em: {output_file}")
    else:
        print("❌ Não foi possível obter os dados do dashboard")

if __name__ == "__main__":
    main()

