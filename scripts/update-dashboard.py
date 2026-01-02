#!/usr/bin/env python3
"""
Script pour mettre à jour le dashboard principal avec les nouvelles visualisations
et configurer la période de temps par défaut
"""
import requests
import json

KIBANA_URL = "http://localhost:5601"
HEADERS = {
    "kbn-xsrf": "true",
    "Content-Type": "application/json"
}

def update_dashboard():
    """Mettre à jour le dashboard principal"""
    dashboard_id = "ecommerce-dashboard"
    
    print(f"🔍 Récupération du dashboard {dashboard_id}...")
    
    try:
        # Récupérer le dashboard actuel
        response = requests.get(
            f"{KIBANA_URL}/api/saved_objects/dashboard/{dashboard_id}",
            headers=HEADERS
        )
        
        if response.status_code != 200:
            print(f"❌ Dashboard non trouvé: {response.status_code}")
            return False
        
        dashboard = response.json()
        attributes = dashboard.get('attributes', {})
        
        print(f"✅ Dashboard trouvé: {attributes.get('title', 'Sans titre')}")
        
        # Mettre à jour les visualisations qui posent problème
        panels_str = attributes.get('panelsJSON', '[]')
        panels = json.loads(panels_str)
        
        print(f"📊 Nombre de panneaux: {len(panels)}")
        
        # Mapper les anciennes visualisations vers les nouvelles
        viz_mapping = {
            'success-rate-viz': 'success-rate-pie',
            'payment-types-viz': 'payment-types-pie',
            'products-by-category-viz': 'categories-bar',
            'top-customers-viz': 'top-customers-table',
            'top-errors-viz': 'top-errors-table'
        }
        
        updated = False
        for panel in panels:
            panel_id = panel.get('panelRefName', '')
            
            # Chercher les références dans les références du dashboard
            for ref in dashboard.get('references', []):
                if ref.get('name') == panel_id:
                    old_id = ref.get('id')
                    if old_id in viz_mapping:
                        new_id = viz_mapping[old_id]
                        print(f"   🔄 Mise à jour: {old_id} → {new_id}")
                        ref['id'] = new_id
                        updated = True
        
        if updated:
            # Sauvegarder le dashboard mis à jour
            print("\n💾 Sauvegarde du dashboard...")
            response = requests.put(
                f"{KIBANA_URL}/api/saved_objects/dashboard/{dashboard_id}",
                headers=HEADERS,
                json={
                    "attributes": attributes,
                    "references": dashboard.get('references', [])
                }
            )
            
            if response.status_code == 200:
                print("✅ Dashboard mis à jour avec succès!")
                return True
            else:
                print(f"❌ Erreur lors de la sauvegarde: {response.status_code}")
                print(response.text[:300])
        else:
            print("ℹ️  Aucune mise à jour nécessaire")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_simple_instructions():
    """Créer des instructions simples pour l'utilisateur"""
    print("\n" + "=" * 70)
    print("📝 INSTRUCTIONS POUR CORRIGER LES VISUALISATIONS")
    print("=" * 70)
    print("\nLe problème vient probablement de la période de temps sélectionnée.")
    print("Voici comment corriger:")
    print("\n🔧 Solution 1: Changer la période de temps")
    print("   1. Ouvrez: http://localhost:5601")
    print("   2. Allez dans le dashboard 'E-Commerce Analytics'")
    print("   3. En haut à droite, cliquez sur le calendrier/horloge")
    print("   4. Sélectionnez 'Last 30 days' ou 'Last 90 days'")
    print("   5. Cliquez sur 'Update'")
    print("   6. Les visualisations devraient maintenant afficher les données!")
    
    print("\n🔧 Solution 2: Utiliser les nouvelles visualisations")
    print("   1. Dans Kibana, allez dans 'Visualize Library'")
    print("   2. Vous y trouverez les visualisations corrigées:")
    print("      • Taux de Succès")
    print("      • Moyens de Paiement")
    print("      • Catégories Produits")
    print("      • Top 10 Clients VIP")
    print("      • Top 10 Erreurs")
    print("   3. Ouvrez chacune pour vérifier qu'elle affiche bien les données")
    print("   4. Si elles fonctionnent, ajoutez-les au dashboard:")
    print("      - Dans le dashboard, cliquez sur 'Edit'")
    print("      - Cliquez sur 'Add panel'")
    print("      - Sélectionnez la visualisation")
    print("      - Positionnez-la dans le dashboard")
    print("      - Cliquez sur 'Save'")
    
    print("\n📊 Vérification des données disponibles:")
    try:
        # Vérifier les données
        response = requests.get(
            "http://localhost:9200/logs-*/_search?size=0",
            headers={"Content-Type": "application/json"},
            json={"query": {"range": {"@timestamp": {"gte": "now-30d"}}}}
        )
        if response.status_code == 200:
            count = response.json().get('hits', {}).get('total', {}).get('value', 0)
            print(f"   ✅ {count} documents disponibles pour les 30 derniers jours")
    except:
        pass
    
    print("\n💡 Astuce:")
    print("   Si vous voyez 'No results found', c'est que la période de temps")
    print("   est trop courte. Élargissez-la à 30 jours minimum.")
    print("\n" + "=" * 70)

def main():
    print("=" * 70)
    print("🔧 MISE À JOUR DU DASHBOARD KIBANA")
    print("=" * 70)
    
    update_dashboard()
    create_simple_instructions()

if __name__ == "__main__":
    main()
