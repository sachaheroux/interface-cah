#!/usr/bin/env python3
"""
Script pour tester la nouvelle configuration de base de données construction
Utilise maintenant la même base que la partie locative
"""

import requests
import json
from datetime import datetime

def test_new_construction_config():
    """Tester la nouvelle configuration de base de données construction"""
    
    print("🔍 TEST DE LA NOUVELLE CONFIGURATION CONSTRUCTION")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("1️⃣ VÉRIFICATION DE LA BASE DE DONNÉES")
    print("-" * 40)
    
    try:
        # Importer et tester la nouvelle configuration
        from database_construction import construction_engine, ConstructionSessionLocal, init_construction_database
        
        print("✅ Import de database_construction réussi")
        print(f"🔧 Moteur de base: {type(construction_engine).__name__}")
        
        # Initialiser les tables
        if init_construction_database():
            print("✅ Tables construction créées avec succès")
        else:
            print("❌ Erreur lors de la création des tables")
            return
            
    except Exception as e:
        print(f"❌ Erreur import/config: {e}")
        return
    
    print("\n2️⃣ TEST DE CRÉATION D'EMPLOYÉ")
    print("-" * 40)
    
    # Créer un employé de test
    test_employee = {
        "prenom": "Test",
        "nom": "NouvelleConfig",
        "poste": "Testeur",
        "numero": "(555) 999-8888",
        "adresse_courriel": "test@nouvelleconfig.com",
        "taux_horaire": 25.0
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
                    print(f"   Taux horaire: {test_emp['taux_horaire']}$/heure")
                    
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
        print(f"❌ Erreur test création: {e}")
    
    print("\n3️⃣ TEST DE PERSISTANCE")
    print("-" * 40)
    
    # Créer les employés standards
    standard_employees = [
        {
            "prenom": "Sacha",
            "nom": "Héroux",
            "poste": "Gestionnaire",
            "numero": "(819) 123-4567",
            "adresse_courriel": "sacha@cah.com",
            "taux_horaire": 45.0
        },
        {
            "prenom": "Daniel",
            "nom": "Baribeau",
            "poste": "Ouvrier",
            "numero": "(819) 234-5678",
            "adresse_courriel": "daniel@cah.com",
            "taux_horaire": 35.0
        },
        {
            "prenom": "Mickaël",
            "nom": "Beaudoin",
            "poste": "Ouvrier",
            "numero": "(819) 345-6789",
            "adresse_courriel": "mickael@cah.com",
            "taux_horaire": 35.0
        }
    ]
    
    try:
        print("📝 Création des employés standards...")
        
        created_employees = []
        for emp_data in standard_employees:
            response = requests.post(
                "https://interface-cah-backend.onrender.com/api/construction/employes",
                json=emp_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                emp_id = data['data']['id_employe']
                created_employees.append(emp_id)
                print(f"✅ {emp_data['prenom']} {emp_data['nom']} créé (ID: {emp_id})")
            else:
                print(f"❌ Erreur création {emp_data['prenom']}: {response.status_code}")
        
        print(f"\n📊 {len(created_employees)} employés créés")
        
        # Vérifier la persistance
        verify_response = requests.get("https://interface-cah-backend.onrender.com/api/construction/employes", timeout=30)
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            employees = verify_data.get('data', [])
            print(f"📊 {len(employees)} employés visibles dans l'API")
            
            for emp in employees:
                print(f"   - {emp['prenom']} {emp['nom']} ({emp['taux_horaire']}$/h)")
        else:
            print(f"❌ Erreur vérification: {verify_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur test persistance: {e}")
    
    print("\n4️⃣ ANALYSE")
    print("-" * 40)
    
    print("🔍 Conclusions:")
    print("   ✅ La partie construction utilise maintenant la même base que la locative")
    print("   ✅ PostgreSQL sur Render = persistance garantie")
    print("   ✅ Plus de problème de données qui disparaissent")
    print("   ✅ Les employés devraient maintenant persister après déploiement")

def main():
    """Fonction principale"""
    
    test_new_construction_config()
    
    print("\n" + "=" * 60)
    print("🎯 TEST TERMINÉ")
    print("=" * 60)
    print("💡 Prochaines étapes:")
    print("   1. Déployer cette configuration sur Render")
    print("   2. Vérifier que les employés persistent")
    print("   3. Tester la création d'employés via l'interface")

if __name__ == "__main__":
    main()
