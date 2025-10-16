#!/usr/bin/env python3
"""
Script pour nettoyer et recréer les employés corrects
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def delete_all_employees():
    """Supprimer tous les employés existants"""
    
    print("🗑️ SUPPRESSION DE TOUS LES EMPLOYÉS")
    print("=" * 60)
    
    try:
        # Récupérer tous les employés
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            
            print(f"👥 {len(employees)} employé(s) trouvé(s) à supprimer")
            
            for emp in employees:
                print(f"   Suppression: {emp['prenom']} {emp['nom']} (ID: {emp['id_employe']})")
                
                # Supprimer l'employé
                delete_response = requests.delete(
                    f"{CONSTRUCTION_BASE}/employes/{emp['id_employe']}",
                    timeout=30
                )
                
                if delete_response.status_code == 200:
                    print(f"   ✅ Supprimé")
                else:
                    print(f"   ❌ Erreur: {delete_response.status_code}")
            
            print(f"\n✅ {len(employees)} employé(s) supprimé(s)")
        else:
            print(f"❌ Erreur récupération: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def create_correct_employees():
    """Créer seulement les employés corrects"""
    
    print("\n👥 CRÉATION DES EMPLOYÉS CORRECTS")
    print("=" * 60)
    
    # Les employés que tu veux vraiment
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
                created_employees.append(emp_id)
                print(f"✅ Créé: ID {emp_id} - ${emp_data['taux_horaire']}/h")
            else:
                print(f"❌ Erreur: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    return created_employees

def verify_final_state():
    """Vérifier l'état final"""
    
    print("\n🔍 VÉRIFICATION FINALE")
    print("=" * 60)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            
            print(f"👥 {len(employees)} employé(s) final:")
            for emp in employees:
                print(f"   - {emp['prenom']} {emp['nom']} (${emp['taux_horaire']}/h)")
        else:
            print(f"❌ Erreur: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 NETTOYAGE ET RECRÉATION DES EMPLOYÉS")
    print("⏰", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Supprimer tous les employés
    delete_all_employees()
    
    # Créer les employés corrects
    employees = create_correct_employees()
    
    # Vérifier l'état final
    verify_final_state()
    
    print("\n🎉 TERMINÉ!")
    print("=" * 60)
    print("💡 Maintenant il n'y a qu'une seule base de données")
    print("   avec les 3 employés corrects.")
