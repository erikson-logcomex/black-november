"""
Script de teste para comparar pipeline previsto para hoje
entre HubSpot API e Banco de Dados PostgreSQL

Verifica se há divergências nos dados de deals previstos para fechar hoje
"""

import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

# Configurações
HUBSPOT_API_TOKEN = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_DATABASE = os.getenv('PG_DATABASE_HUBSPOT', 'hubspot-sync')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')

# Timezone Brasil (GMT-3)
BRAZIL_TZ = timezone(timedelta(hours=-3))

def get_today_date_brazil():
    """Retorna a data de hoje no Brasil (YYYY-MM-DD)"""
    now_brazil = datetime.now(BRAZIL_TZ)
    return now_brazil.strftime('%Y-%m-%d')

def inspect_specific_deal(deal_id):
    """
    Busca detalhes completos de um deal específico do HubSpot para investigação
    """
    print(f"\n🔍 INVESTIGANDO DEAL {deal_id} no HubSpot...")
    
    url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "properties": [
            "dealname",
            "amount",
            "closedate",
            "dealstage",
            "tipo_de_receita",
            "tipo_de_negociacao",
            "pipeline",
            "valor_ganho",
            "hs_is_closed_won",
            "hs_is_closed"
        ]
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        deal = response.json()
        props = deal.get("properties", {})
        
        print(f"\n📋 Detalhes do Deal:")
        print(f"   Nome: {props.get('dealname', 'N/A')}")
        print(f"   Amount: R$ {float(props.get('amount') or 0):,.2f}")
        print(f"   Closedate: {props.get('closedate', 'N/A')}")
        print(f"   Deal Stage ID: {props.get('dealstage', 'N/A')}")
        print(f"   Is Closed Won: {props.get('hs_is_closed_won', 'N/A')}")
        print(f"   Is Closed: {props.get('hs_is_closed', 'N/A')}")
        print(f"   Tipo Receita: {props.get('tipo_de_receita', 'N/A')}")
        print(f"   Tipo Negociação: {props.get('tipo_de_negociacao', 'N/A')}")
        print(f"   Pipeline: {props.get('pipeline', 'N/A')}")
        
        # Busca label do stage
        dealstage_id = props.get('dealstage')
        if dealstage_id:
            pipelines_url = "https://api.hubapi.com/crm/v3/pipelines/deals"
            pipelines_response = requests.get(pipelines_url, headers=headers)
            if pipelines_response.status_code == 200:
                pipelines_data = pipelines_response.json()
                for pipeline in pipelines_data.get("results", []):
                    for stage in pipeline.get("stages", []):
                        if stage.get("id") == dealstage_id:
                            print(f"   Stage Label: {stage.get('label')}")
                            print(f"   Pipeline Label: {pipeline.get('label')}")
                            break
        
        return deal
    else:
        print(f"❌ Erro ao buscar deal: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

def fetch_deals_from_hubspot():
    """
    Busca deals do HubSpot com os mesmos critérios da query SQL:
    - closedate = hoje (Brasil)
    - Não ganhos/fechados
    - Tipo de receita != Pontual
    - Tipo de negociação != Variação Cambial
    - amount > 0
    """
    print("\n🔍 Buscando deals do HubSpot API...")
    
    url = "https://api.hubapi.com/crm/v3/objects/deals/search"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    today_brazil = get_today_date_brazil()
    today_start_timestamp = int(datetime.strptime(today_brazil, '%Y-%m-%d').replace(tzinfo=BRAZIL_TZ).timestamp() * 1000)
    today_end_timestamp = today_start_timestamp + (24 * 60 * 60 * 1000) - 1
    
    # Filtros do HubSpot (equivalentes à query SQL)
    payload = {
        "filterGroups": [
            {
                "filters": [
                    # closedate = hoje
                    {
                        "propertyName": "closedate",
                        "operator": "GTE",
                        "value": str(today_start_timestamp)
                    },
                    {
                        "propertyName": "closedate",
                        "operator": "LTE",
                        "value": str(today_end_timestamp)
                    },
                    # amount > 0
                    {
                        "propertyName": "amount",
                        "operator": "GT",
                        "value": "0"
                    },
                    # Tipo de receita != Pontual
                    {
                        "propertyName": "tipo_de_receita",
                        "operator": "NEQ",
                        "value": "Pontual"
                    },
                    # Tipo de negociação != Variação Cambial
                    {
                        "propertyName": "tipo_de_negociacao",
                        "operator": "NEQ",
                        "value": "Variação Cambial"
                    },
                    # Vamos buscar todos e filtrar depois com base no stage_label
                ]
            }
        ],
        "properties": [
            "dealname",
            "amount",
            "closedate",
            "dealstage",
            "tipo_de_receita",
            "tipo_de_negociacao",
            "pipeline",
            "valor_ganho",
            "hs_is_closed_won",
            "hs_is_closed"
        ],
        "limit": 100
    }
    
    all_deals = []
    after = None
    
    while True:
        if after:
            payload["after"] = after
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro na API do HubSpot: {response.status_code}")
            print(f"Resposta: {response.text}")
            break
        
        data = response.json()
        results = data.get("results", [])
        all_deals.extend(results)
        
        # Paginação
        paging = data.get("paging", {})
        after = paging.get("next", {}).get("after")
        
        if not after:
            break
    
    print(f"✅ Total de deals encontrados no HubSpot: {len(all_deals)}")
    
    # Busca informações de pipelines e stages para filtrar corretamente
    print("🔍 Buscando informações de pipelines...")
    pipelines_url = "https://api.hubapi.com/crm/v3/pipelines/deals"
    pipelines_response = requests.get(pipelines_url, headers=headers)
    
    stage_labels = {}
    if pipelines_response.status_code == 200:
        pipelines_data = pipelines_response.json()
        for pipeline in pipelines_data.get("results", []):
            for stage in pipeline.get("stages", []):
                stage_id = stage.get("id")
                stage_label = stage.get("label", "").lower()
                stage_labels[stage_id] = {
                    "label": stage_label,
                    "is_closed": "ganho" in stage_label or "faturamento" in stage_label or "aguardando" in stage_label
                }
    
    # Processa e filtra deals
    processed_deals = []
    filtered_out = []
    total_amount = 0
    
    for deal in all_deals:
        props = deal.get("properties", {})
        
        # Validações adicionais (equivalente ao SQL)
        tipo_receita = props.get("tipo_de_receita", "")
        tipo_negociacao = props.get("tipo_de_negociacao", "")
        amount = float(props.get("amount") or 0)
        dealstage = props.get("dealstage", "")
        hs_is_closed_won = props.get("hs_is_closed_won", "false")
        hs_is_closed = props.get("hs_is_closed", "false")
        
        # Pula se for Pontual ou Variação Cambial
        if tipo_receita == "Pontual" or tipo_negociacao == "Variação Cambial":
            continue
        
        # Pula se amount <= 0
        if amount <= 0:
            continue
        
        # CRÍTICO: Filtra deals que já estão ganhos/fechados/perdidos
        stage_info = stage_labels.get(dealstage, {})
        stage_label = stage_info.get("label", "").lower()
        is_closed_stage = stage_info.get("is_closed", False)
        
        # Verifica se é deal perdido/churn
        is_lost = "perdido" in stage_label or "churn" in stage_label
        
        # CORRIGIDO: Usa APENAS stage_label para filtrar (igual ao SQL do banco)
        # SQL do banco: stage_label NOT LIKE ganho/faturamento/aguardando/perdido
        # Não usa hs_is_closed porque o banco permite deal_isclosed = NULL
        if is_closed_stage or is_lost or hs_is_closed_won == "true":
            reason_parts = []
            if hs_is_closed_won == "true":
                reason_parts.append("fechado como ganho")
            if is_closed_stage:
                reason_parts.append("stage de ganho/faturamento/aguardando")
            if is_lost:
                reason_parts.append("deal perdido/churn")
            
            filtered_out.append({
                "id": deal.get("id"),
                "dealname": props.get("dealname", ""),
                "amount": amount,
                "stage_label": stage_label,
                "reason": " | ".join(reason_parts)
            })
            continue
        
        processed_deals.append({
            "id": deal.get("id"),
            "dealname": props.get("dealname", ""),
            "amount": amount,
            "closedate": props.get("closedate", ""),
            "dealstage": dealstage,
            "stage_label": stage_label,
            "tipo_receita": tipo_receita,
            "tipo_negociacao": tipo_negociacao
        })
        total_amount += amount
    
    if filtered_out:
        print(f"🚫 {len(filtered_out)} deal(s) filtrados por já estarem ganhos/fechados")
        print("\nPrimeiros 5 deals filtrados:")
        for deal in filtered_out[:5]:
            print(f"   - ID {deal['id']}: {deal['dealname']} - R$ {deal['amount']:,.2f}")
            print(f"     Stage: {deal['stage_label']} | Razão: {deal['reason']}")
    
    print(f"\n✅ Total de deals VÁLIDOS (não ganhos): {len(processed_deals)}")
    if processed_deals:
        print("\nPrimeiros 5 deals válidos:")
        for deal in processed_deals[:5]:
            print(f"   - ID {deal['id']}: {deal['dealname']} - R$ {deal['amount']:,.2f}")
            print(f"     Stage: {deal['stage_label']}")
    
    return processed_deals, total_amount

def fetch_deals_from_database():
    """
    Busca deals do banco de dados usando a mesma query SQL
    """
    print("\n🔍 Buscando deals do Banco de Dados...")
    
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD
    )
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
                d.amount,
                d.valor_ganho,
                d.closedate,
                d.data_prevista_reuniao,
                p.stage_label,
                p.deal_isclosed,
                p.pipeline_label
            FROM deals d
            LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
            WHERE COALESCE(d.tipo_de_receita, '') <> 'Pontual'
                AND COALESCE(d.tipo_de_negociacao, '') <> 'Variação Cambial'
        ),
        previstos_hoje AS (
            SELECT *
            FROM base
            WHERE 
                -- Previsão de fechamento é HOJE
                DATE(closedate - INTERVAL '3 hour') = DATE(CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
                -- Ainda NÃO está ganho/fechado
                AND (
                    deal_isclosed = FALSE 
                    OR deal_isclosed IS NULL
                    OR (LOWER(stage_label) NOT LIKE '%ganho%' 
                        AND LOWER(stage_label) NOT LIKE '%faturamento%'
                        AND LOWER(stage_label) NOT LIKE '%aguardando%')
                )
                -- Tem valor
                AND (amount IS NOT NULL AND amount > 0)
        )
        SELECT 
            hs_object_id,
            dealname,
            amount,
            closedate,
            dealstage,
            tipo_de_receita,
            tipo_de_negociacao,
            stage_label
        FROM previstos_hoje
        ORDER BY amount DESC
    """
    
    cursor.execute(query)
    deals = cursor.fetchall()
    
    total_amount = float(sum(deal['amount'] for deal in deals))
    
    cursor.close()
    conn.close()
    
    print(f"✅ Total de deals encontrados no Banco: {len(deals)}")
    
    return deals, total_amount

def compare_results(hubspot_deals, hubspot_total, db_deals, db_total):
    """
    Compara resultados entre HubSpot e Banco de Dados
    """
    print("\n" + "="*80)
    print("📊 COMPARAÇÃO: HUBSPOT vs BANCO DE DADOS")
    print("="*80)
    
    print(f"\n{'Métrica':<30} {'HubSpot':<20} {'Banco de Dados':<20} {'Divergência':<15}")
    print("-"*85)
    
    # Total de deals
    deals_diff = len(hubspot_deals) - len(db_deals)
    deals_diff_pct = (deals_diff / max(len(db_deals), 1)) * 100 if len(db_deals) > 0 else 0
    print(f"{'Total de Deals':<30} {len(hubspot_deals):<20} {len(db_deals):<20} {deals_diff:+d} ({deals_diff_pct:+.1f}%)")
    
    # Total de pipeline
    pipeline_diff = hubspot_total - db_total
    pipeline_diff_pct = (pipeline_diff / max(db_total, 1)) * 100 if db_total > 0 else 0
    print(f"{'Pipeline Total':<30} {'R$ {:,.2f}'.format(hubspot_total):<20} {'R$ {:,.2f}'.format(db_total):<20} R$ {pipeline_diff:+,.2f} ({pipeline_diff_pct:+.1f}%)")
    
    # Ticket médio
    hubspot_avg = hubspot_total / len(hubspot_deals) if len(hubspot_deals) > 0 else 0
    db_avg = db_total / len(db_deals) if len(db_deals) > 0 else 0
    avg_diff = hubspot_avg - db_avg
    print(f"{'Ticket Médio':<30} {'R$ {:,.2f}'.format(hubspot_avg):<20} {'R$ {:,.2f}'.format(db_avg):<20} R$ {avg_diff:+,.2f}")
    
    print("\n" + "="*80)
    
    # Identifica deals que estão em um mas não no outro
    hubspot_ids = {deal['id'] for deal in hubspot_deals}
    db_ids = {str(deal['hs_object_id']) for deal in db_deals}
    
    only_hubspot = hubspot_ids - db_ids
    only_db = db_ids - hubspot_ids
    
    if only_hubspot:
        print(f"\n⚠️  {len(only_hubspot)} deal(s) APENAS no HubSpot:")
        for deal_id in list(only_hubspot)[:5]:  # Mostra só os 5 primeiros
            deal = next(d for d in hubspot_deals if d['id'] == deal_id)
            print(f"   - ID {deal_id}: {deal['dealname']} - R$ {deal['amount']:,.2f}")
        if len(only_hubspot) > 5:
            print(f"   ... e mais {len(only_hubspot) - 5} deal(s)")
    
    if only_db:
        print(f"\n⚠️  {len(only_db)} deal(s) APENAS no Banco:")
        for deal_id in list(only_db)[:5]:  # Mostra só os 5 primeiros
            deal = next(d for d in db_deals if str(d['hs_object_id']) == deal_id)
            print(f"   - ID {deal_id}: {deal['dealname']} - R$ {deal['amount']:,.2f}")
        if len(only_db) > 5:
            print(f"   ... e mais {len(only_db) - 5} deal(s)")
    
    if not only_hubspot and not only_db:
        print("\n✅ Todos os deals estão sincronizados!")
    
    # Verifica divergências de valores
    print(f"\n📋 Verificando valores dos deals em comum...")
    value_mismatches = []
    for deal_id in hubspot_ids & db_ids:
        hubspot_deal = next(d for d in hubspot_deals if d['id'] == deal_id)
        db_deal = next(d for d in db_deals if str(d['hs_object_id']) == deal_id)
        
        if abs(hubspot_deal['amount'] - float(db_deal['amount'])) > 0.01:
            value_mismatches.append({
                'id': deal_id,
                'name': hubspot_deal['dealname'],
                'hubspot_amount': hubspot_deal['amount'],
                'db_amount': float(db_deal['amount']),
                'diff': hubspot_deal['amount'] - float(db_deal['amount'])
            })
    
    if value_mismatches:
        print(f"\n⚠️  {len(value_mismatches)} deal(s) com valores divergentes:")
        for mismatch in value_mismatches[:5]:
            print(f"   - {mismatch['name']} (ID {mismatch['id']}):")
            print(f"     HubSpot: R$ {mismatch['hubspot_amount']:,.2f}")
            print(f"     Banco:   R$ {mismatch['db_amount']:,.2f}")
            print(f"     Diff:    R$ {mismatch['diff']:+,.2f}")
        if len(value_mismatches) > 5:
            print(f"   ... e mais {len(value_mismatches) - 5} deal(s)")
    else:
        print("✅ Todos os valores estão consistentes!")

def main():
    print("="*80)
    print("🔍 TESTE DE DIVERGÊNCIA: PIPELINE PREVISTO HOJE")
    print(f"Data de hoje (Brasil): {get_today_date_brazil()}")
    print("="*80)
    
    # Investiga deals específicos
    suspect_deal_ids = [
        "46629777725",  # Gator International - estava no HubSpot mas não deveria
        "43058776248",  # IBETEX - está no banco mas não no HubSpot
    ]
    for deal_id in suspect_deal_ids:
        inspect_specific_deal(deal_id)
        print("\n" + "="*80)
    
    # Busca dados
    hubspot_deals, hubspot_total = fetch_deals_from_hubspot()
    db_deals, db_total = fetch_deals_from_database()
    
    # Compara
    compare_results(hubspot_deals, hubspot_total, db_deals, db_total)
    
    print("\n" + "="*80)
    print("✅ Teste concluído!")
    print("="*80)

if __name__ == "__main__":
    main()
