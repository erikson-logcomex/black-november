"""
Utilitário para salvar/carregar cookies do Looker em Cloud Storage
Permite que os cookies sejam compartilhados entre execuções locais e Cloud Run
"""

import os
import pickle
from pathlib import Path
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

# Configurações
COOKIES_DIR = Path('data/looker_cookies')
COOKIES_FILE_LOCAL = COOKIES_DIR / 'looker_session.pkl'
STORAGE_STATE_FILE_LOCAL = COOKIES_DIR / 'looker_storage_state.json'
GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'logcortex-assets')  # Bucket: logcortex-assets
GCS_COOKIES_PATH = 'looker_cookies/looker_session.pkl'
GCS_STORAGE_STATE_PATH = 'looker_cookies/looker_storage_state.json'

# Cria diretório local se não existir
COOKIES_DIR.mkdir(parents=True, exist_ok=True)

def save_cookies_to_gcs(cookies):
    """Salva cookies no Google Cloud Storage (substitui arquivo existente)"""
    if not GCS_BUCKET_NAME:
        print("⚠️ GCS_BUCKET_NAME não configurado, salvando apenas localmente")
        return save_cookies_local(cookies)
    
    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(GCS_COOKIES_PATH)
        
        # Verifica se já existe um arquivo antigo
        if blob.exists():
            print(f"🔄 Substituindo cookies antigos no Cloud Storage...")
            blob.delete()  # Remove o arquivo antigo explicitamente
        
        # Converte cookies para bytes
        cookies_bytes = pickle.dumps(cookies)
        
        # Faz upload do novo arquivo (substitui se existir)
        blob.upload_from_string(
            cookies_bytes, 
            content_type='application/octet-stream',
            if_generation_match=None  # Permite substituir qualquer versão
        )
        
        print(f"✅ Cookies salvos no Cloud Storage: gs://{GCS_BUCKET_NAME}/{GCS_COOKIES_PATH}")
        print(f"   Total de cookies: {len(cookies)}")
        return True
    except Exception as e:
        print(f"⚠️ Erro ao salvar cookies no Cloud Storage: {e}")
        print("   Salvando apenas localmente...")
        return save_cookies_local(cookies)

def load_cookies_from_gcs():
    """Carrega cookies do Google Cloud Storage"""
    if not GCS_BUCKET_NAME:
        print("⚠️ GCS_BUCKET_NAME não configurado, tentando carregar localmente")
        return load_cookies_local()
    
    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(GCS_COOKIES_PATH)
        
        if not blob.exists():
            print(f"⚠️ Cookies não encontrados no Cloud Storage (gs://{GCS_BUCKET_NAME}/{GCS_COOKIES_PATH})")
            print("   Tentando carregar localmente...")
            return load_cookies_local()
        
        cookies_bytes = blob.download_as_bytes()
        cookies = pickle.loads(cookies_bytes)
        
        print(f"✅ Cookies carregados do Cloud Storage (gs://{GCS_BUCKET_NAME}/{GCS_COOKIES_PATH})")
        # Também salva localmente como backup
        save_cookies_local(cookies)
        return cookies
    except Exception as e:
        print(f"⚠️ Erro ao carregar cookies do Cloud Storage: {e}")
        print("   (Isso é normal se você não tiver permissões ou estiver rodando localmente sem credenciais)")
        print("   Tentando carregar localmente...")
        return load_cookies_local()

def save_cookies_local(cookies):
    """Salva cookies localmente"""
    try:
        with open(COOKIES_FILE_LOCAL, 'wb') as f:
            pickle.dump(cookies, f)
        print(f"✅ Cookies salvos localmente em {COOKIES_FILE_LOCAL}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar cookies localmente: {e}")
        return False

def load_cookies_local():
    """Carrega cookies localmente"""
    try:
        if not COOKIES_FILE_LOCAL.exists():
            print(f"⚠️ Arquivo de cookies local não encontrado: {COOKIES_FILE_LOCAL}")
            return None
        
        with open(COOKIES_FILE_LOCAL, 'rb') as f:
            cookies = pickle.load(f)
        print(f"✅ Cookies carregados localmente de {COOKIES_FILE_LOCAL}")
        return cookies
    except Exception as e:
        print(f"❌ Erro ao carregar cookies localmente: {e}")
        return None

