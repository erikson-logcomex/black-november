"""
Rotas de páginas (templates HTML)
"""
from flask import Blueprint, render_template
from utils.auth import require_auth

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
@require_auth
def index():
    """Página principal - Seleção de painéis"""
    return render_template('index.html')

@pages_bp.route('/natal')
@require_auth
def natal():
    """Rota para painel de Natal"""
    return render_template('funnel_natal.html')

@pages_bp.route('/natal/logos-supply')
@require_auth
def logos_supply_natal():
    """Rota para página de Logos Supply - Natal"""
    return render_template('supply_logos_natal.html')

@pages_bp.route('/natal/arr')
@require_auth
def natal_arr():
    """Rota para página de ARR - Natal"""
    return render_template('arr_natal.html')

@pages_bp.route('/black-november')
@require_auth
def black_november():
    """Rota para versão Black November"""
    return render_template('funnel_black_november.html')

@pages_bp.route('/natal/metas')
@require_auth
def metas_natal():
    """Rota para página de meta diária - Versão Natal"""
    return render_template('metas_natal.html')

@pages_bp.route('/black-november/metas')
@require_auth
def metas_black_november():
    """Rota para versão Black November"""
    return render_template('metas_black_november.html')

# Mantém rota antiga para compatibilidade
@pages_bp.route('/metas')
@require_auth
def metas():
    """Rota para página de meta diária - Redireciona para Natal"""
    return render_template('metas_natal.html')

@pages_bp.route('/demo')
@require_auth
def demo():
    """Rota para página de teste/demo com controles"""
    return render_template('funnel_demo.html')

@pages_bp.route('/natal/hall-da-fama')
@require_auth
def hall_da_fama_natal():
    """Página Hall da Fama com badges e conquistas - Versão Natal"""
    return render_template('hall_da_fama_natal.html')

@pages_bp.route('/black-november/hall-da-fama')
@require_auth
def hall_da_fama_black_november():
    """Rota para versão Black November"""
    return render_template('hall_da_fama_black_november.html')

# Mantém rota antiga para compatibilidade
@pages_bp.route('/hall-da-fama')
@require_auth
def hall_da_fama():
    """Página Hall da Fama - Redireciona para Natal"""
    return render_template('hall_da_fama_natal.html')

@pages_bp.route('/natal/destaques')
@require_auth
def destaques_natal():
    """Página de destaques da semana e do mês - Versão Natal"""
    return render_template('destaques_natal.html')

@pages_bp.route('/black-november/destaques')
@require_auth
def destaques_black_november():
    """Rota para versão Black November"""
    return render_template('destaques_black_november.html')

# Mantém rota antiga para compatibilidade
@pages_bp.route('/destaques')
@require_auth
def destaques():
    """Página de destaques - Redireciona para Natal"""
    return render_template('destaques_natal.html')

@pages_bp.route('/aleatorio')
def aleatorio():
    """Página de rotação automática"""
    return render_template('aleatorio.html')

@pages_bp.route('/webhook-debug')
@require_auth
def webhook_debug():
    """Interface de debug para visualizar webhooks recebidos"""
    from routes.api.webhooks import webhook_logs, deal_notifications
    from utils.deals import fetch_pending_notifications_db
    
    # Busca notificações do banco de dados (últimas 50)
    db_notifications = fetch_pending_notifications_db(client_id=None, since_timestamp=None, limit=50)
    
    # Se banco não estiver disponível, usa fallback em memória
    if db_notifications is None:
        db_notifications = deal_notifications
    
    return render_template('webhook_debug.html', 
                         webhook_logs=webhook_logs,
                         notifications=db_notifications)

