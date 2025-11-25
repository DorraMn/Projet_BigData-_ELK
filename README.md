# 📊 Monitoring SaaS - ELK Stack

## 📋 Description du Projet

Ce projet est une plateforme de monitoring SaaS basée sur la stack ELK (Elasticsearch, Logstash, Kibana) intégrée avec MongoDB, Redis et une application web Flask. La solution permet de télécharger, traiter et visualiser des fichiers de logs au format CSV et JSON.

## 🏗️ Architecture

Le projet est composé de **7 services Docker** orchestrés via Docker Compose :

### Services Principaux

1. **Elasticsearch** (Port: 9200)
   - Moteur de recherche et d'analyse pour le stockage des logs
   - Configuration single-node pour le développement
   - Persistance des données dans `./data/elasticsearch`

2. **Kibana** (Port: 5601)
   - Interface de visualisation des données Elasticsearch
   - Dashboard interactif pour l'analyse des logs
   - Persistance dans `./data/kibana`

3. **Logstash** (Port: 5044)
   - Pipeline de traitement des logs (CSV et JSON)
   - Configurations personnalisées dans `./pipeline`
   - Ingestion automatique des fichiers uploadés

4. **MongoDB** (Port: 27017)
   - Base de données NoSQL pour les métadonnées des fichiers
   - Stockage des informations d'upload
   - Persistance dans `./data/mongodb`

5. **Mongo Express** (Port: 8081)
   - Interface web d'administration pour MongoDB
   - Visualisation et gestion des bases de données
   - Authentification : admin / admin123

6. **Redis** (Port: 6379)
   - Cache en mémoire pour les sessions et données temporaires
   - Persistance dans `./data/redis`

7. **WebApp Flask** (Port: 8000)
   - Interface web pour le téléchargement de fichiers
   - API REST pour l'upload de logs
   - Gestion des métadonnées et prévisualisation

## 📁 Structure du Projet

```
projet/
├── docker-compose.yml          # Orchestration des services
├── README.md                   # Documentation (ce fichier)
├── CREDENTIALS.md              # Identifiants et accès
├── DESIGN.md                   # Documentation du design system
├── DARK-THEME.md               # Guide du thème dark
├── test-services.sh            # Script de test automatique
├── .env                        # Variables d'environnement
├── data/                       # Données persistantes
│   ├── elasticsearch/          # Index Elasticsearch
│   ├── kibana/                 # Config Kibana
│   ├── logstash/               # Data Logstash
│   ├── mongodb/                # Base MongoDB
│   ├── redis/                  # Snapshots Redis
│   └── uploads/                # Fichiers uploadés
├── elasticsearch/
│   └── logs-saas-template.json # Template d'index
├── pipeline/
│   ├── csv-pipeline.conf       # Pipeline Logstash CSV
│   └── json-pipeline.conf      # Pipeline Logstash JSON
└── webapp/
    ├── app.py                  # Application Flask (+ routes)
    ├── Dockerfile              # Image Docker webapp
    ├── requirements.txt        # Dépendances Python
    ├── templates/              # Templates HTML
    │   ├── index.html          # Page d'accueil moderne
    │   ├── upload.html         # Page d'upload avec drag & drop
    │   └── dashboard.html      # Dashboard avec statistiques
    ├── static/                 # Ressources statiques
    │   └── style.css           # Design system complet
    └── uploads/                # (deprecated, use data/uploads)
```

## 🚀 Installation et Démarrage

### Prérequis

- Docker (version 20.10+)
- Docker Compose (version 1.29+)
- 4 GB RAM minimum disponible pour Docker

### Variables d'Environnement

Créez un fichier `.env` à la racine du projet avec les valeurs suivantes :

```bash
# Versions ELK Stack
ELASTIC_VERSION=8.10.0
KIBANA_VERSION=8.10.0
LOGSTASH_VERSION=8.10.0

# Flask Configuration
FLASK_ENV=development
FLASK_RUN_PORT=8000
```

### Démarrage des Services

1. **Cloner le projet** (si nécessaire)
```bash
cd /home/dorrah/Bureau/projet
```

2. **Créer le fichier .env**
```bash
cat > .env << EOF
ELASTIC_VERSION=8.10.0
KIBANA_VERSION=8.10.0
LOGSTASH_VERSION=8.10.0
FLASK_ENV=development
FLASK_RUN_PORT=8000
EOF
```

