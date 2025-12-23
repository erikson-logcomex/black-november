import os
from dotenv import load_dotenv
import psycopg2


def run_migration(sql_path: str):
    load_dotenv()

    host = os.getenv('PG_HOST')
    port = os.getenv('PG_PORT')
    db = os.getenv('PG_DATABASE_HUBSPOT')
    user = os.getenv('PG_USER')
    password = os.getenv('PG_PASSWORD')

    if not all([host, port, db, user, password]):
        raise RuntimeError('Variáveis de ambiente do banco ausentes. Verifique o arquivo .env (PG_HOST, PG_PORT, PG_DATABASE_HUBSPOT, PG_USER, PG_PASSWORD).')

    with open(sql_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    conn = psycopg2.connect(host=host, port=port, database=db, user=user, password=password)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql)
        print('✅ Migração executada com sucesso.')
    finally:
        conn.close()


if __name__ == '__main__':
    sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations', '001_create_deal_notifications.sql')
    run_migration(sql_file)
