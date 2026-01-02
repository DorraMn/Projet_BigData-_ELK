#!/usr/bin/env python3
"""
Script pour créer des visualisations Lens (nouveau format Kibana)
au lieu des anciennes visualisations
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
    for _ in range(10):
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

def create_lens_visualization(lens_config):
    """Créer une visualisation Lens"""
    lens_id = lens_config.get('id')
    lens_title = lens_config.get('title')
    
    try:
        # Vérifier si la visualisation existe
        response = requests.get(
            f"{KIBANA_URL}/api/saved_objects/lens/{lens_id}",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            print(f"   🔄 Mise à jour de {lens_title}...")
            # Mettre à jour
            response = requests.put(
                f"{KIBANA_URL}/api/saved_objects/lens/{lens_id}",
                headers=HEADERS,
                json={"attributes": lens_config['attributes']}
            )
        else:
            print(f"   📝 Création de {lens_title}...")
            # Créer avec POST en utilisant l'ID
            response = requests.post(
                f"{KIBANA_URL}/api/saved_objects/lens/{lens_id}",
                headers=HEADERS,
                json={"attributes": lens_config['attributes']}
            )
        
        if response.status_code in [200, 201]:
            print(f"   ✅ {lens_title} configuré!")
            return True
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    return False

def create_all_lens_visualizations(data_view_id):
    """Créer toutes les visualisations Lens"""
    
    lens_visualizations = [
        {
            'id': 'success-rate-pie',
            'title': 'Taux de Succès',
            'attributes': {
                'title': 'Taux de Succès',
                'description': 'Répartition success vs failed',
                'visualizationType': 'lnsPie',
                'state': {
                    'datasourceStates': {
                        'formBased': {
                            'layers': {
                                'layer1': {
                                    'columns': {
                                        'col1': {
                                            'label': 'Count',
                                            'dataType': 'number',
                                            'operationType': 'count',
                                            'isBucketed': False,
                                            'scale': 'ratio',
                                            'sourceField': '___records___',
                                            'params': {'emptyAsNull': False}
                                        },
                                        'col2': {
                                            'label': 'Top 10 values of status.keyword',
                                            'dataType': 'string',
                                            'operationType': 'terms',
                                            'isBucketed': True,
                                            'scale': 'ordinal',
                                            'sourceField': 'status.keyword',
                                            'params': {
                                                'size': 10,
                                                'orderBy': {'type': 'column', 'columnId': 'col1'},
                                                'orderDirection': 'desc',
                                                'otherBucket': True,
                                                'missingBucket': False,
                                                'parentFormat': {'id': 'terms'}
                                            }
                                        }
                                    },
                                    'columnOrder': ['col2', 'col1'],
                                    'incompleteColumns': {},
                                    'indexPatternId': data_view_id
                                }
                            }
                        }
                    },
                    'visualization': {
                        'shape': 'donut',
                        'layers': [{
                            'layerId': 'layer1',
                            'primaryGroups': ['col2'],
                            'metrics': ['col1'],
                            'numberDisplay': 'percent',
                            'categoryDisplay': 'default',
                            'legendDisplay': 'show',
                            'nestedLegend': False,
                            'legendPosition': 'right'
                        }]
                    },
                    'query': {'query': '', 'language': 'kuery'},
                    'filters': []
                },
                'references': [{
                    'type': 'index-pattern',
                    'id': data_view_id,
                    'name': 'indexpattern-datasource-layer-layer1'
                }]
            }
        },
        {
            'id': 'payment-types-pie',
            'title': 'Moyens de Paiement',
            'attributes': {
                'title': 'Moyens de Paiement',
                'description': 'Répartition par type de paiement',
                'visualizationType': 'lnsPie',
                'state': {
                    'datasourceStates': {
                        'formBased': {
                            'layers': {
                                'layer1': {
                                    'columns': {
                                        'col1': {
                                            'label': 'Count',
                                            'dataType': 'number',
                                            'operationType': 'count',
                                            'isBucketed': False,
                                            'scale': 'ratio',
                                            'sourceField': '___records___',
                                            'params': {'emptyAsNull': False}
                                        },
                                        'col2': {
                                            'label': 'Top 10 values of payment_type.keyword',
                                            'dataType': 'string',
                                            'operationType': 'terms',
                                            'isBucketed': True,
                                            'scale': 'ordinal',
                                            'sourceField': 'payment_type.keyword',
                                            'params': {
                                                'size': 10,
                                                'orderBy': {'type': 'column', 'columnId': 'col1'},
                                                'orderDirection': 'desc',
                                                'otherBucket': True,
                                                'missingBucket': False,
                                                'parentFormat': {'id': 'terms'}
                                            }
                                        }
                                    },
                                    'columnOrder': ['col2', 'col1'],
                                    'incompleteColumns': {},
                                    'indexPatternId': data_view_id
                                }
                            }
                        }
                    },
                    'visualization': {
                        'shape': 'pie',
                        'layers': [{
                            'layerId': 'layer1',
                            'primaryGroups': ['col2'],
                            'metrics': ['col1'],
                            'numberDisplay': 'percent',
                            'categoryDisplay': 'default',
                            'legendDisplay': 'show',
                            'nestedLegend': False,
                            'legendPosition': 'right'
                        }]
                    },
                    'query': {'query': '', 'language': 'kuery'},
                    'filters': []
                },
                'references': [{
                    'type': 'index-pattern',
                    'id': data_view_id,
                    'name': 'indexpattern-datasource-layer-layer1'
                }]
            }
        },
        {
            'id': 'categories-bar',
            'title': 'Catégories Produits',
            'attributes': {
                'title': 'Catégories Produits',
                'description': 'Distribution par catégorie',
                'visualizationType': 'lnsXY',
                'state': {
                    'datasourceStates': {
                        'formBased': {
                            'layers': {
                                'layer1': {
                                    'columns': {
                                        'col1': {
                                            'label': 'Count',
                                            'dataType': 'number',
                                            'operationType': 'count',
                                            'isBucketed': False,
                                            'scale': 'ratio',
                                            'sourceField': '___records___',
                                            'params': {'emptyAsNull': False}
                                        },
                                        'col2': {
                                            'label': 'Top 10 values of category.keyword',
                                            'dataType': 'string',
                                            'operationType': 'terms',
                                            'isBucketed': True,
                                            'scale': 'ordinal',
                                            'sourceField': 'category.keyword',
                                            'params': {
                                                'size': 10,
                                                'orderBy': {'type': 'column', 'columnId': 'col1'},
                                                'orderDirection': 'desc',
                                                'otherBucket': True,
                                                'missingBucket': False,
                                                'parentFormat': {'id': 'terms'}
                                            }
                                        }
                                    },
                                    'columnOrder': ['col2', 'col1'],
                                    'incompleteColumns': {},
                                    'indexPatternId': data_view_id
                                }
                            }
                        }
                    },
                    'visualization': {
                        'legend': {'isVisible': True, 'position': 'right'},
                        'valueLabels': 'hide',
                        'fittingFunction': 'None',
                        'axisTitlesVisibilitySettings': {'x': True, 'yLeft': True, 'yRight': True},
                        'tickLabelsVisibilitySettings': {'x': True, 'yLeft': True, 'yRight': True},
                        'labelsOrientation': {'x': 0, 'yLeft': 0, 'yRight': 0},
                        'gridlinesVisibilitySettings': {'x': True, 'yLeft': True, 'yRight': True},
                        'preferredSeriesType': 'bar_horizontal',
                        'layers': [{
                            'layerId': 'layer1',
                            'accessors': ['col1'],
                            'position': 'top',
                            'seriesType': 'bar_horizontal',
                            'showGridlines': False,
                            'layerType': 'data',
                            'xAccessor': 'col2'
                        }]
                    },
                    'query': {'query': '', 'language': 'kuery'},
                    'filters': []
                },
                'references': [{
                    'type': 'index-pattern',
                    'id': data_view_id,
                    'name': 'indexpattern-datasource-layer-layer1'
                }]
            }
        },
        {
            'id': 'top-customers-table',
            'title': 'Top 10 Clients VIP',
            'attributes': {
                'title': 'Top 10 Clients VIP',
                'description': 'Top clients par montant total',
                'visualizationType': 'lnsDatatable',
                'state': {
                    'datasourceStates': {
                        'formBased': {
                            'layers': {
                                'layer1': {
                                    'columns': {
                                        'col1': {
                                            'label': 'customer_name.keyword',
                                            'dataType': 'string',
                                            'operationType': 'terms',
                                            'isBucketed': True,
                                            'scale': 'ordinal',
                                            'sourceField': 'customer_name.keyword',
                                            'params': {
                                                'size': 10,
                                                'orderBy': {'type': 'column', 'columnId': 'col2'},
                                                'orderDirection': 'desc',
                                                'otherBucket': False,
                                                'missingBucket': False,
                                                'parentFormat': {'id': 'terms'}
                                            }
                                        },
                                        'col2': {
                                            'label': 'Montant Total',
                                            'dataType': 'number',
                                            'operationType': 'sum',
                                            'isBucketed': False,
                                            'scale': 'ratio',
                                            'sourceField': 'amount',
                                            'params': {'emptyAsNull': False}
                                        },
                                        'col3': {
                                            'label': 'Transactions',
                                            'dataType': 'number',
                                            'operationType': 'count',
                                            'isBucketed': False,
                                            'scale': 'ratio',
                                            'sourceField': '___records___',
                                            'params': {'emptyAsNull': False}
                                        }
                                    },
                                    'columnOrder': ['col1', 'col2', 'col3'],
                                    'incompleteColumns': {},
                                    'indexPatternId': data_view_id
                                }
                            }
                        }
                    },
                    'visualization': {
                        'layerId': 'layer1',
                        'layerType': 'data',
                        'columns': [
                            {'columnId': 'col1'},
                            {'columnId': 'col2'},
                            {'columnId': 'col3'}
                        ]
                    },
                    'query': {'query': '', 'language': 'kuery'},
                    'filters': []
                },
                'references': [{
                    'type': 'index-pattern',
                    'id': data_view_id,
                    'name': 'indexpattern-datasource-layer-layer1'
                }]
            }
        },
        {
            'id': 'top-errors-table',
            'title': 'Top 10 Erreurs',
            'attributes': {
                'title': 'Top 10 Erreurs',
                'description': 'Erreurs les plus fréquentes',
                'visualizationType': 'lnsDatatable',
                'state': {
                    'datasourceStates': {
                        'formBased': {
                            'layers': {
                                'layer1': {
                                    'columns': {
                                        'col1': {
                                            'label': 'error_code.keyword',
                                            'dataType': 'string',
                                            'operationType': 'terms',
                                            'isBucketed': True,
                                            'scale': 'ordinal',
                                            'sourceField': 'error_code.keyword',
                                            'params': {
                                                'size': 10,
                                                'orderBy': {'type': 'column', 'columnId': 'col2'},
                                                'orderDirection': 'desc',
                                                'otherBucket': False,
                                                'missingBucket': False,
                                                'parentFormat': {'id': 'terms'}
                                            }
                                        },
                                        'col2': {
                                            'label': 'Occurrences',
                                            'dataType': 'number',
                                            'operationType': 'count',
                                            'isBucketed': False,
                                            'scale': 'ratio',
                                            'sourceField': '___records___',
                                            'params': {'emptyAsNull': False}
                                        }
                                    },
                                    'columnOrder': ['col1', 'col2'],
                                    'incompleteColumns': {},
                                    'indexPatternId': data_view_id
                                }
                            }
                        }
                    },
                    'visualization': {
                        'layerId': 'layer1',
                        'layerType': 'data',
                        'columns': [
                            {'columnId': 'col1'},
                            {'columnId': 'col2'}
                        ]
                    },
                    'query': {'query': 'status.keyword: "failed"', 'language': 'kuery'},
                    'filters': []
                },
                'references': [{
                    'type': 'index-pattern',
                    'id': data_view_id,
                    'name': 'indexpattern-datasource-layer-layer1'
                }]
            }
        }
    ]
    
    print("\n🎨 Création des visualisations Lens:")
    success_count = 0
    
    for lens in lens_visualizations:
        if create_lens_visualization(lens):
            success_count += 1
    
    return success_count

def main():
    print("=" * 70)
    print("🔧 CRÉATION DES VISUALISATIONS LENS POUR KIBANA")
    print("=" * 70)
    
    if not wait_for_kibana():
        print("❌ Impossible de se connecter à Kibana")
        return
    
    print("\n📋 Étape 1: Récupération du data view...")
    data_view_id = get_data_view_id()
    
    if not data_view_id:
        print("❌ Data view 'logs-*' non trouvé!")
        return
    
    print(f"   ✅ Data view trouvé: {data_view_id}")
    
    print("\n📊 Étape 2: Création des visualisations Lens...")
    success_count = create_all_lens_visualizations(data_view_id)
    
    print("\n" + "=" * 70)
    print(f"✅ CONFIGURATION TERMINÉE ({success_count}/5 visualisations)")
    print("=" * 70)
    print("\n📌 Instructions:")
    print("   1. Rafraîchissez la page Kibana (F5)")
    print("   2. Le dashboard devrait maintenant fonctionner!")
    print("   3. N'oubliez pas de sélectionner 'Last 30 days'")
    print("\n💡 Les visualisations utilisent maintenant le format Lens (moderne)")

if __name__ == "__main__":
    main()
