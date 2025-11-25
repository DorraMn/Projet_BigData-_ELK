# 🔍 Page de Recherche - Documentation

## Vue d'ensemble

La page de recherche permet de rechercher et filtrer les logs Elasticsearch avec une interface intuitive utilisant DataTables.js pour l'affichage et la manipulation des données.

## URLs

- **Page de recherche** : `http://localhost:8000/search`
- **API de recherche** : `http://localhost:8000/api/search`

## Fonctionnalités

### 1. Interface de recherche (`/search`)

#### Formulaire de recherche
- **🔎 Recherche texte libre** : Recherche dans message, produit, client, type de paiement
  - Supporte la recherche floue (fuzziness AUTO)
  - Recherche multi-champs avec Elasticsearch multi_match

- **📊 Filtre par niveau** : 
  - Success
  - Failed
  - Pending
  - Info
  - Warning
  - Error

- **🛠️ Filtre par service** : Nom du service

- **📅 Filtres de dates** :
  - Date début (datetime-local)
  - Date fin (datetime-local)

#### Boutons d'action
- **🔍 Rechercher** : Lance la recherche avec les critères sélectionnés
- **🔄 Reset** : Réinitialise le formulaire et les résultats
- **📥 Export CSV** : Exporte les résultats en CSV (activé uniquement après une recherche)

#### Affichage des résultats
- **DataTables.js** : Tableau interactif avec :
  - Tri par colonne
  - Recherche locale dans les résultats
  - Pagination locale (50 résultats par page)
  - Traduction française
  
- **Colonnes affichées** :
  - Timestamp (formaté en français)
  - Niveau (badge coloré)
  - Service
  - Message
  - Produit
  - Client
  - Type de paiement
  - Montant (avec €)

- **Pagination serveur** :
  - 50 logs par page
  - Boutons Précédent/Suivant
  - Affichage du numéro de page actuel

### 2. API de recherche (`/api/search`)

#### Paramètres de requête (GET)

```
GET /api/search?query=<text>&level=<status>&service=<name>&date_from=<iso>&date_to=<iso>&page=<num>
```

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `query` | string | Recherche texte libre | `?query=paypal` |
| `level` | string | Filtre par niveau/status | `?level=failed` |
| `service` | string | Filtre par service | `?service=payment-api` |
| `date_from` | string (ISO) | Date début | `?date_from=2025-11-25T00:00:00` |
| `date_to` | string (ISO) | Date fin | `?date_to=2025-11-26T00:00:00` |
| `page` | integer | Numéro de page (défaut: 1) | `?page=2` |

#### Réponse JSON

```json
{
  "success": true,
  "total": 67,
  "page": 1,
  "page_size": 50,
  "total_pages": 2,
  "logs": [
    {
      "timestamp": "2025-11-26T00:40:00Z",
      "level": "failed",
      "service": "unknown",
      "message": "",
      "product": "",
      "customer": "Jacques Roux",
      "payment_type": "paypal",
      "amount": 23.5,
      "category": "electronics"
    }
  ],
  "query_params": {
    "query": "paypal",
    "level": "",
    "service": "",
    "date_from": "",
    "date_to": ""
  }
}
```

#### Requête Elasticsearch (Query DSL)

L'API construit automatiquement une requête Elasticsearch optimisée :

**Exemple 1 : Recherche texte**
```json
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "paypal",
            "fields": ["message", "product", "customer_name", "payment_type"],
            "type": "best_fields",
            "fuzziness": "AUTO"
          }
        }
      ]
    }
  },
  "sort": [{"@timestamp": {"order": "desc"}}],
  "from": 0,
  "size": 50
}
```

**Exemple 2 : Filtres combinés**
```json
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "status": "failed"
          }
        },
        {
          "range": {
            "@timestamp": {
              "gte": "2025-11-25T00:00:00",
              "lte": "2025-11-26T00:00:00"
            }
          }
        }
      ]
    }
  },
  "sort": [{"@timestamp": {"order": "desc"}}],
  "from": 0,
  "size": 50
}
```

