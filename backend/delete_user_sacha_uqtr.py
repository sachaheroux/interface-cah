#!/usr/bin/env python3
"""
Script pour supprimer l'utilisateur sacha.heroux@uqtr.ca
"""

import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"
EMAIL_TO_DELETE = "sacha.heroux@uqtr.ca"

def delete_user_by_email():
    """Supprimer l'utilisateur par email"""
    print("🗑️ Suppression de l'utilisateur")
    print("=" * 50)
    
    try:
        print(f"📧 Email à supprimer: {EMAIL_TO_DELETE}")
        print(f"📡 Appel de l'endpoint de suppression...")
        print(f"   URL: {RENDER_URL}/api/auth/debug/delete-user-by-email")
        
        response = requests.post(
            f"{RENDER_URL}/api/auth/debug/delete-user-by-email",
            json={"email": EMAIL_TO_DELETE},
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Résultat de la suppression:")
            print(f"   - success: {data.get('success')}")
            print(f"   - message: {data.get('message')}")
            
            if data.get('success'):
                print("🎉 Utilisateur supprimé avec succès !")
                return True
            else:
                print("❌ Suppression échouée")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Le serveur Render met trop de temps à répondre")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Erreur de connexion - Impossible de joindre le serveur")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def list_all_users():
    """Lister tous les utilisateurs pour vérification"""
    print("\n👥 Liste de tous les utilisateurs")
    print("=" * 50)
    
    try:
        print(f"📡 Récupération de la liste des utilisateurs...")
        print(f"   URL: {RENDER_URL}/api/auth/debug/users")
        
        response = requests.get(
            f"{RENDER_URL}/api/auth/debug/users",
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Structure de la réponse:")
            print(f"   - success: {data.get('success')}")
            
            if data.get('success'):
                users = data.get('data', [])
                print(f"👥 Nombre d'utilisateurs: {len(users)}")
                
                if users:
                    print("\n📋 Liste des utilisateurs:")
                    for i, user in enumerate(users, 1):
                        print(f"  {i}. {user.get('prenom', 'N/A')} {user.get('nom', 'N/A')}")
                        print(f"     - Email: {user.get('email', 'N/A')}")
                        print(f"     - Rôle: {user.get('role', 'N/A')}")
                        print(f"     - Statut: {user.get('statut', 'N/A')}")
                        print(f"     - ID: {user.get('id_utilisateur', 'N/A')}")
                        print()
                else:
                    print("⚠️ Aucun utilisateur trouvé")
            else:
                print(f"❌ API retourne success=False")
                print(f"   Message: {data.get('message', 'Aucun message')}")
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def verify_deletion():
    """Vérifier que l'utilisateur a bien été supprimé"""
    print("\n🔍 Vérification de la suppression")
    print("=" * 50)
    
    try:
        response = requests.get(
            f"{RENDER_URL}/api/auth/debug/users",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                users = data.get('data', [])
                
                # Chercher l'utilisateur supprimé
                found_user = None
                for user in users:
                    if user.get('email') == EMAIL_TO_DELETE:
                        found_user = user
                        break
                
                if found_user:
                    print(f"❌ UTILISATEUR ENCORE PRÉSENT !")
                    print(f"   Email: {found_user.get('email')}")
                    print(f"   Nom: {found_user.get('prenom')} {found_user.get('nom')}")
                    return False
                else:
                    print(f"✅ UTILISATEUR BIEN SUPPRIMÉ !")
                    print(f"   Email {EMAIL_TO_DELETE} non trouvé dans la liste")
                    return True
            else:
                print("❌ Impossible de vérifier - API error")
                return False
        else:
            print(f"❌ Impossible de vérifier - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Suppression utilisateur - Interface CAH")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Lister les utilisateurs avant suppression
    print("📋 État avant suppression :")
    list_all_users()
    
    # Supprimer l'utilisateur
    deletion_success = delete_user_by_email()
    
    if deletion_success:
        print("\n✅ Suppression terminée")
        
        # Vérifier la suppression
        verification_success = verify_deletion()
        
        if verification_success:
            print("\n🎉 SUPPRESSION CONFIRMÉE !")
            print("   L'utilisateur sacha.heroux@uqtr.ca a été supprimé")
        else:
            print("\n⚠️ Suppression non confirmée")
            print("   Vérifier manuellement sur Render")
    else:
        print("\n❌ Suppression échouée")
        print("   Vérifier que l'endpoint existe sur Render")
    
    # Lister les utilisateurs après suppression
    print("\n📋 État après suppression :")
    list_all_users()
    
    print("\n" + "=" * 50)
    print("🏁 Script terminé")
