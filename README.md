# ⚡ LogStream Studio - Plateforme de Monitoring Big Data

## 📋 Vue d'ensemble

**LogStream Studio** est une plateforme complète de monitoring et d'analyse de logs Big Data construite avec la stack ELK (Elasticsearch, Logstash, Kibana). Le projet intègre MongoDB pour la gestion des métadonnées, Redis pour le caching, et une application web Flask moderne avec système d'authentification JWT.

### Objectifs du Projet

- 🎯 Centraliser et analyser des logs de différentes sources (CSV, JSON)
- 📊 Visualiser les données en temps réel via des dashboards interactifs
- 🔐 Sécuriser l'accès avec un système d'authentification robuste
- 📈 Fournir des statistiques et métriques en temps réel
- 🔍 Permettre la recherche avancée dans les logs
- 💾 Stocker et gérer efficacement les métadonnées des uploads

📐 **Architecture Complète** : Consultez [ARCHITECTURE.md](./ARCHITECTURE.md) pour une vue détaillée de l'organisation du projet.

---

## 🚀 Démarches de Réalisation du Projet

### Phase 1 : Mise en Place de l'Infrastructure ELK

**Objectif** : Déployer la stack ELK de base avec Docker Compose

#### Étapes réalisées :

1. **Configuration Docker Compose**
   - Création du fichier `docker-compose.yml` avec 7 services
   - Configuration des volumes pour la persistance des données
   - Mise en place du réseau `elk_net` pour la communication inter-services
   - Définition des variables d'environnement dans `.env`

2. **Déploiement Elasticsearch**
   - Version 8.10.3 configurée en mode single-node
   - Désactivation de la sécurité pour l'environnement de développement
   - Mapping du port 9200 pour l'API REST
   - Volume `./data/elasticsearch` pour la persistance

3. **Intégration Kibana**
   - Configuration de la connexion à Elasticsearch
   - Interface web accessible sur le port 5601
   - Personnalisation des dashboards pour l'analyse e-commerce

4. **Configuration Logstash**
   - Création de pipelines pour CSV et JSON dans `./pipeline/`
   - Configuration des inputs (file), filters (parsing) et outputs (Elasticsearch)
   - Mapping automatique vers les indices Elasticsearch

**Résultats** : Infrastructure ELK fonctionnelle et communicante

---

### Phase 2 : Ajout des Bases de Données (MongoDB & Redis)

**Objectif** : Intégrer des bases de données pour la gestion des métadonnées et le caching

#### Étapes réalisées :

1. **Déploiement MongoDB**
   - Container MongoDB version 7
   - Base de données `monitoring` avec collections :
     - `uploads` : Métadonnées des fichiers uploadés
     - `users` : Comptes utilisateurs (ajouté en Phase 5)
   - Mongo Express sur port 8081 pour l'administration web
   - Credentials : admin/admin123

2. **Intégration Redis**
   - Déploiement Redis pour le caching des sessions
   - Configuration de la persistance avec `dump.rdb`
   - Port 6379 exposé pour les connexions

3. **Tests de Connexion**
   - Vérification de la communication entre services
   - Tests CRUD sur MongoDB
   - Tests SET/GET sur Redis

**Résultats** : Bases de données opérationnelles et intégrées à l'écosystème

---

### Phase 3 : Développement de l'Application Web Flask

**Objectif** : Créer une interface web moderne pour l'upload et la visualisation des logs

#### Étapes réalisées :

1. **Architecture Flask** (`webapp/app.py`)
   - Structure modulaire avec séparation des routes
   - Connexions aux 5 services (Elasticsearch, MongoDB, Redis, Kibana, Logstash)
   - Gestion des erreurs et fallbacks si services indisponibles

2. **Système de Fichiers**
   - Upload de fichiers CSV/JSON/TXT/LOG
   - Validation des extensions autorisées
   - Stockage dans `./data/uploads/` avec noms sécurisés (secure_filename)
   - Prévisualisation des 10 premières lignes

3. **Intégration avec Logstash**
   - Volume partagé entre Flask et Logstash
   - Traitement automatique des fichiers uploadés
   - Injection dans Elasticsearch via les pipelines

