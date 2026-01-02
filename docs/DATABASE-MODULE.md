# 📚 Module Database - Documentation

## 🎯 Objectif

Le module `database.py` centralise la gestion des connexions MongoDB et Redis pour LogStream Studio. Il fournit une interface unifiée, des tests de connexion automatiques et un health check complet.

## 🏗️ Architecture

```
database.py
├── DatabaseManager (classe principale)
│   ├── connect_mongodb()      # Connexion MongoDB
│   ├── connect_redis()         # Connexion Redis
│   ├── connect_all()           # Connexion à toutes les DB
│   ├── get_mongo_collection()  # Récupérer une collection
│   ├── get_redis_client()      # Récupérer le client Redis
│   ├── health_check()          # Vérifier l'état des services
│   └── close_all()             # Fermer toutes les connexions
│
└── init_databases() (fonction globale)
```

## 🚀 Installation

### 1. Prérequis

```bash
pip install pymongo redis
```

### 2. Variables d'environnement

Créez un fichier `.env` à partir de `.env.example` :

```bash
cp .env.example .env
```

Variables disponibles :
- `MONGO_URI` : URI de connexion MongoDB (défaut: `mongodb://mongodb:27017`)
- `MONGO_DB` : Nom de la base de données (défaut: `monitoring`)
- `REDIS_HOST` : Hôte Redis (défaut: `redis`)
- `REDIS_PORT` : Port Redis (défaut: `6379`)
- `REDIS_DB` : Numéro de DB Redis (défaut: `0`)

## 💻 Utilisation

### Option 1 : Utilisation simple

```python
from database import init_databases, db_manager

# Initialiser les connexions au démarrage
init_databases()

# Utiliser MongoDB
uploads_col = db_manager.get_mongo_collection('uploads')
if uploads_col is not None:
    uploads_col.insert_one({'filename': 'test.csv', 'status': 'processed'})

# Utiliser Redis
redis_client = db_manager.get_redis_client()
if redis_client is not None:
    redis_client.set('key', 'value', ex=60)
```

### Option 2 : Intégration Flask

```python
from flask import Flask
from database import init_databases, db_manager

app = Flask(__name__)

# Initialiser au démarrage
init_databases()

@app.route('/api/save', methods=['POST'])
def save_data():
    # Accéder à MongoDB
    col = db_manager.get_mongo_collection('logs')
    col.insert_one({'message': 'Log entry'})
    return {'success': True}

@app.route('/api/cache/<key>')
def get_cache(key):
    # Accéder à Redis
    redis = db_manager.get_redis_client()
    value = redis.get(key)
    return {'value': value}

if __name__ == '__main__':
    try:
        app.run()
    finally:
        db_manager.close_all()
```

### Option 3 : Instance personnalisée

```python
from database import DatabaseManager

# Créer une instance personnalisée
db = DatabaseManager()
db.connect_all()

# Utiliser les connexions
mongo_col = db.get_mongo_collection('custom_collection')
redis = db.get_redis_client()

# Fermer les connexions
db.close_all()
```

## 🧪 Tests

### Test du module en standalone

```bash
# Dans le conteneur webapp
docker exec webapp python3 database.py

# Ou localement
python3 webapp/database.py
```

Sortie attendue :
```
🧪 Test du module database.py

============================================================
🚀 Initialisation des connexions base de données
============================================================
🔄 Connexion à MongoDB: mongodb://mongodb:27017...
✅ MongoDB connecté: monitoring
   Collections disponibles: ['uploads', 'search_history']
🔄 Connexion à Redis: redis:6379...
✅ Redis connecté: v7.4.7
   Mémoire utilisée: 1014.16K

============================================================
📊 Résumé des connexions:
   MongoDB: ✅ Connecté
   Redis:   ✅ Connecté
============================================================

📝 Test MongoDB:
   Documents dans 'uploads': 4

🔑 Test Redis:
   Test SET/GET: LogStream Studio

🏥 Health Check:
   mongodb: healthy
   redis: healthy
```

### Test avec l'application exemple

```bash
# Lancer l'application exemple
python3 webapp/example_app.py

# Tester les endpoints
curl http://localhost:5000/db-test
curl http://localhost:5000/health
curl http://localhost:5000/cache-example/test-key
```

## 📊 API Reference

### DatabaseManager

#### `__init__()`
Initialise le gestionnaire avec les variables d'environnement.

#### `connect_mongodb() -> bool`
Établit la connexion MongoDB.

**Returns:**
- `True` si connexion réussie
- `False` en cas d'erreur

#### `connect_redis() -> bool`
Établit la connexion Redis.