3. **Lancer tous les services**
```bash
docker-compose up -d
```

4. **Vérifier l'état des services**
```bash
docker-compose ps
```

5. **Consulter les logs** (optionnel)
```bash
docker-compose logs -f
```

### Arrêt des Services

```bash
docker-compose down
```

Pour supprimer également les volumes de données :
```bash
docker-compose down -v
```

## 🎨 Interface Web Moderne - Dark Theme

L'application dispose d'une interface web professionnelle en **mode dark** avec :

- **🏠 Page d'Accueil** : Vue d'ensemble des services et fonctionnalités
- **📤 Page Upload** : Interface drag & drop pour uploader des fichiers
- **📊 Dashboard** : Statistiques et liste des uploads récents
- **🌙 Thème Dark** : Palette sombre élégante (Slate) avec effets glow
- **🎯 Design moderne** : Cards élevées, animations fluides, contraste optimal
- **📱 Responsive** : S'adapte à tous les écrans

📄 **Documentation design** :
- [DESIGN.md](./DESIGN.md) - Guide complet du design system
- [DARK-THEME.md](./DARK-THEME.md) - Détails du thème dark et palette

## 🔗 Liens de Test et Accès aux Services

### 📋 Tableau Récapitulatif des Accès

| Service | URL | Port | Authentification |
|---------|-----|------|------------------|
| **Flask WebApp** | http://localhost:8000 | 8000 | Aucune |
| **Kibana** | http://localhost:5601 | 5601 | Aucune |
| **Mongo Express** | http://localhost:8081 | 8081 | admin / admin123 |
| **Elasticsearch** | http://localhost:9200 | 9200 | Aucune |
| **MongoDB** | localhost:27017 | 27017 | Aucune |
| **Redis** | localhost:6379 | 6379 | Aucune |
| **Logstash** | - | 5044 | - |

### 🌐 Application Web Flask
- **URL principale** : http://localhost:8000
- **Page d'upload** : http://localhost:8000/upload
- **Description** : Interface pour télécharger des fichiers CSV/JSON

### 📊 Kibana (Visualisation)
- **URL** : http://localhost:5601
- **Usage** : 
  - Accédez à "Discover" pour explorer les logs
  - Créez des visualisations et dashboards
  - Index patterns à configurer : `logs-saas-csv*` et `logs-saas-json*`

### 🔍 Elasticsearch (API)
- **URL** : http://localhost:9200
- **Health check** : http://localhost:9200/_cluster/health
- **Liste des index** : http://localhost:9200/_cat/indices?v
- **Recherche logs CSV** : http://localhost:9200/logs-saas-csv/_search
- **Recherche logs JSON** : http://localhost:9200/logs-saas-json/_search

### 💾 MongoDB (Base de données)
- **Host** : localhost:27017
- **Connexion via CLI** :
```bash
docker exec -it mongodb mongosh
```
- **Commandes utiles** :
```javascript
use monitoring
db.uploads.find().pretty()  // Voir les métadonnées des uploads
```

### 🗄️ Mongo Express (Interface MongoDB)
- **URL** : http://localhost:8081
- **Authentification** :
  - Username : `admin`
  - Password : `admin123`
- **Fonctionnalités** :
  - ✅ Visualiser toutes les bases de données MongoDB
  - ✅ Parcourir la collection `monitoring.uploads`
  - ✅ Créer/modifier/supprimer des documents
  - ✅ Exporter des données en JSON/CSV
  - ✅ Exécuter des requêtes MongoDB
  - ✅ Gestion des index

**Guide d'utilisation rapide** :
1. Ouvrez http://localhost:8081 dans votre navigateur
2. Entrez les identifiants : `admin` / `admin123`
3. Cliquez sur la base de données `monitoring`
4. Sélectionnez la collection `uploads`
5. Visualisez les métadonnées des fichiers uploadés

### 🔴 Redis (Cache)
- **Host** : localhost:6379
- **Connexion via CLI** :
```bash
docker exec -it redis redis-cli
```

### 📥 Logstash (Pipeline)
- **Port** : 5044
- **Logs en temps réel** :
```bash
docker logs -f logstash
```

## 📤 Utilisation - Upload de Fichiers

### Via l'Interface Web

1. Accédez à http://localhost:8000/upload
2. Sélectionnez un fichier CSV ou JSON
3. Cliquez sur "Upload"
4. Visualisez la prévisualisation des données

