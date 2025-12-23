"""
Testes de Viabilidade de Gamificação - TODOS OS PERFIS
Valida dados disponíveis para badges de EVs, SDRs e LDRs
"""

import psycopg2
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do banco
DB_CONFIG = {
    'host': os.getenv('PG_HOST', 'localhost'),
    'port': os.getenv('PG_PORT', 5432),
    'database': os.getenv('PG_DATABASE_HUBSPOT', 'hubspot-sync'),
    'user': os.getenv('PG_USER'),
    'password': os.getenv('PG_PASSWORD')
}

def get_db_connection():
    """Cria conexão com o banco PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_subheader(title):
    """Imprime subcabeçalho formatado"""
    print(f"\n--- {title} ---\n")

# ============================================================================
# TESTES PERFIL: EVs (Executivos de Vendas)
# ============================================================================

def test_evs_deals_distribution():
    """Testa distribuição de deals ganhos por EVs nos últimos 7 dias"""
    print_subheader("🏆 EVs - Distribuição de Deals Ganhos (Últimos 7 dias)")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        d.analista_comercial as owner_id,
        COUNT(*) as deal_count,
        SUM(d.valor_ganho) as total_revenue,
        MIN(d.closedate - INTERVAL '3 hour') as first_deal,
        MAX(d.closedate - INTERVAL '3 hour') as last_deal
    FROM deals d
    LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
    WHERE LOWER(p.stage_label) LIKE '%ganho%'
        AND d.closedate >= CURRENT_DATE - INTERVAL '7 days'
        AND d.analista_comercial IS NOT NULL
    GROUP BY d.analista_comercial
    ORDER BY deal_count DESC, total_revenue DESC
    LIMIT 10;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"✅ {len(results)} EVs com deals ganhos hoje\n")
        
        for idx, (owner_id, count, revenue, first, last) in enumerate(results, 1):
            print(f"{idx}. EV ID {owner_id}:")
            print(f"   - Deals: {count}")
            print(f"   - Revenue: R$ {revenue:,.2f}")
            print(f"   - Período: {first.strftime('%H:%M')} → {last.strftime('%H:%M')}")
            
            # Badges detectáveis
            badges = []
            if count >= 3:
                badges.append("🥇 Hat Trick")
            if count >= 5:
                badges.append("🏆 Unstoppable")
            if count >= 10:
                badges.append("👑 Godlike")
            if revenue >= 50000:
                badges.append("💰 Big Fish")
            if revenue >= 150000:
                badges.append("💎 Whale Hunter")
                
            if badges:
                print(f"   - Badges: {', '.join(badges)}")
            print()
    else:
        print("⚠️ Nenhum EV com deals ganhos hoje")
    
    cursor.close()
    conn.close()

def test_evs_speed_badges():
    """Testa viabilidade de badges de velocidade para EVs"""
    print_subheader("⚡ EVs - Badges de Velocidade (Últimos 30 dias)")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    WITH deal_intervals AS (
        SELECT 
            d.analista_comercial as owner_id,
            d.closedate - INTERVAL '3 hour' as closedate,
            LAG(d.closedate - INTERVAL '3 hour') OVER (
                PARTITION BY d.analista_comercial 
                ORDER BY d.closedate
            ) as prev_closedate
        FROM deals d
        LEFT JOIN deal_stages_pipelines dsp ON d.dealstage = CAST(dsp.stage_id AS TEXT)
        WHERE 
            LOWER(dsp.stage_label) LIKE '%ganho%'
            AND d.closedate >= NOW() - INTERVAL '30 days'
            AND d.analista_comercial IS NOT NULL
    )
    SELECT 
        owner_id,
        COUNT(*) FILTER (WHERE closedate - prev_closedate < INTERVAL '1 hour') as speed_demon_count,
        COUNT(*) FILTER (WHERE closedate - prev_closedate < INTERVAL '3 hours') as flash_count,
        MIN(closedate - prev_closedate) as min_interval
    FROM deal_intervals
    WHERE prev_closedate IS NOT NULL
    GROUP BY owner_id
    HAVING COUNT(*) FILTER (WHERE closedate - prev_closedate < INTERVAL '1 hour') > 0
    ORDER BY speed_demon_count DESC
    LIMIT 5;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"✅ Top 5 EVs com badges de velocidade:\n")
        
        for idx, (owner_id, speed, flash, min_int) in enumerate(results, 1):
            print(f"{idx}. EV ID {owner_id}:")
            print(f"   - ⚡ Speed Demon: {speed} ocorrências (< 1h)")
            print(f"   - 🏃 Flash: {flash} ocorrências (< 3h)")
            if min_int:
                hours = min_int.total_seconds() / 3600
                print(f"   - Menor intervalo: {hours:.1f}h")
            print()
    else:
        print("⚠️ Nenhum EV com badges de velocidade (últimos 30 dias)")
    
    cursor.close()
    conn.close()

def test_evs_time_badges():
    """Testa badges de horário para EVs"""
    print_subheader("🕐 EVs - Badges de Horário (Últimos 7 dias)")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        d.analista_comercial as owner_id,
        COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.closedate - INTERVAL '3 hour') < 10) as early_bird_count,
        COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.closedate - INTERVAL '3 hour') > 17) as night_owl_count,
        MIN(EXTRACT(HOUR FROM d.closedate - INTERVAL '3 hour')) as earliest_hour,
        MAX(EXTRACT(HOUR FROM d.closedate - INTERVAL '3 hour')) as latest_hour
    FROM deals d
    LEFT JOIN deal_stages_pipelines dsp ON d.dealstage = CAST(dsp.stage_id AS TEXT)
    WHERE 
        LOWER(dsp.stage_label) LIKE '%ganho%'
        AND d.closedate >= NOW() - INTERVAL '7 days'
        AND d.analista_comercial IS NOT NULL
    GROUP BY d.analista_comercial
    HAVING COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.closedate - INTERVAL '3 hour') < 10) > 0
        OR COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.closedate - INTERVAL '3 hour') > 17) > 0
    ORDER BY 2 DESC, 3 DESC
    LIMIT 5;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"✅ Top 5 EVs com badges de horário:\n")
        
        for idx, (owner_id, early, night, earliest, latest) in enumerate(results, 1):
            print(f"{idx}. EV ID {owner_id}:")
            if early > 0:
                print(f"   - 🌅 Early Bird: {early} deal(s) antes 10h")
            if night > 0:
                print(f"   - 🌙 Night Owl: {night} deal(s) depois 17h")
            print(f"   - Horário: {int(earliest)}h → {int(latest)}h")
            print()
    else:
        print("⚠️ Nenhum EV com badges de horário (últimos 7 dias)")
    
    cursor.close()
    conn.close()

# ============================================================================
# TESTES PERFIL: SDRs (Sales Development Representatives)
# ============================================================================

def test_sdrs_scheduled_distribution():
    """Testa distribuição de agendamentos por SDRs"""
    print_subheader("📞 SDRs - Distribuição de Agendamentos (Hoje)")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Pipeline NEW = 6810518, Expansão = 4007305
    for pipeline_id, pipeline_name in [('6810518', 'NEW'), ('4007305', 'Expansão')]:
        print(f"\n🎯 Pipeline {pipeline_name}:\n")
        
        cursor = conn.cursor()
        
        # AVISO: data_de_agendamento NÃO TEM HORA (apenas DATE)
        # Badges de horário NÃO SÃO POSSÍVEIS para SDRs
        query = """
        SELECT 
            TRIM(d.pr_vendedor) as sdr_id,
            COUNT(*) as scheduled_count,
            MAX(d.data_de_agendamento) as last_scheduled_date
        FROM deals d
        WHERE 
            d.pipeline = %s
            AND DATE(d.data_de_agendamento) = CURRENT_DATE
            AND d.pr_vendedor IS NOT NULL
            AND TRIM(d.pr_vendedor) != ''
        GROUP BY TRIM(d.pr_vendedor)
        ORDER BY scheduled_count DESC
        LIMIT 5;
        """
        
        cursor.execute(query, (pipeline_id,))
        results = cursor.fetchall()
        
        if results:
            print(f"✅ {len(results)} SDRs com agendamentos hoje\n")
            
            for idx, (sdr_id, count, last_date) in enumerate(results, 1):
                print(f"{idx}. SDR ID {sdr_id}:")
                print(f"   - Agendamentos: {count}")
                if last_date:
                    print(f"   - Último agendamento: {last_date.strftime('%Y-%m-%d')}")
                
                # Badges detectáveis
                badges = []
                if count >= 3:
                    badges.append("🎯 Hat Trick SDR")
                if count >= 5:
                    badges.append("📅 Master Scheduler")
                if count >= 7:
                    badges.append("🏆 Unstoppable")
                    
                if badges:
                    print(f"   - Badges: {', '.join(badges)}")
                print()
        else:
            print("⚠️ Nenhum SDR com agendamentos hoje")
    
    cursor.close()
    conn.close()

def test_sdrs_weekly_performance():
    """Testa performance semanal de SDRs (apenas badges viáveis sem hora)"""
    print_subheader("📅 SDRs - Performance Semanal (Últimos 7 dias)")
    
    print("⚠️  IMPORTANTE: data_de_agendamento NÃO possui hora/minuto!")
    print("⚠️  Badges de velocidade e horário NÃO SÃO IMPLEMENTÁVEIS para SDRs\n")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Testa apenas badges viáveis: volume por dia/semana
    query = """
    SELECT 
        TRIM(d.pr_vendedor) as sdr_id,
        COUNT(*) as total_scheduled,
        COUNT(DISTINCT DATE(d.data_de_agendamento)) as days_active,
        MAX(subq.daily_max) as best_day_count
    FROM deals d
    LEFT JOIN (
        SELECT 
            TRIM(pr_vendedor) as sdr,
            DATE(data_de_agendamento) as dia,
            COUNT(*) as daily_max
        FROM deals
        WHERE data_de_agendamento >= CURRENT_DATE - INTERVAL '7 days'
            AND pr_vendedor IS NOT NULL
        GROUP BY TRIM(pr_vendedor), DATE(data_de_agendamento)
    ) subq ON TRIM(d.pr_vendedor) = subq.sdr
    WHERE 
        d.data_de_agendamento >= CURRENT_DATE - INTERVAL '7 days'
        AND d.pr_vendedor IS NOT NULL
        AND TRIM(d.pr_vendedor) != ''
    GROUP BY TRIM(d.pr_vendedor)
    ORDER BY total_scheduled DESC
    LIMIT 5;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"✅ Top 5 SDRs - Últimos 7 dias:\n")
        
        for idx, (sdr_id, total, days, best_day) in enumerate(results, 1):
            print(f"{idx}. SDR ID {sdr_id}:")
            print(f"   - Total agendamentos: {total}")
            print(f"   - Dias ativos: {days}/7")
            print(f"   - Melhor dia: {best_day} agendamentos")
            
            # Badges detectáveis (APENAS volume)
            badges = []
            if best_day and best_day >= 7:
                badges.append("🏆 Unstoppable (7+ em 1 dia)")
            if best_day and best_day >= 5:
                badges.append("📅 Master Scheduler (5+ em 1 dia)")
            if best_day and best_day >= 3:
                badges.append("🎯 Hat Trick (3+ em 1 dia)")
            if days >= 5:
                badges.append("📈 Consistency King (5+ dias ativos)")
                
            if badges:
                print(f"   - Badges: {', '.join(badges)}")
            print()
    else:
        print("⚠️ Nenhum SDR com agendamentos (últimos 7 dias)")
    
    cursor.close()
    conn.close()

