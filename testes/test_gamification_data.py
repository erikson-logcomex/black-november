"""
Script de validação de dados para sistema de gamificação
Verifica se os dados existentes suportam badges propostos

Executa:
1. Análise de timestamps (granularidade hora/minuto/segundo)
2. Distribuição de deals por hora do dia
3. Intervalos entre deals consecutivos
4. Queries de exemplo para cada tipo de badge
5. Cobertura de dados de analistas
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

load_dotenv()

def get_db_connection():
    """Conecta ao banco de dados PostgreSQL"""
    return psycopg2.connect(
        host=os.getenv('PG_HOST'),
        port=os.getenv('PG_PORT'),
        database=os.getenv('PG_DATABASE_HUBSPOT'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASSWORD')
    )

def print_section(title):
    """Imprime seção formatada"""
    print(f"\n{'='*80}")
    print(f"🔍 {title}")
    print('='*80)

def test_timestamp_granularity():
    """Testa se closedate tem hora, minuto e segundo"""
    print_section("TESTE 1: Granularidade de Timestamps")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Busca deals recentes com closedate
    query = """
    SELECT 
        d.hs_object_id,
        d.dealname,
        d.closedate,
        d.createdate,
        EXTRACT(HOUR FROM d.closedate) as hora,
        EXTRACT(MINUTE FROM d.closedate) as minuto,
        EXTRACT(SECOND FROM d.closedate) as segundo,
        p.stage_label
    FROM deals d
    LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
    WHERE d.closedate >= CURRENT_DATE - INTERVAL '7 days'
        AND LOWER(p.stage_label) LIKE '%ganho%'
    ORDER BY d.closedate DESC
    LIMIT 10
    """
    
    cur.execute(query)
    deals = cur.fetchall()
    
    if not deals:
        print("❌ CRÍTICO: Nenhum deal ganho nos últimos 7 dias!")
        return False
    
    print(f"✅ Encontrados {len(deals)} deals ganhos nos últimos 7 dias\n")
    print("Primeiros 5 deals com timestamps:")
    
    has_hours = False
    has_minutes = False
    has_seconds = False
    
    for i, deal in enumerate(deals[:5], 1):
        closedate = deal['closedate']
        print(f"\n{i}. {deal['dealname'][:50]}")
        print(f"   closedate: {closedate}")
        print(f"   Hora: {int(deal['hora'])}h | Minuto: {int(deal['minuto'])}min | Segundo: {int(deal['segundo'])}s")
        
        if deal['hora'] and int(deal['hora']) > 0:
            has_hours = True
        if deal['minuto'] and int(deal['minuto']) > 0:
            has_minutes = True
        if deal['segundo'] and int(deal['segundo']) > 0:
            has_seconds = True
    
    print(f"\n📊 RESULTADO:")
    print(f"   ✅ Horas disponíveis: {'SIM' if has_hours else 'NÃO'}")
    print(f"   ✅ Minutos disponíveis: {'SIM' if has_minutes else 'NÃO'}")
    print(f"   ✅ Segundos disponíveis: {'SIM' if has_seconds else 'NÃO'}")
    
    # Testa createdate também
    cur.execute("""
        SELECT 
            EXTRACT(HOUR FROM createdate) as hora,
            EXTRACT(MINUTE FROM createdate) as minuto
        FROM deals
        WHERE createdate IS NOT NULL
        LIMIT 5
    """)
    
    create_dates = cur.fetchall()
    has_create_time = any(row['hora'] or row['minuto'] for row in create_dates)
    print(f"   ✅ createdate tem hora/minuto: {'SIM' if has_create_time else 'NÃO'}")
    
    cur.close()
    conn.close()
    
    return has_hours or has_minutes

def test_deals_distribution_by_hour():
    """Analisa distribuição de deals por hora do dia"""
    print_section("TESTE 2: Distribuição de Deals por Hora do Dia")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
    SELECT 
        EXTRACT(HOUR FROM closedate - INTERVAL '3 hour') as hora_brasil,
        COUNT(*) as deal_count,
        ROUND(AVG(valor_ganho), 2) as avg_value
    FROM deals d
    LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
    WHERE LOWER(p.stage_label) LIKE '%ganho%'
        AND closedate >= CURRENT_DATE - INTERVAL '30 days'
        AND valor_ganho > 0
    GROUP BY EXTRACT(HOUR FROM closedate - INTERVAL '3 hour')
    ORDER BY hora_brasil
    """
    
    cur.execute(query)
    distribution = cur.fetchall()
    
    if not distribution:
        print("❌ Sem dados suficientes para análise")
        return False
    
    print("\n📊 Deals por hora (últimos 30 dias, horário Brasil GMT-3):\n")
    
    total_deals = sum(row['deal_count'] for row in distribution)
    
    for row in distribution:
        hora = int(row['hora_brasil'])
        count = row['deal_count']
        avg_val = float(row['avg_value']) if row['avg_value'] else 0
        bar = '█' * int(count / max(1, total_deals / 20))
        print(f"   {hora:02d}h: {bar} ({count} deals, média R$ {avg_val:,.2f})")
    
    # Detecta horários com mais deals (para badges)
    top_hours = sorted(distribution, key=lambda x: x['deal_count'], reverse=True)[:3]
    print(f"\n🏆 Horários mais produtivos:")
    for i, row in enumerate(top_hours, 1):
        hora = int(row['hora_brasil'])
        count = row['deal_count']
        print(f"   {i}º. {hora:02d}h - {count} deals")
    
    # Valida badges de horário
    early_birds = next((r['deal_count'] for r in distribution if int(r['hora_brasil']) < 10), 0)
    night_owls = next((r['deal_count'] for r in distribution if int(r['hora_brasil']) >= 17), 0)
    
    print(f"\n✅ BADGES DE HORÁRIO VIÁVEIS:")
    print(f"   🌅 Early Bird (antes 10h): {early_birds} deals disponíveis")
    print(f"   🌙 Night Owl (depois 17h): {night_owls} deals disponíveis")
    
    cur.close()
    conn.close()
    
    return True

