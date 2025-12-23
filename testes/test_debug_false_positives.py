"""
Script de Debug para Investigar Falsos Positivos no Hall da Fama

Problema Identificado:
- Hall da Fama mostra 3 deals ganhos hoje
- Sistema de celebração NÃO enviou notificações
- Webhook NÃO recebeu payload do HubSpot

Possíveis causas:
1. Filtro de closedate pegando deals de dias anteriores (problema de timezone?)
2. Deals em estágios incorretos sendo contabilizados
3. Deals arquivados/deletados sendo incluídos
4. Deals com closedate null ou inválida
5. Conversão de timestamp UTC->Brasil incorreta
6. Deals que mudaram de estágio mas não foram "ganhos" hoje

Estratégia:
- Buscar exatamente os mesmos deals que a API do Hall da Fama está buscando
- Mostrar TODOS os detalhes de cada deal
- Validar cada filtro aplicado
- Comparar com logs do webhook
"""

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

HUBSPOT_TOKEN = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')

# ============================================================================
# FUNÇÕES AUXILIARES (MESMAS DO APP.PY)
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
    try:
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except:
        return datetime.fromtimestamp(int(timestamp) / 1000, tz=timezone.utc)

# ============================================================================
# BUSCAR DEALS EXATAMENTE COMO O HALL DA FAMA FAZ
# ============================================================================