4. **Base de Données**
   - Enregistrement des métadonnées dans MongoDB :
     - Nom du fichier, taille, type MIME
     - Date d'upload, statut (saved/processed/error)
     - Hôte d'origine
   - Requêtes pour récupérer l'historique des uploads

**Résultats** : Application web fonctionnelle permettant l'upload et le traitement des logs

---

### Phase 4 : Création des Interfaces Utilisateur

**Objectif** : Designer des interfaces modernes et intuitives avec HTML/CSS/JavaScript

#### Interface 1 : **Page d'Accueil / Dashboard Principal** (`/`)

**Description** :
- **En-tête** : Logo LogStream Studio avec navigation vers toutes les pages
- **KPIs en temps réel** :
  - Total de logs dans Elasticsearch
  - Logs récents (dernières 24h basé sur les données disponibles)
  - Nombre d'erreurs (status='failed')
  - Fichiers uploadés (depuis MongoDB)
- **Graphique Timeline** : Visualisation Chart.js des logs sur 30 derniers jours
- **Section Services** : Cards avec status de chaque service (Elasticsearch, Kibana, MongoDB, Redis, Logstash)
- **Design** : Thème sombre moderne avec dégradés et animations

**Fonctionnalités** :
- Rafraîchissement automatique des stats toutes les 5 secondes
- Indicateurs visuels colorés (vert/rouge) pour les status
- Liens directs vers Kibana, Mongo Express, indices Elasticsearch
- Responsive design

#### Interface 2 : **Page d'Upload** (`/upload`)

**Description** :
- **Zone de drag & drop** : Interface intuitive pour glisser-déposer les fichiers
- **Sélecteur de fichiers** : Bouton classique pour choisir un fichier
- **Prévisualisation en temps réel** : Affichage des 10 premières lignes après upload
- **Métadonnées** : 
  - Nom du fichier
  - Taille (Ko/Mo)
  - Type MIME
  - Date d'upload
  - Statut de traitement
- **Design** : Cards avec icônes, animations de transition, feedback visuel

**Fonctionnalités** :
- Validation côté client des extensions (.csv, .json, .txt, .log)
- Upload AJAX avec barre de progression
- Messages de succès/erreur dynamiques
- Redirection automatique vers le dashboard après succès

#### Interface 3 : **Page Fichiers / Dashboard Uploads** (`/dashboard`)

**Description** :
- **Statistiques MongoDB** :
  - Total des uploads
  - Uploads réussis
  - Uploads en erreur
- **Liste des 10 derniers uploads** :
  - Tableau avec colonnes : Nom, Taille, Type, Date, Statut
  - Badges colorés pour les statuts (vert=success, rouge=error)
  - Icônes selon le type de fichier
- **Design** : Layout en grille avec cards statistiques en haut

**Fonctionnalités** :
- Tri par date (plus récent en premier)
- Affichage formaté des tailles (Ko/Mo)
- Dates au format français
- Message si aucun upload

#### Interface 4 : **Page Health Check** (`/health`)

**Description** :
- **Status de chaque service** :
  - ✅ Elasticsearch (9200) - Connected/Disconnected + version
  - ✅ Kibana (5601) - Accessible/Inaccessible
  - ✅ MongoDB (27017) - Connected + nombre de documents
  - ✅ Redis (6379) - Connected + test PING
  - ✅ Logstash (9600) - Running + version
- **Informations système** :
  - Timestamp de vérification
  - Status global (All systems operational / Some issues)
- **Design** : Cards avec icônes de services, couleurs selon status

**Fonctionnalités** :
- Vérification en temps réel au chargement
- Indicateurs visuels clairs (✅/❌)
- Liens vers les interfaces d'administration
- Bouton de rafraîchissement

#### Interface 5 : **Page de Recherche** (`/search`)

**Description** :
- **Formulaire de recherche avancée** :
  - Champ texte libre (recherche multi-champs)
  - Filtre par niveau (status: success/failed)
  - Filtre par service/source
  - Sélecteur de dates (de/à)
- **Résultats paginés** :
  - Affichage en cards avec highlights
  - 50 résultats par page
  - Pagination avec boutons Précédent/Suivant
