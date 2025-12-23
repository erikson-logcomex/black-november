"""
API Routes para pipeline
"""
from flask import Blueprint, jsonify, request
from utils.db import get_db_connection_context
from utils.cache import get_cache, get_cache_lock
from psycopg2.extras import RealDictCursor

pipeline_bp = Blueprint('pipeline', __name__, url_prefix='/api/pipeline')

def get_pipeline_today():
    """Busca deals com previsão de fechamento HOJE que ainda não foram ganhos"""
    with get_db_connection_context() as conn:
        if not conn:
            return None
        
        try:
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
                    COALESCE(SUM(amount), 0) as total_pipeline,
                    COALESCE(AVG(amount), 0) as avg_deal_value,
                    COALESCE(MIN(amount), 0) as min_deal_value,
                    COALESCE(MAX(amount), 0) as max_deal_value
                FROM previstos_hoje
            """
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                data = {
                    'total_deals': result['total_deals'],
                    'total_pipeline': float(result['total_pipeline']),
                    'avg_deal_value': float(result['avg_deal_value']),
                    'min_deal_value': float(result['min_deal_value']),
                    'max_deal_value': float(result['max_deal_value']),
                    'date': request.args.get('date') or None
                }
            else:
                data = {
                    'total_deals': 0,
                    'total_pipeline': 0.0,
                    'avg_deal_value': 0.0,
                    'min_deal_value': 0.0,
                    'max_deal_value': 0.0,
                    'date': None
                }
            
            cursor.close()
            return data
        except Exception as e:
            print(f"Erro ao buscar pipeline do dia: {e}")
            return None

@pipeline_bp.route('/today')
def api_pipeline_today():
    """API que retorna pipeline previsto para fechar hoje"""
    _data_cache = get_cache()
    _cache_lock = get_cache_lock()
    
    use_cache = request.args.get('use_cache', 'false').lower() == 'true'
    if use_cache and _data_cache.get('pipeline_today'):
        response = jsonify(_data_cache['pipeline_today'])
        response.headers['X-Cache'] = 'HIT'
        return response
    
    data = get_pipeline_today()
    if data:
        if not use_cache:
            with _cache_lock:
                _data_cache['pipeline_today'] = data
        
        response = jsonify(data)
        response.headers['X-Cache'] = 'MISS'
        return response
    else:
        return jsonify({'error': 'Erro ao buscar pipeline do dia'}), 500


