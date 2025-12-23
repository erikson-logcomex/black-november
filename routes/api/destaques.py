"""
API Routes para destaques (MVPs da semana e do mês)
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import os
import requests
import time
from utils.auth import require_auth
from utils.mappings import get_analyst_name
from utils.datetime_utils import (
    get_week_start_brazil_utc,
    get_month_start_brazil_utc,
    parse_hubspot_timestamp,
    convert_utc_to_brazil
)

destaques_bp = Blueprint('destaques', __name__, url_prefix='/api/destaques')

# Deal ID a ser excluído (gambiarra temporária)
EXCLUDED_DEAL_ID = '34863967009'

def fetch_all_deals(url, headers, payload_base):
    """Função auxiliar para buscar deals com paginação"""
    deals = []
    after = None
    while True:
        payload = payload_base.copy()
        if after:
            payload["after"] = after
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 429:
            print(f"[AVISO] Rate limit atingido, aguardando 1 segundo...")
            time.sleep(1)
            continue
        elif response.status_code != 200:
            print(f"[AVISO] Erro na API: {response.status_code} - {response.text}")
            break
        
        data = response.json()
        results = data.get("results", [])
        deals.extend(results)
        
        paging = data.get("paging", {})
        after = paging.get("next", {}).get("after")
        
        if not after:
            break
        
        time.sleep(0.3)
    
    return deals

@destaques_bp.route('/evs')
@require_auth
def destaques_evs():
    """Retorna MVP de EVs da semana ou do mês (sem badges)"""
    try:
        periodo = request.args.get('periodo', 'semana')
        pipeline = request.args.get('pipeline', '6810518')
        
        if periodo == 'semana':
            start_utc = get_week_start_brazil_utc()
            periodo_nome = 'Semana'
        elif periodo == 'mes':
            start_utc = get_month_start_brazil_utc()
            periodo_nome = 'Mês'
        else:
            return jsonify({'error': 'Período inválido. Use "semana" ou "mes"'}), 400
        
        if pipeline == '6810518':
            stage = '6810524'
            date_property = 'hs_v2_date_entered_6810524'
            pipeline_name = 'NEW'
        elif pipeline == '4007305':
            stage = '13487286'
            date_property = 'hs_v2_date_entered_13487286'
            pipeline_name = 'Expansão'
        else:
            return jsonify({'error': 'Pipeline inválido. Use 6810518 (NEW) ou 4007305 (Expansão)'}), 400
        
        start_ms = int(start_utc.timestamp() * 1000)
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        hubspot_token = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
        url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
        headers = {
            'Authorization': f'Bearer {hubspot_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "pipeline", "operator": "EQ", "value": pipeline},
                    {"propertyName": date_property, "operator": "GTE", "value": str(start_ms)},
                    {"propertyName": date_property, "operator": "LT", "value": str(now_ms)},
                    {"propertyName": "dealstage", "operator": "EQ", "value": stage},
                    {"propertyName": "tipo_de_negociacao", "operator": "NEQ", "value": "Variação Cambial"}
                ]
            }],
            "properties": ["dealname", "analista_comercial", "closedate", "amount", date_property, "tipo_de_negociacao"],
            "limit": 200
        }
        
        all_deals = fetch_all_deals(url, headers, payload)
        print(f"[OK] Deals EVs ({pipeline_name}) encontrados: {len(all_deals)}")
        
        ev_stats = {}
        for deal in all_deals:
            deal_id = str(deal.get('id', ''))
            if deal_id == EXCLUDED_DEAL_ID:
                print(f"[AVISO] Deal {EXCLUDED_DEAL_ID} excluido dos calculos de EVs")
                continue
            
            props = deal.get('properties', {})
            owner_id = props.get('analista_comercial')
            amount = props.get('amount', '0')
            
            if owner_id:
                if owner_id not in ev_stats:
                    ev_stats[owner_id] = {'count': 0, 'revenue': 0}
                
                ev_stats[owner_id]['count'] += 1
                ev_stats[owner_id]['revenue'] += float(amount) if amount else 0
        
        if not ev_stats:
            return jsonify({
                'status': 'success',
                'periodo': periodo_nome,
                'pipeline': pipeline_name,
                'top3': []
            })
        
        top_evs = sorted(ev_stats.items(), key=lambda x: (x[1]['revenue'], x[1]['count']), reverse=True)
        
        top3 = []
        for i, (owner_id, stats) in enumerate(top_evs[:3]):
            user_name = get_analyst_name(owner_id)
            top3.append({
                'position': i + 1,
                'userId': owner_id,
                'userName': user_name,
                'dealCount': stats['count'],
                'revenue': stats['revenue']
            })
        
        return jsonify({
            'status': 'success',
            'periodo': periodo_nome,
            'pipeline': pipeline_name,
            'top3': top3
        })
        
    except Exception as e:
        print(f"Erro ao buscar destaques de EVs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@destaques_bp.route('/sdrs')
@require_auth
def destaques_sdrs():
    """Retorna MVP de SDRs da semana ou do mês (sem badges)"""
    try:
        periodo = request.args.get('periodo', 'semana')
        pipeline = request.args.get('pipeline', '6810518')
        
        if periodo == 'semana':
            start_utc = get_week_start_brazil_utc()
            periodo_nome = 'Semana'
        elif periodo == 'mes':
            start_utc = get_month_start_brazil_utc()
            periodo_nome = 'Mês'
        else:
            return jsonify({'error': 'Período inválido. Use "semana" ou "mes"'}), 400
        
        if pipeline == '6810518':
            date_property = 'hs_v2_date_entered_7417230'
            pipeline_name = 'NEW'
        elif pipeline == '4007305':
            date_property = 'hs_v2_date_entered_13487283'
            pipeline_name = 'Expansão'
        else:
            return jsonify({'error': 'Pipeline inválido. Use 6810518 (NEW) ou 4007305 (Expansão)'}), 400
        
        start_ms = int(start_utc.timestamp() * 1000)
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        hubspot_token = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
        url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
        headers = {
            'Authorization': f'Bearer {hubspot_token}',
            'Content-Type': 'application/json'
        }
        
        payload_base = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "pipeline", "operator": "EQ", "value": pipeline},
                    {"propertyName": date_property, "operator": "GTE", "value": str(start_ms)},
                    {"propertyName": date_property, "operator": "LT", "value": str(now_ms)}
                ]
            }],
            "properties": ["dealname", "pr_vendedor", date_property],
            "limit": 200
        }
        
        deals = fetch_all_deals(url, headers, payload_base)
        print(f"[OK] Deals SDRs ({pipeline_name}) encontrados: {len(deals)}")
        
        sdr_stats = {}
        for deal in deals:
            deal_id = str(deal.get('id', ''))
            if deal_id == EXCLUDED_DEAL_ID:
                print(f"[AVISO] Deal {EXCLUDED_DEAL_ID} excluido dos calculos de SDRs")
                continue
            
            props = deal.get('properties', {})
            sdr_id = props.get('pr_vendedor')
            timestamp = props.get(date_property)
            
            if sdr_id and timestamp:
                dt_utc = parse_hubspot_timestamp(timestamp)
                dt_brazil = convert_utc_to_brazil(dt_utc)
                
                if sdr_id not in sdr_stats:
                    sdr_stats[sdr_id] = {'count': 0, 'timestamps': []}
                
                sdr_stats[sdr_id]['count'] += 1
                sdr_stats[sdr_id]['timestamps'].append(dt_brazil)
        
        if not sdr_stats:
            return jsonify({
                'status': 'success',
                'periodo': periodo_nome,
                'pipeline': pipeline_name,
                'top3': []
            })
        
        max_datetime = datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        top_sdrs = sorted(sdr_stats.items(), key=lambda x: (-x[1]['count'], max(x[1]['timestamps']) if x[1]['timestamps'] else max_datetime))
        
        top3 = []
        for i, (sdr_id, stats) in enumerate(top_sdrs[:3]):
            user_name = get_analyst_name(sdr_id)
            top3.append({
                'position': i + 1,
                'userId': sdr_id,
                'userName': user_name,
                'scheduledCount': stats['count']
            })
        
        return jsonify({
            'status': 'success',
            'periodo': periodo_nome,
            'pipeline': pipeline_name,
            'top3': top3
        })
        
    except Exception as e:
        print(f"Erro ao buscar destaques de SDRs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@destaques_bp.route('/ldrs')
@require_auth
def destaques_ldrs():
    """Retorna MVP de LDRs da semana ou do mês (sem badges)"""
    try:
        periodo = request.args.get('periodo', 'semana')
        pipeline = request.args.get('pipeline', '6810518')
        
        if periodo == 'semana':
            start_utc = get_week_start_brazil_utc()
            periodo_nome = 'Semana'
        elif periodo == 'mes':
            start_utc = get_month_start_brazil_utc()
            periodo_nome = 'Mês'
        else:
            return jsonify({'error': 'Período inválido. Use "semana" ou "mes"'}), 400
        
        if pipeline == '6810518':
            stage = '6810524'
            date_property = 'hs_v2_date_entered_6810524'
            pipeline_name = 'NEW'
        elif pipeline == '4007305':
            stage = '13487286'
            date_property = 'hs_v2_date_entered_13487286'
            pipeline_name = 'Expansão'
        else:
            return jsonify({'error': 'Pipeline inválido. Use 6810518 (NEW) ou 4007305 (Expansão)'}), 400
        
        start_ms = int(start_utc.timestamp() * 1000)
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        hubspot_token = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
        url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
        headers = {
            'Authorization': f'Bearer {hubspot_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "pipeline", "operator": "EQ", "value": pipeline},
                    {"propertyName": date_property, "operator": "GTE", "value": str(start_ms)},
                    {"propertyName": date_property, "operator": "LT", "value": str(now_ms)},
                    {"propertyName": "dealstage", "operator": "EQ", "value": stage},
                    {"propertyName": "tipo_de_negociacao", "operator": "NEQ", "value": "Variação Cambial"}
                ]
            }],
            "properties": ["dealname", "criado_por_", "closedate", "amount", date_property, "tipo_de_negociacao"],
            "limit": 200
        }
        
        all_deals = fetch_all_deals(url, headers, payload)
        print(f"[OK] Deals LDRs ({pipeline_name}) encontrados: {len(all_deals)}")
        
        ldr_stats = {}
        for deal in all_deals:
            deal_id = str(deal.get('id', ''))
            if deal_id == EXCLUDED_DEAL_ID:
                print(f"[AVISO] Deal {EXCLUDED_DEAL_ID} excluido dos calculos de LDRs")
                continue
            
            props = deal.get('properties', {})
            ldr_id = props.get('criado_por_')
            amount = props.get('amount', '0')
            
            if ldr_id:
                if ldr_id not in ldr_stats:
                    ldr_stats[ldr_id] = {'count': 0, 'revenue': 0}
                
                ldr_stats[ldr_id]['count'] += 1
                ldr_stats[ldr_id]['revenue'] += float(amount) if amount else 0
        
        if not ldr_stats:
            return jsonify({
                'status': 'success',
                'periodo': periodo_nome,
                'pipeline': pipeline_name,
                'top3': []
            })
        
        top_ldrs = sorted(ldr_stats.items(), key=lambda x: (x[1]['count'], x[1]['revenue']), reverse=True)
        
        top3 = []
        for i, (ldr_id, stats) in enumerate(top_ldrs[:3]):
            user_name = get_analyst_name(ldr_id)
            top3.append({
                'position': i + 1,
                'userId': ldr_id,
                'userName': user_name,
                'wonDealsCount': stats['count'],
                'revenue': stats['revenue']
            })
        
        return jsonify({
            'status': 'success',
            'periodo': periodo_nome,
            'pipeline': pipeline_name,
            'top3': top3
        })
        
    except Exception as e:
        print(f"Erro ao buscar destaques de LDRs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

