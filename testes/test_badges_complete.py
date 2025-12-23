"""
Script de teste completo para validar a implementação de badges
Testa todos os endpoints e funcionalidades
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*70)
    print(f"🧪 {title}")
    print("="*70)

def test_endpoint(name, endpoint, params=None):
    """Testa um endpoint"""
    print(f"\n📡 Testando: {name}")
    print(f"   Endpoint: {endpoint}")
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Resposta OK")
            
            # Mostra preview dos dados
            if isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], list):
                    print(f"   Registros: {len(data['data'])}")
                    if len(data['data']) > 0:
                        print(f"   Primeiro registro: {json.dumps(data['data'][0], indent=2, ensure_ascii=False)[:200]}...")
                elif 'recordes' in data:
                    print(f"   Recordes encontrados: {len(data['recordes'])}")
                    for key, value in data['recordes'].items():
                        print(f"     {key}: {value}")
                elif 'stats' in data:
                    print(f"   Estatísticas: {json.dumps(data['stats'], indent=2, ensure_ascii=False)[:300]}...")
                else:
                    print(f"   Dados: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
            
            return True, data
        else:
            print(f"   ❌ Erro: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
        return False, None

def run_all_tests():
    """Executa todos os testes"""
    print("="*70)
    print("🚀 TESTE COMPLETO - BADGES DESBLOQUEADOS")
    print("="*70)
    print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    
    resultados = []
    
    # Teste 1: Hall da Fama - EVs
    print_header("Teste 1: Hall da Fama - EVs")
    sucesso, data = test_endpoint(
        "EVs Realtime",
        "/api/hall-da-fama/evs-realtime"
    )
    resultados.append(("Hall da Fama EVs", sucesso))
    
    # Teste 2: Hall da Fama - SDRs NEW
    print_header("Teste 2: Hall da Fama - SDRs NEW")
    sucesso, data = test_endpoint(
        "SDRs NEW Realtime",
        "/api/hall-da-fama/sdrs-realtime",
        params={'pipeline': '6810518'}
    )
    resultados.append(("Hall da Fama SDRs NEW", sucesso))
    
    # Teste 3: Hall da Fama - SDRs Expansão
    print_header("Teste 3: Hall da Fama - SDRs Expansão")
    sucesso, data = test_endpoint(
        "SDRs Expansão Realtime",
        "/api/hall-da-fama/sdrs-realtime",
        params={'pipeline': '4007305'}
    )
    resultados.append(("Hall da Fama SDRs Expansão", sucesso))
    
    # Teste 4: Hall da Fama - LDRs
    print_header("Teste 4: Hall da Fama - LDRs")
    sucesso, data = test_endpoint(
        "LDRs Realtime",
        "/api/hall-da-fama/ldrs-realtime"
    )
    resultados.append(("Hall da Fama LDRs", sucesso))
    
    # Teste 5: Recordes
    print_header("Teste 5: Recordes da Black November")
    sucesso, data = test_endpoint(
        "Recordes",
        "/api/recordes"
    )
    resultados.append(("Recordes", sucesso))
    
    # Teste 6: MVP da Semana
    print_header("Teste 6: MVP da Semana")
    sucesso, data = test_endpoint(
        "MVP Semana",
        "/api/mvp-semana"
    )
    resultados.append(("MVP Semana", sucesso))
    
    # Teste 7: Estatísticas de Badges
    print_header("Teste 7: Estatísticas de Badges")
    sucesso, data = test_endpoint(
        "Stats Badges",
        "/api/badges/stats"
    )
    resultados.append(("Estatísticas Badges", sucesso))
    
    # Teste 8: Badges de Usuário (se houver dados)
    print_header("Teste 8: Badges de Usuário Específico")
    print("   ℹ️  Teste opcional - requer user_type e user_id")
    print("   Formato: /api/badges/user/<user_type>/<user_id>?filter=today")
    print("   Exemplo: /api/badges/user/EV/123456?filter=today")
    
    # Resumo
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    sucessos = sum(1 for _, sucesso in resultados if sucesso)
    falhas = len(resultados) - sucessos
    
    for nome, sucesso in resultados:
        status = "✅" if sucesso else "❌"
        print(f"  {status} {nome}")
    
    print(f"\n✅ Sucessos: {sucessos}/{len(resultados)}")
    if falhas > 0:
        print(f"❌ Falhas: {falhas}/{len(resultados)}")
    
    print(f"\n⏰ Fim: {datetime.now().strftime('%H:%M:%S')}")
    
    # Recomendações
    print("\n" + "="*70)
    print("💡 PRÓXIMOS PASSOS")
    print("="*70)
    
    if sucessos == len(resultados):
        print("\n✅ Todos os testes passaram!")
        print("\n📋 Checklist de validação:")
        print("  1. ✅ Endpoints de Hall da Fama funcionando")
        print("  2. ✅ Endpoint de Recordes funcionando")
        print("  3. ✅ Endpoint de MVP funcionando")
        print("  4. ✅ Endpoint de Estatísticas funcionando")
        print("\n🎉 Sistema de badges totalmente operacional!")
        print("\n🌐 Acesse o Hall da Fama:")
        print(f"   {BASE_URL}/hall-da-fama")
    else:
        print("\n⚠️ Alguns testes falharam!")
        print("\n🔍 Verifique:")
        print("  1. Flask está rodando? (python app.py)")
        print("  2. Banco de dados acessível?")
        print("  3. Tabela badges_desbloqueados existe? (python setup_badges.py)")
        print("  4. Dados populados? (python populate_badges.py)")
    
    return sucessos == len(resultados)

if __name__ == '__main__':
    print("\n⚠️  PRÉ-REQUISITOS:")
    print("  1. Flask rodando (python app.py)")
    print("  2. Tabela criada (python setup_badges.py)")
    print("  3. Dados populados (python populate_badges.py)")
    print("\n")
    
    input("Pressione ENTER para iniciar os testes...")
    
    sucesso = run_all_tests()
    
    if sucesso:
        print("\n✅ TODOS OS TESTES PASSARAM! 🎉")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
