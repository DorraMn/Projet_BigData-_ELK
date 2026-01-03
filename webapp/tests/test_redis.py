# ============================================
# Tests Cache Redis
# ============================================
import pytest
import json
import time


class TestRedisCache:
    """Tests pour le cache Redis"""
    
    def test_redis_connection(self, redis_client):
        """Test: Connexion à Redis"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        assert redis_client.ping() == True
    
    def test_redis_set_get(self, redis_client):
        """Test: Set et Get basique"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        # Set une valeur
        redis_client.set('test:key1', 'value1')
        
        # Get la valeur
        result = redis_client.get('test:key1')
        assert result == 'value1'
        
        # Cleanup
        redis_client.delete('test:key1')
    
    def test_redis_set_with_expiration(self, redis_client):
        """Test: Set avec expiration (TTL)"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        # Set avec TTL de 2 secondes
        redis_client.setex('test:expiring_key', 2, 'temp_value')
        
        # Vérifier que la valeur existe
        assert redis_client.get('test:expiring_key') == 'temp_value'
        
        # Vérifier le TTL
        ttl = redis_client.ttl('test:expiring_key')
        assert ttl > 0 and ttl <= 2
    
    def test_redis_json_cache(self, redis_client):
        """Test: Cache d'objets JSON"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        data = {
            'user_id': 123,
            'username': 'testuser',
            'permissions': ['read', 'write']
        }
        
        # Stocker en JSON
        redis_client.set('test:user:123', json.dumps(data))
        
        # Récupérer et parser
        cached = redis_client.get('test:user:123')
        result = json.loads(cached)
        
        assert result['user_id'] == 123
        assert result['username'] == 'testuser'
        assert 'read' in result['permissions']
        
        # Cleanup
        redis_client.delete('test:user:123')
    
    def test_redis_increment(self, redis_client):
        """Test: Compteur avec INCR"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        key = 'test:counter'
        
        # Initialiser à 0
        redis_client.set(key, 0)
        
        # Incrémenter
        redis_client.incr(key)
        redis_client.incr(key)
        redis_client.incr(key)
        
        assert int(redis_client.get(key)) == 3
        
        # Cleanup
        redis_client.delete(key)
    
    def test_redis_hash(self, redis_client):
        """Test: Hash Redis pour stocker des objets"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        key = 'test:session:abc123'
        
        # Stocker un hash
        redis_client.hset(key, mapping={
            'user_id': '123',
            'username': 'testuser',
            'login_time': '2026-01-03T10:00:00Z'
        })
        
        # Récupérer tout le hash
        session = redis_client.hgetall(key)
        
        assert session['user_id'] == '123'
        assert session['username'] == 'testuser'
        
        # Récupérer un champ spécifique
        username = redis_client.hget(key, 'username')
        assert username == 'testuser'
        
        # Cleanup
        redis_client.delete(key)
    
    def test_redis_list(self, redis_client):
        """Test: Liste Redis pour les files d'attente"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        key = 'test:queue'
        
        # Ajouter des éléments
        redis_client.rpush(key, 'task1', 'task2', 'task3')
        
        # Vérifier la longueur
        assert redis_client.llen(key) == 3
        
        # Pop un élément
        task = redis_client.lpop(key)
        assert task == 'task1'
        
        # Cleanup
        redis_client.delete(key)
    
    def test_redis_set_operations(self, redis_client):
        """Test: Opérations sur les Sets"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        key = 'test:active_users'
        
        # Ajouter des membres
        redis_client.sadd(key, 'user1', 'user2', 'user3')
        
        # Vérifier l'appartenance
        assert redis_client.sismember(key, 'user1') == True
        assert redis_client.sismember(key, 'user99') == False
        
        # Compter les membres
        assert redis_client.scard(key) == 3
        
        # Cleanup
        redis_client.delete(key)
    
    def test_redis_cache_miss(self, redis_client):
        """Test: Cache miss (clé inexistante)"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        result = redis_client.get('test:nonexistent:key:12345')
        assert result is None
    
    def test_redis_delete(self, redis_client):
        """Test: Suppression de clé"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        # Créer puis supprimer
        redis_client.set('test:to_delete', 'value')
        assert redis_client.get('test:to_delete') == 'value'
        
        redis_client.delete('test:to_delete')
        assert redis_client.get('test:to_delete') is None


class TestRedisCachePatterns:
    """Tests pour les patterns de cache courants"""
    
    def test_cache_aside_pattern(self, redis_client):
        """Test: Pattern Cache-Aside"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        cache_key = 'test:product:123'
        
        def get_product(product_id):
            # 1. Vérifier le cache
            cached = redis_client.get(f'test:product:{product_id}')
            if cached:
                return json.loads(cached), 'cache_hit'
            
            # 2. Si pas en cache, chercher en "base de données" (simulé)
            product = {'id': product_id, 'name': 'Test Product', 'price': 99.99}
            
            # 3. Mettre en cache pour 5 minutes
            redis_client.setex(f'test:product:{product_id}', 300, json.dumps(product))
            
            return product, 'cache_miss'
        
        # Premier appel - cache miss
        product, status = get_product(123)
        assert status == 'cache_miss'
        assert product['name'] == 'Test Product'
        
        # Deuxième appel - cache hit
        product, status = get_product(123)
        assert status == 'cache_hit'
        
        # Cleanup
        redis_client.delete(cache_key)
    
    def test_rate_limiting_pattern(self, redis_client):
        """Test: Pattern Rate Limiting"""
        if redis_client is None:
            pytest.skip("Redis non disponible")
        
        def check_rate_limit(user_id, limit=5, window=60):
            key = f'test:rate_limit:{user_id}'
            
            current = redis_client.get(key)
            if current is None:
                redis_client.setex(key, window, 1)
                return True, 1
            
            current_count = int(current)
            if current_count >= limit:
                return False, current_count
            
            redis_client.incr(key)
            return True, current_count + 1
        
        # Simuler des requêtes
        for i in range(5):
            allowed, count = check_rate_limit('user123', limit=5)
            assert allowed == True
        
        # 6ème requête - devrait être bloquée
        allowed, count = check_rate_limit('user123', limit=5)
        assert allowed == False
        
        # Cleanup
        redis_client.delete('test:rate_limit:user123')
