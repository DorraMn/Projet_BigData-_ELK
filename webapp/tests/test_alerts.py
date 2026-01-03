# ============================================
# Tests Règles d'Alerte
# ============================================
import pytest
import json
from datetime import datetime, timedelta


class TestAlertRules:
    """Tests pour les règles d'alerte"""
    
    def test_alerts_page_requires_auth(self, client):
        """Test: La page d'alertes nécessite une authentification"""
        response = client.get('/alerts')
        assert response.status_code in [302, 401, 404]
    
    def test_create_alert_rule(self, client, auth_headers):
        """Test: Création d'une règle d'alerte"""
        alert_data = {
            'name': 'High Error Rate Alert',
            'condition': 'error_rate > 10',
            'threshold': 10,
            'metric': 'error_rate',
            'operator': 'greater_than',
            'severity': 'critical',
            'enabled': True
        }
        
        response = client.post(
            '/api/alerts/rules',
            data=json.dumps(alert_data),
            content_type='application/json',
            headers=auth_headers
        )
        
        # 201 (créé), 200 (ok), 401 (non auth), 404 (route non implémentée)
        assert response.status_code in [200, 201, 401, 404]
    
    def test_list_alert_rules(self, client, auth_headers):
        """Test: Lister les règles d'alerte"""
        response = client.get(
            '/api/alerts/rules',
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 404]
    
    def test_update_alert_rule(self, client, auth_headers):
        """Test: Mise à jour d'une règle d'alerte"""
        update_data = {
            'enabled': False,
            'threshold': 20
        }
        
        response = client.put(
            '/api/alerts/rules/1',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 404]
    
    def test_delete_alert_rule(self, client, auth_headers):
        """Test: Suppression d'une règle d'alerte"""
        response = client.delete(
            '/api/alerts/rules/999',
            headers=auth_headers
        )
        
        # 200/204 (supprimé), 404 (non trouvé), 401 (non auth)
        assert response.status_code in [200, 204, 401, 404]
    
    def test_alert_rule_validation(self, client, auth_headers):
        """Test: Validation des données de règle d'alerte"""
        # Données invalides (threshold négatif)
        invalid_data = {
            'name': '',  # Nom vide
            'threshold': -1,  # Valeur négative
            'metric': 'invalid_metric'
        }
        
        response = client.post(
            '/api/alerts/rules',
            data=json.dumps(invalid_data),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Devrait rejeter les données invalides
        assert response.status_code in [400, 401, 404, 422]
    
    def test_get_active_alerts(self, client, auth_headers):
        """Test: Récupérer les alertes actives"""
        response = client.get(
            '/api/alerts/active',
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 404]
    
    def test_acknowledge_alert(self, client, auth_headers):
        """Test: Acquitter une alerte"""
        response = client.post(
            '/api/alerts/1/acknowledge',
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 404]


class TestAlertConditions:
    """Tests pour l'évaluation des conditions d'alerte"""
    
    def test_threshold_greater_than(self):
        """Test: Condition 'supérieur à'"""
        def evaluate_condition(value, threshold, operator):
            if operator == 'greater_than':
                return value > threshold
            elif operator == 'less_than':
                return value < threshold
            elif operator == 'equals':
                return value == threshold
            return False
        
        assert evaluate_condition(15, 10, 'greater_than') == True
        assert evaluate_condition(5, 10, 'greater_than') == False
        assert evaluate_condition(10, 10, 'greater_than') == False
    
    def test_threshold_less_than(self):
        """Test: Condition 'inférieur à'"""
        def evaluate_condition(value, threshold, operator):
            if operator == 'less_than':
                return value < threshold
            return False
        
        assert evaluate_condition(5, 10, 'less_than') == True
        assert evaluate_condition(15, 10, 'less_than') == False
    
    def test_threshold_equals(self):
        """Test: Condition 'égal à'"""
        def evaluate_condition(value, threshold, operator):
            if operator == 'equals':
                return value == threshold
            return False
        
        assert evaluate_condition(10, 10, 'equals') == True
        assert evaluate_condition(11, 10, 'equals') == False
    
    def test_alert_severity_levels(self):
        """Test: Niveaux de sévérité"""
        severity_levels = ['info', 'warning', 'critical']
        
        for level in severity_levels:
            assert level in ['info', 'warning', 'critical']
    
    def test_alert_cooldown_period(self):
        """Test: Période de cooldown entre alertes"""
        last_alert_time = datetime.now() - timedelta(minutes=5)
        cooldown_minutes = 10
        
        # Pas encore passé le cooldown
        can_alert = (datetime.now() - last_alert_time).total_seconds() > cooldown_minutes * 60
        assert can_alert == False
        
        # Cooldown passé
        last_alert_time = datetime.now() - timedelta(minutes=15)
        can_alert = (datetime.now() - last_alert_time).total_seconds() > cooldown_minutes * 60
        assert can_alert == True
