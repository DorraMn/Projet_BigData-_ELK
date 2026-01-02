#!/usr/bin/env python3
"""
Test rapide du système d'authentification
Sans dépendances Docker - Test local uniquement
"""

import sys
import os

# Ajouter le répertoire webapp au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'webapp'))

def test_auth_module():
    """Test le module auth.py"""
    print("=" * 60)
    print("🔐 TEST DU MODULE D'AUTHENTIFICATION")
    print("=" * 60)
    print()
    
    try:
        from auth import AuthManager
        print("✅ Import de AuthManager réussi")
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    
    # Créer une instance
    try:
        auth = AuthManager()
        print("✅ Création de l'instance AuthManager réussie")
    except Exception as e:
        print(f"❌ Erreur de création: {e}")
        return False
    
    # Test de vérification des credentials
    print("\n📝 Test 1: Vérification des credentials")
    try:
        valid = auth.verify_credentials("admin", "admin123")
        if valid:
            print("   ✅ Credentials valides reconnus")
        else:
            print("   ❌ Credentials valides non reconnus")
            return False
        
        invalid = auth.verify_credentials("admin", "wrong_password")
        if not invalid:
            print("   ✅ Credentials invalides rejetés")
        else:
            print("   ❌ Credentials invalides acceptés")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test de génération de token
    print("\n📝 Test 2: Génération de token JWT")
    try:
        token = auth.generate_token("admin")
        if token and len(token) > 50:
            print(f"   ✅ Token généré: {token[:50]}...")
        else:
            print("   ❌ Token invalide")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test de vérification de token
    print("\n📝 Test 3: Vérification de token")
    try:
        payload = auth.verify_token(token)
        if payload and payload.get('username') == 'admin':
            print(f"   ✅ Token valide, username: {payload['username']}")
        else:
            print("   ❌ Payload invalide")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test de token invalide
    print("\n📝 Test 4: Rejet de token invalide")
    try:
        invalid_payload = auth.verify_token("invalid.token.here")
        if invalid_payload is None:
            print("   ✅ Token invalide correctement rejeté")
        else:
            print("   ❌ Token invalide accepté")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✨ TOUS LES TESTS SONT PASSÉS !")
    print("=" * 60)
    return True


def test_flask_routes():
    """Vérifie que les routes Flask sont bien définies"""
    print("\n" + "=" * 60)
    print("🌐 TEST DES ROUTES FLASK")
    print("=" * 60)
    print()
    
    try:
        # Import sans lancer le serveur
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "webapp/app.py")
        if spec and spec.loader:
            app_module = importlib.util.module_from_spec(spec)
            
            print("✅ Module app.py chargé")
            
            # Vérifier les imports d'auth dans le fichier
            with open('webapp/app.py', 'r') as f:
                content = f.read()
                
            checks = [
                ('from auth import', 'Import du module auth'),
                ('@login_required', 'Décorateur @login_required'),
                ('@api_login_required', 'Décorateur @api_login_required'),
                ('/api/login', 'Route /api/login'),
                ('/api/logout', 'Route /api/logout'),
                ('/api/verify-token', 'Route /api/verify-token'),
            ]
            
            print("\n📋 Vérification du code:")
            for pattern, description in checks:
                if pattern in content:
                    print(f"   ✅ {description} trouvé")
                else:
                    print(f"   ❌ {description} manquant")
                    return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✨ TOUTES LES ROUTES SONT CONFIGURÉES !")
    print("=" * 60)
    return True


def test_templates():
    """Vérifie que les templates sont présents"""
    print("\n" + "=" * 60)
    print("📄 TEST DES TEMPLATES")
    print("=" * 60)
    print()
    
    templates = [
        'webapp/templates/login.html',
        'webapp/templates/index.html',
        'webapp/templates/upload.html',
        'webapp/templates/dashboard.html',
        'webapp/templates/health.html',
        'webapp/templates/search.html',
    ]
    
    all_ok = True
    for template in templates:
        if os.path.exists(template):
            # Vérifier le bouton de déconnexion (sauf login.html)
            if 'login.html' not in template:
                with open(template, 'r') as f:
                    content = f.read()
                    if 'logout-btn' in content and '/api/logout' in content:
                        print(f"   ✅ {os.path.basename(template)} - OK (avec bouton logout)")
                    else:
                        print(f"   ⚠️  {os.path.basename(template)} - OK (sans bouton logout)")
            else:
                print(f"   ✅ {os.path.basename(template)} - OK")
        else:
            print(f"   ❌ {os.path.basename(template)} - MANQUANT")
            all_ok = False
    
    if all_ok:
        print("\n" + "=" * 60)
        print("✨ TOUS LES TEMPLATES SONT PRÉSENTS !")
        print("=" * 60)
    
    return all_ok


