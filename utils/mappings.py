"""
Utilitários para mapeamento de analistas e produtos
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPPING_FILE = os.path.join(BASE_DIR, 'data', 'analistas_mapeamento.json')
PRODUTOS_DEPARA_FILE = os.path.join(BASE_DIR, 'data', 'produtos_de_para.json')

# Cache dos mapeamentos
ANALYSTS_MAPPING = {}
PRODUTOS_DEPARA = {}

def load_analysts_mapping():
    """Carrega o mapeamento de IDs do HubSpot para nomes dos analistas"""
    global ANALYSTS_MAPPING
    try:
        if os.path.exists(MAPPING_FILE):
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                ANALYSTS_MAPPING = json.load(f)
            print(f"Mapeamento carregado: {len(ANALYSTS_MAPPING)} analistas encontrados")
        else:
            print(f"Aviso: Arquivo de mapeamento não encontrado: {MAPPING_FILE}")
            ANALYSTS_MAPPING = {}
    except Exception as e:
        print(f"Erro ao carregar mapeamento de analistas: {e}")
        ANALYSTS_MAPPING = {}

def load_produtos_depara():
    """Carrega o mapeamento DE-PARA de produtos (nome antigo → nome novo)"""
    global PRODUTOS_DEPARA
    try:
        if os.path.exists(PRODUTOS_DEPARA_FILE):
            with open(PRODUTOS_DEPARA_FILE, 'r', encoding='utf-8') as f:
                PRODUTOS_DEPARA = json.load(f)
            print(f"Mapeamento DE-PARA de produtos carregado: {len(PRODUTOS_DEPARA)} produtos")
        else:
            print(f"Aviso: Arquivo DE-PARA de produtos não encontrado: {PRODUTOS_DEPARA_FILE}")
            PRODUTOS_DEPARA = {}
    except Exception as e:
        print(f"Erro ao carregar mapeamento DE-PARA de produtos: {e}")
        PRODUTOS_DEPARA = {}

def get_analyst_name(user_id):
    """
    Converte ID do HubSpot para nome do analista
    Retorna o nome se encontrado, ou o ID original se não encontrar
    """
    if not user_id:
        return ''
    
    # Converte para string para garantir compatibilidade
    user_id_str = str(user_id)
    
    # Busca no mapeamento
    name = ANALYSTS_MAPPING.get(user_id_str)
    
    if name:
        return name
    
    # Se não encontrar, retorna o ID original (pode ser que já seja um nome)
    return str(user_id)

def normalize_product_name(product_name):
    """
    Normaliza nome do produto usando mapeamento DE-PARA
    Se não encontrar no mapeamento, retorna o nome original (fallback)
    
    Args:
        product_name: Nome do produto vindo do HubSpot
    
    Returns:
        str: Nome normalizado ou nome original se não estiver no DE-PARA
    """
    if not product_name:
        return ''
    
    # Busca no mapeamento DE-PARA
    normalized = PRODUTOS_DEPARA.get(product_name, product_name)
    
    if normalized != product_name:
        print(f"  [MAP] Produto normalizado: '{product_name}' -> '{normalized}'")
    
    return normalized

# Carrega os mapeamentos ao importar o módulo
load_analysts_mapping()
load_produtos_depara()

