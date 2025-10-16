#!/usr/bin/env python3
"""
Script pour diagnostiquer pourquoi les employés disparaissent constamment
"""

import requests
import json
import time
from datetime import datetime

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def check_api_status():
    """Vérifier le statut de l'API"""
    
    print("🔍 DIAGNOSTIC DE PERSISTANCE DES EMPLOYÉS")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("1️⃣ VÉRIFICATION DU STATUT DE L'API")
    print("-" * 40)
    
    try:
        # Test de base de l'API
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        print(f"✅ API accessible: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            print(f"👥 Employés actuels: {len(employees)}")
            
            if employees:
                print("   Détails des employés:")
                for emp in employees:
                    print(f"   - {emp['prenom']} {emp['nom']} (ID: {emp['id_employe']}) - ${emp.get('taux_horaire', 'N/A')}/h")
            else:
                print("   ⚠️ AUCUN EMPLOYÉ TROUVÉ!")
                
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_database_structure():
    """Tester la structure de la base de données"""
    
    print("\n2️⃣ VÉRIFICATION DE LA STRUCTURE DE LA BASE")
    print("-" * 40)
    
    try:
        # Test de l'endpoint de debug
        response = requests.get(f"{CONSTRUCTION_BASE}/debug/employes-structure", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Structure de la table employes:")
            print(f"   Colonnes: {data.get('columns', [])}")
            print(f"   Nombre d'enregistrements: {data.get('count', 0)}")
        else:
            print(f"❌ Endpoint debug non disponible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur structure: {e}")

def test_employee_creation():
    """Tester la création d'un employé de test"""
    
    print("\n3️⃣ TEST DE CRÉATION D'EMPLOYÉ")
    print("-" * 40)
    
    test_employee = {
        "prenom": "Test",
        "nom": "Diagnostic",
        "poste": "Testeur",
        "numero": "(555) 123-4567",
        "adresse_courriel": "test@diagnostic.com",
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
            time.sleep(1)
            verify_response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                employees = verify_data.get('data', [])
                test_emp = next((emp for emp in employees if emp['id_employe'] == emp_id), None)
                
                if test_emp:
                    print(f"✅ Employé de test vérifié: {test_emp['prenom']} {test_emp['nom']}")
                    
                    # Nettoyer - supprimer l'employé de test
                    delete_response = requests.delete(f"{CONSTRUCTION_BASE}/employes/{emp_id}", timeout=30)
                    if delete_response.status_code == 200:
                        print("✅ Employé de test supprimé")
                    else:
                        print(f"⚠️ Erreur suppression: {delete_response.status_code}")
                else:
                    print("❌ Employé de test non trouvé après création!")
            else:
                print(f"❌ Erreur vérification: {verify_response.status_code}")
                
        else:
            print(f"❌ Erreur création: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur test création: {e}")

def check_render_logs():
    """Vérifier les logs Render (simulation)"""
    
    print("\n4️⃣ DIAGNOSTIC RENDER")
    print("-" * 40)
    
    print("🔍 Causes possibles de disparition des employés:")
    print("   1. Redémarrage de l'application Render")
    print("   2. Redéploiement automatique")
    print("   3. Problème de persistance du disque")
    print("   4. Erreur dans l'initialisation de la base")
    print("   5. Conflit de schéma de base de données")
    print("   6. Timeout de connexion à la base")
    
    print("\n💡 Solutions recommandées:")
    print("   1. Vérifier les logs Render dans le dashboard")
    print("   2. S'assurer que le disque persistant est bien configuré")
    print("   3. Ajouter des logs de debug dans l'API")
    print("   4. Implémenter une sauvegarde automatique")
    print("   5. Ajouter des vérifications de santé de la base")

def create_persistence_test():
    """Créer un test de persistance étendu"""
    
    print("\n5️⃣ TEST DE PERSISTANCE ÉTENDU")
    print("-" * 40)
    
    # Créer plusieurs employés
    employees_to_create = [
        {
            "prenom": "Sacha",
            "nom": "Héroux",
            "poste": "Charpentier",
            "numero": "(819) 266-9025",
            "adresse_courriel": "sacha.heroux87@gmail.com",
            "taux_horaire": 25.0
        },
        {
            "prenom": "Daniel",
            "nom": "Baribeau",
            "poste": "Charpentier",
            "numero": "(819) 266-8904",
            "adresse_courriel": "",
            "taux_horaire": 35.0
        },
        {
            "prenom": "Mickaël",
            "nom": "Beaudoin",
            "poste": "Charpentier",
            "numero": "",
            "adresse_courriel": "",
            "taux_horaire": 30.0
        }
    ]
    
    created_ids = []
    
    print("📝 Création des employés...")
    for i, emp_data in enumerate(employees_to_create, 1):
        try:
            response = requests.post(
                f"{CONSTRUCTION_BASE}/employes",
                json=emp_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                emp_id = data['data']['id_employe']
                created_ids.append(emp_id)
                print(f"   ✅ {i}. {emp_data['prenom']} {emp_data['nom']} (ID: {emp_id})")
            else:
                print(f"   ❌ {i}. Erreur: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {i}. Exception: {e}")
    
    print(f"\n📊 Résultat: {len(created_ids)}/{len(employees_to_create)} employés créés")
    
    # Vérification immédiate
    print("\n🔍 Vérification immédiate...")
    time.sleep(2)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            print(f"   Employés trouvés: {len(employees)}")
            
            for emp in employees:
                print(f"   - {emp['prenom']} {emp['nom']} (ID: {emp['id_employe']})")
                
            if len(employees) != len(created_ids):
                print("   ⚠️ DISCREPANCE DÉTECTÉE!")
                print(f"   Créés: {len(created_ids)}, Trouvés: {len(employees)}")
        else:
            print(f"   ❌ Erreur vérification: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erreur vérification: {e}")

def main():
    """Fonction principale"""
    
    check_api_status()
    test_database_structure()
    test_employee_creation()
    check_render_logs()
    create_persistence_test()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTIC TERMINÉ")
    print("=" * 60)
    print("💡 Si les employés disparaissent encore:")
    print("   1. Vérifiez les logs Render")
    print("   2. Testez la persistance du disque")
    print("   3. Ajoutez des logs de debug dans l'API")
    print("   4. Considérez une sauvegarde automatique")

if __name__ == "__main__":
    main()
