"""
Script de teste para executar query de análise de produtos para página de Natal
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.getenv('PG_HOST'),
    'port': os.getenv('PG_PORT'),
    'database': os.getenv('PG_DATABASE_HUBSPOT'),  # Usa o mesmo banco das outras queries
    'user': os.getenv('PG_USER'),
    'password': os.getenv('PG_PASSWORD')
}

QUERY = """
SELECT
  "source"."Line Items - hs_object_id__produto_principal" AS "Line Items - hs_object_id_produto_principal",
  
  -- 👇 Contagem de New (Vendas NMRR)
  COUNT(
    DISTINCT
    CASE
      WHEN LOWER("source"."Deal Stages Pipelines - Dealstage_pipeline_label") LIKE '%vendas nmrr%'
      THEN "source"."hs_object_id"
    END
  ) AS "Qtd New",
  
  -- 👇 Contagem de Expansão (Expansão, com mesmas regras do 2º SQL)
  COUNT(
    DISTINCT
    CASE
      WHEN LOWER("source"."Deal Stages Pipelines - Dealstage_pipeline_label") LIKE '%expansão%'
       AND "source"."Line Items - hs_object_id__in_produto_esta_nesta_negociacao" = '1'
       AND "source"."hs_object_id" <> '42020535705'
      THEN "source"."hs_object_id"
    END
  ) AS "Qtd Expansão"

