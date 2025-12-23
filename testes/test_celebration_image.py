"""
Script de teste para gerar e enviar imagem de celebração para grupo de WhatsApp de testes
"""
import os
from dotenv import load_dotenv
import requests
from celebration_image_generator import generate_celebration_image
from datetime import datetime, timezone, timedelta

load_dotenv()

# Grupo de TESTE
TEST_GROUP_ID = "120363425707763466@g.us"

# Dados de exemplo de um deal
test_deal_data = {
    'dealName': 'CAP LOGISTICA FRIGORIFICADA S.A. - CNPJ: 02.956.834/0002-81',
    'amount': 1500.00,
    'ownerName': 'Marilon Rodrigues',
    'sdrName': 'Gustavo Modesto',
    'ldrName': 'Bianca Aguiar',
    'companyName': 'CAP LOGISTICA FRIGORIFICADA S.A.'
}


def send_whatsapp_image_test():
    """
    Envia imagem de celebração para grupo de teste
    """
    try:
        # Configurações da Evolution API
        evolution_api_url = os.getenv('EVOLUTION_API_URL', 'https://evolution-api-logcomex.34-49-195-55.nip.io')
        evolution_api_key = os.getenv('EVOLUTION_API_KEY')
        instance_name = os.getenv('EVOLUTION_INSTANCE_NAME', 'RevOps')
        
        # Valida variáveis de ambiente
        if not evolution_api_key:
            print("❌ EVOLUTION_API_KEY não configurada")
            return False
        
        print("🎨 Gerando imagem de celebração...")
        # Gera a imagem
        image_bytes = generate_celebration_image(test_deal_data)
        print(f"✅ Imagem gerada! Tamanho: {len(image_bytes)} bytes")
        
        # Salva localmente para verificação
        with open('test_celebration.png', 'wb') as f:
            f.write(image_bytes)
        print("💾 Imagem salva como 'test_celebration.png' para verificação")
        
        # Prepara mensagem de texto
        brasilia_tz = timezone(timedelta(hours=-3))
        now_brasilia = datetime.now(brasilia_tz)
        
        caption = "🎉 *DEAL GANHO!* (TESTE)\n\n"
        caption += f"💰 *Valor:* R$ {test_deal_data.get('amount', 0):,.2f}\n"
        caption += f"📝 *Deal:* {test_deal_data.get('dealName', 'N/A')}\n\n"
        caption += "👥 *Time Vencedor:*\n"
        caption += f"👔 *EV:* {test_deal_data.get('ownerName')}\n"
        caption += f"📞 *SDR:* {test_deal_data.get('sdrName')}\n"
        caption += f"🎯 *LDR:* {test_deal_data.get('ldrName')}\n"
        caption += f"\n🏢 *Empresa:* {test_deal_data.get('companyName')}\n"
        caption += f"📅 *Data:* {now_brasilia.strftime('%d/%m/%Y %H:%M')}\n"
        caption += "\n"
        caption += "\n⚠️ *ESTE É UM TESTE*"
        
        print(f"\n📱 Enviando para grupo de teste: {TEST_GROUP_ID}")
        
        # Endpoint da Evolution API para enviar mídia
        url = f"{evolution_api_url}/message/sendMedia/{instance_name}"
        
        headers = {
            "apikey": evolution_api_key,
            "Content-Type": "application/json"
        }
        
        # Prepara payload com a imagem
        import base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        payload = {
            "number": TEST_GROUP_ID,
            "mediatype": "image",
            "mimetype": "image/png",
            "caption": caption,
            "media": image_base64  # Sem o prefixo data:image/png;base64,
        }
        
        print("📤 Enviando requisição para Evolution API...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 201 or response.status_code == 200:
            print("✅ Imagem enviada com sucesso para o grupo de teste!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Erro ao enviar imagem: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DE GERAÇÃO E ENVIO DE IMAGEM DE CELEBRAÇÃO")
    print("=" * 60)
    print()
    
    success = send_whatsapp_image_test()
    
    print()
    print("=" * 60)
    if success:
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("❌ TESTE FALHOU!")
    print("=" * 60)
