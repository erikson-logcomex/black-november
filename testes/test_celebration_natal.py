"""
Script de teste para gerar e enviar imagem de celebração com tema de Natal
para o grupo de WhatsApp de testes
"""
import os
import sys
from dotenv import load_dotenv
import requests
import base64
import json
from datetime import datetime, timezone, timedelta
from celebration_image_generator import generate_celebration_image

# Carrega variáveis de ambiente
load_dotenv()

# Grupo de TESTE do .env
TEST_GROUP_ID = os.getenv('ID_GRUPO_TESTE')

# Dados de exemplo de um deal para teste
test_deal_data = {
    'id': '999999999',
    'dealName': 'Teste Integração - Celebração',
    'amount': 9000.00,
    'ownerName': 'Bruno',
    'sdrName': 'Gabriela',
    'ldrName': 'Marcelo',
    'companyName': 'Empresa Teste LTDA',
    'productName': 'Rastreio Premium'
}


def send_test_celebration_natal():
    """
    Gera imagem de celebração com tema de Natal e envia para grupo de teste
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
        
        if not TEST_GROUP_ID:
            print("❌ ID_GRUPO_TESTE não configurado no .env")
            return False
        
        print("=" * 60)
        print("🎄 TESTE DE CELEBRAÇÃO COM TEMA DE NATAL 🎄")
        print("=" * 60)
        print(f"\n📋 Dados do deal de teste:")
        print(f"   Deal: {test_deal_data['dealName']}")
        print(f"   Valor: R$ {test_deal_data['amount']:,.2f}")
        print(f"   EV: {test_deal_data['ownerName']}")
        print(f"   SDR: {test_deal_data['sdrName']}")
        print(f"   LDR: {test_deal_data['ldrName']}")
        print(f"   Empresa: {test_deal_data['companyName']}")
        
        # Verifica se o tema está configurado como natal
        # Primeiro, vamos garantir que o tema seja natal
        theme_config_file = os.path.join(os.path.dirname(__file__), 'data', 'celebration_theme_config.json')
        theme_config_dir = os.path.dirname(theme_config_file)
        
        # Garante que o diretório existe
        if not os.path.exists(theme_config_dir):
            os.makedirs(theme_config_dir, mode=0o777, exist_ok=True)
        
        # Salva temporariamente o tema como natal para o teste
        theme_config = {"theme": "natal"}
        with open(theme_config_file, 'w', encoding='utf-8') as f:
            json.dump(theme_config, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Tema configurado como 'natal' para o teste")
        
        print("\n🎨 Gerando imagem de celebração com tema de Natal...")
        
        # Gera a imagem (vai usar o tema natal do arquivo JSON)
        try:
            image_bytes = generate_celebration_image(test_deal_data)
            print(f"✅ Imagem gerada! Tamanho: {len(image_bytes)} bytes")
        except Exception as img_error:
            print(f"❌ Erro ao gerar imagem: {img_error}")
            import traceback
            traceback.print_exc()
            return False
        
        # Salva localmente para verificação
        test_image_path = 'test_celebration_natal.png'
        with open(test_image_path, 'wb') as f:
            f.write(image_bytes)
        print(f"💾 Imagem salva como '{test_image_path}' para verificação")
        
        # Prepara mensagem de texto (caption)
        brasilia_tz = timezone(timedelta(hours=-3))
        now_brasilia = datetime.now(brasilia_tz)
        
        caption = "🎄 *TESTE - CONTRATO ASSINADO!* 🎅🏻\n\n"
        caption += f"💰 *Valor:* R$ {test_deal_data.get('amount', 0):,.2f}\n"
        caption += f"📝 *Deal:* {test_deal_data.get('dealName', 'N/A')}\n\n"
        caption += "👥 *Time Vencedor:*\n"
        caption += f"👔 *EV:* {test_deal_data.get('ownerName')}\n"
        caption += f"📞 *SDR:* {test_deal_data.get('sdrName')}\n"
        caption += f"🎯 *LDR:* {test_deal_data.get('ldrName')}\n"
        
        if test_deal_data.get('productName'):
            caption += f"\n📦 *Produto:* {test_deal_data.get('productName')}\n"
        elif test_deal_data.get('companyName'):
            caption += f"\n🏢 *Empresa:* {test_deal_data.get('companyName')}\n"
        
        caption += f"📅 *Data:* {now_brasilia.strftime('%d/%m/%Y %H:%M')}\n"
        caption += "\n"
        caption += "⚠️ *ESTE É UM TESTE DO TEMA DE NATAL*"
        
        # Converte imagem para base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        print(f"\n📱 Enviando para grupo de teste: {TEST_GROUP_ID}")
        print(f"🔗 Evolution API: {evolution_api_url}")
        print(f"📦 Instância: {instance_name}")
        
        # Endpoint da Evolution API para enviar mídia
        url_media = f"{evolution_api_url}/message/sendMedia/{instance_name}"
        
        headers = {
            "apikey": evolution_api_key,
            "Content-Type": "application/json"
        }
        
        payload_media = {
            "number": TEST_GROUP_ID,
            "mediatype": "image",
            "media": image_base64,
            "caption": caption,
            "fileName": "test_celebration_natal.png"
        }
        
        print("\n📤 Enviando imagem...")
        response = requests.post(url_media, headers=headers, json=payload_media, timeout=30)
        
        if response.status_code in [200, 201]:
            print("✅ Imagem enviada com sucesso para o grupo de teste!")
            print(f"📊 Response: {response.text}")
            return True
        else:
            print(f"❌ Erro ao enviar imagem. Status: {response.status_code}")
            print(f"📊 Response: {response.text}")
            
            # Tenta enviar apenas texto como fallback
            print("\n📤 Tentando enviar apenas mensagem de texto...")
            url_text = f"{evolution_api_url}/message/sendText/{instance_name}"
            payload_text = {
                "number": TEST_GROUP_ID,
                "text": caption
            }
            
            response_text = requests.post(url_text, headers=headers, json=payload_text, timeout=10)
            
            if response_text.status_code in [200, 201]:
                print("✅ Mensagem de texto enviada com sucesso!")
                return True
            else:
                print(f"❌ Erro ao enviar mensagem de texto. Status: {response_text.status_code}")
                print(f"📊 Response: {response_text.text}")
                return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar teste: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n🚀 Iniciando teste de celebração com tema de Natal...\n")
    success = send_test_celebration_natal()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ TESTE FALHOU")
        print("=" * 60)
        sys.exit(1)

