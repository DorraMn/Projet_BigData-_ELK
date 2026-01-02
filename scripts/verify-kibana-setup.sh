#!/bin/bash

echo "=========================================="
echo "   RÉSUMÉ KIBANA E-COMMERCE DASHBOARD"
echo "=========================================="
echo ""

# Vérifier Elasticsearch
echo "🔍 Vérification Elasticsearch..."
ES_STATUS=$(curl -s http://localhost:9200/_cluster/health | jq -r '.status')
echo "   Status: ${ES_STATUS}"

# Vérifier l'index
INDEX_COUNT=$(curl -s http://localhost:9200/logs-ecommerce-*/_count | jq -r '.count')
echo "   Documents dans logs-ecommerce-*: ${INDEX_COUNT}"
echo ""

# Vérifier Kibana
echo "🔍 Vérification Kibana..."
KIBANA_STATUS=$(curl -s http://localhost:5601/api/status | jq -r '.status.overall.level')
echo "   Status: ${KIBANA_STATUS}"
echo ""

# Data View
echo "📊 Data View:"
curl -s http://localhost:5601/api/data_views -H "kbn-xsrf: true" 2>/dev/null | \
  jq -r '.data_view[] | select(.title == "logs-*") | "   - Title: \(.title)\n   - ID: \(.id)\n   - Time Field: \(.timeFieldName)"'
echo ""

# Dashboard
echo "📊 Dashboard:"
curl -s "http://localhost:5601/api/saved_objects/_find?type=dashboard&search=E-Commerce" \
  -H "kbn-xsrf: true" 2>/dev/null | \
  jq -r '.saved_objects[0] | "   - Title: \(.attributes.title)\n   - ID: \(.id)\n   - Description: \(.attributes.description)"'
echo ""

# Visualisations
echo "📈 Visualisations:"
curl -s "http://localhost:5601/api/saved_objects/_find?type=visualization&search=*" \
  -H "kbn-xsrf: true" 2>/dev/null | \
  jq -r '.saved_objects[] | "   - \(.attributes.title) (\(.id))"' | \
  grep -E "(Transactions|Erreurs|paiement)" | sort -u
echo ""

# Statistiques des données
echo "📊 Statistiques des données:"
curl -s "http://localhost:9200/logs-ecommerce-*/_search?size=0" \
  -H "Content-Type: application/json" \
  -d '{
    "aggs": {
      "total": { "value_count": { "field": "_id" } },
      "success_count": {
        "filter": { "term": { "status": "success" } }
      },
      "failed_count": {
        "filter": { "term": { "status": "failed" } }
      },
      "total_amount": {
        "sum": { "field": "amount" }
      },
      "avg_amount": {
        "avg": { "field": "amount" }
      }
    }
  }' 2>/dev/null | jq -r '
    "   Total transactions: \(.hits.total.value)",
    "   Transactions réussies: \(.aggregations.success_count.doc_count)",
    "   Transactions échouées: \(.aggregations.failed_count.doc_count)",
    "   Montant total: \(.aggregations.total_amount.value | round)€",
    "   Montant moyen: \(.aggregations.avg_amount.value | round)€"
  '
echo ""

# URLs d'accès
echo "=========================================="
echo "🌐 ACCÈS"
echo "=========================================="
echo ""
echo "Kibana Dashboard:"
echo "  http://localhost:5601/app/dashboards#/view/bb68e670-c9f5-11f0-b9de-2327bf14c31d"
echo ""
echo "Kibana Discover:"
echo "  http://localhost:5601/app/discover#/?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-24h,to:now))&_a=(columns:!(_source),filters:!(),index:'logs-*',interval:auto,query:(language:kuery,query:''),sort:!(!('@timestamp',desc)))"
echo ""
echo "Elasticsearch Index:"
echo "  http://localhost:9200/logs-ecommerce-2025.11.25"
echo ""

echo "=========================================="
echo "📦 FICHIERS GÉNÉRÉS"
echo "=========================================="
echo ""
ls -lh /home/dorrah/Bureau/projet/ | grep -E "(ecommerce|KIBANA)" | awk '{print "  " $9 " (" $5 ")"}'
echo ""

echo "=========================================="
echo "✅ DASHBOARD PRÊT À L'EMPLOI!"
echo "=========================================="
