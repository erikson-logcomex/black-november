"""
Teste de Validação: hs_date_entered_X vs closedate

Objetivo:
- Comparar resultados usando closedate (ATUAL - com falsos positivos)
- Comparar resultados usando hs_date_entered_<stage_id> (PROPOSTO - sem falsos positivos)
- Validar que a nova abordagem resolve o problema

Casos de teste:
1. Deal ganho hoje → Deve aparecer em AMBAS as abordagens
2. Deal ganho sexta (14/11) mas closedate atualizado hoje → Deve aparecer APENAS em closedate (falso positivo)
3. Deal ganho dias atrás → Não deve aparecer em NENHUMA

Estágios para testar:
- 6810524: Ganho (Vendas NMRR)
- 13487286: Ganho (Expansão)
"""

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

HUBSPOT_TOKEN = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

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

# ============================================================================
# ABORDAGEM 1: CLOSEDATE (ATUAL - COM FALSOS POSITIVOS)
# ============================================================================

def get_deals_by_closedate():
    """Busca deals usando closedate (abordagem ATUAL)"""
    
    print("\n" + "="*80)
    print("🔴 ABORDAGEM 1: CLOSEDATE (ATUAL)")
    print("="*80)
    
    today_start_utc = get_today_brazil_start_utc()
    today_start_ms = int(today_start_utc.timestamp() * 1000)
    
    tomorrow_start_utc = today_start_utc + timedelta(days=1)
    tomorrow_start_ms = int(tomorrow_start_utc.timestamp() * 1000)
    
    url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
    headers = {
        'Authorization': f'Bearer {HUBSPOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "filterGroups": [{
            "filters": [
                {"propertyName": "closedate", "operator": "GTE", "value": str(today_start_ms)},
                {"propertyName": "closedate", "operator": "LT", "value": str(tomorrow_start_ms)},
                {"propertyName": "dealstage", "operator": "IN", "values": [
                    "6810524",   # Ganho (Vendas NMRR)
                    "13487286"   # Ganho (Expansão)
                ]}
            ]
        }],
        "properties": [
            "dealname",
            "analista_comercial",
            "closedate",
            "amount",
            "dealstage",
            "hs_date_entered_6810524",    # Data entrada Ganho NMRR
            "hs_date_entered_13487286",   # Data entrada Ganho Expansão
            "hs_lastmodifieddate",
            "createdate"
        ],
        "limit": 100
    }
    
    print(f"\n🔎 Filtro: closedate >= {convert_utc_to_brazil(today_start_utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"           closedate < {convert_utc_to_brazil(tomorrow_start_utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"           Stage IN [6810524, 13487286]")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"\n❌ Erro: {response.status_code}")
            return []
        
        deals = response.json().get('results', [])
        print(f"\n📊 Total de deals encontrados: {len(deals)}")
        
        return deals
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return []

# ============================================================================
# ABORDAGEM 2: HS_DATE_ENTERED (PROPOSTA - SEM FALSOS POSITIVOS)
# ============================================================================

def get_deals_by_date_entered():
    """Busca deals usando hs_date_entered_X (abordagem PROPOSTA)"""
    
    print("\n" + "="*80)
    print("🟢 ABORDAGEM 2: HS_DATE_ENTERED (PROPOSTA)")
    print("="*80)
    
    today_start_utc = get_today_brazil_start_utc()
    today_start_ms = int(today_start_utc.timestamp() * 1000)
    
    tomorrow_start_utc = today_start_utc + timedelta(days=1)
    tomorrow_start_ms = int(tomorrow_start_utc.timestamp() * 1000)
    
    url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
    headers = {
        'Authorization': f'Bearer {HUBSPOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Busca em 2 etapas (uma para cada stage)
    all_deals = []
    
    # 1. Ganho (Vendas NMRR) - Stage 6810524
    print(f"\n🔎 Buscando Stage 6810524 (Ganho NMRR)...")
    payload_nmrr = {
        "filterGroups": [{
            "filters": [
                {"propertyName": "hs_date_entered_6810524", "operator": "GTE", "value": str(today_start_ms)},
                {"propertyName": "hs_date_entered_6810524", "operator": "LT", "value": str(tomorrow_start_ms)},
                {"propertyName": "dealstage", "operator": "EQ", "value": "6810524"}
            ]
        }],
        "properties": [
            "dealname",
            "analista_comercial",
            "closedate",
            "amount",
            "dealstage",
            "hs_date_entered_6810524",
            "hs_date_entered_13487286",
            "hs_lastmodifieddate",
            "createdate"
        ],
        "limit": 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload_nmrr)
        if response.status_code == 200:
            deals_nmrr = response.json().get('results', [])
            all_deals.extend(deals_nmrr)
            print(f"   ✅ {len(deals_nmrr)} deals encontrados")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Ganho (Expansão) - Stage 13487286
    print(f"\n🔎 Buscando Stage 13487286 (Ganho Expansão)...")
    payload_expansao = {
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
            "closedate",
            "amount",
            "dealstage",
            "hs_date_entered_6810524",
            "hs_date_entered_13487286",
            "hs_lastmodifieddate",
            "createdate"
        ],
        "limit": 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload_expansao)
        if response.status_code == 200:
            deals_expansao = response.json().get('results', [])
            all_deals.extend(deals_expansao)
            print(f"   ✅ {len(deals_expansao)} deals encontrados")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print(f"\n📊 Total de deals encontrados: {len(all_deals)}")
    
    return all_deals

# ============================================================================
# ANÁLISE E COMPARAÇÃO
# ============================================================================

def analyze_deal(deal, method_name):
    """Analisa detalhes de um deal"""
    props = deal.get('properties', {})
    deal_id = deal.get('id')
    
    dealname = props.get('dealname', 'N/A')
    amount = props.get('amount', '0')
    stage = props.get('dealstage', 'N/A')
    owner = props.get('analista_comercial', 'N/A')
    
    closedate = props.get('closedate')
    date_entered_nmrr = props.get('hs_date_entered_6810524')
    date_entered_expansao = props.get('hs_date_entered_13487286')
    lastmodified = props.get('hs_lastmodifieddate')
    createdate = props.get('createdate')
    
    print(f"\n{'─'*80}")
    print(f"Deal ID: {deal_id}")
    print(f"Nome: {dealname[:60]}...")
    print(f"Valor: R$ {amount}")
    print(f"Stage: {stage}")
    print(f"Owner ID: {owner}")
    
    # Datas importantes
    now_brazil = convert_utc_to_brazil(datetime.now(timezone.utc))
    
    print(f"\n📅 Timestamps:")
    
    if closedate:
        dt = parse_hubspot_timestamp(closedate)
        if dt:
            dt_brazil = convert_utc_to_brazil(dt)
            is_today = dt_brazil.date() == now_brazil.date()
            print(f"   closedate: {dt_brazil.strftime('%Y-%m-%d %H:%M:%S')} {'✅ HOJE' if is_today else f'❌ {dt_brazil.date()}'}")
    
    if date_entered_nmrr:
        dt = parse_hubspot_timestamp(date_entered_nmrr)
        if dt:
            dt_brazil = convert_utc_to_brazil(dt)
            is_today = dt_brazil.date() == now_brazil.date()
            print(f"   hs_date_entered_6810524: {dt_brazil.strftime('%Y-%m-%d %H:%M:%S')} {'✅ HOJE' if is_today else f'❌ {dt_brazil.date()}'}")
    
    if date_entered_expansao:
        dt = parse_hubspot_timestamp(date_entered_expansao)
        if dt:
            dt_brazil = convert_utc_to_brazil(dt)
            is_today = dt_brazil.date() == now_brazil.date()
            print(f"   hs_date_entered_13487286: {dt_brazil.strftime('%Y-%m-%d %H:%M:%S')} {'✅ HOJE' if is_today else f'❌ {dt_brazil.date()}'}")
    
    if createdate:
        dt = parse_hubspot_timestamp(createdate)
        if dt:
            dt_brazil = convert_utc_to_brazil(dt)
            print(f"   createdate: {dt_brazil.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if lastmodified:
        dt = parse_hubspot_timestamp(lastmodified)
        if dt:
            dt_brazil = convert_utc_to_brazil(dt)
            is_today = dt_brazil.date() == now_brazil.date()
            print(f"   lastmodified: {dt_brazil.strftime('%Y-%m-%d %H:%M:%S')} {'⚠️ MODIFICADO HOJE' if is_today else ''}")
    
    print(f"\n🔍 Link: https://app.hubspot.com/contacts/7024919/deal/{deal_id}")

def compare_results(deals_closedate, deals_date_entered):
    """Compara resultados das duas abordagens"""
    
    print("\n" + "="*80)
    print("📊 COMPARAÇÃO DE RESULTADOS")
    print("="*80)
    
    ids_closedate = set([d.get('id') for d in deals_closedate])
    ids_date_entered = set([d.get('id') for d in deals_date_entered])
    
    # Deals apenas em closedate (FALSOS POSITIVOS)
    false_positives = ids_closedate - ids_date_entered
    
    # Deals apenas em date_entered (FALSOS NEGATIVOS - improvável)
    false_negatives = ids_date_entered - ids_closedate
    
    # Deals em ambos (VERDADEIROS POSITIVOS)
    true_positives = ids_closedate & ids_date_entered
    
    print(f"\n📈 Estatísticas:")
    print(f"   Total closedate: {len(ids_closedate)}")
    print(f"   Total date_entered: {len(ids_date_entered)}")
    print(f"   Verdadeiros positivos (em ambos): {len(true_positives)}")
    print(f"   Falsos positivos (só em closedate): {len(false_positives)} ⚠️")
    print(f"   Falsos negativos (só em date_entered): {len(false_negatives)}")
    
    # Analisa falsos positivos
    if false_positives:
        print("\n" + "="*80)
        print("⚠️ FALSOS POSITIVOS (aparecem em closedate mas NÃO em date_entered)")
        print("="*80)
        print("Estes deals foram ganhos em dias anteriores mas closedate foi atualizado hoje:")
        
        for deal in deals_closedate:
            if deal.get('id') in false_positives:
                analyze_deal(deal, "FALSO POSITIVO")
    
    # Analisa verdadeiros positivos
    if true_positives:
        print("\n" + "="*80)
        print("✅ VERDADEIROS POSITIVOS (aparecem em AMBAS as abordagens)")
        print("="*80)
        print("Estes deals foram realmente ganhos hoje:")
        
        for deal in deals_date_entered:
            if deal.get('id') in true_positives:
                analyze_deal(deal, "VERDADEIRO POSITIVO")
    
    # Analisa falsos negativos (se houver)
    if false_negatives:
        print("\n" + "="*80)
        print("⚠️ FALSOS NEGATIVOS (aparecem em date_entered mas NÃO em closedate)")
        print("="*80)
        
        for deal in deals_date_entered:
            if deal.get('id') in false_negatives:
                analyze_deal(deal, "FALSO NEGATIVO")

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*80)
    print("🧪 TESTE DE VALIDAÇÃO: closedate vs hs_date_entered")
    print("="*80)
    print(f"\nData/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Busca usando closedate (ATUAL)
    deals_closedate = get_deals_by_closedate()
    
    # 2. Busca usando hs_date_entered (PROPOSTA)
    deals_date_entered = get_deals_by_date_entered()
    
    # 3. Compara resultados
    compare_results(deals_closedate, deals_date_entered)
    
    # 4. Conclusão
    print("\n" + "="*80)
    print("💡 CONCLUSÃO")
    print("="*80)
    
    ids_closedate = set([d.get('id') for d in deals_closedate])
    ids_date_entered = set([d.get('id') for d in deals_date_entered])
    false_positives = ids_closedate - ids_date_entered
    
    if len(false_positives) > 0:
        print(f"\n❌ FALSOS POSITIVOS DETECTADOS: {len(false_positives)}")
        print("   A abordagem com closedate está retornando deals que não foram ganhos hoje!")
        print("\n✅ RECOMENDAÇÃO: Migrar para hs_date_entered_<stage_id>")
    elif len(ids_date_entered) == 0 and len(ids_closedate) == 0:
        print(f"\n✅ Nenhum deal ganho hoje (em ambas abordagens)")
        print("   Ambas as abordagens estão consistentes")
    else:
        print(f"\n✅ Nenhum falso positivo detectado!")
        print("   Ambas as abordagens retornam os mesmos resultados")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
