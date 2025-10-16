#!/usr/bin/env python3
"""
Script pour diagnostiquer pourquoi les données disparaissent malgré le disque persistant
"""

import requests
import json
from datetime import datetime

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def check_current_employees():
    """Vérifier l'état actuel des employés"""
    
    print("🔍 VÉRIFICATION DE L'ÉTAT ACTUEL")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            print(f"👥 Employés actuels: {len(employees)}")
            
            if employees:
                for emp in employees:
                    print(f"   - {emp['prenom']} {emp['nom']} (ID: {emp['id_employe']}) - ${emp.get('taux_horaire', 'N/A')}/h")
            else:
                print("   ⚠️ AUCUN EMPLOYÉ!")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def check_database_path():
    """Vérifier le chemin de la base de données"""
    
    print("\n🗄️ VÉRIFICATION DU CHEMIN DE LA BASE")
    print("-" * 40)
    
    try:
        # Essayer d'accéder à l'endpoint de debug
        response = requests.get(f"{CONSTRUCTION_BASE}/debug/employes-structure", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Informations de la base:")
            print(f"   - Colonnes: {data.get('columns', [])}")
            print(f"   - Nombre d'enregistrements: {data.get('count', 0)}")
            print(f"   - Chemin de la base: {data.get('database_path', 'Non spécifié')}")
            
            if data.get('count', 0) == 0:
                print("   ⚠️ PROBLÈME: La table est vide!")
            else:
                print("   ✅ La table contient des données")
                
        else:
            print(f"❌ Endpoint debug non disponible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")

def test_multiple_creations():
    """Tester plusieurs créations pour voir si elles persistent"""
    
    print("\n🔄 TEST DE MULTIPLES CRÉATIONS")
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
        # Créer l'employé
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
                    
                    # Attendre et vérifier à nouveau
                    import time
                    print("   Attente de 5 secondes...")
                    time.sleep(5)
                    
                    verify_response2 = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
                    if verify_response2.status_code == 200:
                        verify_data2 = verify_response2.json()
                        employees2 = verify_data2.get('data', [])
                        test_emp2 = next((emp for emp in employees2 if emp['id_employe'] == emp_id), None)
                        
                        if test_emp2:
                            print("   ✅ Employé toujours visible après 5 secondes")
                        else:
                            print("   ❌ Employé a disparu après 5 secondes!")
                    
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
        print(f"❌ Erreur test: {e}")

def check_render_configuration():
    """Vérifier la configuration Render"""
    
    print("\n⚙️ VÉRIFICATION DE LA CONFIGURATION RENDER")
    print("-" * 40)
    
    print("🔍 Points à vérifier sur Render:")
    print("   1. Le disque persistant est-il bien créé?")
    print("   2. Le chemin DATA_DIR est-il correct?")
    print("   3. L'application a-t-elle les permissions d'écriture?")
    print("   4. Y a-t-il des erreurs dans les logs Render?")
    
    print("\n💡 Actions recommandées:")
    print("   1. Aller sur le dashboard Render")
    print("   2. Vérifier la section 'Disks'")
    print("   3. Vérifier les logs de l'application")
    print("   4. Vérifier les variables d'environnement")

def create_employees_now():
    """Créer les employés maintenant"""
    
    print("\n👥 CRÉATION DES EMPLOYÉS MAINTENANT")
    print("-" * 40)
    
    employees_data = [
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
    
    created_count = 0
    
    for i, emp_data in enumerate(employees_data, 1):
        print(f"\n{i}️⃣ Création: {emp_data['prenom']} {emp_data['nom']}")
        
        try:
            response = requests.post(
                f"{CONSTRUCTION_BASE}/employes",
                json=emp_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                emp_id = data['data']['id_employe']
                created_count += 1
                print(f"✅ Créé: ID {emp_id} - ${emp_data['taux_horaire']}/h")
            else:
                print(f"❌ Erreur: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n📊 Résultat: {created_count}/{len(employees_data)} employés créés")
    
    # Vérification finale
    print("\n🔍 Vérification finale...")
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            print(f"✅ Employés dans la base: {len(employees)}")
            
            for emp in employees:
                print(f"   - {emp['prenom']} {emp['nom']} (${emp.get('taux_horaire', 'N/A')}/h)")
        else:
            print(f"❌ Erreur vérification: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")

def main():
    """Fonction principale"""
    
    check_current_employees()
    check_database_path()
    test_multiple_creations()
    check_render_configuration()
    create_employees_now()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSTIC TERMINÉ")
    print("=" * 50)
    print("💡 Si les employés disparaissent encore après déploiement:")
    print("   1. Vérifiez le dashboard Render pour les disques persistants")
    print("   2. Vérifiez les logs Render pour des erreurs")
    print("   3. Vérifiez que DATA_DIR pointe vers le bon chemin")
    print("   4. Considérez une solution de sauvegarde automatique")

if __name__ == "__main__":
    main()
