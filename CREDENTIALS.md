# 🔐 Identifiants et Accès - Monitoring SaaS

## Services Accessibles via Navigateur

### Mongo Express (Interface MongoDB)
- **URL** : http://localhost:8081
- **Username** : `admin`
- **Password** : `admin123`
- **Description** : Interface d'administration pour MongoDB

### Kibana (Visualisation ELK)
- **URL** : http://localhost:5601
- **Authentification** : Aucune (désactivée pour le développement)
- **Description** : Dashboard de visualisation des logs

### Flask WebApp
- **URL** : http://localhost:8000
- **Authentification** : Aucune
- **Description** : Interface d'upload de fichiers

### Elasticsearch
- **URL** : http://localhost:9200
- **Authentification** : Aucune (désactivée pour le développement)
- **Description** : API REST Elasticsearch

## Services CLI/Programmatiques

### MongoDB
- **Host** : `localhost:27017`
- **Connexion** : `mongodb://localhost:27017`
- **CLI** : `docker exec -it mongodb mongosh`

### Redis
- **Host** : `localhost:6379`
- **CLI** : `docker exec -it redis redis-cli`

### Logstash
- **Port** : 5044
- **Logs** : `docker logs -f logstash`

## Notes de Sécurité

⚠️ **IMPORTANT** : Ces configurations sont prévues pour le **développement uniquement**.

Pour la production :
- Activez l'authentification sur Elasticsearch/Kibana (X-Pack Security)
- Changez tous les mots de passe par défaut
- Utilisez HTTPS/TLS pour tous les services
- Activez l'authentification MongoDB avec des utilisateurs dédiés
- Configurez Redis avec un mot de passe
- Utilisez Docker Secrets pour les credentials
- Activez le rate limiting sur l'API Flask

## Variables d'Environnement

Voir le fichier `.env` à la racine du projet pour les configurations.

---

**Dernière mise à jour** : 25 novembre 2025
