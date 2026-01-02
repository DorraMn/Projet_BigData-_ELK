import requests
import random
import json

ELASTICSEARCH_URL = "http://localhost:9200"
INDEX_NAME = "logs-ecommerce-2025.11.25"

SERVICES = ["payment-api", "order-service", "inventory-service", "notification-service", "user-service", "analytics-service"]
PRODUCTS = ["Laptop Dell XPS 13", "iPhone 15 Pro", "Sony WH-1000XM5", "Samsung Galaxy S24", "MacBook Pro M3", "iPad Air", "AirPods Pro", "Nintendo Switch", "PlayStation 5", "Xbox Series X"]
MESSAGES = {
    "success": ["Transaction completed successfully", "Payment processed", "Order confirmed", "Delivery scheduled", "Item shipped"],
    "failed": ["Payment declined", "Insufficient funds", "Card expired", "Transaction timeout", "Authentication failed"],
    "pending": ["Payment processing", "Awaiting confirmation", "Order in queue", "Verification required"]
}

def fill_empty_fields():
    """Remplit les champs vides (product, message, service) dans les logs existants"""
    print("🔧 Mise à jour des logs avec champs vides...")
    
    # Rechercher les logs sans service
    query = {
        "size": 1000,
        "query": {
            "bool": {
                "should": [
                    {"bool": {"must_not": {"exists": {"field": "service"}}}},
                    {"bool": {"must_not": {"exists": {"field": "product"}}}},
                    {"bool": {"must_not": {"exists": {"field": "message"}}}}
                ]
            }
        }
    }
    
    response = requests.post(
        f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search",
        headers={"Content-Type": "application/json"},
        json=query
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur: {response.status_code}")
        return
    
    hits = response.json()["hits"]["hits"]
    print(f"📊 {len(hits)} logs à mettre à jour")
    
    # Mettre à jour chaque log
    updated = 0
    for hit in hits:
        doc_id = hit["_id"]
        source = hit["_source"]
        
        # Remplir les champs manquants
        updates = {}
        
        if not source.get("service"):
            updates["service"] = random.choice(SERVICES)
        
        if not source.get("product"):
            updates["product"] = random.choice(PRODUCTS)
        
        if not source.get("message"):
            status = source.get("status", "success")
            if status in MESSAGES:
                updates["message"] = random.choice(MESSAGES[status])
            else:
                updates["message"] = "Transaction processed"
        
        if updates:
            # Mettre à jour le document
            update_url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_update/{doc_id}"
            update_body = {"doc": updates}
            
            try:
                resp = requests.post(
                    update_url,
                    headers={"Content-Type": "application/json"},
                    json=update_body
                )
                if resp.status_code == 200:
                    updated += 1
            except Exception as e:
                print(f"⚠️  Erreur lors de la mise à jour: {e}")
    
    print(f"✅ {updated} logs mis à jour avec succès!")
    return updated

def verify_data():
    """Vérifie les données après mise à jour"""
    print("\n🔍 Vérification...")
    
    # Compter les logs avec service
    query = {"query": {"exists": {"field": "service"}}}
    response = requests.post(
        f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_count",
        headers={"Content-Type": "application/json"},
        json=query
    )
    if response.status_code == 200:
        count = response.json()["count"]
        print(f"   Logs avec service: {count}")
    
    # Compter les logs avec product
    query = {"query": {"exists": {"field": "product"}}}
    response = requests.post(
        f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_count",
        headers={"Content-Type": "application/json"},
        json=query
    )
    if response.status_code == 200:
        count = response.json()["count"]
        print(f"   Logs avec product: {count}")
    
    # Compter les logs avec message
    query = {"query": {"exists": {"field": "message"}}}
    response = requests.post(
        f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_count",
        headers={"Content-Type": "application/json"},
        json=query
    )
    if response.status_code == 200:
        count = response.json()["count"]
        print(f"   Logs avec message: {count}")
    
    # Afficher un exemple
    response = requests.post(
        f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search",
        headers={"Content-Type": "application/json"},
        json={"size": 1, "query": {"exists": {"field": "service"}}}
    )
    if response.status_code == 200:
        log = response.json()["hits"]["hits"][0]["_source"]
        print(f"\n📝 Exemple:")
        print(f"   Service: {log.get('service')}")
        print(f"   Product: {log.get('product')}")
        print(f"   Message: {log.get('message')}")

if __name__ == "__main__":
    print("="*60)
    print("🔄 Remplissage des champs vides")
    print("="*60)
    
    filled = fill_empty_fields()
    verify_data()
    
    print("\n" + "="*60)
    print("✅ Terminé!")
    print("="*60)
