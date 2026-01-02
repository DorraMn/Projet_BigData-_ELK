# 🔧 Scripts Utilitaires

Ce dossier contient tous les scripts Python et Bash pour la gestion, le test et la maintenance de LogStream Studio.

## 📜 Scripts disponibles

### 🧪 Tests et Vérification

#### `test-services.sh`
Script principal pour tester tous les services Docker.
```bash
./scripts/test-services.sh
```
Vérifie :
- ✅ Elasticsearch (port 9200)
- ✅ Kibana (port 5601)
- ✅ MongoDB (port 27017)
- ✅ Redis (port 6379)
- ✅ Mongo Express (port 8081)
- ✅ Flask WebApp (port 8000)

#### `test-auth-system.py`
Tests complets du système d'authentification JWT.
```bash
python3 scripts/test-auth-system.py
```
Teste :
- Module d'authentification
- Routes Flask
- Templates
- Configuration
- Documentation

#### `verify-kibana-setup.sh`
Vérifie que Kibana est correctement configuré.
```bash
./scripts/verify-kibana-setup.sh
```

### 📊 Injection de Données

#### `inject-service-logs.py`
Injecte des logs de services dans Elasticsearch.
```bash
python3 scripts/inject-service-logs.py
```

#### `inject-ecommerce-data.sh`
Injecte des données e-commerce de test.
```bash
./scripts/inject-ecommerce-data.sh
```

#### `add-service-logs.py`
Ajoute des logs de services supplémentaires.
```bash
python3 scripts/add-service-logs.py
```

### 🔄 Maintenance et Mise à jour

#### `update-logs-service.py`
Met à jour les logs des services existants.
```bash
python3 scripts/update-logs-service.py
```

#### `fill-empty-fields.py`
Remplit les champs vides dans les logs.
```bash
python3 scripts/fill-empty-fields.py
```

#### `regenerate-customer-data.sh`
Régénère les données clients pour les tests.
```bash
./scripts/regenerate-customer-data.sh
```

### ⚙️ Configuration Kibana

#### `setup-kibana-dashboard.sh`
Configure automatiquement le dashboard Kibana.
```bash
./scripts/setup-kibana-dashboard.sh
```

#### `fix-kibana-dashboard.sh`
Répare les problèmes du dashboard Kibana.
```bash
./scripts/fix-kibana-dashboard.sh
```

## 🚀 Utilisation

### Rendre les scripts exécutables
```bash
chmod +x scripts/*.sh
```

### Exécuter tous les tests
```bash
# Test des services
./scripts/test-services.sh

# Test de l'authentification
python3 scripts/test-auth-system.py

# Vérification Kibana
./scripts/verify-kibana-setup.sh
```

### Workflow de développement

1. **Démarrer les services**
   ```bash
   docker compose up -d
   ```

2. **Tester les services**
   ```bash
   ./scripts/test-services.sh
   ```

3. **Injecter des données de test**
   ```bash
   python3 scripts/inject-service-logs.py
   ./scripts/inject-ecommerce-data.sh
   ```

4. **Configurer Kibana**
   ```bash
   ./scripts/setup-kibana-dashboard.sh
   ```

## 📋 Prérequis

### Pour les scripts Python
```bash
pip install -r webapp/requirements.txt
```

### Pour les scripts Bash
- `curl` - Pour les requêtes HTTP
- `jq` - Pour parser le JSON
- `docker` et `docker-compose` - Pour gérer les containers

## 📚 Documentation

Pour plus d'informations :
- Documentation générale : `/README.md`
- Documentation des docs : `/docs/`
- Configuration Kibana : `/docs/KIBANA-DASHBOARD.md`
- Système d'authentification : `/docs/AUTH-SYSTEM.md`

## 🆘 Support

En cas de problème avec un script :
1. Vérifiez que tous les services Docker sont démarrés
2. Consultez les logs : `docker compose logs <service>`
3. Vérifiez les permissions : `chmod +x scripts/*.sh`
4. Consultez la documentation dans `/docs/`
