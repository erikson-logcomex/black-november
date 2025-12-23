"""
API endpoint para buscar dados do Looker
Usa navegador headless no backend para manter sessão autenticada
"""

from flask import Blueprint, jsonify
from utils.looker_scraper import get_looker_gauge_value

looker_bp = Blueprint('looker', __name__, url_prefix='/api/looker')

@looker_bp.route('/gauge-value', methods=['GET'])
def get_gauge_value():
    """
    Retorna o valor atual do gauge do Looker (considera churns)
    """
    try:
        result = get_looker_gauge_value()
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Não foi possível obter os dados do Looker'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

