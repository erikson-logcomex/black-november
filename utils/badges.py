"""
Utilitários para badges e gamificação
"""
from datetime import datetime
from utils.db import get_db_connection_context
from psycopg2.extras import RealDictCursor
import json

def detect_badges(timestamps, count, revenue=None, user_type='EV'):
    """Detecta badges baseado em timestamps, contagem e revenue (ACUMULATIVO)"""
    badges = []
    
    # Badges de Volume (ACUMULATIVO)
    if count >= 3:
        if user_type == 'SDR':
            badges.append({'code': 'precision_sniper', 'name': 'Precision Sniper', 'category': 'volume'})
        elif user_type == 'LDR':
            badges.append({'code': 'precision_sniper', 'name': 'Precision Sniper', 'category': 'volume'})
        else:
            badges.append({'code': 'precision_sniper', 'name': 'Precision Sniper', 'category': 'volume'})
    
    if count >= 5:
        if user_type == 'SDR':
            badges.append({'code': 'master_scheduler', 'name': 'Master Scheduler', 'category': 'volume'})
        else:
            badges.append({'code': 'full_pressure', 'name': 'Full Pressure', 'category': 'volume'})
    
    if count >= 7:
        badges.append({'code': 'full_pressure', 'name': 'Full Pressure', 'category': 'volume'})
    
    if count >= 10:
        badges.append({'code': 'overload_closer', 'name': 'Overload Closer', 'category': 'volume'})
    
    # Badges de Valor (apenas EVs e LDRs)
    if revenue and user_type in ['EV', 'LDR']:
        if revenue >= 2500:
            badges.append({'code': 'bronze_closer', 'name': 'Bronze Closer', 'category': 'valor'})
        if revenue >= 5000:
            badges.append({'code': 'silver_closer', 'name': 'Silver Closer', 'category': 'valor'})
        if revenue >= 10000:
            badges.append({'code': 'gold_closer', 'name': 'Gold Closer', 'category': 'valor'})
    
    # Badges de Horário
    if timestamps:
        early_bird = sum(1 for dt in timestamps if dt.hour < 8)
        night_owl = sum(1 for dt in timestamps if dt.hour >= 21)
        
        if early_bird > 0:
            badges.append({'code': 'madrugador', 'name': f'Madrugador ({early_bird}x)', 'category': 'horario'})
        if night_owl > 0:
            badges.append({'code': 'coruja', 'name': f'Coruja ({night_owl}x)', 'category': 'horario'})
    
    # Badges de Velocidade (apenas EVs e SDRs)
    if user_type in ['EV', 'SDR'] and len(timestamps) > 1:
        sorted_timestamps = sorted(timestamps)
        speed_demon = 0
        flash = 0
        
        for i in range(1, len(sorted_timestamps)):
            diff_hours = (sorted_timestamps[i] - sorted_timestamps[i-1]).total_seconds() / 3600
            if diff_hours < 1:
                speed_demon += 1
            if diff_hours < 3:
                flash += 1
        
        if flash > 0:
            badges.append({'code': 'velocista', 'name': f'Velocista ({flash}x)', 'category': 'velocidade'})
        if speed_demon > 0:
            badges.append({'code': 'relampago', 'name': f'Relampago ({speed_demon}x)', 'category': 'velocidade'})
    
    return badges

