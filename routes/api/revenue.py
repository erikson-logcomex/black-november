"""
API Routes para receita e faturamento
"""
from flask import Blueprint, jsonify, request
from utils.auth import require_auth
from utils.revenue import (
    get_black_november_revenue,
    get_december_revenue,
    get_current_month_revenue,
    get_revenue_until_yesterday,
    get_today_revenue,
    get_renewal_pipeline_revenue,
    load_manual_revenue_config
)

revenue_bp = Blueprint('revenue', __name__, url_prefix='/api/revenue')

@revenue_bp.route('')
@require_auth
def api_revenue():
    """API que retorna dados de faturamento em JSON"""
    # Verifica se é para pegar dados de dezembro (Natal), novembro (Black November) ou mês atual
    month = request.args.get('month', 'november').lower()
    
    # TODO: Implementar cache quando mover para módulo separado
    if month == 'december' or month == 'dezembro':
        data = get_december_revenue()
    elif month == 'current' or month == 'atual' or month == 'current-month':
        # Carrega configuração antes de buscar dados
        config = load_manual_revenue_config()
        # SEMPRE exclui o pipeline de renovação da query base para evitar duplicação
        # O valor do pipeline de renovação será adicionado separadamente se habilitado
        data = get_current_month_revenue(exclude_renewal_pipeline=True)
    else:
        data = get_black_november_revenue()
    
    if data:
        config = load_manual_revenue_config()
        if config.get('enabled', False):
            additional_value = float(config.get('additionalValue', 0))
            data['total'] = data['total'] + additional_value
            data['has_manual_adjustment'] = True
            data['manual_additional_value'] = additional_value
        else:
            data['has_manual_adjustment'] = False
        
        # Adiciona receita do pipeline de Renovação se habilitado
        # (só adiciona se não foi excluído na query)
        if config.get('includeRenewalPipeline', False):
            renewal_revenue = get_renewal_pipeline_revenue()
            data['total'] = data['total'] + renewal_revenue
            data['has_renewal_pipeline'] = True
            data['renewal_pipeline_revenue'] = renewal_revenue
        else:
            data['has_renewal_pipeline'] = False
        
        return jsonify(data)
    else:
        return jsonify({'error': 'Erro ao buscar dados'}), 500

@revenue_bp.route('/today')
def api_revenue_today():
    """API que retorna faturamento do dia atual"""
    # Carrega configuração antes de buscar dados para saber se deve excluir renovação
    config = load_manual_revenue_config()
    # Se includeRenewalPipeline está desativado, exclui o pipeline de renovação da query
    exclude_renewal = not config.get('includeRenewalPipeline', False)
    data = get_today_revenue(exclude_renewal_pipeline=exclude_renewal)
    
    if data:
        config = load_manual_revenue_config()
        if config.get('enabled', False):
            additional_value = float(config.get('additionalValue', 0))
            data['total_today'] = data['total_today'] + additional_value
            data['has_manual_adjustment'] = True
            data['manual_additional_value'] = additional_value
        else:
            data['has_manual_adjustment'] = False
        
        # Adiciona receita do pipeline de Renovação se habilitado
        # (só adiciona se não foi excluído na query)
        if config.get('includeRenewalPipeline', False):
            # Busca apenas deals de hoje do pipeline de renovação
            from datetime import datetime, timezone, timedelta
            BRAZIL_TZ_OFFSET = timedelta(hours=-3)
            now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
            today_start_brazil = now_brazil.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end_brazil = now_brazil.replace(hour=23, minute=59, second=59, microsecond=999999)
            today_start_utc = today_start_brazil - BRAZIL_TZ_OFFSET
            today_end_utc = today_end_brazil - BRAZIL_TZ_OFFSET
            
            renewal_revenue_today = get_renewal_pipeline_revenue(start_date_utc=today_start_utc, end_date_utc=today_end_utc)
            data['total_today'] = data['total_today'] + renewal_revenue_today
            data['has_renewal_pipeline'] = True
            data['renewal_pipeline_revenue_today'] = renewal_revenue_today
        else:
            data['has_renewal_pipeline'] = False
        
        return jsonify(data)
    else:
        return jsonify({'error': 'Erro ao buscar dados do dia'}), 500

