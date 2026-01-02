#!/bin/bash

# Configuration
KIBANA_URL="http://localhost:5601"
DATAVIEW_ID="32056731-9898-4f69-9916-07bbca0662d1"

echo "=========================================="
echo "  CORRECTION KIBANA DASHBOARD"
echo "=========================================="
echo ""
echo "📊 Data View ID: ${DATAVIEW_ID}"
echo ""

# Supprimer les anciennes visualisations et dashboard
echo "🗑️  Suppression des anciens objets..."

# Supprimer les visualisations
for VIS_ID in "b6393ba0-c9f5-11f0-b9de-2327bf14c31d" "b7d3d8d0-c9f5-11f0-b9de-2327bf14c31d" "b99bc790-c9f5-11f0-b9de-2327bf14c31d"; do
  curl -s -X DELETE "${KIBANA_URL}/api/saved_objects/visualization/${VIS_ID}" -H "kbn-xsrf: true" > /dev/null 2>&1
done

# Supprimer le dashboard
curl -s -X DELETE "${KIBANA_URL}/api/saved_objects/dashboard/bb68e670-c9f5-11f0-b9de-2327bf14c31d" -H "kbn-xsrf: true" > /dev/null 2>&1

echo "✅ Anciens objets supprimés"
echo ""
sleep 2

