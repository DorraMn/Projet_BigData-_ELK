#!/usr/bin/env python3
"""
Script pour visualiser les utilisateurs stockés dans MongoDB
"""

import pymongo
from datetime import datetime
from bson import ObjectId

# Connexion MongoDB
MONGO_URI = 'mongodb://localhost:27017'
DB_NAME = 'monitoring'
COLLECTION = 'users'

try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users_col = db[COLLECTION]
    
    print("=" * 80)
    print("📊 UTILISATEURS DANS MONGODB")
    print("=" * 80)
    print(f"\n📍 Base de données : {DB_NAME}")
    print(f"📍 Collection : {COLLECTION}")
    print(f"📍 URI : {MONGO_URI}\n")
    
    # Compter les utilisateurs
    total_users = users_col.count_documents({})
    active_users = users_col.count_documents({'is_active': True})
    
    print(f"Total utilisateurs : {total_users}")
    print(f"Utilisateurs actifs : {active_users}\n")
    
    if total_users == 0:
        print("⚠️  Aucun utilisateur trouvé dans la base de données.")
        print("\n💡 Pour créer un compte, visitez : http://localhost:8000/signup\n")
    else:
        print("-" * 80)
        
        # Afficher tous les utilisateurs
        for i, user in enumerate(users_col.find().sort('created_at', -1), 1):
            print(f"\n👤 Utilisateur #{i}")
            print(f"   ID             : {user['_id']}")
            print(f"   Username       : {user['username']}")
            print(f"   Email          : {user['email']}")
            print(f"   Rôle           : {user.get('role', 'user')}")
            print(f"   Actif          : {'✅ Oui' if user.get('is_active', True) else '❌ Non'}")
            print(f"   Créé le        : {user['created_at'].strftime('%d/%m/%Y à %H:%M:%S')}")
            
            if user.get('last_login'):
                print(f"   Dernière conn. : {user['last_login'].strftime('%d/%m/%Y à %H:%M:%S')}")
            else:
                print(f"   Dernière conn. : Jamais connecté")
            
            print(f"   Password hash  : {user['password_hash'][:30]}...")
        
        print("\n" + "-" * 80)
    
    print("\n" + "=" * 80)
    print("COMMANDES UTILES")
    print("=" * 80)
    print("\n🔍 Voir tous les utilisateurs :")
    print("   python3 scripts/view-users.py")
    
    print("\n🌐 Interface web MongoDB (Mongo Express) :")
    print("   http://localhost:8081")
    print("   → Sélectionner 'monitoring' → 'users'")
    
    print("\n💻 En ligne de commande MongoDB :")
    print("   mongosh monitoring --eval 'db.users.find().pretty()'")
    
    print("\n📝 Créer un nouveau compte :")
    print("   http://localhost:8000/signup")
    
    print("\n🔐 Se connecter :")
    print("   http://localhost:8000/login")
    
    print("\n" + "=" * 80 + "\n")
    
except Exception as e:
    print(f"\n❌ Erreur de connexion à MongoDB : {e}")
    print("\n💡 Vérifiez que MongoDB est démarré :")
    print("   docker compose ps mongodb")
    print("\n")
