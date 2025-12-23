"""
API Routes para webhooks
"""
from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
import os
import json
from utils.mappings import get_analyst_name, normalize_product_name
from utils.whatsapp import send_whatsapp_notification
from utils.deals import insert_notification_db

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhook')

# Lista de logs de webhooks (em memória)
webhook_logs = []

# Lista de notificações em memória (fallback se banco falhar)
deal_notifications = []

@webhooks_bp.route('/deal-won', methods=['POST'])
def webhook_deal_won():
    """
    Recebe notificações do HubSpot quando um deal é ganho
    Endpoint para ser chamado pelo workflow do HubSpot
    """
    try:
        # Verifica autenticação (opcional mas recomendado)
        webhook_secret = os.getenv('HUBSPOT_WEBHOOK_SECRET')
        if webhook_secret:
            token = request.headers.get('X-HubSpot-Token')
            if token != webhook_secret:
                print(f"Token inválido recebido: {token}")
                return jsonify({'error': 'Token inválido'}), 401
        
        # Obtém dados do payload
        data = request.json
        if not data:
            data = request.form.to_dict()
            if not data:
                return jsonify({'error': 'Payload vazio'}), 400
        
        # Log para debug
        webhook_log = {
            'timestamp': datetime.now().isoformat(),
            'headers': dict(request.headers),
            'payload': data,
            'method': request.method,
            'content_type': request.content_type,
            'remote_addr': request.remote_addr
        }
        webhook_logs.append(webhook_log)
        if len(webhook_logs) > 50:
            webhook_logs.pop(0)
        
        # Extrai campos do payload
        deal_id = data.get('dealId') or data.get('deal_id') or data.get('hs_object_id')
        deal_name = data.get('dealName') or data.get('deal_name') or data.get('dealname', 'Deal sem nome')
        amount = data.get('amount') or data.get('valor_ganho') or data.get('valor_ganho', 0)
        
        # Converte IDs para nomes
        owner_id = data.get('ownerName') or data.get('owner_name') or data.get('analista_comercial', '')
        owner_name = get_analyst_name(owner_id)
        
        sdr_id = data.get('sdrName') or data.get('sdr_name') or data.get('pr_vendedor', '')
        sdr_name = get_analyst_name(sdr_id)
        
        ldr_id = data.get('ldrName') or data.get('ldr_name') or data.get('criado_por_', '')
        ldr_name = get_analyst_name(ldr_id)
        
        company_name = data.get('companyName') or data.get('company_name') or data.get('associated_company_name', '')
        product_name_raw = data.get('produto_principal') or data.get('productName') or ''
        product_name = normalize_product_name(product_name_raw) if product_name_raw else ''
        
        closed_date = data.get('closedDate') or data.get('closed_date') or data.get('closedate', '')
        pipeline = data.get('pipeline', '')
        deal_stage = data.get('dealStage') or data.get('deal_stage') or data.get('dealstage', '')
        
        # Valida campos obrigatórios
        if not deal_id:
            return jsonify({'error': 'dealId é obrigatório'}), 400
        
        try:
            amount = float(amount) if amount else 0.0
        except (ValueError, TypeError):
            amount = 0.0
        
        # Cria notificação
        notification = {
            'id': str(deal_id),
            'dealName': deal_name,
            'amount': amount,
            'ownerName': owner_name,
            'sdrName': sdr_name,
            'ldrName': ldr_name,
            'companyName': company_name,
            'productName': product_name,
            'closedDate': closed_date,
            'pipeline': pipeline,
            'dealStage': deal_stage,
            'timestamp': datetime.now().isoformat(),
            'viewed_by': []
        }
        
        # Tenta persistir no banco; se falhar, usa memória como fallback
        insert_result = insert_notification_db(notification)
        
        # Se já existe no banco, não processa novamente (evita duplicação)
        if insert_result == 'exists':
            print(f"⚠️ Deal {deal_id} já foi processado anteriormente. Ignorando duplicado.")
            return jsonify({
                'status': 'success',
                'message': 'Deal já processado anteriormente (duplicado ignorado)',
                'dealId': deal_id
            }), 200
        
        if not insert_result:
            # Adiciona à lista de notificações em memória se falhou inserir no banco
            deal_notifications.append(notification)
            # Limita a lista a 100 notificações (evita crescimento infinito)
            if len(deal_notifications) > 100:
                deal_notifications.pop(0)
        
        # Verifica se já existe na memória (evita duplicação mesmo sem banco)
        if insert_result != 'inserted':
            # Verifica se já está na lista de memória
            already_in_memory = any(n.get('id') == deal_id for n in deal_notifications)
            if already_in_memory:
                print(f"⚠️ Deal {deal_id} já está na lista de memória. Ignorando duplicado.")
                return jsonify({
                    'status': 'success',
                    'message': 'Deal já processado anteriormente (duplicado ignorado)',
                    'dealId': deal_id
                }), 200
        
        print(f"Notificação adicionada: Deal {deal_id} - {deal_name} - R$ {amount:,.2f}")
        
        # 📱 Envia notificação WhatsApp para o grupo RevOps (apenas se for uma nova notificação)
        send_whatsapp_notification(notification)
        
        return jsonify({
            'status': 'success',
            'message': 'Notificação recebida com sucesso',
            'dealId': deal_id
        }), 200
        
    except Exception as e:
        print(f"Erro ao processar webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Erro ao processar webhook: {str(e)}'
        }), 500

