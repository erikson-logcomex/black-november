"""
Script de teste para verificar se o scraper do Looker funciona
após a configuração inicial
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.looker_scraper import get_looker_gauge_value
import json

if __name__ == "__main__":
    print("🧪 Testando extração de dados do Looker...")
    print("="*60)
    
    result = get_looker_gauge_value()
    
    if result:
        print("\n" + "="*60)
        print("📊 RESULTADOS:")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("="*60)
        
        # Salva em arquivo
        with open('looker_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados salvos em: looker_test_result.json")
    else:
        print("\n❌ Não foi possível obter os dados do Looker")
        print("💡 Verifique se os cookies estão válidos")