### Via API (cURL)

**Upload d'un fichier CSV :**
```bash
curl -X POST -F "file=@votre_fichier.csv" http://localhost:8000/upload
```

**Upload d'un fichier JSON :**
```bash
curl -X POST -F "file=@votre_fichier.json" http://localhost:8000/upload
```

### Formats de Fichiers Supportés

#### CSV
```csv
timestamp,level,message
2024-01-01T10:00:00Z,INFO,Application started
2024-01-01T10:05:00Z,ERROR,Connection failed
```

#### JSON
```json
{"timestamp": "2024-01-01T10:00:00Z", "level": "INFO", "message": "Application started"}
{"timestamp": "2024-01-01T10:05:00Z", "level": "ERROR", "message": "Connection failed"}
```

## 🔄 Pipeline de Traitement des Logs

### Workflow

1. **Upload** → Fichier téléchargé via Flask (`/upload`)
2. **Sauvegarde** → Stocké dans `./data/uploads/`
3. **Métadonnées** → Enregistrées dans MongoDB (collection `uploads`)
4. **Traitement** → Logstash détecte et parse le fichier
5. **Indexation** → Les logs sont envoyés vers Elasticsearch
6. **Visualisation** → Données disponibles dans Kibana

### Pipelines Logstash

- **CSV Pipeline** : Parse les fichiers `.csv` → Index `logs-saas-csv`
- **JSON Pipeline** : Parse les fichiers `.json` → Index `logs-saas-json`

## 📊 Configuration Kibana

### Première Configuration

1. Accédez à http://localhost:5601
2. Allez dans **Stack Management** → **Index Patterns**
3. Créez un index pattern :
   - Pattern name : `logs-saas-*`
   - Time field : `@timestamp`
4. Accédez à **Discover** pour explorer vos logs

### Création de Visualisations

- **Management** → **Visualize Library** → **Create visualization**
- Types disponibles : Line chart, Bar chart, Pie chart, Data table, etc.

## 🛠️ Dépannage

### ⚠️ Problème de Permissions (Erreur EACCES ou AccessDeniedException)

**Symptômes** : Elasticsearch ou Kibana redémarrent en boucle avec des erreurs de permissions

**Solution** :
```bash
# Arrêter tous les services
docker compose down

# Corriger les permissions des dossiers de données
sudo chmod -R 777 data/

# Ou recréer les dossiers si nécessaire
sudo rm -rf data/elasticsearch data/kibana data/logstash
sudo mkdir -p data/elasticsearch data/kibana data/logstash data/uploads
sudo chmod -R 777 data/

# Redémarrer les services
docker compose up -d
```

### Les services ne démarrent pas

```bash
# Vérifier les logs
docker compose logs

# Vérifier l'état des services
docker compose ps

# Redémarrer un service spécifique
docker compose restart webapp
docker compose restart elasticsearch
```

### Elasticsearch ne démarre pas (mémoire insuffisante)

Ajustez les paramètres Java dans `docker-compose.yml` :
```yaml
ES_JAVA_OPTS=-Xms256m -Xmx256m  # Réduit de 512m à 256m
```

### Kibana en boucle de redémarrage

1. **Vérifier les logs** :
```bash
docker logs kibana --tail 50
```

2. **Si erreur de permissions**, suivre la solution ci-dessus

3. **Attendre qu'Elasticsearch soit prêt** (peut prendre 30-60 secondes au démarrage)

### Les fichiers uploadés ne sont pas traités

1. Vérifiez que Logstash est démarré :
```bash
docker compose ps logstash
```

2. Consultez les logs Logstash :
```bash
docker logs -f logstash
```

3. Vérifiez que les fichiers sont dans `./data/uploads/`

### MongoDB n'est pas accessible

```bash
# Redémarrer MongoDB
docker compose restart mongodb

# Vérifier les logs
docker logs mongodb
```

## 🧪 Tests et Validation

### ⚡ Test Rapide de Tous les Services

Utilisez le script de test automatisé :

```bash
./test-services.sh
```

Ce script vérifie automatiquement :
- ✅ Accessibilité de tous les services web
- ✅ État des APIs (Elasticsearch, Flask)
- ✅ Connexion MongoDB et Redis
- ✅ État des conteneurs Docker

### Test Complet du Workflow

