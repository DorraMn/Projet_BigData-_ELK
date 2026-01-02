#!/bin/bash

# Configuration Kibana
KIBANA_URL="http://localhost:5601"
KIBANA_HEADERS="Content-Type: application/json"
KIBANA_HEADERS_NDJSON="Content-Type: application/x-ndjson"
KIBANA_KBN="kbn-xsrf: true"

echo "=========================================="
echo "Configuration Kibana E-Commerce Dashboard"
echo "=========================================="
echo ""

# 1. Créer le Data View (Index Pattern) logs-*
echo "📊 Création du Data View 'logs-*'..."
curl -X POST "${KIBANA_URL}/api/data_views/data_view" \
  -H "${KIBANA_HEADERS}" \
  -H "${KIBANA_KBN}" \
  -d '{
    "data_view": {
      "title": "logs-*",
      "name": "E-Commerce Logs",
      "timeFieldName": "@timestamp"
    }
  }' 2>/dev/null | jq -r '.data_view.id' > /tmp/dataview_id.txt

DATAVIEW_ID=$(cat /tmp/dataview_id.txt)
echo "✅ Data View créé avec ID: ${DATAVIEW_ID}"
echo ""

sleep 2

# 2. Créer Visualisation 1: Courbe des transactions/heure (Line Chart)
echo "📈 Création de la visualisation 'Transactions par heure'..."
VIS1_RESPONSE=$(curl -X POST "${KIBANA_URL}/api/saved_objects/visualization" \
  -H "${KIBANA_HEADERS}" \
  -H "${KIBANA_KBN}" \
  -d "{
    \"attributes\": {
      \"title\": \"Transactions par heure\",
      \"visState\": \"{\\\"title\\\":\\\"Transactions par heure\\\",\\\"type\\\":\\\"line\\\",\\\"aggs\\\":[{\\\"id\\\":\\\"1\\\",\\\"enabled\\\":true,\\\"type\\\":\\\"count\\\",\\\"params\\\":{},\\\"schema\\\":\\\"metric\\\"},{\\\"id\\\":\\\"2\\\",\\\"enabled\\\":true,\\\"type\\\":\\\"date_histogram\\\",\\\"params\\\":{\\\"field\\\":\\\"@timestamp\\\",\\\"timeRange\\\":{\\\"from\\\":\\\"now-24h\\\",\\\"to\\\":\\\"now\\\"},\\\"useNormalizedEsInterval\\\":true,\\\"scaleMetricValues\\\":false,\\\"interval\\\":\\\"h\\\",\\\"drop_partials\\\":false,\\\"min_doc_count\\\":1,\\\"extended_bounds\\\":{}},\\\"schema\\\":\\\"segment\\\"}],\\\"params\\\":{\\\"type\\\":\\\"line\\\",\\\"grid\\\":{\\\"categoryLines\\\":false},\\\"categoryAxes\\\":[{\\\"id\\\":\\\"CategoryAxis-1\\\",\\\"type\\\":\\\"category\\\",\\\"position\\\":\\\"bottom\\\",\\\"show\\\":true,\\\"style\\\":{},\\\"scale\\\":{\\\"type\\\":\\\"linear\\\"},\\\"labels\\\":{\\\"show\\\":true,\\\"filter\\\":true,\\\"truncate\\\":100},\\\"title\\\":{}}],\\\"valueAxes\\\":[{\\\"id\\\":\\\"ValueAxis-1\\\",\\\"name\\\":\\\"LeftAxis-1\\\",\\\"type\\\":\\\"value\\\",\\\"position\\\":\\\"left\\\",\\\"show\\\":true,\\\"style\\\":{},\\\"scale\\\":{\\\"type\\\":\\\"linear\\\",\\\"mode\\\":\\\"normal\\\"},\\\"labels\\\":{\\\"show\\\":true,\\\"rotate\\\":0,\\\"filter\\\":false,\\\"truncate\\\":100},\\\"title\\\":{\\\"text\\\":\\\"Count\\\"}}],\\\"seriesParams\\\":[{\\\"show\\\":true,\\\"type\\\":\\\"line\\\",\\\"mode\\\":\\\"normal\\\",\\\"data\\\":{\\\"label\\\":\\\"Count\\\",\\\"id\\\":\\\"1\\\"},\\\"valueAxis\\\":\\\"ValueAxis-1\\\",\\\"drawLinesBetweenPoints\\\":true,\\\"lineWidth\\\":2,\\\"interpolate\\\":\\\"linear\\\",\\\"showCircles\\\":true}],\\\"addTooltip\\\":true,\\\"addLegend\\\":true,\\\"legendPosition\\\":\\\"right\\\",\\\"times\\\":[],\\\"addTimeMarker\\\":false,\\\"thresholdLine\\\":{\\\"show\\\":false,\\\"value\\\":10,\\\"width\\\":1,\\\"style\\\":\\\"full\\\",\\\"color\\\":\\\"#E7664C\\\"}}}\",
      \"uiStateJSON\": \"{}\",
      \"description\": \"Nombre de transactions par heure\",
      \"version\": 1,
      \"kibanaSavedObjectMeta\": {
        \"searchSourceJSON\": \"{\\\"index\\\":\\\"${DATAVIEW_ID}\\\",\\\"query\\\":{\\\"query\\\":\\\"\\\",\\\"language\\\":\\\"kuery\\\"},\\\"filter\\\":[]}\"
      }
    }
  }" 2>/dev/null)