def save_cookies(cookies):
    """
    Salva cookies (localmente e no Cloud Storage)
    Sempre substitui os cookies antigos em ambos os locais
    """
    print(f"💾 Salvando {len(cookies)} cookies...")
    
    # Salva localmente sempre (substitui se existir)
    save_cookies_local(cookies)
    
    # Tenta salvar no Cloud Storage se configurado (substitui se existir)
    if GCS_BUCKET_NAME:
        save_cookies_to_gcs(cookies)
    
    return True

def save_storage_state_to_gcs(storage_state):
    """Salva storage state no Google Cloud Storage"""
    if not GCS_BUCKET_NAME:
        return save_storage_state_local(storage_state)
    
    try:
        import json
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(GCS_STORAGE_STATE_PATH)
        
        if blob.exists():
            print(f"🔄 Substituindo storage state antigo no Cloud Storage...")
            blob.delete()
        
        storage_state_json = json.dumps(storage_state)
        blob.upload_from_string(
            storage_state_json,
            content_type='application/json'
        )
        
        print(f"✅ Storage state salvo no Cloud Storage: gs://{GCS_BUCKET_NAME}/{GCS_STORAGE_STATE_PATH}")
        return True
    except Exception as e:
        print(f"⚠️ Erro ao salvar storage state no Cloud Storage: {e}")
        return save_storage_state_local(storage_state)

def load_storage_state_from_gcs():
    """Carrega storage state do Google Cloud Storage"""
    if not GCS_BUCKET_NAME:
        return load_storage_state_local()
    
    try:
        import json
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(GCS_STORAGE_STATE_PATH)
        
        if not blob.exists():
            return load_storage_state_local()
        
        storage_state_json = blob.download_as_text()
        storage_state = json.loads(storage_state_json)
        
        print(f"✅ Storage state carregado do Cloud Storage")
        save_storage_state_local(storage_state)  # Backup local
        return storage_state
    except Exception as e:
        print(f"⚠️ Erro ao carregar storage state do Cloud Storage: {e}")
        return load_storage_state_local()

def save_storage_state_local(storage_state):
    """Salva storage state localmente"""
    try:
        import json
        with open(STORAGE_STATE_FILE_LOCAL, 'w') as f:
            json.dump(storage_state, f)
        print(f"✅ Storage state salvo localmente em {STORAGE_STATE_FILE_LOCAL}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar storage state localmente: {e}")
        return False

def load_storage_state_local():
    """Carrega storage state localmente"""
    try:
        import json
        if not STORAGE_STATE_FILE_LOCAL.exists():
            return None
        
        with open(STORAGE_STATE_FILE_LOCAL, 'r') as f:
            storage_state = json.load(f)
        print(f"✅ Storage state carregado localmente")
        return storage_state
    except Exception as e:
        print(f"❌ Erro ao carregar storage state localmente: {e}")
        return None

def save_storage_state(storage_state):
    """Salva storage state (localmente e no Cloud Storage)"""
    save_storage_state_local(storage_state)
    if GCS_BUCKET_NAME:
        save_storage_state_to_gcs(storage_state)
    return True

def load_storage_state():
    """Carrega storage state (tenta local primeiro, depois Cloud Storage)"""
    storage_state = load_storage_state_local()
    if not storage_state and GCS_BUCKET_NAME:
        storage_state = load_storage_state_from_gcs()
    return storage_state

def load_cookies():
    """
    Carrega cookies (tenta local primeiro, depois Cloud Storage)
    Cookies locais têm prioridade pois são mais recentes
    """
    cookies = None
    
    # Tenta carregar local primeiro (mais recente)
    cookies = load_cookies_local()
    
    # Se não encontrou localmente, tenta Cloud Storage como fallback
    if not cookies and GCS_BUCKET_NAME:
        cookies = load_cookies_from_gcs()
    
    return cookies