def save_badge_to_database(user_type, user_id, user_name, badge, deal_id=None, deal_name=None, metric_value=None, pipeline=None, context=None):
    """Salva badge desbloqueado no banco de dados"""
    with get_db_connection_context() as conn:
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            
            context_json = json.dumps(context) if context else None
            
            # INSERT com ON CONFLICT para evitar duplicatas
            query = """
                INSERT INTO badges_desbloqueados 
                    (user_type, user_id, user_name, badge_code, badge_name, badge_category, 
                     deal_id, deal_name, metric_value, pipeline, source, context)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'hubspot_api', %s)
                ON CONFLICT (user_type, user_id, badge_code, DATE(unlocked_at)) 
                DO UPDATE SET 
                    metric_value = GREATEST(badges_desbloqueados.metric_value, EXCLUDED.metric_value),
                    context = EXCLUDED.context
                RETURNING id
            """
            
            cursor.execute(query, (
                user_type, user_id, user_name, badge['code'], badge['name'], badge['category'],
                deal_id, deal_name, metric_value, pipeline, context_json
            ))
            
            badge_id = cursor.fetchone()[0]
            conn.commit()
            
            print(f"[OK] Badge salvo: {badge['name']} para {user_name} (ID: {badge_id})")
            
            cursor.close()
            return badge_id
            
        except Exception as e:
            print(f"[ERRO] Erro ao salvar badge: {e}")
            if conn:
                conn.rollback()
            return None

def get_user_badges(user_type, user_id, date_filter=None):
    """Retorna todos os badges de um usuário"""
    with get_db_connection_context() as conn:
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT 
                    badge_code, badge_name, badge_category, unlocked_at,
                    metric_value, pipeline, context
                FROM badges_desbloqueados
                WHERE user_type = %s AND user_id = %s
            """
            params = [user_type, user_id]
            
            if date_filter == 'today':
                query += " AND DATE(unlocked_at) = CURRENT_DATE"
            elif date_filter == 'week':
                query += " AND unlocked_at >= CURRENT_DATE - INTERVAL '7 days'"
            elif date_filter == 'month':
                query += " AND unlocked_at >= CURRENT_DATE - INTERVAL '30 days'"
            
            query += " ORDER BY unlocked_at DESC"
            
            cursor.execute(query, params)
            badges = cursor.fetchall()
            cursor.close()
            
            return [dict(b) for b in badges]
            
        except Exception as e:
            print(f"❌ Erro ao buscar badges do usuário: {e}")
            return []

def get_recordes():
    """Retorna os recordes da Black November"""
    with get_db_connection_context() as conn:
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            recordes = {}
            
            # Maior dia de faturamento
            cursor.execute("""
                SELECT DATE(unlocked_at) as data, user_name, SUM(metric_value) as total
                FROM badges_desbloqueados
                WHERE badge_category = 'valor' AND metric_value IS NOT NULL AND user_type = 'EV'
                GROUP BY DATE(unlocked_at), user_name
                ORDER BY total DESC LIMIT 1
            """)
            maior_dia = cursor.fetchone()
            if maior_dia:
                recordes['maior_dia'] = {
                    'data': maior_dia['data'].strftime('%d/%m/%Y'),
                    'usuario': maior_dia['user_name'],
                    'valor': float(maior_dia['total'])
                }
            
            # Maior deal individual
            cursor.execute("""
                SELECT user_name, deal_name, metric_value as valor, unlocked_at
                FROM badges_desbloqueados
                WHERE badge_category = 'valor' AND metric_value IS NOT NULL
                ORDER BY metric_value DESC LIMIT 1
            """)
            maior_deal = cursor.fetchone()
            if maior_deal:
                recordes['maior_deal'] = {
                    'usuario': maior_deal['user_name'],
                    'deal': maior_deal['deal_name'],
                    'valor': float(maior_deal['valor']),
                    'data': maior_deal['unlocked_at'].strftime('%d/%m/%Y')
                }
            
            # Mais deals em 1 dia
            cursor.execute("""
                SELECT DATE(unlocked_at) as data, user_name, COUNT(*) as total_deals
                FROM badges_desbloqueados
                WHERE badge_category = 'volume'
                GROUP BY DATE(unlocked_at), user_name
                ORDER BY total_deals DESC LIMIT 1
            """)
            mais_deals = cursor.fetchone()
            if mais_deals:
                recordes['mais_deals_dia'] = {
                    'data': mais_deals['data'].strftime('%d/%m/%Y'),
                    'usuario': mais_deals['user_name'],
                    'total': mais_deals['total_deals']
                }
            
            cursor.close()
            return recordes
            
        except Exception as e:
            print(f"❌ Erro ao buscar recordes: {e}")
            return {}