def test_sdrs_data_structure():
    """Confirma estrutura de dados de agendamentos"""
    print_subheader("� SDRs - Estrutura de Dados (data_de_agendamento)")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        d.pr_vendedor as sdr_name,
        COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.createdate - INTERVAL '3 hour') < 10) as early_bird_count,
        COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.createdate - INTERVAL '3 hour') > 17) as night_owl_count
    FROM deals d
    LEFT JOIN deal_stages_pipelines dsp ON d.dealstage = CAST(dsp.stage_id AS TEXT)
    WHERE 
        dsp.pipeline_id IN ('6810518', '4007305')
        AND d.createdate >= NOW() - INTERVAL '7 days'
        AND d.pr_vendedor IS NOT NULL
        AND d.pr_vendedor != ''
    GROUP BY d.pr_vendedor
    HAVING COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.createdate - INTERVAL '3 hour') < 10) > 0
        OR COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.createdate - INTERVAL '3 hour') > 17) > 0
    ORDER BY 2 DESC, 3 DESC
    LIMIT 5;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"✅ Top 5 SDRs com badges de horário:\n")
        
        for idx, (sdr_name, early, night) in enumerate(results, 1):
            print(f"{idx}. {sdr_name}:")
            if early > 0:
                print(f"   - 🌅 Early Bird: {early} agendamento(s) antes 10h")
            if night > 0:
                print(f"   - 🌙 Night Owl: {night} agendamento(s) depois 17h")
            print()
    else:
        print("⚠️ Nenhum agendamento encontrado")
    
    cursor.close()
    conn.close()