VIS1_ID=$(echo $VIS1_RESPONSE | jq -r '.id')
echo "✅ Visualisation 1 créée avec ID: ${VIS1_ID}"
echo ""

sleep 2

# 3. Créer Visualisation 2: Top 10 erreurs (Data Table)
echo "📋 Création de la visualisation 'Top 10 Erreurs'..."
VIS2_RESPONSE=$(curl -X POST "${KIBANA_URL}/api/saved_objects/visualization" \
  -H "${KIBANA_HEADERS}" \
  -H "${KIBANA_KBN}" \
  -d "{
    \"attributes\": {
      \"title\": \"Top 10 Erreurs\",
      \"visState\": \"{\\\"title\\\":\\\"Top 10 Erreurs\\\",\\\"type\\\":\\\"table\\\",\\\"aggs\\\":[{\\\"id\\\":\\\"1\\\",\\\"enabled\\\":true,\\\"type\\\":\\\"count\\\",\\\"params\\\":{},\\\"schema\\\":\\\"metric\\\"},{\\\"id\\\":\\\"2\\\",\\\"enabled\\\":true,\\\"type\\\":\\\"terms\\\",\\\"params\\\":{\\\"field\\\":\\\"error_code.keyword\\\",\\\"orderBy\\\":\\\"1\\\",\\\"order\\\":\\\"desc\\\",\\\"size\\\":10,\\\"otherBucket\\\":false,\\\"otherBucketLabel\\\":\\\"Other\\\",\\\"missingBucket\\\":false,\\\"missingBucketLabel\\\":\\\"Missing\\\"},\\\"schema\\\":\\\"bucket\\\"}],\\\"params\\\":{\\\"perPage\\\":10,\\\"showPartialRows\\\":false,\\\"showMetricsAtAllLevels\\\":false,\\\"sort\\\":{\\\"columnIndex\\\":null,\\\"direction\\\":null},\\\"showTotal\\\":false,\\\"totalFunc\\\":\\\"sum\\\",\\\"percentageCol\\\":\\\"\\\"}}\",
      \"uiStateJSON\": \"{\\\"vis\\\":{\\\"params\\\":{\\\"sort\\\":{\\\"columnIndex\\\":null,\\\"direction\\\":null}}}}\",
      \"description\": \"Les 10 erreurs les plus fréquentes\",
      \"version\": 1,
      \"kibanaSavedObjectMeta\": {
        \"searchSourceJSON\": \"{\\\"index\\\":\\\"${DATAVIEW_ID}\\\",\\\"query\\\":{\\\"query\\\":\\\"status:failed\\\",\\\"language\\\":\\\"kuery\\\"},\\\"filter\\\":[]}\"
      }
    }
  }" 2>/dev/null)

