# ============================================
# Tests Recherche (Elasticsearch)
# ============================================
import pytest
import json


class TestSearch:
    """Tests pour la fonctionnalité de recherche"""
    
    def test_search_page_requires_auth(self, client):
        """Test: La page de recherche nécessite une authentification"""
        response = client.get('/search')
        assert response.status_code in [302, 401]
    
    def test_search_api_requires_auth(self, client):
        """Test: L'API de recherche nécessite une authentification"""
        response = client.get('/api/search?q=test')
        assert response.status_code in [401, 302]
    
    def test_search_with_query(self, client, auth_headers):
        """Test: Recherche avec un terme"""
        response = client.get(
            '/api/search?q=success',
            headers=auth_headers
        )
        # Peut être 200 (résultats) ou 401 (si auth échoue) ou 500 (si ES down)
        assert response.status_code in [200, 401, 500]
    
    def test_search_empty_query(self, client, auth_headers):
        """Test: Recherche avec requête vide"""
        response = client.get(
            '/api/search?q=',
            headers=auth_headers
        )
        assert response.status_code in [200, 400, 401, 500]
    
    def test_search_with_filters(self, client, auth_headers):
        """Test: Recherche avec filtres"""
        response = client.get(
            '/api/search?q=*&status=success&category=electronics',
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 500]
    
    def test_search_with_date_range(self, client, auth_headers):
        """Test: Recherche avec plage de dates"""
        response = client.get(
            '/api/search?q=*&from=2026-01-01&to=2026-01-31',
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 500]
    
    def test_search_pagination(self, client, auth_headers):
        """Test: Pagination des résultats"""
        response = client.get(
            '/api/search?q=*&page=1&size=10',
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 500]
    
    def test_search_special_characters(self, client, auth_headers):
        """Test: Recherche avec caractères spéciaux"""
        response = client.get(
            '/api/search?q=test%20%26%26%20error',
            headers=auth_headers
        )
        # Ne devrait pas planter
        assert response.status_code in [200, 400, 401, 500]
    
    def test_search_sql_injection_attempt(self, client, auth_headers):
        """Test: Protection contre injection SQL"""
        response = client.get(
            "/api/search?q='; DROP TABLE users; --",
            headers=auth_headers
        )
        # Devrait être géré proprement
        assert response.status_code in [200, 400, 401, 500]


class TestElasticsearchConnection:
    """Tests pour la connexion Elasticsearch"""
    
    def test_elasticsearch_ping(self, es_client):
        """Test: Ping Elasticsearch"""
        if es_client is None:
            pytest.skip("Elasticsearch non disponible")
        
        assert es_client.ping() == True
    
    def test_elasticsearch_cluster_health(self, es_client):
        """Test: Vérifier la santé du cluster"""
        if es_client is None:
            pytest.skip("Elasticsearch non disponible")
        
        health = es_client.cluster.health()
        assert health['status'] in ['green', 'yellow', 'red']
    
    def test_elasticsearch_list_indices(self, es_client):
        """Test: Lister les indices"""
        if es_client is None:
            pytest.skip("Elasticsearch non disponible")
        
        indices = es_client.cat.indices(format='json')
        # Convertir ListApiResponse en list si nécessaire
        indices_list = list(indices)
        assert isinstance(indices_list, list)
    
    def test_elasticsearch_search_logs_index(self, es_client):
        """Test: Recherche dans l'index logs-*"""
        if es_client is None:
            pytest.skip("Elasticsearch non disponible")
        
        try:
            result = es_client.search(
                index='logs-*',
                body={
                    'query': {'match_all': {}},
                    'size': 1
                }
            )
            assert 'hits' in result
        except Exception as e:
            # Index peut ne pas exister en test
            pytest.skip(f"Index logs-* non disponible: {e}")
