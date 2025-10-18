#!/usr/bin/env python3
"""
Script pour tester directement sur Render quelle base de données est utilisée
"""

import requests
import json
from datetime import datetime

def test_render_database():
    """Tester la base de données sur Render"""
    
    print("🔍 TEST DE LA BASE DE DONNÉES SUR RENDER")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("1️⃣ TEST DE L'API LOCATIVE")
    print("-" * 40)
    
    try:
        # Tester l'API locative
        response = requests.get("https://interface-cah-backend.onrender.com/api/buildings", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API locative accessible: {response.status_code}")
            
            # Vérifier la structure de la réponse
            print(f"📊 Structure de la réponse: {list(data.keys())}")
            
            buildings = data.get('data', [])
            print(f"🏢 Nombre d'immeubles: {len(buildings)}")
            
            if buildings:
                print("   Exemples d'immeubles:")
                for i, building in enumerate(buildings[:3], 1):
                    print(f"   {i}. {building.get('nom', 'N/A')} (ID: {building.get('id', 'N/A')})")
            else:
                print("   ⚠️ Aucun immeuble trouvé")
                
        else:
            print(f"❌ Erreur API locative: {response.status_code}")
            print(f"   Réponse: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Erreur test API locative: {e}")
    
    print("\n2️⃣ TEST DE L'API CONSTRUCTION")
    print("-" * 40)
    
    try:
        # Tester l'API construction
        response = requests.get("https://interface-cah-backend.onrender.com/api/construction/employes", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API construction accessible: {response.status_code}")
            
            # Vérifier la structure de la réponse
            print(f"📊 Structure de la réponse: {list(data.keys())}")
            
            employees = data.get('data', [])
            print(f"👥 Nombre d'employés: {len(employees)}")
            
            if employees:
                print("   Exemples d'employés:")
                for i, emp in enumerate(employees[:3], 1):
                    print(f"   {i}. {emp.get('prenom', 'N/A')} {emp.get('nom', 'N/A')} (ID: {emp.get('id_employe', 'N/A')})")
            else:
                print("   ⚠️ Aucun employé trouvé")
                
        else:
            print(f"❌ Erreur API construction: {response.status_code}")
            print(f"   Réponse: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Erreur test API construction: {e}")
    
    print("\n3️⃣ TEST DE PERSISTANCE")
    print("-" * 40)
    
    # Créer un employé de test
    test_employee = {
        "prenom": "Test",
        "nom": "Persistance",
        "poste": "Testeur",
        "numero": "(555) 123-4567",
        "adresse_courriel": "test@persistance.com",
        "taux_horaire": 20.0
    }
    
    try:
        print("📝 Création d'un employé de test...")
        
        # Créer l'employé
        response = requests.post(
            "https://interface-cah-backend.onrender.com/api/construction/employes",
            json=test_employee,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            emp_id = data['data']['id_employe']
            print(f"✅ Employé de test créé: ID {emp_id}")
            
            # Vérifier immédiatement
            verify_response = requests.get("https://interface-cah-backend.onrender.com/api/construction/employes", timeout=30)
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                employees = verify_data.get('data', [])
                test_emp = next((emp for emp in employees if emp['id_employe'] == emp_id), None)
                
                if test_emp:
                    print(f"✅ Employé de test visible: {test_emp['prenom']} {test_emp['nom']}")
                    
                    # Nettoyer
                    delete_response = requests.delete(f"https://interface-cah-backend.onrender.com/api/construction/employes/{emp_id}", timeout=30)
                    if delete_response.status_code == 200:
                        print("✅ Employé de test supprimé")
                    else:
                        print(f"⚠️ Erreur suppression: {delete_response.status_code}")
                else:
                    print("❌ Employé de test NON visible après création!")
            else:
                print(f"❌ Erreur vérification: {verify_response.status_code}")
                
        else:
            print(f"❌ Erreur création: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur test persistance: {e}")
    
    print("\n4️⃣ ANALYSE")
    print("-" * 40)
    
    print("🔍 Conclusions:")
    print("   - Si l'API locative fonctionne avec des données persistantes")
    print("     → La base de données locative persiste correctement")
    print("   - Si l'API construction ne persiste pas")
    print("     → Problème de configuration de la base construction")
    print("   - Si les deux ne persistent pas")
    print("     → Problème général de persistance sur Render")

def main():
    """Fonction principale"""
    
    test_render_database()
    
    print("\n" + "=" * 60)
    print("🎯 TEST TERMINÉ")
    print("=" * 60)
    print("💡 Prochaines étapes:")
    print("   1. Analyser les résultats ci-dessus")
    print("   2. Si la partie locative persiste mais pas la construction")
    print("      → Problème de configuration de la base construction")
    print("   3. Si aucune des deux ne persiste")
    print("      → Problème général de persistance sur Render")
    print("   4. Vérifier la configuration Render dans le dashboard")

if __name__ == "__main__":
    main()
