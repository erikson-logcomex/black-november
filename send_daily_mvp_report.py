"""
Script para enviar relatório diário dos MVPs do Hall da Fama para WhatsApp
Deve ser executado diariamente às 20h (GMT-3) via Cloud Scheduler
"""
import os
import sys
import requests
import base64
from datetime import datetime, timezone, timedelta
from mvp_image_generator import generate_all_mvps_images
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Grupo de teste
TEST_GROUP_ID = '120363405303439862@g.us'

# Grupo de produção (descomente quando validar)
PROD_GROUP_ID = '554191877530-1510578382@g.us'


def get_hall_fama_data():
    """
    Busca dados do Hall da Fama via APIs locais
    
    Returns:
        tuple: (evs_data, sdrs_new_data, sdrs_expansao_data, ldrs_data)
    """
    # URL base da API
    # No Cloud Run, usa a porta do próprio container (PORT env var, padrão 8080)
    # Localmente, usa porta 5000
    port = os.getenv('PORT', '5000')
    base_url = os.getenv('API_BASE_URL', f'http://127.0.0.1:{port}')
    
    try:
        print(f"📡 Buscando dados do Hall da Fama em {base_url}...")
        
        # Busca dados de cada perfil (timeout aumentado para 120s pois HubSpot pode demorar)
        evs_response = requests.get(f'{base_url}/api/hall-da-fama/evs-realtime', timeout=120)
        sdrs_new_response = requests.get(f'{base_url}/api/hall-da-fama/sdrs-realtime?pipeline=6810518', timeout=120)
        sdrs_expansao_response = requests.get(f'{base_url}/api/hall-da-fama/sdrs-realtime?pipeline=4007305', timeout=120)
        ldrs_response = requests.get(f'{base_url}/api/hall-da-fama/ldrs-realtime', timeout=120)
        
        # Verifica se todas as requisições foram bem-sucedidas
        evs_response.raise_for_status()
        sdrs_new_response.raise_for_status()
        sdrs_expansao_response.raise_for_status()
        ldrs_response.raise_for_status()
        
        evs_data = evs_response.json()
        sdrs_new_data = sdrs_new_response.json()
        sdrs_expansao_data = sdrs_expansao_response.json()
        ldrs_data = ldrs_response.json()
        
        print("✅ Dados do Hall da Fama obtidos com sucesso")
        
        return evs_data, sdrs_new_data, sdrs_expansao_data, ldrs_data
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados do Hall da Fama: {e}")
        raise


def send_whatsapp_image(group_id, image_bytes, caption, image_name):
    """
    Envia imagem para grupo WhatsApp via Evolution API
    
    Args:
        group_id: ID do grupo WhatsApp
        image_bytes: Imagem em bytes
        caption: Legenda da imagem
        image_name: Nome do arquivo
    
    Returns:
        bool: True se enviou com sucesso
    """
    try:
        # Configurações da Evolution API
        evolution_api_url = os.getenv('EVOLUTION_API_URL', 'https://evolution-api-logcomex.34-49-195-55.nip.io')
        evolution_api_key = os.getenv('EVOLUTION_API_KEY')
        instance_name = os.getenv('EVOLUTION_INSTANCE_NAME', 'RevOps_AI')
        
        if not evolution_api_key:
            print("❌ EVOLUTION_API_KEY não configurada")
            return False
        
        # Converte imagem para base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Monta payload
        headers = {
            "apikey": evolution_api_key,
            "Content-Type": "application/json"
        }
        
        url_media = f"{evolution_api_url}/message/sendMedia/{instance_name}"
        payload_media = {
            "number": group_id,
            "mediatype": "image",
            "media": image_base64,
            "caption": caption,
            "fileName": image_name
        }
        
        print(f"📤 Enviando imagem '{image_name}' para grupo {group_id}...")
        response = requests.post(url_media, headers=headers, json=payload_media, timeout=30)
        
        if response.status_code in [200, 201]:
            print(f"✅ Imagem '{image_name}' enviada com sucesso!")
            return True
        else:
            print(f"❌ Erro ao enviar imagem. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar imagem WhatsApp: {e}")
        return False