**Returns:**
- `True` si connexion réussie
- `False` en cas d'erreur

#### `connect_all() -> dict`
Établit toutes les connexions.

**Returns:**
```python
{
    'mongodb': {'connected': True, 'uri': '...', 'database': '...'},
    'redis': {'connected': True, 'host': '...', 'port': 6379}
}
```

#### `get_mongo_collection(collection_name: str) -> Collection | None`
Récupère une collection MongoDB.

**Args:**
- `collection_name`: Nom de la collection

**Returns:**
- `Collection` si connecté
- `None` si non connecté

#### `get_redis_client() -> Redis | None`
Récupère le client Redis.

**Returns:**
- `Redis` si connecté
- `None` si non connecté

#### `health_check() -> dict`
Vérifie l'état de santé des services.

**Returns:**
```python
{
    'timestamp': '2025-11-25T...',
    'services': {
        'mongodb': {
            'status': 'healthy',
            'uri': '...',
            'database': '...',
            'collections': 2,
            'data_size_mb': 0.5
        },
        'redis': {
            'status': 'healthy',
            'host': 'redis',
            'port': 6379,
            'version': '7.4.7',
            'used_memory': '1014.16K',
            'connected_clients': 1
        }
    }
}
```

#### `close_all()`
Ferme toutes les connexions.

## 🔒 Bonnes pratiques

### 1. Gestion des erreurs

```python
# Toujours vérifier si la connexion existe
col = db_manager.get_mongo_collection('uploads')
if col is not None:
    # Utiliser la collection
    col.insert_one({...})
else:
    # Gérer l'absence de connexion
    return {'error': 'Database not available'}, 503
```

### 2. Fermeture des connexions

```python
# Dans un script standalone
try:
    db_manager.connect_all()
    # ... utiliser les connexions
finally:
    db_manager.close_all()
```

### 3. Timeouts

```python
# Les timeouts sont configurés par défaut
# MongoDB: 5000ms
# Redis: 5s

# Pour les modifier :
import os
os.environ['MONGO_TIMEOUT'] = '10000'
```

## 🐛 Dépannage

### MongoDB ne se connecte pas

```bash
# Vérifier que le conteneur MongoDB est démarré
docker ps | grep mongodb

# Vérifier les logs
docker logs mongodb

# Tester la connexion
docker exec mongodb mongosh --eval "db.runCommand({ping: 1})"
```

### Redis ne se connecte pas

```bash
# Vérifier que le conteneur Redis est démarré
docker ps | grep redis

# Vérifier les logs
docker logs redis

# Tester la connexion
docker exec redis redis-cli ping
```

### Variables d'environnement non chargées

```bash
# Vérifier les variables dans le conteneur
docker exec webapp env | grep MONGO
docker exec webapp env | grep REDIS
```

## 📈 Métriques et monitoring

Le module fournit des métriques détaillées via `health_check()` :

- **MongoDB** : Nombre de collections, taille des données
- **Redis** : Version, mémoire utilisée, clients connectés
- **Timestamp** : Date/heure du check

## 🔗 Intégration avec l'application existante

Pour migrer l'application actuelle vers le nouveau module :

```python
# Ancien code (app.py)
mongo_client = pymongo.MongoClient(MONGO_URI)
uploads_col = mongo_db['uploads']

# Nouveau code (avec database.py)
from database import init_databases, db_manager

init_databases()
uploads_col = db_manager.get_mongo_collection('uploads')
```

## 📝 Notes

- Le module utilise un pattern Singleton via `db_manager`
- Les connexions sont thread-safe
- Les timeouts sont configurables via variables d'environnement
- Le health check est disponible pour Kubernetes/Docker health probes

## 🎓 Exemples avancés

### Cache with fallback

```python
def get_data_cached(key):
    redis = db_manager.get_redis_client()
    
    # Essayer le cache
    if redis is not None:
        cached = redis.get(f'cache:{key}')
        if cached:
            return cached
    
    # Fallback sur MongoDB
    col = db_manager.get_mongo_collection('data')
    if col is not None:
        data = col.find_one({'key': key})
        
        # Mettre en cache pour la prochaine fois
        if redis is not None and data:
            redis.set(f'cache:{key}', data['value'], ex=300)
        
        return data['value'] if data else None
```

### Bulk operations

```python
def save_logs_batch(logs):
    col = db_manager.get_mongo_collection('logs')
    if col is None:
        return False
    
    result = col.insert_many(logs)
    return len(result.inserted_ids) == len(logs)
```

---

**Version:** 1.0.0  
**Dernière mise à jour:** 25 novembre 2025  
**LogStream Studio** ⚡
