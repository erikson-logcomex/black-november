"""
Debug: Por que deals que entraram em Ganho HOJE não aparecem?

Hipóteses:
1. Deals podem estar em stages DIFERENTES de 6810524 e 13487286
2. Propriedade hs_date_entered pode estar vazia/null
3. Deals podem ter mudado de stage depois
4. Timezone pode estar afetando o filtro
"""

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

HUBSPOT_TOKEN = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')

def get_today_brazil_start_utc():
    """Retorna o início do dia no Brasil (00:00 GMT-3) convertido para UTC"""
    BRAZIL_TZ_OFFSET = timedelta(hours=-3)
    now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
    today_brazil_start = now_brazil.replace(hour=0, minute=0, second=0, microsecond=0)
    today_brazil_start_utc = today_brazil_start - BRAZIL_TZ_OFFSET
    return today_brazil_start_utc

def convert_utc_to_brazil(dt_utc):
    """Converte datetime UTC para horário do Brasil (GMT-3)"""
    BRAZIL_TZ_OFFSET = timedelta(hours=-3)
    return dt_utc + BRAZIL_TZ_OFFSET

def parse_hubspot_timestamp(timestamp):
    """Parse timestamp ISO 8601 ou milliseconds do HubSpot"""
    if not timestamp:
        return None
    try:
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except:
        try:
            return datetime.fromtimestamp(int(timestamp) / 1000, tz=timezone.utc)
        except:
            return None

