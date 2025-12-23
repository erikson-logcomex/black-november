"""
Utilitários para manipulação de datas e timezones
"""
from datetime import datetime, timezone, timedelta

BRAZIL_TZ_OFFSET = timedelta(hours=-3)

def get_today_brazil_start_utc():
    """Retorna o início do dia no Brasil (00:00 GMT-3) convertido para UTC"""
    now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
    today_brazil_start = now_brazil.replace(hour=0, minute=0, second=0, microsecond=0)
    today_brazil_start_utc = today_brazil_start - BRAZIL_TZ_OFFSET
    return today_brazil_start_utc

def convert_utc_to_brazil(dt_utc):
    """Converte datetime UTC para horário do Brasil (GMT-3)"""
    return dt_utc + BRAZIL_TZ_OFFSET

def parse_hubspot_timestamp(timestamp):
    """Parse timestamp ISO 8601 ou milliseconds do HubSpot"""
    try:
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except:
        return datetime.fromtimestamp(int(timestamp) / 1000, tz=timezone.utc)

def get_week_start_brazil_utc():
    """Retorna o início da semana (domingo 00:00 GMT-3) convertido para UTC"""
    now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
    days_since_sunday = (now_brazil.weekday() + 1) % 7
    
    if days_since_sunday == 0:
        week_start_brazil = now_brazil.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        week_start_brazil = now_brazil - timedelta(days=days_since_sunday)
        week_start_brazil = week_start_brazil.replace(hour=0, minute=0, second=0, microsecond=0)
    
    week_start_utc = week_start_brazil - BRAZIL_TZ_OFFSET
    return week_start_utc

def get_month_start_brazil_utc():
    """Retorna o início do mês atual no Brasil (00:00 GMT-3) convertido para UTC"""
    now_brazil = datetime.now(timezone.utc) + BRAZIL_TZ_OFFSET
    month_start_brazil = now_brazil.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_start_utc = month_start_brazil - BRAZIL_TZ_OFFSET
    return month_start_utc


