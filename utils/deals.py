"""
Funções auxiliares para gerenciamento de deals e notificações
"""
import json
from utils.db import get_db_connection_context
from utils.mappings import normalize_product_name
from psycopg2.extras import RealDictCursor

def insert_notification_db(notification):
    """
    Tenta inserir a notificação no banco.
    Retorna:
        - 'inserted': Se inseriu uma nova notificação
        - 'exists': Se a notificação já existia (duplicado)
        - False: Se houve erro/conexão
    """
    with get_db_connection_context() as conn:
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            # Primeiro verifica se já existe
            check_query = "SELECT id FROM deal_notifications WHERE id = %s"
            cursor.execute(check_query, (notification.get('id'),))
            exists = cursor.fetchone()
            
            if exists:
                print(f"⚠️ Deal {notification.get('id')} já existe no banco, ignorando duplicado")
                cursor.close()
                return 'exists'
            
            # Se não existe, insere
            query = """
            INSERT INTO deal_notifications (
                id, deal_name, amount, owner_name, sdr_name, ldr_name,
                company_name, pipeline, deal_stage, payload
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                notification.get('id'),
                notification.get('dealName'),
                notification.get('amount'),
                notification.get('ownerName'),
                notification.get('sdrName'),
                notification.get('ldrName'),
                notification.get('companyName'),
                notification.get('pipeline'),
                notification.get('dealStage'),
                json.dumps(notification)
            ))
            conn.commit()
            cursor.close()
            return 'inserted'
        except Exception as e:
            print(f"Erro ao inserir notificação no banco: {e}")
            return False

def fetch_pending_notifications_db(client_id=None, since_timestamp=None, limit=100):
    """
    Busca notificações pendentes no banco.
    
    Args:
        client_id: ID do cliente para filtrar notificações não vistas por ele
        since_timestamp: Timestamp ISO 8601 para filtrar apenas notificações criadas APÓS esse momento
        limit: Número máximo de notificações a retornar
    
    Returns:
        Lista de notificações no formato esperado pelo frontend ou None em caso de erro/conexão.
    """
    with get_db_connection_context() as conn:
        if not conn:
            return None

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Monta a query dinamicamente baseado nos filtros
            query_base = "SELECT id, payload, created_at FROM deal_notifications WHERE 1=1"
            params = []
            
            # Filtro por client_id (notificações não vistas por esse cliente)
            if client_id:
                query_base += " AND NOT (viewed_by @> ARRAY[%s]::text[])"
                params.append(client_id)
            
            # Filtro por timestamp (notificações criadas APÓS esse momento)
            if since_timestamp:
                query_base += " AND created_at > %s::timestamptz"
                params.append(since_timestamp)
            
            # Ordena por mais recentes primeiro e aplica limite
            query_base += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query_base, tuple(params))

            rows = cursor.fetchall()
            cursor.close()

            notifications = []
            for r in rows:
                payload = r.get('payload') or {}
                p = payload if isinstance(payload, dict) else json.loads(payload) if payload else {}
                
                # Normaliza produto usando DE-PARA
                product_raw = p.get('productName') or ''
                product_normalized = normalize_product_name(product_raw) if product_raw else ''
                
                notif = {
                    'id': str(r.get('id')),
                    'dealName': p.get('dealName') or p.get('deal_name') or '',
                    'amount': float(p.get('amount') or 0),
                    'ownerName': p.get('ownerName') or '',
                    'sdrName': p.get('sdrName') or '',
                    'ldrName': p.get('ldrName') or '',
                    'companyName': p.get('companyName') or '',
                    'productName': product_normalized,
                    'timestamp': r.get('created_at').isoformat() if r.get('created_at') else p.get('timestamp')
                }
                notifications.append(notif)

            return notifications
        except Exception as e:
            print(f"Erro ao buscar notificações no banco: {e}")
            return None

def mark_notification_viewed_db(deal_id, client_id):
    """Marca a notificação como vista para o client_id no banco. Retorna True se atualizou, False se não encontrou/erro."""
    if not client_id:
        return False

    with get_db_connection_context() as conn:
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            # Adiciona ao array apenas se ainda não existir
            query = """
            UPDATE deal_notifications
            SET viewed_by = array_append(viewed_by, %s)
            WHERE id = %s AND NOT (viewed_by @> ARRAY[%s]::text[])
            """
            cursor.execute(query, (client_id, deal_id, client_id))
            updated = cursor.rowcount
            conn.commit()
            cursor.close()
            return updated > 0
        except Exception as e:
            print(f"Erro ao marcar notificação como vista no banco: {e}")
            return False


