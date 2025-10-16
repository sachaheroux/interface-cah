#!/usr/bin/env python3
"""
Script pour diagnostiquer pourquoi les employés ne s'affichent pas sur le site
"""

import requests
import json
from datetime import datetime

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def check_api_response():
    """Vérifier la réponse de l'API"""
    
    print("🔍 DIAGNOSTIC DE L'AFFICHAGE DES EMPLOYÉS")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("1️⃣ VÉRIFICATION DE L'API EMPLOYÉS")
    print("-" * 40)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        print(f"✅ Statut HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Structure de la réponse:")
            print(f"   - Clés disponibles: {list(data.keys())}")
            
            employees = data.get('data', [])
            print(f"👥 Nombre d'employés: {len(employees)}")
            
            if employees:
                print("   Détails des employés:")
                for i, emp in enumerate(employees, 1):
                    print(f"   {i}. {emp.get('prenom', 'N/A')} {emp.get('nom', 'N/A')}")
                    print(f"      - ID: {emp.get('id_employe', 'N/A')}")
                    print(f"      - Poste: {emp.get('poste', 'N/A')}")
                    print(f"      - Taux: ${emp.get('taux_horaire', 'N/A')}/h")
                    print(f"      - Téléphone: {emp.get('numero', 'N/A')}")
                    print(f"      - Email: {emp.get('adresse_courriel', 'N/A')}")
                    print()
            else:
                print("   ⚠️ AUCUN EMPLOYÉ DANS LA RÉPONSE!")
                
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def check_frontend_api_call():
    """Simuler l'appel API du frontend"""
    
    print("\n2️⃣ SIMULATION DE L'APPEL FRONTEND")
    print("-" * 40)
    
    try:
        # Simuler exactement ce que fait le frontend
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            
            print(f"✅ Frontend recevrait: {len(employees)} employés")
            
            if employees:
                print("   Employés que le frontend verrait:")
                for emp in employees:
                    print(f"   - {emp['prenom']} {emp['nom']} (${emp.get('taux_horaire', 'N/A')}/h)")
            else:
                print("   ⚠️ Le frontend ne verrait AUCUN employé!")
                
        else:
            print(f"❌ Le frontend recevrait une erreur: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Le frontend aurait une erreur: {e}")

def check_database_structure():
    """Vérifier la structure de la base de données"""
    
    print("\n3️⃣ VÉRIFICATION DE LA STRUCTURE DE LA BASE")
    print("-" * 40)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/debug/employes-structure", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Structure de la table employes:")
            print(f"   - Colonnes: {data.get('columns', [])}")
            print(f"   - Nombre d'enregistrements: {data.get('count', 0)}")
            
            if data.get('count', 0) == 0:
                print("   ⚠️ PROBLÈME: La table est vide!")
            else:
                print("   ✅ La table contient des données")
                
        else:
            print(f"❌ Endpoint debug non disponible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur structure: {e}")

def test_employee_creation():
    """Tester la création d'un employé"""
    
    print("\n4️⃣ TEST DE CRÉATION D'EMPLOYÉ")
    print("-" * 40)
    
    test_employee = {
        "prenom": "Test",
        "nom": "Affichage",
        "poste": "Testeur",
        "numero": "(555) 999-8888",
        "adresse_courriel": "test@affichage.com",
        "taux_horaire": 20.0
    }
    
    try:
        # Créer l'employé de test
        response = requests.post(
            f"{CONSTRUCTION_BASE}/employes",
            json=test_employee,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            emp_id = data['data']['id_employe']
            print(f"✅ Employé de test créé: ID {emp_id}")
            
            # Vérifier immédiatement
            verify_response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                employees = verify_data.get('data', [])
                test_emp = next((emp for emp in employees if emp['id_employe'] == emp_id), None)
                
                if test_emp:
                    print(f"✅ Employé de test visible: {test_emp['prenom']} {test_emp['nom']}")
                    
                    # Nettoyer
                    delete_response = requests.delete(f"{CONSTRUCTION_BASE}/employes/{emp_id}", timeout=30)
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

def check_frontend_configuration():
    """Vérifier la configuration du frontend"""
    
    print("\n5️⃣ VÉRIFICATION DE LA CONFIGURATION FRONTEND")
    print("-" * 40)
    
    print("🔍 Points à vérifier côté frontend:")
    print("   1. L'URL de l'API est-elle correcte?")
    print("   2. Le service employeesService fonctionne-t-il?")
    print("   3. Y a-t-il des erreurs dans la console du navigateur?")
    print("   4. Le composant Employees.jsx charge-t-il les données?")
    print("   5. Y a-t-il des erreurs de CORS?")
    
    print("\n💡 Actions recommandées:")
    print("   1. Ouvrir la console du navigateur (F12)")
    print("   2. Aller sur la page Employés")
    print("   3. Vérifier les requêtes réseau dans l'onglet Network")
    print("   4. Chercher les erreurs dans la console")

def main():
    """Fonction principale"""
    
    check_api_response()
    check_frontend_api_call()
    check_database_structure()
    test_employee_creation()
    check_frontend_configuration()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTIC TERMINÉ")
    print("=" * 60)
    print("💡 Si les employés ne s'affichent toujours pas:")
    print("   1. Vérifiez la console du navigateur")
    print("   2. Vérifiez l'onglet Network dans les outils de développement")
    print("   3. Vérifiez que l'URL de l'API est correcte")
    print("   4. Testez l'API directement dans le navigateur")

if __name__ == "__main__":
    main()