### 3. Historique des recherches (MongoDB)

Chaque recherche est automatiquement sauvegardée dans MongoDB :

**Collection** : `monitoring.search_history`

**Structure du document** :
```json
{
  "_id": ObjectId("..."),
  "timestamp": ISODate("2025-11-25T15:16:19.537Z"),
  "query_text": "paypal",
  "level": "",
  "service": "",
  "date_from": "",
  "date_to": "",
  "results_count": 67,
  "ip_address": "172.18.0.1"
}
```

**Consulter l'historique** :
```bash
docker compose exec mongodb mongosh monitoring --eval "db.search_history.find().limit(10).pretty()"
```

## Exemples d'utilisation

### Exemple 1 : Rechercher tous les logs avec "paypal"
```bash
curl "http://localhost:8000/api/search?query=paypal"
```

### Exemple 2 : Rechercher les erreurs
```bash
curl "http://localhost:8000/api/search?level=failed"
```

### Exemple 3 : Rechercher dans une plage de dates
```bash
curl "http://localhost:8000/api/search?date_from=2025-11-25T00:00:00&date_to=2025-11-26T00:00:00"
```

### Exemple 4 : Recherche combinée
```bash
curl "http://localhost:8000/api/search?query=credit_card&level=success&page=1"
```

## Export CSV

L'export CSV génère un fichier avec toutes les colonnes :

**Format** :
```csv
Timestamp,Niveau,Service,Message,Produit,Client,Paiement,Montant
"2025-11-26T00:40:00Z","failed","unknown","","","Jacques Roux","paypal","23.5"
```

**Nom du fichier** : `logs-export-YYYY-MM-DDThh-mm-ss.csv`

## Technologies utilisées

- **Backend** : Flask + Elasticsearch Python Client
- **Frontend** : 
  - jQuery 3.7.1
  - DataTables.js 1.13.7
  - DataTables Buttons (HTML5 export)
  - JSZip 3.10.1
- **Storage** : MongoDB (historique des recherches)

## Performances

- **Pagination serveur** : 50 logs par page pour limiter la charge
- **Index Elasticsearch** : Recherche optimisée avec multi_match
- **Cache** : Résultats stockés côté client pour navigation rapide
- **Timeout** : 5 secondes pour les requêtes Elasticsearch

## Sécurité

- Aucun paramètre SQL (utilisation d'Elasticsearch Query DSL)
- Échappement automatique des guillemets dans l'export CSV
- Sauvegarde de l'IP pour traçabilité des recherches
- Timeout configuré pour éviter les requêtes trop longues

## Tests

### Test de l'API
```bash
# Test recherche simple
curl -s "http://localhost:8000/api/search?page=1" | python3 -m json.tool

# Test avec filtres
curl -s "http://localhost:8000/api/search?level=failed&page=1"

# Test recherche texte
curl -s "http://localhost:8000/api/search?query=paypal"
```

### Test de l'historique MongoDB
```bash
docker compose exec mongodb mongosh monitoring --eval "db.search_history.find().count()"
```

## Résultats des tests

✅ **API fonctionnelle** :
- Total de logs : 200
- Logs avec "paypal" : 67
- Logs "failed" : 50
- Historique MongoDB : Sauvegardé correctement

✅ **Interface web** :
- Formulaire de recherche responsive
- DataTables.js avec traduction française
- Export CSV fonctionnel
- Pagination serveur active

## Améliorations futures

1. **Autocomplete** : Suggestions de recherche basées sur l'historique
2. **Recherche sauvegardée** : Sauvegarder les filtres favoris
3. **Graphiques** : Visualisation des résultats de recherche
4. **Export JSON/Excel** : Formats d'export supplémentaires
5. **Recherche avancée** : Opérateurs booléens (AND, OR, NOT)
6. **Highlights** : Mise en évidence des termes recherchés
7. **Filtres dynamiques** : Liste déroulante basée sur les valeurs existantes
