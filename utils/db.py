"""
Utilitários para gerenciamento de banco de dados
"""
import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pool de conexões compartilhado
_db_pool = None

def init_db_pool():
    """Inicializa o pool de conexões PostgreSQL com SSL"""
    global _db_pool
    if _db_pool is None:
        try:
            # Configuração SSL para criptografia em trânsito
            ssl_params = {
                'sslmode': 'require'  # Padrão: SSL sem verificação de certificado
            }
            
            # Tenta encontrar certificado CA (prioridade: Secret Manager > arquivo local)
            ssl_cert_path = None
            
            # 1. Verifica se tem certificado no Secret Manager (Cloud Run)
            ssl_cert_content = os.getenv('CLOUD_SQL_CA_CERT')
            if ssl_cert_content:
                # Escrever certificado em arquivo temporário
                ssl_cert_path = '/tmp/server-ca.pem'
                try:
                    with open(ssl_cert_path, 'w') as f:
                        f.write(ssl_cert_content)
                    print("[SSL] Certificado CA obtido do Secret Manager")
                except Exception as cert_error:
                    print(f"[AVISO] Erro ao escrever certificado do Secret Manager: {cert_error}")
                    ssl_cert_path = None
            
            # 2. Se não tiver no Secret Manager, verifica arquivo local (desenvolvimento)
            if not ssl_cert_path:
                local_cert_path = os.path.join(BASE_DIR, 'certs', 'server-ca.pem')
                if os.path.exists(local_cert_path):
                    ssl_cert_path = local_cert_path
                    print("[SSL] Certificado CA encontrado localmente")
            
            # 3. Se encontrou certificado, usar verificação
            if ssl_cert_path:
                try:
                    ssl_params = {
                        'sslmode': 'verify-ca',  # Verifica certificado do servidor
                        'sslrootcert': ssl_cert_path
                    }
                    print("[SSL] SSL configurado com verificação de certificado CA")
                except Exception as cert_error:
                    print(f"[AVISO] Erro ao configurar certificado CA: {cert_error}")
                    print("[AVISO] Continuando com sslmode=require (sem verificação)")
            else:
                print("[SSL] SSL configurado sem verificação de certificado (sslmode=require)")
            
            _db_pool = pool.ThreadedConnectionPool(
                minconn=2,  # Mínimo de 2 conexões sempre disponíveis
                maxconn=50,  # Máximo de 50 conexões simultâneas
                host=os.getenv('PG_HOST'),
                port=os.getenv('PG_PORT'),
                database=os.getenv('PG_DATABASE_HUBSPOT'),
                user=os.getenv('PG_USER'),
                password=os.getenv('PG_PASSWORD'),
                **ssl_params  # Adiciona parâmetros SSL
            )
            print("[OK] Pool de conexoes PostgreSQL inicializado com SSL (min: 2, max: 50)")
        except Exception as e:
            print(f"[ERRO] Erro ao inicializar pool de conexoes: {e}")
            _db_pool = None
    return _db_pool

# Inicializa o pool quando o módulo é carregado
init_db_pool()

def get_db_connection():
    """
    Obtém uma conexão do pool de conexões PostgreSQL.
    
    IMPORTANTE: A conexão deve ser devolvida ao pool usando putconn() após o uso.
    Para uso seguro, prefira usar get_db_connection_context() que gerencia automaticamente.
    
    Returns:
        psycopg2.connection ou None se não conseguir obter conexão
    """
    global _db_pool
    if _db_pool is None:
        _db_pool = init_db_pool()
    
    if _db_pool is None:
        return None
    
    try:
        conn = _db_pool.getconn()
        return conn
    except Exception as e:
        print(f"[ERRO] Erro ao obter conexao do pool: {e}")
        return None

def put_db_connection(conn):
    """
    Devolve uma conexão ao pool.
    
    Args:
        conn: Conexão obtida via get_db_connection()
    """
    global _db_pool
    if _db_pool and conn:
        try:
            _db_pool.putconn(conn)
        except Exception as e:
            print(f"[AVISO] Erro ao devolver conexao ao pool: {e}")

@contextmanager
def get_db_connection_context():
    """
    Context manager para obter e devolver automaticamente uma conexão do pool.
    
    Uso:
        with get_db_connection_context() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ...")
                result = cursor.fetchall()
    """
    conn = get_db_connection()
    try:
        yield conn
    finally:
        if conn:
            put_db_connection(conn)

def get_pool_status():
    """
    Retorna informações sobre o status do pool de conexões.
    Útil para debug e monitoramento.
    """
    global _db_pool
    if _db_pool is None:
        return {'status': 'not_initialized'}
    
    try:
        return {
            'status': 'active',
            'minconn': 2,
            'maxconn': 50,
            'note': 'Use get_db_connection_context() para garantir devolução automática'
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

