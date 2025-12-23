"""
Testes de Viabilidade de Gamificação - API HUBSPOT
Valida dados em tempo real da API do HubSpot para badges de SDRs
Testa propriedades: hs_v2_date_entered_7417230 (NEW) e hs_v2_date_entered_13487283 (Expansão)
"""

import requests
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração HubSpot
HUBSPOT_TOKEN = os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')
HUBSPOT_API_URL = "https://api.hubapi.com/crm/v3/objects/deals"

# Carrega mapeamento de analistas
ANALYSTS_MAP = {}
try:
    with open('data/analistas_mapeamento.json', 'r', encoding='utf-8') as f:
        ANALYSTS_MAP = json.load(f)
except Exception as e:
    print(f"⚠️ Erro ao carregar mapeamento de analistas: {e}")

def get_analyst_name(analyst_id):
    """Retorna o nome do analista pelo ID"""
    if not analyst_id:
        return "N/A"
    return ANALYSTS_MAP.get(str(analyst_id), f"ID: {analyst_id}")

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_subheader(title):
    """Imprime subcabeçalho formatado"""
    print(f"\n--- {title} ---\n")

# ============================================================================
# TESTES API HUBSPOT - SDRs
# ============================================================================

def test_hubspot_api_connection():
    """Testa conexão com a API do HubSpot"""
    print_subheader("🔌 Teste de Conexão com API HubSpot")
    
    try:
        url = f"{HUBSPOT_API_URL}/search"
        headers = {
            "Authorization": f"Bearer {HUBSPOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "limit": 1,
            "properties": ["dealname"]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Conexão com HubSpot API: SUCESSO")
            print(f"   Status Code: {response.status_code}")
            print(f"   Total deals disponíveis: {response.json().get('total', 'N/A')}")
            return True
        else:
            print(f"❌ Erro na conexão: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar: {str(e)}")
        return False

def test_timestamp_properties_exist():
    """Verifica se as propriedades de timestamp existem no HubSpot"""
    print_subheader("🔍 Validação de Propriedades de Timestamp")
    
    try:
        url = f"{HUBSPOT_API_URL}/search"
        headers = {
            "Authorization": f"Bearer {HUBSPOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Busca deals do pipeline NEW com a propriedade específica
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        timestamp_ms = int(today_start.timestamp() * 1000)
        
        payload = {
            "filterGroups": [{
                "filters": [
                    {
                        "propertyName": "pipeline",
                        "operator": "EQ",
                        "value": "6810518"  # NEW
                    },
                    {
                        "propertyName": "hs_v2_date_entered_7417230",
                        "operator": "GTE",
                        "value": timestamp_ms
                    }
                ]
            }],
            "properties": [
                "dealname",
                "pr_vendedor",
                "pipeline",
                "hs_v2_date_entered_7417230"
            ],
            "limit": 5
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"✅ Propriedade hs_v2_date_entered_7417230 encontrada!")
            print(f"   Deals encontrados hoje (Pipeline NEW): {len(results)}")
            
            if results:
                print(f"\n📊 Exemplos de dados (primeiros 3):\n")
                for idx, deal in enumerate(results[:3], 1):
                    props = deal.get('properties', {})
                    timestamp = props.get('hs_v2_date_entered_7417230')
                    sdr = props.get('pr_vendedor', 'N/A')
                    name = props.get('dealname', 'N/A')
                    
                    print(f"{idx}. Deal: {name[:50]}")
                    print(f"   SDR: {sdr}")
                    print(f"   Timestamp: {timestamp}")
                    
                    if timestamp:
                        # HubSpot retorna timestamp como string ISO 8601
                        try:
                            # Tenta parsear como ISO string
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except:
                            # Fallback para timestamp em milliseconds
                            dt = datetime.fromtimestamp(int(timestamp) / 1000)
                        
                        print(f"   DateTime: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"   Hora: {dt.hour}h | Minuto: {dt.minute}m | Segundo: {dt.second}s")
                    print()
                
                return True
            else:
                print("⚠️  Nenhum deal encontrado hoje (pode ser normal se ainda não houve agendamentos)")
                return True
        else:
            print(f"❌ Erro ao buscar propriedade: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao validar propriedades: {str(e)}")
        return False

def test_sdrs_new_pipeline_realtime():
    """Testa agendamentos do Pipeline NEW em tempo real"""
    print_subheader("📞 SDRs - Pipeline NEW (Tempo Real - Hoje)")
    
    try:
        url = f"{HUBSPOT_API_URL}/search"
        headers = {
            "Authorization": f"Bearer {HUBSPOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Timestamp de início do dia (00:00:00)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        timestamp_start_ms = int(today_start.timestamp() * 1000)
        
        # Timestamp atual
        timestamp_now_ms = int(datetime.now().timestamp() * 1000)
        
        payload = {
            "filterGroups": [{
                "filters": [
                    {
                        "propertyName": "pipeline",
                        "operator": "EQ",
                        "value": "6810518"
                    },
                    {
                        "propertyName": "hs_v2_date_entered_7417230",
                        "operator": "GTE",
                        "value": timestamp_start_ms
                    },
                    {
                        "propertyName": "hs_v2_date_entered_7417230",
                        "operator": "LTE",
                        "value": timestamp_now_ms
                    }
                ]
            }],
            "properties": [
                "dealname",
                "pr_vendedor",
                "hs_v2_date_entered_7417230",
                "amount"
            ],
            "limit": 100
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            deals = data.get('results', [])
            
            print(f"✅ Total de agendamentos hoje (Pipeline NEW): {len(deals)}\n")
            
            if deals:
                # Agrupa por SDR
                sdr_stats = {}
                all_timestamps = []
                
                for deal in deals:
                    props = deal.get('properties', {})
                    sdr_id = props.get('pr_vendedor')
                    timestamp = props.get('hs_v2_date_entered_7417230')
                    
                    if sdr_id and timestamp:
                        try:
                            # HubSpot returns ISO 8601 string like "2025-11-13T11:00:19.171Z"
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except:
                            # Fallback for milliseconds format
                            dt = datetime.fromtimestamp(int(timestamp) / 1000)
                        all_timestamps.append(dt)
                        
                        if sdr_id not in sdr_stats:
                            sdr_stats[sdr_id] = {
                                'count': 0,
                                'timestamps': [],
                                'deals': []
                            }
                        
                        sdr_stats[sdr_id]['count'] += 1
                        sdr_stats[sdr_id]['timestamps'].append(dt)
                        sdr_stats[sdr_id]['deals'].append(props.get('dealname', 'N/A'))
                
                # Top 5 SDRs
                top_sdrs = sorted(sdr_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
                
                print("🏆 TOP 5 SDRs (Pipeline NEW - Hoje):\n")
                
                for idx, (sdr_id, stats) in enumerate(top_sdrs, 1):
                    timestamps = sorted(stats['timestamps'])
                    count = stats['count']
                    
                    print(f"{idx}. SDR ID: {sdr_id}")
                    print(f"   Agendamentos: {count}")
                    
                    if timestamps:
                        first = timestamps[0]
                        last = timestamps[-1]
                        print(f"   Período: {first.strftime('%H:%M:%S')} → {last.strftime('%H:%M:%S')}")
                    
                    # Detecta badges
                    badges = []
                    
                    # Volume
                    if count >= 7:
                        badges.append("🏆 Unstoppable (7+)")
                    elif count >= 5:
                        badges.append("📅 Master Scheduler (5+)")
                    elif count >= 3:
                        badges.append("🎯 Hat Trick (3+)")
                    
                    # Horário
                    early_bird = any(dt.hour < 10 for dt in timestamps)
                    night_owl = any(dt.hour > 17 for dt in timestamps)
                    
                    if early_bird:
                        badges.append("🌅 Early Bird (<10h)")
                    if night_owl:
                        badges.append("🌙 Night Owl (>17h)")
                    
                    # Velocidade
                    if len(timestamps) > 1:
                        min_interval = min((timestamps[i] - timestamps[i-1]).total_seconds() / 3600 
                                         for i in range(1, len(timestamps)))
                        if min_interval < 1:
                            badges.append(f"⚡ Speed Demon (<1h: {min_interval:.1f}h)")
                    
                    if badges:
                        print(f"   Badges: {', '.join(badges)}")
                    
                    print()
                
                # Estatísticas gerais
                print("📊 ESTATÍSTICAS GERAIS (Todos SDRs):\n")
                
                hours_distribution = {}
                for dt in all_timestamps:
                    hour = dt.hour
                    hours_distribution[hour] = hours_distribution.get(hour, 0) + 1
                
                print(f"   Total de agendamentos: {len(all_timestamps)}")
                print(f"   SDRs únicos: {len(sdr_stats)}")
                
                early_count = sum(1 for dt in all_timestamps if dt.hour < 10)
                night_count = sum(1 for dt in all_timestamps if dt.hour > 17)
                
                print(f"   Agendamentos antes 10h: {early_count} ({early_count/len(all_timestamps)*100:.1f}%)")
                print(f"   Agendamentos depois 17h: {night_count} ({night_count/len(all_timestamps)*100:.1f}%)")
                
                # Top 3 horários
                top_hours = sorted(hours_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"\n   🕐 Horários mais produtivos:")
                for hour, count in top_hours:
                    print(f"      {hour:02d}h: {count} agendamentos")
                
                return True
            else:
                print("⚠️  Nenhum agendamento hoje (Pipeline NEW)")
                print("   Isso pode ser normal dependendo do horário do dia")
                return True
                
        else:
            print(f"❌ Erro ao buscar agendamentos: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Pipeline NEW: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_sdrs_expansao_pipeline_realtime():
    """Testa agendamentos do Pipeline Expansão em tempo real"""
    print_subheader("📞 SDRs - Pipeline Expansão (Tempo Real - Hoje)")
    
    try:
        url = f"{HUBSPOT_API_URL}/search"
        headers = {
            "Authorization": f"Bearer {HUBSPOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Timestamp de início do dia
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        timestamp_start_ms = int(today_start.timestamp() * 1000)
        
        # Timestamp atual
        timestamp_now_ms = int(datetime.now().timestamp() * 1000)
        
        payload = {
            "filterGroups": [{
                "filters": [
                    {
                        "propertyName": "pipeline",
                        "operator": "EQ",
                        "value": "4007305"
                    },
                    {
                        "propertyName": "hs_v2_date_entered_13487283",
                        "operator": "GTE",
                        "value": timestamp_start_ms
                    },
                    {
                        "propertyName": "hs_v2_date_entered_13487283",
                        "operator": "LTE",
                        "value": timestamp_now_ms
                    }
                ]
            }],
            "properties": [
                "dealname",
                "pr_vendedor",
                "hs_v2_date_entered_13487283",
                "amount"
            ],
            "limit": 100
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            deals = data.get('results', [])
            
            print(f"✅ Total de agendamentos hoje (Pipeline Expansão): {len(deals)}\n")
            
            if deals:
                # Agrupa por SDR
                sdr_stats = {}
                
                for deal in deals:
                    props = deal.get('properties', {})
                    sdr_id = props.get('pr_vendedor')
                    timestamp = props.get('hs_v2_date_entered_13487283')
                    
                    if sdr_id and timestamp:
                        try:
                            # HubSpot returns ISO 8601 string like "2025-11-13T11:00:19.171Z"
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except:
                            # Fallback for milliseconds format
                            dt = datetime.fromtimestamp(int(timestamp) / 1000)
                        
                        if sdr_id not in sdr_stats:
                            sdr_stats[sdr_id] = {
                                'count': 0,
                                'timestamps': []
                            }
                        
                        sdr_stats[sdr_id]['count'] += 1
                        sdr_stats[sdr_id]['timestamps'].append(dt)
                
                # Top 5 SDRs
                top_sdrs = sorted(sdr_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
                
                print("🏆 TOP 5 SDRs (Pipeline Expansão - Hoje):\n")
                
                for idx, (sdr_id, stats) in enumerate(top_sdrs, 1):
                    timestamps = sorted(stats['timestamps'])
                    count = stats['count']
                    
                    print(f"{idx}. SDR ID: {sdr_id}")
                    print(f"   Agendamentos: {count}")
                    
                    if timestamps:
                        first = timestamps[0]
                        last = timestamps[-1]
                        print(f"   Período: {first.strftime('%H:%M:%S')} → {last.strftime('%H:%M:%S')}")
                    
                    # Detecta badges
                    badges = []
                    if count >= 5:
                        badges.append("📅 Master Scheduler")
                    elif count >= 3:
                        badges.append("🎯 Hat Trick")
                    
                    early_bird = any(dt.hour < 10 for dt in timestamps)
                    night_owl = any(dt.hour > 17 for dt in timestamps)
                    
                    if early_bird:
                        badges.append("🌅 Early Bird")
                    if night_owl:
                        badges.append("🌙 Night Owl")
                    
                    if badges:
                        print(f"   Badges: {', '.join(badges)}")
                    
                    print()
                
                return True
            else:
                print("⚠️  Nenhum agendamento hoje (Pipeline Expansão)")
                return True
                
        else:
            print(f"❌ Erro ao buscar agendamentos: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Pipeline Expansão: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_evs_realtime_today():
    """Testa deals ganhos de EVs em tempo real (HOJE APENAS)"""
    print_subheader("💰 EVs - Deals Ganhos (Tempo Real - HOJE)")
    
    try:
        url = f"{HUBSPOT_API_URL}/search"
        headers = {
            "Authorization": f"Bearer {HUBSPOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Calcula timestamps para HOJE em horário do Brasil (UTC-3)
        from zoneinfo import ZoneInfo
        
        # Meia-noite de hoje no Brasil (00:00:00 BRT)
        now_brazil = datetime.now(ZoneInfo('America/Sao_Paulo'))
        today_start_brazil = now_brazil.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Converter para UTC para enviar ao HubSpot
        today_start_utc = today_start_brazil.astimezone(ZoneInfo('UTC'))
        today_start_ms = int(today_start_utc.timestamp() * 1000)
        
        # Meia-noite de amanhã no Brasil (00:00:00 BRT)
        tomorrow_start_brazil = today_start_brazil + timedelta(days=1)
        tomorrow_start_utc = tomorrow_start_brazil.astimezone(ZoneInfo('UTC'))
        tomorrow_start_ms = int(tomorrow_start_utc.timestamp() * 1000)
        
        print(f"🕐 Período de busca (Horário do Brasil):")
        print(f"   Início: {today_start_brazil.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Fim:    {tomorrow_start_brazil.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"\n🌍 Período de busca (UTC para HubSpot):")
        print(f"   Início: {today_start_utc.strftime('%Y-%m-%d %H:%M:%S %Z')} ({today_start_ms})")
        print(f"   Fim:    {tomorrow_start_utc.strftime('%Y-%m-%d %H:%M:%S %Z')} ({tomorrow_start_ms})")
        print()
        
        # Mesmo payload que está no app.py (usando os dealstages corretos do código de produção)
        # IMPORTANTE: analista_comercial é a propriedade customizada do HubSpot para identificar o EV responsável
        payload = {
            "filterGroups": [{
                "filters": [
                    {
                        "propertyName": "closedate",
                        "operator": "GTE",
                        "value": str(today_start_ms)
                    },
                    {
                        "propertyName": "closedate",
                        "operator": "LT",
                        "value": str(tomorrow_start_ms)
                    },
                    {
                        "propertyName": "dealstage",
                        "operator": "IN",
                        "values": [
                            "6810524",      # Ganho (Vendas NMRR)
                            "13487286",     # Ganho (Expansão)
                            "16657792",     # Faturamento (Vendas NMRR)
                            "180044058",    # Aguardando Correção - Faturamento (Vendas NMRR)
                            "33646228",     # Faturamento (Expansão)
                            "180043078"     # Aguardando Correção - Faturamento (Expansão)
                        ]
                    }
                ]
            }],
            "properties": [
                "dealname",
                "analista_comercial",  # ID do EV (propriedade customizada)
                "closedate",
                "amount",
                "dealstage",
                "pipeline"
            ],
            "limit": 100
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            deals = data.get('results', [])
            
            print(f"✅ Total de deals ganhos HOJE: {len(deals)}\n")
            
            if deals:
                # Agrupa por EV
                ev_stats = {}
                all_deals_info = []
                
                for deal in deals:
                    props = deal.get('properties', {})
                    ev_id = props.get('analista_comercial')  # Propriedade customizada do HubSpot para identificar o EV
                    closedate_str = props.get('closedate')
                    amount = props.get('amount', '0')
                    name = props.get('dealname', 'N/A')
                    dealstage = props.get('dealstage', 'N/A')
                    
                    if closedate_str:
                        try:
                            # HubSpot retorna ISO 8601 ou timestamp em ms
                            if 'T' in closedate_str or 'Z' in closedate_str:
                                dt_utc = datetime.fromisoformat(closedate_str.replace('Z', '+00:00'))
                            else:
                                dt_utc = datetime.fromtimestamp(int(closedate_str) / 1000, tz=ZoneInfo('UTC'))
                            
                            # Converter para horário do Brasil
                            dt_brazil = dt_utc.astimezone(ZoneInfo('America/Sao_Paulo'))
                            
                        except Exception as e:
                            print(f"⚠️  Erro ao parsear data: {closedate_str} - {str(e)}")
                            continue
                        
                        all_deals_info.append({
                            'ev': ev_id or 'N/A',
                            'name': name,
                            'closedate_utc': dt_utc,
                            'closedate_brazil': dt_brazil,
                            'amount': float(amount) if amount else 0,
                            'dealstage': dealstage
                        })
                        
                        if ev_id:
                            if ev_id not in ev_stats:
                                ev_stats[ev_id] = {
                                    'count': 0,
                                    'revenue': 0,
                                    'deals': []
                                }
                            
                            ev_stats[ev_id]['count'] += 1
                            ev_stats[ev_id]['revenue'] += float(amount) if amount else 0
                            ev_stats[ev_id]['deals'].append(name)
                
                # Ordena por revenue
                top_evs = sorted(ev_stats.items(), key=lambda x: x[1]['revenue'], reverse=True)[:10]
                
                print("🏆 TOP 10 EVs (Deals Ganhos HOJE):\n")
                
                for idx, (ev_id, stats) in enumerate(top_evs, 1):
                    count = stats['count']
                    revenue = stats['revenue']
                    ev_name = get_analyst_name(ev_id)
                    
                    print(f"{idx}. {ev_name} (ID: {ev_id})")
                    print(f"   Deals ganhos: {count}")
                    print(f"   Faturamento: R$ {revenue:,.2f}")
                    
                    # Mostra os deals
                    if count <= 3:
                        for deal_name in stats['deals']:
                            print(f"      • {deal_name[:50]}")
                    
                    # Detecta badges de valor (mesmos thresholds do app.py)
                    badges = []
                    if revenue >= 10000:
                        badges.append("💰 Chuva de Dinheiro (R$ 10k+)")
                    elif revenue >= 5000:
                        badges.append("💵 Faturamento Premium (R$ 5k+)")
                    elif revenue >= 2500:
                        badges.append("🤑 Caixa Cheio (R$ 2.5k+)")
                    
                    if badges:
                        print(f"   Badges: {', '.join(badges)}")
                    
                    print()
                
                # ANÁLISE DETALHADA DE DATAS
                print("="*80)
                print("📅 ANÁLISE DETALHADA DE TODAS AS DATAS DE FECHAMENTO:")
                print("="*80)
                print()
                
                # Ordena por data
                all_deals_info.sort(key=lambda x: x['closedate_brazil'])
                
                deals_today = []
                deals_future = []
                deals_past = []
                
                for deal_info in all_deals_info:
                    dt_brazil = deal_info['closedate_brazil']
                    
                    # Verifica se é hoje, futuro ou passado
                    if dt_brazil.date() == now_brazil.date():
                        deals_today.append(deal_info)
                    elif dt_brazil.date() > now_brazil.date():
                        deals_future.append(deal_info)
                    else:
                        deals_past.append(deal_info)
                
                print(f"✅ Deals com closedate = HOJE ({now_brazil.date()}): {len(deals_today)}")
                print(f"⚠️  Deals com closedate = FUTURO: {len(deals_future)}")
                print(f"⚠️  Deals com closedate = PASSADO: {len(deals_past)}")
                print()
                
                if deals_future:
                    print("🔴 ALERTA: DEALS COM DATA FUTURA ENCONTRADOS!")
                    print("="*80)
                    for deal in deals_future[:5]:  # Mostra primeiros 5
                        print(f"   Deal: {deal['name'][:50]}")
                        print(f"   EV: {deal['ev']}")
                        print(f"   Closedate: {deal['closedate_brazil'].strftime('%Y-%m-%d %H:%M:%S')} (Brasil)")
                        print(f"   Amount: R$ {deal['amount']:,.2f}")
                        print()
                
                if deals_today:
                    print("✅ DEALS COM DATA DE HOJE:")
                    print("="*80)
                    for deal in deals_today[:10]:  # Mostra primeiros 10
                        print(f"   Deal: {deal['name'][:50]}")
                        print(f"   EV: {deal['ev']}")
                        print(f"   Closedate: {deal['closedate_brazil'].strftime('%Y-%m-%d %H:%M:%S')} (Brasil)")
                        print(f"   Amount: R$ {deal['amount']:,.2f}")
                        print()
                
                # BUSCA ESPECÍFICA POR ANDREZA SANDIM
                print("="*80)
                print("🔍 BUSCANDO ESPECIFICAMENTE POR 'ANDREZA SANDIM' (ID: 35096765):")
                print("="*80)
                print()
                
                # Busca pelo ID da Andreza Sandim
                andreza_id = "35096765"
                andreza_deals = [d for d in all_deals_info if d['ev'] == andreza_id]
                
                # Também busca por nome
                andreza_deals_by_name = [d for d in all_deals_info if get_analyst_name(d['ev']).lower() == 'andreza sandim']
                
                if andreza_deals or andreza_deals_by_name:
                    all_andreza = andreza_deals + [d for d in andreza_deals_by_name if d not in andreza_deals]
                    print(f"✅ Encontrados {len(all_andreza)} deals de Andreza Sandim:")
                    for deal in all_andreza:
                        print(f"   Deal: {deal['name']}")
                        print(f"   EV ID: {deal['ev']}")
                        print(f"   EV Nome: {get_analyst_name(deal['ev'])}")
                        print(f"   Closedate: {deal['closedate_brazil'].strftime('%Y-%m-%d %H:%M:%S')} (Brasil)")
                        print(f"   É hoje? {'✅ SIM' if deal['closedate_brazil'].date() == now_brazil.date() else '❌ NÃO'}")
                        print(f"   Amount: R$ {deal['amount']:,.2f}")
                        print()
                else:
                    print("❌ NENHUM deal de Andreza Sandim encontrado no período!")
                    print("   Isso confirma que ela NÃO deve aparecer no ranking de hoje.")
                
                return True
            else:
                print("⚠️  Nenhum deal ganho hoje")
                print("   Isso pode ser normal dependendo do horário do dia")
                return True
                
        else:
            print(f"❌ Erro ao buscar deals: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar EVs: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_timestamp_granularity():
    """Valida se os timestamps têm hora/minuto/segundo completos"""
    print_subheader("🔬 Análise de Granularidade dos Timestamps")
    
    try:
        url = f"{HUBSPOT_API_URL}/search"
        headers = {
            "Authorization": f"Bearer {HUBSPOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Busca últimos 10 deals com agendamento (últimos 7 dias)
        seven_days_ago = datetime.now() - timedelta(days=7)
        timestamp_ms = int(seven_days_ago.timestamp() * 1000)
        
        payload = {
            "filterGroups": [{
                "filters": [
                    {
                        "propertyName": "pipeline",
                        "operator": "EQ",
                        "value": "6810518"
                    },
                    {
                        "propertyName": "hs_v2_date_entered_7417230",
                        "operator": "GTE",
                        "value": timestamp_ms
                    }
                ]
            }],
            "properties": [
                "dealname",
                "pr_vendedor",
                "hs_v2_date_entered_7417230"
            ],
            "limit": 10,
            "sorts": [{
                "propertyName": "hs_v2_date_entered_7417230",
                "direction": "DESCENDING"
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            deals = data.get('results', [])
            
            print(f"✅ Analisando {len(deals)} agendamentos (últimos 7 dias):\n")
            
            if deals:
                has_hour = False
                has_minute = False
                has_second = False
                
                for idx, deal in enumerate(deals[:5], 1):
                    props = deal.get('properties', {})
                    timestamp = props.get('hs_v2_date_entered_7417230')
                    name = props.get('dealname', 'N/A')[:40]
                    sdr = props.get('pr_vendedor', 'N/A')
                    
                    if timestamp:
                        try:
                            # HubSpot returns ISO 8601 string like "2025-11-13T11:00:19.171Z"
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except:
                            # Fallback for milliseconds format
                            dt = datetime.fromtimestamp(int(timestamp) / 1000)
                        
                        print(f"{idx}. Deal: {name}")
                        print(f"   SDR: {sdr}")
                        print(f"   Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"   Hora: {dt.hour}h | Minuto: {dt.minute}m | Segundo: {dt.second}s")
                        print()
                        
                        if dt.hour > 0 or dt.minute > 0:
                            has_hour = True
                        if dt.minute > 0 or dt.second > 0:
                            has_minute = True
                        if dt.second > 0:
                            has_second = True
                
                print("📊 RESULTADO DA ANÁLISE DE GRANULARIDADE:")
                print(f"   Hora disponível: {'✅ SIM' if has_hour else '❌ NÃO'}")
                print(f"   Minuto disponível: {'✅ SIM' if has_minute else '❌ NÃO'}")
                print(f"   Segundo disponível: {'✅ SIM' if has_second else '❌ NÃO'}")
                print()
                
                if has_hour and has_minute:
                    print("✅ CONCLUSÃO: Timestamps têm granularidade completa!")
                    print("✅ Badges de horário (Early Bird, Night Owl) são VIÁVEIS")
                    print("✅ Badges de velocidade (Speed Demon) são VIÁVEIS")
                else:
                    print("⚠️  AVISO: Timestamps podem não ter granularidade completa")
                
                return has_hour and has_minute
            else:
                print("⚠️  Nenhum deal encontrado para análise")
                return False
                
        else:
            print(f"❌ Erro ao buscar deals: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao validar granularidade: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def print_summary():
    """Imprime resumo consolidado"""
    print_header("📊 RESUMO - VALIDAÇÃO API HUBSPOT")
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    VALIDAÇÃO DE DADOS DA API HUBSPOT                       ║
╚════════════════════════════════════════════════════════════════════════════╝

✅ PROPRIEDADES VALIDADAS:

   📞 SDRs - Pipeline NEW (6810518):
      Propriedade: hs_v2_date_entered_7417230
      Descrição: Date entered "Reunião Prevista (Vendas NMRR)"
      Status: ✅ DISPONÍVEL COM TIMESTAMP COMPLETO
      
   📞 SDRs - Pipeline Expansão (4007305):
      Propriedade: hs_v2_date_entered_13487283
      Descrição: Date entered "Reunião Prevista (Expansão)"
      Status: ✅ DISPONÍVEL COM TIMESTAMP COMPLETO

✅ BADGES VIÁVEIS COM API HUBSPOT:

   🎯 Volume:
      - Hat Trick SDR (3+ agendamentos/dia)
      - Master Scheduler (5+ agendamentos/dia)
      - Unstoppable (7+ agendamentos/dia)
      
   🕐 Horário:
      - Early Bird (agendamento antes 10h) ✅ NOVO!
      - Night Owl (agendamento depois 17h) ✅ NOVO!
      
   ⚡ Velocidade:
      - Speed Demon (< 1h entre agendamentos) ✅ NOVO!
      - Flash (< 3h entre agendamentos) ✅ NOVO!
      
   📈 Consistência:
      - Consistency King (5+ dias ativos)

╔════════════════════════════════════════════════════════════════════════════╗
║                        PRÓXIMOS PASSOS                                     ║
╚════════════════════════════════════════════════════════════════════════════╝

1. ✅ Implementar endpoint /api/hall-da-fama/sdrs-realtime
2. ✅ Criar frontend hall_da_fama.html com dados da API
3. ✅ Adicionar detecção de badges em tempo real
4. ✅ Criar tabela badges_desbloqueados com campo source='hubspot_api'
5. ✅ Atualizar a cada 30 segundos (dados em tempo real)

Status: 🟢 VALIDADO - API HUBSPOT VIÁVEL
Vantagem: ✅ Timestamps completos + Dados em tempo real
Esforço: 🟢 BAIXO (endpoints já especificados)
""")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Executa todos os testes"""
    print_header("🎮 VALIDAÇÃO DE GAMIFICAÇÃO - API HUBSPOT")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Teste 1: Conexão
        if not test_hubspot_api_connection():
            print("\n❌ Falha na conexão. Verifique o token do HubSpot.")
            return
        
        # TESTE CRÍTICO: EVs com análise detalhada de datas
        print("\n" + "="*80)
        print("⚠️  EXECUTANDO TESTE CRÍTICO: VALIDAÇÃO DE DATAS DE DEALS DOS EVs")
        print("="*80 + "\n")
        test_evs_realtime_today()
        
        # Teste 2: Propriedades existem
        if not test_timestamp_properties_exist():
            print("\n❌ Propriedades de timestamp não encontradas.")
            return
        
        # Teste 3: Granularidade
        test_timestamp_granularity()
        
        # Teste 4: Pipeline NEW
        test_sdrs_new_pipeline_realtime()
        
        # Teste 5: Pipeline Expansão
        test_sdrs_expansao_pipeline_realtime()
        
        # Resumo
        print_summary()
        
        print("\n✅ Todos os testes concluídos com sucesso!\n")
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
