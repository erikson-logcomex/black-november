"""
Script para popular badges chamando os endpoints de real-time
e salvando no banco de dados
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def call_endpoint_and_save(endpoint, params=None):
    """Chama endpoint e salva badges no banco"""
    try:
        print(f"\n📡 Chamando {endpoint}...")
        response = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                ranking = data.get('data', [])
                user_type = data.get('userType')
                
                print(f"✅ Resposta recebida: {len(ranking)} usuários")
                
                # Salva badges de cada usuário
                badges_salvos = 0
                for user in ranking:
                    user_id = user.get('userId')
                    user_name = user.get('userName')
                    badges = user.get('badges', [])
                    
                    if badges:
                        print(f"  → {user_name}: {len(badges)} badges detectados")
                        
                        # Os badges já foram salvos pelo endpoint
                        # Esta função é apenas para trigger e verificação
                        badges_salvos += len(badges)
                
                print(f"✅ Total de badges processados: {badges_salvos}")
                return True
            else:
                print(f"⚠️ Status não é success: {data.get('status')}")
                return False
        else:
            print(f"❌ Status code: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao chamar endpoint: {e}")
        return False

def populate_all_badges():
    """Popula badges de todos os perfis"""
    print("="*70)
    print("🚀 POPULANDO BADGES - HALL DA FAMA")
    print("="*70)
    print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    
    endpoints = [
        {
            'name': 'EVs',
            'endpoint': '/api/hall-da-fama/evs-realtime',
            'params': None
        },
        {
            'name': 'SDRs NEW',
            'endpoint': '/api/hall-da-fama/sdrs-realtime',
            'params': {'pipeline': '6810518'}
        },
        {
            'name': 'SDRs Expansão',
            'endpoint': '/api/hall-da-fama/sdrs-realtime',
            'params': {'pipeline': '4007305'}
        },
        {
            'name': 'LDRs',
            'endpoint': '/api/hall-da-fama/ldrs-realtime',
            'params': None
        }
    ]
    
    resultados = []
    
    for config in endpoints:
        print(f"\n{'='*70}")
        print(f"📊 Processando: {config['name']}")
        print('='*70)
        
        sucesso = call_endpoint_and_save(config['endpoint'], config['params'])
        resultados.append({
            'name': config['name'],
            'sucesso': sucesso
        })
        
        # Aguarda 2 segundos entre chamadas
        time.sleep(2)
    
    # Resumo
    print("\n" + "="*70)
    print("📊 RESUMO")
    print("="*70)
    
    sucessos = sum(1 for r in resultados if r['sucesso'])
    falhas = len(resultados) - sucessos
    
    for r in resultados:
        status = "✅" if r['sucesso'] else "❌"
        print(f"  {status} {r['name']}")
    
    print(f"\n✅ Sucessos: {sucessos}/{len(resultados)}")
    if falhas > 0:
        print(f"❌ Falhas: {falhas}/{len(resultados)}")
    
    print(f"\n⏰ Fim: {datetime.now().strftime('%H:%M:%S')}")
    
    # Verificar badges salvos
    verify_saved_badges()
    
    return sucessos == len(resultados)

def verify_saved_badges():
    """Verifica badges salvos via API"""
    print("\n" + "="*70)
    print("🔍 VERIFICANDO BADGES SALVOS")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/badges/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                stats = data.get('stats', {})
                
                print(f"\n📊 Estatísticas:")
                print(f"  Badges hoje: {stats.get('badges_hoje', 0)}")
                print(f"  Badges na semana: {stats.get('badges_semana', 0)}")
                
                por_categoria = stats.get('por_categoria_hoje', {})
                if por_categoria:
                    print(f"\n  Por categoria (hoje):")
                    for categoria, total in por_categoria.items():
                        print(f"    {categoria}: {total}")
                
                top_usuarios = stats.get('top_usuarios_hoje', [])
                if top_usuarios:
                    print(f"\n  Top usuários (hoje):")
                    for idx, user in enumerate(top_usuarios, 1):
                        print(f"    {idx}º {user['user_name']} ({user['user_type']}): {user['total_badges']} badges")
                
                return True
            else:
                print(f"⚠️ Status não é success")
                return False
        else:
            print(f"❌ Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar badges: {e}")
        return False

if __name__ == '__main__':
    print("\n⚠️  IMPORTANTE: Certifique-se que o Flask está rodando!")
    print("   python app.py\n")
    
    input("Pressione ENTER para continuar...")
    
    sucesso = populate_all_badges()
    
    if sucesso:
        print("\n" + "="*70)
        print("✅ TODOS OS BADGES FORAM POPULADOS COM SUCESSO!")
        print("="*70)
        print("\n💡 Próximos passos:")
        print("  1. Acesse http://localhost:5000/hall-da-fama")
        print("  2. Verifique os badges nos cards dos MVPs")
        print("  3. Confira os recordes: http://localhost:5000/api/recordes")
    else:
        print("\n" + "="*70)
        print("⚠️ ALGUNS ENDPOINTS FALHARAM")
        print("="*70)
        print("\n💡 Verifique:")
        print("  1. Flask está rodando?")
        print("  2. Banco de dados está acessível?")
        print("  3. Variáveis de ambiente configuradas?")
