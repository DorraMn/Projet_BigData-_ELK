"""
LogStream Studio - Exemple d'utilisation du module database.py
Montre comment intégrer le module dans l'application Flask
"""

from flask import Flask
from database import init_databases, db_manager

# Créer l'application Flask
app = Flask(__name__)

# Initialiser les connexions au démarrage
print("\n🚀 Démarrage de l'application LogStream Studio")
init_databases()


@app.route('/db-test')
def test_databases():
    """Route de test pour vérifier les connexions"""
    results = {
        'mongodb': 'disconnected',
        'redis': 'disconnected',
        'data': {}
    }
    
    # Test MongoDB
    if db_manager.mongo_connected:
        uploads_col = db_manager.get_mongo_collection('uploads')
        if uploads_col is not None:
            count = uploads_col.count_documents({})
            results['mongodb'] = 'connected'
            results['data']['uploads_count'] = count
    
    # Test Redis
    if db_manager.redis_connected:
        redis_client = db_manager.get_redis_client()
        if redis_client is not None:
            # Incrémenter un compteur de visites
            visits = redis_client.incr('page_visits')
            results['redis'] = 'connected'
            results['data']['page_visits'] = visits
    
    return results


@app.route('/health')
def health():
    """Endpoint de health check complet"""
    return db_manager.health_check()


# Exemple d'utilisation dans les routes
@app.route('/save-log', methods=['POST'])
def save_log():
    """Exemple: sauvegarder un log dans MongoDB"""
    from datetime import datetime
    
    logs_col = db_manager.get_mongo_collection('logs')
    if logs_col is None:
        return {'error': 'MongoDB not connected'}, 500
    
    log_entry = {
        'message': 'Test log entry',
        'level': 'info',
        'timestamp': datetime.utcnow(),
        'source': 'webapp'
    }
    
    result = logs_col.insert_one(log_entry)
    return {'success': True, 'id': str(result.inserted_id)}


@app.route('/cache-example/<key>')
def cache_example(key):
    """Exemple: utilisation du cache Redis"""
    redis_client = db_manager.get_redis_client()
    if redis_client is None:
        return {'error': 'Redis not connected'}, 500
    
    # Essayer de récupérer depuis le cache
    cached_value = redis_client.get(f'cache:{key}')
    
    if cached_value:
        return {'source': 'cache', 'value': cached_value}
    else:
        # Simuler une requête coûteuse
        new_value = f"Computed value for {key}"
        # Mettre en cache pour 60 secondes
        redis_client.set(f'cache:{key}', new_value, ex=60)
        return {'source': 'computed', 'value': new_value}


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        # Fermer les connexions à l'arrêt
        db_manager.close_all()
