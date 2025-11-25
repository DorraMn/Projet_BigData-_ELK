import requests
import random
from datetime import datetime, timedelta
import json

# Configuration
ELASTICSEARCH_URL = "http://localhost:9200"
INDEX_NAME = "logs-ecommerce-2025.11.25"

# Données de test
SERVICES = [
    "payment-api",
    "order-service",
    "inventory-service",
    "notification-service",
    "user-service",
    "analytics-service"
]

PRODUCTS = [
    "Laptop Dell XPS 13",
    "iPhone 15 Pro",
    "Sony WH-1000XM5",
    "Samsung Galaxy S24",
    "MacBook Pro M3",
    "iPad Air",
    "AirPods Pro",
    "Nintendo Switch",
    "PlayStation 5",
    "Xbox Series X",
    "Canon EOS R6",
    "GoPro Hero 12",
    "Kindle Paperwhite",
    "Apple Watch Series 9",
    "Dyson V15"
]

CUSTOMERS = [
    "Marie Dubois", "Pierre Martin", "Sophie Bernard", "Luc Petit",
    "Emma Durand", "Thomas Moreau", "Julie Simon", "Antoine Laurent",
    "Camille Lefebvre", "Nicolas Roux", "Laura Fournier", "Alexandre Morel",
    "Léa Girard", "Maxime André", "Chloé Mercier", "Hugo Blanc",
    "Manon Garcia", "Lucas Rodriguez", "Sarah Sanchez", "Julien Dupont"
]

PAYMENT_TYPES = ["credit_card", "debit_card", "paypal", "bank_transfer", "apple_pay"]
CATEGORIES = ["electronics", "clothing", "books", "home", "sports", "beauty"]
STATUSES = ["success", "failed", "pending"]

MESSAGES = {
    "success": [
        "Transaction completed successfully",
        "Payment processed",
        "Order confirmed",
        "Item shipped",
        "Delivery confirmed"
    ],
    "failed": [
        "Payment declined",
        "Insufficient funds",
        "Card expired",
        "Transaction timeout",
        "Authentication failed"
    ],
    "pending": [
        "Payment processing",
        "Awaiting confirmation",
        "Order in queue",
        "Verification required",
        "Pending approval"
    ]
}

def generate_log_entry(timestamp):
    """Génère une entrée de log aléatoire"""
    status = random.choice(STATUSES)
    service = random.choice(SERVICES)
    
    log = {
        "@timestamp": timestamp.isoformat() + "Z",
        "service": service,
        "status": status,
        "message": random.choice(MESSAGES[status]),
        "product": random.choice(PRODUCTS),
        "customer_name": random.choice(CUSTOMERS),
        "payment_type": random.choice(PAYMENT_TYPES),
        "category": random.choice(CATEGORIES),
        "amount": round(random.uniform(10, 1000), 2),
        "transaction_id": f"TXN-{random.randint(100000, 999999)}",
        "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
        "user_agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0"
        ]),
        "response_time_ms": random.randint(50, 2000)
    }
    
    return log

def bulk_insert_logs(num_logs=300):
    """Insère des logs en masse dans Elasticsearch"""
    print(f"🚀 Génération de {num_logs} logs avec champ service...")
    
    # Générer les logs sur les 7 derniers jours
    now = datetime.utcnow()
    bulk_data = []
    
    for i in range(num_logs):
        # Distribuer les logs sur les 7 derniers jours
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        log_entry = generate_log_entry(timestamp)
        
        # Format bulk API
        action = {"index": {"_index": INDEX_NAME}}
        bulk_data.append(json.dumps(action))
        bulk_data.append(json.dumps(log_entry))
    
    # Envoyer les données
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
                print("⚠️  Certaines insertions ont échoué")
                failed = sum(1 for item in result.get("items", []) if item.get("index", {}).get("error"))
                print(f"   Échecs: {failed}/{num_logs}")
            else:
                print(f"✅ {num_logs} logs insérés avec succès!")
                
            # Afficher les statistiques
            print(f"\n📊 Statistiques:")
            print(f"   - Services: {', '.join(SERVICES)}")
            print(f"   - Produits: {len(PRODUCTS)} types")
            print(f"   - Clients: {len(CUSTOMERS)} personnes")
            print(f"   - Période: 7 derniers jours")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(response.text[:500])
    
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion: {e}")

def verify_data():
    """Vérifie les données insérées"""
    print("\n🔍 Vérification des données...")
    
    try:
        # Compter les logs
        response = requests.get(f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_count")
        if response.status_code == 200:
            count = response.json()["count"]
            print(f"✅ Total des logs: {count}")
        
        # Compter par service
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
            print(f"\n📊 Logs par service:")
            for bucket in buckets:
                print(f"   - {bucket['key']}: {bucket['doc_count']} logs")
        
        # Compter par status
        query["aggs"] = {
            "statuses": {
                "terms": {
                    "field": "status.keyword",
                    "size": 10
                }
            }
        }
        
        response = requests.post(
            f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search",
            headers={"Content-Type": "application/json"},
            json=query
        )
        
        if response.status_code == 200:
            buckets = response.json()["aggregations"]["statuses"]["buckets"]
            print(f"\n📊 Logs par status:")
            for bucket in buckets:
                print(f"   - {bucket['key']}: {bucket['doc_count']} logs")
    
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

if __name__ == "__main__":
    print("="*60)
    print("📦 Injection de données avec champ service")
    print("="*60)
    
    # Insérer 300 nouveaux logs
    bulk_insert_logs(300)
    
    # Vérifier les données
    verify_data()
    
    print("\n" + "="*60)
    print("✅ Injection terminée!")
    print("🌐 Testez la recherche: http://localhost:8000/search")
    print("="*60)