@revenue_bp.route('/until-yesterday')
@require_auth
def api_revenue_until_yesterday():
    """API que retorna faturamento até ontem (excluindo o dia atual)"""
    # Carrega configuração antes de buscar dados para saber se deve excluir renovação
    config = load_manual_revenue_config()
    # Se includeRenewalPipeline está desativado, exclui o pipeline de renovação da query
    exclude_renewal = not config.get('includeRenewalPipeline', False)
    data = get_revenue_until_yesterday(exclude_renewal_pipeline=exclude_renewal)
    
    if data:
        config = load_manual_revenue_config()
        
        # Adiciona receita do pipeline de Renovação se habilitado
        # (só adiciona se não foi excluído na query)
        if config.get('includeRenewalPipeline', False):
            # Busca apenas deals até ontem do pipeline de renovação
            from datetime import datetime, timezone, timedelta
            BRAZIL_TZ_OFFSET = timedelta(hours=-3)
            now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
            month_start_brazil = now_brazil.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            yesterday_end_brazil = now_brazil.replace(hour=23, minute=59, second=59, microsecond=999999) - timedelta(days=1)
            month_start_utc = month_start_brazil - BRAZIL_TZ_OFFSET
            yesterday_end_utc = yesterday_end_brazil - BRAZIL_TZ_OFFSET
            
            renewal_revenue_until_yesterday = get_renewal_pipeline_revenue(start_date_utc=month_start_utc, end_date_utc=yesterday_end_utc)
            data['total'] = data['total'] + renewal_revenue_until_yesterday
            data['has_renewal_pipeline'] = True
            data['renewal_pipeline_revenue'] = renewal_revenue_until_yesterday
        else:
            data['has_renewal_pipeline'] = False
        
        return jsonify(data)
    else:
        return jsonify({'error': 'Erro ao buscar dados até ontem'}), 500

