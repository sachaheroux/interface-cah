#!/usr/bin/env python3
"""
Script pour effacer les anciens employés sur Render
"""

import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"

def list_employees():
    """Lister tous les employés"""
    print("👥 Liste des employés actuels")
    print("=" * 50)
    
    try:
        response = requests.get(f"{RENDER_URL}/api/construction/employes", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                employees = data.get('data', [])
                print(f"👥 Nombre d'employés: {len(employees)}")
                
                if employees:
                    print("\n📋 Employés trouvés:")
                    for i, emp in enumerate(employees, 1):
                        print(f"  {i}. {emp.get('prenom', 'N/A')} {emp.get('nom', 'N/A')}")
                        print(f"     - ID: {emp.get('id_employe')}")
                        print(f"     - Poste: {emp.get('poste', 'N/A')}")
                        print(f"     - Email: {emp.get('adresse_courriel', 'N/A')}")
                        print()
                    return employees
                else:
                    print("⚠️ Aucun employé trouvé")
                    return []
            else:
                print(f"❌ API error: {data.get('message')}")
                return []
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def delete_employee(employee_id, employee_name):
    """Supprimer un employé"""
    try:
        print(f"🗑️ Suppression de {employee_name} (ID: {employee_id})...")
        
        response = requests.delete(
            f"{RENDER_URL}/api/construction/employes/{employee_id}",
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"🎉 Employé supprimé avec succès !")
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

def delete_all_employees():
    """Supprimer tous les employés"""
    print("🗑️ Suppression de tous les employés")
    print("=" * 50)
    
    # Lister les employés
    employees = list_employees()
    
    if not employees:
        print("✅ Aucun employé à supprimer")
        return True
    
    print(f"\n⚠️ ATTENTION: {len(employees)} employé(s) seront supprimés !")
    
    # Demander confirmation
    confirm = input("Voulez-vous continuer ? (oui/non): ").lower().strip()
    
    if confirm not in ['oui', 'o', 'yes', 'y']:
        print("❌ Suppression annulée")
        return False
    
    success_count = 0
    
    for emp in employees:
        employee_name = f"{emp.get('prenom', 'N/A')} {emp.get('nom', 'N/A')}"
        if delete_employee(emp.get('id_employe'), employee_name):
            success_count += 1
        print()
    
    print(f"📊 Résultat: {success_count}/{len(employees)} employés supprimés")
    return success_count == len(employees)

def verify_deletion():
    """Vérifier que tous les employés ont été supprimés"""
    print("\n🔍 Vérification de la suppression")
    print("=" * 50)
    
    employees = list_employees()
    
    if not employees:
        print("✅ Tous les employés ont été supprimés")
        return True
    else:
        print(f"⚠️ {len(employees)} employé(s) restant(s)")
        return False

if __name__ == "__main__":
    print("🚀 Suppression des employés - Interface CAH")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Supprimer tous les employés
    deletion_success = delete_all_employees()
    
    if deletion_success:
        print("✅ Suppression terminée")
        
        # Vérifier la suppression
        verify_success = verify_deletion()
        
        if verify_success:
            print("\n🎉 SUPPRESSION CONFIRMÉE !")
            print("   Tu peux maintenant créer de nouveaux employés sur le site")
        else:
            print("\n⚠️ Suppression non confirmée")
    else:
        print("\n❌ Échec de la suppression")
    
    print("\n" + "=" * 50)
    print("🏁 Script terminé")