def search_deals_entered_today_expansao():
    """Busca TODOS os deals que PODEM ter entrado em Ganho (Expansão) hoje"""
    
    print("\n" + "="*80)
    print("🔍 BUSCANDO DEALS QUE ENTRARAM EM GANHO (EXPANSÃO) HOJE")
    print("="*80)
    
    today_start_utc = get_today_brazil_start_utc()
    today_start_ms = int(today_start_utc.timestamp() * 1000)
    
    tomorrow_start_utc = today_start_utc + timedelta(days=1)
    tomorrow_start_ms = int(tomorrow_start_utc.timestamp() * 1000)
    
    now_brazil = convert_utc_to_brazil(datetime.now(timezone.utc))
    
    print(f"\n📅 Intervalo de busca (Brasil):")
    print(f"   Início: {convert_utc_to_brazil(today_start_utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Fim: {convert_utc_to_brazil(tomorrow_start_utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Agora: {now_brazil.strftime('%Y-%m-%d %H:%M:%S')}")
    
    url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
    headers = {
        'Authorization': f'Bearer {HUBSPOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Busca 1: Com filtro de hs_date_entered_13487286 E stage atual = 13487286
    print(f"\n🔎 Busca 1: hs_date_entered_13487286 HOJE + Stage ATUAL = 13487286")
    payload1 = {
        "filterGroups": [{
            "filters": [
                {"propertyName": "hs_date_entered_13487286", "operator": "GTE", "value": str(today_start_ms)},
                {"propertyName": "hs_date_entered_13487286", "operator": "LT", "value": str(tomorrow_start_ms)},
                {"propertyName": "dealstage", "operator": "EQ", "value": "13487286"}
            ]
        }],
        "properties": [
            "dealname",
            "analista_comercial",
            "dealstage",
            "amount",
            "hs_date_entered_13487286",
            "closedate",
            "hs_lastmodifieddate"
        ],
        "limit": 100
    }
    
    response1 = requests.post(url, headers=headers, json=payload1)
    deals1 = []
    if response1.status_code == 200:
        deals1 = response1.json().get('results', [])
        print(f"   ✅ {len(deals1)} deals encontrados")
    else:
        print(f"   ❌ Erro: {response1.status_code}")
    
    # Busca 2: Sem filtro de stage (para ver se deals mudaram de stage)
    print(f"\n🔎 Busca 2: hs_date_entered_13487286 HOJE (SEM filtro de stage atual)")
    payload2 = {
        "filterGroups": [{
            "filters": [
                {"propertyName": "hs_date_entered_13487286", "operator": "GTE", "value": str(today_start_ms)},
                {"propertyName": "hs_date_entered_13487286", "operator": "LT", "value": str(tomorrow_start_ms)}
            ]
        }],
        "properties": [
            "dealname",
            "analista_comercial",
            "dealstage",
            "amount",
            "hs_date_entered_13487286",
            "closedate",
            "hs_lastmodifieddate"
        ],
        "limit": 100
    }
    
    response2 = requests.post(url, headers=headers, json=payload2)
    deals2 = []
    if response2.status_code == 200:
        deals2 = response2.json().get('results', [])
        print(f"   ✅ {len(deals2)} deals encontrados")
    else:
        print(f"   ❌ Erro: {response2.status_code}")
    
    # Busca 3: Pipeline Expansão + lastmodified hoje (para ver todos os deals mexidos)
    print(f"\n🔎 Busca 3: Pipeline Expansão + modificado HOJE")
    payload3 = {
        "filterGroups": [{
            "filters": [
                {"propertyName": "pipeline", "operator": "EQ", "value": "4007305"},
                {"propertyName": "hs_lastmodifieddate", "operator": "GTE", "value": str(today_start_ms)}
            ]
        }],
        "properties": [
            "dealname",
            "analista_comercial",
            "dealstage",
            "amount",
            "hs_date_entered_13487286",
            "hs_date_entered_33646228",  # Faturamento Expansão
            "closedate",
            "hs_lastmodifieddate"
        ],
        "limit": 100
    }
    
    response3 = requests.post(url, headers=headers, json=payload3)
    deals3 = []
    if response3.status_code == 200:
        deals3 = response3.json().get('results', [])
        print(f"   ✅ {len(deals3)} deals encontrados")
    else:
        print(f"   ❌ Erro: {response3.status_code}")
    
    # Análise
    print("\n" + "="*80)
    print("📊 ANÁLISE DOS RESULTADOS")
    print("="*80)
    
    if len(deals2) > 0:
        print(f"\n✅ {len(deals2)} deals ENTRARAM em Ganho (Expansão) HOJE:")
        for deal in deals2:
            props = deal.get('properties', {})
            deal_id = deal.get('id')
            dealname = props.get('dealname', 'N/A')
            stage = props.get('dealstage')
            date_entered = props.get('hs_date_entered_13487286')
            
            if date_entered:
                dt = parse_hubspot_timestamp(date_entered)
                if dt:
                    dt_brazil = convert_utc_to_brazil(dt)
                    
                    print(f"\n   Deal ID: {deal_id}")
                    print(f"   Nome: {dealname[:60]}...")
                    print(f"   Stage ATUAL: {stage}")
                    print(f"   Entrou em 13487286 às: {dt_brazil.strftime('%H:%M:%S')} (Brasil)")
                    
                    if stage != "13487286":
                        print(f"   ⚠️ MUDOU DE STAGE! Não está mais em Ganho (Expansão)")
                    else:
                        print(f"   ✅ Ainda está em Ganho (Expansão)")
    
    if len(deals1) != len(deals2):
        print(f"\n⚠️ DISCREPÂNCIA DETECTADA:")
        print(f"   Deals que ENTRARAM hoje: {len(deals2)}")
        print(f"   Deals que ESTÃO no stage hoje: {len(deals1)}")
        print(f"   Diferença: {len(deals2) - len(deals1)} deals MUDARAM de stage!")
    
    return deals1, deals2, deals3

def main():
    print("="*80)
    print("🔍 DEBUG: Por que deals não aparecem no Hall da Fama?")
    print("="*80)
    
    deals1, deals2, deals3 = search_deals_entered_today_expansao()
    
    print("\n" + "="*80)
    print("💡 CONCLUSÃO")
    print("="*80)
    
    if len(deals2) > len(deals1):
        print(f"\n⚠️ PROBLEMA IDENTIFICADO:")
        print(f"   {len(deals2)} deals entraram em Ganho (Expansão) hoje")
        print(f"   Mas apenas {len(deals1)} ainda estão nesse stage")
        print(f"\n   CAUSA: Deals foram movidos para outro stage (ex: Faturamento)")
        print(f"\n   SOLUÇÃO: Remover filtro 'dealstage = 13487286'")
        print(f"   Ou: Aceitar que deals que mudaram de stage não contam")
    elif len(deals1) == 0 and len(deals2) == 0:
        print(f"\n⚠️ PROBLEMA: Propriedade hs_date_entered_13487286 pode estar vazia")
        print(f"   Ou: Intervalo de datas está incorreto")
    else:
        print(f"\n✅ Filtro está correto")
        print(f"   {len(deals1)} deals encontrados")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
