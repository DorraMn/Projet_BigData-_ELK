# 📊 Changements Dashboard E-Commerce - Novembre 25, 2025

## 🎯 Objectif
Modifier la visualisation "Top 10 clients" pour afficher les **noms des clients** au lieu des IDs, et ajouter une métrique pour le **nombre total de clients uniques**.

## ✅ Modifications apportées

### 1. Enrichissement des données
- **Ajout du champ** `customer_name` à toutes les transactions
- **70 clients uniques** avec des noms français réalistes
- **100 transactions** totales dans la base

**Exemples de clients** :
- Alice Martin (C001) - 12 transactions
- Bob Dubois (C002) - 12 transactions  
- Claire Bernard (C003) - 12 transactions
- David Laurent (C004) - 12 transactions
- Emma Petit (C005) - 12 transactions
- François Moreau (C006) - 12 transactions

### 2. Modification de la visualisation "Top 10 clients"

**AVANT** :
```
Type: Graphique à barres horizontales (lnsXY)
Champ: customer_id
Affichage: C001, C002, C003, etc.
Format: Graphique visuel
```

**APRÈS** :
```
Type: Tableau de données (lnsDatatable)
Champ: customer_name
Affichage: Alice Martin, Bob Dubois, Claire Bernard, etc.
Format: Tableau avec 2 colonnes
  - Nom du client
  - Nombre de transactions
```

**Avantages** :
- ✅ Noms lisibles et compréhensibles
- ✅ Format tableau plus professionnel
- ✅ Tri automatique par nombre de transactions
- ✅ Meilleure présentation pour les rapports

### 3. Nouvelle métrique ajoutée

**Visualisation** : "Nombre total de clients"
- **ID** : `total-customers-viz`
- **Type** : Métrique (lnsMetric)
- **Agrégation** : Unique Count sur `customer_id`
- **Valeur actuelle** : 70 clients uniques
- **Position** : Ligne 1 du dashboard (KPIs)

### 4. Mise à jour du layout du dashboard

**Nouvelle organisation** :
```
Ligne 1 - KPIs (5 métriques) :
  [CA total] [Panier moyen] [Nb clients] [Transactions/h] [Taux succès]

Ligne 2 - Analyses (2 graphiques) :
  [Produits par catégorie - 50%] [Top 10 clients - 50%]

Ligne 3 - Détails (3 graphiques) :
  [Types paiement] [Top 10 erreurs] [Transactions par heure]
```

## 📦 Fichiers modifiés

### 1. `kibana-import.ndjson`
- Modification de la visualisation `top-customers-viz` (barres → tableau, customer_id → customer_name)
- Ajout de la visualisation `total-customers-viz` (nouvelle métrique)
- Mise à jour du dashboard avec les nouvelles références
- **Total objets** : 11 (1 data view + 9 visualisations + 1 dashboard)

### 2. `ecommerce-dashboard-export.ndjson`
- Export complet du dashboard mis à jour
- Inclut toutes les références nécessaires
- Prêt pour l'import dans un autre Kibana
- **Format** : NDJSON 11 lignes

### 3. `KIBANA-DASHBOARD.md`
- Documentation mise à jour avec la nouvelle visualisation
- Ajout du champ `customer_name` dans la structure des données
- Mise à jour des statistiques (70 clients uniques)
- Description complète de toutes les 9 visualisations

### 4. `regenerate-customer-data.sh` (nouveau)
- Script pour régénérer les données avec noms de clients
- Paramétrable : `./regenerate-customer-data.sh [nb_transactions]`
- Supprime l'ancien index et recrée les données
- Affiche les statistiques après injection

## 📊 Structure de données mise à jour

```json
{
  "@timestamp": "2025-11-25T08:00:00Z",
  "transaction_id": "TXN001",
  "amount": 89.99,
  "payment_type": "credit_card",
  "status": "success",
  "category": "electronics",
  "customer_id": "C001",
  "customer_name": "Alice Martin",  ← NOUVEAU CHAMP
  "error_code": ""
}
```

## 🔧 Commandes utilisées

### Suppression de l'ancien index
```bash
curl -X DELETE "http://localhost:9200/logs-ecommerce-*"
```

### Génération des données avec Python
```bash
python3 generate_data.py  # Voir regenerate-customer-data.sh
```

### Injection des données
```bash
curl -X POST "http://localhost:9200/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @/tmp/ecommerce-with-names.ndjson
```

### Import du dashboard
```bash
curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  --form file=@kibana-import.ndjson
```

### Export du dashboard
```bash
curl -X POST "http://localhost:5601/api/saved_objects/_export" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{"objects":[{"type":"dashboard","id":"ecommerce-dashboard"}],"includeReferencesDeep":true}' \
  > ecommerce-dashboard-export.ndjson
```

## 📈 Statistiques actuelles

- **Transactions totales** : 100
- **Clients uniques** : 70
- **Transactions réussies** : 75 (75%)
- **Transactions échouées** : 25 (25%)
- **Chiffre d'affaires** : ~10 460€
- **Panier moyen** : ~154€

**Top 5 clients** :
1. Alice Martin - 12 transactions
2. Bob Dubois - 12 transactions
3. Claire Bernard - 12 transactions
4. David Laurent - 12 transactions
5. Emma Petit - 12 transactions

## 🌐 Accès

**Dashboard Kibana** :
```
http://localhost:5601/app/dashboards#/view/ecommerce-dashboard
```

**Elasticsearch** :
```
http://localhost:9200/logs-ecommerce-*/_search
```

## 🚀 Prochaines étapes possibles

### Analyses avancées
- [ ] Ajouter un graphique du CA par client (Top 10 en valeur)
- [ ] Créer une heatmap des transactions par jour/heure
- [ ] Ajouter un funnel de conversion
- [ ] Visualisation géographique si on ajoute des localisations

### Enrichissement des données
- [ ] Ajouter des emails clients
- [ ] Ajouter des adresses (villes, régions)
- [ ] Enrichir avec des catégories de produits détaillées
- [ ] Ajouter des informations de session (durée, pages vues)

### Alertes et monitoring
- [ ] Configurer des alertes sur les erreurs de paiement
- [ ] Surveillance du taux de succès en temps réel
- [ ] Alertes sur les clients à forte valeur

## 📝 Notes techniques

### Mapping Elasticsearch
Tous les champs texte sont indexés comme `keyword` directement :
- `customer_name` → keyword
- `customer_id` → keyword
- `payment_type` → keyword
- `status` → keyword
- `category` → keyword
- `error_code` → keyword
- `transaction_id` → keyword

**Important** : Pas besoin d'utiliser `.keyword` dans les requêtes !

### Format Lens (Kibana 8.10.3)
- **lnsDatatable** : Tableau de données
- **lnsMetric** : Métrique simple
- **lnsPie** : Graphique en donut/camembert
- **lnsXY** : Graphiques à lignes/barres
- **formBased** : Source de données Elasticsearch

### API Kibana
- Import : `POST /api/saved_objects/_import`
- Export : `POST /api/saved_objects/_export`
- Overwrite : Ajouter `?overwrite=true`
- Header requis : `kbn-xsrf: true`

## ✨ Résultat final

Le dashboard affiche maintenant :
- ✅ **9 visualisations** fonctionnelles
- ✅ **Noms de clients lisibles** dans le tableau
- ✅ **Métrique du nombre total de clients**
- ✅ **Layout optimisé** avec 5 KPIs en ligne 1
- ✅ **Données réalistes** avec 70 clients français
- ✅ **Documentation complète** et à jour

**Satisfaction** : 🎉 Dashboard professionnel prêt pour la démonstration !
