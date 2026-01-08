"""
Script de teste para buscar faturamento do mês atual de DUAS fontes:
1. Banco de dados PostgreSQL (mesma query SQL usada no sistema)
2. API do HubSpot (aplicando os mesmos critérios)

Compara os resultados para identificar divergências.

Critérios da query:
- closedate no mês atual (ajustado para Brasil -3h)
- Deal stage com "ganho", "faturamento" ou "aguardando" no label
- tipo_de_receita != 'Pontual'
- tipo_de_negociacao != 'Variação Cambial'
- valor_ganho > 0
"""
import os
import sys
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import json

# Adiciona o diretório raiz ao path para importar utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_db_connection_context

load_dotenv()

# Configuração
HUBSPOT_API_TOKEN = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
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

def adjust_date_to_brazil(utc_datetime):
    """Ajusta datetime UTC para horário do Brasil (GMT-3)"""
    if not utc_datetime:
        return None
    return utc_datetime + BRAZIL_TZ_OFFSET

def parse_hubspot_timestamp(timestamp):
    """Parse timestamp do HubSpot (milliseconds) para datetime UTC"""
    if not timestamp:
        return None
    try:
        # HubSpot retorna em milliseconds
        return datetime.fromtimestamp(int(timestamp) / 1000, tz=timezone.utc)
    except (ValueError, TypeError):
        return None

