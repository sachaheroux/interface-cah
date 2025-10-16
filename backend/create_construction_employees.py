#!/usr/bin/env python3
"""
Script pour créer des employés dans la base de construction
"""

import requests
import json
from datetime import datetime

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def create_construction_employees():
    """Créer des employés dans la base de construction"""
    
    employes_test = [
        {
            "prenom": "Sacha",
            "nom": "Héroux",
            "poste": "Charpentier",
            "numero": "(555) 123-4567",
            "adresse_courriel": "sacha@exemple.com",
            "taux_horaire": 35.00
        },
        {
            "prenom": "Daniel",
            "nom": "Baribeau",
            "poste": "Charpentier",
            "numero": "(555) 987-6543",
            "adresse_courriel": "daniel@exemple.com",
            "taux_horaire": 30.00
        }
    ]
    
    employes_crees = []
    
    print("👥 CRÉATION D'EMPLOYÉS DANS LA BASE CONSTRUCTION")
    print("=" * 60)
    
    for i, employe_data in enumerate(employes_test, 1):
        print(f"\n{i}️⃣ Création de l'employé: {employe_data['prenom']} {employe_data['nom']}")
        
        try:
            response = requests.post(
                f"{CONSTRUCTION_BASE}/employes",
                json=employe_data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                employe_id = data['data']['id_employe']
                employes_crees.append(employe_id)
                print(f"✅ Employé créé avec succès: ID {employe_id}")
                print(f"   Nom: {data['data']['prenom']} {data['data']['nom']}")
                print(f"   Poste: {data['data']['poste']}")
                print(f"   Taux: ${data['data']['taux_horaire']}/h")
            else:
                print(f"❌ Erreur création: {response.status_code}")
                print(f"   Réponse: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    print(f"\n📊 RÉSUMÉ")
    print("=" * 60)
    print(f"✅ {len(employes_crees)} employé(s) créé(s) avec succès")
    print(f"📋 IDs des employés: {employes_crees}")
    
    return employes_crees

def verify_construction_employees():
    """Vérifier que les employés ont été créés dans la base construction"""
    
    print("\n🔍 VÉRIFICATION DES EMPLOYÉS CONSTRUCTION")
    print("=" * 60)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            employes = data.get('data', [])
            
            print(f"✅ {len(employes)} employé(s) trouvé(s) dans la base construction")
            
            for employe in employes:
                print(f"   👤 ID: {employe['id_employe']} - {employe['prenom']} {employe['nom']}")
                print(f"      Poste: {employe['poste']}")
                print(f"      Taux: ${employe['taux_horaire']}/h")
                print(f"      Email: {employe['adresse_courriel']}")
                print()
            
            return employes
        else:
            print(f"❌ Erreur récupération: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

if __name__ == "__main__":
    print("🚀 SCRIPT DE CRÉATION D'EMPLOYÉS CONSTRUCTION")
    print("⏰", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Créer les employés
    employes_crees = create_construction_employees()
    
    # Vérifier les employés
    employes_verifies = verify_construction_employees()
    
    print("\n🎉 TERMINÉ!")
    print("=" * 60)
    print("💡 Les employés peuvent maintenant être sélectionnés")
    print("   dans le formulaire de pointage mobile.")
