#!/usr/bin/env python3
"""
Script pour corriger les champs dans les visualisations Lens existantes
"""
import requests
import json

KIBANA_URL = "http://localhost:5601"
HEADERS = {"kbn-xsrf": "true", "Content-Type": "application/json"}

def fix_visualization(viz_id, field_mapping):
    """
    Corriger les champs d'une visualisation
    field_mapping: dict {old_field: new_field}
    """
    print(f"\n🔧 Correction de {viz_id}...")
    
    try:
        # Récupérer la visualisation
        response = requests.get(
            f"{KIBANA_URL}/api/saved_objects/lens/{viz_id}",
            headers=HEADERS
        )
        
        if response.status_code != 200:
            print(f"   ⚠️  Visualisation non trouvée")
            return False
        
        viz = response.json()
        state = viz['attributes']['state']
        
        # Parcourir les layers et columns
        layers = state.get('datasourceStates', {}).get('formBased', {}).get('layers', {})
        
        modified = False
        for layer_name, layer in layers.items():
            for col_name, col in layer.get('columns', {}).items():
                old_field = col.get('sourceField', '')
                
                # Vérifier si le champ doit être corrigé
                for old, new in field_mapping.items():
                    if old_field == old:
                        print(f"   🔄 Colonne {col_name}: {old} → {new}")
                        col['sourceField'] = new
                        modified = True
        
        if not modified:
            print(f"   ℹ️  Aucune modification nécessaire")
            return True
        
        # Sauvegarder
        response = requests.put(
            f"{KIBANA_URL}/api/saved_objects/lens/{viz_id}?overwrite=true",
            headers=HEADERS,
            json={"attributes": viz['attributes']}
        )
        
        if response.status_code == 200:
            print(f"   ✅ Visualisation mise à jour!")
            return True
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    print("=" * 70)
    print("🔧 CORRECTION DES CHAMPS DANS LES VISUALISATIONS LENS")
    print("=" * 70)
    
    # Définir les corrections à appliquer
    visualizations_to_fix = [
        {
            'id': 'success-rate-viz',
            'fields': {'status': 'status.keyword'}
        },
        {
            'id': 'payment-types-viz',
            'fields': {'payment_type': 'payment_type.keyword'}
        },
        {
            'id': 'products-by-category-viz',
            'fields': {'category': 'category.keyword'}
        },
        {
            'id': 'top-customers-viz',
            'fields': {'customer_name': 'customer_name.keyword'}
        },
        {
            'id': 'top-errors-viz',
            'fields': {'error_code': 'error_code.keyword'}
        }
    ]
    
    success_count = 0
    for viz in visualizations_to_fix:
        if fix_visualization(viz['id'], viz['fields']):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ CORRECTION TERMINÉE ({success_count}/{len(visualizations_to_fix)} visualisations)")
    print("=" * 70)
    print("\n📌 Prochaines étapes:")
    print("   1. Rafraîchissez votre page Kibana (F5)")
    print("   2. Le dashboard devrait maintenant afficher les données")
    print("   3. Sélectionnez 'Last 30 days' pour voir toutes les données")
    print("\n💡 Les champs utilisent maintenant le suffixe .keyword pour les agrégations")

if __name__ == "__main__":
    main()
