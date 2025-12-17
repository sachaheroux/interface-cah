#!/usr/bin/env python3
"""
Script simple pour exécuter la migration bail-add-id-unite
"""

import requests
import sys

# URL de votre API (modifiez si nécessaire)
API_URL = "https://interface-cah-backend.onrender.com"

def run_migration():
    """Exécuter la migration via l'API"""
    url = f"{API_URL}/api/migrate/bail-add-id-unite"
    
    print("🚀 Démarrage de la migration...")
    print(f"📡 URL : {url}")
    print()
    
    try:
        response = requests.post(url, timeout=300)  # 5 minutes timeout
        
        print("📥 Réponse reçue :")
        print(f"   Status : {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RÉSULTAT :")
            print(f"   Succès : {result.get('success', False)}")
            print(f"   Message : {result.get('message', 'N/A')}")
            if result.get('details'):
                print(f"   Détails : {result.get('details')}")
        else:
            print("❌ ERREUR :")
            print(f"   {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Timeout - La migration prend trop de temps")
        print("   Vérifiez les logs sur Render pour voir l'état")
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion")
        print(f"   Impossible de se connecter à {API_URL}")
        print("   Vérifiez que l'application est démarrée sur Render")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    # Permettre de passer l'URL en argument
    if len(sys.argv) > 1:
        API_URL = sys.argv[1]
    
    run_migration()

