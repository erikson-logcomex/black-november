"""
API Routes para Hall da Fama (rankings com badges)
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone, timedelta
import os
import requests
from utils.mappings import get_analyst_name
from utils.datetime_utils import (
    get_today_brazil_start_utc,
    convert_utc_to_brazil,
    parse_hubspot_timestamp
)
from utils.badges import detect_badges, save_badge_to_database
from utils.cache_manager import get_cache, get_cache_lock

hall_da_fama_bp = Blueprint('hall_da_fama', __name__, url_prefix='/api/hall-da-fama')

@hall_da_fama_bp.route('/evs-realtime')
def hall_da_fama_evs_realtime():
    """Retorna Top 5 EVs com badges em tempo real via HubSpot API"""
    _data_cache = get_cache()
    _cache_lock = get_cache_lock()
    
    use_cache = request.args.get('use_cache', 'false').lower() == 'true'
    if use_cache and _data_cache.get('hall_evs'):
        response = jsonify(_data_cache['hall_evs'])
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['X-Cache'] = 'HIT'
        return response
    
    try:
        today_start_utc = get_today_brazil_start_utc()
        today_start_ms = int(today_start_utc.timestamp() * 1000)
        tomorrow_start_utc = today_start_utc + timedelta(days=1)
        tomorrow_start_ms = int(tomorrow_start_utc.timestamp() * 1000)
        
        hubspot_token = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
        url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
        headers = {
            'Authorization': f'Bearer {hubspot_token}',
            'Content-Type': 'application/json'
        }
        
        all_deals = []
        
        # 1. Ganho (Vendas NMRR) - Stage 6810524
        payload_nmrr = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "hs_v2_date_entered_6810524", "operator": "GTE", "value": str(today_start_ms)},
                    {"propertyName": "hs_v2_date_entered_6810524", "operator": "LT", "value": str(tomorrow_start_ms)},
                    {"propertyName": "dealstage", "operator": "EQ", "value": "6810524"},
                    {"propertyName": "tipo_de_negociacao", "operator": "NEQ", "value": "Variação Cambial"}
                ]
            }],
            "properties": ["dealname", "analista_comercial", "closedate", "amount", "hs_v2_date_entered_6810524", "tipo_de_negociacao"],
            "limit": 100
        }
        
        response_nmrr = requests.post(url, headers=headers, json=payload_nmrr, timeout=25)
        if response_nmrr.status_code == 200:
            all_deals.extend(response_nmrr.json().get('results', []))
        
        # 2. Ganho (Expansão) - Stage 13487286
        payload_expansao = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "hs_v2_date_entered_13487286", "operator": "GTE", "value": str(today_start_ms)},
                    {"propertyName": "hs_v2_date_entered_13487286", "operator": "LT", "value": str(tomorrow_start_ms)},
                    {"propertyName": "dealstage", "operator": "EQ", "value": "13487286"},
                    {"propertyName": "tipo_de_negociacao", "operator": "NEQ", "value": "Variação Cambial"}
                ]
            }],
            "properties": ["dealname", "analista_comercial", "closedate", "amount", "hs_v2_date_entered_13487286", "tipo_de_negociacao"],
            "limit": 100
        }
        
        response_expansao = requests.post(url, headers=headers, json=payload_expansao, timeout=25)
        if response_expansao.status_code == 200:
            all_deals.extend(response_expansao.json().get('results', []))
        
        if response_nmrr.status_code != 200 and response_expansao.status_code != 200:
            return jsonify({'error': 'Erro ao consultar HubSpot API', 'status_code': response_nmrr.status_code}), 500
        
        deals = all_deals
        
        # Agrupa por EV
        ev_stats = {}
        for deal in deals:
            props = deal.get('properties', {})
            owner_id = props.get('analista_comercial')
            closedate = props.get('closedate')
            amount = props.get('amount', '0')
            
            if owner_id and closedate:
                dt_utc = parse_hubspot_timestamp(closedate)
                dt_brazil = convert_utc_to_brazil(dt_utc)
                
                if owner_id not in ev_stats:
                    ev_stats[owner_id] = {
                        'count': 0,
                        'revenue': 0,
                        'timestamps': [],
                        'deals': []
                    }
                
                ev_stats[owner_id]['count'] += 1
                ev_stats[owner_id]['revenue'] += float(amount) if amount else 0
                ev_stats[owner_id]['timestamps'].append(dt_brazil)
                ev_stats[owner_id]['deals'].append(props.get('dealname', 'N/A'))
        
        # Top 5 EVs
        top_evs = sorted(ev_stats.items(), key=lambda x: (x[1]['revenue'], x[1]['count']), reverse=True)[:5]
        
        # Formata resposta e salva badges
        ranking = []
        for idx, (owner_id, stats) in enumerate(top_evs, 1):
            timestamps = sorted(stats['timestamps'])
            badges = detect_badges(timestamps, stats['count'], stats['revenue'], 'EV')
            user_name = get_analyst_name(owner_id)
            
            # Salva badges no banco de dados
            for badge in badges:
                try:
                    save_badge_to_database(
                        user_type='EV',
                        user_id=owner_id,
                        user_name=user_name,
                        badge=badge,
                        metric_value=stats['revenue'],
                        context={
                            'count': stats['count'],
                            'revenue': stats['revenue'],
                            'deals': stats['deals'],
                            'timestamps': [t.isoformat() for t in timestamps]
                        }
                    )
                except Exception as e:
                    print(f"[AVISO] Erro ao salvar badge {badge['code']} para {user_name}: {e}")
            
            ranking.append({
                'position': idx,
                'userId': owner_id,
                'userName': user_name,
                'dealCount': stats['count'],
                'revenue': stats['revenue'],
                'badges': badges,
                'firstDeal': timestamps[0].strftime('%H:%M:%S') if timestamps else None,
                'lastDeal': timestamps[-1].strftime('%H:%M:%S') if timestamps else None
            })
        
        result = {
            'status': 'success',
            'userType': 'EV',
            'data': ranking,
            'total': len(deals),
            'timestamp': datetime.now().isoformat()
        }
        
        # Atualiza cache se não estava usando
        if not use_cache:
            with _cache_lock:
                _data_cache['hall_evs'] = result
        
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Cache'] = 'MISS'
        
        return response
        
    except Exception as e:
        print(f"Erro ao buscar EVs realtime: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@hall_da_fama_bp.route('/sdrs-realtime')
def hall_da_fama_sdrs_realtime():
    """Retorna Top 5 SDRs com badges em tempo real via HubSpot API"""
    _data_cache = get_cache()
    _cache_lock = get_cache_lock()
    
    pipeline = request.args.get('pipeline', '6810518')
    
    use_cache = request.args.get('use_cache', 'false').lower() == 'true'
    cache_key = 'hall_sdrs_new' if pipeline == '6810518' else 'hall_sdrs_expansao'
    
    if use_cache and _data_cache.get(cache_key):
        response = jsonify(_data_cache[cache_key])
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['X-Cache'] = 'HIT'
        return response
    
    try:
        if pipeline == '6810518':
            date_property = 'hs_v2_date_entered_7417230'
            pipeline_name = 'NEW'
        elif pipeline == '4007305':
            date_property = 'hs_v2_date_entered_13487283'
            pipeline_name = 'Expansão'
        else:
            return jsonify({'error': 'Pipeline inválido. Use 6810518 (NEW) ou 4007305 (Expansão)'}), 400
        
        today_start_utc = get_today_brazil_start_utc()
        today_start_ms = int(today_start_utc.timestamp() * 1000)
        tomorrow_start_utc = today_start_utc + timedelta(days=1)
        tomorrow_start_ms = int(tomorrow_start_utc.timestamp() * 1000)
        
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
                    {"propertyName": date_property, "operator": "GTE", "value": str(today_start_ms)},
                    {"propertyName": date_property, "operator": "LT", "value": str(tomorrow_start_ms)}
                ]
            }],
            "properties": ["dealname", "pr_vendedor", date_property],
            "limit": 100
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        
        if response.status_code != 200:
            return jsonify({'error': 'Erro ao consultar HubSpot API', 'status_code': response.status_code}), 500
        
        deals = response.json().get('results', [])
        
        # Agrupa por SDR
        sdr_stats = {}
        for deal in deals:
            props = deal.get('properties', {})
            sdr_id = props.get('pr_vendedor')
            timestamp = props.get(date_property)
            
            if sdr_id and timestamp:
                dt_utc = parse_hubspot_timestamp(timestamp)
                dt_brazil = convert_utc_to_brazil(dt_utc)
                
                if sdr_id not in sdr_stats:
                    sdr_stats[sdr_id] = {
                        'count': 0,
                        'timestamps': [],
                        'deals': []
                    }
                
                sdr_stats[sdr_id]['count'] += 1
                sdr_stats[sdr_id]['timestamps'].append(dt_brazil)
                sdr_stats[sdr_id]['deals'].append(props.get('dealname', 'N/A'))
        
        # Top 5 SDRs - ordenado por quantidade, desempate por horário do último agendamento
        max_datetime = datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        top_sdrs = sorted(sdr_stats.items(), key=lambda x: (-x[1]['count'], max(x[1]['timestamps']) if x[1]['timestamps'] else max_datetime))[:5]
        
        # Formata resposta e salva badges
        ranking = []
        for idx, (sdr_id, stats) in enumerate(top_sdrs, 1):
            timestamps = sorted(stats['timestamps'])
            badges = detect_badges(timestamps, stats['count'], None, 'SDR')
            user_name = get_analyst_name(sdr_id)
            
            # Salva badges no banco de dados
            for badge in badges:
                try:
                    save_badge_to_database(
                        user_type='SDR',
                        user_id=sdr_id,
                        user_name=user_name,
                        badge=badge,
                        metric_value=stats['count'],
                        pipeline=pipeline_name,
                        context={
                            'count': stats['count'],
                            'pipeline': pipeline_name,
                            'deals': stats['deals'],
                            'timestamps': [t.isoformat() for t in timestamps]
                        }
                    )
                except Exception as e:
                    print(f"[AVISO] Erro ao salvar badge {badge['code']} para {user_name}: {e}")
            
            ranking.append({
                'position': idx,
                'userId': sdr_id,
                'userName': user_name,
                'scheduledCount': stats['count'],
                'badges': badges,
                'firstScheduled': timestamps[0].strftime('%H:%M:%S') if timestamps else None,
                'lastScheduled': timestamps[-1].strftime('%H:%M:%S') if timestamps else None
            })
        
        result = {
            'status': 'success',
            'userType': 'SDR',
            'pipeline': pipeline_name,
            'data': ranking,
            'total': len(deals),
            'timestamp': datetime.now().isoformat()
        }
        
        # Atualiza cache se não estava usando
        if not use_cache:
            with _cache_lock:
                _data_cache[cache_key] = result
        
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Cache'] = 'MISS'
        
        return response
        
    except Exception as e:
        print(f"Erro ao buscar SDRs realtime: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@hall_da_fama_bp.route('/ldrs-realtime')
def hall_da_fama_ldrs_realtime():
    """Retorna Top 5 LDRs com badges em tempo real via HubSpot API"""
    _data_cache = get_cache()
    _cache_lock = get_cache_lock()
    
    use_cache = request.args.get('use_cache', 'false').lower() == 'true'
    if use_cache and _data_cache.get('hall_ldrs'):
        response = jsonify(_data_cache['hall_ldrs'])
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['X-Cache'] = 'HIT'
        return response
    
    try:
        today_start_utc = get_today_brazil_start_utc()
        today_start_ms = int(today_start_utc.timestamp() * 1000)
        tomorrow_start_utc = today_start_utc + timedelta(days=1)
        tomorrow_start_ms = int(tomorrow_start_utc.timestamp() * 1000)
        
        hubspot_token = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
        url = 'https://api.hubapi.com/crm/v3/objects/deals/search'
        headers = {
            'Authorization': f'Bearer {hubspot_token}',
            'Content-Type': 'application/json'
        }
        
        all_deals = []
        
        # 1. Ganho (Vendas NMRR) - Stage 6810524
        payload_nmrr = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "hs_v2_date_entered_6810524", "operator": "GTE", "value": str(today_start_ms)},
                    {"propertyName": "hs_v2_date_entered_6810524", "operator": "LT", "value": str(tomorrow_start_ms)},
                    {"propertyName": "dealstage", "operator": "EQ", "value": "6810524"},
                    {"propertyName": "tipo_de_negociacao", "operator": "NEQ", "value": "Variação Cambial"}
                ]
            }],
            "properties": ["dealname", "criado_por_", "closedate", "amount", "hs_v2_date_entered_6810524", "tipo_de_negociacao"],
            "limit": 100
        }
        
        response_nmrr = requests.post(url, headers=headers, json=payload_nmrr, timeout=25)
        if response_nmrr.status_code == 200:
            all_deals.extend(response_nmrr.json().get('results', []))
        
        # 2. Ganho (Expansão) - Stage 13487286
        payload_expansao = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "hs_v2_date_entered_13487286", "operator": "GTE", "value": str(today_start_ms)},
                    {"propertyName": "hs_v2_date_entered_13487286", "operator": "LT", "value": str(tomorrow_start_ms)},
                    {"propertyName": "dealstage", "operator": "EQ", "value": "13487286"},
                    {"propertyName": "tipo_de_negociacao", "operator": "NEQ", "value": "Variação Cambial"}
                ]
            }],
            "properties": ["dealname", "criado_por_", "closedate", "amount", "hs_v2_date_entered_13487286", "tipo_de_negociacao"],
            "limit": 100
        }
        
        response_expansao = requests.post(url, headers=headers, json=payload_expansao, timeout=25)
        if response_expansao.status_code == 200:
            all_deals.extend(response_expansao.json().get('results', []))
        
        if response_nmrr.status_code != 200 and response_expansao.status_code != 200:
            return jsonify({'error': 'Erro ao consultar HubSpot API', 'status_code': response_nmrr.status_code}), 500
        
        deals = all_deals
        
        # Agrupa por LDR
        ldr_stats = {}
        for deal in deals:
            props = deal.get('properties', {})
            ldr_id = props.get('criado_por_')
            closedate = props.get('closedate')
            amount = props.get('amount', '0')
            
            if ldr_id and closedate:
                dt_utc = parse_hubspot_timestamp(closedate)
                dt_brazil = convert_utc_to_brazil(dt_utc)
                
                if ldr_id not in ldr_stats:
                    ldr_stats[ldr_id] = {
                        'count': 0,
                        'revenue': 0,
                        'timestamps': [],
                        'deals': []
                    }
                
                ldr_stats[ldr_id]['count'] += 1
                ldr_stats[ldr_id]['revenue'] += float(amount) if amount else 0
                ldr_stats[ldr_id]['timestamps'].append(dt_brazil)
                ldr_stats[ldr_id]['deals'].append(props.get('dealname', 'N/A'))
        
        # Top 5 LDRs - ordenado por quantidade, desempate por receita
        top_ldrs = sorted(ldr_stats.items(), key=lambda x: (x[1]['count'], x[1]['revenue']), reverse=True)[:5]
        
        # Formata resposta e salva badges
        ranking = []
        for idx, (ldr_id, stats) in enumerate(top_ldrs, 1):
            timestamps = sorted(stats['timestamps'])
            badges = detect_badges(timestamps, stats['count'], stats['revenue'], 'LDR')
            user_name = get_analyst_name(ldr_id)
            
            # Salva badges no banco de dados
            for badge in badges:
                try:
                    save_badge_to_database(
                        user_type='LDR',
                        user_id=ldr_id,
                        user_name=user_name,
                        badge=badge,
                        metric_value=stats['revenue'],
                        context={
                            'count': stats['count'],
                            'revenue': stats['revenue'],
                            'deals': stats['deals'],
                            'timestamps': [t.isoformat() for t in timestamps]
                        }
                    )
                except Exception as e:
                    print(f"[AVISO] Erro ao salvar badge {badge['code']} para {user_name}: {e}")
            
            ranking.append({
                'position': idx,
                'userId': ldr_id,
                'userName': user_name,
                'wonDealsCount': stats['count'],
                'revenue': stats['revenue'],
                'badges': badges,
                'firstDeal': timestamps[0].strftime('%H:%M:%S') if timestamps else None,
                'lastDeal': timestamps[-1].strftime('%H:%M:%S') if timestamps else None
            })
        
        result = {
            'status': 'success',
            'userType': 'LDR',
            'data': ranking,
            'total': len(deals),
            'timestamp': datetime.now().isoformat()
        }
        
        # Atualiza cache se não estava usando
        if not use_cache:
            with _cache_lock:
                _data_cache['hall_ldrs'] = result
        
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Cache'] = 'MISS'
        
        return response
        
    except Exception as e:
        print(f"Erro ao buscar LDRs realtime: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

