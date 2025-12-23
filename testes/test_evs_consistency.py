"""
Teste de consistência da API de EVs
"""

import requests
import time

print("=" * 80)
print("🔍 TESTE DE CONSISTÊNCIA - API EVS")
print("=" * 80)

for i in range(5):
    print(f"\n📊 Teste #{i+1}")
    try:
        r = requests.get('http://localhost:5000/api/hall-da-fama/evs-realtime')
        data = r.json()
        
        if 'data' in data:
            evs = data['data']
            print(f"   Total de EVs: {len(evs)}")
            print(f"   EVs encontrados:")
            for ev in evs:
                print(f"      - {ev['userName']}: {ev['dealCount']} deals, R$ {ev['revenue']:,.2f}")
        else:
            print(f"   ❌ Resposta sem campo 'data': {data}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    if i < 4:
        time.sleep(1)

print("\n" + "=" * 80)
print("✅ TESTE CONCLUÍDO")
print("=" * 80)
