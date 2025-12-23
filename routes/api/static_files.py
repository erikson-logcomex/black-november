"""
Rotas para arquivos estáticos
"""
from flask import Blueprint, send_from_directory, request, Response, jsonify
import os

static_bp = Blueprint('static_files', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@static_bp.route('/static/img/<path:filename>')
def serve_static_image(filename):
    """Serve imagens estáticas (favicon, etc)"""
    if filename.startswith('team/'):
        return send_from_directory('static/img', filename)
    return send_from_directory('static/img', filename)

@static_bp.route('/static/img/team/<path:filename>')
def serve_team_image(filename):
    """Serve imagens do time comercial"""
    return send_from_directory('static/img/team', filename)

@static_bp.route('/static/media/<path:filename>')
def serve_media(filename):
    """Serve vídeos e áudios com suporte a Range Requests para streaming"""
    try:
        media_path = os.path.join('static', 'media', filename)
        
        # Verifica se o arquivo existe
        if not os.path.exists(media_path):
            print(f"Arquivo não encontrado: {media_path} (cwd: {os.getcwd()})")
            return jsonify({'error': 'Arquivo não encontrado', 'path': media_path}), 404
        
        # Detecta o tipo MIME baseado na extensão
        if filename.lower().endswith('.mp4'):
            mimetype = 'video/mp4'
        elif filename.lower().endswith(('.mp3', '.mpeg')):
            mimetype = 'audio/mpeg'
        else:
            mimetype = 'application/octet-stream'
        
        # Tenta usar send_from_directory primeiro (mais simples)
        range_header = request.headers.get('Range', None)
        
        if not range_header:
            # Sem range header, retorna arquivo completo
            return send_from_directory('static/media', filename, mimetype=mimetype)
        
        # Com range header, precisa processar
        try:
            size = os.path.getsize(media_path)
        except OSError as e:
            print(f"Erro ao obter tamanho do arquivo {media_path}: {e}")
            # Fallback: retorna arquivo completo sem range
            return send_from_directory('static/media', filename, mimetype=mimetype)
        
        # Parse range header
        try:
            range_match = range_header.replace('bytes=', '').split('-')
            byte1 = int(range_match[0]) if range_match[0] else 0
            byte2 = int(range_match[1]) if range_match[1] and range_match[1] else size - 1
        except (ValueError, IndexError) as e:
            print(f"Erro ao parsear range header: {e}")
            # Fallback: retorna arquivo completo
            return send_from_directory('static/media', filename, mimetype=mimetype)
        
        # Garante que os bytes estão dentro dos limites
        byte1 = max(0, byte1)
        byte2 = min(size - 1, byte2)
        
        if byte1 > byte2 or byte1 >= size:
            # Range inválido, retorna 416
            rv = Response('', 416, mimetype=mimetype)
            rv.headers.add('Content-Range', f'bytes */{size}')
            return rv
        
        length = byte2 - byte1 + 1
        
        # Lê apenas o range necessário (chunked para evitar carregar tudo na memória)
        try:
            def generate():
                with open(media_path, 'rb') as f:
                    f.seek(byte1)
                    remaining = length
                    chunk_size = 8192  # 8KB chunks
                    while remaining > 0:
                        read_size = min(chunk_size, remaining)
                        chunk = f.read(read_size)
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk
            
            rv = Response(generate(), 206, mimetype=mimetype)
            rv.headers.add('Content-Range', f'bytes {byte1}-{byte2}/{size}')
            rv.headers.add('Accept-Ranges', 'bytes')
            rv.headers.add('Content-Length', str(length))
            rv.headers.add('Cache-Control', 'public, max-age=3600')
            
            return rv
            
        except IOError as e:
            print(f"Erro ao ler arquivo {media_path}: {e}")
            # Fallback: retorna arquivo completo
            return send_from_directory('static/media', filename, mimetype=mimetype)
        
    except Exception as e:
        print(f"Erro geral ao servir mídia {filename}: {e}")
        import traceback
        traceback.print_exc()
        # Último fallback: tenta servir sem range
        try:
            mimetype = 'audio/mpeg' if filename.lower().endswith(('.mp3', '.mpeg')) else 'video/mp4' if filename.lower().endswith('.mp4') else 'application/octet-stream'
            return send_from_directory('static/media', filename, mimetype=mimetype)
        except:
            return jsonify({'error': f'Erro ao servir arquivo: {str(e)}'}), 500

@static_bp.route('/teste-allan-chromakey')
def teste_allan_chromakey():
    """Rota para página de teste do chromakey do vídeo do Allan"""
    from utils.auth import require_auth
    from flask import send_from_directory
    return send_from_directory(BASE_DIR, 'teste_allan_chromakey.html')


