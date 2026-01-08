"""
Aplicação Flask - Estrutura Modular
Similar ao App Router do Next.js
"""
from flask import Flask
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Define o diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cria aplicação Flask
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))

# ============================================================================
# INICIALIZAÇÃO DE MÓDULOS
# ============================================================================

# Inicializa banco de dados (pool de conexões)
from utils.db import init_db_pool
init_db_pool()

# Inicializa OAuth
from routes.auth import init_oauth
init_oauth(app)

# Inicializa cache
from utils.cache_manager import start_cache_refresh_thread
start_cache_refresh_thread(app)

# Carrega mapeamentos
from utils.mappings import load_analysts_mapping, load_produtos_depara
load_analysts_mapping()
load_produtos_depara()

# ============================================================================
# REGISTRO DE BLUEPRINTS
# ============================================================================

# Rotas de páginas
from routes.pages import pages_bp
app.register_blueprint(pages_bp)

# Rotas de autenticação
from routes.auth import auth_bp
app.register_blueprint(auth_bp)

# APIs
from routes.api.revenue import revenue_bp
from routes.api.pipeline import pipeline_bp
from routes.api.deals import deals_bp
from routes.api.webhooks import webhooks_bp
from routes.api.debug import debug_bp
from routes.api.static_files import static_bp

app.register_blueprint(revenue_bp)
app.register_blueprint(pipeline_bp)
app.register_blueprint(deals_bp)
app.register_blueprint(webhooks_bp)
app.register_blueprint(debug_bp)
app.register_blueprint(static_bp)

# Blueprints restantes
from routes.api.rankings import rankings_bp
from routes.api.hall_da_fama import hall_da_fama_bp
from routes.api.destaques import destaques_bp
from routes.api.badges import badges_bp
from routes.api.reports import reports_bp
from routes.api.supply_logos import supply_logos_bp

app.register_blueprint(rankings_bp)
app.register_blueprint(hall_da_fama_bp)
app.register_blueprint(destaques_bp)
app.register_blueprint(badges_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(supply_logos_bp)

from routes.api.looker import looker_bp
app.register_blueprint(looker_bp)
from routes.api.arr import arr_bp
app.register_blueprint(arr_bp)
from routes.api.themes import themes_bp
app.register_blueprint(themes_bp)

print("[OK] Aplicacao Flask inicializada com estrutura modular")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

