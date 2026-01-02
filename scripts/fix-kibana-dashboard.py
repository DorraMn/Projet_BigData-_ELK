#!/usr/bin/env python3
"""
Script pour corriger les visualisations Kibana qui affichent "No results found"
Recréer les visualisations avec les bons champs et agrégations
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
    for i in range(30):
        try:
            response = requests.get(f"{KIBANA_URL}/api/status", timeout=5)
            if response.status_code == 200:
                print("✅ Kibana est prêt!")
                return True
        except:
            pass
        time.sleep(2)
    return False

def get_data_view_id():
    """Récupérer l'ID du data view logs-*"""
    try:
        response = requests.get(f"{KIBANA_URL}/api/data_views", headers=HEADERS)
        if response.status_code == 200:
            data_views = response.json().get('data_view', [])
            for dv in data_views:
                if dv.get('title') == 'logs-*':
                    return dv.get('id')
    except Exception as e:
        print(f"❌ Erreur: {e}")
    return None

def create_visualization(vis_config):
    """Créer ou mettre à jour une visualisation"""
    vis_id = vis_config.get('id')
    vis_title = vis_config.get('title')
    
    try:
        # Vérifier si la visualisation existe
        response = requests.get(
            f"{KIBANA_URL}/api/saved_objects/visualization/{vis_id}",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            print(f"   ⚠️  {vis_title} existe déjà, mise à jour...")
            # Mettre à jour
            response = requests.put(
                f"{KIBANA_URL}/api/saved_objects/visualization/{vis_id}",
                headers=HEADERS,
                json={"attributes": vis_config['attributes']}
            )
        else:
            print(f"   📝 Création de {vis_title}...")
            # Créer
            response = requests.post(
                f"{KIBANA_URL}/api/saved_objects/visualization/{vis_id}",
                headers=HEADERS,
                json={"attributes": vis_config['attributes']}
            )
        
        if response.status_code in [200, 201]:
            print(f"   ✅ {vis_title} configuré!")
            return True
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    return False

def create_all_visualizations(data_view_id):
    """Créer toutes les visualisations manquantes"""
    
    visualizations = [
        {
            'id': 'success-rate-pie',
            'title': 'Taux de Succès',
            'attributes': {
                'title': 'Taux de Succès',
                'visState': json.dumps({
                    'title': 'Taux de Succès',
                    'type': 'pie',
                    'aggs': [
                        {
                            'id': '1',
                            'enabled': True,
                            'type': 'count',
                            'schema': 'metric',
                            'params': {}
                        },
                        {
                            'id': '2',
                            'enabled': True,
                            'type': 'terms',
                            'schema': 'segment',
                            'params': {
                                'field': 'status.keyword',
                                'size': 10,
                                'order': 'desc',
                                'orderBy': '1'
                            }
                        }
                    ],
                    'params': {
                        'type': 'pie',
                        'addTooltip': True,
                        'addLegend': True,
                        'legendPosition': 'right',
                        'isDonut': True
                    }
                }),
                'uiStateJSON': '{}',
                'description': '',
                'version': 1,
                'kibanaSavedObjectMeta': {
                    'searchSourceJSON': json.dumps({
                        'index': data_view_id,
                        'query': {'query': '', 'language': 'kuery'},
                        'filter': []
                    })
                }
            }
        },
        {
            'id': 'payment-types-pie',
            'title': 'Moyens de Paiement',
            'attributes': {
                'title': 'Moyens de Paiement',
                'visState': json.dumps({
                    'title': 'Moyens de Paiement',
                    'type': 'pie',
                    'aggs': [
                        {
                            'id': '1',
                            'enabled': True,
                            'type': 'count',
                            'schema': 'metric',
                            'params': {}
                        },
                        {
                            'id': '2',
                            'enabled': True,
                            'type': 'terms',
                            'schema': 'segment',
                            'params': {
                                'field': 'payment_type.keyword',
                                'size': 10,
                                'order': 'desc',
                                'orderBy': '1'
                            }
                        }
                    ],
                    'params': {
                        'type': 'pie',
                        'addTooltip': True,
                        'addLegend': True,
                        'legendPosition': 'right',
                        'isDonut': False
                    }
                }),
                'uiStateJSON': '{}',
                'description': '',
                'version': 1,
                'kibanaSavedObjectMeta': {
                    'searchSourceJSON': json.dumps({
                        'index': data_view_id,
                        'query': {'query': '', 'language': 'kuery'},
                        'filter': []
                    })
                }
            }
        },
        {
            'id': 'categories-bar',
            'title': 'Catégories Produits',
            'attributes': {
                'title': 'Catégories Produits',
                'visState': json.dumps({
                    'title': 'Catégories Produits',
                    'type': 'histogram',
                    'aggs': [
                        {
                            'id': '1',
                            'enabled': True,
                            'type': 'count',
                            'schema': 'metric',
                            'params': {}
                        },
                        {
                            'id': '2',
                            'enabled': True,
                            'type': 'terms',
                            'schema': 'segment',
                            'params': {
                                'field': 'category.keyword',
                                'size': 10,
                                'order': 'desc',
                                'orderBy': '1'
                            }
                        }
                    ],
                    'params': {
                        'type': 'histogram',
                        'grid': {'categoryLines': False},
                        'categoryAxes': [{
                            'id': 'CategoryAxis-1',
                            'type': 'category',
                            'position': 'bottom',
                            'show': True,
                            'style': {},
                            'scale': {'type': 'linear'},
                            'labels': {'show': True, 'truncate': 100},
                            'title': {}
                        }],
                        'valueAxes': [{
                            'id': 'ValueAxis-1',
                            'name': 'LeftAxis-1',
                            'type': 'value',
                            'position': 'left',
                            'show': True,
                            'style': {},
                            'scale': {'type': 'linear', 'mode': 'normal'},
                            'labels': {'show': True, 'rotate': 0, 'filter': False, 'truncate': 100},
                            'title': {'text': 'Count'}
                        }],
                        'seriesParams': [{
                            'show': True,
                            'type': 'histogram',
                            'mode': 'stacked',
                            'data': {'label': 'Count', 'id': '1'},
                            'valueAxis': 'ValueAxis-1',
                            'drawLinesBetweenPoints': True,
                            'lineWidth': 2,
                            'showCircles': True
                        }],
                        'addTooltip': True,
                        'addLegend': True,
                        'legendPosition': 'right',
                        'times': [],
                        'addTimeMarker': False
                    }
                }),
                'uiStateJSON': '{}',
                'description': '',
                'version': 1,
                'kibanaSavedObjectMeta': {
                    'searchSourceJSON': json.dumps({
                        'index': data_view_id,
                        'query': {'query': '', 'language': 'kuery'},
                        'filter': []
                    })
                }
            }
        },
        {
            'id': 'top-customers-table',
            'title': 'Top 10 Clients VIP',
            'attributes': {
                'title': 'Top 10 Clients VIP',
                'visState': json.dumps({
                    'title': 'Top 10 Clients VIP',
                    'type': 'table',
                    'aggs': [
                        {
                            'id': '1',
                            'enabled': True,
                            'type': 'sum',
                            'schema': 'metric',
                            'params': {'field': 'amount'}
                        },
                        {
                            'id': '2',
                            'enabled': True,
                            'type': 'count',
                            'schema': 'metric',
                            'params': {}
                        },
                        {
                            'id': '3',
                            'enabled': True,
                            'type': 'terms',
                            'schema': 'bucket',
                            'params': {
                                'field': 'customer_name.keyword',
                                'size': 10,
                                'order': 'desc',
                                'orderBy': '1'
                            }
                        }
                    ],
                    'params': {
                        'perPage': 10,
                        'showPartialRows': False,
                        'showMetricsAtAllLevels': False,
                        'showTotal': False,
                        'totalFunc': 'sum',
                        'percentageCol': ''
                    }
                }),
                'uiStateJSON': '{}',
                'description': '',
                'version': 1,
                'kibanaSavedObjectMeta': {
                    'searchSourceJSON': json.dumps({
                        'index': data_view_id,
                        'query': {'query': '', 'language': 'kuery'},
                        'filter': []
                    })
                }
            }
        },
        {
            'id': 'top-errors-table',
            'title': 'Top 10 Erreurs',
            'attributes': {
                'title': 'Top 10 Erreurs',
                'visState': json.dumps({
                    'title': 'Top 10 Erreurs',
                    'type': 'table',
                    'aggs': [
                        {
                            'id': '1',
                            'enabled': True,
                            'type': 'count',
                            'schema': 'metric',
                            'params': {}
                        },
                        {
                            'id': '2',
                            'enabled': True,
                            'type': 'terms',
                            'schema': 'bucket',
                            'params': {
                                'field': 'error_code.keyword',
                                'size': 10,
                                'order': 'desc',
                                'orderBy': '1',
                                'exclude': ''
                            }
                        }
                    ],
                    'params': {
                        'perPage': 10,
                        'showPartialRows': False,
                        'showMetricsAtAllLevels': False,
                        'showTotal': False,
                        'totalFunc': 'sum'
                    }
                }),
                'uiStateJSON': '{}',
                'description': '',
                'version': 1,
                'kibanaSavedObjectMeta': {
                    'searchSourceJSON': json.dumps({
                        'index': data_view_id,
                        'query': {'query': 'status.keyword: "failed"', 'language': 'kuery'},
                        'filter': []
                    })
                }
            }
        }
    ]
    
    print("\n🎨 Création/Mise à jour des visualisations:")
    success_count = 0
    
    for vis in visualizations:
        if create_visualization(vis):
            success_count += 1
    
    return success_count

def main():
    print("=" * 70)
    print("🔧 CORRECTION DES VISUALISATIONS KIBANA")
    print("=" * 70)
    
    if not wait_for_kibana():
        print("❌ Impossible de se connecter à Kibana")
        return
    
    print("\n📋 Étape 1: Récupération du data view...")
    data_view_id = get_data_view_id()
    
    if not data_view_id:
        print("❌ Data view 'logs-*' non trouvé!")
        print("💡 Exécutez d'abord: python3 scripts/fix-kibana-visualizations.py")
        return
    
    print(f"   ✅ Data view trouvé: {data_view_id}")
    
    print("\n📊 Étape 2: Création des visualisations...")
    success_count = create_all_visualizations(data_view_id)
    
    print("\n" + "=" * 70)
    print(f"✅ CONFIGURATION TERMINÉE ({success_count}/5 visualisations)")
    print("=" * 70)
    print("\n📌 Instructions:")
    print("   1. Ouvrez Kibana: http://localhost:5601")
    print("   2. Allez dans 'Visualize Library'")
    print("   3. Vous devriez voir les 5 nouvelles visualisations:")
    print("      • Taux de Succès (pie chart)")
    print("      • Moyens de Paiement (pie chart)")
    print("      • Catégories Produits (bar chart)")
    print("      • Top 10 Clients VIP (table)")
    print("      • Top 10 Erreurs (table)")
    print("\n💡 Vous pouvez les ajouter à votre dashboard!")

if __name__ == "__main__":
    main()
