"""
Rotas de autenticação
"""
from flask import Blueprint, render_template, redirect, url_for, session, request
from authlib.integrations.flask_client import OAuth
import os
from utils.auth import is_allowed_ip

auth_bp = Blueprint('auth', __name__)

# Configuração OAuth Google (será inicializado no app.py)
google = None

def init_oauth(app):
    """Inicializa OAuth no blueprint"""
    global google
    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

@auth_bp.route('/login')
def login():
    """Página de login com Google OAuth"""
    # Se o IP é permitido, redireciona direto para o index (seleção de painéis)
    if is_allowed_ip():
        return redirect(url_for('pages.index'))
    
    return render_template('login.html')

@auth_bp.route('/auth/google/login')
def google_login():
    """Inicia o fluxo OAuth do Google"""
    global google
    if not google:
        return "OAuth não configurado", 500
    
    # Usa a variável de ambiente se disponível, senão gera automaticamente
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI') or url_for('auth.auth_callback', _external=True, _scheme='https')
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/google/callback')
def auth_callback():
    """Callback do Google OAuth"""
    global google
    if not google:
        return "OAuth não configurado", 500
    
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            return "Erro ao obter informações do usuário", 400
        
        email = user_info.get('email', '')
        ALLOWED_DOMAIN = '@logcomex.com'
        
        # Valida domínio do email
        if not email.endswith(ALLOWED_DOMAIN):
            return f"Acesso negado. Apenas emails {ALLOWED_DOMAIN} são permitidos.", 403
        
        # Salva usuário na sessão
        session['user'] = {
            'email': email,
            'name': user_info.get('name', ''),
            'picture': user_info.get('picture', '')
        }
        
        # Redireciona para página original ou home
        next_url = session.pop('next', url_for('pages.index'))
        return redirect(next_url)
        
    except Exception as e:
        print(f"Erro no callback OAuth: {e}")
        return f"Erro na autenticação: {str(e)}", 400

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.pop('user', None)
    return redirect(url_for('pages.index'))


