"""
Debug: Por que deals legítimos não geraram notificação no webhook?

Condições do Webhook HubSpot:
1. Pipeline: Vendas NMRR OU Expansão
2. Stage: Múltiplos (incluindo Ganho e Faturamento)
3. Associado a Orçamento com:
   - Assinaturas no ESign >= 1 E atualizado nos últimos 7 dias
   OU
   - Assinaturas no ESign é desconhecido

Deals encontrados hoje:
1. Deal #43292480376 - Andreza Sandim - R$ 6.450 (Stage: 13487286 - Ganho Expansão)
2. Deal #43373844371 - Andreza Sandim - R$ 1.750 (Stage: 13487286 - Ganho Expansão)
3. Deal #47668656998 - Inaiara Lorusso - R$ 5.083 (Stage: 13487286 - Ganho Expansão)

Hipóteses:
- Deals não estão associados a Orçamento
- Orçamento não tem assinaturas ESign
- Assinaturas não foram atualizadas nos últimos 7 dias
- Stage "Ganho" não está na lista de stages do webhook (mas deveria estar!)
"""

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

HUBSPOT_TOKEN = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')

# Deals encontrados hoje que NÃO geraram notificação
DEALS_TO_CHECK = [
    {'id': '43292480376', 'name': 'BORRACHAS VIPAL', 'owner': 'Andreza Sandim', 'stage': '13487286'},
    {'id': '43373844371', 'name': 'ASIA SHIPPING', 'owner': 'Andreza Sandim', 'stage': '13487286'},
    {'id': '47668656998', 'name': 'INTEBRA COMERCIAL', 'owner': 'Inaiara Lorusso', 'stage': '13487286'},
]

def get_deal_details(deal_id):
    """Busca detalhes completos de um deal incluindo associações"""
    url = f'https://api.hubapi.com/crm/v3/objects/deals/{deal_id}'
    headers = {
        'Authorization': f'Bearer {HUBSPOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'properties': [
            'dealname',
            'dealstage',
            'pipeline',
            'closedate',
            'amount',
            'hs_lastmodifieddate'
        ],
        'associations': ['quotes', 'line_items']  # Busca orçamentos associados
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  ❌ Erro ao buscar deal {deal_id}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return None

