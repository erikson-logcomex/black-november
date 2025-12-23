"""
Script para criar tabela badges_desbloqueados e popular com dados iniciais
Executa o DDL e faz uma importação retroativa dos badges do dia
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def execute_ddl():
    """Executa o DDL para criar tabela e view"""
    conn = None
    try:
        print("📊 Conectando ao banco de dados...")
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT'),
            database=os.getenv('PG_DATABASE_HUBSPOT'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD')
        )
        cursor = conn.cursor()
        
        print("📝 Lendo arquivo DDL...")
        with open('ddl_badges_desbloqueados.sql', 'r', encoding='utf-8') as f:
            ddl = f.read()
        
        print("🔨 Executando DDL...")
        cursor.execute(ddl)
        conn.commit()
        
        print("✅ Tabela badges_desbloqueados criada com sucesso!")
        print("✅ View recordes_black_november criada com sucesso!")
        print("✅ Índices criados com sucesso!")
        
        # Verifica se a tabela foi criada
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'badges_desbloqueados'
        """)
        
        if cursor.fetchone()[0] == 1:
            print("✅ Verificação: Tabela existe no banco!")
        else:
            print("❌ Erro: Tabela não foi criada!")
            return False
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar DDL: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def populate_initial_data():
    """
    Popula dados iniciais fazendo chamadas aos endpoints de real-time
    para registrar badges do dia atual
    """
    import requests
    
    try:
        print("\n🔄 Populando dados iniciais dos badges de hoje...")
        print("📡 Fazendo chamadas aos endpoints de real-time...")
        
        base_url = "http://localhost:5000"
        
        # Chama endpoints para gerar badges em tempo real
        endpoints = [
            f"{base_url}/api/hall-da-fama/evs-realtime",
            f"{base_url}/api/hall-da-fama/sdrs-realtime?pipeline=6810518",
            f"{base_url}/api/hall-da-fama/sdrs-realtime?pipeline=4007305",
            f"{base_url}/api/hall-da-fama/ldrs-realtime"
        ]
        
        for endpoint in endpoints:
            print(f"  → Chamando {endpoint}...")
            try:
                response = requests.get(endpoint, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    total = data.get('total', 0)
                    print(f"    ✅ {total} registros processados")
                else:
                    print(f"    ⚠️ Status {response.status_code}")
            except Exception as e:
                print(f"    ❌ Erro: {e}")
        
        print("\n✅ População inicial concluída!")
        print("💡 Os badges serão salvos automaticamente quando os endpoints forem chamados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao popular dados: {e}")
        return False

def verify_data():
    """Verifica dados na tabela"""
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT'),
            database=os.getenv('PG_DATABASE_HUBSPOT'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD')
        )
        cursor = conn.cursor()
        
        print("\n📊 Verificando dados na tabela...")
        
        # Total de badges
        cursor.execute("SELECT COUNT(*) FROM badges_desbloqueados")
        total = cursor.fetchone()[0]
        print(f"  Total de badges: {total}")
        
        # Badges de hoje
        cursor.execute("""
            SELECT COUNT(*) 
            FROM badges_desbloqueados 
            WHERE DATE(unlocked_at) = CURRENT_DATE
        """)
        hoje = cursor.fetchone()[0]
        print(f"  Badges de hoje: {hoje}")
        
        # Por categoria
        cursor.execute("""
            SELECT badge_category, COUNT(*) as total
            FROM badges_desbloqueados
            WHERE DATE(unlocked_at) = CURRENT_DATE
            GROUP BY badge_category
            ORDER BY total DESC
        """)
        print("\n  Por categoria:")
        for row in cursor.fetchall():
            print(f"    {row[0]}: {row[1]}")
        
        # Por user_type
        cursor.execute("""
            SELECT user_type, COUNT(*) as total
            FROM badges_desbloqueados
            WHERE DATE(unlocked_at) = CURRENT_DATE
            GROUP BY user_type
            ORDER BY total DESC
        """)
        print("\n  Por tipo de usuário:")
        for row in cursor.fetchall():
            print(f"    {row[0]}: {row[1]}")
        
        # Top 5 usuários
        cursor.execute("""
            SELECT user_name, user_type, COUNT(*) as total
            FROM badges_desbloqueados
            WHERE DATE(unlocked_at) = CURRENT_DATE
            GROUP BY user_name, user_type
            ORDER BY total DESC
            LIMIT 5
        """)
        print("\n  Top 5 usuários com mais badges hoje:")
        for row in cursor.fetchall():
            print(f"    {row[0]} ({row[1]}): {row[2]} badges")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")
        if conn:
            conn.close()
        return False

if __name__ == '__main__':
    print("="*60)
    print("🚀 SETUP - BADGES DESBLOQUEADOS")
    print("="*60)
    
    # Passo 1: Criar tabela
    if not execute_ddl():
        print("\n❌ Falha ao criar tabela. Abortando...")
        exit(1)
    
    # Passo 2: Instruções para popular dados
    print("\n" + "="*60)
    print("📝 PRÓXIMO PASSO: POPULAR DADOS")
    print("="*60)
    print("\n⚠️  IMPORTANTE: Para popular os badges, siga estes passos:")
    print("\n1. Certifique-se que o Flask está rodando:")
    print("   python app.py")
    print("\n2. Em outro terminal, execute:")
    print("   python populate_badges.py")
    print("\nOu faça chamadas manuais aos endpoints:")
    print("   curl http://localhost:5000/api/hall-da-fama/evs-realtime")
    print("   curl http://localhost:5000/api/hall-da-fama/sdrs-realtime?pipeline=6810518")
    print("   curl http://localhost:5000/api/hall-da-fama/sdrs-realtime?pipeline=4007305")
    print("   curl http://localhost:5000/api/hall-da-fama/ldrs-realtime")
    
    # Passo 3: Verificar dados
    print("\n" + "="*60)
    print("🔍 VERIFICAÇÃO")
    print("="*60)
    verify_data()
    
    print("\n✅ Setup concluído!")
    print("💡 A tabela está pronta para receber badges!")
