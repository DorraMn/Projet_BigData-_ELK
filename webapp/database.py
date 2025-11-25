"""
LogStream Studio - Database Module
Gestion centralisée des connexions MongoDB et Redis
"""

import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import redis
from redis.exceptions import ConnectionError as RedisConnectionError
from datetime import datetime


class DatabaseManager:
    """Gestionnaire centralisé des connexions aux bases de données"""
    
    def __init__(self):
        # Configuration MongoDB
        self.mongo_uri = os.environ.get('MONGO_URI', 'mongodb://mongodb:27017')
        self.mongo_db_name = os.environ.get('MONGO_DB', 'monitoring')
        self.mongo_client = None
        self.mongo_db = None
        
        # Configuration Redis
        self.redis_host = os.environ.get('REDIS_HOST', 'redis')
        self.redis_port = int(os.environ.get('REDIS_PORT', '6379'))
        self.redis_db = int(os.environ.get('REDIS_DB', '0'))
        self.redis_client = None
        
        # État des connexions
        self.mongo_connected = False
        self.redis_connected = False
    
    def connect_mongodb(self):
        """
        Établit la connexion à MongoDB
        
        Returns:
            bool: True si connexion réussie, False sinon
        """
        try:
            print(f"🔄 Connexion à MongoDB: {self.mongo_uri}...")
            self.mongo_client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test de la connexion
            self.mongo_client.server_info()
            self.mongo_db = self.mongo_client[self.mongo_db_name]
            self.mongo_connected = True
            
            print(f"✅ MongoDB connecté: {self.mongo_db_name}")
            print(f"   Collections disponibles: {self.mongo_db.list_collection_names()}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.mongo_connected = False
            print(f"❌ Erreur de connexion MongoDB: {e}")
            return False
        except Exception as e:
            self.mongo_connected = False
            print(f"❌ Erreur MongoDB inattendue: {e}")
            return False
    
    def connect_redis(self):
        """
        Établit la connexion à Redis
        
        Returns:
            bool: True si connexion réussie, False sinon
        """
        try:
            print(f"🔄 Connexion à Redis: {self.redis_host}:{self.redis_port}...")
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                socket_connect_timeout=5,
                socket_timeout=5,
                decode_responses=True
            )
            
            # Test de la connexion
            self.redis_client.ping()
            self.redis_connected = True
            
            info = self.redis_client.info()
            print(f"✅ Redis connecté: v{info.get('redis_version', 'unknown')}")
            print(f"   Mémoire utilisée: {info.get('used_memory_human', 'unknown')}")
            return True
            
        except RedisConnectionError as e:
            self.redis_connected = False
            print(f"❌ Erreur de connexion Redis: {e}")
            return False
        except Exception as e:
            self.redis_connected = False
            print(f"❌ Erreur Redis inattendue: {e}")
            return False
    
    def connect_all(self):
        """
        Établit toutes les connexions aux bases de données
        
        Returns:
            dict: Statut de chaque connexion
        """
        print("\n" + "="*60)
        print("🚀 Initialisation des connexions base de données")
        print("="*60)
        
        mongo_status = self.connect_mongodb()
        redis_status = self.connect_redis()
        
        print("\n" + "="*60)
        print("📊 Résumé des connexions:")
        print(f"   MongoDB: {'✅ Connecté' if mongo_status else '❌ Déconnecté'}")
        print(f"   Redis:   {'✅ Connecté' if redis_status else '❌ Déconnecté'}")
        print("="*60 + "\n")
        
        return {
            'mongodb': {
                'connected': mongo_status,
                'uri': self.mongo_uri,
                'database': self.mongo_db_name
            },
            'redis': {
                'connected': redis_status,
                'host': self.redis_host,
                'port': self.redis_port
            }
        }
    
    def get_mongo_collection(self, collection_name):
        """
        Récupère une collection MongoDB
        
        Args:
            collection_name (str): Nom de la collection
            
        Returns:
            Collection: Collection MongoDB ou None si non connecté
        """
        if not self.mongo_connected or self.mongo_db is None:
            print(f"⚠️  MongoDB non connecté, impossible d'accéder à {collection_name}")
            return None
        
        return self.mongo_db[collection_name]
    
    def get_redis_client(self):
        """
        Récupère le client Redis
        
        Returns:
            Redis: Client Redis ou None si non connecté
        """
        if not self.redis_connected or self.redis_client is None:
            print("⚠️  Redis non connecté")
            return None
        
        return self.redis_client
    
    def health_check(self):
        """
        Vérifie l'état de santé des connexions
        
        Returns:
            dict: Statut détaillé de chaque service
        """
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'services': {}
        }
        
        # Check MongoDB
        if self.mongo_connected and self.mongo_client:
            try:
                self.mongo_client.server_info()
                db_stats = self.mongo_db.command('dbStats')
                health_status['services']['mongodb'] = {
                    'status': 'healthy',
                    'uri': self.mongo_uri,
                    'database': self.mongo_db_name,
                    'collections': db_stats.get('collections', 0),
                    'data_size_mb': round(db_stats.get('dataSize', 0) / (1024 * 1024), 2)
                }
            except Exception as e:
                health_status['services']['mongodb'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        else:
            health_status['services']['mongodb'] = {
                'status': 'disconnected'
            }
        
        # Check Redis
        if self.redis_connected and self.redis_client:
            try:
                self.redis_client.ping()
                info = self.redis_client.info()
                health_status['services']['redis'] = {
                    'status': 'healthy',
                    'host': self.redis_host,
                    'port': self.redis_port,
                    'version': info.get('redis_version', 'unknown'),
                    'used_memory': info.get('used_memory_human', 'unknown'),
                    'connected_clients': info.get('connected_clients', 0)
                }
            except Exception as e:
                health_status['services']['redis'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        else:
            health_status['services']['redis'] = {
                'status': 'disconnected'
            }
        
        return health_status
    
    def close_all(self):
        """Ferme toutes les connexions"""
        print("\n🔌 Fermeture des connexions...")
        
        if self.mongo_client:
            self.mongo_client.close()
            print("   ✅ MongoDB déconnecté")
        
        if self.redis_client:
            self.redis_client.close()
            print("   ✅ Redis déconnecté")
        
        print("👋 Toutes les connexions ont été fermées\n")


# Instance globale du gestionnaire de base de données
db_manager = DatabaseManager()


def init_databases():
    """
    Fonction d'initialisation à appeler au démarrage de l'application
    
    Returns:
        DatabaseManager: Instance du gestionnaire de base de données
    """
    db_manager.connect_all()
    return db_manager


# Test autonome du module
if __name__ == "__main__":
    print("🧪 Test du module database.py\n")
    
    # Initialiser les connexions
    manager = init_databases()
    
    # Test MongoDB
    if manager.mongo_connected:
        print("\n📝 Test MongoDB:")
        uploads_col = manager.get_mongo_collection('uploads')
        if uploads_col is not None:
            count = uploads_col.count_documents({})
            print(f"   Documents dans 'uploads': {count}")
    
    # Test Redis
    if manager.redis_connected:
        print("\n🔑 Test Redis:")
        redis_client = manager.get_redis_client()
        if redis_client is not None:
            redis_client.set('test_key', 'LogStream Studio', ex=60)
            value = redis_client.get('test_key')
            print(f"   Test SET/GET: {value}")
    
    # Health check
    print("\n🏥 Health Check:")
    health = manager.health_check()
    for service, status in health['services'].items():
        print(f"   {service}: {status['status']}")
    
    # Fermer les connexions
    manager.close_all()
