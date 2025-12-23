"""
Sistema de cache centralizado
"""
import threading
from datetime import datetime

# Cache em memória para todos os dados do dashboard
# Atualizado a cada 10 minutos em background thread
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


