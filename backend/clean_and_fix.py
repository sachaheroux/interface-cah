#!/usr/bin/env python3
"""
Script pour nettoyer les doublons et vérifier la configuration Render
"""

import requests
import json
from datetime import datetime

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def clean_all_duplicates():
    """Nettoyer tous les doublons"""
    
    print("🧹 NETTOYAGE COMPLET DES DOUBLONS")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Récupérer tous les employés
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            print(f"👥 Employés actuels: {len(employees)}")
            
            if not employees:
                print("✅ Aucun employé à nettoyer")
                return
            
            # Supprimer TOUS les employés
            print("\n🗑️ Suppression de tous les employés...")
            deleted_count = 0
            
            for emp in employees:
                try:
                    delete_response = requests.delete(
                        f"{CONSTRUCTION_BASE}/employes/{emp['id_employe']}",
                        timeout=30
                    )
                    
                    if delete_response.status_code == 200:
                        print(f"   ✅ Supprimé: {emp['prenom']} {emp['nom']} (ID: {emp['id_employe']})")
                        deleted_count += 1
                    else:
                        print(f"   ❌ Erreur suppression ID {emp['id_employe']}: {delete_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Exception suppression ID {emp['id_employe']}: {e}")
            
            print(f"\n📊 Résultat: {deleted_count}/{len(employees)} employés supprimés")
            
        else:
            print(f"❌ Erreur récupération: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def create_clean_employees():
    """Créer les employés propres (sans doublons)"""
    
    print("\n👥 CRÉATION DES EMPLOYÉS PROPRES")
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
    
    return created_count

def verify_final_state():
    """Vérifier l'état final"""
    
    print("\n🔍 VÉRIFICATION DE L'ÉTAT FINAL")
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

def check_render_disk_config():
    """Vérifier la configuration du disque Render"""
    
    print("\n⚙️ VÉRIFICATION DE LA CONFIGURATION RENDER")
    print("-" * 40)
    
    print("🔍 Actions à effectuer sur Render:")
    print("   1. Aller sur https://dashboard.render.com")
    print("   2. Sélectionner votre service 'interface-cah-backend'")
    print("   3. Vérifier la section 'Disks':")
    print("      - Y a-t-il un disque 'cah-persistent-disk'?")
    print("      - Le montage est-il sur '/opt/render/project/src/data'?")
    print("   4. Vérifier les variables d'environnement:")
    print("      - DATA_DIR = /opt/render/project/src/data")
    print("   5. Vérifier les logs pour des erreurs de montage")
    
    print("\n💡 Si le disque n'existe pas:")
    print("   1. Créer un nouveau disque persistant")
    print("   2. Le monter sur '/opt/render/project/src/data'")
    print("   3. Redémarrer l'application")

def main():
    """Fonction principale"""
    
    clean_all_duplicates()
    created_count = create_clean_employees()
    verify_final_state()
    check_render_disk_config()
    
    print("\n" + "=" * 50)
    print("🎯 NETTOYAGE TERMINÉ")
    print("=" * 50)
    
    if created_count == 3:
        print("✅ Employés créés avec succès!")
        print("💡 Prochaines étapes:")
        print("   1. Vérifier sur le site si les employés s'affichent")
        print("   2. Vérifier la configuration du disque Render")
        print("   3. Tester la persistance après un redéploiement")
    else:
        print("⚠️ Problème lors de la création des employés")

if __name__ == "__main__":
    main()
