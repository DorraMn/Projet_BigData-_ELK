"""
LogStream Studio - Module d'authentification JWT
Système d'authentification sécurisé avec support MongoDB
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash


class AuthManager:
    """Gestionnaire d'authentification JWT avec MongoDB"""
    
    def __init__(self, users_collection=None):
        # Clé secrète pour JWT (en production, utiliser une clé forte)
        self.secret_key = os.environ.get('JWT_SECRET_KEY', 'logstream-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.token_expiration = int(os.environ.get('JWT_EXPIRATION_HOURS', '24'))
        
        # Collection MongoDB pour les utilisateurs
        self.users_col = users_collection
        
        # Credentials admin (fallback si MongoDB indisponible)
        self.admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        self.admin_password_hash = generate_password_hash(
            os.environ.get('ADMIN_PASSWORD', 'admin123')
        )
    
    def create_user(self, username, email, password):
        """
        Crée un nouveau utilisateur dans MongoDB
        
        Args:
            username (str): Nom d'utilisateur
            email (str): Email
            password (str): Mot de passe en clair
            
        Returns:
            dict: {'success': bool, 'message': str, 'user_id': str}
        """
        if self.users_col is None:
            return {'success': False, 'message': 'Base de données non disponible'}
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = self.users_col.find_one({'$or': [
            {'username': username},
            {'email': email}
        ]})
        
        if existing_user:
            if existing_user.get('username') == username:
                return {'success': False, 'message': 'Ce nom d\'utilisateur est déjà utilisé'}
            else:
                return {'success': False, 'message': 'Cet email est déjà utilisé'}
        
        # Créer le nouvel utilisateur
        user_doc = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'role': 'user',
            'created_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True
        }
        
        try:
            result = self.users_col.insert_one(user_doc)
            return {
                'success': True,
                'message': 'Compte créé avec succès',
                'user_id': str(result.inserted_id)
            }
        except Exception as e:
            return {'success': False, 'message': f'Erreur lors de la création: {str(e)}'}
    
    def verify_credentials(self, username, password):
        """
        Vérifie les identifiants de l'utilisateur (MongoDB ou admin)
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe
            
        Returns:
            dict: {'valid': bool, 'user': dict} ou False
        """
        # Vérifier d'abord dans MongoDB si disponible
        if self.users_col is not None:
            user = self.users_col.find_one({'username': username, 'is_active': True})
            if user and check_password_hash(user['password_hash'], password):
                # Mettre à jour last_login
                self.users_col.update_one(
                    {'_id': user['_id']},
                    {'$set': {'last_login': datetime.utcnow()}}
                )
                return {
                    'valid': True,
                    'user': {
                        'username': user['username'],
                        'email': user.get('email', ''),
                        'role': user.get('role', 'user')
                    }
                }
        
        # Fallback sur le compte admin par défaut
        if username == self.admin_username and check_password_hash(self.admin_password_hash, password):
            return {
                'valid': True,
                'user': {
                    'username': self.admin_username,
                    'email': 'admin@logstream.local',
                    'role': 'admin'
                }
            }
        
        return False
    
    def generate_token(self, user_info):
        """
        Génère un token JWT pour l'utilisateur
        
        Args:
            user_info (dict): Informations utilisateur (username, role, email)
            
        Returns:
            str: Token JWT
        """
        payload = {
            'username': user_info.get('username'),
            'email': user_info.get('email', ''),
            'role': user_info.get('role', 'user'),
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiration),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token):
        """
        Vérifie la validité d'un token JWT
        
        Args:
            token (str): Token JWT à vérifier
            
        Returns:
            dict: Payload du token si valide, None sinon
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token expiré
        except jwt.InvalidTokenError:
            return None  # Token invalide
    
    def get_token_from_request(self):
        """
        Extrait le token JWT de la requête HTTP
        
        Returns:
            str: Token JWT ou None
        """
        # Vérifier l'en-tête Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        
        # Vérifier les cookies
        token = request.cookies.get('access_token')
        if token:
            return token
        
        return None


# Instance globale (sera initialisée dans app.py avec la collection users)
auth_manager = None


def init_auth_manager(users_collection):
    """Initialise l'AuthManager avec la collection MongoDB"""
    global auth_manager
    auth_manager = AuthManager(users_collection)
    return auth_manager


def login_required(f):
    """
    Décorateur pour protéger les routes qui nécessitent une authentification
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return 'Content accessible uniquement aux utilisateurs authentifiés'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = auth_manager.get_token_from_request()
        
        if not token:
            # Rediriger vers la page de login pour les routes HTML
            return redirect(url_for('login'))
        
        payload = auth_manager.verify_token(token)
        
        if not payload:
            # Rediriger vers la page de login si le token est invalide
            return redirect(url_for('login'))
        
        # Ajouter les infos utilisateur à la requête
        request.user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def api_login_required(f):
    """
    Décorateur pour protéger les routes API
    Retourne toujours du JSON
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = auth_manager.get_token_from_request()
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'code': 'AUTH_REQUIRED'
            }), 401
        
        payload = auth_manager.verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token',
                'code': 'TOKEN_INVALID'
            }), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function


def check_auth():
    """
    Vérifie si l'utilisateur est authentifié (pour les templates)
    
    Returns:
        bool: True si authentifié
    """
    token = auth_manager.get_token_from_request()
    if not token:
        return False
    
    payload = auth_manager.verify_token(token)
    return payload is not None


def get_current_user():
    """
    Récupère les informations de l'utilisateur courant
    
    Returns:
        dict: Payload du token ou None
    """
    token = auth_manager.get_token_from_request()
    if not token:
        return None
    
    return auth_manager.verify_token(token)


# Fonction de test
if __name__ == "__main__":
    print("🧪 Test du module auth.py\n")
    
    # Test 1: Génération de token
    print("1️⃣  Test génération de token:")
    token = auth_manager.generate_token('admin')
    print(f"   Token généré: {token[:50]}...")
    
    # Test 2: Vérification de token
    print("\n2️⃣  Test vérification de token:")
    payload = auth_manager.verify_token(token)
    if payload:
        print(f"   ✅ Token valide")
        print(f"   Username: {payload['username']}")
        print(f"   Role: {payload['role']}")
        print(f"   Expiration: {datetime.fromtimestamp(payload['exp'])}")
    else:
        print("   ❌ Token invalide")
    
    # Test 3: Vérification des credentials
    print("\n3️⃣  Test vérification credentials:")
    valid = auth_manager.verify_credentials('admin', 'admin123')
    print(f"   Credentials valides: {'✅' if valid else '❌'}")
    
    invalid = auth_manager.verify_credentials('admin', 'wrongpassword')
    print(f"   Mauvais password: {'❌' if not invalid else '✅ (ERREUR!)'}")
    
    print("\n✨ Tests terminés !")
