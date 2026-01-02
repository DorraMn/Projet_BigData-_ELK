# 📋 Configuration Files

Ce dossier contient tous les fichiers de configuration pour les différents services du projet LogStream Studio.

## 📄 Fichiers

### Dashboards Kibana
- `dashboard-final.ndjson` - Dashboard Kibana final optimisé
- `ecommerce-dashboard-export.ndjson` - Export du dashboard e-commerce
- `kibana-import-pro.ndjson` - Configuration professionnelle pour import Kibana
- `kibana-import.ndjson` - Configuration basique pour import Kibana

### Visualisations Kibana
- `fix-tables.ndjson` - Configuration des tables Kibana
- `fix-visualizations.ndjson` - Configuration des visualisations Kibana

### Données de test
- `test-ecommerce-logs.json` - Logs de test pour le système e-commerce
- `test-mongo.csv` - Données de test pour MongoDB

## 🔄 Import des configurations

### Import d'un dashboard Kibana
```bash
curl -X POST "localhost:5601/api/saved_objects/_import" \
  -H "kbn-xsrf: true" \
  --form file=@config/dashboard-final.ndjson
```

### Utilisation des données de test
Les fichiers de test peuvent être utilisés avec les scripts d'injection dans le dossier `scripts/`.

## 📚 Documentation

Pour plus d'informations :
- Configuration Kibana : `/docs/KIBANA-DASHBOARD.md`
- Documentation complète : `/README.md`
