# Guide de Dépannage - Graphiques Kibana Vides

## 🔍 Problème Identifié

Les graphiques Kibana affichaient "No results found" car :
1. ❌ Les données dans Elasticsearch étaient anciennes (novembre 2025)
2. ❌ Le filtre temporel du dashboard était configuré sur "Last 24 hours"
3. ❌ Aucune donnée récente n'existait dans cette plage

## ✅ Solutions Appliquées

### 1. Injection de Données Récentes

**Fichiers créés :**
- `/home/dorrah/Bureau/projet/scripts/inject-recent-data.py` - Injecte les données du fichier JSON
- `/home/dorrah/Bureau/projet/scripts/generate-realtime-data.py` - Génère des données en temps réel

**Données ajoutées :**
- 500 documents depuis `/tmp/logstream_test_data/ecommerce_recent.json` (26 déc 2025 → 2 jan 2026)
- 240 documents générés pour les dernières 24 heures
- **Total : 1740 documents** dans Elasticsearch

### 2. Configuration des Data Views Kibana

**Script créé :**
- `/home/dorrah/Bureau/projet/scripts/fix-kibana-visualizations.py`

**Actions effectuées :**
- ✅ Rafraîchissement des data views existants
- ✅ Configuration du data view par défaut (`logs-*`)
- ✅ Vérification du champ temporel (`@timestamp`)

### 3. Distribution des Données

```
📊 Derniers 7 jours : 735 documents

2025-12-27:   74 documents ███
2025-12-28:   63 documents ███
2025-12-29:   72 documents ███
2025-12-30:   82 documents ████
2025-12-31:   62 documents ███
2026-01-01:  127 documents ██████
2026-01-02:  255 documents ███████████
```

## 📋 Comment Utiliser Kibana Maintenant

### Étape 1 : Ouvrir le Dashboard
```
http://localhost:5601
```

### Étape 2 : Sélectionner la Bonne Période

Dans Kibana, cliquez sur le **sélecteur de temps** en haut à droite :

**Options recommandées :**
- ⭐ **Last 7 days** - Affichera 735 documents
- ⭐ **Last 24 hours** - Affichera 317 documents  
- ⭐ **Last 30 days** - Affichera tous les documents

**À éviter :**
- ❌ Last 15 minutes (trop court, pas de données)
- ❌ Today (peut être vide selon l'heure)

### Étape 3 : Vérifier les Visualisations

Les graphiques suivants devraient maintenant afficher des données :
- 📈 Timeline des transactions
- 💰 Montant total des ventes
- ✅/❌ Taux de succès/échec
- 📊 Répartition par catégorie
- 💳 Répartition par mode de paiement

## 🔧 Maintenance Continue

### Générer de Nouvelles Données

Pour maintenir des données fraîches dans vos dashboards :

```bash
# Générer 240 nouveaux logs pour les dernières 24h
python3 /home/dorrah/Bureau/projet/scripts/generate-realtime-data.py

# Injecter des données depuis un fichier
python3 /home/dorrah/Bureau/projet/scripts/inject-recent-data.py
```

### Vérifier l'État des Données

```bash
# Compter les documents
curl -s "http://localhost:9200/logs-*/_count"

# Voir les dernières entrées
curl -s "http://localhost:9200/logs-*/_search?size=5&sort=@timestamp:desc"
```

## 🚨 Dépannage Supplémentaire

### Si les graphiques sont encore vides :

1. **Vérifier le data view**
   - Dans Kibana : Stack Management → Data Views
   - Assurez-vous que `logs-*` existe et utilise `@timestamp`

2. **Vérifier les données**
   ```bash
   curl "http://localhost:9200/logs-*/_count"
   ```
   Si count = 0, ré-injecter les données

3. **Rafraîchir Kibana**
   - Appuyez sur `Ctrl + R` pour recharger la page
   - Ou cliquez sur "Refresh" dans le dashboard

4. **Vérifier les filtres**
   - Dans le dashboard, vérifiez qu'aucun filtre restrictif n'est activé
   - Supprimez les filtres en cliquant sur la croix (X)

5. **Recréer le data view**
   ```bash
   python3 /home/dorrah/Bureau/projet/scripts/fix-kibana-visualizations.py
   ```

## 📊 Statistiques Finales

- **Total documents** : 1740
- **Dernières 24h** : 317 documents
- **Derniers 7 jours** : 735 documents
- **Période couverte** : 18 novembre 2025 → 2 janvier 2026
- **Indices utilisés** : `logs-*` (4 indices)

## ✅ Checklist de Vérification

- [x] Elasticsearch fonctionne (port 9200)
- [x] Kibana fonctionne (port 5601)
- [x] 1740+ documents dans Elasticsearch
- [x] Data view `logs-*` configuré
- [x] Données récentes disponibles (dernières 24h)
- [x] Scripts de génération créés
- [ ] Dashboard Kibana vérifié avec période "Last 7 days"
- [ ] Toutes les visualisations affichent des données

## 🎯 Prochaines Étapes

1. Ouvrez Kibana et vérifiez que les graphiques fonctionnent
2. Si nécessaire, ajustez la période de temps
3. Relancez `generate-realtime-data.py` quotidiennement pour des données fraîches
4. Créez de nouvelles visualisations selon vos besoins

---

**Date de résolution** : 2 janvier 2026
**Scripts créés** : 3 (inject-recent-data.py, fix-kibana-visualizations.py, generate-realtime-data.py)
**Données injectées** : 740 nouveaux documents