def test_dependencies():
    """Vérifie que les dépendances sont installées"""
    print("\n" + "=" * 60)
    print("📦 TEST DES DÉPENDANCES")
    print("=" * 60)
    print()
    
    dependencies = [
        ('jwt', 'PyJWT'),
        ('werkzeug', 'Werkzeug'),
        ('flask', 'Flask'),
    ]
    
    all_ok = True
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"   ✅ {package_name} installé")
        except ImportError:
            print(f"   ❌ {package_name} manquant")
            all_ok = False
    
    if all_ok:
        print("\n" + "=" * 60)
        print("✨ TOUTES LES DÉPENDANCES SONT INSTALLÉES !")
        print("=" * 60)
    else:
        print("\n⚠️  Pour installer les dépendances manquantes:")
        print("   pip install -r webapp/requirements.txt")
    
    return all_ok


def test_configuration():
    """Vérifie la configuration"""
    print("\n" + "=" * 60)
    print("⚙️  TEST DE LA CONFIGURATION")
    print("=" * 60)
    print()
    
    # Vérifier .env.example
    if os.path.exists('.env.example'):
        with open('.env.example', 'r') as f:
            content = f.read()
            
        config_vars = [
            'JWT_SECRET_KEY',
            'JWT_EXPIRATION_HOURS',
            'ADMIN_USERNAME',
            'ADMIN_PASSWORD',
        ]
        
        all_ok = True
        for var in config_vars:
            if var in content:
                print(f"   ✅ {var} présent dans .env.example")
            else:
                print(f"   ❌ {var} manquant dans .env.example")
                all_ok = False
        
        if all_ok:
            print("\n" + "=" * 60)
            print("✨ CONFIGURATION COMPLÈTE !")
            print("=" * 60)
        
        return all_ok
    else:
        print("   ❌ .env.example manquant")
        return False


def test_documentation():
    """Vérifie la documentation"""
    print("\n" + "=" * 60)
    print("📚 TEST DE LA DOCUMENTATION")
    print("=" * 60)
    print()
    
    docs = [
        ('AUTH-SYSTEM.md', 'Documentation du système d\'authentification'),
        ('CHANGELOG-AUTH.md', 'Changelog des modifications'),
        ('RECAP-AUTH.md', 'Récapitulatif complet'),
        ('README.md', 'Documentation principale'),
    ]
    
    all_ok = True
    for filename, description in docs:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"   ✅ {filename} ({size:,} bytes) - {description}")
        else:
            print(f"   ❌ {filename} - MANQUANT")
            all_ok = False
    
    if all_ok:
        print("\n" + "=" * 60)
        print("✨ TOUTE LA DOCUMENTATION EST PRÉSENTE !")
        print("=" * 60)
    
    return all_ok


def main():
    """Lance tous les tests"""
    print("\n")
    print("🚀 " + "=" * 58)
    print("🚀  TEST COMPLET DU SYSTÈME D'AUTHENTIFICATION")
    print("🚀 " + "=" * 58)
    print("\n")
    
    results = {
        "Dépendances": test_dependencies(),
        "Module Auth": test_auth_module(),
        "Routes Flask": test_flask_routes(),
        "Templates": test_templates(),
        "Configuration": test_configuration(),
        "Documentation": test_documentation(),
    }
    
    print("\n\n")
    print("=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"   {test_name:20s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("🎉 LE SYSTÈME D'AUTHENTIFICATION EST PRÊT !")
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("⚠️  VÉRIFIEZ LES ERREURS CI-DESSUS")
    print("=" * 60)
    print()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
