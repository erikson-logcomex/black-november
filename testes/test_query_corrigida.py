import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('PG_HOST'),
    port=os.getenv('PG_PORT'),
    database=os.getenv('PG_DATABASE_HUBSPOT'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD')
)

cur = conn.cursor()

# Query CORRIGIDA com AND em vez de OR
query = """
WITH base AS (
    SELECT
        d.hs_object_id,
        d.dealname,
        d.amount,
        d.closedate,
        p.stage_label,
        p.deal_isclosed
    FROM deals d
    LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
    WHERE COALESCE(d.tipo_de_receita, '') <> 'Pontual'
        AND COALESCE(d.tipo_de_negociacao, '') <> 'Variação Cambial'
),
previstos_hoje AS (
    SELECT *
    FROM base
    WHERE 
        DATE(closedate - INTERVAL '3 hour') = CURRENT_DATE
        AND (deal_isclosed = FALSE OR deal_isclosed IS NULL)
        AND LOWER(stage_label) NOT LIKE '%ganho%'
        AND LOWER(stage_label) NOT LIKE '%faturamento%'
        AND LOWER(stage_label) NOT LIKE '%aguardando%'
        AND LOWER(stage_label) NOT LIKE '%perdido%'
        AND (amount IS NOT NULL AND amount > 0)
)
SELECT 
    COUNT(*) as total_deals,
    COALESCE(SUM(amount), 0) as total_pipeline
FROM previstos_hoje
"""

cur.execute(query)
result = cur.fetchone()

print(f"✅ Query CORRIGIDA (com AND e NOT LIKE perdido):")
print(f"   Deals: {result[0]}")
print(f"   Pipeline: R$ {float(result[1]):,.2f}")

# Compara com a query ANTIGA (com OR)
query_old = """
WITH base AS (
    SELECT
        d.hs_object_id,
        d.dealname,
        d.amount,
        d.closedate,
        p.stage_label,
        p.deal_isclosed
    FROM deals d
    LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
    WHERE COALESCE(d.tipo_de_receita, '') <> 'Pontual'
        AND COALESCE(d.tipo_de_negociacao, '') <> 'Variação Cambial'
),
previstos_hoje AS (
    SELECT *
    FROM base
    WHERE 
        DATE(closedate - INTERVAL '3 hour') = CURRENT_DATE
        AND (
            deal_isclosed = FALSE 
            OR deal_isclosed IS NULL
            OR (LOWER(stage_label) NOT LIKE '%ganho%' 
                AND LOWER(stage_label) NOT LIKE '%faturamento%'
                AND LOWER(stage_label) NOT LIKE '%aguardando%')
        )
        AND (amount IS NOT NULL AND amount > 0)
)
SELECT 
    COUNT(*) as total_deals,
    COALESCE(SUM(amount), 0) as total_pipeline
FROM previstos_hoje
"""

cur.execute(query_old)
result_old = cur.fetchone()

print(f"\n⚠️  Query ANTIGA (com OR - incorreta):")
print(f"   Deals: {result_old[0]}")
print(f"   Pipeline: R$ {float(result_old[1]):,.2f}")

print(f"\n📊 Diferença:")
print(f"   Deals: {result[0] - result_old[0]} ({result[0] - result_old[0]} deals a menos)")
print(f"   Pipeline: R$ {float(result[1]) - float(result_old[1]):,.2f}")

cur.close()
conn.close()