FROM
  (
    SELECT
      "source"."hs_object_id" AS "hs_object_id",
      "source"."dealname" AS "dealname",
      "source"."pipeline" AS "pipeline",
      "source"."dealstage" AS "dealstage",
      "source"."tipo_de_negociacao" AS "tipo_de_negociacao",
      "source"."tipo_negociação_ajustada" AS "tipo_negociação_ajustada",
      "source"."tipo_de_receita" AS "tipo_de_receita",
      "source"."status_de_agendamento" AS "status_de_agendamento",
      "source"."produto_principal" AS "produto_principal",
      "source"."ramo_de_atuacao_do_negocio" AS "ramo_de_atuacao_do_negocio",
      "source"."segmento_oficial" AS "segmento_oficial",
      "source"."sub_segmento_oficial" AS "sub_segmento_oficial",
      "source"."valor_ganho" AS "valor_ganho",
      "source"."campanha" AS "campanha",
      "source"."canal_de_aquisicao" AS "canal_de_aquisicao",
      "source"."coordenador" AS "coordenador",
      "source"."criado_por" AS "criado_por",
      "source"."pr_vendedor" AS "pr_vendedor",
      "source"."analista_comercial" AS "analista_comercial",
      "source"."createdate" AS "createdate",
      "source"."data_de_entrada_na_etapa_distribuicao_vendas_nmrr" AS "data_de_entrada_na_etapa_distribuicao_vendas_nmrr",
      "source"."data_de_prospect" AS "data_de_prospect",
      "source"."etapa_data_de_tentando_contato" AS "etapa_data_de_tentando_contato",
      "source"."data_de_qualificacao" AS "data_de_qualificacao",
      "source"."data_de_agendamento" AS "data_de_agendamento",
      "source"."fase_data_de_no_show" AS "fase_data_de_no_show",
      "source"."data_de_demonstracao" AS "data_de_demonstracao",
      "source"."data_de_onboarding_trial" AS "data_de_onboarding_trial",
      "source"."data_de_proposta" AS "data_de_proposta",
      "source"."etapa_data_de_entrada_em_fechamento" AS "etapa_data_de_entrada_em_fechamento",
      "source"."sales_data_de_faturamento" AS "sales_data_de_faturamento",
      "source"."closedate" AS "closedate",
      "source"."closedate_ajustada" AS "closedate_ajustada",
      "source"."notes_next_activity_date" AS "notes_next_activity_date",
      "source"."data_prevista_reuniao" AS "data_prevista_reuniao",
      "source"."notes_last_updated" AS "notes_last_updated",
      "source"."hs_lastmodifieddate" AS "hs_lastmodifieddate",
      "source"."faturamento_anual_ic" AS "faturamento_anual_ic",
      "source"."fob_anual_ic" AS "fob_anual_ic",
      "source"."ultima_etapa_antes_do_perdido" AS "ultima_etapa_antes_do_perdido",
      "source"."temperatura_do_deal" AS "temperatura_do_deal",
      "source"."presales_temperatura_v2" AS "presales_temperatura_v2",
      "source"."bu_business_unit" AS "bu_business_unit",
      "source"."sales_business_unit" AS "sales_business_unit",
      "source"."bu_country_unit" AS "bu_country_unit",
      "source"."ic_sync_mkt_campanha" AS "ic_sync_mkt_campanha",
      "source"."data_de_atribuicao_pre_vendas" AS "data_de_atribuicao_pre_vendas",
      "source"."sales_sal_sales_accepted_lead" AS "sales_sal_sales_accepted_lead",
      "source"."mkt_sla_de_atendimento" AS "mkt_sla_de_atendimento",
      "source"."origem_da_ultima_interacao_2_criacao_do_deal" AS "origem_da_ultima_interacao_2_criacao_do_deal",
      "source"."sales_a_empresa_estava_no_timing_para_uma_contratacao" AS "sales_a_empresa_estava_no_timing_para_uma_contratacao",
      "source"."sales_a_reuniao_foi_realizada_com_uma_persona_adequada" AS "sales_a_reuniao_foi_realizada_com_uma_persona_adequada",
      "source"."sales_a_qualificacao_snippet_esta_preenchida_e_de_forma_clara" AS "sales_a_qualificacao_snippet_esta_preenchida_e_de_f_92f8fba5",
      "source"."sales_a_dor_mapeada_pelo_pre_vendedor" AS "sales_a_dor_mapeada_pelo_pre_vendedor",
      "source"."o_decisor_participou_da_reuniao" AS "o_decisor_participou_da_reuniao",
      "source"."Qualificação/Snippet" AS "Qualificação/Snippet",
      "source"."Owners - Criado Por_email" AS "Owners - Criado Por_email",
      "source"."Owners - Criado Por_fullname" AS "Owners - Criado Por_fullname",
      "source"."Owners - Pr Vendedor_email" AS "Owners - Pr Vendedor_email",
      "source"."Owners - Pr Vendedor_fullname" AS "Owners - Pr Vendedor_fullname",
      "source"."Owners - Analista Comercial_email" AS "Owners - Analista Comercial_email",
      "source"."Owners - Analista Comercial_fullname" AS "Owners - Analista Comercial_fullname",
      "source"."Owners - Hubspot Owner_email" AS "Owners - Hubspot Owner_email",
      "source"."Owners - Hubspot Owner_fullname" AS "Owners - Hubspot Owner_fullname",
      "source"."Deal Stages Pipelines - Dealstage_stage_label" AS "Deal Stages Pipelines - Dealstage_stage_label",
      "source"."Deal Stages Pipelines - Dealstage_deal_isclosed" AS "Deal Stages Pipelines - Dealstage_deal_isclosed",
      "source"."Deal Stages Pipelines - Dealstage_pipeline_label" AS "Deal Stages Pipelines - Dealstage_pipeline_label",
      "source"."estrategia_IC" AS "estrategia_IC",
      "source"."ciclo_prospeccao_ate_agendamento" AS "ciclo_prospeccao_ate_agendamento",
      "source"."sales_sal_qualificada" AS "sales_sal_qualificada",
      CASE
        WHEN NOT ("source"."bu_country_unit" IS NULL) THEN 'Internacional'
        ELSE CASE
          WHEN (
            "Line Items - hs_object_id"."produto_principal" = 'Catálogo de Produtos'
          )
          OR (
            "Line Items - hs_object_id"."produto_principal" = 'PLG - Catálogo de Produtos'
          )
          OR (
            "Line Items - hs_object_id"."produto_principal" = 'Log OS'
          )
          OR (
            "Line Items - hs_object_id"."produto_principal" = 'LogOS - LogTokens'
          )
          OR (
            "Line Items - hs_object_id"."produto_principal" = 'Automação'
          )
          OR (
            "Line Items - hs_object_id"."produto_principal" = 'LogManager'
          ) THEN 'Supply'
          ELSE 'Intel'
        END
      END AS "Business_unit_dash",
      CASE
        WHEN ("source"."tipo_de_negociacao" = 'Upsell')
          OR ("source"."tipo_de_negociacao" = 'Cross Sell') THEN 'Upsell/Cross'
      END AS "tipo_negociação_ajustada_2",
      "Line Items - hs_object_id"."hs_object_id" AS "Line Items - hs_object_id__hs_object_id",
      "Line Items - hs_object_id"."name" AS "Line Items - hs_object_id__name",
      "Line Items - hs_object_id"."codigo_de_produto_omie" AS "Line Items - hs_object_id__codigo_de_produto_omie",
      "Line Items - hs_object_id"."hs_sku" AS "Line Items - hs_object_id__hs_sku",
      "Line Items - hs_object_id"."price" AS "Line Items - hs_object_id__price",
      "Line Items - hs_object_id"."sales_bu" AS "Line Items - hs_object_id__sales_bu",
      "Line Items - hs_object_id"."produto_principal" AS "Line Items - hs_object_id__produto_principal",
      "Line Items - hs_object_id"."in_produto_esta_nesta_negociacao" AS "Line Items - hs_object_id__in_produto_esta_nesta_negociacao",
      "Line Items - hs_object_id"."hs_margin_mrr" AS "Line Items - hs_object_id__hs_margin_mrr",
      "Line Items - hs_object_id"."description" AS "Line Items - hs_object_id__description",
      "Line Items - hs_object_id"."adds_on" AS "Line Items - hs_object_id__adds_on",
      "Line Items - hs_object_id"."amount" AS "Line Items - hs_object_id__amount",
      "Line Items - hs_object_id"."discount" AS "Line Items - hs_object_id__discount",
      "Line Items - hs_object_id"."recurringbillingfrequency" AS "Line Items - hs_object_id__recurringbillingfrequency",
      "Line Items - hs_object_id"."createdate" AS "Line Items - hs_object_id__createdate",
      "Line Items - hs_object_id"."row_updated" AS "Line Items - hs_object_id__row_updated",
      "Line Items - hs_object_id"."archived" AS "Line Items - hs_object_id__archived",
      "Line Items - hs_object_id"."deal_id" AS "Line Items - hs_object_id__deal_id",
      "Line Items - hs_object_id"."hs_lastmodifieddate" AS "Line Items - hs_object_id__hs_lastmodifieddate"
    FROM
      (
        SELECT
          "source"."hs_object_id" AS "hs_object_id",
          "source"."dealname" AS "dealname",
          "source"."pipeline" AS "pipeline",
          "source"."dealstage" AS "dealstage",
          "source"."tipo_de_negociacao" AS "tipo_de_negociacao",
          "source"."tipo_negociação_ajustada" AS "tipo_negociação_ajustada",
          "source"."tipo_de_receita" AS "tipo_de_receita",
          "source"."status_de_agendamento" AS "status_de_agendamento",
          "source"."produto_principal" AS "produto_principal",
          "source"."ramo_de_atuacao_do_negocio" AS "ramo_de_atuacao_do_negocio",
          -- ⬇ NOVOS CAMPOS
          "source"."segmento_oficial" AS "segmento_oficial",
          "source"."sub_segmento_oficial" AS "sub_segmento_oficial",
          "source"."valor_ganho" AS "valor_ganho",
          "source"."campanha" AS "campanha",
          "source"."canal_de_aquisicao" AS "canal_de_aquisicao",
          "source"."coordenador" AS "coordenador",
          "source"."criado_por" AS "criado_por",
          "source"."pr_vendedor" AS "pr_vendedor",
          "source"."analista_comercial" AS "analista_comercial",
          "source"."createdate" AS "createdate",
          "source"."data_de_entrada_na_etapa_distribuicao_vendas_nmrr" AS "data_de_entrada_na_etapa_distribuicao_vendas_nmrr",
          "source"."data_de_prospect" AS "data_de_prospect",
          "source"."etapa_data_de_tentando_contato" AS "etapa_data_de_tentando_contato",
          "source"."data_de_qualificacao" AS "data_de_qualificacao",
          "source"."data_de_agendamento" AS "data_de_agendamento",
          "source"."fase_data_de_no_show" AS "fase_data_de_no_show",
          "source"."data_de_demonstracao" AS "data_de_demonstracao",
          "source"."data_de_onboarding_trial" AS "data_de_onboarding_trial",
          "source"."data_de_proposta" AS "data_de_proposta",
          "source"."etapa_data_de_entrada_em_fechamento" AS "etapa_data_de_entrada_em_fechamento",
          "source"."sales_data_de_faturamento" AS "sales_data_de_faturamento",
          "source"."closedate" AS "closedate",
          ("source"."closedate" - interval '3 hour') AS "closedate_ajustada",
          "source"."notes_next_activity_date" AS "notes_next_activity_date",
          "source"."data_prevista_reuniao" AS "data_prevista_reuniao",
          "source"."notes_last_updated" AS "notes_last_updated",
          "source"."hs_lastmodifieddate" AS "hs_lastmodifieddate",
          "source"."faturamento_anual_ic" AS "faturamento_anual_ic",
          "source"."fob_anual_ic" AS "fob_anual_ic",
          "source"."ultima_etapa_antes_do_perdido" AS "ultima_etapa_antes_do_perdido",
          "source"."temperatura_do_deal" AS "temperatura_do_deal",
          "source"."presales_temperatura_v2" AS "presales_temperatura_v2",
          "source"."bu_business_unit" AS "bu_business_unit",
          "source"."sales_business_unit" AS "sales_business_unit",
          "source"."bu_country_unit" AS "bu_country_unit",
          "source"."ic_sync_mkt_campanha" AS "ic_sync_mkt_campanha",
          "source"."data_de_atribuicao_pre_vendas" AS "data_de_atribuicao_pre_vendas",
          "source"."sales_sal_sales_accepted_lead" AS "sales_sal_sales_accepted_lead",
          "source"."mkt_sla_de_atendimento" AS "mkt_sla_de_atendimento",
          "source"."origem_da_ultima_interacao_2_criacao_do_deal" AS "origem_da_ultima_interacao_2_criacao_do_deal",
          "source"."sales_timing_contratacao" AS "sales_a_empresa_estava_no_timing_para_uma_contratacao",
          "source"."sales_persona_adequada" AS "sales_a_reuniao_foi_realizada_com_uma_persona_adequada",
          "source"."sales_snippet_claro" AS "sales_a_qualificacao_snippet_esta_preenchida_e_de_forma_clara",
          "source"."sales_dor_mapeada" AS "sales_a_dor_mapeada_pelo_pre_vendedor",
          "source"."decisor_participou" AS "o_decisor_participou_da_reuniao",
          "source"."sales_snippet_claro" AS "Qualificação/Snippet",
          "source"."Owners - Criado Por__email" AS "Owners - Criado Por_email",
          "source"."Owners - Criado Por__fullname" AS "Owners - Criado Por_fullname",
          "source"."Owners - Pr Vendedor__email" AS "Owners - Pr Vendedor_email",
          "source"."Owners - Pr Vendedor__fullname" AS "Owners - Pr Vendedor_fullname",
          "source"."Owners - Analista Comercial__email" AS "Owners - Analista Comercial_email",
          "source"."Owners - Analista Comercial__fullname" AS "Owners - Analista Comercial_fullname",
          "source"."Owners - Hubspot Owner__email" AS "Owners - Hubspot Owner_email",
          "source"."Owners - Hubspot Owner__fullname" AS "Owners - Hubspot Owner_fullname",
          "source"."Deal Stages Pipelines - Dealstage__stage_label" AS "Deal Stages Pipelines - Dealstage_stage_label",
          "source"."Deal Stages Pipelines - Dealstage__deal_isclosed" AS "Deal Stages Pipelines - Dealstage_deal_isclosed",
          "source"."Deal Stages Pipelines - Dealstage__pipeline_label" AS "Deal Stages Pipelines - Dealstage_pipeline_label",
          COALESCE(
            NULLIF("source"."campanha", ''),
            "source"."ic_sync_mkt_campanha"
          ) AS "estrategia_IC",
          CASE
            WHEN "source"."data_de_agendamento" IS NULL
              OR "source"."data_de_atribuicao_pre_vendas" IS NULL THEN NULL
            ELSE ROUND(
              EXTRACT(
                EPOCH
                FROM
                  (
                    "source"."data_de_agendamento" :: timestamp - "source"."data_de_atribuicao_pre_vendas" :: timestamp
                  )
              ) / 3600.0,
              2
            )
          END AS "ciclo_prospeccao_ate_agendamento",
          CASE
            WHEN "source"."sales_sal_sales_accepted_lead" IN (
              'Qualificada',
              'Oportunidade forte, alta prioridade',
              'Boa oportunidade, mas precisa de maturação'
            ) THEN 'Sim'
            ELSE 'Não'
          END AS "sales_sal_qualificada"
        FROM
          (
            SELECT
              "public"."deals"."hs_object_id",
              "public"."deals"."dealname",
              "public"."deals"."pipeline",
              "public"."deals"."dealstage",
              "public"."deals"."tipo_de_negociacao",
              CASE
                WHEN "public"."deals"."tipo_de_negociacao" IN ('Upsell', 'Cross Sell') THEN 'Upsell/CrossSell'
                ELSE "public"."deals"."tipo_de_negociacao"
              END AS "tipo_negociação_ajustada",
              "public"."deals"."tipo_de_receita",
              "public"."deals"."produto_principal",
              "public"."deals"."ramo_de_atuacao_do_negocio",
              -- ⬇ NOVOS CAMPOS (subselect)
              "public"."deals"."segmento_oficial" AS "segmento_oficial",
              "public"."deals"."sub_segmento_oficial" AS "sub_segmento_oficial",
              "public"."deals"."status_de_agendamento",
              "public"."deals"."valor_ganho",
              "public"."deals"."canal_de_aquisicao",
              "public"."deals"."campanha",
              "public"."deals"."coordenador",
              "public"."deals"."criado_por",
              "public"."deals"."pr_vendedor",
              "public"."deals"."analista_comercial",
              CAST("public"."deals"."createdate" AS date) AS "createdate",
              "public"."deals"."data_de_entrada_na_etapa_distribuicao_vendas_nmrr",
              "public"."deals"."data_de_prospect",
              "public"."deals"."etapa_data_de_tentando_contato",
              "public"."deals"."data_de_qualificacao",
              "public"."deals"."data_de_agendamento",
              "public"."deals"."fase_data_de_no_show",
              "public"."deals"."data_de_demonstracao",
              "public"."deals"."data_de_onboarding_trial",
              "public"."deals"."data_de_proposta",
              "public"."deals"."etapa_data_de_entrada_em_fechamento",
              "public"."deals"."sales_data_de_faturamento",
              "public"."deals"."closedate",
              "public"."deals"."notes_next_activity_date",
              "public"."deals"."data_prevista_reuniao",
              "public"."deals"."notes_last_updated",
              "public"."deals"."hs_lastmodifieddate",
              "public"."deals"."faturamento_anual_ic",
              "public"."deals"."fob_anual_ic",
              "public"."deals"."ultima_etapa_antes_do_perdido",
              "public"."deals"."temperatura_do_deal",
              "public"."deals"."presales_temperatura_v2",
              "public"."deals"."bu_business_unit",
              "public"."deals"."sales_business_unit",
              "public"."deals"."bu_country_unit",
              "public"."deals"."ic_sync_mkt_campanha",
              "public"."deals"."data_de_atribuicao_pre_vendas",
              "public"."deals"."sales_sal_sales_accepted_lead",
              -- Extras
              "public"."deals"."mkt_sla_de_atendimento" AS "mkt_sla_de_atendimento",
              "public"."deals"."origem_da_ultima_interacao_2_criacao_do_deal" AS "origem_da_ultima_interacao_2_criacao_do_deal",
              -- Aliases CURTOS (evitam truncamento)
              "public"."deals"."sales_a_empresa_estava_no_timing_para_uma_contratacao" AS "sales_timing_contratacao",
              "public"."deals"."sales_a_reuniao_foi_realizada_com_uma_persona_adequada" AS "sales_persona_adequada",
              "public"."deals"."sales_a_qualificacao_snippet_esta_preenchida_e_de_forma_clara" AS "sales_snippet_claro",
              "public"."deals"."sales_a_dor_mapeada_pelo_pre_vendedor" AS "sales_dor_mapeada",
              "public"."deals"."o_decisor_participou_da_reuniao" AS "decisor_participou",
              "Owners - Criado Por"."email" AS "Owners - Criado Por__email",
              "Owners - Criado Por"."fullname" AS "Owners - Criado Por__fullname",
              "Owners - Pr Vendedor"."email" AS "Owners - Pr Vendedor__email",
              "Owners - Pr Vendedor"."fullname" AS "Owners - Pr Vendedor__fullname",
              "Owners - Analista Comercial"."email" AS "Owners - Analista Comercial__email",
              "Owners - Analista Comercial"."fullname" AS "Owners - Analista Comercial__fullname",
              "Owners - Hubspot Owner"."email" AS "Owners - Hubspot Owner__email",
              "Owners - Hubspot Owner"."fullname" AS "Owners - Hubspot Owner__fullname",
              "Deal Stages Pipelines - Dealstage"."stage_label" AS "Deal Stages Pipelines - Dealstage__stage_label",
              "Deal Stages Pipelines - Dealstage"."deal_isclosed" AS "Deal Stages Pipelines - Dealstage__deal_isclosed",
              "Deal Stages Pipelines - Dealstage"."pipeline_label" AS "Deal Stages Pipelines - Dealstage__pipeline_label"
            FROM
              "public"."deals"
              LEFT JOIN "public"."owners" AS "Owners - Criado Por" ON "public"."deals"."criado_por" = "Owners - Criado Por"."id"
              LEFT JOIN "public"."owners" AS "Owners - Pr Vendedor" ON "public"."deals"."pr_vendedor" = "Owners - Pr Vendedor"."id"
              LEFT JOIN "public"."owners" AS "Owners - Analista Comercial" ON "public"."deals"."analista_comercial" = "Owners - Analista Comercial"."id"
              LEFT JOIN "public"."owners" AS "Owners - Hubspot Owner" ON "public"."deals"."hubspot_owner_id" = "Owners - Hubspot Owner"."id"
              LEFT JOIN "public"."deal_stages_pipelines" AS "Deal Stages Pipelines - Dealstage" ON "public"."deals"."dealstage" = CAST(
                "Deal Stages Pipelines - Dealstage"."stage_id" AS TEXT
              )
            WHERE
              COALESCE("public"."deals"."tipo_de_receita", '') <> 'Pontual'
              AND COALESCE("public"."deals"."tipo_de_negociacao", '') <> 'Variação Cambial'
            LIMIT
              1048575
          ) AS "source"
        LIMIT
          1048575
      ) AS "source"
      LEFT JOIN "public"."line_items" AS "Line Items - hs_object_id"
        ON "source"."hs_object_id" = "Line Items - hs_object_id"."deal_id"
    WHERE
      ("Line Items - hs_object_id"."archived" = FALSE)
      AND (
        ("Line Items - hs_object_id"."produto_principal" <> 'Onboarding')
        OR ("Line Items - hs_object_id"."produto_principal" IS NULL)
      )
  ) AS "source"