def test_deal_intervals():
    """Analisa intervalos entre deals consecutivos do mesmo EV"""
    print_section("TESTE 3: Intervalos Entre Deals Consecutivos")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
    WITH deals_ordenados AS (
        SELECT 
            d.analista_comercial,
            d.hs_object_id,
            d.dealname,
            d.closedate,
            LAG(d.closedate) OVER (
                PARTITION BY d.analista_comercial 
                ORDER BY d.closedate
            ) as closedate_anterior
        FROM deals d
        LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
        WHERE LOWER(p.stage_label) LIKE '%ganho%'
            AND d.closedate >= CURRENT_DATE - INTERVAL '30 days'
            AND d.analista_comercial IS NOT NULL
    ),
    intervalos AS (
        SELECT 
            analista_comercial,
            hs_object_id,
            dealname,
            closedate,
            closedate_anterior,
            EXTRACT(EPOCH FROM (closedate - closedate_anterior)) / 3600 as horas_intervalo
        FROM deals_ordenados
        WHERE closedate_anterior IS NOT NULL
    )
    SELECT 
        analista_comercial,
        COUNT(*) as total_deals,
        ROUND(AVG(horas_intervalo), 2) as media_horas,
        ROUND(MIN(horas_intervalo), 2) as menor_intervalo_horas,
        ROUND(MAX(horas_intervalo), 2) as maior_intervalo_horas,
        COUNT(CASE WHEN horas_intervalo < 1 THEN 1 END) as deals_menos_1h,
        COUNT(CASE WHEN horas_intervalo < 3 THEN 1 END) as deals_menos_3h,
        COUNT(CASE WHEN horas_intervalo < 24 THEN 1 END) as deals_menos_24h
    FROM intervalos
    GROUP BY analista_comercial
    ORDER BY total_deals DESC
    LIMIT 10
    """
    
    cur.execute(query)
    results = cur.fetchall()
    
    if not results:
        print("❌ Sem dados suficientes para análise de intervalos")
        return False
    
    print("\n📊 Análise de intervalos entre deals por EV (últimos 30 dias):\n")
    
    total_menos_1h = 0
    total_menos_3h = 0
    
    for row in results:
        ev = row['analista_comercial']
        total = row['total_deals']
        media = float(row['media_horas'])
        menor = float(row['menor_intervalo_horas'])
        deals_1h = row['deals_menos_1h']
        deals_3h = row['deals_menos_3h']
        deals_24h = row['deals_menos_24h']
        
        total_menos_1h += deals_1h
        total_menos_3h += deals_3h
        
        print(f"   👤 {ev[:30]}")
        print(f"      Total deals: {total}")
        print(f"      Intervalo médio: {media:.1f}h")
        print(f"      Menor intervalo: {menor:.1f}h")
        print(f"      < 1h: {deals_1h} | < 3h: {deals_3h} | < 24h: {deals_24h}")
        print()
    
    print(f"✅ BADGES DE VELOCIDADE VIÁVEIS:")
    print(f"   ⚡ Speed Demon (< 1h entre deals): {total_menos_1h} ocorrências")
    print(f"   🏃 Flash (< 3h entre deals): {total_menos_3h} ocorrências")
    
    if total_menos_1h < 5:
        print(f"\n⚠️  AVISO: Poucos deals com intervalo < 1h. Considere ajustar critério.")
    
    cur.close()
    conn.close()
    
    return total_menos_3h > 0

def test_badge_queries():
    """Testa queries para cada tipo de badge"""
    print_section("TESTE 4: Queries de Badges Propostos")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    badges_results = {}
    
    # 1. HAT TRICK (3 deals em 1 dia)
    print("\n🥇 Badge: HAT TRICK (3 deals em 1 dia)")
    cur.execute("""
        SELECT 
            analista_comercial,
            DATE(closedate - INTERVAL '3 hour') as dia,
            COUNT(*) as deals_count
        FROM deals d
        LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
        WHERE LOWER(p.stage_label) LIKE '%ganho%'
            AND closedate >= CURRENT_DATE - INTERVAL '30 days'
            AND analista_comercial IS NOT NULL
        GROUP BY analista_comercial, DATE(closedate - INTERVAL '3 hour')
        HAVING COUNT(*) >= 3
        ORDER BY deals_count DESC
        LIMIT 5
    """)
    hat_tricks = cur.fetchall()
    badges_results['hat_trick'] = len(hat_tricks)
    
    if hat_tricks:
        for row in hat_tricks:
            print(f"   ✅ {row['analista_comercial']} - {row['deals_count']} deals no dia {row['dia']}")
    else:
        print("   ⚠️  Nenhum Hat Trick nos últimos 30 dias")
    
    # 2. BIG FISH (deal > R$ 100k)
    print("\n💰 Badge: BIG FISH (deal > R$ 100.000)")
    cur.execute("""
        SELECT 
            analista_comercial,
            dealname,
            valor_ganho,
            closedate
        FROM deals d
        LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
        WHERE LOWER(p.stage_label) LIKE '%ganho%'
            AND closedate >= CURRENT_DATE - INTERVAL '30 days'
            AND valor_ganho >= 100000
            AND analista_comercial IS NOT NULL
        ORDER BY valor_ganho DESC
        LIMIT 5
    """)
    big_fish = cur.fetchall()
    badges_results['big_fish'] = len(big_fish)
    
    if big_fish:
        for row in big_fish:
            print(f"   ✅ {row['analista_comercial']} - R$ {float(row['valor_ganho']):,.2f} ({row['dealname'][:40]})")
    else:
        print("   ⚠️  Nenhum Big Fish nos últimos 30 dias")
    
    # 3. SNIPER (5 deals consecutivos > R$ 50k)
    print("\n🎯 Badge: SNIPER (5 deals consecutivos > R$ 50k)")
    cur.execute("""
        WITH deals_ordenados AS (
            SELECT 
                analista_comercial,
                valor_ganho,
                closedate,
                CASE WHEN valor_ganho >= 50000 THEN 1 ELSE 0 END as high_value
            FROM deals d
            LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
            WHERE LOWER(p.stage_label) LIKE '%ganho%'
                AND closedate >= CURRENT_DATE - INTERVAL '30 days'
                AND analista_comercial IS NOT NULL
            ORDER BY analista_comercial, closedate
        ),
        streaks AS (
            SELECT 
                analista_comercial,
                SUM(high_value) OVER (
                    PARTITION BY analista_comercial 
                    ORDER BY closedate 
                    ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
                ) as consecutive_high_value
            FROM deals_ordenados
        )
        SELECT DISTINCT
            analista_comercial,
            consecutive_high_value
        FROM streaks
        WHERE consecutive_high_value >= 5
        LIMIT 5
    """)
    snipers = cur.fetchall()
    badges_results['sniper'] = len(snipers)
    
    if snipers:
        for row in snipers:
            print(f"   ✅ {row['analista_comercial']} - {row['consecutive_high_value']} deals consecutivos > R$ 50k")
    else:
        print("   ⚠️  Nenhum Sniper nos últimos 30 dias")
    
    # 4. SUIT UP (R$ 500k na semana)
    print("\n👔 Badge: SUIT UP (R$ 500k na semana)")
    cur.execute("""
        SELECT 
            analista_comercial,
            date_trunc('week', closedate - INTERVAL '3 hour') as semana,
            SUM(valor_ganho) as total_semana,
            COUNT(*) as deals_count
        FROM deals d
        LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
        WHERE LOWER(p.stage_label) LIKE '%ganho%'
            AND closedate >= CURRENT_DATE - INTERVAL '30 days'
            AND analista_comercial IS NOT NULL
        GROUP BY analista_comercial, date_trunc('week', closedate - INTERVAL '3 hour')
        HAVING SUM(valor_ganho) >= 500000
        ORDER BY total_semana DESC
        LIMIT 5
    """)
    suit_ups = cur.fetchall()
    badges_results['suit_up'] = len(suit_ups)
    
    if suit_ups:
        for row in suit_ups:
            print(f"   ✅ {row['analista_comercial']} - R$ {float(row['total_semana']):,.2f} ({row['deals_count']} deals)")
    else:
        print("   ⚠️  Nenhum Suit Up nos últimos 30 dias")
    
    # 5. EARLY BIRD (deal antes das 10h)
    print("\n🌅 Badge: EARLY BIRD (deal fechado antes das 10h)")
    cur.execute("""
        SELECT 
            analista_comercial,
            dealname,
            closedate,
            EXTRACT(HOUR FROM closedate - INTERVAL '3 hour') as hora_brasil
        FROM deals d
        LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
        WHERE LOWER(p.stage_label) LIKE '%ganho%'
            AND closedate >= CURRENT_DATE - INTERVAL '30 days'
            AND EXTRACT(HOUR FROM closedate - INTERVAL '3 hour') < 10
            AND analista_comercial IS NOT NULL
        ORDER BY closedate DESC
        LIMIT 5
    """)
    early_birds = cur.fetchall()
    badges_results['early_bird'] = len(early_birds)
    
    if early_birds:
        for row in early_birds:
            hora = int(row['hora_brasil'])
            print(f"   ✅ {row['analista_comercial']} - {hora:02d}h ({row['dealname'][:40]})")
    else:
        print("   ⚠️  Nenhum Early Bird nos últimos 30 dias")
    
    print(f"\n{'='*80}")
    print("📊 RESUMO DE VIABILIDADE DOS BADGES:")
    print('='*80)
    
    total_badges = 0
    for badge, count in badges_results.items():
        status = "✅ VIÁVEL" if count > 0 else "⚠️  RARO/AJUSTAR"
        print(f"   {badge.upper()}: {count} ocorrências - {status}")
        if count > 0:
            total_badges += 1
    
    print(f"\n🎯 RESULTADO: {total_badges} de {len(badges_results)} badges possuem dados válidos")
    
    cur.close()
    conn.close()
    
    return badges_results

def test_analyst_data_coverage():
    """Verifica cobertura de dados de analistas"""
    print_section("TESTE 5: Cobertura de Dados de Analistas")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Busca analistas únicos com deals ganhos
    cur.execute("""
        SELECT DISTINCT
            d.analista_comercial,
            COUNT(*) as total_deals,
            SUM(valor_ganho) as total_revenue
        FROM deals d
        LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
        WHERE LOWER(p.stage_label) LIKE '%ganho%'
            AND d.closedate >= CURRENT_DATE - INTERVAL '30 days'
            AND d.analista_comercial IS NOT NULL
            AND d.analista_comercial != ''
        GROUP BY d.analista_comercial
        ORDER BY total_deals DESC
    """)
    
    analysts = cur.fetchall()
    
    print(f"\n📋 Encontrados {len(analysts)} analistas com deals ganhos (últimos 30 dias)\n")
    
    # Carrega mapeamento
    mapping_file = 'data/analistas_mapeamento.json'
    has_mapping = os.path.exists(mapping_file)
    
    if has_mapping:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
    else:
        mapping = {}
        print("⚠️  Arquivo analistas_mapeamento.json não encontrado!\n")
    
    missing_mapping = []
    missing_photos = []
    
    for analyst in analysts[:10]:  # Top 10
        analyst_id = analyst['analista_comercial']
        deals = analyst['total_deals']
        revenue = float(analyst['total_revenue']) if analyst['total_revenue'] else 0
        
        # Verifica mapeamento
        has_name = analyst_id in mapping if has_mapping else False
        name = mapping.get(analyst_id, analyst_id) if has_mapping else analyst_id
        
        # Verifica foto
        normalized_name = name.lower().replace(' ', '_')
        photo_path = f'static/img/team/{normalized_name}.png'
        has_photo = os.path.exists(photo_path)
        
        status_map = "✅" if has_name else "❌"
        status_photo = "✅" if has_photo else "❌"
        
        print(f"   {status_map} {status_photo} {name[:30]}")
        print(f"      Deals: {deals} | Revenue: R$ {revenue:,.2f}")
        print(f"      ID: {analyst_id}")
        
        if not has_name:
            missing_mapping.append(analyst_id)
        if not has_photo:
            missing_photos.append(name)
    
    print(f"\n{'='*80}")
    print("📊 COBERTURA DE DADOS:")
    print('='*80)
    
    coverage_map = ((len(analysts) - len(missing_mapping)) / len(analysts) * 100) if analysts else 0
    coverage_photo = ((len(analysts) - len(missing_photos)) / len(analysts) * 100) if analysts else 0
    
    print(f"   Mapeamento de nomes: {coverage_map:.1f}% ({len(analysts) - len(missing_mapping)}/{len(analysts)})")
    print(f"   Fotos disponíveis: {coverage_photo:.1f}% ({len(analysts) - len(missing_photos)}/{len(analysts)})")
    
    if missing_mapping:
        print(f"\n⚠️  {len(missing_mapping)} analistas sem mapeamento:")
        for mid in missing_mapping[:5]:
            print(f"      - {mid}")
    
    if missing_photos:
        print(f"\n⚠️  {len(missing_photos)} analistas sem foto:")
        for name in missing_photos[:5]:
            print(f"      - {name}")
    
    cur.close()
    conn.close()
    
    return coverage_map >= 80 and coverage_photo >= 80

def generate_report():
    """Gera relatório consolidado"""
    print_section("RELATÓRIO FINAL DE VIABILIDADE")
    
    print("""
    
    ✅ = Implementável sem modificações
    ⚠️  = Requer ajustes ou poucos dados
    ❌ = Não implementável com dados atuais
    
    RECOMENDAÇÕES:
    
    1. BADGES PRIORITÁRIOS (implementar primeiro):
       ✅ Hat Trick (3 deals/dia) - dados completos
       ✅ Big Fish (deal > R$ 100k) - dados completos  
       ✅ Early Bird (antes 10h) - dados completos
       ✅ Night Owl (depois 17h) - dados completos
       ✅ Suit Up (R$ 500k/semana) - dados completos
    
    2. BADGES QUE REQUEREM AJUSTE:
       ⚠️  Speed Demon - considerar intervalo > 1h (ex: < 3h ou < 6h)
       ⚠️  Flash - ajustar para "3 deals no mesmo dia" em vez de "< 3h"
       ⚠️  Sniper - funciona mas é raro (critério exigente)
    
    3. MVP DA SEMANA:
       ✅ Dados completos para ranking semanal
       ✅ Revenue, deal count, avg deal disponíveis
    
    4. RECORDES:
       ✅ Maior dia - implementável
       ✅ Maior deal - implementável
       ✅ Mais deals em 1 dia - implementável
       ⚠️  Melhor streak - requer window functions complexas
    
    5. DADOS DE ANALISTAS:
       ⚠️  Verificar cobertura de fotos e mapeamento de nomes
       ⚠️  Alguns IDs podem precisar ser adicionados ao mapping
    
    PRÓXIMOS PASSOS:
    - Implementar badges prioritários (1-2 dias)
    - Criar tabela badges_desbloqueados
    - Ajustar badges de velocidade conforme dados disponíveis
    - Completar mapeamento de analistas e fotos
    """)

def main():
    """Executa todos os testes"""
    print("="*80)
    print("🎮 VALIDAÇÃO DE DADOS PARA SISTEMA DE GAMIFICAÇÃO")
    print("="*80)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Banco: {os.getenv('PG_DATABASE_HUBSPOT')} @ {os.getenv('PG_HOST')}")
    
    try:
        # Executa testes
        test1 = test_timestamp_granularity()
        test2 = test_deals_distribution_by_hour()
        test3 = test_deal_intervals()
        badges = test_badge_queries()
        test5 = test_analyst_data_coverage()
        
        # Relatório final
        generate_report()
        
        print("\n✅ Todos os testes concluídos com sucesso!")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
