# 🐳 Guide de Conteneurisation Docker - LogStream Studio

## Vue d'ensemble de l'architecture

```
                                    ┌─────────────────┐
                                    │   Navigateur    │
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │    Frontend     │
                                    │  (Nginx:80)     │
                                    └────────┬────────┘
                     ┌───────────────────────┼───────────────────────┐
                     │                       │                       │
            ┌────────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
            │    Backend      │    │    Kibana       │    │  Static Files   │
            │  (Flask:8000)   │    │   (Port 5601)   │    │   (/static/)    │
            └────────┬────────┘    └────────┬────────┘    └─────────────────┘
                     │                      │
     ┌───────────────┼───────────────┐      │
     │               │               │      │
┌────▼────┐   ┌─────▼─────┐   ┌─────▼─────▼─────┐
│ MongoDB │   │   Redis   │   │  Elasticsearch  │
│ (27017) │   │  (6379)   │   │     (9200)      │
└─────────┘   └───────────┘   └─────────────────┘
```

---

## 📁 Structure des fichiers Docker

```
projet/
├── docker-compose.yml          # Orchestration des conteneurs
├── .env                        # Variables d'environnement
├── webapp/
│   ├── Dockerfile              # Image du backend Flask
│   ├── Dockerfile.frontend     # Image du frontend Nginx
│   ├── .dockerignore          # Fichiers exclus du build
│   ├── nginx.conf             # Configuration Nginx
│   ├── requirements.txt       # Dépendances Python
│   └── ...
├── pipeline/                   # Configurations Logstash
├── data/                       # Volumes de données (gitignore)
└── config/                     # Fichiers de configuration
```

---

## 🚀 Étape 1 : Comprendre les Dockerfiles

### Backend Flask (`webapp/Dockerfile`)

```dockerfile
# Image de base légère
FROM python:3.11-slim

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE=1    # Pas de fichiers .pyc
ENV PYTHONUNBUFFERED=1           # Logs en temps réel
ENV FLASK_APP=app.py

WORKDIR /app

# Installer les dépendances système (curl pour healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends curl

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Sécurité : utilisateur non-root
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]
```