VIS2_ID=$(echo $VIS2_RESPONSE | jq -r '.id')
echo "✅ Visualisation 2 créée avec ID: ${VIS2_ID}"
echo ""

sleep 2

# 4. Créer Visualisation 3: Répartition par type de paiement (Pie Chart)
echo "🥧 Création de la visualisation 'Répartition par type de paiement'..."
VIS3_RESPONSE=$(curl -X POST "${KIBANA_URL}/api/saved_objects/visualization" \
  -H "${KIBANA_HEADERS}" \
  -H "${KIBANA_KBN}" \
  -d "{
    \"attributes\": {
      \"title\": \"Répartition par type de paiement\",
      \"visState\": \"{\\\"title\\\":\\\"Répartition par type de paiement\\\",\\\"type\\\":\\\"pie\\\",\\\"aggs\\\":[{\\\"id\\\":\\\"1\\\",\\\"enabled\\\":true,\\\"type\\\":\\\"count\\\",\\\"params\\\":{},\\\"schema\\\":\\\"metric\\\"},{\\\"id\\\":\\\"2\\\",\\\"enabled\\\":true,\\\"type\\\":\\\"terms\\\",\\\"params\\\":{\\\"field\\\":\\\"payment_type.keyword\\\",\\\"orderBy\\\":\\\"1\\\",\\\"order\\\":\\\"desc\\\",\\\"size\\\":5,\\\"otherBucket\\\":false,\\\"otherBucketLabel\\\":\\\"Other\\\",\\\"missingBucket\\\":false,\\\"missingBucketLabel\\\":\\\"Missing\\\"},\\\"schema\\\":\\\"segment\\\"}],\\\"params\\\":{\\\"type\\\":\\\"pie\\\",\\\"addTooltip\\\":true,\\\"addLegend\\\":true,\\\"legendPosition\\\":\\\"right\\\",\\\"isDonut\\\":true,\\\"labels\\\":{\\\"show\\\":true,\\\"values\\\":true,\\\"last_level\\\":true,\\\"truncate\\\":100}}}\",
      \"uiStateJSON\": \"{}\",
      \"description\": \"Distribution des transactions par type de paiement\",
      \"version\": 1,
      \"kibanaSavedObjectMeta\": {
        \"searchSourceJSON\": \"{\\\"index\\\":\\\"${DATAVIEW_ID}\\\",\\\"query\\\":{\\\"query\\\":\\\"\\\",\\\"language\\\":\\\"kuery\\\"},\\\"filter\\\":[]}\"
      }
    }
  }" 2>/dev/null)

VIS3_ID=$(echo $VIS3_RESPONSE | jq -r '.id')
echo "✅ Visualisation 3 créée avec ID: ${VIS3_ID}"
echo ""

sleep 2