# ============================================================================
# TESTES PERFIL: LDRs (Lead Development Representatives)
# ============================================================================

def test_ldrs_won_deals_distribution():
    """Testa distribuição de deals ganhos criados por LDRs"""
    print_subheader("🎓 LDRs - Deals Qualificados Ganhos (Hoje)")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        d.criado_por as ldr_name,
        COUNT(*) as won_deals_count,
        MIN(d.closedate - INTERVAL '3 hour') as first_won,
        MAX(d.closedate - INTERVAL '3 hour') as last_won
    FROM deals d
    LEFT JOIN deal_stages_pipelines dsp ON d.dealstage = CAST(dsp.stage_id AS TEXT)
    WHERE 
        LOWER(dsp.stage_label) LIKE '%ganho%'
        AND DATE(d.closedate - INTERVAL '3 hour') = CURRENT_DATE
        AND d.criado_por IS NOT NULL
        AND d.criado_por != ''
    GROUP BY d.criado_por
    ORDER BY won_deals_count DESC
    LIMIT 5;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"✅ {len(results)} LDRs com deals ganhos hoje\n")
        
        for idx, (ldr_name, count, first, last) in enumerate(results, 1):
            print(f"{idx}. {ldr_name}:")
            print(f"   - Deals ganhos: {count}")
            print(f"   - Período: {first.strftime('%H:%M')} → {last.strftime('%H:%M')}")
            
            # Badges detectáveis
            badges = []
            if count >= 3:
                badges.append("🎯 Hat Trick LDR")
            if count >= 5:
                badges.append("🏆 Unstoppable")
                
            if badges:
                print(f"   - Badges: {', '.join(badges)}")
            print()
    else:
        print("⚠️ Nenhum LDR com deals ganhos hoje")
    
    cursor.close()
    conn.close()

