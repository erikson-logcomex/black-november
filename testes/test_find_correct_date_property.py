"""
Debug: Encontrar a propriedade correta de data para o stage Ganho Expansão
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

def get_deal_all_properties(deal_id):
    """Busca TODAS as propriedades de um deal específico"""
    url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
    
    # Não especificar propriedades retorna todas
    params = {
        "properties": []  # Retorna todas as propriedades
    }
    
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)
        return None
    
    return response.json()


def analyze_date_properties(deal_data):
    """Analisa todas as propriedades relacionadas a datas"""
    props = deal_data['properties']
    
    print("\n" + "=" * 80)
    print(f"📊 TODAS AS PROPRIEDADES DE DATA DO DEAL {deal_data['id']}")
    print("=" * 80)
    
    # Filtrar propriedades que contêm 'date' no nome
    date_props = {k: v for k, v in props.items() if 'date' in k.lower() or 'time' in k.lower()}
    
    # Ordenar por nome
    for prop_name in sorted(date_props.keys()):
        value = date_props[prop_name]
        if value:  # Só mostrar se não for None ou vazio
            print(f"  {prop_name}: {value}")
    
    # Procurar propriedades específicas do stage 13487286
    print("\n" + "=" * 80)
    print("🔍 PROPRIEDADES RELACIONADAS AO STAGE 13487286 (Ganho Expansão)")
    print("=" * 80)
    
    stage_props = {k: v for k, v in props.items() if '13487286' in k}
    
    if stage_props:
        for prop_name, value in sorted(stage_props.items()):
            print(f"  {prop_name}: {value}")
    else:
        print("  ❌ Nenhuma propriedade encontrada com '13487286'")
    
    # Procurar variações possíveis
    print("\n" + "=" * 80)
    print("🔍 VARIAÇÕES DE PROPRIEDADES 'date_entered' E 'dealstage'")
    print("=" * 80)
    
    variations = [
        'hs_date_entered_closedwon',
        'hs_date_entered_closedlost', 
        'hs_date_entered_qualifiedtobuy',
        'hs_date_entered_appointmentscheduled',
        'notes_last_updated',
        'dealstage',
        'hs_lastmodifieddate',
        'closedate'
    ]
    
    for var in variations:
        if var in props:
            print(f"  {var}: {props[var]}")
    
    # Mostrar TODAS as propriedades que começam com 'hs_'
    print("\n" + "=" * 80)
    print("🔍 TODAS AS PROPRIEDADES QUE COMEÇAM COM 'hs_'")
    print("=" * 80)
    
    hs_props = {k: v for k, v in props.items() if k.startswith('hs_') and v}
    
    for prop_name in sorted(hs_props.keys())[:50]:  # Limitar a 50 para não poluir
        value = hs_props[prop_name]
        # Truncar valores muito longos
        if isinstance(value, str) and len(value) > 100:
            value = value[:100] + "..."
        print(f"  {prop_name}: {value}")


def main():
    # Pegar um deal que sabemos que está em Ganho Expansão
    # Vamos usar o primeiro da lista que vimos antes
    test_deals = [
        "44859614012",  # Deal em Ganho Expansão
        "33474562938",  # Outro deal em Ganho Expansão
        "48393761135"   # Mais um deal em Ganho Expansão
    ]
    
    print("=" * 80)
    print("🔍 INSPECIONANDO DEALS EM GANHO EXPANSÃO")
    print("=" * 80)
    
    for deal_id in test_deals:
        print(f"\n{'=' * 80}")
        print(f"📋 DEAL ID: {deal_id}")
        print("=" * 80)
        
        deal_data = get_deal_all_properties(deal_id)
        
        if deal_data:
            analyze_date_properties(deal_data)
        else:
            print(f"❌ Não foi possível carregar o deal {deal_id}")
        
        print("\n\n")


if __name__ == "__main__":
    main()
