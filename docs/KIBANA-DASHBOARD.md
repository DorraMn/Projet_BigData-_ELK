# Configuration Kibana - E-Commerce Dashboard

## 📊 Résumé

Dashboard Kibana créé avec succès pour le monitoring des transactions E-Commerce.

## 🎯 Index Pattern

- **Nom**: `logs-*`
- **ID**: `logs-ecommerce-dataview` (référence: `32056731-9898-4f69-9916-07bbca0662d1`)
- **Champ temporel**: `@timestamp`
- **Description**: Data View pour tous les logs E-Commerce

## 📈 Visualisations créées

### 1. Transactions par heure
- **Type**: Lens Line Chart (Courbe)
- **ID**: `trans-per-hour-viz`
- **Description**: Évolution du nombre de transactions par heure
- **Agrégation**: 
  - Métrique: Count
  - Bucket: Date Histogram sur `@timestamp` (intervalle: automatique)
- **Utilité**: Visualiser les pics d'activité et tendances horaires

### 2. Top 10 Erreurs
- **Type**: Lens Data Table (Tableau)
- **ID**: `top-errors-viz`
- **Description**: Les 10 codes d'erreur les plus fréquents
- **Filtre**: `status: failed`
- **Agrégation**:
  - Métrique: Count
  - Bucket: Terms sur `error_code` (top 10)
- **Note**: Le champ `error_code` est déjà de type `keyword`, pas besoin du suffixe `.keyword`
- **Utilité**: Identifier rapidement les erreurs principales à corriger

### 3. Répartition par type de paiement
- **Type**: Lens Pie Chart (Donut)
- **ID**: `payment-types-viz`
- **Description**: Distribution des transactions par méthode de paiement
- **Agrégation**:
  - Métrique: Count
  - Bucket: Terms sur `payment_type`
- **Note**: Le champ `payment_type` est déjà de type `keyword`, pas besoin du suffixe `.keyword`
- **Utilité**: Comprendre les préférences de paiement des clients

### 4. Produits par catégorie
- **Type**: Lens Bar Chart (Barres verticales)
- **ID**: `products-by-category-viz`
- **Description**: Nombre de transactions par catégorie de produits
- **Agrégation**:
  - Métrique: Count
  - Bucket: Terms sur `category`
- **Catégories**: electronics, books, clothing, home
- **Utilité**: Identifier les catégories de produits les plus populaires

### 5. Chiffre d'affaires
- **Type**: Lens Metric (Métrique)
- **ID**: `revenue-metric-viz`
- **Description**: Montant total des ventes réussies
- **Agrégation**:
  - Métrique: Sum sur `amount`
  - Filtre: `status: success`
- **Utilité**: Suivre le chiffre d'affaires en temps réel

### 6. Panier moyen
- **Type**: Lens Metric (Métrique)
- **ID**: `avg-basket-viz`
- **Description**: Montant moyen par transaction réussie
- **Agrégation**:
  - Métrique: Average sur `amount`
  - Filtre: `status: success`
- **Utilité**: Analyser le comportement d'achat moyen

### 7. Taux de succès vs échecs
- **Type**: Lens Pie Chart (Donut)
- **ID**: `success-rate-viz`
- **Description**: Répartition entre transactions réussies et échouées
- **Agrégation**:
  - Métrique: Count
  - Bucket: Terms sur `status`
- **Utilité**: Monitorer la santé de la plateforme

### 8. Top 10 clients
- **Type**: Lens Data Table (Tableau)
- **ID**: `top-customers-viz`
- **Description**: Les 10 clients avec le plus de transactions
- **Agrégation**:
  - Métrique: Count
  - Bucket: Terms sur `customer_name` (top 10)
- **Colonnes**:
  - Nom du client (customer_name)
  - Nombre de transactions (count)
- **Utilité**: Identifier les clients fidèles et VIP avec leurs noms

### 9. Nombre total de clients
- **Type**: Lens Metric (Métrique)
- **ID**: `total-customers-viz`
- **Description**: Nombre de clients uniques ayant effectué au moins une transaction
- **Agrégation**:
  - Métrique: Unique Count sur `customer_id`
- **Utilité**: Suivre la base client active

## 🎨 Dashboard

- **Nom**: **E-Commerce Logs Dashboard**
- **ID**: `ecommerce-dashboard`
- **Layout**: Grid 3x3 optimisé
  - **Ligne 1 - KPIs** (5 métriques):
    - Chiffre d'affaires (20%)
    - Panier moyen (20%)
    - Nombre total de clients (20%)
    - Transactions par heure (19%)
    - Taux de succès (19%)
  - **Ligne 2 - Analyses**:
    - Produits par catégorie (50%)
    - Top 10 clients avec noms (50%)
  - **Ligne 3 - Détails**:
    - Répartition paiements (33%)
    - Top 10 Erreurs (33%)
    - Transactions par heure (33%)
- **Time Range**: Dernières 24 heures (now-24h to now)
- **Refresh**: Manuel (pause)
- **Nombre total de visualisations**: 9

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
- **Format**: NDJSON (11 lignes)
- **Contenu**: 
  - 1 index pattern (Data View)
  - 9 visualisations Lens (métriques, graphiques, tableaux)
  - 1 dashboard
  - Toutes les références nécessaires
- **Utilisation**: Import dans un autre Kibana avec `POST /api/saved_objects/_import?overwrite=true`

## 🌐 Accès

### Kibana
- **URL Dashboard**: http://localhost:5601/app/dashboards#/view/ecommerce-dashboard
- **URL Discover**: http://localhost:5601/app/discover
- **Navigation manuelle**: Analytics > Dashboard > E-Commerce Logs Dashboard

### Elasticsearch
- **URL**: http://localhost:9200
- **Index**: `logs-ecommerce-2025.11.25`
- **Vérification**: `curl http://localhost:9200/logs-ecommerce-*/_count`

## 🗂️ Structure des données (Mapping)

Tous les champs textuels sont indexés comme `keyword` directement :
- `error_code` → type `keyword` (pas besoin de `.keyword`)
- `payment_type` → type `keyword`
- `status` → type `keyword`
- `category` → type `keyword`
- `customer_id` → type `keyword`
- `customer_name` → type `keyword`
- `transaction_id` → type `keyword`
- `@timestamp` → type `date`
- `amount` → type `float`

## 📊 Données injectées

- **Nombre de documents**: 100 transactions
- **Période**: 25 novembre 2025, 08:00 - 23:59
- **Transactions réussies**: 75 (75%)
- **Transactions échouées**: 25 (25%)
- **Nombre de clients uniques**: 70 clients
- **Clients les plus actifs**: Alice Martin, Bob Dubois, Claire Bernard (12 transactions chacun)
- **Chiffre d'affaires total**: ~10 460€
- **Panier moyen**: ~154€
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