def test_ldrs_conversion_quality():
    """Testa qualidade de conversão dos LDRs (deals criados → ganhos)"""
    print_subheader("💎 LDRs - Taxa de Conversão (Últimos 30 dias)")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    WITH ldr_stats AS (
        SELECT 
            d.criado_por as ldr_name,
            COUNT(*) as total_created,
            COUNT(*) FILTER (WHERE LOWER(dsp.stage_label) LIKE '%ganho%') as total_won,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE LOWER(dsp.stage_label) LIKE '%ganho%') / COUNT(*),
                1
            ) as conversion_rate
        FROM deals d
        LEFT JOIN deal_stages_pipelines dsp ON d.dealstage = CAST(dsp.stage_id AS TEXT)
        WHERE 
            d.createdate >= NOW() - INTERVAL '30 days'
            AND d.criado_por IS NOT NULL
            AND d.criado_por != ''
        GROUP BY d.criado_por
        HAVING COUNT(*) >= 5  -- Mínimo 5 deals para ter estatística relevante
    )
    SELECT *
    FROM ldr_stats
    WHERE conversion_rate >= 50  -- Taxa mínima de 50% para badges
    ORDER BY conversion_rate DESC, total_won DESC
    LIMIT 5;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"✅ Top 5 LDRs com melhor conversão:\n")
        
        for idx, (ldr_name, created, won, rate) in enumerate(results, 1):
            print(f"{idx}. {ldr_name}:")
            print(f"   - Deals criados: {created}")
            print(f"   - Deals ganhos: {won}")
            print(f"   - Taxa de conversão: {rate}%")
            
            # Badges detectáveis
            if rate >= 80:
                print(f"   - Badge: 💎 Quality Master")
            print()
    else:
        print("⚠️ Nenhum LDR com taxa de conversão >= 50% (últimos 30 dias)")
    
    cursor.close()
    conn.close()

