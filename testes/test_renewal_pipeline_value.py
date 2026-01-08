"""
Script de teste para verificar o valor retornado pela função get_renewal_pipeline_revenue()
e comparar com os dados do teste de comparação
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.revenue import get_renewal_pipeline_revenue
from datetime import datetime, timezone, timedelta

def format_currency(value):
    """Formata valor em moeda brasileira"""
    return f"R$ {value:,.2f}"

print("="*80)
print("TESTE: VALOR DO PIPELINE DE RENOVACAO")
print("="*80)

# Busca receita do pipeline de renovação para o mês atual
renewal_revenue = get_renewal_pipeline_revenue()

print(f"\n[RESULTADO] Receita do Pipeline de Renovacao (mes atual):")
print(f"   Valor retornado: {format_currency(renewal_revenue)}")

# Compara com o valor esperado do teste anterior
# Do teste: Pipeline 7075777: 49 deals, R$ 15.386,27
expected_value = 15386.27
difference = abs(renewal_revenue - expected_value)
difference_percent = (difference / expected_value * 100) if expected_value > 0 else 0

print(f"\n[COMPARACAO]")
print(f"   Valor esperado (do teste HubSpot): {format_currency(expected_value)}")
print(f"   Valor retornado pela funcao: {format_currency(renewal_revenue)}")
print(f"   Diferenca: {format_currency(difference)} ({difference_percent:.2f}%)")

if difference < 0.01:
    print("   [OK] Valores coincidem!")
elif difference_percent < 1:
    print("   [AVISO] Diferenca pequena (< 1%)")
else:
    print("   [ERRO] Diferenca significativa!")

print("\n" + "="*80)
print("TESTE CONCLUIDO")
print("="*80)
