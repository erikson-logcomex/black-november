"""
Teste para verificar se o filtro de pipeline está funcionando corretamente
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_db_connection_context
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone, timedelta

def test_pipeline_filter():
    """Testa se o filtro de pipeline está excluindo corretamente"""
    BRAZIL_TZ_OFFSET = timedelta(hours=-3)
    now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
    current_year = now_brazil.year
    current_month = now_brazil.month
    month_start_str = f"{current_year}-{current_month:02d}-01"
    RENEWAL_PIPELINE_ID = '7075777'
    
    with get_db_connection_context() as conn:
        if not conn:
            print("[ERRO] Não foi possível conectar ao banco")
            return
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Teste 1: Sem filtro (inclui tudo)
        query_all = f"""
            WITH base AS (
                SELECT
                    d.hs_object_id,
                    d.pipeline,
                    d.valor_ganho,
                    d.closedate,
                    p.stage_label
                FROM deals d
                LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
                WHERE COALESCE(d.tipo_de_receita, '') <> 'Pontual'
                    AND COALESCE(d.tipo_de_negociacao, '') <> 'Variação Cambial'
            ),
            enriquecido AS (
                SELECT *,
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
                COUNT(*) as total_deals,
                COUNT(CASE WHEN pipeline = '{RENEWAL_PIPELINE_ID}' THEN 1 END) as renewal_deals,
                COALESCE(SUM(CASE WHEN pipeline = '{RENEWAL_PIPELINE_ID}' THEN valor_ganho ELSE 0 END), 0) as renewal_revenue
            FROM filtrado
        """
        
        cursor.execute(query_all)
        result_all = cursor.fetchone()
        
        print("="*80)
        print("TESTE: FILTRO DE PIPELINE")
        print("="*80)
        print(f"\n[TESTE 1] SEM filtro (inclui tudo):")
        print(f"   Total: R$ {result_all['total_revenue']:,.2f}")
        print(f"   Total Deals: {result_all['total_deals']}")
        print(f"   Deals Renovação: {result_all['renewal_deals']}")
        print(f"   Receita Renovação: R$ {result_all['renewal_revenue']:,.2f}")
        print(f"   Receita SEM Renovação: R$ {result_all['total_revenue'] - result_all['renewal_revenue']:,.2f}")
        
        # Teste 2: Com filtro (exclui renovação)
        query_exclude = f"""
            WITH base AS (
                SELECT
                    d.hs_object_id,
                    d.pipeline,
                    d.valor_ganho,
                    d.closedate,
                    p.stage_label
                FROM deals d
                LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
                WHERE COALESCE(d.tipo_de_receita, '') <> 'Pontual'
                    AND COALESCE(d.tipo_de_negociacao, '') <> 'Variação Cambial'
                    AND d.pipeline <> '{RENEWAL_PIPELINE_ID}'
            ),
            enriquecido AS (
                SELECT *,
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
                COUNT(*) as total_deals
            FROM filtrado
        """
        
        cursor.execute(query_exclude)
        result_exclude = cursor.fetchone()
        
        print(f"\n[TESTE 2] COM filtro (exclui renovação):")
        print(f"   Total: R$ {result_exclude['total_revenue']:,.2f}")
        print(f"   Total Deals: {result_exclude['total_deals']}")
        
        # Verifica tipos de dados
        query_types = """
            SELECT 
                pipeline,
                pg_typeof(pipeline) as pipeline_type,
                COUNT(*) as count
            FROM deals
            WHERE pipeline IS NOT NULL
            GROUP BY pipeline, pg_typeof(pipeline)
            ORDER BY count DESC
            LIMIT 10
        """
        
        cursor.execute(query_types)
        types_result = cursor.fetchall()
        
        print(f"\n[INFO] Tipos de dados do campo pipeline:")
        for row in types_result:
            print(f"   Pipeline: {row['pipeline']} (tipo: {row['pipeline_type']}, count: {row['count']})")
        
        cursor.close()
        
        print("\n" + "="*80)
        print("TESTE CONCLUIDO")
        print("="*80)

if __name__ == "__main__":
    test_pipeline_filter()