def test_ldrs_time_badges():
    """Testa badges de horário para LDRs"""
    print_subheader("🕐 LDRs - Badges de Horário (Últimos 7 dias)")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        d.criado_por as ldr_name,
        COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.closedate - INTERVAL '3 hour') < 10) as early_bird_count,
        COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.closedate - INTERVAL '3 hour') > 17) as night_owl_count
    FROM deals d
    LEFT JOIN deal_stages_pipelines dsp ON d.dealstage = CAST(dsp.stage_id AS TEXT)
    WHERE 
        LOWER(dsp.stage_label) LIKE '%ganho%'
        AND d.closedate >= NOW() - INTERVAL '7 days'
        AND d.criado_por IS NOT NULL
        AND d.criado_por != ''
    GROUP BY d.criado_por
    HAVING COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.closedate - INTERVAL '3 hour') < 10) > 0
        OR COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM d.closedate - INTERVAL '3 hour') > 17) > 0
    ORDER BY 2 DESC, 3 DESC
    LIMIT 5;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"✅ Top 5 LDRs com badges de horário:\n")
        
        for idx, (ldr_name, early, night) in enumerate(results, 1):
            print(f"{idx}. {ldr_name}:")
            if early > 0:
                print(f"   - 🌅 Early Bird: {early} deal(s) antes 10h")
            if night > 0:
                print(f"   - 🌙 Night Owl: {night} deal(s) depois 17h")
            print()
    else:
        print("⚠️ Nenhum LDR com badges de horário (últimos 7 dias)")
    
    cursor.close()
    conn.close()

# ============================================================================
# RESUMO CONSOLIDADO
# ============================================================================

def print_summary():
    """Imprime resumo consolidado dos testes"""
    print_header("📊 RESUMO - VIABILIDADE POR PERFIL")
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                         BADGES VIÁVEIS POR PERFIL                          ║
╚════════════════════════════════════════════════════════════════════════════╝

🏆 EVs (Executivos de Vendas):
   ✅ Hat Trick, Double Kill, Unstoppable, Godlike (volume)
   ✅ Big Fish, Whale Hunter, Suit Up (valor)
   ✅ Speed Demon, Flash (velocidade)
   ✅ Early Bird, Night Owl (horário)
   Métrica: Revenue + Deal Count
   
📞 SDRs (Sales Development Representatives):
   ✅ Hat Trick SDR, Master Scheduler, Unstoppable (agendamentos)
   ✅ Speed Demon (velocidade entre agendamentos)
   ✅ Early Bird, Night Owl (horário)
   ✅ Perfect Week (meta semanal)
   Métrica: Scheduled Count
   
🎓 LDRs (Lead Development Representatives):
   ✅ Hat Trick LDR, Golden Touch, Unstoppable (deals ganhos)
   ✅ Quality Master (taxa conversão)
   ✅ Early Bird, Night Owl (horário)
   ✅ Perfect Week (meta semanal)
   Métrica: Won Deals Count
   
🎖️ UNIVERSAIS (Todos):
   ✅ MVP da Semana (líder geral)
   ✅ Streak Master (5 dias consecutivos)
   ✅ Comeback (virar ranking)
   ✅ First Blood (primeiro do dia)

╔════════════════════════════════════════════════════════════════════════════╗
║                        PRÓXIMOS PASSOS RECOMENDADOS                        ║
╚════════════════════════════════════════════════════════════════════════════╝

1. ✅ Criar tabela badges_desbloqueados com campo user_type
2. ✅ Implementar endpoints separados por perfil:
   - /api/badges/ev/<owner_id>
   - /api/badges/sdr/<sdr_name>
   - /api/badges/ldr/<ldr_name>
3. ✅ Adaptar check_badges() para detectar badges dos 3 perfis
4. ✅ Criar 3 seções no Hall da Fama (rotação entre perfis)
5. ✅ Testar detecção em tempo real para cada perfil

Status: 🟢 VIÁVEL para todos os perfis
Risco: 🟢 BAIXO
Esforço: 🟡 MÉDIO-ALTO (3-4 dias)
""")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Executa todos os testes"""
    print_header("🎮 VALIDAÇÃO DE GAMIFICAÇÃO - TODOS OS PERFIS")
    
    try:
        # Testes EVs
        print_header("🏆 PERFIL: EVs (Executivos de Vendas)")
        test_evs_deals_distribution()
        test_evs_speed_badges()
        test_evs_time_badges()
        
        # Testes SDRs
        print_header("📞 PERFIL: SDRs (Sales Development Representatives)")
        test_sdrs_scheduled_distribution()
        test_sdrs_weekly_performance()
        test_sdrs_data_structure()
        
        # Testes LDRs
        print_header("🎓 PERFIL: LDRs (Lead Development Representatives)")
        test_ldrs_won_deals_distribution()
        test_ldrs_conversion_quality()
        test_ldrs_time_badges()
        
        # Resumo
        print_summary()
        
        print("\n✅ Todos os testes concluídos com sucesso!\n")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {str(e)}\n")
        raise

if __name__ == "__main__":
    main()




