#!/usr/bin/env python3
"""
Script pour créer les employés sur Render
"""

import requests
import json
from datetime import datetime

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def create_employees_on_render():
    """Créer les employés sur Render"""
    
    # Les mêmes employés que dans ta base locale
    employes_data = [
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
    
    print("👥 CRÉATION DES EMPLOYÉS SUR RENDER")
    print("=" * 50)
    
    for i, employe in enumerate(employes_data, 1):
        print(f"\n{i}️⃣ Création: {employe['prenom']} {employe['nom']}")
        
        try:
            response = requests.post(
                f"{CONSTRUCTION_BASE}/employes",
                json=employe,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Créé avec succès: ID {data['data']['id_employe']}")
                print(f"   Taux: ${data['data']['taux_horaire']}/h")
            else:
                print(f"❌ Erreur: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")

def verify_employees_on_render():
    """Vérifier les employés sur Render"""
    
    print("\n🔍 VÉRIFICATION SUR RENDER")
    print("=" * 50)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/employes", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            employes = data.get('data', [])
            
            print(f"✅ {len(employes)} employé(s) trouvé(s) sur Render")
            
            for employe in employes:
                print(f"   👤 {employe['prenom']} {employe['nom']} - ${employe['taux_horaire']}/h")
            
            return len(employes) > 0
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SYNCHRONISATION EMPLOYÉS RENDER")
    print("⏰", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Créer les employés
    create_employees_on_render()
    
    # Vérifier
    success = verify_employees_on_render()
    
    if success:
        print("\n🎉 SUCCÈS!")
        print("💡 Le formulaire de pointage devrait maintenant fonctionner")
    else:
        print("\n❌ ÉCHEC!")
        print("💡 Il y a encore un problème avec l'API")
