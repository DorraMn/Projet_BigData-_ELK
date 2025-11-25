# Configuration Kibana - E-Commerce Dashboard

## 📊 Résumé

Dashboard Kibana créé avec succès pour le monitoring des transactions E-Commerce.

## 🎯 Index Pattern

- **Nom**: `logs-*`
- **ID**: `32056731-9898-4f69-9916-07bbca0662d1`
- **Champ temporel**: `@timestamp`
- **Description**: Data View pour tous les logs E-Commerce

## 📈 Visualisations créées

### 1. Transactions par heure
- **Type**: Line Chart (Courbe)
- **ID**: `b6393ba0-c9f5-11f0-b9de-2327bf14c31d`
- **Description**: Évolution du nombre de transactions par heure
- **Agrégation**: 
  - Métrique: Count
  - Bucket: Date Histogram sur `@timestamp` (intervalle: 1 heure)
- **Utilité**: Visualiser les pics d'activité et tendances horaires

### 2. Top 10 Erreurs
- **Type**: Data Table (Tableau)
- **ID**: `b7d3d8d0-c9f5-11f0-b9de-2327bf14c31d`
- **Description**: Les 10 codes d'erreur les plus fréquents
- **Filtre**: `status:failed`
- **Agrégation**:
  - Métrique: Count
  - Bucket: Terms sur `error_code.keyword` (top 10)
- **Utilité**: Identifier rapidement les erreurs principales à corriger

### 3. Répartition par type de paiement
- **Type**: Pie Chart (Donut)
- **ID**: `b99bc790-c9f5-11f0-b9de-2327bf14c31d`
- **Description**: Distribution des transactions par méthode de paiement
- **Agrégation**:
  - Métrique: Count
  - Bucket: Terms sur `payment_type.keyword`
- **Utilité**: Comprendre les préférences de paiement des clients

## 🎨 Dashboard

- **Nom**: **E-Commerce Logs Dashboard**
- **ID**: `bb68e670-c9f5-11f0-b9de-2327bf14c31d`
- **Layout**:
  - **Ligne 1**: 
    - Transactions par heure (gauche, 50%)
    - Top 10 Erreurs (droite, 50%)
  - **Ligne 2**: 
    - Répartition par type de paiement (gauche, 50%)

## 📦 Fichiers générés

### 1. Données de test
- **Fichier**: `test-ecommerce-logs.json`
- **Contenu**: 30 transactions E-Commerce avec:
  - Timestamps répartis sur 8 heures (10:00 - 17:00)
  - Mix de transactions réussies et échouées
  - Différents types de paiement (credit_card, paypal, debit_card)
  - Codes d'erreur variés (PAYMENT_DECLINED, INSUFFICIENT_FUNDS, etc.)
  - Montants variés (19.99€ - 299.99€)

### 2. Pipeline Logstash
- **Fichier**: `pipeline/ecommerce-pipeline.conf`
- **Fonction**: Ingérer les logs JSON dans Elasticsearch
- **Index cible**: `logs-ecommerce-YYYY.MM.dd`

### 3. Script de configuration
- **Fichier**: `setup-kibana-dashboard.sh`
- **Fonction**: Automatiser la création du dashboard via l'API Kibana
- **Actions**:
  - Création du Data View
  - Création des 3 visualisations
  - Création du dashboard
  - Export du dashboard

### 4. Export du dashboard
- **Fichier**: `ecommerce-dashboard-export.ndjson`
- **Format**: NDJSON (4 lignes)
- **Contenu**: 
  - 3 visualisations
  - 1 dashboard
  - Toutes les références nécessaires
- **Utilisation**: Import dans un autre Kibana avec `POST /api/saved_objects/_import`

## 🌐 Accès

### Kibana
- **URL**: http://localhost:5601
- **Navigation**: Analytics > Dashboard > E-Commerce Logs Dashboard

### Elasticsearch
- **URL**: http://localhost:9200
- **Index**: `logs-ecommerce-2025.11.25`
- **Vérification**: `curl http://localhost:9200/logs-ecommerce-*/_count`

## 📊 Données injectées

- **Nombre de documents**: 30 transactions
- **Période**: 25 novembre 2025, 10:00 - 17:00
- **Transactions réussies**: 20 (66.7%)
- **Transactions échouées**: 10 (33.3%)
- **Types de paiement**:
  - Credit Card: 10 transactions
  - PayPal: 10 transactions
  - Debit Card: 10 transactions
- **Codes d'erreur**:
  - PAYMENT_DECLINED: 3
  - NETWORK_ERROR: 2
  - INSUFFICIENT_FUNDS: 1
  - CARD_EXPIRED: 1
  - FRAUD_DETECTED: 1
  - TIMEOUT: 1
  - INVALID_CVV: 1

## 🔄 Import du dashboard dans un autre Kibana

```bash
# Via l'interface web
1. Aller dans Stack Management > Saved Objects
2. Cliquer sur "Import"
3. Sélectionner le fichier ecommerce-dashboard-export.ndjson
4. Confirmer l'import

# Via API
curl -X POST "http://localhost:5601/api/saved_objects/_import" \
  -H "kbn-xsrf: true" \
  --form file=@ecommerce-dashboard-export.ndjson
```

## 🎯 Exemple de requêtes

### Compter les transactions par statut
```json
GET logs-ecommerce-*/_search
{
  "size": 0,
  "aggs": {
    "by_status": {
      "terms": {
        "field": "status.keyword"
      }
    }
  }
}
```

### Top 5 clients par nombre de transactions
```json
GET logs-ecommerce-*/_search
{
  "size": 0,
  "aggs": {
    "top_customers": {
      "terms": {
        "field": "customer_id.keyword",
        "size": 5
      }
    }
  }
}
```

### Montant moyen par type de paiement
```json
GET logs-ecommerce-*/_search
{
  "size": 0,
  "aggs": {
    "by_payment": {
      "terms": {
        "field": "payment_type.keyword"
      },
      "aggs": {
        "avg_amount": {
          "avg": {
            "field": "amount"
          }
        }
      }
    }
  }
}
```

## ✅ Vérification

```bash
# Vérifier l'index
curl http://localhost:9200/logs-ecommerce-*/_count

# Lister les visualisations
curl -s http://localhost:5601/api/saved_objects/_find?type=visualization \
  -H "kbn-xsrf: true" | jq -r '.saved_objects[] | .attributes.title'

# Lister les dashboards
curl -s http://localhost:5601/api/saved_objects/_find?type=dashboard \
  -H "kbn-xsrf: true" | jq -r '.saved_objects[] | .attributes.title'
```

## 📝 Notes

- Les données de test sont fictives et générées pour démonstration
- Le dashboard est pré-configuré avec des filtres et time ranges appropriés
- Pour injecter plus de données, modifiez `test-ecommerce-logs.json` et relancez Logstash
- Les visualisations utilisent le langage KQL (Kibana Query Language)

---

**Date de création**: 25 novembre 2025  
**Version Kibana**: 8.10.3  
**Version Elasticsearch**: 8.10.3