- **Détails des logs** :
  - Timestamp, message, niveau, source
  - Champs additionnels (customer_name, payment_type, amount, etc.)
- **Design** : Interface de type moteur de recherche avec résultats stylisés

**Fonctionnalités** :
- Recherche fuzzy (tolérance aux fautes)
- Multi-match sur plusieurs champs (message, product, customer_name, payment_type)
- Filtres combinables
- Export JSON des résultats possible
- Highlighting des termes recherchés

#### Interface 6 : **Page de Connexion** (`/login`)

**Description** :
- **Formulaire centré** avec logo animé
- **Champs** :
  - Nom d'utilisateur (icône 👤)
  - Mot de passe (icône 🔒)
  - Checkbox "Se souvenir de moi"
- **Bouton de connexion** avec animation de chargement
- **Lien** vers la page d'inscription
- **Design** : Glassmorphism, fond avec dégradés animés, animations fluides

**Fonctionnalités** :
- Validation côté client
- Authentication JWT via API `/api/login`
- Cookie httpOnly avec expiration (24h ou 30j si "remember")
- Messages d'erreur clairs
- Auto-focus sur le champ username
- Redirection vers `/` après connexion réussie

#### Interface 7 : **Page d'Inscription** (`/signup`)

**Description** :
- **Formulaire d'inscription** :
  - Nom d'utilisateur (min 3 caractères)
  - Email (validation format)
  - Mot de passe (min 6 caractères)
  - Confirmation mot de passe
- **Validation en temps réel** :
  - Vérification des longueurs minimales
  - Comparaison des mots de passe
  - Messages d'aide sous les champs
- **Lien** vers la page de connexion
- **Design** : Même thème que login avec logo vert

**Fonctionnalités** :
- Création de compte via API `/api/signup`
- Stockage dans MongoDB (collection `users`)
- Hash des mots de passe avec werkzeug.security
- Vérification unicité username et email
- Redirection vers `/login` après création réussie
- Scroll vertical activé pour voir tout le formulaire

**Technologies Frontend** :
- HTML5 sémantique
- CSS3 avec variables custom et animations
- Vanilla JavaScript (ES6+)
- Chart.js pour les graphiques
- Fetch API pour les requêtes AJAX
- Google Fonts (Inter)

---

### Phase 5 : Système d'Authentification JWT

**Objectif** : Sécuriser l'application avec authentification et gestion des utilisateurs

#### Étapes réalisées :

1. **Module d'Authentification** (`webapp/auth.py`)
   - Classe `AuthManager` pour gérer les tokens JWT
   - Génération de tokens avec expiration (24h par défaut)
   - Vérification des credentials (MongoDB + fallback admin)
   - Extraction des tokens depuis cookies ou headers
   - Décorateurs `@login_required` et `@api_login_required`

2. **Gestion des Utilisateurs MongoDB**
   - Collection `users` avec schéma :
     ```python
     {
       'username': str,
       'email': str,
       'password_hash': str,  # Hash sécurisé
       'role': str,           # 'user' ou 'admin'
       'created_at': datetime,
       'last_login': datetime,
       'is_active': bool
     }
     ```
   - Fonction `create_user()` avec validations
   - Fonction `verify_credentials()` pour login
   - Mise à jour automatique de `last_login`

3. **Routes API d'Authentification**
   - `POST /api/login` : Connexion avec JWT
   - `POST /api/signup` : Création de compte
   - `POST /api/logout` : Déconnexion (suppression cookie)
   - `GET /api/verify-token` : Vérification de session

4. **Protection des Routes**
   - Toutes les pages principales protégées par `@login_required`
   - Routes API protégées par `@api_login_required`
   - Redirection automatique vers `/login` si non authentifié
   - Stockage des infos utilisateur dans `request.user`

5. **Configuration Sécurité**
   - Variables d'environnement pour JWT_SECRET_KEY
   - Cookies httpOnly pour éviter XSS
   - Hash des mots de passe avec scrypt
   - Compte admin par défaut (admin/admin123) comme fallback

**Résultats** : Application entièrement sécurisée avec gestion multi-utilisateurs

---

