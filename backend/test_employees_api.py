#!/usr/bin/env python3
"""
Script pour tester l'API des employés
"""

import requests
import json

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def test_employees_api():
    """Tester l'API des employés"""
    
    print("🔍 TEST DE L'API EMPLOYÉS")
    print("=" * 50)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            employes = data.get('data', [])
            print(f"\n📊 {len(employes)} employé(s) trouvé(s)")
            
            for employe in employes:
                print(f"   👤 {employe.get('prenom', 'N/A')} {employe.get('nom', 'N/A')}")
                print(f"      ID: {employe.get('id_employe', 'N/A')}")
                print(f"      Poste: {employe.get('poste', 'N/A')}")
                print(f"      Taux: ${employe.get('taux_horaire', 'N/A')}/h")
                print()
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_employees_api()