@webhooks_bp.route('/logs', methods=['GET'])
def get_webhook_logs():
    """Retorna logs de webhooks recebidos"""
    from utils.deals import fetch_pending_notifications_db
    
    # Busca notificações do banco de dados (últimas 100)
    db_notifications = fetch_pending_notifications_db(client_id=None, since_timestamp=None, limit=100)
    
    # Se banco não estiver disponível, usa fallback em memória
    if db_notifications is None:
        db_notifications = deal_notifications
    
    return jsonify({
        'logs': webhook_logs,
        'count': len(webhook_logs),
        'notifications': db_notifications,
        'notifications_count': len(db_notifications)
    }), 200

@webhooks_bp.route('/test', methods=['POST', 'GET'])
def test_webhook():
    """
    Endpoint de teste para simular webhook do HubSpot
    Aceita GET para formulário de teste ou POST com dados de teste
    """
    if request.method == 'GET':
        # Retorna formulário de teste simples
        return """
        <html>
        <head><title>Teste Webhook</title></head>
        <body>
            <h1>Teste de Webhook</h1>
            <form method="POST" action="/api/webhook/test">
                <p>
                    <label>dealId:</label><br>
                    <input type="text" name="dealId" value="123456789" required>
                </p>
                <p>
                    <label>dealName:</label><br>
                    <input type="text" name="dealName" value="Deal de Teste" required>
                </p>
                <p>
                    <label>amount:</label><br>
                    <input type="number" name="amount" value="50000" required>
                </p>
                <p>
                    <label>ownerName:</label><br>
                    <input type="text" name="ownerName" value="João Silva" required>
                </p>
                <p>
                    <label>sdrName:</label><br>
                    <input type="text" name="sdrName" value="Maria Santos">
                </p>
                <p>
                    <label>ldrName:</label><br>
                    <input type="text" name="ldrName" value="Carlos Oliveira">
                </p>
                <p>
                    <label>companyName:</label><br>
                    <input type="text" name="companyName" value="Empresa XYZ">
                </p>
                <p>
                    <button type="submit">Enviar Webhook de Teste</button>
                </p>
            </form>
            <hr>
            <p><a href="/webhook-debug">Ver Logs de Webhooks</a></p>
            <p><a href="/api/webhook/logs">API: Ver Logs (JSON)</a></p>
        </body>
        </html>
        """
    
    # Processa como se fosse um webhook real
    try:
        # Tenta obter JSON primeiro
        if request.is_json:
            data = request.json
        else:
            # Se for form-data, converte
            data = request.form.to_dict()
            # Converte amount para float se existir
            if 'amount' in data:
                try:
                    data['amount'] = float(data['amount'])
                except:
                    pass
        
        # Simula o processamento do webhook_deal_won
        print(f"=== WEBHOOK DE TESTE RECEBIDO ===")
        print(f"Payload: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print(f"Headers: {dict(request.headers)}")
        
        # Chama a função de webhook real
        return webhook_deal_won()
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro no teste: {str(e)}'
        }), 500

