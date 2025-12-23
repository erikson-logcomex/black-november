"""
API Routes para estatísticas de logos da BU Supply
"""
from flask import Blueprint, jsonify
from utils.auth import require_auth
from utils.supply_logos import get_supply_logos_stats
from utils.looker_scraper import get_looker_gauge_value

supply_logos_bp = Blueprint('supply_logos', __name__, url_prefix='/api/supply-logos')

@supply_logos_bp.route('')
@require_auth
def api_supply_logos():
    """API que retorna estatísticas de logos da BU Supply em JSON"""
    # Busca dados do banco para os cards e gráfico
    data = get_supply_logos_stats()
    
    if not data:
        return jsonify({'error': 'Erro ao buscar dados de logos Supply'}), 500
    
    # Busca o valor atual do Looker (considera churns) - OBRIGATÓRIO para o gauge
    try:
        looker_data = get_looker_gauge_value()
        if looker_data and looker_data.get('gauge_value'):
            # Usa o valor do Looker como total_current (já considera churns)
            looker_value = looker_data['gauge_value']
            looker_target = looker_data.get('gauge_target', data.get('target', 800))
            
            data['total_current'] = looker_value
            data['target'] = looker_target  # Usa o target do Looker também
            data['remaining'] = max(0, looker_target - looker_value)
            data['percentage'] = round((looker_value / looker_target * 100) if looker_target > 0 else 0, 2)
            data['from_looker'] = True  # Flag para indicar que veio do Looker
            print(f"✅ Usando valores do Looker: {looker_value}/{looker_target} (considera churns)")
        else:
            # SEM FALLBACK - retorna erro se Looker não disponível
            return jsonify({
                'error': 'Não foi possível obter os dados do Looker',
                'message': 'O scraper do Looker retornou None. Verifique os logs do servidor.'
            }), 500
    except Exception as e:
        print(f"❌ Erro ao buscar valor do Looker: {e}")
        import traceback
        traceback.print_exc()
        # SEM FALLBACK - retorna erro se Looker falhar
        return jsonify({
            'error': f'Erro ao buscar dados do Looker: {str(e)}',
            'message': 'O sistema requer dados do Looker para funcionar corretamente.'
        }), 500
    
    return jsonify(data)