def get_all_deal_stages():
    """
    Busca todos os deal stages do HubSpot para identificar quais têm
    "ganho", "faturamento" ou "aguardando" no label
    """
    print("\n[INFO] Buscando deal stages do HubSpot...")
    
    url = 'https://api.hubapi.com/crm/v3/pipelines/deals'
    headers = {
        'Authorization': f'Bearer {HUBSPOT_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"[ERRO] Erro ao buscar pipelines: {response.status_code}")
            print(f"   Response: {response.text}")
            return {}
        
        pipelines_data = response.json().get('results', [])
        
        # Mapeia stage_id -> stage_label para identificar stages válidos
        valid_stages = {}
        
        for pipeline in pipelines_data:
            pipeline_id = pipeline.get('id')
            stages = pipeline.get('stages', [])
            
            for stage in stages:
                stage_id = stage.get('id')
                stage_label = stage.get('label', '').lower()
                
                # Verifica se o label contém as palavras-chave
                if any(keyword in stage_label for keyword in ['ganho', 'faturamento', 'aguardando']):
                    valid_stages[stage_id] = {
                        'label': stage.get('label'),
                        'pipeline_id': pipeline_id,
                        'pipeline_label': pipeline.get('label')
                    }
        
        print(f"[OK] Encontrados {len(valid_stages)} stages válidos:")
        for stage_id, info in valid_stages.items():
            print(f"   - Stage {stage_id}: {info['label']} (Pipeline: {info['pipeline_label']})")
        
        return valid_stages
        
    except Exception as e:
        print(f"[ERRO] Erro ao buscar stages: {e}")
        return {}

def fetch_current_month_revenue_from_hubspot():
    """
    Busca faturamento do mês atual do HubSpot API
    Aplicando os mesmos critérios da query SQL:
    - closedate no mês atual (ajustado para Brasil -3h)
    - Deal stage com "ganho", "faturamento" ou "aguardando"
    - tipo_de_receita != 'Pontual'
    - tipo_de_negociacao != 'Variação Cambial'
    - valor_ganho > 0
    """
    print("\n" + "="*80)
    print("BUSCANDO FATURAMENTO DO MÊS ATUAL NO HUBSPOT API")
    print("="*80)
    
    if not HUBSPOT_API_TOKEN:
        print("[ERRO] HUBSPOT_PRIVATE_APP_TOKEN não configurado")
        return None
    
    # Busca stages válidos primeiro
    valid_stages = get_all_deal_stages()
    if not valid_stages:
        print("[ERRO] Não foi possível identificar stages válidos")
        return None
    
    valid_stage_ids = list(valid_stages.keys())
    
    # Calcula período do mês atual (Brasil)
    month_start_utc = get_month_start_brazil_utc()
    month_end_utc = get_month_end_brazil_utc()
    
    month_start_ms = int(month_start_utc.timestamp() * 1000)
    month_end_ms = int(month_end_utc.timestamp() * 1000)
    
    print(f"\n[INFO] Período de busca:")
    print(f"   Início: {month_start_utc.strftime('%Y-%m-%d %H:%M:%S UTC')} ({adjust_date_to_brazil(month_start_utc).strftime('%Y-%m-%d %H:%M:%S BRT')})")
    print(f"   Fim: {month_end_utc.strftime('%Y-%m-%d %H:%M:%S UTC')} ({adjust_date_to_brazil(month_end_utc).strftime('%Y-%m-%d %H:%M:%S BRT')})")
    
    url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
    headers = {
        'Authorization': f'Bearer {HUBSPOT_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    all_deals = []
    after = None
    
    # Busca deals em lotes (HubSpot limita a 100 por vez)
    while True:
        payload = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "dealstage", "operator": "IN", "values": valid_stage_ids},
                    {"propertyName": "closedate", "operator": "GTE", "value": str(month_start_ms)},
                    {"propertyName": "closedate", "operator": "LTE", "value": str(month_end_ms)},
                    {"propertyName": "tipo_de_receita", "operator": "NEQ", "value": "Pontual"},
                    {"propertyName": "tipo_de_negociacao", "operator": "NEQ", "value": "Variação Cambial"},
                    {"propertyName": "valor_ganho", "operator": "GT", "value": "0"}
                ]
            }],
            "properties": [
                "dealname",
                "amount",
                "closedate",
                "dealstage",
                "tipo_de_receita",
                "tipo_de_negociacao",
                "valor_ganho",
                "pipeline"
            ],
            "limit": 100
        }
        
        if after:
            payload["after"] = after
        
        try:
            print(f"\n[INFO] Fazendo requisição para HubSpot API... (after: {after})")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                print(f"[ERRO] Erro na requisição: {response.status_code}")
                print(f"   Response: {response.text}")
                break
            
            data = response.json()
            deals = data.get('results', [])
            all_deals.extend(deals)
            
            print(f"   [OK] Recebidos {len(deals)} deals (Total: {len(all_deals)})")
            
            # Verifica se há mais páginas
            paging = data.get('paging', {})
            after = paging.get('next', {}).get('after')
            
            if not after:
                break
                
        except Exception as e:
            print(f"[ERRO] Erro ao buscar deals: {e}")
            break
    
    print(f"\n[INFO] Total de deals encontrados: {len(all_deals)}")
    
    # Processa os deals
    total_revenue = 0.0
    deals_by_stage = {}
    deals_by_pipeline = {}
    
    for deal in all_deals:
        props = deal.get('properties', {})
        valor_ganho_str = props.get('valor_ganho', '0')
        
        try:
            valor_ganho = float(valor_ganho_str) if valor_ganho_str else 0.0
        except (ValueError, TypeError):
            valor_ganho = 0.0
        
        if valor_ganho > 0:
            total_revenue += valor_ganho
            
            # Agrupa por stage
            stage_id = props.get('dealstage')
            if stage_id in valid_stages:
                stage_label = valid_stages[stage_id]['label']
                if stage_label not in deals_by_stage:
                    deals_by_stage[stage_label] = {'count': 0, 'revenue': 0.0}
                deals_by_stage[stage_label]['count'] += 1
                deals_by_stage[stage_label]['revenue'] += valor_ganho
            
            # Agrupa por pipeline
            pipeline_id = props.get('pipeline', 'N/A')
            if pipeline_id not in deals_by_pipeline:
                deals_by_pipeline[pipeline_id] = {'count': 0, 'revenue': 0.0}
            deals_by_pipeline[pipeline_id]['count'] += 1
            deals_by_pipeline[pipeline_id]['revenue'] += valor_ganho
    
    # Calcula tiers (mesma lógica da query SQL)
    tier_1 = 0.0
    tier_2 = 0.0
    tier_3 = 0.0
    tier_4 = 0.0
    
    for deal in all_deals:
        props = deal.get('properties', {})
        valor_ganho_str = props.get('valor_ganho', '0')
        try:
            valor_ganho = float(valor_ganho_str) if valor_ganho_str else 0.0
        except (ValueError, TypeError):
            valor_ganho = 0.0
        
        if valor_ganho >= 1200000:
            tier_1 += valor_ganho
        if valor_ganho >= 900000:
            tier_2 += valor_ganho
        if valor_ganho >= 600000:
            tier_3 += valor_ganho
        if valor_ganho >= 300000:
            tier_4 += valor_ganho
    
    # Resultado
    result = {
        'total_revenue': total_revenue,
        'tier_1': tier_1,
        'tier_2': tier_2,
        'tier_3': tier_3,
        'tier_4': tier_4,
        'total_deals': len(all_deals),
        'deals_by_stage': deals_by_stage,
        'deals_by_pipeline': deals_by_pipeline,
        'month_start': month_start_utc.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'month_end': month_end_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
    }
    
    # Exibe resultados
    print("\n" + "="*80)
    print("RESULTADOS HUBSPOT API")
    print("="*80)
    print(f"\nFaturamento Total: R$ {total_revenue:,.2f}")
    print(f"Total de Deals: {len(all_deals)}")
    print(f"\nTiers:")
    print(f"   Tier 1 (>= R$ 1.200.000): R$ {tier_1:,.2f}")
    print(f"   Tier 2 (>= R$ 900.000): R$ {tier_2:,.2f}")
    print(f"   Tier 3 (>= R$ 600.000): R$ {tier_3:,.2f}")
    print(f"   Tier 4 (>= R$ 300.000): R$ {tier_4:,.2f}")
    
    if deals_by_stage:
        print(f"\nPor Stage:")
        for stage_label, data in sorted(deals_by_stage.items(), key=lambda x: x[1]['revenue'], reverse=True):
            print(f"   {stage_label}: {data['count']} deals, R$ {data['revenue']:,.2f}")
    
    if deals_by_pipeline:
        print(f"\nPor Pipeline:")
        for pipeline_id, data in sorted(deals_by_pipeline.items(), key=lambda x: x[1]['revenue'], reverse=True):
            print(f"   Pipeline {pipeline_id}: {data['count']} deals, R$ {data['revenue']:,.2f}")
    
    return result

