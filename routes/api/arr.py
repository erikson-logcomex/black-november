"""
API Routes para dados de ARR do Looker
"""
from flask import Blueprint, jsonify
from utils.auth import require_auth
from utils.arr_scraper import get_arr_value
import traceback

arr_bp = Blueprint('arr', __name__, url_prefix='/api/arr')

@arr_bp.route('')
@require_auth
def api_arr():
    """API que retorna dados de ARR do Looker em JSON"""
    try:
        result = get_arr_value()
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({
                'error': 'Não foi possível obter os dados de ARR do Looker',
                'message': 'O scraper retornou None. Verifique os logs do servidor.'
            }), 500
            
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Erro no endpoint /api/arr: {e}")
        print(f"📋 Traceback completo:\n{error_trace}")
        return jsonify({
            'error': str(e),
            'traceback': error_trace
        }), 500

