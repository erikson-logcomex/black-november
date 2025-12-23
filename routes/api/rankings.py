"""
API Routes para rankings (Top EVs, SDRs, LDRs)
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from utils.auth import require_auth
from utils.db import get_db_connection_context
from utils.mappings import get_analyst_name
from psycopg2.extras import RealDictCursor

rankings_bp = Blueprint('rankings', __name__, url_prefix='/api')

@rankings_bp.route('/top-evs-today', methods=['GET'])
@require_auth
def get_top_evs_today():
    """Retorna o ranking dos Top 5 EVs por receita do dia atual"""
    with get_db_connection_context() as conn:
        if not conn:
            return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                WITH base AS (
                    SELECT
                        d.hs_object_id,
                        d.dealname,
                        d.hubspot_owner_id,
                        d.analista_comercial,
                        d.closedate,
                        d.valor_ganho,
                        d.tipo_de_receita,
                        d.tipo_de_negociacao,
                        p.stage_label
                    FROM deals d
                    LEFT JOIN deal_stages_pipelines p ON d.dealstage = CAST(p.stage_id AS TEXT)
                    WHERE COALESCE(d.tipo_de_receita, '') <> 'Pontual'
                        AND COALESCE(d.tipo_de_negociacao, '') <> 'Variação Cambial'
                ),
                deals_hoje AS (
                    SELECT 
                        COALESCE(analista_comercial, hubspot_owner_id) as owner_id,
                        valor_ganho
                    FROM base
                    WHERE (
                        LOWER(stage_label) LIKE '%ganho%'
                        OR LOWER(stage_label) LIKE '%faturamento%'
                        OR LOWER(stage_label) LIKE '%aguardando%'
                    )
                    AND DATE(closedate - INTERVAL '3 hour') = DATE(CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
                    AND valor_ganho IS NOT NULL
                    AND valor_ganho > 0
                )
                SELECT 
                    owner_id,
                    COALESCE(SUM(valor_ganho), 0) as total_revenue,
                    COUNT(*) as deal_count
                FROM deals_hoje
                WHERE owner_id IS NOT NULL
                    AND owner_id <> ''
                GROUP BY owner_id
                ORDER BY total_revenue DESC
                LIMIT 5
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            print(f"\n[DEBUG] Ranking EVs Hoje:")
            print(f"   Data atual no banco: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   EVs encontrados: {len(results)}")
            
            ranking = []
            for idx, row in enumerate(results):
                owner_id = row['owner_id']
                owner_name = get_analyst_name(owner_id)
                
                print(f"   {idx+1}o {owner_name}: R$ {row['total_revenue']:.2f} ({row['deal_count']} deals)")
                
                ranking.append({
                    'position': idx + 1,
                    'ownerId': owner_id,
                    'ownerName': owner_name,
                    'revenue': float(row['total_revenue']),
                    'dealCount': row['deal_count']
                })
            
            print(f"   [TOTAL] Total geral: R$ {sum([r['revenue'] for r in ranking]):.2f}\n")
            
            cursor.close()
            
            return jsonify({
                'status': 'success',
                'data': ranking,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Erro ao buscar ranking de EVs: {e}")
            return jsonify({'error': str(e)}), 500

@rankings_bp.route('/top-sdrs-today', methods=['GET'])
@require_auth
def get_top_sdrs_today():
    """Retorna o ranking dos Top 5 SDRs por agendamentos feitos hoje"""
    with get_db_connection_context() as conn:
        if not conn:
            return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            pipeline_filter = request.args.get('pipeline')
            
            query = """
                SELECT 
                    TRIM(pr_vendedor) as sdr_id,
                    COUNT(*) as scheduled_count,
                    MAX(data_de_agendamento) as last_scheduled_time
                FROM deals
                WHERE DATE(data_de_agendamento) = CURRENT_DATE
                    AND pr_vendedor IS NOT NULL
                    AND TRIM(pr_vendedor) <> ''
            """
            
            if pipeline_filter:
                query += f" AND pipeline = '{pipeline_filter}'"
            
            query += """
                GROUP BY TRIM(pr_vendedor)
                ORDER BY 
                    scheduled_count DESC,
                    last_scheduled_time ASC
                LIMIT 5
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            ranking = []
            for idx, row in enumerate(results):
                sdr_id = row['sdr_id']
                sdr_name = get_analyst_name(sdr_id)
                
                ranking.append({
                    'position': idx + 1,
                    'sdrId': sdr_id,
                    'sdrName': sdr_name,
                    'scheduledCount': row['scheduled_count']
                })
            
            cursor.close()
            
            return jsonify({
                'status': 'success',
                'data': ranking,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Erro ao buscar ranking de SDRs: {e}")
            return jsonify({'error': str(e)}), 500

@rankings_bp.route('/top-ldrs-today', methods=['GET'])
@require_auth
def get_top_ldrs_today():
    """Retorna o ranking dos Top 5 LDRs por deals ganhos hoje"""
    with get_db_connection_context() as conn:
        if not conn:
            return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT 
                    ldr_name,
                    COUNT(*) as won_deals_count,
                    COALESCE(SUM(amount), 0) as total_revenue
                FROM deal_notifications
                WHERE DATE(created_at) = CURRENT_DATE
                    AND ldr_name IS NOT NULL
                    AND ldr_name <> ''
                GROUP BY ldr_name
                ORDER BY won_deals_count DESC
                LIMIT 5
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            ranking = []
            for idx, row in enumerate(results):
                ldr_name = row['ldr_name']
                
                ranking.append({
                    'position': idx + 1,
                    'ldrName': ldr_name,
                    'wonDealsCount': row['won_deals_count'],
                    'totalRevenue': float(row['total_revenue'])
                })
            
            cursor.close()
            
            return jsonify({
                'status': 'success',
                'data': ranking,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Erro ao buscar ranking de LDRs: {e}")
            return jsonify({'error': str(e)}), 500

