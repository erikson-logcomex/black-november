"""
API Routes para relatórios
"""
from flask import Blueprint, jsonify, request
from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/api')

@reports_bp.route('/send-daily-mvp-report', methods=['POST'])
def api_send_daily_mvp_report():
    """
    Endpoint para enviar relatório diário dos MVPs
    Pode ser chamado manualmente ou via Cloud Scheduler
    
    Query params:
        - env: 'prod' (padrão) ou 'test'
    
    Nota: Não requer autenticação pois é chamado pelo Cloud Scheduler
    """
    try:
        from send_daily_mvp_report import send_daily_mvp_report
        
        env = request.args.get('env', 'prod')
        use_test_group = env == 'test'
        
        print(f"[REPORT] Enviando relatorio de MVPs - Ambiente: {'TESTE' if use_test_group else 'PRODUCAO'}")
        print(f"[DEBUG] Headers recebidos: {dict(request.headers)}")
        print(f"[DEBUG] Remote addr: {request.remote_addr}")
        
        success = send_daily_mvp_report(use_test_group=use_test_group)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Relatório de MVPs enviado com sucesso para {env.upper()}',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Erro ao enviar relatório de MVPs',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        print(f"[ERRO] Erro ao enviar relatorio de MVPs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

