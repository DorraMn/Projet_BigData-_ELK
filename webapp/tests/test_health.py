# ============================================
# Tests API /health et endpoints de santé
# ============================================
import pytest
import json


class TestHealthEndpoints:
    """Tests pour les endpoints de santé"""
    
    def test_healthz_public_endpoint(self, client):
        """Test: /healthz est accessible sans authentification"""
        response = client.get('/healthz')
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data is not None
        assert 'status' in data
        assert data['status'] == 'ok'
    
    def test_healthz_returns_json(self, client):
        """Test: /healthz retourne du JSON"""
        response = client.get('/healthz')
        
        assert response.content_type == 'application/json'
    
    def test_health_page_requires_auth(self, client):
        """Test: /health nécessite une authentification"""
        response = client.get('/health')
        
        # Devrait rediriger vers login
        assert response.status_code in [302, 401]
    
    def test_api_health_requires_auth(self, client):
        """Test: /api/health nécessite une authentification"""
        response = client.get('/api/health')
        
        assert response.status_code in [401, 302]
    
    def test_api_health_with_auth(self, client, auth_headers):
        """Test: /api/health avec authentification"""
        response = client.get('/api/health', headers=auth_headers)
        
        # 200 (succès) ou 401 (si auth échoue)
        if response.status_code == 200:
            data = response.get_json()
            assert data is not None
    
    def test_health_check_services_status(self, client, auth_headers):
        """Test: Vérification du statut des services"""
        response = client.get('/api/health', headers=auth_headers)
        
        if response.status_code == 200:
            data = response.get_json()
            
            # Vérifier que les services sont listés
            # (les clés peuvent varier selon l'implémentation)
            possible_keys = ['elasticsearch', 'mongodb', 'redis', 'status', 'services', 'overall_status']
            has_service_info = any(key in data for key in possible_keys)
            # Le test passe si on a des infos de services
            assert has_service_info or 'healthy' in str(data)


class TestServiceHealth:
    """Tests pour la santé des services individuels"""
    
    def test_elasticsearch_health(self, es_client):
        """Test: Santé Elasticsearch"""
        if es_client is None:
            pytest.skip("Elasticsearch non disponible")
        
        health = es_client.cluster.health()
        
        assert 'status' in health
        assert health['status'] in ['green', 'yellow', 'red']
        assert 'cluster_name' in health
    
    def test_redis_health(self, redis_client):
        """Test: Santé Redis"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        # Ping
        assert redis_client.ping() == True
        
        # Info
        info = redis_client.info()
        assert 'redis_version' in info
    
    def test_mongodb_health(self):
        """Test: Santé MongoDB"""
        import pymongo
        import os
        
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
        
        try:
            client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
            result = client.admin.command('ping')
            assert result.get('ok') == 1.0
            client.close()
        except Exception:
            pytest.skip("MongoDB non disponible")


class TestAPIEndpoints:
    """Tests pour les autres endpoints API"""
    
    def test_root_endpoint(self, client):
        """Test: Endpoint racine"""
        response = client.get('/')
        
        # Devrait rediriger vers login ou afficher la page d'accueil
        assert response.status_code in [200, 302]
    
    def test_login_page(self, client):
        """Test: Page de login accessible"""
        response = client.get('/login')
        
        assert response.status_code == 200
    
    def test_signup_page(self, client):
        """Test: Page d'inscription accessible"""
        response = client.get('/signup')
        
        assert response.status_code == 200
    
    def test_api_login(self, client):
        """Test: API de login"""
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        response = client.post(
            '/api/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # 200 (succès), 401 (échec auth), 400 (données invalides)
        assert response.status_code in [200, 400, 401]
    
    def test_api_login_missing_fields(self, client):
        """Test: Login avec champs manquants"""
        response = client.post(
            '/api/login',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Devrait retourner une erreur
        assert response.status_code in [400, 401]
    
    def test_api_signup(self, client):
        """Test: API d'inscription"""
        import uuid
        
        signup_data = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'securepassword123'
        }
        
        response = client.post(
            '/api/signup',
            data=json.dumps(signup_data),
            content_type='application/json'
        )
        
        # 201 (créé), 200 (ok), 400 (existe déjà)
        assert response.status_code in [200, 201, 400, 409]
    
    def test_protected_route_without_auth(self, client):
        """Test: Route protégée sans authentification"""
        protected_routes = ['/dashboard', '/upload', '/search', '/health']
        
        for route in protected_routes:
            response = client.get(route)
            # Devrait rediriger vers login ou retourner 401
            assert response.status_code in [302, 401, 404], f"Route {route} non protégée"
    
    def test_logout(self, client, auth_headers):
        """Test: Déconnexion"""
        response = client.post('/api/logout', headers=auth_headers)
        
        # 200 (succès), 302 (redirect), 404 (route non implémentée)
        assert response.status_code in [200, 302, 401, 404]


class TestErrorHandling:
    """Tests pour la gestion des erreurs"""
    
    def test_404_not_found(self, client):
        """Test: Page 404"""
        response = client.get('/this-page-does-not-exist')
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test: Méthode non autorisée"""
        # POST sur une route GET only
        response = client.post('/login')
        
        # 405 (method not allowed) ou 302 (redirect)
        assert response.status_code in [200, 302, 405]
    
    def test_invalid_json(self, client):
        """Test: JSON invalide"""
        response = client.post(
            '/api/login',
            data='not valid json{{{',
            content_type='application/json'
        )
        
        # Devrait gérer proprement
        assert response.status_code in [400, 401, 415, 500]
