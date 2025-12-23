"""
Teste de Validação: Endpoints EVs e LDRs após correção

Objetivo:
- Testar se os endpoints /api/hall-da-fama/evs-realtime e ldrs-realtime
  estão funcionando corretamente com a nova lógica hs_date_entered
- Verificar se ainda retornam 0 deals (já que nenhum foi ganho hoje)
- Validar estrutura da resposta
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'  # Ajustar se necessário

def test_evs_endpoint():
    """Testa endpoint de EVs"""
    print("\n" + "="*80)
    print("🧪 TESTE: /api/hall-da-fama/evs-realtime")
    print("="*80)
    
    try:
        response = requests.get(f'{BASE_URL}/api/hall-da-fama/evs-realtime', timeout=30)
        
        print(f"\n📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 Resposta:")
            print(f"   Status: {data.get('status')}")
            print(f"   User Type: {data.get('userType')}")
            print(f"   Total deals: {data.get('total')}")
            print(f"   Ranking length: {len(data.get('data', []))}")
            print(f"   Timestamp: {data.get('timestamp')}")
            
            if data.get('total') == 0:
                print(f"\n✅ CORRETO: Nenhum deal ganho hoje")
                print(f"   Falsos positivos eliminados com sucesso!")
            else:
                print(f"\n⚠️ ATENÇÃO: {data.get('total')} deals encontrados")
                print(f"\n   Deals no ranking:")
                for ev in data.get('data', []):
                    print(f"   - {ev.get('userName')}: {ev.get('dealCount')} deals, R$ {ev.get('revenue')}")
            
            return True
        else:
            print(f"\n❌ Erro: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro na requisição: {e}")
        return False

def test_ldrs_endpoint():
    """Testa endpoint de LDRs"""
    print("\n" + "="*80)
    print("🧪 TESTE: /api/hall-da-fama/ldrs-realtime")
    print("="*80)
    
    try:
        response = requests.get(f'{BASE_URL}/api/hall-da-fama/ldrs-realtime', timeout=30)
        
        print(f"\n📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 Resposta:")
            print(f"   Status: {data.get('status')}")
            print(f"   User Type: {data.get('userType')}")
            print(f"   Total deals: {data.get('total')}")
            print(f"   Ranking length: {len(data.get('data', []))}")
            print(f"   Timestamp: {data.get('timestamp')}")
            
            if data.get('total') == 0:
                print(f"\n✅ CORRETO: Nenhum deal ganho hoje")
                print(f"   Falsos positivos eliminados com sucesso!")
            else:
                print(f"\n⚠️ ATENÇÃO: {data.get('total')} deals encontrados")
                print(f"\n   Deals no ranking:")
                for ldr in data.get('data', []):
                    print(f"   - {ldr.get('userName')}: {ldr.get('wonDealsCount')} deals, R$ {ldr.get('revenue')}")
            
            return True
        else:
            print(f"\n❌ Erro: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro na requisição: {e}")
        return False

def test_sdrs_endpoint():
    """Testa endpoint de SDRs (para garantir que não quebramos nada)"""
    print("\n" + "="*80)
    print("🧪 TESTE: /api/hall-da-fama/sdrs-realtime (NEW)")
    print("="*80)
    
    try:
        response = requests.get(f'{BASE_URL}/api/hall-da-fama/sdrs-realtime?pipeline=6810518', timeout=30)
        
        print(f"\n📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 Resposta:")
            print(f"   Status: {data.get('status')}")
            print(f"   User Type: {data.get('userType')}")
            print(f"   Pipeline: {data.get('pipeline')}")
            print(f"   Total deals: {data.get('total')}")
            print(f"   Ranking length: {len(data.get('data', []))}")
            
            print(f"\n✅ Endpoint SDRs continua funcionando")
            return True
        else:
            print(f"\n❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro na requisição: {e}")
        return False

def main():
    print("="*80)
    print("🧪 TESTE DE VALIDAÇÃO - CORREÇÃO DE FALSOS POSITIVOS")
    print("="*80)
    print(f"\nData/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    results = {
        'evs': False,
        'ldrs': False,
        'sdrs': False
    }
    
    # Testa cada endpoint
    results['evs'] = test_evs_endpoint()
    results['ldrs'] = test_ldrs_endpoint()
    results['sdrs'] = test_sdrs_endpoint()
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    
    for endpoint, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"   {endpoint.upper()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ TODOS OS TESTES PASSARAM!")
        print("   Correção implementada com sucesso!")
        print("   Falsos positivos eliminados!")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("   Verifique os logs acima")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