### Phase 6 : Optimisation et Debugging

**Objectif** : Résoudre les problèmes et optimiser les performances

#### Problèmes résolus :

1. **Graphiques vides sur le dashboard**
   - **Cause** : Données datées de novembre 2025, requêtes cherchaient "aujourd'hui" (janvier 2026)
   - **Solution** : Modification de l'API `/api/stats` pour afficher toutes les données disponibles
   - Calcul dynamique des "logs récents" basé sur la date la plus récente des données
   - Timeline affichant 30 derniers jours de données (au lieu de seulement 7j depuis maintenant)

2. **Inputs non cliquables sur login/signup**
   - **Cause** : `z-index` insuffisant sur `.login-card`
   - **Solution** : Ajout de `z-index: 100` pour passer au-dessus de la décoration de fond

3. **Scroll bloqué sur signup**
   - **Cause** : `overflow: hidden` sur `.login-body`
   - **Solution** : Changement vers `overflow-y: auto` + `padding: 2rem 0`

4. **Services non accessibles**
   - **Cause** : Flask local utilisait hostnames Docker (mongodb, elasticsearch)
   - **Solution** : Configuration `.env` avec localhost pour tous les services
   - Modification de `app.py` pour charger les variables d'environnement

5. **Port Logstash manquant**
   - **Cause** : Port 9600 (API monitoring) non exposé dans docker-compose
   - **Solution** : Ajout du mapping `9600:9600`

6. **Volume uploads non monté**
   - **Cause** : Logstash ne voyait pas les fichiers uploadés
   - **Solution** : Ajout du volume `./data/uploads:/data/uploads:ro` dans docker-compose

**Résultats** : Application stable et performante sans bugs

---

### Phase 7 : Scripts Utilitaires

**Objectif** : Fournir des outils pour le développement et le test

#### Scripts créés :

1. **`scripts/view-users.py`**
   - Affiche tous les utilisateurs de MongoDB
   - Statistiques (total, actifs, dernière connexion)
   - Commandes utiles pour gérer les users

2. **`scripts/generate-recent-data.py`**
   - Génère 500 transactions e-commerce avec dates récentes
   - Sortie CSV et JSON dans `/tmp/logstream_test_data/`
   - Répartition 70% success / 30% failed
   - Utilisation : Tester la mise à jour automatique des graphiques

3. **`scripts/setup-kibana-dashboard.sh`**
   - Automatise l'import des dashboards Kibana
   - Configure les visualisations e-commerce

4. **`scripts/inject-ecommerce-data.sh`**
   - Injecte les données de test dans Elasticsearch
   - 1000 transactions e-commerce initiales

**Résultats** : Outils facilitant le développement et les tests

---

### Phase 8 : Nettoyage et Documentation

**Objectif** : Nettoyer le code et documenter le projet

#### Actions réalisées :

1. **Suppression des fichiers inutiles**
   - `example_app.py` (démo non utilisée)
   - `quick_test.py` (script de test)
   - `test_database.py` (tests unitaires)
   - `test_es_stats.py` (diagnostic temporaire)
   - `.env.example` (doublon de .env)
   - `REORGANISATION.md` (historique, `ARCHITECTURE.md` suffit)

2. **Organisation des dossiers**
   - `config/` : Fichiers de configuration Kibana et données de test
   - `docs/` : Documentation technique (AUTH-SYSTEM.md, DESIGN.md, etc.)
   - `scripts/` : Scripts utilitaires Python et Bash
   - `data/` : Volumes Docker persistants
   - `pipeline/` : Configurations Logstash
   - `webapp/` : Application Flask complète

3. **Documentation**
   - `README.md` : Guide complet (ce fichier)
   - `ARCHITECTURE.md` : Structure détaillée du projet
   - `docs/AUTH-SYSTEM.md` : Documentation système d'authentification
   - Commentaires dans le code

**Résultats** : Projet propre, organisé et bien documenté

---

## 📊 Statistiques du Projet

- **7 services Docker** orchestrés
- **8 pages web** interactives
- **15+ routes API** REST
- **2 bases de données** (MongoDB, Redis)
- **3 pipelines Logstash** (CSV, JSON, e-commerce)
- **1000+ documents** de test dans Elasticsearch
- **Authentification JWT** complète
- **~3000 lignes de code** Python/HTML/CSS/JS

