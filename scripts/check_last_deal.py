#!/usr/bin/env python3
"""
Script para verificar a tabela deal_notifications e mostrar estatísticas
sobre os últimos deals ganhos registrados.
"""
import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_db_connection_context
from psycopg2.extras import RealDictCursor
import json

load_dotenv()

def format_currency(value):
    """Formata valor como moeda brasileira"""
    if value is None:
        return "R$ 0,00"
    return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def format_datetime(dt):
    """Formata datetime para exibição"""
    if dt is None:
        return "N/A"
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    # Converte para horário de Brasília (GMT-3)
    brasilia_tz = timezone(timedelta(hours=-3))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_brasilia = dt.astimezone(brasilia_tz)
    return dt_brasilia.strftime('%d/%m/%Y %H:%M:%S')

def get_statistics():
    """Obtém estatísticas da tabela deal_notifications"""
    with get_db_connection_context() as conn:
        if not conn:
            print("❌ Erro: Não foi possível conectar ao banco de dados")
            print("   Verifique as variáveis de ambiente: PG_HOST, PG_PORT, PG_DATABASE_HUBSPOT, PG_USER, PG_PASSWORD")
            return None
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Estatísticas gerais
            stats_query = """
            SELECT 
                COUNT(*) as total_deals,
                SUM(amount) as total_valor,
                MIN(created_at) as primeiro_deal,
                MAX(created_at) as ultimo_deal,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as deals_24h,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as deals_7d,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as deals_30d
            FROM deal_notifications
            """
            cursor.execute(stats_query)
            stats = cursor.fetchone()
            
            # Últimos 10 deals
            last_deals_query = """
            SELECT 
                id,
                deal_name,
                amount,
                owner_name,
                sdr_name,
                ldr_name,
                company_name,
                pipeline,
                deal_stage,
                created_at,
                payload
            FROM deal_notifications
            ORDER BY created_at DESC
            LIMIT 10
            """
            cursor.execute(last_deals_query)
            last_deals = cursor.fetchall()
            
            # Deals por dia (últimos 7 dias)
            deals_by_day_query = """
            SELECT 
                DATE(created_at AT TIME ZONE 'America/Sao_Paulo') as data,
                COUNT(*) as quantidade,
                SUM(amount) as valor_total
            FROM deal_notifications
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY DATE(created_at AT TIME ZONE 'America/Sao_Paulo')
            ORDER BY data DESC
            """
            cursor.execute(deals_by_day_query)
            deals_by_day = cursor.fetchall()
            
            cursor.close()
            
            return {
                'stats': stats,
                'last_deals': last_deals,
                'deals_by_day': deals_by_day
            }
            
        except Exception as e:
            print(f"❌ Erro ao consultar banco de dados: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    print("=" * 80)
    print("📊 ANÁLISE DA TABELA DEAL_NOTIFICATIONS")
    print("=" * 80)
    print()
    
    data = get_statistics()
    
    if not data:
        return
    
    stats = data['stats']
    last_deals = data['last_deals']
    deals_by_day = data['deals_by_day']
    
    # Estatísticas gerais
    print("📈 ESTATÍSTICAS GERAIS")
    print("-" * 80)
    print(f"Total de deals registrados: {stats['total_deals']}")
    print(f"Valor total: {format_currency(stats['total_valor'])}")
    print(f"Primeiro deal: {format_datetime(stats['primeiro_deal'])}")
    print(f"Último deal: {format_datetime(stats['ultimo_deal'])}")
    print()
    print("📅 DEALS POR PERÍODO")
    print("-" * 80)
    print(f"Últimas 24 horas: {stats['deals_24h']} deals")
    print(f"Últimos 7 dias: {stats['deals_7d']} deals")
    print(f"Últimos 30 dias: {stats['deals_30d']} deals")
    print()
    
    # Deals por dia
    if deals_by_day:
        print("📆 DEALS POR DIA (ÚLTIMOS 7 DIAS)")
        print("-" * 80)
        for row in deals_by_day:
            data_str = row['data'].strftime('%d/%m/%Y') if row['data'] else 'N/A'
            print(f"{data_str}: {row['quantidade']} deals - {format_currency(row['valor_total'])}")
        print()
    
    # Últimos deals
    if last_deals:
        print("🎯 ÚLTIMOS 10 DEALS GANHOS")
        print("-" * 80)
        for i, deal in enumerate(last_deals, 1):
            print(f"\n{i}. Deal ID: {deal['id']}")
            print(f"   Nome: {deal['deal_name']}")
            print(f"   Valor: {format_currency(deal['amount'])}")
            print(f"   Data: {format_datetime(deal['created_at'])}")
            if deal['owner_name']:
                print(f"   EV: {deal['owner_name']}")
            if deal['sdr_name']:
                print(f"   SDR: {deal['sdr_name']}")
            if deal['ldr_name']:
                print(f"   LDR: {deal['ldr_name']}")
            if deal['company_name']:
                print(f"   Empresa: {deal['company_name']}")
            if deal['pipeline']:
                print(f"   Pipeline: {deal['pipeline']}")
    else:
        print("⚠️ Nenhum deal encontrado na tabela")
    
    print()
    print("=" * 80)
    
    # Análise do último deal
    if stats['ultimo_deal']:
        ultimo_deal_dt = stats['ultimo_deal']
        if isinstance(ultimo_deal_dt, str):
            ultimo_deal_dt = datetime.fromisoformat(ultimo_deal_dt.replace('Z', '+00:00'))
        
        agora = datetime.now(timezone.utc)
        if ultimo_deal_dt.tzinfo is None:
            ultimo_deal_dt = ultimo_deal_dt.replace(tzinfo=timezone.utc)
        
        diferenca = agora - ultimo_deal_dt
        
        print("⏰ ANÁLISE DO ÚLTIMO DEAL")
        print("-" * 80)
        print(f"Último deal registrado: {format_datetime(stats['ultimo_deal'])}")
        
        if diferenca.days > 0:
            print(f"⏳ Tempo desde o último deal: {diferenca.days} dia(s) e {diferenca.seconds // 3600} hora(s)")
        elif diferenca.seconds > 3600:
            horas = diferenca.seconds // 3600
            minutos = (diferenca.seconds % 3600) // 60
            print(f"⏳ Tempo desde o último deal: {horas} hora(s) e {minutos} minuto(s)")
        else:
            minutos = diferenca.seconds // 60
            print(f"⏳ Tempo desde o último deal: {minutos} minuto(s)")
        
        if diferenca.days > 7:
            print("⚠️ ATENÇÃO: Não há deals registrados há mais de 7 dias!")
        elif diferenca.days > 1:
            print("⚠️ ATENÇÃO: Não há deals registrados há mais de 1 dia!")
        else:
            print("✅ Sistema parece estar funcionando normalmente")
    
    print("=" * 80)

if __name__ == '__main__':
    main()

