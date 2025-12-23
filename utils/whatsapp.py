"""
Utilitários para envio de notificações WhatsApp
"""
import os
import requests
from datetime import datetime, timezone, timedelta
from celebration_image_generator import generate_celebration_image

def send_whatsapp_notification(deal_data):
    """
    Envia notificação de deal ganho para o grupo WhatsApp via Evolution API
    Inclui uma imagem de celebração gerada automaticamente
    
    Args:
        deal_data: Dicionário com os dados do deal (dealName, amount, ownerName, etc.)
    
    Returns:
        True se enviou com sucesso, False caso contrário
    """
    try:
        # Configurações da Evolution API (vindas das variáveis de ambiente)
        evolution_api_url = os.getenv('EVOLUTION_API_URL', 'https://evolution-api-logcomex.34-49-195-55.nip.io')
        evolution_api_key = os.getenv('EVOLUTION_API_KEY')
        instance_name = os.getenv('EVOLUTION_INSTANCE_NAME', 'RevOps')
        group_id = os.getenv('ID_GRUPO_REVOPS')
        
        # Valida variáveis de ambiente
        if not evolution_api_key:
            print("[ERRO] EVOLUTION_API_KEY nao configurada")
            return False
        
        if not group_id:
            print("[ERRO] ID_GRUPO_REVOPS nao configurado")
            return False
        
        # Formata a mensagem
        mensagem = "🎉 *CONTRATO ASSINADO!*\n\n"
        mensagem += f"💰 *Valor:* R$ {deal_data.get('amount', 0):,.2f}\n"
        mensagem += f"📝 *Deal:* {deal_data.get('dealName', 'N/A')}\n\n"
        mensagem += "👥 *Time Vencedor:*\n"
        
        # Adiciona informações do time
        if deal_data.get('ownerName'):
            mensagem += f"👔 *EV:* {deal_data.get('ownerName')}\n"
        if deal_data.get('sdrName'):
            mensagem += f"📞 *SDR:* {deal_data.get('sdrName')}\n"
        if deal_data.get('ldrName'):
            mensagem += f"🎯 *LDR:* {deal_data.get('ldrName')}\n"
        
        # Adiciona produto principal (prioridade) ou empresa (fallback)
        if deal_data.get('productName'):
            mensagem += f"\n📦 *Produto:* {deal_data.get('productName')}\n"
        elif deal_data.get('companyName'):
            mensagem += f"\n🏢 *Empresa:* {deal_data.get('companyName')}\n"
        
        # Adiciona data/hora (GMT-3 - horário de Brasília)
        brasilia_tz = timezone(timedelta(hours=-3))
        now_brasilia = datetime.now(brasilia_tz)
        mensagem += f"📅 *Data:* {now_brasilia.strftime('%d/%m/%Y %H:%M')}\n"
        
        headers = {
            "apikey": evolution_api_key,
            "Content-Type": "application/json"
        }
        
        # 1. Tenta gerar imagem de celebração
        image_base64 = None
        try:
            image_bytes = generate_celebration_image(deal_data)
            if image_bytes:
                import base64
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                print("[OK] Imagem de celebracao gerada com sucesso")
        except Exception as img_error:
            print(f"[AVISO] Erro ao gerar imagem de celebracao: {img_error}")
            image_base64 = None
        
        # 2. Envia a imagem com a mensagem como caption (se foi gerada com sucesso)
        if image_base64:
            url_media = f"{evolution_api_url}/message/sendMedia/{instance_name}"
            payload_media = {
                "number": group_id,
                "mediatype": "image",
                "media": image_base64,
                "caption": mensagem,  # Mensagem como legenda da imagem
                "fileName": f"deal_celebration_{deal_data.get('dealName', 'deal').replace(' ', '_')}.png"
            }
            
            print(f"📤 Enviando imagem de celebração com mensagem para grupo {group_id}...")
            response_media = requests.post(url_media, headers=headers, json=payload_media, timeout=30)
            
            if response_media.status_code in [200, 201]:
                print(f"[OK] Imagem de celebracao enviada com sucesso!")
                return True
            else:
                print(f"[AVISO] Erro ao enviar imagem. Status: {response_media.status_code}, Response: {response_media.text}")
                # Se falhar, tenta enviar só o texto
        
        # 3. Fallback: envia apenas a mensagem de texto (se imagem falhou ou não foi gerada)
        url_text = f"{evolution_api_url}/message/sendText/{instance_name}"
        payload_text = {
            "number": group_id,
            "text": mensagem
        }
        
        print(f"📤 Enviando mensagem de texto para grupo {group_id}...")
        response_text = requests.post(url_text, headers=headers, json=payload_text, timeout=10)
        
        if response_text.status_code in [200, 201]:
            print(f"[OK] Notificacao WhatsApp enviada com sucesso! Deal: {deal_data.get('dealName')}")
            return True
        else:
            print(f"[ERRO] Erro ao enviar mensagem de texto. Status: {response_text.status_code}, Response: {response_text.text}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao enviar notificacao WhatsApp: {e}")
        return False

