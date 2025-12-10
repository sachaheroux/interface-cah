#!/usr/bin/env python3
"""
Script de test pour vérifier que le changement d'email et de mot de passe
fonctionne correctement et persiste dans la base de données auth.db
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000/api/auth"
# Pour Render: API_BASE = "https://interface-cah-backend.onrender.com/api/auth"

def test_change_email_and_password():
    """Tester le changement d'email et de mot de passe"""
    
    print("🧪 TEST DU CHANGEMENT D'EMAIL ET DE MOT DE PASSE")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Se connecter pour obtenir un token
    print("1️⃣ CONNEXION")
    print("-" * 40)
    login_data = {
        "email": "sacha.heroux87@gmail.com",
        "mot_de_passe": "Champion2024!"
    }
    
    try:
        response = requests.post(f"{API_BASE}/login", json=login_data, timeout=30)
        if response.status_code != 200:
            print(f"❌ Erreur de connexion: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return
        
        data = response.json()
        token = data.get("token")
        if not token:
            print("❌ Aucun token reçu")
            return
        
        print("✅ Connexion réussie")
        print(f"   Token: {token[:20]}...")
        print()
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Récupérer les infos utilisateur actuelles
        print("2️⃣ RÉCUPÉRATION DES INFOS UTILISATEUR")
        print("-" * 40)
        response = requests.get(f"{API_BASE}/me", headers=headers, timeout=30)
        if response.status_code == 200:
            user_data = response.json().get("user", {})
            old_email = user_data.get("email")
            print(f"✅ Email actuel: {old_email}")
            print()
        else:
            print(f"❌ Erreur récupération utilisateur: {response.status_code}")
            return
        
        # 3. Tester le changement de mot de passe
        print("3️⃣ TEST DU CHANGEMENT DE MOT DE PASSE")
        print("-" * 40)
        new_password = "NouveauMotDePasse2024!"
        password_data = {
            "mot_de_passe_actuel": "Champion2024!",
            "nouveau_mot_de_passe": new_password
        }
        
        response = requests.put(f"{API_BASE}/password", json=password_data, headers=headers, timeout=30)
        if response.status_code == 200:
            print("✅ Mot de passe changé avec succès")
            print(f"   Message: {response.json().get('message')}")
            print()
            
            # Vérifier que le nouveau mot de passe fonctionne
            print("4️⃣ VÉRIFICATION DU NOUVEAU MOT DE PASSE")
            print("-" * 40)
            test_login = {
                "email": old_email,
                "mot_de_passe": new_password
            }
            response = requests.post(f"{API_BASE}/login", json=test_login, timeout=30)
            if response.status_code == 200:
                print("✅ Le nouveau mot de passe fonctionne!")
                token = response.json().get("token")
                headers = {"Authorization": f"Bearer {token}"}
            else:
                print(f"❌ Le nouveau mot de passe ne fonctionne pas: {response.status_code}")
                return
        else:
            print(f"❌ Erreur changement mot de passe: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return
        
        # 5. Remettre l'ancien mot de passe (pour ne pas casser le système)
        print("5️⃣ RESTAURATION DE L'ANCIEN MOT DE PASSE")
        print("-" * 40)
        restore_password_data = {
            "mot_de_passe_actuel": new_password,
            "nouveau_mot_de_passe": "Champion2024!"
        }
        
        response = requests.put(f"{API_BASE}/password", json=restore_password_data, headers=headers, timeout=30)
        if response.status_code == 200:
            print("✅ Ancien mot de passe restauré")
            print()
        else:
            print(f"⚠️ Impossible de restaurer l'ancien mot de passe: {response.status_code}")
            print("   Vous devrez peut-être le changer manuellement")
            print()
        
        # 6. Tester le changement d'email (avec un email de test)
        print("6️⃣ TEST DU CHANGEMENT D'EMAIL")
        print("-" * 40)
        test_email = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"
        email_data = {
            "nouveau_email": test_email,
            "mot_de_passe": "Champion2024!"
        }
        
        response = requests.put(f"{API_BASE}/email", json=email_data, headers=headers, timeout=30)
        if response.status_code == 200:
            print(f"✅ Email changé vers: {test_email}")
            print(f"   Message: {response.json().get('message')}")
            print()
            
            # Vérifier que le nouvel email est bien enregistré
            print("7️⃣ VÉRIFICATION DU NOUVEL EMAIL")
            print("-" * 40)
            response = requests.get(f"{API_BASE}/me", headers=headers, timeout=30)
            if response.status_code == 200:
                user_data = response.json().get("user", {})
                current_email = user_data.get("email")
                if current_email == test_email:
                    print(f"✅ Le nouvel email est bien enregistré: {current_email}")
                else:
                    print(f"❌ Email différent: attendu {test_email}, obtenu {current_email}")
            print()
            
            # Remettre l'ancien email
            print("8️⃣ RESTAURATION DE L'ANCIEN EMAIL")
            print("-" * 40)
            restore_email_data = {
                "nouveau_email": old_email,
                "mot_de_passe": "Champion2024!"
            }
            
            response = requests.put(f"{API_BASE}/email", json=restore_email_data, headers=headers, timeout=30)
            if response.status_code == 200:
                print(f"✅ Ancien email restauré: {old_email}")
            else:
                print(f"⚠️ Impossible de restaurer l'ancien email: {response.status_code}")
                print(f"   Vous devrez peut-être le changer manuellement vers: {old_email}")
        
        else:
            print(f"❌ Erreur changement email: {response.status_code}")
            print(f"   Réponse: {response.text}")
        
        print()
        print("=" * 60)
        print("✅ TESTS TERMINÉS")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_change_email_and_password()

