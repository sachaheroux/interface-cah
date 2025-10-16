#!/usr/bin/env python3
"""
Script pour vérifier et recréer les données manquantes
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def check_current_data():
    """Vérifier l'état actuel des données"""
    
    print("🔍 VÉRIFICATION DES DONNÉES ACTUELLES")
    print("=" * 60)
    
    # Vérifier les employés
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            print(f"👥 Employés: {len(employees)} trouvé(s)")
            for emp in employees:
                print(f"   - {emp['prenom']} {emp['nom']} (${emp['taux_horaire']}/h)")
        else:
            print(f"❌ Erreur employés: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur employés: {e}")
    
    # Vérifier les projets
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/projets", timeout=30)
        if response.status_code == 200:
            data = response.json()
            projects = data.get('data', [])
            print(f"🏗️ Projets: {len(projects)} trouvé(s)")
            for proj in projects:
                print(f"   - {proj['nom']}")
        else:
            print(f"❌ Erreur projets: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur projets: {e}")
    
    # Vérifier les pointages
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/punchs-employes", timeout=30)
        if response.status_code == 200:
            data = response.json()
            punchs = data.get('data', [])
            print(f"⏰ Pointages: {len(punchs)} trouvé(s)")
            for punch in punchs:
                print(f"   - ID {punch['id_punch']}: {punch['date']} ({punch['heure_travaillee']}h)")
        else:
            print(f"❌ Erreur pointages: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur pointages: {e}")

def recreate_employees():
    """Recréer les employés"""
    
    print("\n👥 RECRÉATION DES EMPLOYÉS")
    print("=" * 60)
    
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

def recreate_projects():
    """Recréer les projets"""
    
    print("\n🏗️ RECRÉATION DES PROJETS")
    print("=" * 60)
    
    projects_data = [
        {
            "nom": "Maison Unifamiliale - 123 Rue Principale",
            "date_debut": (datetime.now() - timedelta(days=30)).isoformat(),
            "date_fin_prevue": (datetime.now() + timedelta(days=60)).isoformat(),
            "notes": "Construction d'une maison unifamiliale de 3 chambres"
        },
        {
            "nom": "Condominium - 456 Avenue Centrale",
            "date_debut": (datetime.now() - timedelta(days=15)).isoformat(),
            "date_fin_prevue": (datetime.now() + timedelta(days=90)).isoformat(),
            "notes": "Construction d'un bâtiment de 12 unités"
        },
        {
            "nom": "Rénovation Commerciale - Centre-Ville",
            "date_debut": (datetime.now() - timedelta(days=7)).isoformat(),
            "date_fin_prevue": (datetime.now() + timedelta(days=45)).isoformat(),
            "notes": "Rénovation complète d'un bâtiment commercial"
        },
        {
            "nom": "Garage Résidentiel - 789 Rue Secondaire",
            "date_debut": datetime.now().isoformat(),
            "date_fin_prevue": (datetime.now() + timedelta(days=21)).isoformat(),
            "notes": "Construction d'un garage double pour résidence"
        }
    ]
    
    created_projects = []
    
    for i, proj_data in enumerate(projects_data, 1):
        print(f"\n{i}️⃣ Création: {proj_data['nom']}")
        
        try:
            response = requests.post(
                f"{CONSTRUCTION_BASE}/projets",
                json=proj_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                proj_id = data['data']['id_projet']
                created_projects.append(proj_id)
                print(f"✅ Créé: ID {proj_id}")
            else:
                print(f"❌ Erreur: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    return created_projects

if __name__ == "__main__":
    print("🚀 VÉRIFICATION ET RECRÉATION DES DONNÉES")
    print("⏰", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Vérifier l'état actuel
    check_current_data()
    
    # Recréer les employés
    employees = recreate_employees()
    
    # Recréer les projets
    projects = recreate_projects()
    
    print("\n🎉 TERMINÉ!")
    print("=" * 60)
    print(f"✅ {len(employees)} employé(s) créé(s)")
    print(f"✅ {len(projects)} projet(s) créé(s)")
    print("💡 Les données sont maintenant disponibles sur l'interface")
