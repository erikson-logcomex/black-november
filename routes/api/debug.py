"""
API Routes para debug
"""
from flask import Blueprint, jsonify, render_template
from utils.auth import require_auth
from utils.db import get_pool_status
from routes.api.webhooks import webhook_logs, deal_notifications
from utils.deals import fetch_pending_notifications_db

debug_bp = Blueprint('debug', __name__, url_prefix='/api/debug')

@debug_bp.route('/pool-status', methods=['GET'])
@require_auth
def debug_pool_status():
    """Endpoint de debug para verificar status do pool de conexões"""
    status = get_pool_status()
    return jsonify(status)


