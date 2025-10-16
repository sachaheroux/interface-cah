#!/usr/bin/env python3
"""
Script pour recréer immédiatement les employés après le diagnostic
"""

import requests
import json
from datetime import datetime

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def recreate_employees_now():
    """Recréer immédiatement les employés"""
    
    print("🚀 RECRÉATION IMMÉDIATE DES EMPLOYÉS")
    print("=" * 60)
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
    
    created_employees = []
    
    print("📝 Création des employés...")
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
    
    print(f"\n📊 Résultat: {len(created_employees)}/{len(employees_data)} employés créés")
    
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
    
    return created_employees

def main():
    """Fonction principale"""
    
    employees = recreate_employees_now()
    
    print("\n" + "=" * 60)
    print("🎯 RECRÉATION TERMINÉE")
    print("=" * 60)
    
    if len(employees) == 3:
        print("✅ Tous les employés ont été créés avec succès!")
        print("💡 Prochaines étapes:")
        print("   1. Déployer le nouveau render.yaml avec disque persistant")
        print("   2. Tester la persistance après redéploiement")
        print("   3. Configurer des sauvegardes automatiques")
    else:
        print("⚠️ Certains employés n'ont pas pu être créés")
        print("💡 Vérifiez les logs pour plus de détails")

if __name__ == "__main__":
    main()