@revenue_bp.route('/manual-revenue/config', methods=['GET'])
def get_manual_revenue_config():
    """Retorna a configuração do modo manual de faturamento"""
    import os
    import json
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MANUAL_REVENUE_CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'manual_revenue_config.json')
    
    try:
        if os.path.exists(MANUAL_REVENUE_CONFIG_FILE):
            with open(MANUAL_REVENUE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return jsonify(config)
        else:
            default_config = {"enabled": False, "additionalValue": 0, "includeRenewalPipeline": False}
            return jsonify(default_config)
    except Exception as e:
        print(f"Erro ao ler configuração de faturamento manual: {e}")
        return jsonify({'error': 'Erro ao ler configuração'}), 500

@revenue_bp.route('/manual-revenue/config', methods=['POST'])
@require_auth
def save_manual_revenue_config():
    """Salva a configuração do modo manual de faturamento"""
    import os
    import json
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MANUAL_REVENUE_CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'manual_revenue_config.json')
    
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        enabled = bool(data.get('enabled', False))
        additional_value = float(data.get('additionalValue', 0))
        include_renewal_pipeline = bool(data.get('includeRenewalPipeline', False))
        
        if additional_value < 0:
            return jsonify({'error': 'Valor adicional não pode ser negativo'}), 400
        
        config = {
            "enabled": enabled,
            "additionalValue": additional_value,
            "includeRenewalPipeline": include_renewal_pipeline
        }
        
        data_dir = os.path.dirname(MANUAL_REVENUE_CONFIG_FILE)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, mode=0o777, exist_ok=True)
        
        with open(MANUAL_REVENUE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        try:
            os.chmod(MANUAL_REVENUE_CONFIG_FILE, 0o666)
        except Exception as chmod_error:
            print(f"Aviso: Não foi possível alterar permissões do arquivo: {chmod_error}")
        
        print(f"Configuração de faturamento manual salva: enabled={enabled}, additionalValue={additional_value}, includeRenewalPipeline={include_renewal_pipeline}")
        return jsonify({'status': 'success', 'config': config})
        
    except PermissionError as e:
        print(f"Erro de permissão ao salvar configuração: {e}")
        return jsonify({'error': 'Erro de permissão ao salvar arquivo. Verifique as permissões da pasta data/'}), 500
    except Exception as e:
        print(f"Erro ao salvar configuração de faturamento manual: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro ao salvar configuração: {str(e)}'}), 500

@revenue_bp.route('/manual-goal/config', methods=['GET'])
def get_manual_goal_config():
    """Retorna a configuração da meta manual"""
    import os
    import json
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MANUAL_GOAL_CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'manual_goal_config.json')
    
    try:
        if os.path.exists(MANUAL_GOAL_CONFIG_FILE):
            with open(MANUAL_GOAL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return jsonify(config)
        else:
            default_config = {"enabled": False, "goalValue": 1500000}
            return jsonify(default_config)
    except Exception as e:
        print(f"Erro ao ler configuração de meta manual: {e}")
        return jsonify({'error': 'Erro ao ler configuração'}), 500

@revenue_bp.route('/manual-goal/config', methods=['POST'])
@require_auth
def save_manual_goal_config():
    """Salva a configuração da meta manual"""
    import os
    import json
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MANUAL_GOAL_CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'manual_goal_config.json')
    
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        enabled = bool(data.get('enabled', False))
        goal_value = float(data.get('goalValue', 1500000))
        
        if goal_value < 0:
            return jsonify({'error': 'Valor da meta não pode ser negativo'}), 400
        
        config = {
            "enabled": enabled,
            "goalValue": goal_value
        }
        
        data_dir = os.path.dirname(MANUAL_GOAL_CONFIG_FILE)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, mode=0o777, exist_ok=True)
        
        with open(MANUAL_GOAL_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        try:
            os.chmod(MANUAL_GOAL_CONFIG_FILE, 0o666)
        except Exception as chmod_error:
            print(f"Aviso: Não foi possível alterar permissões do arquivo: {chmod_error}")
        
        print(f"Configuração de meta manual salva: enabled={enabled}, goalValue={goal_value}")
        return jsonify({'status': 'success', 'config': config})
        
    except PermissionError as e:
        print(f"Erro de permissão ao salvar configuração: {e}")
        return jsonify({'error': 'Erro de permissão ao salvar arquivo. Verifique as permissões da pasta data/'}), 500
    except Exception as e:
        print(f"Erro ao salvar configuração de meta manual: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro ao salvar configuração: {str(e)}'}), 500

@revenue_bp.route('/celebration-theme/config', methods=['GET'])
def get_celebration_theme_config():
    """Retorna a configuração do tema de celebração"""
    import os
    import json
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    THEME_CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'celebration_theme_config.json')
    
    try:
        if os.path.exists(THEME_CONFIG_FILE):
            with open(THEME_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return jsonify(config)
        else:
            default_config = {"theme": "black-november"}
            return jsonify(default_config)
    except Exception as e:
        print(f"Erro ao ler configuração de tema de celebração: {e}")
        return jsonify({'error': 'Erro ao ler configuração'}), 500

@revenue_bp.route('/celebration-theme/config', methods=['POST'])
@require_auth
def save_celebration_theme_config():
    """Salva a configuração do tema de celebração"""
    import os
    import json
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    THEME_CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'celebration_theme_config.json')
    
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        theme = data.get('theme', 'black-november')
        
        # Valida o tema
        valid_themes = ['black-november', 'natal', 'padrao']
        if theme not in valid_themes:
            return jsonify({'error': f'Tema inválido. Temas válidos: {", ".join(valid_themes)}'}), 400
        
        config = {
            "theme": theme
        }
        
        data_dir = os.path.dirname(THEME_CONFIG_FILE)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, mode=0o777, exist_ok=True)
        
        with open(THEME_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        try:
            os.chmod(THEME_CONFIG_FILE, 0o666)
        except Exception as chmod_error:
            print(f"Aviso: Não foi possível alterar permissões do arquivo: {chmod_error}")
        
        print(f"Configuração de tema de celebração salva: theme={theme}")
        return jsonify({'status': 'success', 'config': config})
        
    except PermissionError as e:
        print(f"Erro de permissão ao salvar configuração: {e}")
        return jsonify({'error': 'Erro de permissão ao salvar arquivo. Verifique as permissões da pasta data/'}), 500
    except Exception as e:
        print(f"Erro ao salvar configuração de tema de celebração: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro ao salvar configuração: {str(e)}'}), 500

