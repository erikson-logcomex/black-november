"""
Teste simples: Verificar quantos deals aparecem em cada endpoint
"""

import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 80)
print("🧪 TESTE RÁPIDO - HALL DA FAMA")
print("=" * 80)

# Teste EVs
print("\n📊 EVS:")
response = requests.get(f"{BASE_URL}/api/hall-da-fama/evs-realtime")
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ {len(data)} EVs encontrados no ranking")
    print(f"   Resposta: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
else:
    print(f"   ❌ Erro: {response.status_code}")

# Teste LDRs
print("\n📊 LDRs:")
response = requests.get(f"{BASE_URL}/api/hall-da-fama/ldrs-realtime")
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ {len(data)} LDRs encontrados no ranking")
    print(f"   Resposta: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
else:
    print(f"   ❌ Erro: {response.status_code}")

print("\n" + "=" * 80)
print("✅ TESTE CONCLUÍDO")
print("=" * 80)
