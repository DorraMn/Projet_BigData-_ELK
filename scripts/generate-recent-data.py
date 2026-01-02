#!/usr/bin/env python3
"""
Script pour générer des données e-commerce avec des dates récentes
et les injecter dans Elasticsearch via l'API de upload de l'application
"""

import json
import random
from datetime import datetime, timedelta
import csv
import os

# Configuration
OUTPUT_DIR = "/tmp/logstream_test_data"
CSV_FILE = f"{OUTPUT_DIR}/ecommerce_recent.csv"
JSON_FILE = f"{OUTPUT_DIR}/ecommerce_recent.json"

# Données de référence
CATEGORIES = ["electronics", "books", "clothing", "home", "sports", "food"]
PAYMENT_TYPES = ["credit_card", "debit_card", "paypal", "bank_transfer"]
STATUSES = ["success", "failed"]
ERROR_CODES = ["", "PAYMENT_DECLINED", "INSUFFICIENT_FUNDS", "CARD_EXPIRED", "NETWORK_ERROR", "FRAUD_DETECTED", "TIMEOUT"]

# Noms de clients
CUSTOMER_NAMES = [
    "Alice Martin", "Bob Dupont", "Charlie Dubois", "Diana Bernard", "Eve Lambert",
    "Frank Moreau", "Grace Simon", "Henry Laurent", "Iris Petit", "Jack Roux"
]

def generate_transaction(transaction_id, timestamp):
    """Génère une transaction e-commerce"""
    status = random.choices(STATUSES, weights=[70, 30])[0]  # 70% success, 30% failed
    error_code = ""
    
    if status == "failed":
        error_code = random.choice([e for e in ERROR_CODES if e])
    
    return {
        "transaction_id": f"TXN{transaction_id:04d}",
        "@timestamp": timestamp.isoformat() + "Z",
        "amount": round(random.uniform(10, 500), 2),
        "payment_type": random.choice(PAYMENT_TYPES),
        "status": status,
        "category": random.choice(CATEGORIES),
        "customer_id": f"C{random.randint(1, 100):03d}",
        "customer_name": random.choice(CUSTOMER_NAMES),
        "error_code": error_code
    }

def main():
    """Génère les fichiers de test"""
    
    # Créer le répertoire de sortie
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 80)
    print("GÉNÉRATION DE DONNÉES E-COMMERCE RÉCENTES")
    print("=" * 80)
    
    # Générer 500 transactions sur les 7 derniers jours
    transactions = []
    start_date = datetime.utcnow() - timedelta(days=7)
    
    for i in range(1, 501):
        # Répartir les transactions sur 7 jours
        random_hours = random.randint(0, 7 * 24)
        timestamp = start_date + timedelta(hours=random_hours)
        transaction = generate_transaction(i, timestamp)
        transactions.append(transaction)
    
    # Trier par date
    transactions.sort(key=lambda x: x['@timestamp'])
    
    # Sauvegarder en JSON
    with open(JSON_FILE, 'w') as f:
        for t in transactions:
            f.write(json.dumps(t) + '\n')
    
    print(f"\n✅ Fichier JSON créé : {JSON_FILE}")
    print(f"   {len(transactions)} transactions générées")
    
    # Sauvegarder en CSV
    with open(CSV_FILE, 'w', newline='') as f:
        fieldnames = ["transaction_id", "@timestamp", "amount", "payment_type", "status", 
                     "category", "customer_id", "customer_name", "error_code"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)
    
    print(f"✅ Fichier CSV créé : {CSV_FILE}")
    
    # Statistiques
    success_count = sum(1 for t in transactions if t['status'] == 'success')
    failed_count = len(transactions) - success_count
    
    print(f"\n📊 Statistiques :")
    print(f"   Total : {len(transactions)} transactions")
    print(f"   Succès : {success_count} ({success_count/len(transactions)*100:.1f}%)")
    print(f"   Échecs : {failed_count} ({failed_count/len(transactions)*100:.1f}%)")
    print(f"   Période : {transactions[0]['@timestamp']} → {transactions[-1]['@timestamp']}")
    
    print(f"\n📝 Pour uploader les fichiers :")
    print(f"   1. Ouvrez http://localhost:8000/upload")
    print(f"   2. Uploadez : {CSV_FILE}")
    print(f"   3. Uploadez : {JSON_FILE}")
    print(f"   4. Les graphiques se mettront à jour automatiquement !")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
