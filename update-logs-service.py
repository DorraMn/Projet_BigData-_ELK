import requests
import random
import json

# Configuration
ELASTICSEARCH_URL = "http://localhost:9200"
INDEX_NAME = "logs-ecommerce-2025.11.25"

SERVICES = [
    "payment-api",
    "order-service",
    "inventory-service",
    "notification-service",
    "user-service",
    "analytics-service"
]

def update_existing_logs():
    """Met à jour tous les logs existants pour ajouter le champ service"""
    print("🔄 Mise à jour des logs existants avec le champ service...")
    
    try:
        # Récupérer tous les logs
        response = requests.post(
            f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search",
            headers={"Content-Type": "application/json"},
            json={
                "size": 1000,
                "query": {"match_all": {}}
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Erreur lors de la récupération: {response.status_code}")
            return
        
        hits = response.json()["hits"]["hits"]
        total = len(hits)
        print(f"📊 {total} logs trouvés")
        
        # Préparer les mises à jour en bulk
        bulk_data = []
        
        for hit in hits:
            doc_id = hit["_id"]
            source = hit["_source"]
            
            # Choisir un service aléatoire
            service = random.choice(SERVICES)
            
            # Ajouter des champs supplémentaires
            source["service"] = service
            source["transaction_id"] = source.get("transaction_id", f"TXN-{random.randint(100000, 999999)}")
            source["ip_address"] = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            source["response_time_ms"] = random.randint(50, 2000)
            
            # Messages selon le status
            if source.get("status") == "success":
                source["message"] = random.choice([
                    "Transaction completed successfully",
                    "Payment processed",
                    "Order confirmed"
                ])
            elif source.get("status") == "failed":
                source["message"] = random.choice([
                    "Payment declined",
                    "Insufficient funds",
                    "Transaction timeout"
                ])
            else:
                source["message"] = "Transaction pending"
            
            # Format bulk update
            action = {"update": {"_index": INDEX_NAME, "_id": doc_id}}
            bulk_data.append(json.dumps(action))
            bulk_data.append(json.dumps({"doc": source}))
        
        # Envoyer les mises à jour
        bulk_body = "\n".join(bulk_data) + "\n"
        
        response = requests.post(
            f"{ELASTICSEARCH_URL}/_bulk",
            headers={"Content-Type": "application/x-ndjson"},
            data=bulk_body,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("errors"):
                print("⚠️  Certaines mises à jour ont échoué")
            else:
                print(f"✅ {total} logs mis à jour avec succès!")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(response.text[:500])
    
    except Exception as e:
        print(f"❌ Erreur: {e}")

def verify_updates():
    """Vérifie que les logs ont bien été mis à jour"""
    print("\n🔍 Vérification des mises à jour...")
    
    try:
        # Compter les logs par service
        query = {
            "size": 0,
            "aggs": {
                "services": {
                    "terms": {
                        "field": "service.keyword",
                        "size": 10
                    }
                }
            }
        }
        
        response = requests.post(
            f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search",
            headers={"Content-Type": "application/json"},
            json=query
        )
        
        if response.status_code == 200:
            buckets = response.json()["aggregations"]["services"]["buckets"]
            print(f"\n📊 Distribution par service:")
            for bucket in buckets:
                print(f"   - {bucket['key']}: {bucket['doc_count']} logs")
        
        # Afficher un exemple de log mis à jour
        response = requests.post(
            f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search",
            headers={"Content-Type": "application/json"},
            json={"size": 1, "query": {"match_all": {}}}
        )
        
        if response.status_code == 200:
            log = response.json()["hits"]["hits"][0]["_source"]
            print(f"\n📝 Exemple de log mis à jour:")
            print(f"   - Service: {log.get('service', 'N/A')}")
            print(f"   - Message: {log.get('message', 'N/A')}")
            print(f"   - Transaction ID: {log.get('transaction_id', 'N/A')}")
            print(f"   - Response Time: {log.get('response_time_ms', 'N/A')} ms")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🔧 Mise à jour des logs avec champ service")
    print("="*60)
    
    update_existing_logs()
    verify_updates()
    
    print("\n" + "="*60)
    print("✅ Mise à jour terminée!")
    print("🌐 Testez la recherche: http://localhost:8000/search")
    print("="*60)
