"""
Funções auxiliares para cálculos de receita
"""
import os
import json
from datetime import datetime, timezone, timedelta
from utils.db import get_db_connection_context
from psycopg2.extras import RealDictCursor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUAL_REVENUE_CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'manual_revenue_config.json')

def load_manual_revenue_config():
    """Carrega a configuração do modo manual de faturamento"""
    try:
        if os.path.exists(MANUAL_REVENUE_CONFIG_FILE):
            with open(MANUAL_REVENUE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'enabled': False, 'additionalValue': 0, 'includeRenewalPipeline': False}
    except Exception as e:
        print(f"Erro ao carregar configuração manual: {e}")
        return {'enabled': False, 'additionalValue': 0, 'includeRenewalPipeline': False}

def get_black_november_revenue():
    """Busca faturamento da Black November"""
    with get_db_connection_context() as conn:
        if not conn:
            return None
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = """
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
                    AND closedate_ajustada >= DATE_TRUNC('month', '2025-11-01'::timestamp)
                    AND closedate_ajustada < DATE_TRUNC('month', '2025-11-01'::timestamp + INTERVAL '1 month')
                    AND valor_ganho IS NOT NULL
                    AND valor_ganho > 0
                )
                SELECT 
                    COALESCE(SUM(valor_ganho), 0) as total_revenue,
                    COALESCE(SUM(CASE WHEN valor_ganho >= 1200000 THEN valor_ganho ELSE 0 END), 0) as tier_1,
                    COALESCE(SUM(CASE WHEN valor_ganho >= 900000 THEN valor_ganho ELSE 0 END), 0) as tier_2,
                    COALESCE(SUM(CASE WHEN valor_ganho >= 600000 THEN valor_ganho ELSE 0 END), 0) as tier_3,
                    COALESCE(SUM(CASE WHEN valor_ganho >= 300000 THEN valor_ganho ELSE 0 END), 0) as tier_4
                FROM filtrado
            """
            cursor.execute(query)
            result = cursor.fetchone()
            if result and result['total_revenue'] and float(result['total_revenue']) > 0:
                total = float(result['total_revenue'])
            else:
                total = 0.0
            cursor.close()
            return {
                'total': total,
                'goal': 1500000,
                'has_data': total > 0
            }
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return None

def get_current_month_revenue(exclude_renewal_pipeline=False):
    """
    Busca faturamento do mês atual dinamicamente
    
    Args:
        exclude_renewal_pipeline: Se True, exclui deals do pipeline de Renovação (7075777)
    """
    BRAZIL_TZ_OFFSET = timedelta(hours=-3)
    now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
    current_year = now_brazil.year
    current_month = now_brazil.month
    
    # Formata a data do início do mês atual no formato PostgreSQL
    month_start_str = f"{current_year}-{current_month:02d}-01"
    
    # Pipeline de Renovação que deve ser excluído quando a configuração estiver desativada
    RENEWAL_PIPELINE_ID = '7075777'
    
    with get_db_connection_context() as conn:
        if not conn:
            return None
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Adiciona filtro para excluir pipeline de renovação se necessário
            renewal_filter = ""
            if exclude_renewal_pipeline:
                renewal_filter = f"AND d.pipeline <> '{RENEWAL_PIPELINE_ID}'"
            
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
                        {renewal_filter}
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
                    COALESCE(SUM(CASE WHEN valor_ganho >= 300000 THEN valor_ganho ELSE 0 END), 0) as tier_4
                FROM filtrado
            """
            cursor.execute(query)
            result = cursor.fetchone()
            if result and result['total_revenue'] and float(result['total_revenue']) > 0:
                total = float(result['total_revenue'])
            else:
                total = 0.0
            cursor.close()
            return {
                'total': total,
                'goal': 1500000,  # Meta padrão, pode ser sobrescrita pela meta manual
                'has_data': total > 0
            }
        except Exception as e:
            print(f"Erro ao buscar dados do mês atual: {e}")
            return None

def get_december_revenue():
    """Busca faturamento de Dezembro (Natal)"""
    with get_db_connection_context() as conn:
        if not conn:
            return None
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = """
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
                        AND d.pipeline IN ('6810518', '4007305')
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
                    AND closedate_ajustada >= DATE_TRUNC('month', '2025-12-01'::timestamp)
                    AND closedate_ajustada < DATE_TRUNC('month', '2025-12-01'::timestamp + INTERVAL '1 month')
                    AND valor_ganho IS NOT NULL
                    AND valor_ganho > 0
                )
                SELECT 
                    COALESCE(SUM(valor_ganho), 0) as total_revenue
                FROM filtrado
            """
            cursor.execute(query)
            result = cursor.fetchone()
            if result and result['total_revenue'] and float(result['total_revenue']) > 0:
                total = float(result['total_revenue'])
            else:
                total = 0.0
            cursor.close()
            return {
                'total': total,
                'goal': 739014.83,  # Meta de Natal
                'has_data': total > 0
            }
        except Exception as e:
            print(f"Erro ao buscar dados de dezembro: {e}")
            return None

def get_revenue_until_yesterday(exclude_renewal_pipeline=False):
    """
    Busca faturamento do mês atual até ontem (excluindo o dia atual)
    
    Args:
        exclude_renewal_pipeline: Se True, exclui deals do pipeline de Renovação (7075777)
    """
    BRAZIL_TZ_OFFSET = timedelta(hours=-3)
    now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
    current_year = now_brazil.year
    current_month = now_brazil.month
    
    # Formata a data do início do mês atual no formato PostgreSQL
    month_start_str = f"{current_year}-{current_month:02d}-01"
    RENEWAL_PIPELINE_ID = '7075777'
    
    with get_db_connection_context() as conn:
        if not conn:
            return None
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Adiciona filtro para excluir pipeline de renovação se necessário
            renewal_filter = ""
            if exclude_renewal_pipeline:
                renewal_filter = f"AND d.pipeline <> '{RENEWAL_PIPELINE_ID}'"
            
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
                        {renewal_filter}
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
                    AND DATE(closedate_ajustada) < DATE(CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
                    AND valor_ganho IS NOT NULL
                    AND valor_ganho > 0
                )
                SELECT 
                    COALESCE(SUM(valor_ganho), 0) as total_revenue
                FROM filtrado
            """
            cursor.execute(query)
            result = cursor.fetchone()
            if result and result['total_revenue'] and float(result['total_revenue']) > 0:
                total = float(result['total_revenue'])
            else:
                total = 0.0
            cursor.close()
            return {
                'total': total,
                'goal': 1500000,
                'has_data': total > 0
            }
        except Exception as e:
            print(f"Erro ao buscar dados até ontem: {e}")
            return None

