"""
Teste: Validar se hs_v2_date_entered funciona corretamente
"""

import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_TOKEN = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
BRAZIL_TZ_OFFSET = timedelta(hours=-3)

def get_today_brazil_start_utc():
    """Retorna 00:00 de hoje Brasil em UTC"""
    now_utc = datetime.now(timezone.utc)
    now_brazil = now_utc + BRAZIL_TZ_OFFSET
    start_of_today_brazil = now_brazil.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_today_utc = start_of_today_brazil - BRAZIL_TZ_OFFSET
    return start_of_today_utc

def test_v2_property():
    """Testa busca com hs_v2_date_entered_13487286"""
    
    today_start_utc = get_today_brazil_start_utc()
    today_start_ms = int(today_start_utc.timestamp() * 1000)
    tomorrow_start_utc = today_start_utc + timedelta(days=1)
    tomorrow_start_ms = int(tomorrow_start_utc.timestamp() * 1000)
    
    print("=" * 80)
    print("🔍 TESTANDO COM PROPRIEDADE CORRETA: hs_v2_date_entered_13487286")
    print("=" * 80)
    print(f"\n📅 Hoje Brasil: {today_start_utc + BRAZIL_TZ_OFFSET}")
    print(f"📅 Range UTC: {today_start_ms} - {tomorrow_start_ms}\n")
    
    url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
    headers = {
        'Authorization': f'Bearer {HUBSPOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Buscar deals que entraram em Ganho (Expansão) hoje
    payload = {
        "filterGroups": [{
            "filters": [
                {"propertyName": "hs_v2_date_entered_13487286", "operator": "GTE", "value": str(today_start_ms)},
                {"propertyName": "hs_v2_date_entered_13487286", "operator": "LT", "value": str(tomorrow_start_ms)},
                {"propertyName": "dealstage", "operator": "EQ", "value": "13487286"}
            ]
        }],
        "properties": [
            "dealname", 
            "dealstage", 
            "closedate",
            "hs_v2_date_entered_13487286",
            "analista_comercial"
        ],
        "limit": 100
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    deals = data.get('results', [])
    
    print(f"✅ {len(deals)} deals encontrados que entraram em Ganho (Expansão) HOJE\n")
    
    if deals:
        print("📋 DEALS ENCONTRADOS:")
        print("=" * 80)
        for deal in deals:
            props = deal['properties']
            date_entered = props.get('hs_v2_date_entered_13487286')
            
            # Converter para horário Brasil
            if date_entered:
                dt = datetime.fromisoformat(date_entered.replace('Z', '+00:00'))
                dt_brazil = dt + BRAZIL_TZ_OFFSET
                time_str = dt_brazil.strftime('%H:%M:%S')
            else:
                time_str = "N/A"
            
            print(f"\nDeal ID: {deal['id']}")
            print(f"  Nome: {props.get('dealname', 'N/A')[:60]}")
            print(f"  Entrou em Ganho às: {time_str} (GMT-3)")
            print(f"  Analista: {props.get('analista_comercial', 'N/A')}")
            print(f"  Close Date: {props.get('closedate', 'N/A')}")
    else:
        print("ℹ️  Nenhum deal entrou em Ganho (Expansão) hoje ainda")
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 80)

if __name__ == "__main__":
    test_v2_property()
