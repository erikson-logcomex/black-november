"""
Script de teste para verificar se o scraper de ARR funciona
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.arr_scraper import get_arr_value
import json

if __name__ == "__main__":
    print("🧪 Testando extração de dados de ARR do Looker...")
    print("="*60)
    
    result = get_arr_value()
    
    if result:
        print("\n" + "="*60)
        print("📊 RESULTADOS:")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("="*60)
        
        # Formata valores monetários
        if result.get('arr_value'):
            print(f"\n💰 ARR Atual: R$ {result['arr_value']:,.2f}")
        if result.get('arr_target'):
            print(f"🎯 Meta: R$ {result['arr_target']:,.2f}")
        if result.get('remaining'):
            print(f"📈 Restante: R$ {result['remaining']:,.2f}")
        if result.get('percentage'):
            print(f"📊 Progresso: {result['percentage']:.2f}%")
        
        # Salva em arquivo
        with open('arr_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados salvos em: arr_test_result.json")
    else:
        print("\n❌ Não foi possível obter os dados de ARR do Looker")
        print("💡 Verifique se os cookies estão válidos")

