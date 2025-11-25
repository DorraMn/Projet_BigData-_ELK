#!/usr/bin/env python3
"""
Script de test rapide pour le module database.py
Usage: python3 quick_test.py
"""

from database import init_databases, db_manager

def main():
    print("\n" + "="*60)
    print("  🧪 TEST RAPIDE DU MODULE DATABASE")
    print("="*60)
    
    # Initialiser
    print("\n1️⃣  Initialisation...")
    init_databases()
    
    # Vérifier les connexions
    print("\n2️⃣  Vérification des connexions:")
    print(f"   • MongoDB: {'✅ OK' if db_manager.mongo_connected else '❌ KO'}")
    print(f"   • Redis:   {'✅ OK' if db_manager.redis_connected else '❌ KO'}")
    
    # Test MongoDB
    if db_manager.mongo_connected:
        print("\n3️⃣  Test MongoDB:")
        col = db_manager.get_mongo_collection('uploads')
        if col is not None:
            count = col.count_documents({})
            print(f"   • Documents dans 'uploads': {count}")
            
            # Insérer un document test
            test_doc = {'_test': True, 'message': 'Quick test'}
            result = col.insert_one(test_doc)
            print(f"   • Document test inséré: {result.inserted_id}")
            
            # Supprimer le document test
            col.delete_one({'_test': True})
            print("   • Document test supprimé")
    
    # Test Redis
    if db_manager.redis_connected:
        print("\n4️⃣  Test Redis:")
        redis = db_manager.get_redis_client()
        if redis is not None:
            # SET/GET
            redis.set('quick_test', 'LogStream Studio', ex=30)
            value = redis.get('quick_test')
            print(f"   • SET/GET: {value}")
            
            # Compteur
            visits = redis.incr('quick_test:visits')
            print(f"   • Compteur: {visits}")
            
            # Cleanup
            redis.delete('quick_test', 'quick_test:visits')
            print("   • Clés nettoyées")
    
    # Health check
    print("\n5️⃣  Health Check:")
    health = db_manager.health_check()
    for service, status in health['services'].items():
        emoji = "✅" if status.get('status') == 'healthy' else "❌"
        print(f"   {emoji} {service}: {status.get('status', 'unknown')}")
    
    print("\n" + "="*60)
    print("  ✨ TEST TERMINÉ AVEC SUCCÈS")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
