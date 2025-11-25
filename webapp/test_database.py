#!/usr/bin/env python3
"""
LogStream Studio - Script de test complet du module database.py
Teste toutes les fonctionnalités avec rapport détaillé
"""

import sys
import time
from datetime import datetime
from database import DatabaseManager, init_databases


def print_section(title):
    """Affiche un titre de section"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_mongodb_operations(db_manager):
    """Teste les opérations MongoDB"""
    print_section("🧪 TEST MONGODB - Opérations CRUD")
    
    if not db_manager.mongo_connected:
        print("❌ MongoDB non connecté, tests ignorés")
        return False
    
    test_col = db_manager.get_mongo_collection('test_logs')
    if test_col is None:
        print("❌ Impossible de récupérer la collection")
        return False
    
    try:
        # CREATE
        print("\n1️⃣  INSERT - Insertion de documents...")
        test_docs = [
            {'level': 'info', 'message': 'Test log 1', 'timestamp': datetime.utcnow()},
            {'level': 'warning', 'message': 'Test log 2', 'timestamp': datetime.utcnow()},
            {'level': 'error', 'message': 'Test log 3', 'timestamp': datetime.utcnow()}
        ]
        result = test_col.insert_many(test_docs)
        print(f"   ✅ {len(result.inserted_ids)} documents insérés")
        
        # READ
        print("\n2️⃣  FIND - Lecture de documents...")
        count = test_col.count_documents({})
        print(f"   ✅ Total de documents: {count}")
        
        error_logs = test_col.count_documents({'level': 'error'})
        print(f"   ✅ Logs de niveau 'error': {error_logs}")
        
        # UPDATE
        print("\n3️⃣  UPDATE - Mise à jour de documents...")
        update_result = test_col.update_many(
            {'level': 'error'},
            {'$set': {'processed': True}}
        )
        print(f"   ✅ {update_result.modified_count} documents mis à jour")
        
        # DELETE
        print("\n4️⃣  DELETE - Suppression de la collection test...")
        test_col.drop()
        print("   ✅ Collection test supprimée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests MongoDB: {e}")
        return False


def test_redis_operations(db_manager):
    """Teste les opérations Redis"""
    print_section("🧪 TEST REDIS - Opérations Cache")
    
    if not db_manager.redis_connected:
        print("❌ Redis non connecté, tests ignorés")
        return False
    
    redis = db_manager.get_redis_client()
    if redis is None:
        print("❌ Impossible de récupérer le client Redis")
        return False
    
    try:
        # SET/GET
        print("\n1️⃣  SET/GET - Opérations basiques...")
        redis.set('test:string', 'LogStream Studio')
        value = redis.get('test:string')
        print(f"   ✅ SET/GET: {value}")
        
        # INCR
        print("\n2️⃣  INCR - Incrémentation...")
        redis.delete('test:counter')  # Reset
        for i in range(5):
            count = redis.incr('test:counter')
        print(f"   ✅ Compteur après 5 incrémentations: {count}")
        
        # EXPIRE
        print("\n3️⃣  EXPIRE - Expiration de clés...")
        redis.set('test:temp', 'temporary value', ex=2)
        print(f"   ✅ Clé créée avec TTL 2s")
        ttl = redis.ttl('test:temp')
        print(f"   ✅ TTL restant: {ttl}s")
        
        # HASH
        print("\n4️⃣  HASH - Structure de données...")
        redis.hset('test:user:1', mapping={
            'name': 'John Doe',
            'email': 'john@example.com',
            'role': 'admin'
        })
        user_data = redis.hgetall('test:user:1')
        print(f"   ✅ Hash créé: {user_data}")
        
        # LIST
        print("\n5️⃣  LIST - File d'attente...")
        redis.delete('test:queue')
        redis.rpush('test:queue', 'task1', 'task2', 'task3')
        queue_len = redis.llen('test:queue')
        print(f"   ✅ File créée avec {queue_len} tâches")
        
        # Cleanup
        print("\n6️⃣  CLEANUP - Nettoyage des clés de test...")
        keys_deleted = redis.delete(
            'test:string', 'test:counter', 'test:temp',
            'test:user:1', 'test:queue'
        )
        print(f"   ✅ {keys_deleted} clés supprimées")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests Redis: {e}")
        return False


def test_performance(db_manager):
    """Teste les performances"""
    print_section("⚡ TEST PERFORMANCE")
    
    # MongoDB Performance
    if db_manager.mongo_connected:
        print("\n📊 MongoDB - Performance insertion...")
        test_col = db_manager.get_mongo_collection('perf_test')
        if test_col is not None:
            start = time.time()
            
            # Insertion de 1000 documents
            docs = [
                {'index': i, 'data': f'test data {i}', 'timestamp': datetime.utcnow()}
                for i in range(1000)
            ]
            test_col.insert_many(docs)
            
            duration = time.time() - start
            print(f"   ✅ 1000 insertions en {duration:.3f}s ({1000/duration:.0f} ops/sec)")
            
            # Cleanup
            test_col.drop()
    
    # Redis Performance
    if db_manager.redis_connected:
        print("\n📊 Redis - Performance SET/GET...")
        redis = db_manager.get_redis_client()
        if redis is not None:
            start = time.time()
            
            # 1000 SET operations
            for i in range(1000):
                redis.set(f'perf:key:{i}', f'value{i}')
            
            duration = time.time() - start
            print(f"   ✅ 1000 SET en {duration:.3f}s ({1000/duration:.0f} ops/sec)")
            
            # 1000 GET operations
            start = time.time()
            for i in range(1000):
                redis.get(f'perf:key:{i}')
            
            duration = time.time() - start
            print(f"   ✅ 1000 GET en {duration:.3f}s ({1000/duration:.0f} ops/sec)")
            
            # Cleanup
            redis.delete(*[f'perf:key:{i}' for i in range(1000)])


def test_health_check(db_manager):
    """Teste le health check"""
    print_section("🏥 TEST HEALTH CHECK")
    
    health = db_manager.health_check()
    
    print(f"\n⏰ Timestamp: {health['timestamp']}")
    print("\n📋 Services:")
    
    for service, status in health['services'].items():
        status_emoji = "✅" if status.get('status') == 'healthy' else "❌"
        print(f"\n   {status_emoji} {service.upper()}")
        for key, value in status.items():
            if key != 'status':
                print(f"      • {key}: {value}")


def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "🚀"*35)
    print("  LOGSTREAM STUDIO - SUITE DE TESTS COMPLÈTE")
    print("🚀"*35)
    
    # Initialisation
    print_section("⚙️  INITIALISATION")
    db_manager = init_databases()
    
    results = {
        'mongodb_crud': False,
        'redis_ops': False,
        'performance': True,  # Always passes if no exception
        'health_check': True
    }
    
    # Tests MongoDB
    if db_manager.mongo_connected:
        results['mongodb_crud'] = test_mongodb_operations(db_manager)
    else:
        print("\n⚠️  MongoDB non disponible, tests ignorés")
    
    # Tests Redis
    if db_manager.redis_connected:
        results['redis_ops'] = test_redis_operations(db_manager)
    else:
        print("\n⚠️  Redis non disponible, tests ignorés")
    
    # Tests Performance
    try:
        test_performance(db_manager)
    except Exception as e:
        print(f"\n❌ Erreur tests performance: {e}")
        results['performance'] = False
    
    # Health Check
    try:
        test_health_check(db_manager)
    except Exception as e:
        print(f"\n❌ Erreur health check: {e}")
        results['health_check'] = False
    
    # Rapport final
    print_section("📊 RAPPORT FINAL")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    print("\n🎯 Résultats des tests:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name.replace('_', ' ').title()}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n📈 Taux de réussite: {passed_tests}/{total_tests} ({success_rate:.0f}%)")
    
    if success_rate == 100:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS ! 🎉")
    elif success_rate >= 50:
        print("\n⚠️  Certains tests ont échoué")
    else:
        print("\n❌ La majorité des tests ont échoué")
    
    # Fermeture
    print_section("🔌 FERMETURE DES CONNEXIONS")
    db_manager.close_all()
    
    print("\n✨ Tests terminés !\n")
    
    # Exit code
    sys.exit(0 if success_rate == 100 else 1)


if __name__ == "__main__":
    run_all_tests()