WHERE
  (
    LOWER("source"."Deal Stages Pipelines - Dealstage_stage_label") LIKE '%ganho%'
    OR LOWER("source"."Deal Stages Pipelines - Dealstage_stage_label") LIKE '%faturamento%'
  )
  AND "source"."closedate_ajustada" >= DATE_TRUNC('month', NOW())
  AND "source"."closedate_ajustada" < DATE_TRUNC('month', (NOW() + INTERVAL '1 month'))
  AND (
    LOWER("source"."Line Items - hs_object_id__produto_principal") LIKE '%logos%'
    OR LOWER("source"."Line Items - hs_object_id__produto_principal") LIKE '%logmanager%'
    OR LOWER("source"."Line Items - hs_object_id__produto_principal") LIKE '%catálogo%'
    OR LOWER("source"."Line Items - hs_object_id__produto_principal") LIKE '%logautomation%'
    OR LOWER("source"."Line Items - hs_object_id__produto_principal") LIKE '%automação%'
  )
GROUP BY
  "source"."Line Items - hs_object_id__produto_principal"
ORDER BY
  "Qtd New" DESC,
  "Qtd Expansão" DESC,
  "source"."Line Items - hs_object_id__produto_principal" ASC;
"""


def execute_query():
    """Executa a query e retorna os resultados"""
    try:
        print("=" * 80)
        print("🔍 TESTE DE QUERY - ANÁLISE DE PRODUTOS PARA PÁGINA DE NATAL")
        print("=" * 80)
        print(f"\n📊 Conectando ao banco de dados...")
        print(f"   Host: {DB_CONFIG['host']}")
        print(f"   Database: {DB_CONFIG['database']}")
        
        # Conecta ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print(f"\n⚡ Executando query...")
        start_time = datetime.now()
        
        cursor.execute(QUERY)
        results = cursor.fetchall()
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Query executada com sucesso!")
        print(f"⏱️  Tempo de execução: {execution_time:.2f} segundos")
        print(f"📈 Total de registros retornados: {len(results)}")
        
        # Exibe os resultados
        print("\n" + "=" * 80)
        print("📋 RESULTADOS:")
        print("=" * 80)
        
        if not results:
            print("\n⚠️  Nenhum resultado encontrado para o mês atual.")
        else:
            # Cabeçalho da tabela
            print(f"\n{'Produto Principal':<50} {'Qtd New':<15} {'Qtd Expansão':<15}")
            print("-" * 80)
            
            # Dados
            total_new = 0
            total_expansao = 0
            
            for row in results:
                produto = row.get('Line Items - hs_object_id_produto_principal', 'N/A') or 'N/A'
                qtd_new = row.get('Qtd New', 0) or 0
                qtd_expansao = row.get('Qtd Expansão', 0) or 0
                
                total_new += qtd_new
                total_expansao += qtd_expansao
                
                print(f"{produto[:48]:<50} {qtd_new:<15} {qtd_expansao:<15}")
            
            print("-" * 80)
            print(f"{'TOTAL':<50} {total_new:<15} {total_expansao:<15}")
        
        # Salva resultados em JSON
        output_file = 'query_natal_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Resultados salvos em: {output_file}")
        
        # Exibe detalhes de cada registro
        print("\n" + "=" * 80)
        print("📝 DETALHES DOS REGISTROS:")
        print("=" * 80)
        
        for idx, row in enumerate(results, 1):
            print(f"\n[{idx}] {row.get('Line Items - hs_object_id_produto_principal', 'N/A')}")
            print(f"    Qtd New: {row.get('Qtd New', 0)}")
            print(f"    Qtd Expansão: {row.get('Qtd Expansão', 0)}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
        
        return results
        
    except psycopg2.Error as e:
        print(f"\n❌ Erro ao executar query: {e}")
        import traceback
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    print("\n🚀 Iniciando teste de query para página de Natal...\n")
    results = execute_query()
    
    if results is None:
        sys.exit(1)
    else:
        sys.exit(0)

