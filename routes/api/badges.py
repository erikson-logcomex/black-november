"""
API Routes para badges e recordes
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from utils.mappings import get_analyst_name
from utils.badges import get_user_badges, get_recordes
from utils.db import get_db_connection_context
from psycopg2.extras import RealDictCursor

badges_bp = Blueprint('badges', __name__, url_prefix='/api')

@badges_bp.route('/badges/user/<user_type>/<user_id>')
def get_user_badges_api(user_type, user_id):
    """Retorna badges de um usuário específico"""
    try:
        date_filter = request.args.get('filter', None)
        badges = get_user_badges(user_type, user_id, date_filter)
        
        return jsonify({
            'status': 'success',
            'userType': user_type,
            'userId': user_id,
            'userName': get_analyst_name(user_id),
            'filter': date_filter,
            'badges': badges,
            'total': len(badges)
        })
        
    except Exception as e:
        print(f"Erro ao buscar badges do usuário: {e}")
        return jsonify({'error': str(e)}), 500

@badges_bp.route('/recordes')
def get_recordes_api():
    """Retorna recordes da Black November"""
    try:
        recordes = get_recordes()
        
        return jsonify({
            'status': 'success',
            'recordes': recordes,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Erro ao buscar recordes: {e}")
        return jsonify({'error': str(e)}), 500

@badges_bp.route('/mvp-semana')
def get_mvp_semana():
    """Retorna MVP da semana (últimos 7 dias)"""
    with get_db_connection_context() as conn:
        if not conn:
            return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            mvps = {}
            
            # MVP EVs (por revenue)
            cursor.execute("""
                SELECT 
                    user_id, user_name,
                    SUM(metric_value) as total_revenue,
                    COUNT(DISTINCT DATE(unlocked_at)) as dias_ativos,
                    COUNT(*) as total_badges
                FROM badges_desbloqueados
                WHERE user_type = 'EV'
                    AND unlocked_at >= CURRENT_DATE - INTERVAL '7 days'
                    AND metric_value IS NOT NULL
                GROUP BY user_id, user_name
                ORDER BY total_revenue DESC
                LIMIT 1
            """)
            mvp_ev = cursor.fetchone()
            if mvp_ev:
                mvps['ev'] = {
                    'userId': mvp_ev['user_id'],
                    'userName': mvp_ev['user_name'],
                    'totalRevenue': float(mvp_ev['total_revenue']),
                    'diasAtivos': mvp_ev['dias_ativos'],
                    'totalBadges': mvp_ev['total_badges']
                }
            
            # MVP SDRs (por número de agendamentos)
            cursor.execute("""
                SELECT 
                    user_id, user_name, pipeline,
                    COUNT(*) as total_badges,
                    COUNT(DISTINCT DATE(unlocked_at)) as dias_ativos
                FROM badges_desbloqueados
                WHERE user_type = 'SDR'
                    AND unlocked_at >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY user_id, user_name, pipeline
                ORDER BY total_badges DESC
                LIMIT 1
            """)
            mvp_sdr = cursor.fetchone()
            if mvp_sdr:
                mvps['sdr'] = {
                    'userId': mvp_sdr['user_id'],
                    'userName': mvp_sdr['user_name'],
                    'pipeline': mvp_sdr['pipeline'],
                    'totalBadges': mvp_sdr['total_badges'],
                    'diasAtivos': mvp_sdr['dias_ativos']
                }
            
            # MVP LDRs (por revenue)
            cursor.execute("""
                SELECT 
                    user_id, user_name,
                    SUM(metric_value) as total_revenue,
                    COUNT(DISTINCT DATE(unlocked_at)) as dias_ativos,
                    COUNT(*) as total_badges
                FROM badges_desbloqueados
                WHERE user_type = 'LDR'
                    AND unlocked_at >= CURRENT_DATE - INTERVAL '7 days'
                    AND metric_value IS NOT NULL
                GROUP BY user_id, user_name
                ORDER BY total_revenue DESC
                LIMIT 1
            """)
            mvp_ldr = cursor.fetchone()
            if mvp_ldr:
                mvps['ldr'] = {
                    'userId': mvp_ldr['user_id'],
                    'userName': mvp_ldr['user_name'],
                    'totalRevenue': float(mvp_ldr['total_revenue']),
                    'diasAtivos': mvp_ldr['dias_ativos'],
                    'totalBadges': mvp_ldr['total_badges']
                }
            
            cursor.close()
            
            return jsonify({
                'status': 'success',
                'mvps': mvps,
                'periodo': 'últimos 7 dias',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Erro ao buscar MVP da semana: {e}")
            return jsonify({'error': str(e)}), 500

@badges_bp.route('/badges/stats')
def get_badges_stats():
    """Retorna estatísticas gerais de badges"""
    with get_db_connection_context() as conn:
        if not conn:
            return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            stats = {}
            
            # Total de badges desbloqueados hoje
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM badges_desbloqueados
                WHERE DATE(unlocked_at) = CURRENT_DATE
            """)
            stats['badges_hoje'] = cursor.fetchone()['total']
            
            # Total de badges na semana
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM badges_desbloqueados
                WHERE unlocked_at >= CURRENT_DATE - INTERVAL '7 days'
            """)
            stats['badges_semana'] = cursor.fetchone()['total']
            
            # Badges por categoria hoje
            cursor.execute("""
                SELECT 
                    badge_category,
                    COUNT(*) as total
                FROM badges_desbloqueados
                WHERE DATE(unlocked_at) = CURRENT_DATE
                GROUP BY badge_category
                ORDER BY total DESC
            """)
            stats['por_categoria_hoje'] = {row['badge_category']: row['total'] for row in cursor.fetchall()}
            
            # Top 3 usuários com mais badges hoje
            cursor.execute("""
                SELECT 
                    user_name, user_type,
                    COUNT(*) as total_badges
                FROM badges_desbloqueados
                WHERE DATE(unlocked_at) = CURRENT_DATE
                GROUP BY user_name, user_type
                ORDER BY total_badges DESC
                LIMIT 3
            """)
            stats['top_usuarios_hoje'] = [dict(row) for row in cursor.fetchall()]
            
            cursor.close()
            
            return jsonify({
                'status': 'success',
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Erro ao buscar estatísticas de badges: {e}")
            return jsonify({'error': str(e)}), 500

