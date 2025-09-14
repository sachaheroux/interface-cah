#!/usr/bin/env python3
"""
Script pour vérifier la structure de la table tenants sur Render
"""

import requests
import json

def check_tenants_structure():
    """Vérifier la structure de la table tenants via l'API Render"""
    print("🔍 Vérification de la structure de la table tenants sur Render")
    
    try:
        # Tester l'API des locataires
        response = requests.get("https://interface-cah-backend.onrender.com/api/tenants")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API des locataires fonctionne")
            
            if data.get("data") and len(data["data"]) > 0:
                tenant = data["data"][0]
                print("\n📋 Structure d'un locataire existant:")
                print(json.dumps(tenant, indent=2, ensure_ascii=False))
                
                print("\n🔍 Colonnes disponibles:")
                for key in tenant.keys():
                    print(f"  - {key}")
            else:
                print("ℹ️ Aucun locataire trouvé")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_tenants_structure()
