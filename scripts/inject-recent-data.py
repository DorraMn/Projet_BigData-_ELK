#!/usr/bin/env python3
"""
Script pour injecter les données récentes dans Elasticsearch
"""
import json
import requests
from datetime import datetime

ES_URL = "http://localhost:9200"
INDEX_NAME = "logs-ecommerce"

def inject_json_file(filepath):
    """Injecte les données d'un fichier JSON dans Elasticsearch"""
    print(f"📥 Injection des données depuis {filepath}...")
    
    count_success = 0
    count_error = 0
    
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    doc = json.loads(line)
                    
                    # Indexer le document
                    response = requests.post(
                        f"{ES_URL}/{INDEX_NAME}/_doc",
                        json=doc,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code in [200, 201]:
                        count_success += 1
                    else:
                        count_error += 1
                        if count_error <= 3:
                            print(f"❌ Erreur ligne {line_num}: {response.status_code} - {response.text[:100]}")
                    
                    # Afficher la progression
                    if line_num % 100 == 0:
                        print(f"   ✓ {line_num} lignes traitées...")
                        
                except json.JSONDecodeError as e:
                    count_error += 1
                    if count_error <= 3:
                        print(f"❌ JSON invalide ligne {line_num}: {e}")
                except Exception as e:
                    count_error += 1
                    if count_error <= 3:
                        print(f"❌ Erreur ligne {line_num}: {e}")
    
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {filepath}")
        return False
    
    print(f"\n✅ Injection terminée:")
    print(f"   - Succès: {count_success}")
    print(f"   - Erreurs: {count_error}")
    
    # Rafraîchir l'index
    requests.post(f"{ES_URL}/{INDEX_NAME}/_refresh")
    
    return count_success > 0

def verify_data():
    """Vérifie les données dans Elasticsearch"""
    print(f"\n🔍 Vérification des données dans {INDEX_NAME}...")
    
    try:
        # Compter les documents
        response = requests.get(f"{ES_URL}/{INDEX_NAME}/_count")
        if response.status_code == 200:
            count = response.json().get('count', 0)
            print(f"   📊 Total documents: {count}")
        
        # Obtenir les derniers documents
        response = requests.get(
            f"{ES_URL}/{INDEX_NAME}/_search",
            json={
                "size": 3,
                "sort": [{"@timestamp": {"order": "desc"}}],
                "_source": ["@timestamp", "amount", "status", "category"]
            }
        )
        
        if response.status_code == 200:
            hits = response.json().get('hits', {}).get('hits', [])
            if hits:
                print(f"\n   📅 Derniers documents:")
                for hit in hits:
                    source = hit['_source']
                    print(f"      - {source.get('@timestamp', 'N/A')} | "
                          f"{source.get('amount', 'N/A')}€ | "
                          f"{source.get('status', 'N/A')} | "
                          f"{source.get('category', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

if __name__ == "__main__":
    json_file = "/tmp/logstream_test_data/ecommerce_recent.json"
    
    print("=" * 60)
    print("🚀 INJECTION DE DONNÉES RÉCENTES DANS ELASTICSEARCH")
    print("=" * 60)
    
    if inject_json_file(json_file):
        verify_data()
        print("\n✅ Les graphiques Kibana devraient maintenant afficher les données!")
        print("   👉 Rafraîchissez le dashboard: http://localhost:5601")
    else:
        print("\n❌ L'injection a échoué")