# Créer Visualisation 1: Transactions par heure (utilise Lens moderne)
echo "📈 Création 'Transactions par heure'..."
VIS1=$(curl -s -X POST "${KIBANA_URL}/api/saved_objects/lens" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{
    "attributes": {
      "title": "Transactions par heure",
      "description": "Nombre de transactions par heure",
      "visualizationType": "lnsXY",
      "state": {
        "datasourceStates": {
          "formBased": {
            "layers": {
              "layer1": {
                "columns": {
                  "col1": {
                    "label": "@timestamp",
                    "dataType": "date",
                    "operationType": "date_histogram",
                    "sourceField": "@timestamp",
                    "isBucketed": true,
                    "scale": "interval",
                    "params": {
                      "interval": "1h",
                      "includeEmptyRows": true
                    }
                  },
                  "col2": {
                    "label": "Count",
                    "dataType": "number",
                    "operationType": "count",
                    "isBucketed": false,
                    "scale": "ratio",
                    "sourceField": "___records___"
                  }
                },
                "columnOrder": ["col1", "col2"],
                "incompleteColumns": {}
              }
            }
          }
        },
        "visualization": {
          "legend": {
            "isVisible": true,
            "position": "right"
          },
          "valueLabels": "hide",
          "fittingFunction": "Linear",
          "axisTitlesVisibilitySettings": {
            "x": true,
            "yLeft": true,
            "yRight": true
          },
          "tickLabelsVisibilitySettings": {
            "x": true,
            "yLeft": true,
            "yRight": true
          },
          "labelsOrientation": {
            "x": 0,
            "yLeft": 0,
            "yRight": 0
          },
          "gridlinesVisibilitySettings": {
            "x": true,
            "yLeft": true,
            "yRight": true
          },
          "preferredSeriesType": "line",
          "layers": [
            {
              "layerId": "layer1",
              "accessors": ["col2"],
              "position": "top",
              "seriesType": "line",
              "showGridlines": false,
              "layerType": "data",
              "xAccessor": "col1"
            }
          ]
        },
        "query": {
          "query": "",
          "language": "kuery"
        },
        "filters": []
      },
      "references": [
        {
          "type": "index-pattern",
          "id": "'"${DATAVIEW_ID}"'",
          "name": "indexpattern-datasource-layer-layer1"
        }
      ]
    }
  }')
VIS1_ID=$(echo $VIS1 | jq -r '.id')
echo "✅ Visualisation 1: ${VIS1_ID}"
sleep 1

# Créer Visualisation 2: Top 10 Erreurs
echo "📋 Création 'Top 10 Erreurs'..."
VIS2=$(curl -s -X POST "${KIBANA_URL}/api/saved_objects/lens" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{
    "attributes": {
      "title": "Top 10 Erreurs",
      "description": "Les 10 codes erreur les plus fréquents",
      "visualizationType": "lnsDatatable",
      "state": {
        "datasourceStates": {
          "formBased": {
            "layers": {
              "layer1": {
                "columns": {
                  "col1": {
                    "label": "Code Erreur",
                    "dataType": "string",
                    "operationType": "terms",
                    "sourceField": "error_code.keyword",
                    "isBucketed": true,
                    "scale": "ordinal",
                    "params": {
                      "size": 10,
                      "orderBy": {
                        "type": "column",
                        "columnId": "col2"
                      },
                      "orderDirection": "desc",
                      "otherBucket": false,
                      "missingBucket": false
                    }
                  },
                  "col2": {
                    "label": "Nombre",
                    "dataType": "number",
                    "operationType": "count",
                    "isBucketed": false,
                    "scale": "ratio",
                    "sourceField": "___records___"
                  }
                },
                "columnOrder": ["col1", "col2"],
                "incompleteColumns": {}
              }
            }
          }
        },
        "visualization": {
          "layerId": "layer1",
          "layerType": "data",
          "columns": [
            {
              "columnId": "col1",
              "isTransposed": false
            },
            {
              "columnId": "col2",
              "isTransposed": false
            }
          ]
        },
        "query": {
          "query": "status: failed",
          "language": "kuery"
        },
        "filters": []
      },
      "references": [
        {
          "type": "index-pattern",
          "id": "'"${DATAVIEW_ID}"'",
          "name": "indexpattern-datasource-layer-layer1"
        }
      ]
    }
  }')
VIS2_ID=$(echo $VIS2 | jq -r '.id')
echo "✅ Visualisation 2: ${VIS2_ID}"
sleep 1

# Créer Visualisation 3: Répartition par type de paiement
echo "🥧 Création 'Répartition par type de paiement'..."
VIS3=$(curl -s -X POST "${KIBANA_URL}/api/saved_objects/lens" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{
    "attributes": {
      "title": "Répartition par type de paiement",
      "description": "Distribution des transactions par méthode de paiement",
      "visualizationType": "lnsPie",
      "state": {
        "datasourceStates": {
          "formBased": {
            "layers": {
              "layer1": {
                "columns": {
                  "col1": {
                    "label": "Type de paiement",
                    "dataType": "string",
                    "operationType": "terms",
                    "sourceField": "payment_type.keyword",
                    "isBucketed": true,
                    "scale": "ordinal",
                    "params": {
                      "size": 5,
                      "orderBy": {
                        "type": "column",
                        "columnId": "col2"
                      },
                      "orderDirection": "desc",
                      "otherBucket": false,
                      "missingBucket": false
                    }
                  },
                  "col2": {
                    "label": "Transactions",
                    "dataType": "number",
                    "operationType": "count",
                    "isBucketed": false,
                    "scale": "ratio",
                    "sourceField": "___records___"
                  }
                },
                "columnOrder": ["col1", "col2"],
                "incompleteColumns": {}
              }
            }
          }
        },
        "visualization": {
          "shape": "donut",
          "layers": [
            {
              "layerId": "layer1",
              "primaryGroups": ["col1"],
              "metrics": ["col2"],
              "numberDisplay": "percent",
              "categoryDisplay": "default",
              "legendDisplay": "default",
              "nestedLegend": false,
              "layerType": "data"
            }
          ]
        },
        "query": {
          "query": "",
          "language": "kuery"
        },
        "filters": []
      },
      "references": [
        {
          "type": "index-pattern",
          "id": "'"${DATAVIEW_ID}"'",
          "name": "indexpattern-datasource-layer-layer1"
        }
      ]
    }
  }')
VIS3_ID=$(echo $VIS3 | jq -r '.id')
echo "✅ Visualisation 3: ${VIS3_ID}"
echo ""
sleep 1

# Créer le nouveau Dashboard
echo "📊 Création du Dashboard..."
DASHBOARD=$(curl -s -X POST "${KIBANA_URL}/api/saved_objects/dashboard" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{
    "attributes": {
      "title": "E-Commerce Logs Dashboard",
      "description": "Dashboard de monitoring des transactions E-Commerce",
      "panelsJSON": "[{\"version\":\"8.10.3\",\"type\":\"lens\",\"gridData\":{\"x\":0,\"y\":0,\"w\":24,\"h\":15,\"i\":\"1\"},\"panelIndex\":\"1\",\"embeddableConfig\":{\"enhancements\":{}},\"panelRefName\":\"panel_1\"},{\"version\":\"8.10.3\",\"type\":\"lens\",\"gridData\":{\"x\":24,\"y\":0,\"w\":24,\"h\":15,\"i\":\"2\"},\"panelIndex\":\"2\",\"embeddableConfig\":{\"enhancements\":{}},\"panelRefName\":\"panel_2\"},{\"version\":\"8.10.3\",\"type\":\"lens\",\"gridData\":{\"x\":0,\"y\":15,\"w\":24,\"h\":15,\"i\":\"3\"},\"panelIndex\":\"3\",\"embeddableConfig\":{\"enhancements\":{}},\"panelRefName\":\"panel_3\"}]",
      "optionsJSON": "{\"hidePanelTitles\":false,\"useMargins\":true}",
      "version": 1,
      "timeRestore": true,
      "timeFrom": "now-24h",
      "timeTo": "now",
      "refreshInterval": {
        "pause": true,
        "value": 0
      },
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filter\":[]}"
      }
    },
    "references": [
      {
        "name": "panel_1",
        "type": "lens",
        "id": "'"${VIS1_ID}"'"
      },
      {
        "name": "panel_2",
        "type": "lens",
        "id": "'"${VIS2_ID}"'"
      },
      {
        "name": "panel_3",
        "type": "lens",
        "id": "'"${VIS3_ID}"'"
      }
    ]
  }')
DASHBOARD_ID=$(echo $DASHBOARD | jq -r '.id')
echo "✅ Dashboard créé: ${DASHBOARD_ID}"
echo ""

# Exporter le dashboard
echo "💾 Export du Dashboard..."
curl -s -X POST "${KIBANA_URL}/api/saved_objects/_export" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d "{
    \"objects\": [
      {
        \"type\": \"dashboard\",
        \"id\": \"${DASHBOARD_ID}\"
      }
    ],
    \"includeReferencesDeep\": true
  }" > /home/dorrah/Bureau/projet/ecommerce-dashboard-export.ndjson 2>/dev/null

echo "✅ Export terminé"
echo ""

echo "=========================================="
echo "✅ DASHBOARD CORRIGÉ!"
echo "=========================================="
echo ""
echo "📊 Nouveau Dashboard ID: ${DASHBOARD_ID}"
echo ""
echo "🌐 URL d'accès:"
echo "http://localhost:5601/app/dashboards#/view/${DASHBOARD_ID}"
echo ""
echo "📈 Visualisations:"
echo "  1. Transactions par heure: ${VIS1_ID}"
echo "  2. Top 10 Erreurs: ${VIS2_ID}"
echo "  3. Répartition par type de paiement: ${VIS3_ID}"
echo ""