**Points clés :**
- `python:3.11-slim` : Image légère (~150MB vs ~900MB pour l'image complète)
- `HEALTHCHECK` : Permet à Docker de vérifier si l'app fonctionne
- Utilisateur non-root pour la sécurité

### Frontend Nginx (`webapp/Dockerfile.frontend`)

```dockerfile
FROM nginx:alpine

# Copier les fichiers statiques
COPY static/ /usr/share/nginx/html/static/
COPY templates/ /usr/share/nginx/html/

# Configuration personnalisée
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Rôle de Nginx :**
- Servir les fichiers statiques (CSS, JS, images)
- Reverse proxy vers Flask (port 8000)
- Reverse proxy vers Kibana (port 5601)
- Compression gzip et cache

---

## 🔧 Étape 2 : Configuration docker-compose.yml

### Services et dépendances

| Service | Image | Port | Dépend de |
|---------|-------|------|-----------|
| elasticsearch | elasticsearch:8.10.3 | 9200 | - |
| kibana | kibana:8.10.3 | 5601 | elasticsearch |
| logstash | logstash:8.10.3 | 5044 | elasticsearch |
| mongodb | mongo:7 | 27017 | - |
| redis | redis:7-alpine | 6379 | - |
| webapp | Build local | 8000 | mongodb, redis, elasticsearch |
| frontend | Build local | 80 | webapp, kibana |

### Ordre de démarrage

```
1. elasticsearch ──┬──▶ 2. kibana ──────────┐
                   │                        │
                   └──▶ 3. logstash         │
                                            │
   mongodb ────────┬                        │
                   │                        │
   redis ──────────┼──▶ 4. webapp ──────────┼──▶ 5. frontend
                   │                        │
                   └────────────────────────┘
```

### Healthchecks

Chaque service a un healthcheck pour s'assurer qu'il est prêt :

```yaml
elasticsearch:
  healthcheck:
    test: ["CMD-SHELL", "curl -s http://localhost:9200/_cluster/health"]
    interval: 30s
    timeout: 10s
    retries: 5
    start_period: 60s
```

---

## 📦 Étape 3 : Volumes et persistance

### Volumes nommés (recommandé)

```yaml
volumes:
  elasticsearch_data:   # Données Elasticsearch
  kibana_data:          # Configuration Kibana
  mongodb_data:         # Base de données MongoDB
  redis_data:           # Cache Redis
```

**Avantages :**
- Gérés par Docker
- Faciles à sauvegarder
- Persistent après `docker-compose down`

### Voir les volumes

```bash
docker volume ls
docker volume inspect elasticsearch_data
```

---

## 🌐 Étape 4 : Réseau Docker

```yaml
networks:
  elk_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

**Communication interne :**
- Les conteneurs communiquent par leur nom (DNS interne)
- `webapp` → `http://elasticsearch:9200`
- `kibana` → `http://elasticsearch:9200`
- `frontend` → `http://webapp:8000`

---

## 🚀 Étape 5 : Commandes de démarrage

### Démarrer tous les services

```bash
# Construire et démarrer
docker-compose up -d --build

# Voir les logs
docker-compose logs -f

# Voir l'état des services
docker-compose ps
```

### Démarrer un service spécifique

```bash
# Reconstruire uniquement le backend
docker-compose up -d --build webapp

# Reconstruire uniquement le frontend
docker-compose up -d --build frontend
```

### Arrêter les services

```bash
# Arrêter sans supprimer les volumes
docker-compose down

# Arrêter ET supprimer les volumes (⚠️ perte de données)
docker-compose down -v
```

---

## 🔍 Étape 6 : Vérification

### Tester chaque service

```bash
# Elasticsearch
curl http://localhost:9200/_cluster/health?pretty

# Kibana
curl http://localhost:5601/api/status

# Backend Flask
curl http://localhost:8000/health

# Frontend Nginx
curl http://localhost/

# MongoDB
docker exec -it mongodb mongosh --eval "db.adminCommand('ping')"

# Redis
docker exec -it redis redis-cli ping
```

### Voir les logs d'un service

```bash
docker-compose logs -f webapp
docker-compose logs -f elasticsearch
docker-compose logs --tail=100 frontend
```

---

## 🛠️ Étape 7 : Debugging

### Entrer dans un conteneur

```bash
# Backend Flask
docker exec -it webapp bash

# Elasticsearch
docker exec -it elasticsearch bash

# MongoDB
docker exec -it mongodb mongosh
```

### Voir les ressources utilisées

```bash
docker stats
```

### Reconstruire complètement

```bash
# Supprimer tout et reconstruire
docker-compose down -v --rmi all
docker-compose up -d --build
```

---

## 📊 Accès aux interfaces

| Service | URL | Identifiants |
|---------|-----|--------------|
| **Application** | http://localhost/ | (login requis) |
| **Backend API** | http://localhost:8000/ | - |
| **Kibana** | http://localhost:5601/ | - |
| **Mongo Express** | http://localhost:8081/ | admin / admin123 |
| **Elasticsearch** | http://localhost:9200/ | - |

---

## 🔒 Sécurité en production

### Variables d'environnement

Créer un fichier `.env.production` :

```env
FLASK_ENV=production
JWT_SECRET_KEY=your-super-secret-key-change-me
ADMIN_PASSWORD=secure-password-123
```

### Activer la sécurité Elasticsearch

```yaml
elasticsearch:
  environment:
    - xpack.security.enabled=true
    - ELASTIC_PASSWORD=changeme
```

### SSL/TLS pour Nginx

Ajouter dans `nginx.conf` :

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
}
```

---

## 📈 Optimisations

### Limiter les ressources

```yaml
webapp:
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
      reservations:
        cpus: '0.25'
        memory: 256M
```

### Multi-stage build (production)

```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["python", "-m", "flask", "run"]
```

---

## 🎯 Résumé des commandes

```bash
# Démarrer tout
docker-compose up -d --build

# Voir les logs
docker-compose logs -f

# État des services
docker-compose ps

# Arrêter
docker-compose down

# Reconstruire un service
docker-compose up -d --build webapp

# Nettoyer tout
docker-compose down -v --rmi all
docker system prune -af
```