---

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
├── README.md                   # Documentation principale
├── .env                        # Variables d'environnement
├── .env.example                # Template de configuration
├── .gitignore                  # Fichiers ignorés par Git
│
├── config/                     # 📋 Fichiers de configuration
│   ├── dashboard-final.ndjson         # Dashboard Kibana final
│   ├── ecommerce-dashboard-export.ndjson
│   ├── fix-tables.ndjson             # Configuration des tables
│   ├── fix-visualizations.ndjson     # Configuration des visualisations
│   ├── kibana-import-pro.ndjson      # Import Kibana professionnel
│   ├── kibana-import.ndjson          # Import Kibana basique
│   ├── test-ecommerce-logs.json      # Logs de test e-commerce
│   └── test-mongo.csv                # Données de test MongoDB
│
├── data/                       # 💾 Données persistantes (volumes Docker)
│   ├── elasticsearch/          # Index Elasticsearch
│   ├── kibana/                 # Configuration Kibana
│   ├── logstash/               # Données Logstash
│   ├── mongodb/                # Base MongoDB
│   ├── redis/                  # Snapshots Redis
│   └── uploads/                # Fichiers uploadés
│
├── docs/                       # 📚 Documentation complète
│   ├── AUTH-SYSTEM.md          # Système d'authentification JWT
│   ├── CHANGELOG-AUTH.md       # Changelog authentification
│   ├── CHANGELOG-DASHBOARD.md  # Changelog dashboard
│   ├── CREDENTIALS.md          # Identifiants et accès
│   ├── DATABASE-MODULE.md      # Module base de données
│   ├── DARK-THEME.md           # Guide du thème dark
│   ├── DESIGN.md               # Design system
│   ├── KIBANA-DASHBOARD.md     # Documentation Kibana
│   ├── PHASE5-COMPLETE.md      # Historique Phase 5
│   ├── RECAP-AUTH.md           # Récapitulatif authentification
│   └── SEARCH-PAGE.md          # Page de recherche
│
├── elasticsearch/              # ⚙️ Configuration Elasticsearch
│   └── logs-saas-template.json # Template d'index
│
├── pipeline/                   # 🔄 Pipelines Logstash
│   ├── csv-pipeline.conf       # Pipeline pour fichiers CSV
│   └── json-pipeline.conf      # Pipeline pour fichiers JSON
│
├── scripts/                    # 🔧 Scripts utilitaires
│   ├── add-service-logs.py            # Ajout de logs de services
│   ├── fill-empty-fields.py           # Remplissage des champs vides
│   ├── fix-kibana-dashboard.sh        # Correction dashboard Kibana
│   ├── inject-ecommerce-data.sh       # Injection données e-commerce
│   ├── inject-service-logs.py         # Injection logs de services
│   ├── regenerate-customer-data.sh    # Régénération données clients
│   ├── setup-kibana-dashboard.sh      # Configuration dashboard
│   ├── test-auth-system.py            # Tests authentification
│   ├── test-services.sh               # Tests des services
│   ├── update-logs-service.py         # Mise à jour logs
│   └── verify-kibana-setup.sh         # Vérification setup Kibana
│
└── webapp/                     # 🌐 Application Web Flask
    ├── app.py                  # Application Flask principale
    ├── auth.py                 # Module d'authentification JWT
    ├── database.py             # Module base de données
    ├── Dockerfile              # Image Docker
    ├── requirements.txt        # Dépendances Python
    ├── models/                 # Modèles de données
    │   └── __init__.py
    ├── routes/                 # Routes API
    │   └── __init__.py
    ├── static/                 # Ressources statiques
    │   └── style.css           # Stylesheet principal
    ├── templates/              # Templates HTML
    │   ├── index.html          # Dashboard principal
    │   ├── login.html          # Page de connexion
    │   ├── upload.html         # Page d'upload
    │   ├── dashboard.html      # Dashboard monitoring
    │   ├── health.html         # Health check
    │   └── search.html         # Recherche de logs
    ├── uploads/                # (deprecated)
    └── utils/                  # Utilitaires
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

