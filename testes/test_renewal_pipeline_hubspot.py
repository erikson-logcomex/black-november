"""
Script de teste para buscar deals do pipeline de Renovação (7075777) 
diretamente da API do HubSpot, aplicando os mesmos critérios da query do banco.
"""
import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import json

load_dotenv()

# Configuração
HUBSPOT_API_TOKEN = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
RENEWAL_PIPELINE_ID = '7075777'  # Pipeline de Renovação
RENEWAL_WON_STAGE_ID = '7075780'  # Stage "Ganho" do pipeline de Renovação
BRAZIL_TZ_OFFSET = timedelta(hours=-3)

def get_month_start_brazil_utc():
    """Retorna o início do mês atual (1º dia 00:00) no Brasil (GMT-3) convertido para UTC"""
    now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
    month_start_brazil = now_brazil.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_start_utc = month_start_brazil - BRAZIL_TZ_OFFSET
    return month_start_utc

def get_month_end_brazil_utc():
    """Retorna o fim do mês atual (último dia 23:59:59) no Brasil (GMT-3) convertido para UTC"""
    now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
    # Próximo mês, dia 1, 00:00
    if now_brazil.month == 12:
        next_month = now_brazil.replace(year=now_brazil.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        next_month = now_brazil.replace(month=now_brazil.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    month_end_brazil = next_month - timedelta(seconds=1)  # 23:59:59 do último dia do mês
    month_end_utc = month_end_brazil - BRAZIL_TZ_OFFSET
    return month_end_utc

def parse_hubspot_timestamp(timestamp):
    """Parse timestamp do HubSpot (milliseconds) para datetime UTC"""
    if not timestamp:
        return None
    try:
        # HubSpot retorna em milliseconds
        return datetime.fromtimestamp(int(timestamp) / 1000, tz=timezone.utc)
    except (ValueError, TypeError):
        return None

def adjust_date_to_brazil(utc_datetime):
    """Ajusta datetime UTC para horário do Brasil (GMT-3)"""
    if not utc_datetime:
        return None
    return utc_datetime + BRAZIL_TZ_OFFSET

def fetch_renewal_deals_from_hubspot():
    """
    Busca deals do pipeline de Renovação (7075777) do HubSpot API
    Aplicando os mesmos critérios da query do banco:
    - Pipeline = 7075777 (Renovação)
    - closedate no mês atual (ajustado para Brasil -3h)
    - Deal stage com "ganho", "faturamento" ou "aguardando"
    - tipo_de_receita != 'Pontual'
    - tipo_de_negociacao != 'Variação Cambial'
    - amount > 0
    """
    print("\n" + "="*80)
    print("BUSCANDO DEALS DO PIPELINE DE RENOVACAO (7075777) NO HUBSPOT API")
    print("="*80)
    
    if not HUBSPOT_API_TOKEN:
        print("ERRO: HUBSPOT_PRIVATE_APP_TOKEN nao configurado")
        return []
    
    # Calcula período do mês atual (Brasil)
    month_start_utc = get_month_start_brazil_utc()
    month_end_utc = get_month_end_brazil_utc()
    
    month_start_ms = int(month_start_utc.timestamp() * 1000)
    month_end_ms = int(month_end_utc.timestamp() * 1000)
    
    print(f"\nPeriodo de busca:")
    print(f"   Início: {month_start_utc.strftime('%Y-%m-%d %H:%M:%S UTC')} ({adjust_date_to_brazil(month_start_utc).strftime('%Y-%m-%d %H:%M:%S BRT')})")
    print(f"   Fim: {month_end_utc.strftime('%Y-%m-%d %H:%M:%S UTC')} ({adjust_date_to_brazil(month_end_utc).strftime('%Y-%m-%d %H:%M:%S BRT')})")
    
    url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
    headers = {
        'Authorization': f'Bearer {HUBSPOT_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Busca deals do pipeline de renovação no mês, apenas do stage "Ganho" (7075780)
    RENEWAL_WON_STAGE_ID = '7075780'  # Stage "Ganho" do pipeline de Renovação
    
    payload = {
        "filterGroups": [{
            "filters": [
                {"propertyName": "pipeline", "operator": "EQ", "value": RENEWAL_PIPELINE_ID},
                {"propertyName": "dealstage", "operator": "EQ", "value": RENEWAL_WON_STAGE_ID},
                {"propertyName": "closedate", "operator": "GTE", "value": str(month_start_ms)},
                {"propertyName": "closedate", "operator": "LTE", "value": str(month_end_ms)}
            ]
        }],
        "properties": [
            "dealname",
            "dealstage",
            "closedate",
            "valor_ganho",
            "tipo_de_receita",
            "tipo_de_negociacao",
            "pipeline"
        ],
        "limit": 100
    }
    
    print(f"\nFazendo requisicao para HubSpot API...")
    print(f"   Pipeline: {RENEWAL_PIPELINE_ID} (Renovacao)")
    print(f"   Stage: {RENEWAL_WON_STAGE_ID} (Ganho)")
    
    all_deals = []
    after = None
    page = 1
    
    while True:
        if after:
            payload["after"] = after
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 429:
                print(f"AVISO: Rate limit atingido, aguardando 2 segundos...")
                import time
                time.sleep(2)
                continue
            elif response.status_code != 200:
                print(f"ERRO na API: {response.status_code}")
                print(f"   Resposta: {response.text}")
                break
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                break
            
            print(f"   Pagina {page}: {len(results)} deals encontrados")
            all_deals.extend(results)
            
            # Paginação
            paging = data.get("paging", {})
            after = paging.get("next", {}).get("after")
            
            if not after:
                break
            
            page += 1
            import time
            time.sleep(0.5)  # Delay para evitar rate limit
            
        except Exception as e:
            print(f"ERRO na requisicao: {e}")
            break
    
    print(f"\nTotal de deals encontrados (antes dos filtros): {len(all_deals)}")
    
    # Agora precisamos buscar informações sobre os stages para filtrar
    # Vamos buscar todos os pipelines e filtrar pelo de renovação
    print(f"\nBuscando informacoes de stages do pipeline de Renovacao...")
    pipelines_url = 'https://api.hubapi.com/crm/v3/pipelines/deals'
    pipelines_response = requests.get(pipelines_url, headers=headers)
    
    stages_info = {}
    if pipelines_response.status_code == 200:
        pipelines_data = pipelines_response.json()
        for pipeline in pipelines_data.get('results', []):
            pipeline_id = str(pipeline.get('id'))
            if pipeline_id == RENEWAL_PIPELINE_ID:
                print(f"   Pipeline encontrado: {pipeline.get('label', 'N/A')} (ID: {pipeline_id})")
                for stage in pipeline.get('stages', []):
                    stage_id = str(stage.get('id'))
                    stage_label = stage.get('label', '').lower()
                    stages_info[stage_id] = {
                        'label': stage.get('label'),
                        'label_lower': stage_label
                    }
                break
    
    print(f"\nStages do pipeline de Renovacao encontrados: {len(stages_info)}")
    for stage_id, info in stages_info.items():
        print(f"   - {stage_id}: {info['label']}")
    
    # Filtra deals pelos criterios
    filtered_deals = []
    total_revenue = 0.0
    
    print(f"\nAplicando filtros (mesmos criterios do banco):")
    print(f"   - Pipeline: {RENEWAL_PIPELINE_ID} (Renovacao)")
    print(f"   - Deal stage: {RENEWAL_WON_STAGE_ID} (Ganho)")
    print(f"   - tipo_de_receita != 'Pontual'")
    print(f"   - tipo_de_negociacao != 'Variação Cambial'")
    print(f"   - valor_ganho > 0")
    
    for deal in all_deals:
        props = deal.get('properties', {})
        
        deal_name = props.get('dealname', 'N/A')
        deal_stage_id = props.get('dealstage', '')
        closedate_str = props.get('closedate', '')
        valor_ganho_str = props.get('valor_ganho', '0')
        tipo_receita = props.get('tipo_de_receita', '')
        tipo_negociacao = props.get('tipo_de_negociacao', '')
        
        # Filtro 1: tipo_de_receita != 'Pontual'
        if tipo_receita == 'Pontual':
            continue
        
        # Filtro 2: tipo_de_negociacao != 'Variação Cambial'
        if tipo_negociacao == 'Variação Cambial':
            continue
        
        # Filtro 3: Deal stage deve ser exatamente "Ganho" (7075780)
        if deal_stage_id != RENEWAL_WON_STAGE_ID:
            continue
        
        # Filtro 4: valor_ganho > 0
        try:
            valor_ganho = float(valor_ganho_str) if valor_ganho_str else 0.0
        except (ValueError, TypeError):
            valor_ganho = 0.0
        
        if valor_ganho <= 0:
            continue
        
        # Filtro 5: Verifica se closedate está no mês (ajustado para Brasil)
        closedate_utc = parse_hubspot_timestamp(closedate_str)
        if closedate_utc:
            closedate_brazil = adjust_date_to_brazil(closedate_utc)
            # Verifica se está no mês atual
            now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
            if closedate_brazil.month != now_brazil.month or closedate_brazil.year != now_brazil.year:
                continue
        
        # Deal passou em todos os filtros
        stage_info = stages_info.get(deal_stage_id, {})
        filtered_deals.append({
            'deal_id': deal.get('id'),
            'deal_name': deal_name,
            'deal_stage_id': deal_stage_id,
            'deal_stage_label': stage_info.get('label', 'Ganho'),
            'closedate': closedate_str,
            'closedate_utc': closedate_utc.isoformat() if closedate_utc else None,
            'closedate_brazil': adjust_date_to_brazil(closedate_utc).isoformat() if closedate_utc else None,
            'valor_ganho': valor_ganho,
            'tipo_receita': tipo_receita,
            'tipo_negociacao': tipo_negociacao
        })
        
        total_revenue += valor_ganho
    
    print(f"\nDeals que passaram nos filtros: {len(filtered_deals)}")
    print(f"Receita total: R$ {total_revenue:,.2f}")
    
    # Exibe detalhes dos deals filtrados
    if filtered_deals:
        print(f"\nDetalhes dos deals filtrados:")
        print("-" * 80)
        for i, deal in enumerate(filtered_deals[:10], 1):  # Mostra os 10 primeiros
            print(f"\n{i}. {deal['deal_name']}")
            print(f"   Stage: {deal['deal_stage_label']} ({deal['deal_stage_id']})")
            print(f"   Valor: R$ {deal['valor_ganho']:,.2f}")
            print(f"   Data (Brasil): {deal['closedate_brazil']}")
            print(f"   Tipo Receita: {deal['tipo_receita'] or 'N/A'}")
            print(f"   Tipo Negociação: {deal['tipo_negociacao'] or 'N/A'}")
        
        if len(filtered_deals) > 10:
            print(f"\n   ... e mais {len(filtered_deals) - 10} deals")
    
    # Salva resultado em JSON para análise
    output_file = 'testes/renewal_deals_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_deals_found': len(all_deals),
            'total_deals_filtered': len(filtered_deals),
            'total_revenue': total_revenue,
            'deals': filtered_deals,
            'stages_info': stages_info
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nResultado salvo em: {output_file}")
    
    return filtered_deals, total_revenue

if __name__ == '__main__':
    try:
        deals, revenue = fetch_renewal_deals_from_hubspot()
        print(f"\n{'='*80}")
        print(f"TESTE CONCLUIDO")
        print(f"   Deals encontrados: {len(deals)}")
        print(f"   Receita total: R$ {revenue:,.2f}")
        print(f"{'='*80}\n")
    except Exception as e:
        print(f"\nERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()

