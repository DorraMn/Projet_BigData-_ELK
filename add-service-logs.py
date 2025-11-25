import requests
import random
from datetime import datetime, timedelta
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

PRODUCTS = [
    "Laptop Dell XPS 13", "iPhone 15 Pro", "Sony WH-1000XM5",
    "Samsung Galaxy S24", "MacBook Pro M3", "iPad Air",
    "AirPods Pro", "Nintendo Switch", "PlayStation 5",
    "Xbox Series X", "Canon EOS R6", "GoPro Hero 12",
    "Kindle Paperwhite", "Apple Watch Series 9", "Dyson V15"
]

CUSTOMERS = [
    "Marie Dubois", "Pierre Martin", "Sophie Bernard", "Luc Petit",
    "Emma Durand", "Thomas Moreau", "Julie Simon", "Antoine Laurent",
    "Camille Lefebvre", "Nicolas Roux", "Laura Fournier", "Alexandre Morel",
    "Léa Girard", "Maxime André", "Chloé Mercier", "Hugo Blanc"
]

PAYMENT_TYPES = ["credit_card", "debit_card", "paypal", "bank_transfer", "apple_pay"]
CATEGORIES = ["electronics", "clothing", "books", "home", "sports"]
STATUSES = ["success", "failed", "pending"]

MESSAGES = {
    "success": ["Transaction completed", "Payment processed", "Order confirmed"],
    "failed": ["Payment declined", "Insufficient funds", "Transaction timeout"],
    "pending": ["Payment processing", "Awaiting confirmation", "Pending approval"]
}

def generate_logs(count=300):
    """Génère et insère des logs avec le champ service"""
    print(f"🚀 Génération de {count} nouveaux logs...")
    
    now = datetime.utcnow()
    logs = []
    
    for i in range(count):
        days_ago = random.randint(0, 6)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        status = random.choice(STATUSES)
        service = random.choice(SERVICES)
        
        log = {
            "@timestamp": timestamp.isoformat() + "Z",
            "service": service,
            "status": status,
            "message": random.choice(MESSAGES[status]),
            "product": random.choice(PRODUCTS),
            "customer_name": random.choice(CUSTOMERS),
            "customer_id": f"C{random.randint(1, 100):03d}",
            "payment_type": random.choice(PAYMENT_TYPES),
            "category": random.choice(CATEGORIES),
            "amount": round(random.uniform(15, 999), 2),
            "transaction_id": f"TXN-{random.randint(100000, 999999)}",
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "response_time_ms": random.randint(50, 2000),
            "error_code": "" if status != "failed" else f"ERR_{random.randint(1000, 9999)}"
        }
        
        logs.append(log)
        
        # Insérer par batch de 50
        if len(logs) >= 50:
            insert_batch(logs)
            logs = []
    
    # Insérer les logs restants
    if logs:
        insert_batch(logs)
    
    print(f"✅ {count} logs insérés avec succès!")

def insert_batch(logs):
    """Insère un batch de logs"""
    bulk_data = []
    for log in logs:
        action = {"index": {}}
        bulk_data.append(json.dumps(action))
        bulk_data.append(json.dumps(log))
    
    bulk_body = "\n".join(bulk_data) + "\n"
    
    try:
        response = requests.post(
            f"{ELASTICSEARCH_URL}/_bulk",
            headers={"Content-Type": "application/x-ndjson"},
            data=bulk_body,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("errors"):
                errors = sum(1 for item in result.get("items", []) if item.get("create", {}).get("error"))
                print(f"⚠️  {errors} erreurs sur {len(logs)} logs")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")

def show_stats():
    """Affiche les statistiques"""
    print("\n📊 Statistiques:")
    
    try:
        # Total
        response = requests.get(f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_count")
        if response.status_code == 200:
            total = response.json()["count"]
            print(f"   Total: {total} logs")
        
        # Par service
        query = {
            "size": 0,
            "aggs": {
                "services": {
                    "terms": {"field": "service.keyword", "size": 10}
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
            print(f"\n   Par service:")
            for b in buckets:
                print(f"   • {b['key']}: {b['doc_count']}")
        
        # Par status
        query["aggs"] = {"statuses": {"terms": {"field": "status.keyword"}}}
        
        response = requests.post(
            f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search",
            headers={"Content-Type": "application/json"},
            json=query
        )
        
        if response.status_code == 200:
            buckets = response.json()["aggregations"]["statuses"]["buckets"]
            print(f"\n   Par status:")
            for b in buckets:
                print(f"   • {b['key']}: {b['doc_count']}")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("="*60)
    print("📦 Injection de logs avec services")
    print("="*60)
    
    generate_logs(300)
    show_stats()
    
    print("\n" + "="*60)
    print("✅ Terminé!")
    print("🔗 http://localhost:8000/search")
    print("="*60)