def get_badge_description(badge_name, profile_type='EVs'):
    """
    Retorna descrição de um emblema com emoji (baseado no Hall da Fama)
    
    Args:
        badge_name: Código do emblema
        profile_type: Tipo de perfil (EVs, SDRs-New, SDRs-Expansao, LDRs)
    
    Returns:
        str: Descrição formatada
    """
    # Badges específicos para SDRs (medidos por AGENDAMENTOS)
    if 'SDR' in profile_type:
        badges_info = {
            'precision_sniper': '🎯 *Precision Sniper* - 3+ agendamentos',
            'master_scheduler': '📅 *Master Scheduler* - 5+ agendamentos',
            'full_pressure': '💪 *Full Pressure* - 7+ agendamentos',
            'overload_closer': '👑 *Overload Closer* - 10+ agendamentos',
            'madrugador': '🌅 *Madrugador* - Agendamentos antes das 08h',
            'coruja': '🦉 *Coruja* - Agendamentos depois das 21h',
            'relampago': '⚡ *Relâmpago* - < 1h entre agendamentos',
            'velocista': '🏃🏻‍➡️ *Velocista* - < 3h entre agendamentos',
        }
    # Badges para EVs e LDRs (medidos por DEALS GANHOS + FATURAMENTO)
    else:
        badges_info = {
            'precision_sniper': '🎯 *Precision Sniper* - 3+ deals',
            'full_pressure': '💪 *Full Pressure* - 7+ deals',
            'overload_closer': '👑 *Overload Closer* - 10+ deals',
            'madrugador': '🌅 *Madrugador* - Deals antes das 08h',
            'coruja': '🦉 *Coruja* - Deals depois das 21h',
            'relampago': '⚡ *Relâmpago* - < 1h entre deals',
            'velocista': '🏃🏻‍➡️ *Velocista* - < 3h entre deals',
            # Badges de faturamento (apenas EVs/LDRs)
            'bronze_closer': '🥉 *Bronze Closer* - R$ 2.5k+ no dia',
            'bronze_closer_2.5k+': '🥉 *Bronze Closer* - R$ 2.5k+ no dia',
            'silver_closer': '🥈 *Silver Closer* - R$ 5k+ no dia',
            'silver_closer_5k+': '🥈 *Silver Closer* - R$ 5k+ no dia',
            'gold_closer': '🥇 *Gold Closer* - R$ 10k+ no dia',
            'gold_closer_10k+': '🥇 *Gold Closer* - R$ 10k+ no dia',
        }
    
    # Se não encontrar descrição específica, retorna nome formatado
    return badges_info.get(badge_name.lower(), f'🏅 *{badge_name.replace("_", " ").title()}*')


def build_mvp_caption(profile_type, mvp_data):
    """
    Constrói caption detalhado para o destaque do dia
    
    Args:
        profile_type: Tipo de perfil (EVs, SDRs-New, etc)
        mvp_data: Dados do destaque (pode ser dict completo da API com 'data' array ou objeto direto)
    
    Returns:
        str: Caption formatado
    """
    # Se mvp_data for a resposta completa da API, pega o primeiro do ranking
    if isinstance(mvp_data, dict) and 'data' in mvp_data:
        ranking_data = mvp_data.get('data', [])
        if not ranking_data:
            return f"🏆 *{profile_type}* - Destaque do Dia 🎉"
        mvp = ranking_data[0]  # Pega o TOP 1 (position 1)
    else:
        mvp = mvp_data
    
    if not mvp:
        return f"🏆 *{profile_type}* - Destaque do Dia 🎉"
    
    name = mvp.get('userName', 'Destaque')
    
    # Monta caption baseado no tipo de perfil
    if profile_type == 'EVs':
        deals = mvp.get('dealCount', 0)
        revenue = mvp.get('revenue', 0)
        
        caption = f"""🏆 *DESTAQUE DO DIA - EV*

👤 *{name}*

💼 *Deals Fechados:* {deals}
💰 *Revenue Total:* R$ {revenue:,.2f}"""
        
    elif 'SDR' in profile_type:
        pipeline_name = 'New' if 'New' in profile_type else 'Expansão'
        agendamentos = mvp.get('scheduledCount', 0)
        
        caption = f"""🏆 *DESTAQUE DO DIA - SDR {pipeline_name.upper()}*

👤 *{name}*

📅 *Agendamentos:* {agendamentos}
🎯 *Pipeline:* {pipeline_name}"""
        
    elif profile_type == 'LDRs':
        deals = mvp.get('wonDealsCount', 0)
        revenue = mvp.get('revenue', 0)
        
        caption = f"""🏆 *DESTAQUE DO DIA - LDR*

👤 *{name}*

🫱🏻‍🫲🏻 *Deals Ganhos (MQL → Ganho):* {deals}
💰 *Revenue Total:* R$ {revenue:,.2f}"""
    
    else:
        caption = f"🏆 *{profile_type}* - {name}"
    
    # Adiciona emblemas conquistados
    badges = mvp.get('badges', [])
    if badges and len(badges) > 0:
        caption += "\n\n🏅 *EMBLEMAS CONQUISTADOS:*\n"
        for badge in badges:  # Mostra TODOS os emblemas conquistados
            if isinstance(badge, dict):
                badge_code = badge.get('code', '')
                badge_name = badge.get('name', '')
            else:
                badge_code = str(badge)
                badge_name = str(badge)
            
            if badge_code or badge_name:
                badge_key = badge_code if badge_code else badge_name
                caption += f"  • {get_badge_description(badge_key, profile_type)}\n"
    
    caption += "\n✨ *Parabéns pela dedicação!* 🎉"
    
    return caption


