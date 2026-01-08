"""
API Routes para gerenciamento de temas
"""
from flask import Blueprint, jsonify
import os
import json

themes_bp = Blueprint('themes', __name__, url_prefix='/api/themes')

def load_themes_config():
    """Carrega configuração de temas do arquivo JSON"""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    THEMES_CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'themes_config.json')
    
    try:
        if os.path.exists(THEMES_CONFIG_FILE):
            with open(THEMES_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {'themes': {}, 'default_theme': 'natal'}
    except Exception as e:
        print(f"Erro ao carregar configuração de temas: {e}")
        return {'themes': {}, 'default_theme': 'natal'}

@themes_bp.route('/config')
def get_themes_config():
    """Retorna configuração completa de temas"""
    try:
        config = load_themes_config()
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar temas: {str(e)}'}), 500

@themes_bp.route('/<theme_id>')
def get_theme(theme_id):
    """Retorna informações de um tema específico"""
    try:
        config = load_themes_config()
        themes = config.get('themes', {})
        
        if theme_id not in themes:
            return jsonify({'error': f'Tema "{theme_id}" não encontrado'}), 404
        
        return jsonify({
            'theme_id': theme_id,
            'theme': themes[theme_id]
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar tema: {str(e)}'}), 500
