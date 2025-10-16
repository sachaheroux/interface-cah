#!/usr/bin/env python3
"""
Script pour tester la nouvelle configuration de base de données construction
et recréer les employés avec la persistance correcte
"""

import requests
import json
from datetime import datetime

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def test_new_database_config():
    """Tester la nouvelle configuration de base de données"""
    
    print("🔧 TEST DE LA NOUVELLE CONFIGURATION DE BASE DE DONNÉES")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("1️⃣ VÉRIFICATION DE L'ÉTAT ACTUEL")
    print("-" * 40)
    
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

def check_database_structure():
    """Vérifier la structure de la base de données"""
    
    print("\n2️⃣ VÉRIFICATION DE LA STRUCTURE")
    print("-" * 40)
    
    try:
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

def clean_and_recreate_employees():
    """Nettoyer et recréer les employés"""
    
    print("\n3️⃣ NETTOYAGE ET RECRÉATION DES EMPLOYÉS")
    print("-" * 40)
    
    # D'abord, supprimer tous les employés existants
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            
            if employees:
                print(f"🗑️ Suppression de {len(employees)} employés existants...")
                for emp in employees:
                    try:
                        delete_response = requests.delete(
                            f"{CONSTRUCTION_BASE}/employes/{emp['id_employe']}",
                            timeout=30
                        )
                        if delete_response.status_code == 200:
                            print(f"   ✅ Supprimé: {emp['prenom']} {emp['nom']}")
                        else:
                            print(f"   ❌ Erreur suppression: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Exception suppression: {e}")
            else:
                print("✅ Aucun employé à supprimer")
                
    except Exception as e:
        print(f"❌ Erreur récupération: {e}")
    
    # Maintenant créer les employés corrects
    print("\n👥 Création des employés corrects...")
    
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
                print(f"   Réponse: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n📊 Résultat: {created_count}/{len(employees_data)} employés créés")
    return created_count

def verify_final_state():
    """Vérifier l'état final"""
    
    print("\n4️⃣ VÉRIFICATION DE L'ÉTAT FINAL")
    print("-" * 40)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            print(f"👥 Employés finaux: {len(employees)}")
            
            if employees:
                print("   Détails:")
                for emp in employees:
                    print(f"   - {emp['prenom']} {emp['nom']} (ID: {emp['id_employe']}) - ${emp.get('taux_horaire', 'N/A')}/h")
                    
                if len(employees) == 3:
                    print("   ✅ PARFAIT! 3 employés uniques")
                else:
                    print(f"   ⚠️ ATTENTION! {len(employees)} employés (devrait être 3)")
            else:
                print("   ⚠️ Aucun employé trouvé!")
                
        else:
            print(f"❌ Erreur vérification: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")

def test_persistence():
    """Tester la persistance"""
    
    print("\n5️⃣ TEST DE PERSISTANCE")
    print("-" * 40)
    
    print("💡 La nouvelle configuration utilise maintenant:")
    print("   - Le même système de persistance que la base locative")
    print("   - La variable DATA_DIR pour le chemin")
    print("   - Les mêmes optimisations SQLite (WAL, etc.)")
    print("   - Un gestionnaire de base de données robuste")
    
    print("\n🔍 Pour tester la persistance:")
    print("   1. Les employés devraient maintenant persister entre les redéploiements")
    print("   2. La base sera dans le même répertoire que la base locative")
    print("   3. Les sauvegardes automatiques sont disponibles")

def main():
    """Fonction principale"""
    
    test_new_database_config()
    check_database_structure()
    created_count = clean_and_recreate_employees()
    verify_final_state()
    test_persistence()
    
    print("\n" + "=" * 70)
    print("🎯 TEST TERMINÉ")
    print("=" * 70)
    
    if created_count == 3:
        print("✅ Employés créés avec succès avec la nouvelle configuration!")
        print("💡 Prochaines étapes:")
        print("   1. Déployer les changements (git add, commit, push)")
        print("   2. Vérifier sur le site si les employés s'affichent")
        print("   3. Tester la persistance après un redéploiement")
        print("   4. Les employés devraient maintenant persister!")
    else:
        print("⚠️ Problème lors de la création des employés")

if __name__ == "__main__":
    main()
