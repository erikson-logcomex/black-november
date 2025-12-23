"""
Script de teste para verificar todas as rotas após refatoração
"""
from app import app

def test_routes():
    """Testa as principais rotas da aplicação"""
    client = app.test_client()
    
    print("=" * 60)
    print("TESTE DE ROTAS APOS REFATORACAO")
    print("=" * 60)
    
    # Rotas de páginas
    print("\n[PAGINAS]")
    routes_pages = [
        ('/', 'GET'),
        ('/natal', 'GET'),
        ('/black-november', 'GET'),
        ('/metas', 'GET'),
        ('/hall-da-fama', 'GET'),
        ('/destaques', 'GET'),
    ]
    
    for route, method in routes_pages:
        try:
            if method == 'GET':
                r = client.get(route)
            print(f"  {route:30} -> Status: {r.status_code}")
        except Exception as e:
            print(f"  {route:30} -> ERRO: {str(e)[:50]}")
    
    # Rotas de API
    print("\n[APIS - Revenue]")
    routes_revenue = [
        ('/api/revenue', 'GET'),
        ('/api/revenue/today', 'GET'),
        ('/api/revenue/until-yesterday', 'GET'),
        ('/api/pipeline/today', 'GET'),
    ]
    
    for route, method in routes_revenue:
        try:
            r = client.get(route)
            print(f"  {route:40} -> Status: {r.status_code}")
        except Exception as e:
            print(f"  {route:40} -> ERRO: {str(e)[:50]}")
    
    print("\n[APIS - Rankings]")
    routes_rankings = [
        ('/api/top-evs-today', 'GET'),
        ('/api/top-sdrs-today', 'GET'),
        ('/api/top-ldrs-today', 'GET'),
    ]
    
    for route, method in routes_rankings:
        try:
            r = client.get(route)
            print(f"  {route:40} -> Status: {r.status_code}")
        except Exception as e:
            print(f"  {route:40} -> ERRO: {str(e)[:50]}")
    
    print("\n[APIS - Hall da Fama]")
    routes_hall = [
        ('/api/hall-da-fama/evs-realtime', 'GET'),
        ('/api/hall-da-fama/sdrs-realtime?pipeline=6810518', 'GET'),
        ('/api/hall-da-fama/ldrs-realtime', 'GET'),
    ]
    
    for route, method in routes_hall:
        try:
            r = client.get(route)
            print(f"  {route:50} -> Status: {r.status_code}")
        except Exception as e:
            print(f"  {route:50} -> ERRO: {str(e)[:50]}")
    
    print("\n[APIS - Destaques]")
    routes_destaques = [
        ('/api/destaques/evs?periodo=semana&pipeline=6810518', 'GET'),
        ('/api/destaques/sdrs?periodo=semana&pipeline=6810518', 'GET'),
        ('/api/destaques/ldrs?periodo=semana&pipeline=6810518', 'GET'),
    ]
    
    for route, method in routes_destaques:
        try:
            r = client.get(route)
            print(f"  {route:60} -> Status: {r.status_code}")
        except Exception as e:
            print(f"  {route:60} -> ERRO: {str(e)[:50]}")
    
    print("\n[APIS - Badges]")
    routes_badges = [
        ('/api/recordes', 'GET'),
        ('/api/badges/stats', 'GET'),
        ('/api/mvp-semana', 'GET'),
    ]
    
    for route, method in routes_badges:
        try:
            r = client.get(route)
            print(f"  {route:40} -> Status: {r.status_code}")
        except Exception as e:
            print(f"  {route:40} -> ERRO: {str(e)[:50]}")
    
    print("\n[APIS - Webhooks]")
    routes_webhooks = [
        ('/api/webhook/logs', 'GET'),
        ('/api/webhook/test', 'GET'),
    ]
    
    for route, method in routes_webhooks:
        try:
            r = client.get(route)
            print(f"  {route:40} -> Status: {r.status_code}")
        except Exception as e:
            print(f"  {route:40} -> ERRO: {str(e)[:50]}")
    
    print("\n[APIS - Debug]")
    routes_debug = [
        ('/api/debug/pool-status', 'GET'),
    ]
    
    for route, method in routes_debug:
        try:
            r = client.get(route)
            print(f"  {route:40} -> Status: {r.status_code}")
        except Exception as e:
            print(f"  {route:40} -> ERRO: {str(e)[:50]}")
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DE BLUEPRINTS")
    print("=" * 60)
    for name, bp in app.blueprints.items():
        print(f"  - {name}: {len(bp.deferred_functions)} funcoes registradas")
    print(f"\nTotal de blueprints: {len(app.blueprints)}")
    print(f"Total de rotas: {len(list(app.url_map.iter_rules()))}")
    print("=" * 60)

if __name__ == '__main__':
    test_routes()

