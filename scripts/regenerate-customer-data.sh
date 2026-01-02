#!/bin/bash

# Script pour regénérer les données avec les noms de clients
# Usage: ./regenerate-customer-data.sh [nombre_transactions]

NUM_TRANSACTIONS=${1:-100}

echo "🔄 Régénération des données avec noms de clients..."
echo "📊 Nombre de transactions: $NUM_TRANSACTIONS"

# Supprimer l'ancien index
echo "🗑️  Suppression de l'ancien index..."
curl -s -X DELETE "http://localhost:9200/logs-ecommerce-*" > /dev/null

# Générer les données avec Python
echo "📝 Génération des données..."
python3 << EOFPY
import json
from datetime import datetime, timedelta
import random

# Mapping des IDs vers les noms
customer_names = {
    "C001": "Alice Martin", "C002": "Bob Dubois", "C003": "Claire Bernard",
    "C004": "David Laurent", "C005": "Emma Petit", "C006": "François Moreau",
    "C007": "Gabrielle Simon", "C008": "Hugo Michel", "C009": "Isabelle Leroy",
    "C010": "Jacques Roux", "C011": "Karine Blanc", "C012": "Léa Garnier",
    "C013": "Marc Faure", "C014": "Nathalie Vincent", "C015": "Olivier Renard",
    "C016": "Pauline Girard", "C017": "Quentin André", "C018": "Rose Lambert",
    "C019": "Sophie Lefebvre", "C020": "Thomas Mercier", "C021": "Valérie Blanc",
    "C022": "William Guerin", "C023": "Xavier Rousseau", "C024": "Yves Boyer",
    "C025": "Zoé Dupont", "C026": "Antoine Lambert", "C027": "Brigitte Fontaine",
    "C028": "Camille Fontaine", "C029": "Denis Mercier", "C030": "Élise Renaud"
}

categories = ["electronics", "books", "clothing", "home"]
payment_types = ["credit_card", "paypal", "debit_card"]
error_codes = ["PAYMENT_DECLINED", "INSUFFICIENT_FUNDS", "CARD_EXPIRED", 
               "FRAUD_DETECTED", "NETWORK_ERROR", "TIMEOUT", "INVALID_CVV", "SYSTEM_ERROR"]

ndjson_lines = []
start_time = datetime(2025, 11, 25, 8, 0)

for i in range(1, $NUM_TRANSACTIONS + 1):
    tx_id = f"TXN{i:03d}"
    timestamp = (start_time + timedelta(minutes=i*10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Répartition des clients avec concentration sur les premiers
    if i <= 60:
        customer_idx = ((i - 1) % 6) + 1  # C001-C006
    else:
        customer_idx = ((i - 1) % 30) + 1  # C001-C030
    
    customer_id = f"C{customer_idx:03d}"
    customer_name = customer_names.get(customer_id, f"Client {customer_idx}")
    
    amount = round(23.5 + (i * 5.75) % 575, 2)
    category = categories[i % 4]
    payment_type = payment_types[i % 3]
    
    # 75% taux de succès
    if i % 4 == 0:
        status = "failed"
        error_code = error_codes[i % 8]
    else:
        status = "success"
        error_code = ""
    
    # Action de création
    ndjson_lines.append(json.dumps({"create": {"_index": "logs-ecommerce-2025.11.25"}}))
    
    # Document
    doc = {
        "@timestamp": timestamp,
        "transaction_id": tx_id,
        "amount": amount,
        "payment_type": payment_type,
        "status": status,
        "category": category,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "error_code": error_code
    }
    ndjson_lines.append(json.dumps(doc))

with open('/tmp/ecommerce-with-names.ndjson', 'w') as f:
    f.write('\n'.join(ndjson_lines) + '\n')

print(f"✅ Généré {len(ndjson_lines)//2} transactions")
EOFPY

# Injecter les données
echo "💉 Injection dans Elasticsearch..."
RESULT=$(curl -s -X POST "http://localhost:9200/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @/tmp/ecommerce-with-names.ndjson)

CREATED=$(echo $RESULT | jq '[.items[] | select(.create.result == "created")] | length')
ERRORS=$(echo $RESULT | jq '.errors')

if [ "$ERRORS" = "false" ]; then
  echo "✅ $CREATED transactions injectées avec succès!"
else
  echo "⚠️  Erreurs détectées lors de l'injection"
  echo $RESULT | jq '.items[] | select(.create.error)'
fi

# Statistiques
echo ""
echo "📊 Statistiques finales:"
curl -s "http://localhost:9200/logs-ecommerce-*/_search?size=0" \
  -H "Content-Type: application/json" \
  -d '{
    "aggs": {
      "total_customers": {"cardinality": {"field": "customer_id"}},
      "total_revenue": {
        "filter": {"term": {"status": "success"}},
        "aggs": {"sum_amount": {"sum": {"field": "amount"}}}
      },
      "top_customers": {"terms": {"field": "customer_name", "size": 5}}
    }
  }' | jq -r '"  • Total transactions: \(.hits.total.value)\n  • Clients uniques: \(.aggregations.total_customers.value)\n  • CA total: \(.aggregations.total_revenue.sum_amount.value | round)€\n\n🏆 Top 5 clients:\n" + (.aggregations.top_customers.buckets | map("  \(.doc_count)x - \(.key)") | join("\n"))'

echo ""
echo "🌐 Dashboard disponible sur:"
echo "http://localhost:5601/app/dashboards#/view/ecommerce-dashboard"
