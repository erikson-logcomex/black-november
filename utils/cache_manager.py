"""
Gerenciador de cache centralizado
"""
import threading
import time
from datetime import datetime

# Cache em memória para todos os dados do dashboard
_data_cache = {
    'revenue': None,
    'revenue_today': None,
    'pipeline_today': None,
    'hall_evs': None,
    'hall_sdrs_new': None,
    'hall_sdrs_expansao': None,
    'hall_ldrs': None,
    'destaques_evs_semana_new': None,
    'destaques_evs_semana_expansao': None,
    'destaques_evs_mes_new': None,
    'destaques_evs_mes_expansao': None,
    'destaques_sdrs_semana_new': None,
    'destaques_sdrs_semana_expansao': None,
    'destaques_sdrs_mes_new': None,
    'destaques_sdrs_mes_expansao': None,
    'destaques_ldrs_semana_new': None,
    'destaques_ldrs_semana_expansao': None,
    'destaques_ldrs_mes_new': None,
    'destaques_ldrs_mes_expansao': None,
    'top_evs_today': None,
    'top_sdrs_today_new': None,
    'top_sdrs_today_expansao': None,
    'top_ldrs_today': None,
    'last_update': None,
    'is_updating': False
}

_cache_lock = threading.Lock()
CACHE_UPDATE_INTERVAL = 600  # 10 minutos em segundos

def get_cache():
    """Retorna o dicionário de cache"""
    return _data_cache

def get_cache_lock():
    """Retorna o lock do cache"""
    return _cache_lock

def get_cache_interval():
    """Retorna o intervalo de atualização do cache"""
    return CACHE_UPDATE_INTERVAL

def refresh_data_cache(app):
    """Atualiza todos os dados do cache fazendo requisições HTTP internas"""
    global _data_cache
    
    with _cache_lock:
        if _data_cache['is_updating']:
            print("[CACHE] Cache ja esta sendo atualizado, pulando...")
            return
        
        _data_cache['is_updating'] = True
    
    try:
        print("[CACHE] Iniciando atualizacao do cache centralizado...")
        start_time = time.time()
        
        with app.test_client() as client:
            # Endpoints principais
            try:
                resp = client.get('/api/revenue')
                if resp.status_code == 200:
                    _data_cache['revenue'] = resp.get_json()
            except Exception as e:
                print(f"[AVISO] Erro ao buscar revenue: {e}")
            
            try:
                resp = client.get('/api/revenue/today')
                if resp.status_code == 200:
                    _data_cache['revenue_today'] = resp.get_json()
            except Exception as e:
                print(f"⚠️ Erro ao buscar revenue_today: {e}")
            
            try:
                resp = client.get('/api/pipeline/today')
                if resp.status_code == 200:
                    _data_cache['pipeline_today'] = resp.get_json()
            except Exception as e:
                print(f"⚠️ Erro ao buscar pipeline_today: {e}")
            
            # Hall da Fama
            try:
                resp = client.get('/api/hall-da-fama/evs-realtime')
                if resp.status_code == 200:
                    _data_cache['hall_evs'] = resp.get_json()
            except Exception as e:
                print(f"⚠️ Erro ao buscar hall_evs: {e}")
            
            try:
                resp = client.get('/api/hall-da-fama/sdrs-realtime?pipeline=6810518')
                if resp.status_code == 200:
                    _data_cache['hall_sdrs_new'] = resp.get_json()
            except Exception as e:
                print(f"⚠️ Erro ao buscar hall_sdrs_new: {e}")
            
            try:
                resp = client.get('/api/hall-da-fama/sdrs-realtime?pipeline=4007305')
                if resp.status_code == 200:
                    _data_cache['hall_sdrs_expansao'] = resp.get_json()
            except Exception as e:
                print(f"⚠️ Erro ao buscar hall_sdrs_expansao: {e}")
            
            try:
                resp = client.get('/api/hall-da-fama/ldrs-realtime')
                if resp.status_code == 200:
                    _data_cache['hall_ldrs'] = resp.get_json()
            except Exception as e:
                print(f"⚠️ Erro ao buscar hall_ldrs: {e}")
            
            # Top rankings
            try:
                resp = client.get('/api/top-evs-today')
                if resp.status_code == 200:
                    _data_cache['top_evs_today'] = resp.get_json()
            except Exception as e:
                print(f"⚠️ Erro ao buscar top_evs_today: {e}")
            
            try:
                resp = client.get('/api/top-sdrs-today?pipeline=6810518')
                if resp.status_code == 200:
                    _data_cache['top_sdrs_today_new'] = resp.get_json()
            except Exception as e:
                print(f"⚠️ Erro ao buscar top_sdrs_today_new: {e}")
            
            try:
                resp = client.get('/api/top-sdrs-today?pipeline=4007305')
                if resp.status_code == 200:
                    _data_cache['top_sdrs_today_expansao'] = resp.get_json()
            except Exception as e:
                print(f"⚠️ Erro ao buscar top_sdrs_today_expansao: {e}")
            
            try:
                resp = client.get('/api/top-ldrs-today')
                if resp.status_code == 200:
                    _data_cache['top_ldrs_today'] = resp.get_json()
            except Exception as e:
                print(f"⚠️ Erro ao buscar top_ldrs_today: {e}")
        
        _data_cache['last_update'] = datetime.now().isoformat()
        elapsed = time.time() - start_time
        print(f"[OK] Cache atualizado com sucesso em {elapsed:.2f}s")
        
    except Exception as e:
        print(f"[ERRO] Erro ao atualizar cache: {e}")
        import traceback
        traceback.print_exc()
    finally:
        with _cache_lock:
            _data_cache['is_updating'] = False

def start_cache_refresh_thread(app):
    """Inicia thread em background para atualizar cache periodicamente"""
    def refresh_loop():
        time.sleep(5)
        refresh_data_cache(app)
        
        while True:
            time.sleep(CACHE_UPDATE_INTERVAL)
            refresh_data_cache(app)
    
    thread = threading.Thread(target=refresh_loop, daemon=True)
    thread.start()
    print(f"[OK] Thread de atualizacao de cache iniciada (intervalo: {CACHE_UPDATE_INTERVAL}s)")

