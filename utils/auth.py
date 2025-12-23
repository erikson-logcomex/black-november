"""
Utilitários para autenticação e autorização
"""
from functools import wraps
from flask import session, request, redirect, url_for

# IPs permitidos para acesso direto
ALLOWED_IPS = ['127.0.0.1', 'localhost', '168.90.50.50', '200.169.67.198']
ALLOWED_DOMAIN = '@logcomex.com'

def get_client_ip():
    """Obtém o IP real do cliente, considerando proxies"""
    if request.headers.get('X-Forwarded-For'):
        # Cloud Run usa X-Forwarded-For
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def is_allowed_ip():
    """Verifica se o IP do cliente está na lista de IPs permitidos"""
    client_ip = get_client_ip()
    is_allowed = client_ip in ALLOWED_IPS
    print(f"[DEBUG] IP do cliente: {client_ip} | Permitido: {is_allowed} | IPs permitidos: {ALLOWED_IPS}")
    return is_allowed

def require_auth(f):
    """
    Decorator que protege rotas:
    - Permite acesso direto se IP for permitido
    - Caso contrário, requer autenticação Google (@logcomex.com)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se é IP permitido
        if is_allowed_ip():
            return f(*args, **kwargs)
        
        # Verifica se usuário está autenticado
        if 'user' in session:
            return f(*args, **kwargs)
        
        # Redireciona para login
        session['next'] = request.url
        return redirect(url_for('auth.login'))
    
    return decorated_function


