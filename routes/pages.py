"""
Rotas de páginas (templates HTML)
"""
from flask import Blueprint, render_template, abort
from utils.auth import require_auth
import os
import json

pages_bp = Blueprint('pages', __name__)

def load_themes_config():
    """Carrega configuração de temas"""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    THEMES_CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'themes_config.json')
    
    try:
        if os.path.exists(THEMES_CONFIG_FILE):
            with open(THEMES_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'themes': {}, 'default_theme': 'natal'}
    except Exception as e:
        print(f"Erro ao carregar temas: {e}")
        return {'themes': {}, 'default_theme': 'natal'}

@pages_bp.route('/')
@require_auth
def index():
    """Página principal - Seleção de temas"""
    return render_template('index.html')

@pages_bp.route('/temas/<theme_id>/painéis')
@require_auth
def theme_panels(theme_id):
    """Página de seleção de painéis de um tema específico"""
    config = load_themes_config()
    themes = config.get('themes', {})
    
    if theme_id not in themes:
        abort(404, description=f"Tema '{theme_id}' não encontrado")
    
    theme = themes[theme_id]
    
    return render_template('theme_panels.html',
                         theme_id=theme_id,
                         theme_name=theme.get('name', theme_id),
                         theme_icon=theme.get('icon', '📊'),
                         theme_data=theme)

@pages_bp.route('/temas/<theme_id>/<panel_id>')
@require_auth
def theme_panel(theme_id, panel_id):
    """Rota dinâmica para painéis de temas"""
    config = load_themes_config()
    themes = config.get('themes', {})
    
    if theme_id not in themes:
        abort(404, description=f"Tema '{theme_id}' não encontrado")
    
    theme = themes[theme_id]
    panels = theme.get('panels', {})
    
    if panel_id not in panels:
        abort(404, description=f"Painel '{panel_id}' não encontrado no tema '{theme_id}'")
    
    panel = panels[panel_id]
    template = panel.get('template')
    
    if not template:
        abort(500, description=f"Template não configurado para o painel '{panel_id}'")
    
    # Renderiza o template (Flask verifica automaticamente se existe)
    return render_template(template)

# ============================================================================
# ROTAS LEGADAS - Mantidas para compatibilidade (redirecionam para novo sistema)
# ============================================================================

@pages_bp.route('/natal')
@require_auth
def natal():
    """Rota legada - Redireciona para novo sistema"""
    return render_template('funnel_natal.html')

@pages_bp.route('/black-november')
@require_auth
def black_november():
    """Rota legada - Redireciona para novo sistema"""
    return render_template('funnel_black_november.html')

@pages_bp.route('/natal/logos-supply')
@require_auth
def logos_supply_natal():
    """Rota legada - Redireciona para novo sistema"""
    return render_template('supply_logos_natal.html')

@pages_bp.route('/natal/arr')
@require_auth
def natal_arr():
    """Rota legada - Redireciona para novo sistema"""
    return render_template('arr_natal.html')

@pages_bp.route('/natal/metas')
@require_auth
def metas_natal():
    """Rota legada - Redireciona para novo sistema"""
    return render_template('metas_natal.html')

@pages_bp.route('/black-november/metas')
@require_auth
def metas_black_november():
    """Rota legada - Redireciona para novo sistema"""
    return render_template('metas_black_november.html')

@pages_bp.route('/metas')
@require_auth
def metas():
    """Rota legada - Redireciona para Natal"""
    return render_template('metas_natal.html')

@pages_bp.route('/demo')
@require_auth
def demo():
    """Rota para página de teste/demo com controles"""
    return render_template('funnel_demo.html')

@pages_bp.route('/natal/hall-da-fama')
@require_auth
def hall_da_fama_natal():
    """Rota legada - Redireciona para novo sistema"""
    return render_template('hall_da_fama_natal.html')

@pages_bp.route('/black-november/hall-da-fama')
@require_auth
def hall_da_fama_black_november():
    """Rota legada - Redireciona para novo sistema"""
    return render_template('hall_da_fama_black_november.html')

@pages_bp.route('/hall-da-fama')
@require_auth
def hall_da_fama():
    """Rota legada - Redireciona para Natal"""
    return render_template('hall_da_fama_natal.html')

@pages_bp.route('/natal/destaques')
@require_auth
def destaques_natal():
    """Rota legada - Redireciona para novo sistema"""
    return render_template('destaques_natal.html')

@pages_bp.route('/black-november/destaques')
@require_auth
def destaques_black_november():
    """Rota legada - Redireciona para novo sistema"""
    return render_template('destaques_black_november.html')

@pages_bp.route('/destaques')
@require_auth
def destaques():
    """Rota legada - Redireciona para Natal"""
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
