#!/usr/bin/env python3
"""
Script pour recréer les employés et tester la persistance
"""

import requests
import json
import time
from datetime import datetime

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def recreate_employees_with_persistence_test():
    """Recréer les employés et tester la persistance"""
    
    print("🚀 RECRÉATION DES EMPLOYÉS AVEC TEST DE PERSISTANCE")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Les employés corrects
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
    
    print("📝 Création des employés...")
    created_employees = []
    
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
                created_employees.append({
                    'id': emp_id,
                    'name': f"{emp_data['prenom']} {emp_data['nom']}",
                    'rate': emp_data['taux_horaire']
                })
                print(f"✅ Créé: ID {emp_id} - ${emp_data['taux_horaire']}/h")
            else:
                print(f"❌ Erreur: {response.status_code}")
                print(f"   Réponse: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n📊 Résultat création: {len(created_employees)}/{len(employees_data)} employés créés")
    
    # Test de persistance immédiate
    print("\n🔍 TEST DE PERSISTANCE IMMÉDIATE")
    print("-" * 40)
    
    time.sleep(2)  # Attendre 2 secondes
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            print(f"✅ Employés trouvés immédiatement: {len(employees)}")
            
            if employees:
                print("   Détails:")
                for emp in employees:
                    print(f"   - {emp['prenom']} {emp['nom']} (ID: {emp['id_employe']}) - ${emp.get('taux_horaire', 'N/A')}/h")
            else:
                print("   ⚠️ AUCUN EMPLOYÉ TROUVÉ!")
        else:
            print(f"❌ Erreur vérification: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
    
    # Test de persistance après délai
    print("\n⏳ TEST DE PERSISTANCE APRÈS DÉLAI (10 secondes)")
    print("-" * 40)
    
    print("   Attente de 10 secondes...")
    time.sleep(10)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            print(f"✅ Employés trouvés après délai: {len(employees)}")
            
            if employees:
                print("   Détails:")
                for emp in employees:
                    print(f"   - {emp['prenom']} {emp['nom']} (ID: {emp['id_employe']}) - ${emp.get('taux_horaire', 'N/A')}/h")
                    
                if len(employees) == len(created_employees):
                    print("   ✅ PERSISTANCE OK!")
                else:
                    print("   ⚠️ PERTE DE DONNÉES DÉTECTÉE!")
            else:
                print("   ❌ TOUS LES EMPLOYÉS ONT DISPARU!")
        else:
            print(f"❌ Erreur vérification: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
    
    return created_employees

def check_database_persistence():
    """Vérifier la persistance de la base de données"""
    
    print("\n🗄️ VÉRIFICATION DE LA PERSISTANCE DE LA BASE")
    print("-" * 40)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/debug/employes-structure", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Structure de la table employes:")
            print(f"   - Colonnes: {data.get('columns', [])}")
            print(f"   - Nombre d'enregistrements: {data.get('count', 0)}")
            
            if data.get('count', 0) > 0:
                print("   ✅ La table contient des données")
            else:
                print("   ⚠️ La table est vide - PROBLÈME DE PERSISTANCE!")
                
        else:
            print(f"❌ Endpoint debug non disponible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur vérification structure: {e}")

def main():
    """Fonction principale"""
    
    employees = recreate_employees_with_persistence_test()
    check_database_persistence()
    
    print("\n" + "=" * 70)
    print("🎯 TEST DE PERSISTANCE TERMINÉ")
    print("=" * 70)
    
    if len(employees) == 3:
        print("✅ Employés créés avec succès!")
        print("💡 Prochaines étapes:")
        print("   1. Vérifier sur le site si les employés s'affichent")
        print("   2. Si ils disparaissent encore, déployer le render.yaml avec disque persistant")
        print("   3. Configurer des sauvegardes automatiques")
    else:
        print("⚠️ Problème lors de la création des employés")
        print("💡 Vérifiez les logs pour plus de détails")

if __name__ == "__main__":
    main()