def debug_evs_deals():
    """Busca e analisa deals de EVs EXATAMENTE como o endpoint do Hall da Fama"""
    
    print("\n" + "="*80)
    print("🔍 DEBUG: DEALS DE EVs")
    print("="*80)
    
    # Data de hoje Brasil 00:00 até 23:59:59 em UTC
    today_start_utc = get_today_brazil_start_utc()
    today_start_ms = int(today_start_utc.timestamp() * 1000)
    
    # Data de amanhã Brasil 00:00 em UTC (para pegar até 23:59:59 de hoje)
    tomorrow_start_utc = today_start_utc + timedelta(days=1)
    tomorrow_start_ms = int(tomorrow_start_utc.timestamp() * 1000)
    
    # Horário atual
    now_utc = datetime.now(timezone.utc)
    now_brazil = convert_utc_to_brazil(now_utc)
    
    print(f"\n⏰ Horário Atual:")
    print(f"   UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Brasil: {now_brazil.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📅 Intervalo de Busca:")
    print(f"   Início (Brasil): {convert_utc_to_brazil(today_start_utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Início (UTC): {today_start_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Início (MS): {today_start_ms}")
    print(f"   Fim (Brasil): {convert_utc_to_brazil(tomorrow_start_utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Fim (UTC): {tomorrow_start_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Fim (MS): {tomorrow_start_ms}")
    
    # Request para HubSpot API (EXATAMENTE IGUAL AO APP.PY)
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
                    "6810524",      # Ganho (Vendas NMRR)
                    "13487286",     # Ganho (Expansão)
                    "16657792",     # Faturamento (Vendas NMRR)
                    "180044058",    # Aguardando Correção - Faturamento (Vendas NMRR)
                    "33646228",     # Faturamento (Expansão)
                    "180043078"     # Aguardando Correção - Faturamento (Expansão)
                ]}
            ]
        }],
        "properties": [
            "dealname", 
            "analista_comercial", 
            "closedate", 
            "amount",
            "dealstage",
            "hs_lastmodifieddate",
            "createdate",
            "pipeline",
            "hs_is_closed",
            "hs_is_closed_won"
        ],
        "limit": 100
    }
    
    print(f"\n🔎 Payload da Busca:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"\n❌ Erro na API: {response.status_code}")
            print(response.text)
            return
        
        data = response.json()
        deals = data.get('results', [])
        
        print(f"\n📊 Total de deals encontrados: {len(deals)}")
        
        if len(deals) == 0:
            print("\n✅ NENHUM DEAL ENCONTRADO - Isso está correto se não houve deals ganhos hoje!")
            return
        
        # Analisa cada deal em detalhes
        print("\n" + "="*80)
        print("📋 DETALHAMENTO DOS DEALS")
        print("="*80)
        
        for idx, deal in enumerate(deals, 1):
            props = deal.get('properties', {})
            deal_id = deal.get('id')
            
            print(f"\n{'─'*80}")
            print(f"DEAL #{idx} - ID: {deal_id}")
            print(f"{'─'*80}")
            
            # Informações básicas
            dealname = props.get('dealname', 'N/A')
            amount = props.get('amount', '0')
            dealstage = props.get('dealstage', 'N/A')
            pipeline = props.get('pipeline', 'N/A')
            owner_id = props.get('analista_comercial', 'N/A')
            
            print(f"📝 Nome: {dealname}")
            print(f"💰 Valor: R$ {amount}")
            print(f"🎯 Stage: {dealstage}")
            print(f"📊 Pipeline: {pipeline}")
            print(f"👤 Owner ID: {owner_id}")
            
            # Datas importantes
            closedate = props.get('closedate')
            createdate = props.get('createdate')
            lastmodified = props.get('hs_lastmodifieddate')
            
            print(f"\n📅 Timestamps:")
            
            if closedate:
                dt_utc = parse_hubspot_timestamp(closedate)
                dt_brazil = convert_utc_to_brazil(dt_utc)
                print(f"   Close Date (UTC): {dt_utc.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Close Date (Brasil): {dt_brazil.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Close Date (Raw): {closedate}")
                
                # Verifica se está realmente dentro do intervalo de HOJE
                if dt_brazil.date() == now_brazil.date():
                    print(f"   ✅ ESTÁ NO DIA DE HOJE (Brasil)")
                else:
                    print(f"   ⚠️ NÃO ESTÁ NO DIA DE HOJE! Data: {dt_brazil.date()} vs Hoje: {now_brazil.date()}")
            else:
                print(f"   Close Date: NULL ⚠️")
            
            if createdate:
                dt_utc = parse_hubspot_timestamp(createdate)
                dt_brazil = convert_utc_to_brazil(dt_utc)
                print(f"   Create Date (Brasil): {dt_brazil.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if lastmodified:
                dt_utc = parse_hubspot_timestamp(lastmodified)
                dt_brazil = convert_utc_to_brazil(dt_utc)
                print(f"   Last Modified (Brasil): {dt_brazil.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Status do deal
            is_closed = props.get('hs_is_closed')
            is_closed_won = props.get('hs_is_closed_won')
            
            print(f"\n🔒 Status:")
            print(f"   Is Closed: {is_closed}")
            print(f"   Is Closed Won: {is_closed_won}")
            
            # Link para o deal
            print(f"\n🔗 Link: https://app.hubspot.com/contacts/7024919/deal/{deal_id}")
            
            # ANÁLISE CRÍTICA
            print(f"\n🧪 Análise Crítica:")
            
            warnings = []
            
            # 1. Verifica se closedate é realmente de hoje
            if closedate:
                dt_brazil = convert_utc_to_brazil(parse_hubspot_timestamp(closedate))
                if dt_brazil.date() != now_brazil.date():
                    warnings.append(f"⚠️ CLOSEDATE NÃO É DE HOJE! ({dt_brazil.date()})")
            else:
                warnings.append("⚠️ CLOSEDATE É NULL!")
            
            # 2. Verifica se foi modificado hoje (possível mudança de estágio)
            if lastmodified:
                dt_brazil = convert_utc_to_brazil(parse_hubspot_timestamp(lastmodified))
                if dt_brazil.date() == now_brazil.date():
                    warnings.append(f"⚠️ Deal foi MODIFICADO hoje às {dt_brazil.strftime('%H:%M:%S')} - Pode ter mudado de estágio!")
            
            # 3. Verifica se está nos estágios corretos
            valid_stages = ["6810524", "13487286", "16657792", "180044058", "33646228", "180043078"]
            if dealstage not in valid_stages:
                warnings.append(f"⚠️ STAGE INVÁLIDO: {dealstage}")
            
            if warnings:
                for warning in warnings:
                    print(f"   {warning}")
            else:
                print(f"   ✅ Deal parece estar correto")
        
        # Resumo
        print("\n" + "="*80)
        print("📊 RESUMO DA ANÁLISE")
        print("="*80)
        print(f"Total de deals retornados: {len(deals)}")
        print(f"\n💡 CONCLUSÃO:")
        print(f"Se esses {len(deals)} deals NÃO geraram notificação de celebração,")
        print(f"verifique:")
        print(f"1. Se o closedate deles é realmente de HOJE")
        print(f"2. Se eles foram criados/modificados HOJE mas closedate é antigo")
        print(f"3. Se o webhook está configurado para os stages corretos")
        print(f"4. Se há algum filtro adicional no sistema de celebração")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

# ============================================================================
# COMPARAR COM WEBHOOK
# ============================================================================

def check_webhook_configuration():
    """Verifica se há diferença entre filtros do Hall da Fama e do Webhook"""
    
    print("\n" + "="*80)
    print("🔍 COMPARAÇÃO: HALL DA FAMA vs WEBHOOK")
    print("="*80)
    
    print("\n📊 HALL DA FAMA - Estágios considerados:")
    hall_stages = [
        "6810524",      # Ganho (Vendas NMRR)
        "13487286",     # Ganho (Expansão)
        "16657792",     # Faturamento (Vendas NMRR)
        "180044058",    # Aguardando Correção - Faturamento (Vendas NMRR)
        "33646228",     # Faturamento (Expansão)
        "180043078"     # Aguardando Correção - Faturamento (Expansão)
    ]
    for stage in hall_stages:
        print(f"   - {stage}")
    
    print("\n🔔 WEBHOOK (Sistema de Celebração):")
    print("   Estágios que DEVERIAM gerar notificação:")
    webhook_stages = [
        "6810524",      # Ganho (Vendas NMRR)
        "13487286"      # Ganho (Expansão)
    ]
    for stage in webhook_stages:
        print(f"   - {stage}")
    
    print("\n⚠️ DISCREPÂNCIA IDENTIFICADA:")
    print("   O Hall da Fama está contando deals em estágios de FATURAMENTO,")
    print("   mas o webhook só notifica deals em estágios de GANHO!")
    print("")
    print("   Estágios contados mas NÃO notificados:")
    extra_stages = [
        "16657792",     # Faturamento (Vendas NMRR)
        "180044058",    # Aguardando Correção - Faturamento (Vendas NMRR)
        "33646228",     # Faturamento (Expansão)
        "180043078"     # Aguardando Correção - Faturamento (Expansão)
    ]
    for stage in extra_stages:
        print(f"   - {stage}")
    
    print("\n💡 PROVÁVEL CAUSA DO FALSO POSITIVO:")
    print("   Deals que já estavam em 'Faturamento' com closedate antigo")
    print("   estão sendo contabilizados porque o filtro usa closedate,")
    print("   mas podem ter sido ganhos em dias anteriores!")

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*80)
    print("🔍 DEBUG DE FALSOS POSITIVOS - HALL DA FAMA")
    print("="*80)
    
    # 1. Debug dos deals de EVs
    debug_evs_deals()
    
    # 2. Verifica configuração do webhook
    check_webhook_configuration()
    
    print("\n" + "="*80)
    print("✅ Debug concluído!")
    print("="*80)

if __name__ == '__main__':
    main()
