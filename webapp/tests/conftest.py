# ============================================
# Configuration pytest pour LogStream Studio
# ============================================
import pytest
import os
import sys
import tempfile
import json

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Variables d'environnement pour les tests
os.environ['FLASK_ENV'] = 'testing'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-pytest'
os.environ['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
os.environ['MONGO_DB'] = 'test_monitoring'
os.environ['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
os.environ['ELASTICSEARCH_URL'] = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')


@pytest.fixture(scope='session')
def app():
    """Fixture Flask app pour les tests"""
    from app import app as flask_app
    
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })
    
    yield flask_app


@pytest.fixture
def client(app):
    """Fixture client de test Flask"""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Fixture pour obtenir les headers d'authentification"""
    # Créer un utilisateur de test et se connecter
    signup_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123'
    }
    
    # Tenter de créer l'utilisateur (peut échouer si existe déjà)
    client.post('/api/signup', 
                data=json.dumps(signup_data),
                content_type='application/json')
    
    # Se connecter
    login_data = {
        'username': 'testuser',
        'password': 'testpassword123'
    }
    response = client.post('/api/login',
                          data=json.dumps(login_data),
                          content_type='application/json')
    
    if response.status_code == 200:
        data = response.get_json()
        token = data.get('token', '')
        return {'Authorization': f'Bearer {token}'}
    
    return {}


@pytest.fixture
def sample_csv_file():
    """Fixture pour créer un fichier CSV temporaire"""
    content = """transaction_id,@timestamp,amount,status,payment_type,category
TXN001,2026-01-03T10:00:00Z,99.99,success,credit_card,electronics
TXN002,2026-01-03T11:00:00Z,49.99,failed,paypal,books
TXN003,2026-01-03T12:00:00Z,199.99,success,debit_card,clothing"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def sample_json_file():
    """Fixture pour créer un fichier JSON temporaire"""
    content = [
        {"transaction_id": "TXN001", "amount": 99.99, "status": "success"},
        {"transaction_id": "TXN002", "amount": 49.99, "status": "failed"}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(content, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def redis_client():
    """Fixture Redis client pour les tests"""
    import redis as redis_lib
    
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    try:
        client = redis_lib.from_url(redis_url, decode_responses=True)
        client.ping()
        yield client
        # Cleanup - supprimer les clés de test
        for key in client.keys('test:*'):
            client.delete(key)
    except Exception:
        yield None


@pytest.fixture
def es_client():
    """Fixture Elasticsearch client pour les tests"""
    from elasticsearch import Elasticsearch
    
    es_url = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')
    try:
        client = Elasticsearch([es_url], request_timeout=5)
        if client.ping():
            yield client
        else:
            yield None
    except Exception:
        yield None