def send_daily_mvp_report(use_test_group=True):
    """
    Envia relatório diário dos destaques do dia para WhatsApp
    
    Args:
        use_test_group: Se True, envia para grupo de teste, senão para produção
    
    Returns:
        bool: True se tudo foi enviado com sucesso
    """
    try:
        print("=" * 60)
        print("🏆 INICIANDO ENVIO DO RELATÓRIO DIÁRIO - DESTAQUES DO DIA")
        print("=" * 60)
        
        # Define grupo de destino
        group_id = TEST_GROUP_ID if use_test_group else PROD_GROUP_ID
        env_name = "TESTE" if use_test_group else "PRODUÇÃO"
        
        print(f"📍 Ambiente: {env_name}")
        print(f"📱 Grupo: {group_id}")
        
        # Busca dados do Hall da Fama
        evs_data, sdrs_new_data, sdrs_expansao_data, ldrs_data = get_hall_fama_data()
        
        # Gera imagens dos destaques
        print("\n🎨 Gerando imagens dos destaques do dia...")
        images = generate_all_mvps_images(evs_data, sdrs_new_data, sdrs_expansao_data, ldrs_data)
        
        if not images:
            print("⚠️ Nenhuma imagem foi gerada. Não há destaques hoje.")
            return False
        
        # Data atual (GMT-3 - Brasília)
        brasilia_tz = timezone(timedelta(hours=-3))
        now_brasilia = datetime.now(brasilia_tz)
        data_formatada = now_brasilia.strftime('%d/%m/%Y')
        
        # Mensagem introdutória
        intro_message = f"""🏆 *HALL DA FAMA - DESTAQUES DO DIA*

📅 *Data:* {data_formatada}

Confira os destaques de hoje e suas conquistas! 🎉👇"""
        
        # Envia mensagem introdutória
        send_whatsapp_text(group_id, intro_message)
        
        # Aguarda 2 segundos
        import time
        time.sleep(2)
        
        # Mapeia dados para cada tipo de perfil
        mvp_data_map = {
            'EVs': evs_data,
            'SDRs-New': sdrs_new_data,
            'SDRs-Expansao': sdrs_expansao_data,
            'LDRs': ldrs_data
        }
        
        # Envia cada imagem com caption detalhado
        success_count = 0
        total_count = len(images)
        
        for profile_type, image_bytes in images.items():
            # Pega dados do MVP correspondente
            mvp_data = mvp_data_map.get(profile_type)
            
            # Constrói caption detalhado
            caption = build_mvp_caption(profile_type, mvp_data)
            image_name = f"mvp_{profile_type.lower().replace(' ', '_')}_{now_brasilia.strftime('%Y%m%d')}.png"
            
            if send_whatsapp_image(group_id, image_bytes, caption, image_name):
                success_count += 1
            
            # Aguarda 3 segundos entre envios
            if success_count < total_count:
                time.sleep(3)
        
        # Mensagem de encerramento
        if success_count == total_count:
            footer_message = f"""---
✨ *Parabéns aos {total_count} destaques de hoje!* 🎊

Continue assim, time! Cada conquista nos aproxima dos nossos objetivos! 💪🚀
"""
            send_whatsapp_text(group_id, footer_message)
            
            print("\n" + "=" * 60)
            print(f"✅ RELATÓRIO ENVIADO COM SUCESSO ({success_count}/{total_count})")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print(f"⚠️ RELATÓRIO PARCIALMENTE ENVIADO ({success_count}/{total_count})")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO AO ENVIAR RELATÓRIO: {e}")
        import traceback
        traceback.print_exc()
        return False


def send_whatsapp_text(group_id, message):
    """
    Envia mensagem de texto para grupo WhatsApp
    
    Args:
        group_id: ID do grupo
        message: Mensagem de texto
    
    Returns:
        bool: True se enviou com sucesso
    """
    try:
        evolution_api_url = os.getenv('EVOLUTION_API_URL', 'https://evolution-api-logcomex.34-49-195-55.nip.io')
        evolution_api_key = os.getenv('EVOLUTION_API_KEY')
        instance_name = os.getenv('EVOLUTION_INSTANCE_NAME', 'RevOps_AI')
        
        if not evolution_api_key:
            return False
        
        headers = {
            "apikey": evolution_api_key,
            "Content-Type": "application/json"
        }
        
        url_text = f"{evolution_api_url}/message/sendText/{instance_name}"
        payload_text = {
            "number": group_id,
            "text": message
        }
        
        response = requests.post(url_text, headers=headers, json=payload_text, timeout=10)
        return response.status_code in [200, 201]
        
    except Exception as e:
        print(f"Erro ao enviar texto WhatsApp: {e}")
        return False


if __name__ == '__main__':
    # Verifica argumentos de linha de comando
    # PRODUÇÃO por padrão, use --test para enviar para grupo de teste
    use_test = '--test' in sys.argv
    
    if use_test:
        print("⚠️ MODO TESTE - Enviando para grupo de teste")
    else:
        print("🚀 MODO PRODUÇÃO - Enviando para grupo de produção")
        print(f"   Para testar, use: python send_daily_mvp_report.py --test")
    
    # Envia relatório
    success = send_daily_mvp_report(use_test_group=use_test)
    
    # Exit code
    sys.exit(0 if success else 1)
