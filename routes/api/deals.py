"""
API Routes para deals e notificações
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from routes.api.webhooks import deal_notifications
from utils.deals import fetch_pending_notifications_db, mark_notification_viewed_db

deals_bp = Blueprint('deals', __name__, url_prefix='/api/deals')

@deals_bp.route('/pending', methods=['GET'])
def get_pending_deals():
    """
    Retorna notificações pendentes para exibição no frontend
    Usado pelo JavaScript para verificar novos deals ganhos
    
    Query parameters:
        - client_id: ID do painel/cliente (obrigatório)
        - since: Timestamp ISO 8601 para filtrar apenas deals criados após esse momento
    """
    try:
        client_id = request.args.get('client_id')
        since_timestamp = request.args.get('since')
        
        # Tenta buscar no banco primeiro
        db_notifications = fetch_pending_notifications_db(client_id, since_timestamp)
        if db_notifications is not None:
            pending = db_notifications
        else:
            # Fallback em memória
            if client_id:
                pending = [n for n in deal_notifications if client_id not in n.get('viewed_by', [])]
            else:
                pending = [n for n in deal_notifications if not n.get('viewed', False) and not n.get('viewed_by')]
            
            # Aplica filtro de timestamp
            if since_timestamp and pending:
                since_dt = datetime.fromisoformat(since_timestamp.replace('Z', '+00:00'))
                pending = [
                    n for n in pending 
                    if n.get('timestamp') and datetime.fromisoformat(n['timestamp'].replace('Z', '+00:00')) > since_dt
                ]
        
        # Ordena por timestamp (mais recentes primeiro)
        pending.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        print(f"GET /api/deals/pending: {len(pending)} notificação(ões) pendente(s)")
        
        return jsonify({
            'notifications': pending,
            'count': len(pending)
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar notificações pendentes: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro ao buscar notificações: {str(e)}'
        }), 500

@deals_bp.route('/mark-viewed/<deal_id>', methods=['POST'])
def mark_deal_viewed(deal_id):
    """
    Marca uma notificação como visualizada
    Chamado após a animação ser exibida
    """
    try:
        client_id = request.args.get('client_id')
        if not client_id:
            try:
                body = request.get_json(silent=True) or {}
                client_id = body.get('client_id')
            except Exception:
                client_id = None
        
        # Tenta marcar no banco
        if client_id:
            updated = mark_notification_viewed_db(str(deal_id), client_id)
            # Atualiza também memória
            for notification in deal_notifications:
                if notification['id'] == str(deal_id):
                    viewed_by = notification.setdefault('viewed_by', [])
                    if client_id not in viewed_by:
                        viewed_by.append(client_id)
                    break
            if updated:
                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'status': 'success', 'message': 'Atualizado em memória'}), 200
        else:
            # Comportamento legacy
            for notification in deal_notifications:
                if notification['id'] == str(deal_id):
                    notification['viewed'] = True
                    return jsonify({'status': 'success'}), 200
            
            return jsonify({'status': 'not_found', 'message': 'Notificação não encontrada'}), 404
        
    except Exception as e:
        print(f"Erro ao marcar notificação como visualizada: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro ao marcar notificação: {str(e)}'
        }), 500