def get_deal_associations(deal_id):
    """Busca associações de um deal (quotes)"""
    url = f'https://api.hubapi.com/crm/v3/objects/deals/{deal_id}/associations/quotes'
    headers = {
        'Authorization': f'Bearer {HUBSPOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('results', [])
        else:
            return []
            
    except Exception as e:
        print(f"  ⚠️ Erro ao buscar associações: {e}")
        return []

def get_quote_details(quote_id):
    """Busca detalhes de um orçamento (quote)"""
    url = f'https://api.hubapi.com/crm/v3/objects/quotes/{quote_id}'
    headers = {
        'Authorization': f'Bearer {HUBSPOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'properties': [
            'hs_title',
            'hs_esign_num_signed',  # Assinaturas no ESign
            'hs_lastmodifieddate'
        ]
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  ⚠️ Erro ao buscar quote {quote_id}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ⚠️ Erro: {e}")
        return None

def check_webhook_conditions(deal_info, quote_info=None):
    """Verifica se o deal atende às condições do webhook"""
    
    print("\n  🔍 VERIFICANDO CONDIÇÕES DO WEBHOOK:")
    
    stage = deal_info.get('properties', {}).get('dealstage')
    pipeline = deal_info.get('properties', {}).get('pipeline')
    
    # Condição 1: Pipeline
    valid_pipelines = ['6810518', '4007305']  # Vendas NMRR, Expansão
    pipeline_ok = pipeline in valid_pipelines
    print(f"    {'✅' if pipeline_ok else '❌'} Pipeline: {pipeline} ({'OK' if pipeline_ok else 'INVÁLIDO'})")
    
    # Condição 2: Stage
    # IMPORTANTE: Verificar se "Ganho" está na lista do webhook!
    webhook_stages = [
        '13487286',  # Ganho (Expansão) - APARECE NO NOSSO RESULTADO
        '6810524',   # Ganho (Vendas NMRR)
        '16657792',  # Faturamento (Vendas NMRR)
        '33646228',  # Faturamento (Expansão)
        # ... outros stages de Proposta, Negociação, etc
    ]
    
    # PROBLEMA IDENTIFICADO: Stage "Ganho" pode NÃO estar na lista do webhook!
    stage_ok = stage in webhook_stages
    print(f"    {'✅' if stage_ok else '❌'} Stage: {stage} ({'OK' if stage_ok else 'NÃO ESTÁ NA LISTA DO WEBHOOK'})")
    
    # Condição 3: Orçamento associado
    if quote_info is None:
        print(f"    ❌ Orçamento: NÃO ASSOCIADO (CONDIÇÃO NÃO ATENDIDA)")
        return False
    
    print(f"    ✅ Orçamento: ASSOCIADO (ID: {quote_info.get('id')})")
    
    # Condição 4: Assinaturas ESign
    esign_signed = quote_info.get('properties', {}).get('hs_esign_num_signed')
    esign_modified = quote_info.get('properties', {}).get('hs_lastmodifieddate')
    
    print(f"    📝 Assinaturas ESign: {esign_signed if esign_signed else 'DESCONHECIDO'}")
    
    if esign_signed and esign_signed != '':
        num_signed = int(esign_signed)
        if num_signed >= 1:
            # Verifica se foi atualizado nos últimos 7 dias
            if esign_modified:
                from datetime import datetime, timezone, timedelta
                modified_dt = datetime.fromisoformat(esign_modified.replace('Z', '+00:00'))
                seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
                
                updated_recently = modified_dt >= seven_days_ago
                print(f"    {'✅' if updated_recently else '❌'} Atualizado recentemente: {updated_recently} (última atualização: {modified_dt.strftime('%Y-%m-%d %H:%M')})")
                
                return pipeline_ok and stage_ok and updated_recently
            else:
                print(f"    ⚠️ Data de modificação não disponível")
                return False
        else:
            print(f"    ❌ Assinaturas insuficientes: {num_signed} (necessário >= 1)")
            return False
    else:
        # ESign desconhecido - atende à condição do Grupo 2
        print(f"    ✅ ESign DESCONHECIDO - Atende condição do Grupo 2")
        return pipeline_ok and stage_ok

def main():
    print("="*80)
    print("🔍 DEBUG: POR QUE DEALS NÃO GERARAM NOTIFICAÇÃO?")
    print("="*80)
    
    print("\n📋 Condições do Webhook HubSpot:")
    print("  Grupo 1:")
    print("    - Pipeline: Vendas NMRR OU Expansão")
    print("    - Stage: Lista específica")
    print("    - Orçamento com ESign >= 1 E atualizado últimos 7 dias")
    print("  Grupo 2:")
    print("    - Pipeline: Vendas NMRR OU Expansão")
    print("    - Stage: Faturamento")
    print("    - Orçamento com ESign desconhecido")
    
    print("\n" + "="*80)
    print("ANÁLISE DOS DEALS")
    print("="*80)
    
    for deal_data in DEALS_TO_CHECK:
        deal_id = deal_data['id']
        
        print(f"\n{'─'*80}")
        print(f"DEAL: {deal_data['name']} (ID: {deal_id})")
        print(f"Owner: {deal_data['owner']}")
        print(f"Stage ID: {deal_data['stage']}")
        print(f"{'─'*80}")
        
        # 1. Busca detalhes do deal
        print("\n  📥 Buscando detalhes do deal...")
        deal_info = get_deal_details(deal_id)
        
        if not deal_info:
            print("  ❌ Não foi possível buscar detalhes do deal")
            continue
        
        # 2. Busca orçamentos associados
        print("\n  📥 Buscando orçamentos associados...")
        quotes = get_deal_associations(deal_id)
        
        if not quotes or len(quotes) == 0:
            print("  ❌ NENHUM ORÇAMENTO ASSOCIADO!")
            print("  💡 MOTIVO: Deal não tem orçamento = WEBHOOK NÃO DISPARA")
            check_webhook_conditions(deal_info, None)
            continue
        
        print(f"  ✅ {len(quotes)} orçamento(s) encontrado(s)")
        
        # 3. Verifica cada orçamento
        for quote_assoc in quotes:
            quote_id = quote_assoc.get('id')
            print(f"\n  📄 Orçamento ID: {quote_id}")
            
            quote_info = get_quote_details(quote_id)
            
            if quote_info:
                # Verifica condições
                meets_conditions = check_webhook_conditions(deal_info, quote_info)
                
                if meets_conditions:
                    print(f"\n  ✅ DEVERIA TER GERADO NOTIFICAÇÃO!")
                    print(f"  🔍 Verificar logs do webhook no HubSpot")
                else:
                    print(f"\n  ❌ NÃO ATENDE CONDIÇÕES DO WEBHOOK")
    
    print("\n" + "="*80)
    print("💡 POSSÍVEIS CAUSAS")
    print("="*80)
    print("""
1. ❌ Deals não têm orçamento associado
2. ❌ Orçamento não tem assinaturas ESign
3. ❌ Assinaturas não foram atualizadas nos últimos 7 dias
4. ⚠️ Stage "Ganho" (13487286) NÃO está na lista do webhook
   - Webhook só dispara para stages específicos
   - "Ganho" pode não estar incluído
   - Verificar configuração do workflow no HubSpot
5. ⚠️ Webhook pode estar configurado apenas para MUDANÇAS de stage
   - Se deal já estava em "Ganho", não dispara novamente
    """)

if __name__ == '__main__':
    main()