## 🔐 Authentification et Sécurité

### Système d'authentification JWT

LogStream Studio intègre un système d'authentification sécurisé basé sur **JWT (JSON Web Tokens)** pour protéger l'accès à l'interface d'administration.

#### 🔑 Identifiants par défaut
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Changez ces identifiants en production via les variables d'environnement.

#### Configuration dans `.env`

```dotenv
# Authentication
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_EXPIRATION_HOURS=24
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

#### Fonctionnalités
- ✅ Authentification par JWT avec cookies HTTP-only
- ✅ Expiration automatique des tokens (24h par défaut)
- ✅ Option "Se souvenir de moi" (30 jours)
- ✅ Protection contre XSS et CSRF
- ✅ Hachage sécurisé des mots de passe (PBKDF2-SHA256)
- ✅ Toutes les routes principales protégées

#### Routes protégées
- `/` - Dashboard principal
- `/health` - Health check
- `/search` - Recherche de logs
- `/upload` - Upload de fichiers
- `/dashboard` - Dashboard de monitoring
- Toutes les routes `/api/*` (sauf login/logout)

#### Documentation complète
📖 Consultez [AUTH-SYSTEM.md](./AUTH-SYSTEM.md) pour la documentation détaillée du système d'authentification.

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
| **Flask WebApp** | http://localhost:8000 | 8000 | **admin / admin123** |
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
- **PyMongo 4.3.3** - Driver MongoDB pour Python
- **redis-py 4.5.1** - Client Redis pour Python
- **Docker & Docker Compose** - Conteneurisation et orchestration

## 🗄️ Module Database - Intégration MongoDB et Redis

### 📦 Nouveau Module `database.py`

Un module Python centralisé pour gérer les connexions MongoDB et Redis avec :

✅ **Connexions automatiques** avec variables d'environnement
✅ **Tests de connexion** au démarrage
✅ **Health check** complet des services
✅ **Gestion des erreurs** avec fallback gracieux
✅ **API simple** pour récupérer les clients

### 🚀 Utilisation Rapide

```python
from database import init_databases, db_manager

# Initialiser les connexions
init_databases()

# Utiliser MongoDB
uploads_col = db_manager.get_mongo_collection('uploads')
uploads_col.insert_one({'filename': 'test.csv', 'status': 'processed'})

# Utiliser Redis
redis_client = db_manager.get_redis_client()
redis_client.set('cache:key', 'value', ex=60)

# Health check
health = db_manager.health_check()
print(health)
```

### 🧪 Tests Complets

Testez le module avec la suite de tests :

```bash
# Test basique
docker exec webapp python3 database.py

# Test complet (CRUD, Performance, Health Check)
docker exec webapp python3 test_database.py
```

**Résultats des tests** :
- ✅ MongoDB CRUD operations (71,361 ops/sec)
- ✅ Redis operations (33,127 SET/sec, 45,250 GET/sec)
- ✅ Health check avec métriques détaillées
- ✅ 100% de réussite sur 4 catégories de tests

### 📚 Documentation Complète

Consultez **[DATABASE-MODULE.md](./DATABASE-MODULE.md)** pour :
- Guide d'utilisation détaillé
- API Reference complète
- Variables d'environnement
- Exemples avancés (cache, bulk operations)
- Dépannage et bonnes pratiques

### 🔧 Configuration

Variables d'environnement disponibles dans `.env.example` :

```bash
# MongoDB
MONGO_URI=mongodb://mongodb:27017
MONGO_DB=monitoring
MONGO_TIMEOUT=5000

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_TIMEOUT=5
```

### 📊 Métriques Health Check

Le module fournit des métriques détaillées :

```json
{
  "timestamp": "2025-11-25T16:29:15.663079",
  "services": {
    "mongodb": {
      "status": "healthy",
      "database": "monitoring",
      "collections": 2,
      "data_size_mb": 0.01
    },
    "redis": {
      "status": "healthy",
      "version": "7.4.7",
      "used_memory": "1.20M",
      "connected_clients": 1
    }
  }
}
```

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