# 5. Créer le Dashboard
echo "📊 Création du Dashboard 'E-Commerce Logs Dashboard'..."
DASHBOARD_RESPONSE=$(curl -X POST "${KIBANA_URL}/api/saved_objects/dashboard" \
  -H "${KIBANA_HEADERS}" \
  -H "${KIBANA_KBN}" \
  -d "{
    \"attributes\": {
      \"title\": \"E-Commerce Logs Dashboard\",
      \"description\": \"Dashboard de monitoring des transactions E-Commerce\",
      \"panelsJSON\": \"[{\\\"version\\\":\\\"8.10.3\\\",\\\"type\\\":\\\"visualization\\\",\\\"gridData\\\":{\\\"x\\\":0,\\\"y\\\":0,\\\"w\\\":24,\\\"h\\\":15,\\\"i\\\":\\\"1\\\"},\\\"panelIndex\\\":\\\"1\\\",\\\"embeddableConfig\\\":{\\\"enhancements\\\":{}},\\\"panelRefName\\\":\\\"panel_1\\\"},{\\\"version\\\":\\\"8.10.3\\\",\\\"type\\\":\\\"visualization\\\",\\\"gridData\\\":{\\\"x\\\":24,\\\"y\\\":0,\\\"w\\\":24,\\\"h\\\":15,\\\"i\\\":\\\"2\\\"},\\\"panelIndex\\\":\\\"2\\\",\\\"embeddableConfig\\\":{\\\"enhancements\\\":{}},\\\"panelRefName\\\":\\\"panel_2\\\"},{\\\"version\\\":\\\"8.10.3\\\",\\\"type\\\":\\\"visualization\\\",\\\"gridData\\\":{\\\"x\\\":0,\\\"y\\\":15,\\\"w\\\":24,\\\"h\\\":15,\\\"i\\\":\\\"3\\\"},\\\"panelIndex\\\":\\\"3\\\",\\\"embeddableConfig\\\":{\\\"enhancements\\\":{}},\\\"panelRefName\\\":\\\"panel_3\\\"}]\",
      \"optionsJSON\": \"{\\\"hidePanelTitles\\\":false,\\\"useMargins\\\":true}\",
      \"version\": 1,
      \"timeRestore\": false,
      \"kibanaSavedObjectMeta\": {
        \"searchSourceJSON\": \"{\\\"query\\\":{\\\"query\\\":\\\"\\\",\\\"language\\\":\\\"kuery\\\"},\\\"filter\\\":[]}\"
      }
    },
    \"references\": [
      {
        \"name\": \"panel_1\",
        \"type\": \"visualization\",
        \"id\": \"${VIS1_ID}\"
      },
      {
        \"name\": \"panel_2\",
        \"type\": \"visualization\",
        \"id\": \"${VIS2_ID}\"
      },
      {
        \"name\": \"panel_3\",
        \"type\": \"visualization\",
        \"id\": \"${VIS3_ID}\"
      }
    ]
  }" 2>/dev/null)

DASHBOARD_ID=$(echo $DASHBOARD_RESPONSE | jq -r '.id')
echo "✅ Dashboard créé avec ID: ${DASHBOARD_ID}"
echo ""

# 6. Exporter le Dashboard
echo "💾 Export du Dashboard..."
curl -X POST "${KIBANA_URL}/api/saved_objects/_export" \
  -H "${KIBANA_HEADERS}" \
  -H "${KIBANA_KBN}" \
  -d "{
    \"objects\": [
      {
        \"type\": \"dashboard\",
        \"id\": \"${DASHBOARD_ID}\"
      }
    ],
    \"includeReferencesDeep\": true
  }" > /tmp/ecommerce-dashboard-export.ndjson 2>/dev/null

cp /tmp/ecommerce-dashboard-export.ndjson /home/dorrah/Bureau/projet/
echo "✅ Dashboard exporté dans: /home/dorrah/Bureau/projet/ecommerce-dashboard-export.ndjson"
echo ""

echo "=========================================="
echo "✅ Configuration terminée!"
echo "=========================================="
echo ""
echo "📊 Data View: logs-* (ID: ${DATAVIEW_ID})"
echo ""
echo "📈 Visualisations créées:"
echo "  1. Transactions par heure (ID: ${VIS1_ID})"
echo "  2. Top 10 Erreurs (ID: ${VIS2_ID})"
echo "  3. Répartition par type de paiement (ID: ${VIS3_ID})"
echo ""
echo "🎯 Dashboard: E-Commerce Logs Dashboard (ID: ${DASHBOARD_ID})"
echo ""
echo "🌐 Accès Kibana: http://localhost:5601"
echo "   → Analytics > Dashboard > E-Commerce Logs Dashboard"
echo ""