def get_today_revenue(exclude_renewal_pipeline=False):
    """
    Busca faturamento APENAS DO DIA ATUAL
    
    Args:
        exclude_renewal_pipeline: Se True, exclui deals do pipeline de Renovação (7075777)
    """
    RENEWAL_PIPELINE_ID = '7075777'
    
    with get_db_connection_context() as conn:
        if not conn:
            return None
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Adiciona filtro para excluir pipeline de renovação se necessário
            renewal_filter = ""
            if exclude_renewal_pipeline:
                renewal_filter = f"AND d.pipeline <> '{RENEWAL_PIPELINE_ID}'"
            
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
                        {renewal_filter}
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
                    AND DATE(closedate_ajustada) = DATE(CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
                    AND valor_ganho IS NOT NULL
                    AND valor_ganho > 0
                )
                SELECT 
                    COALESCE(SUM(valor_ganho), 0) as total_today
                FROM filtrado
            """
            cursor.execute(query)
            result = cursor.fetchone()
            if result and result['total_today']:
                total_today = float(result['total_today'])
            else:
                total_today = 0.0
            cursor.close()
            return {
                'total_today': total_today,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        except Exception as e:
            print(f"Erro ao buscar faturamento do dia: {e}")
            return None

def get_month_start_brazil_utc():
    """Retorna o início do mês atual (1º dia 00:00) no Brasil (GMT-3) convertido para UTC"""
    BRAZIL_TZ_OFFSET = timedelta(hours=-3)
    now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
    month_start_brazil = now_brazil.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_start_utc = month_start_brazil - BRAZIL_TZ_OFFSET
    return month_start_utc

def get_renewal_pipeline_revenue(start_date_utc=None, end_date_utc=None):
    """
    Busca receita do pipeline de Renovação (7075777) diretamente do HubSpot API
    Busca TODOS os stages válidos (com "ganho", "faturamento" ou "aguardando" no label)
    para manter consistência com a query do banco de dados
    """
    RENEWAL_PIPELINE_ID = '7075777'
    BRAZIL_TZ_OFFSET = timedelta(hours=-3)
    
    try:
        if start_date_utc and end_date_utc:
            month_start_utc = start_date_utc
            month_end_utc = end_date_utc
        else:
            month_start_utc = get_month_start_brazil_utc()
            now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
            if now_brazil.month == 12:
                next_month = now_brazil.replace(year=now_brazil.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                next_month = now_brazil.replace(month=now_brazil.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end_brazil = next_month - timedelta(seconds=1)
            month_end_utc = month_end_brazil - BRAZIL_TZ_OFFSET
        
        month_start_ms = int(month_start_utc.timestamp() * 1000)
        month_end_ms = int(month_end_utc.timestamp() * 1000)
        
        hubspot_token = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
        if not hubspot_token:
            print("Erro: HUBSPOT_PRIVATE_APP_TOKEN não configurado")
            return 0.0
        
        import requests
        import time
        
        # Primeiro, busca todos os stages do pipeline de Renovação
        pipelines_url = 'https://api.hubapi.com/crm/v3/pipelines/deals'
        pipelines_headers = {
            'Authorization': f'Bearer {hubspot_token}',
            'Content-Type': 'application/json'
        }
        
        pipelines_response = requests.get(pipelines_url, headers=pipelines_headers, timeout=30)
        valid_stage_ids = []
        
        if pipelines_response.status_code == 200:
            pipelines_data = pipelines_response.json()
            for pipeline in pipelines_data.get('results', []):
                pipeline_id = str(pipeline.get('id'))
                if pipeline_id == RENEWAL_PIPELINE_ID:
                    stages = pipeline.get('stages', [])
                    for stage in stages:
                        stage_id = str(stage.get('id'))
                        stage_label = stage.get('label', '').lower()
                        # Inclui stages com "ganho", "faturamento" ou "aguardando" no label
                        # (mesmos critérios da query do banco)
                        if any(keyword in stage_label for keyword in ['ganho', 'faturamento', 'aguardando']):
                            valid_stage_ids.append(stage_id)
                    break
        
        if not valid_stage_ids:
            print(f"[AVISO] Nenhum stage válido encontrado para o pipeline de Renovação {RENEWAL_PIPELINE_ID}")
            return 0.0
        
        url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
        headers = {
            'Authorization': f'Bearer {hubspot_token}',
            'Content-Type': 'application/json'
        }
        
        # Busca deals de TODOS os stages válidos
        # Nota: A API do HubSpot limita a 6 filtros por grupo, então filtramos tipo_de_receita,
        # tipo_de_negociacao e valor_ganho no processamento dos deals
        payload_base = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "pipeline", "operator": "EQ", "value": RENEWAL_PIPELINE_ID},
                    {"propertyName": "dealstage", "operator": "IN", "values": valid_stage_ids},
                    {"propertyName": "closedate", "operator": "GTE", "value": str(month_start_ms)},
                    {"propertyName": "closedate", "operator": "LTE", "value": str(month_end_ms)}
                ]
            }],
            "properties": [
                "dealname", "dealstage", "closedate", "valor_ganho",
                "tipo_de_receita", "tipo_de_negociacao", "pipeline"
            ],
            "limit": 100
        }
        
        all_deals = []
        after = None
        
        while True:
            payload = payload_base.copy()
            if after:
                payload["after"] = after
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 429:
                print("[AVISO] Rate limit atingido (Renovacao), aguardando 2 segundos...")
                time.sleep(2)
                continue
            elif response.status_code != 200:
                print(f"[AVISO] Erro na API HubSpot (Renovacao): {response.status_code} - {response.text}")
                break
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                break
            
            all_deals.extend(results)
            
            paging = data.get("paging", {})
            after = paging.get("next", {}).get("after")
            
            if not after:
                break
            
            time.sleep(0.5)
        
        total_revenue = 0.0
        
        for deal in all_deals:
            props = deal.get('properties', {})
            tipo_receita = props.get('tipo_de_receita', '')
            tipo_negociacao = props.get('tipo_de_negociacao', '')
            valor_ganho_str = props.get('valor_ganho', '0')
            
            # Aplica filtros que não puderam ser aplicados na API (limite de 6 filtros)
            if tipo_receita == 'Pontual':
                continue
            if tipo_negociacao == 'Variação Cambial':
                continue
            
            try:
                valor_ganho = float(valor_ganho_str) if valor_ganho_str else 0.0
            except (ValueError, TypeError):
                valor_ganho = 0.0
            
            if valor_ganho <= 0:
                continue
            
            total_revenue += valor_ganho
        
        print(f"[INFO] Receita total do pipeline de Renovação: R$ {total_revenue:,.2f} ({len(all_deals)} deals)")
        return total_revenue
        
    except Exception as e:
        print(f"[ERRO] Erro ao buscar receita do pipeline de Renovacao: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

