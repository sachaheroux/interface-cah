#!/usr/bin/env python3
"""
Script pour nettoyer les doublons d'employés
"""

import requests
import json
from datetime import datetime

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def clean_duplicate_employees():
    """Nettoyer les doublons d'employés"""
    
    print("🧹 NETTOYAGE DES DOUBLONS D'EMPLOYÉS")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Récupérer tous les employés
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            print(f"👥 Employés actuels: {len(employees)}")
            
            # Grouper par nom pour identifier les doublons
            employees_by_name = {}
            for emp in employees:
                key = f"{emp['prenom']} {emp['nom']}"
                if key not in employees_by_name:
                    employees_by_name[key] = []
                employees_by_name[key].append(emp)
            
            print("\n🔍 Analyse des doublons:")
            duplicates_found = False
            
            for name, emp_list in employees_by_name.items():
                if len(emp_list) > 1:
                    duplicates_found = True
                    print(f"   ⚠️ {name}: {len(emp_list)} exemplaires")
                    for i, emp in enumerate(emp_list):
                        print(f"      {i+1}. ID {emp['id_employe']} - ${emp.get('taux_horaire', 'N/A')}/h")
                else:
                    print(f"   ✅ {name}: 1 exemplaire (ID {emp_list[0]['id_employe']})")
            
            if not duplicates_found:
                print("✅ Aucun doublon trouvé!")
                return
            
            # Supprimer les doublons (garder le plus récent)
            print("\n🗑️ Suppression des doublons...")
            deleted_count = 0
            
            for name, emp_list in employees_by_name.items():
                if len(emp_list) > 1:
                    # Garder le plus récent (ID le plus élevé)
                    emp_list.sort(key=lambda x: x['id_employe'], reverse=True)
                    keep_emp = emp_list[0]
                    delete_emps = emp_list[1:]
                    
                    print(f"\n   Garder: {name} (ID {keep_emp['id_employe']})")
                    
                    for emp in delete_emps:
                        try:
                            delete_response = requests.delete(
                                f"{CONSTRUCTION_BASE}/employes/{emp['id_employe']}",
                                timeout=30
                            )
                            
                            if delete_response.status_code == 200:
                                print(f"   ✅ Supprimé: ID {emp['id_employe']}")
                                deleted_count += 1
                            else:
                                print(f"   ❌ Erreur suppression ID {emp['id_employe']}: {delete_response.status_code}")
                                
                        except Exception as e:
                            print(f"   ❌ Exception suppression ID {emp['id_employe']}: {e}")
            
            print(f"\n📊 Résultat: {deleted_count} doublon(s) supprimé(s)")
            
        else:
            print(f"❌ Erreur récupération: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

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
            else:
                print("   ⚠️ Aucun employé trouvé!")
                
        else:
            print(f"❌ Erreur vérification: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")

def main():
    """Fonction principale"""
    
    clean_duplicate_employees()
    verify_final_state()
    
    print("\n" + "=" * 60)
    print("🎯 NETTOYAGE TERMINÉ")
    print("=" * 60)
    print("💡 Maintenant tu peux:")
    print("   1. Aller sur le site pour voir les employés")
    print("   2. Créer/modifier des employés via l'interface")
    print("   3. Déployer le render.yaml avec disque persistant")

if __name__ == "__main__":
    main()
