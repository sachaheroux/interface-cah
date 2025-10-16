#!/usr/bin/env python3
"""
Script pour créer les 2 employés sur Render
"""

import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"

def create_employee(employee_data):
    """Créer un employé"""
    try:
        print(f"📡 Création de {employee_data['prenom']} {employee_data['nom']}...")
        
        response = requests.post(
            f"{RENDER_URL}/api/construction/employes",
            json=employee_data,
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"🎉 Employé créé avec succès !")
                print(f"   ID: {data['data']['id_employe']}")
                return True
            else:
                print(f"❌ Erreur: {data.get('message')}")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_employees():
    """Créer les 2 employés"""
    print("👥 Création des employés sur Render")
    print("=" * 50)
    
    employees = [
        {
            "prenom": "Sacha",
            "nom": "Héroux",
            "poste": "Charpentier",
            "numero": "(555) 123-4567",
            "adresse_courriel": "sacha@exemple.com",
            "taux_horaire": 35.00
        },
        {
            "prenom": "Daniel",
            "nom": "Baribeau",
            "poste": "Charpentier",
            "numero": "(555) 987-6543",
            "adresse_courriel": "daniel@exemple.com",
            "taux_horaire": 30.00
        }
    ]
    
    success_count = 0
    
    for emp in employees:
        if create_employee(emp):
            success_count += 1
        print()
    
    print(f"📊 Résultat: {success_count}/{len(employees)} employés créés")
    return success_count == len(employees)

def test_employees_after_creation():
    """Tester l'API des employés après création"""
    print("\n👥 Test des employés après création")
    print("=" * 50)
    
    try:
        response = requests.get(f"{RENDER_URL}/api/construction/employes", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                employees = data.get('data', [])
                print(f"👥 Nombre d'employés: {len(employees)}")
                
                if employees:
                    print("\n📋 Employés créés:")
                    for i, emp in enumerate(employees, 1):
                        print(f"  {i}. {emp.get('prenom', 'N/A')} {emp.get('nom', 'N/A')}")
                        print(f"     - ID: {emp.get('id_employe')}")
                        print(f"     - Poste: {emp.get('poste', 'N/A')}")
                        print(f"     - Taux horaire: ${emp.get('taux_horaire', 'N/A')}")
                        print(f"     - Email: {emp.get('adresse_courriel', 'N/A')}")
                        print()
                    return True
                else:
                    print("⚠️ Aucun employé trouvé")
                    return False
            else:
                print(f"❌ API error: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Création des employés - Interface CAH")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Créer les employés
    creation_success = create_employees()
    
    if creation_success:
        print("✅ Tous les employés créés avec succès")
        
        # Tester l'API
        test_success = test_employees_after_creation()
        
        if test_success:
            print("\n🎉 PROBLÈME RÉSOLU !")
            print("   Les employés sont maintenant visibles dans l'interface")
            print("   Tu peux rafraîchir la page Employees")
        else:
            print("\n⚠️ Employés créés mais problème persistant")
    else:
        print("\n❌ Échec de la création des employés")
    
    print("\n" + "=" * 50)
    print("🏁 Script terminé")