1. **Créer un fichier de test** :
```bash
cat > test.csv << EOF
timestamp,level,message
2024-11-08T10:00:00Z,INFO,Test log 1
2024-11-08T10:01:00Z,WARN,Test log 2
2024-11-08T10:02:00Z,ERROR,Test log 3
EOF
```

2. **Upload le fichier** :
```bash
curl -X POST -F "file=@test.csv" http://localhost:8000/upload
```

3. **Vérifier dans MongoDB** (2 options) :

**Via CLI** :
```bash
docker exec -it mongodb mongosh --eval "use monitoring; db.uploads.find().pretty()"
```

**Via Mongo Express** :
- Ouvrez http://localhost:8081
- Connectez-vous avec `admin` / `admin123`
- Naviguez vers la base `monitoring` → collection `uploads`
- Visualisez les métadonnées du fichier uploadé

4. **Attendre 10-30 secondes** pour le traitement Logstash

5. **Vérifier dans Elasticsearch** :
```bash
curl http://localhost:9200/logs-saas-csv/_search?pretty
```

6. **Visualiser dans Kibana** : http://localhost:5601

## 📈 Monitoring et Métriques

### Health Checks

```bash
# Elasticsearch
curl http://localhost:9200/_cluster/health?pretty

# Webapp Flask
curl http://localhost:8000


# Kibana
curl http://localhost:5601/api/status
```

### Statistiques des Index

```bash
# Nombre de documents par index
curl http://localhost:9200/_cat/count/logs-saas-*?v

# Taille des index
curl http://localhost:9200/_cat/indices/logs-saas-*?v&s=store.size:desc
```

## 🔐 Sécurité

⚠️ **Note de sécurité** : Cette configuration est prévue pour le **développement uniquement**.

### Identifiants par Défaut

📄 Consultez le fichier **[CREDENTIALS.md](./CREDENTIALS.md)** pour la liste complète des identifiants.

**Accès rapide** :
- Mongo Express : `admin` / `admin123`
- Autres services : Authentification désactivée en mode développement

### Pour la Production

Activez impérativement :
- ✅ L'authentification Elasticsearch/Kibana (X-Pack Security)
- ✅ HTTPS/TLS pour tous les services
- ✅ Variables d'environnement sécurisées (Docker Secrets)
- ✅ Authentification MongoDB avec utilisateurs dédiés
- ✅ Mot de passe Redis
- ✅ Rate limiting sur l'API Flask
- ✅ Changez tous les mots de passe par défaut

## 📝 Technologies Utilisées

- **Python 3.11** - Application Flask
- **Flask 2.3.2** - Framework web
- **Elasticsearch 8.10.3** - Moteur de recherche
- **Kibana 8.10.3** - Visualisation des logs
- **Logstash 8.10.3** - Pipeline de traitement
- **MongoDB 7** - Base de données NoSQL
- **Mongo Express 1.0.2** - Interface d'administration MongoDB
- **Redis 7** - Cache en mémoire
- **Docker & Docker Compose** - Conteneurisation et orchestration

## 🎯 Cas d'Usage et Exemples

### Visualiser les Métadonnées dans Mongo Express

1. **Accès** : http://localhost:8081 (admin / admin123)
2. **Navigation** : Base `monitoring` → Collection `uploads`
3. **Visualisation** : Liste de tous les fichiers uploadés avec leurs métadonnées

### Requêtes MongoDB Utiles

```javascript
// Compter tous les uploads
db.uploads.countDocuments()

// Trouver les uploads en erreur
db.uploads.find({status: "error"})

// Statistiques par extension
db.uploads.aggregate([
  { $group: { _id: "$extension", count: { $sum: 1 } } }
])

// Uploads des dernières 24h
db.uploads.find({
  uploaded_at: { $gte: new Date(Date.now() - 24*60*60*1000).toISOString() }
})
```

### Pipeline ELK Complet

1. **Upload** → Flask enregistre le fichier et les métadonnées
2. **Stockage** → Fichier dans `data/uploads/`, métadonnées dans MongoDB
3. **Traitement** → Logstash parse et transforme les logs
4. **Indexation** → Elasticsearch stocke les logs indexés
5. **Visualisation** → Kibana pour l'analyse, Mongo Express pour les métadonnées

## 👥 Auteurs

Projet réalisé dans le cadre du cours de Monitoring et ELK Stack.

## 📅 Date

25 novembre 2025

---

**Bon monitoring ! 📊🚀**
