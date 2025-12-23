"""
Debug: Inspecionar propriedades dos deals modificados hoje
"""

import os
import requests
from datetime import datetime, timezone, timedelta
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração
HUBSPOT_API_KEY = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
HEADERS = {'Authorization': f'Bearer {HUBSPOT_API_KEY}'}

# Timezone Brasil
BRAZIL_TZ_OFFSET = timedelta(hours=-3)

# Pegar deals do pipeline Expansão que foram modificados hoje
def get_deals_modified_today():
    """Busca deals modificados hoje no pipeline Expansão"""
    # Calcular hoje em Brasil
    now_utc = datetime.now(timezone.utc)
    now_brazil = now_utc + BRAZIL_TZ_OFFSET
    start_of_today_brazil = now_brazil.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_today_utc = start_of_today_brazil - BRAZIL_TZ_OFFSET
    
    print("=" * 80)
    print(f"🔍 BUSCANDO DEALS MODIFICADOS HOJE NO PIPELINE EXPANSÃO")
    print("=" * 80)
    print(f"\n📅 Hoje Brasil: {start_of_today_brazil.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Hoje UTC: {start_of_today_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    
    url = "https://api.hubapi.com/crm/v3/objects/deals/search"
    
    # Buscar todos os deals modificados hoje no pipeline Expansão
    payload = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "pipeline",
                        "operator": "EQ",
                        "value": "4007305"  # Pipeline Expansão
                    },
                    {
                        "propertyName": "hs_lastmodifieddate",
                        "operator": "GTE",
                        "value": int(start_of_today_utc.timestamp() * 1000)
                    }
                ]
            }
        ],
        "properties": [
            "dealname",
            "dealstage",
            "pipeline",
            "closedate",
            "hs_lastmodifieddate",
            "hs_date_entered_13487286",  # Data entrada Ganho Expansão
            "hs_date_exited_13487286",   # Data saída Ganho Expansão
            "hubspot_owner_id"
        ],
        "sorts": [{"propertyName": "hs_lastmodifieddate", "direction": "DESCENDING"}],
        "limit": 100
    }
    
    response = requests.post(url, json=payload, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"\n❌ Erro: {response.status_code}")
        print(response.text)
        return []
    
    data = response.json()
    deals = data.get('results', [])
    
    print(f"\n✅ {len(deals)} deals encontrados")
    return deals


def inspect_deals(deals):
    """Inspeciona as propriedades dos deals"""
    print("\n" + "=" * 80)
    print(f"📊 INSPEÇÃO DETALHADA DOS DEALS")
    print("=" * 80)
    
    # Mapear stage IDs
    STAGE_NAMES = {
        "6810524": "Ganho NMRR",
        "13487286": "Ganho Expansão",
        "16657792": "Faturamento (NEW)",
        "33646228": "Faturamento (Expansão)",
        "180044058": "Faturamento (NEW 2)",
        "180043078": "Faturamento (Expansão 2)"
    }
    
    # Filtrar deals em stage "Ganho" ou "Faturamento"
    relevant_deals = []
    for deal in deals:
        stage = deal['properties'].get('dealstage')
        if stage in ["13487286", "33646228", "180043078"]:
            relevant_deals.append(deal)
    
    print(f"\n📌 Deals em Ganho Expansão ou Faturamento: {len(relevant_deals)}\n")
    
    # Agrupar por stage
    by_stage = {}
    for deal in relevant_deals:
        stage = deal['properties'].get('dealstage', 'N/A')
        stage_name = STAGE_NAMES.get(stage, f"Unknown ({stage})")
        if stage_name not in by_stage:
            by_stage[stage_name] = []
        by_stage[stage_name].append(deal)
    
    # Mostrar resumo por stage
    for stage_name, stage_deals in by_stage.items():
        print(f"\n{'=' * 80}")
        print(f"📍 STAGE: {stage_name}")
        print(f"{'=' * 80}")
        print(f"Total: {len(stage_deals)} deals\n")
        
        for deal in stage_deals[:10]:  # Mostrar apenas os primeiros 10 de cada stage
            props = deal['properties']
            
            print(f"Deal ID: {deal['id']}")
            print(f"  Nome: {props.get('dealname', 'N/A')}")
            print(f"  Stage Atual: {STAGE_NAMES.get(props.get('dealstage'), props.get('dealstage'))}")
            print(f"  Close Date: {props.get('closedate', 'N/A')}")
            print(f"  Modificado: {props.get('hs_lastmodifieddate', 'N/A')}")
            print(f"  ✅ hs_date_entered_13487286: {props.get('hs_date_entered_13487286', '❌ VAZIA')}")
            print(f"  🚪 hs_date_exited_13487286: {props.get('hs_date_exited_13487286', '❌ VAZIA')}")
            print(f"  Owner: {props.get('hubspot_owner_id', 'N/A')}")
            print()
    
    # Estatísticas
    print("\n" + "=" * 80)
    print("📊 ESTATÍSTICAS DAS PROPRIEDADES")
    print("=" * 80)
    
    total = len(relevant_deals)
    with_entered = sum(1 for d in relevant_deals if d['properties'].get('hs_date_entered_13487286'))
    with_exited = sum(1 for d in relevant_deals if d['properties'].get('hs_date_exited_13487286'))
    
    print(f"\nTotal de deals analisados: {total}")
    print(f"Com hs_date_entered_13487286: {with_entered} ({with_entered/total*100:.1f}%)")
    print(f"Com hs_date_exited_13487286: {with_exited} ({with_exited/total*100:.1f}%)")
    
    # Verificar deals que têm data_entered HOJE
    BRAZIL_TZ_OFFSET = timedelta(hours=-3)
    now_utc = datetime.now(timezone.utc)
    now_brazil = now_utc + BRAZIL_TZ_OFFSET
    start_of_today_brazil = now_brazil.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today_brazil = start_of_today_brazil + timedelta(days=1)
    
    deals_entered_today = []
    for deal in relevant_deals:
        date_entered = deal['properties'].get('hs_date_entered_13487286')
        if date_entered:
            try:
                # Converter de string ISO para datetime
                dt = datetime.fromisoformat(date_entered.replace('Z', '+00:00'))
                dt_brazil = dt + BRAZIL_TZ_OFFSET
                
                if start_of_today_brazil <= dt_brazil < end_of_today_brazil:
                    deals_entered_today.append(deal)
            except:
                pass
    
    print(f"\n🎯 Deals que ENTRARAM em Ganho Expansão HOJE: {len(deals_entered_today)}")
    
    if deals_entered_today:
        print("\nDetalhes:")
        for deal in deals_entered_today:
            props = deal['properties']
            date_entered = props.get('hs_date_entered_13487286')
            dt = datetime.fromisoformat(date_entered.replace('Z', '+00:00'))
            dt_brazil = dt + BRAZIL_TZ_OFFSET
            
            print(f"\n  Deal ID: {deal['id']}")
            print(f"    Nome: {props.get('dealname', 'N/A')}")
            print(f"    Stage Atual: {STAGE_NAMES.get(props.get('dealstage'), props.get('dealstage'))}")
            print(f"    Entrou em Ganho: {dt_brazil.strftime('%Y-%m-%d %H:%M:%S')} (Brasil)")
            print(f"    Saiu de Ganho: {props.get('hs_date_exited_13487286', 'Ainda em Ganho')}")


if __name__ == "__main__":
    deals = get_deals_modified_today()
    
    if deals:
        inspect_deals(deals)
    else:
        print("\n❌ Nenhum deal encontrado para inspecionar")
