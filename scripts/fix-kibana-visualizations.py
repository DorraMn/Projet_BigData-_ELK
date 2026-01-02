#!/usr/bin/env python3
"""
Script pour corriger les visualisations Kibana qui n'affichent pas de données
"""
import requests
import json
import time

KIBANA_URL = "http://localhost:5601"
HEADERS = {
    "kbn-xsrf": "true",
    "Content-Type": "application/json"
}

def wait_for_kibana():
    """Attendre que Kibana soit prêt"""
    print("⏳ Attente de Kibana...")
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get(f"{KIBANA_URL}/api/status", timeout=5)
            if response.status_code == 200:
                print("✅ Kibana est prêt!")
                return True
        except:
            pass
        time.sleep(2)
        if (i + 1) % 5 == 0:
            print(f"   Tentative {i + 1}/{max_attempts}...")
    return False

def get_data_views():
    """Récupérer les data views existants"""
    try:
        response = requests.get(
            f"{KIBANA_URL}/api/data_views",
            headers=HEADERS
        )
        if response.status_code == 200:
            data_views = response.json().get('data_view', [])
            print(f"📊 {len(data_views)} data views trouvés:")
            for dv in data_views:
                print(f"   - {dv.get('title')} (ID: {dv.get('id')})")
            return data_views
    except Exception as e:
        print(f"❌ Erreur: {e}")
    return []

def refresh_data_view(data_view_id):
    """Rafraîchir un data view pour qu'il détecte les nouveaux champs"""
    try:
        print(f"🔄 Rafraîchissement du data view {data_view_id}...")
        response = requests.post(
            f"{KIBANA_URL}/api/data_views/data_view/{data_view_id}/fields",
            headers=HEADERS
        )
        if response.status_code in [200, 201]:
            print(f"   ✅ Data view rafraîchi")
            return True
        else:
            print(f"   ⚠️  Code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    return False

def create_default_data_view():
    """Créer un data view par défaut si nécessaire"""
    try:
        # Vérifier si logs-* existe déjà
        response = requests.get(
            f"{KIBANA_URL}/api/data_views",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data_views = response.json().get('data_view', [])
            logs_pattern = [dv for dv in data_views if dv.get('title') == 'logs-*']
            
            if logs_pattern:
                print(f"✅ Data view 'logs-*' existe déjà")
                return logs_pattern[0].get('id')
        
        # Créer le data view
        print("📝 Création du data view 'logs-*'...")
        payload = {
            "data_view": {
                "title": "logs-*",
                "name": "Logs Stream",
                "timeFieldName": "@timestamp"
            }
        }
        
        response = requests.post(
            f"{KIBANA_URL}/api/data_views/data_view",
            headers=HEADERS,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            data_view_id = response.json().get('data_view', {}).get('id')
            print(f"   ✅ Data view créé avec l'ID: {data_view_id}")
            return data_view_id
        else:
            print(f"   ❌ Échec: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    return None

def set_default_index_pattern(data_view_id):
    """Définir le data view par défaut"""
    try:
        print(f"🎯 Configuration du data view par défaut...")
        response = requests.post(
            f"{KIBANA_URL}/api/data_views/default",
            headers=HEADERS,
            json={"data_view_id": data_view_id, "force": True}
        )
        
        if response.status_code in [200, 201]:
            print("   ✅ Data view par défaut configuré")
            return True
    except Exception as e:
        print(f"   ⚠️  {e}")
    return False

def main():
    print("=" * 70)
    print("🔧 CORRECTION DES VISUALISATIONS KIBANA")
    print("=" * 70)
    
    if not wait_for_kibana():
        print("❌ Impossible de se connecter à Kibana")
        return
    
    print("\n📋 Étape 1: Récupération des data views...")
    data_views = get_data_views()
    
    if not data_views:
        print("\n📝 Aucun data view trouvé, création d'un nouveau...")
        data_view_id = create_default_data_view()
        if data_view_id:
            set_default_index_pattern(data_view_id)
    else:
        print("\n🔄 Étape 2: Rafraîchissement des data views...")
        for dv in data_views:
            if 'logs' in dv.get('title', '').lower():
                refresh_data_view(dv.get('id'))
                set_default_index_pattern(dv.get('id'))
    
    print("\n" + "=" * 70)
    print("✅ CONFIGURATION TERMINÉE")
    print("=" * 70)
    print("\n📌 Instructions pour vérifier:")
    print("   1. Ouvrez Kibana: http://localhost:5601")
    print("   2. Allez dans Dashboard")
    print("   3. Cliquez sur le sélecteur de temps (en haut à droite)")
    print("   4. Sélectionnez 'Last 7 days' ou 'Last 30 days'")
    print("   5. Les graphiques devraient maintenant afficher les données")
    print("\n💡 Si les graphiques sont encore vides:")
    print("   - Vérifiez que le data view est 'logs-*'")
    print("   - Changez la plage de temps pour inclure les derniers jours")
    print("   - Rafraîchissez la page (Ctrl+R)")

if __name__ == "__main__":
    main()
