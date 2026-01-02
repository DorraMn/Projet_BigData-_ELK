#!/usr/bin/env python3
"""
Script pour générer des données de log en temps réel pour aujourd'hui
Cela garantit que les dashboards Kibana affichent toujours des données récentes
"""
import json
import random
import requests
from datetime import datetime, timedelta

ES_URL = "http://localhost:9200"
INDEX_NAME = "logs-ecommerce"

# Données de référence
CATEGORIES = ["electronics", "clothing", "food", "books", "home", "sports"]
PAYMENT_TYPES = ["credit_card", "paypal", "debit_card", "bank_transfer"]
STATUSES_SUCCESS = ["success"] * 7 + ["failed"] * 3  # 70% succès
ERROR_CODES = ["", "", "", "", "", "", "INSUFFICIENT_FUNDS", "PAYMENT_DECLINED", "NETWORK_ERROR", "TIMEOUT"]
FIRST_NAMES = ["Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Isaac", "Julia"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

def generate_log_entry(timestamp):
    """Génère une entrée de log réaliste"""
    status = random.choice(STATUSES_SUCCESS)
    error_code = "" if status == "success" else random.choice([e for e in ERROR_CODES if e])
    
    return {
        "transaction_id": f"TXN{random.randint(10000, 99999)}",
        "@timestamp": timestamp.isoformat() + "Z",
        "amount": round(random.uniform(10, 500), 2),
        "payment_type": random.choice(PAYMENT_TYPES),
        "status": status,
        "category": random.choice(CATEGORIES),
        "customer_id": f"C{random.randint(100, 999)}",
        "customer_name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "error_code": error_code
    }

def inject_today_data(hours=24, logs_per_hour=10):
    """Injecte des données pour les dernières X heures"""
    print(f"🚀 Génération de données pour les {hours} dernières heures...")
    print(f"   ({logs_per_hour} logs/heure = {hours * logs_per_hour} logs total)")
    
    now = datetime.utcnow()
    count_success = 0
    count_error = 0
    
    for hour in range(hours):
        base_time = now - timedelta(hours=hours-hour)
        
        for _ in range(logs_per_hour):
            # Ajouter quelques minutes aléatoires
            timestamp = base_time + timedelta(minutes=random.randint(0, 59))
            log_entry = generate_log_entry(timestamp)
            
            try:
                response = requests.post(
                    f"{ES_URL}/{INDEX_NAME}/_doc",
                    json=log_entry,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 201]:
                    count_success += 1
                else:
                    count_error += 1
            except Exception as e:
                count_error += 1
        
        if (hour + 1) % 6 == 0:
            progress = int((hour + 1) / hours * 100)
            print(f"   📈 Progression: {progress}% ({count_success} logs injectés)")
    
    # Rafraîchir l'index
    requests.post(f"{ES_URL}/{INDEX_NAME}/_refresh")
    
    print(f"\n✅ Injection terminée:")
    print(f"   - Succès: {count_success}")
    print(f"   - Erreurs: {count_error}")
    
    return count_success

def verify_recent_data():
    """Vérifie les données récentes"""
    print(f"\n🔍 Vérification des données récentes...")
    
    # Compter les documents des dernières 24h
    now = datetime.utcnow()
    yesterday = now - timedelta(hours=24)
    
    query = {
        "query": {
            "range": {
                "@timestamp": {
                    "gte": yesterday.isoformat() + "Z"
                }
            }
        }
    }
    
    response = requests.post(
        f"{ES_URL}/{INDEX_NAME}/_count",
        json=query,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        count = response.json().get('count', 0)
        print(f"   📊 Documents des dernières 24h: {count}")
        
        # Afficher quelques exemples
        response = requests.get(
            f"{ES_URL}/{INDEX_NAME}/_search",
            json={
                "size": 3,
                "sort": [{"@timestamp": {"order": "desc"}}],
                "query": query["query"]
            }
        )
        
        if response.status_code == 200:
            hits = response.json().get('hits', {}).get('hits', [])
            if hits:
                print(f"\n   📝 Derniers logs:")
                for hit in hits[:3]:
                    source = hit['_source']
                    ts = source.get('@timestamp', 'N/A')[:19]
                    print(f"      - {ts} | {source.get('amount', 0)}€ | "
                          f"{source.get('status', 'N/A')} | {source.get('category', 'N/A')}")

if __name__ == "__main__":
    print("=" * 70)
    print("⚡ GÉNÉRATION DE DONNÉES EN TEMPS RÉEL POUR KIBANA")
    print("=" * 70)
    
    # Générer des données pour les dernières 24 heures (10 logs/heure)
    count = inject_today_data(hours=24, logs_per_hour=10)
    
    if count > 0:
        verify_recent_data()
        
        print("\n" + "=" * 70)
        print("✅ DONNÉES GÉNÉRÉES AVEC SUCCÈS")
        print("=" * 70)
        print("\n📌 Maintenant dans Kibana:")
        print("   1. Ouvrez: http://localhost:5601")
        print("   2. Allez dans Dashboard")
        print("   3. Sélectionnez la période 'Last 24 hours' ou 'Last 7 days'")
        print("   4. Les graphiques devraient afficher les nouvelles données!")
        print("\n💡 Astuce: Vous pouvez relancer ce script régulièrement")
        print("   pour maintenir des données fraîches dans vos dashboards.")
    else:
        print("\n❌ Échec de la génération de données")