def fetch_current_month_revenue_from_db():
    """
    Busca faturamento do mês atual do banco de dados PostgreSQL
    Usa a mesma query SQL da função get_current_month_revenue()
    """
    print("\n" + "="*80)
    print("BUSCANDO FATURAMENTO DO MÊS ATUAL NO BANCO DE DADOS")
    print("="*80)
    
    BRAZIL_TZ_OFFSET = timedelta(hours=-3)
    now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
    current_year = now_brazil.year
    current_month = now_brazil.month
    
    # Formata a data do início do mês atual no formato PostgreSQL
    month_start_str = f"{current_year}-{current_month:02d}-01"
    
    print(f"\n[INFO] Período de busca: Mês {current_month:02d}/{current_year}")
    print(f"   Query SQL: closedate_ajustada >= '{month_start_str}' AND < próximo mês")
    
    try:
        with get_db_connection_context() as conn:
            if not conn:
                print("[ERRO] Não foi possível conectar ao banco de dados")
                return None
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = f"""
                WITH base AS (
                    SELECT
                        d.hs_object_id,
                        d.dealname,
                        d.pipeline,
                        d.dealstage,
                        d.tipo_de_negociacao,
                        d.tipo_de_receita,
                        d.valor_ganho,
                        d.closedate,
                        p.stage_label,
                        p.deal_isclosed,
                        p.pipeline_label
                    FROM deals d
                    LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
                    WHERE COALESCE(d.tipo_de_receita, '') <> 'Pontual'
                        AND COALESCE(d.tipo_de_negociacao, '') <> 'Variação Cambial'
                ),
                enriquecido AS (
                    SELECT
                        *,
                        (closedate - INTERVAL '3 hour') AS closedate_ajustada
                    FROM base
                ),
                filtrado AS (
                    SELECT *
                    FROM enriquecido
                    WHERE (
                        LOWER(stage_label) LIKE '%ganho%'
                        OR LOWER(stage_label) LIKE '%faturamento%'
                        OR LOWER(stage_label) LIKE '%aguardando%'
                    )
                    AND closedate_ajustada >= DATE_TRUNC('month', '{month_start_str}'::timestamp)
                    AND closedate_ajustada < DATE_TRUNC('month', '{month_start_str}'::timestamp) + INTERVAL '1 month'
                    AND valor_ganho IS NOT NULL
                    AND valor_ganho > 0
                )
                SELECT 
                    COALESCE(SUM(valor_ganho), 0) as total_revenue,
                    COALESCE(SUM(CASE WHEN valor_ganho >= 1200000 THEN valor_ganho ELSE 0 END), 0) as tier_1,
                    COALESCE(SUM(CASE WHEN valor_ganho >= 900000 THEN valor_ganho ELSE 0 END), 0) as tier_2,
                    COALESCE(SUM(CASE WHEN valor_ganho >= 600000 THEN valor_ganho ELSE 0 END), 0) as tier_3,
                    COALESCE(SUM(CASE WHEN valor_ganho >= 300000 THEN valor_ganho ELSE 0 END), 0) as tier_4,
                    COUNT(*) as total_deals
                FROM filtrado
            """
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                db_result = {
                    'total_revenue': float(result['total_revenue'] or 0),
                    'tier_1': float(result['tier_1'] or 0),
                    'tier_2': float(result['tier_2'] or 0),
                    'tier_3': float(result['tier_3'] or 0),
                    'tier_4': float(result['tier_4'] or 0),
                    'total_deals': int(result['total_deals'] or 0),
                    'source': 'database'
                }
                
                print("\n" + "="*80)
                print("RESULTADOS DO BANCO DE DADOS")
                print("="*80)
                print(f"\nFaturamento Total: R$ {db_result['total_revenue']:,.2f}")
                print(f"Total de Deals: {db_result['total_deals']}")
                print(f"\nTiers:")
                print(f"   Tier 1 (>= R$ 1.200.000): R$ {db_result['tier_1']:,.2f}")
                print(f"   Tier 2 (>= R$ 900.000): R$ {db_result['tier_2']:,.2f}")
                print(f"   Tier 3 (>= R$ 600.000): R$ {db_result['tier_3']:,.2f}")
                print(f"   Tier 4 (>= R$ 300.000): R$ {db_result['tier_4']:,.2f}")
                
                return db_result
            else:
                print("[ERRO] Nenhum resultado retornado do banco de dados")
                return None
                
    except Exception as e:
        print(f"[ERRO] Erro ao buscar dados do banco: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_results(db_result, hubspot_result):
    """
    Compara os resultados do banco de dados e do HubSpot
    """
    if not db_result or not hubspot_result:
        print("\n❌ Não é possível comparar: um ou ambos os resultados estão vazios")
        return
    
    print("\n" + "="*80)
    print("COMPARACAO: BANCO DE DADOS vs HUBSPOT API")
    print("="*80)
    
    # Compara faturamento total
    db_total = db_result['total_revenue']
    hs_total = hubspot_result['total_revenue']
    diff_total = abs(db_total - hs_total)
    diff_percent = (diff_total / db_total * 100) if db_total > 0 else 0
    
    print(f"\nFATURAMENTO TOTAL:")
    print(f"   Banco de Dados: R$ {db_total:,.2f}")
    print(f"   HubSpot API:   R$ {hs_total:,.2f}")
    print(f"   Diferenca:     R$ {diff_total:,.2f} ({diff_percent:.2f}%)")
    
    if diff_total < 0.01:
        print("   [OK] Valores identicos!")
    elif diff_percent < 1:
        print("   [AVISO] Diferenca pequena (< 1%)")
    else:
        print("   [ERRO] Diferenca significativa!")
    
    # Compara total de deals
    db_deals = db_result['total_deals']
    hs_deals = hubspot_result['total_deals']
    diff_deals = abs(db_deals - hs_deals)
    
    print(f"\nTOTAL DE DEALS:")
    print(f"   Banco de Dados: {db_deals}")
    print(f"   HubSpot API:   {hs_deals}")
    print(f"   Diferenca:     {diff_deals} deals")
    
    if diff_deals == 0:
        print("   [OK] Quantidade identica!")
    else:
        print(f"   [AVISO] Diferenca de {diff_deals} deals")
    
    # Compara tiers
    print(f"\nTIERS:")
    for tier_num in [1, 2, 3, 4]:
        tier_key = f'tier_{tier_num}'
        db_tier = db_result.get(tier_key, 0)
        hs_tier = hubspot_result.get(tier_key, 0)
        diff_tier = abs(db_tier - hs_tier)
        
        tier_threshold = [1200000, 900000, 600000, 300000][tier_num - 1]
        print(f"\n   Tier {tier_num} (>= R$ {tier_threshold:,}):")
        print(f"      Banco de Dados: R$ {db_tier:,.2f}")
        print(f"      HubSpot API:   R$ {hs_tier:,.2f}")
        print(f"      Diferenca:     R$ {diff_tier:,.2f}")
        
        if diff_tier < 0.01:
            print("      [OK] Valores identicos!")
        else:
            print("      [AVISO] Diferenca encontrada")
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO DA COMPARACAO")
    print("="*80)
    
    all_match = (
        diff_total < 0.01 and
        diff_deals == 0 and
        all(abs(db_result.get(f'tier_{i}', 0) - hubspot_result.get(f'tier_{i}', 0)) < 0.01 for i in [1, 2, 3, 4])
    )
    
    if all_match:
        print("\n[OK] Todos os valores coincidem perfeitamente!")
    else:
        print("\n[AVISO] Foram encontradas diferencas entre as duas fontes.")
        print("   Possiveis causas:")
        print("   - Sincronizacao pendente entre HubSpot e banco de dados")
        print("   - Diferencas na interpretacao de filtros")
        print("   - Deals processados mas ainda nao sincronizados")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("INICIANDO TESTE DE COMPARACAO: BANCO vs HUBSPOT")
    print("="*80)
    
    # Busca do banco de dados
    db_result = fetch_current_month_revenue_from_db()
    
    # Busca do HubSpot
    hubspot_result = fetch_current_month_revenue_from_hubspot()
    
    # Compara resultados
    if db_result and hubspot_result:
        compare_results(db_result, hubspot_result)
        
        # Salva resultados em JSON
        comparison_result = {
            'database': db_result,
            'hubspot': hubspot_result,
            'comparison': {
                'total_revenue_diff': abs(db_result['total_revenue'] - hubspot_result['total_revenue']),
                'total_deals_diff': abs(db_result['total_deals'] - hubspot_result['total_deals']),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }
        
        output_file = os.path.join('testes', 'test_current_month_revenue_comparison.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n[INFO] Resultado completo salvo em: {output_file}")
        print("\n[OK] Teste concluido!")
    else:
        print("\n[ERRO] Teste falhou: nao foi possivel obter resultados de uma ou ambas as fontes")
