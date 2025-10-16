#!/usr/bin/env python3
"""
Script pour parser la réponse de l'endpoint de debug
"""

import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"

def check_employees_structure():
    """Vérifier la structure de la table employes"""
    print("🔍 Vérification de la structure de la table employes")
    print("=" * 60)
    
    try:
        print(f"📡 Appel de l'endpoint de debug...")
        response = requests.get(f"{RENDER_URL}/api/construction/debug/employes-structure", timeout=30)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Réponse complète:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                structure = data.get('structure', [])
                count = data.get('count', 0)
                sample_data = data.get('sample_data', [])
                
                print(f"\n📋 Structure de la table employes:")
                for col in structure:
                    print(f"  - {col['name']}: {col['type']} (not_null: {col['not_null']})")
                
                print(f"\n👥 Nombre d'employés dans la base: {count}")
                
                if sample_data:
                    print(f"\n📋 Exemples d'employés:")
                    for i, emp in enumerate(sample_data, 1):
                        print(f"  {i}. {emp.get('prenom', 'N/A')} {emp.get('nom', 'N/A')}")
                        print(f"     - ID: {emp.get('id_employe')}")
                        print(f"     - Poste: {emp.get('poste', 'N/A')}")
                        print(f"     - Taux horaire: {emp.get('taux_horaire', 'N/A')}")
                        print(f"     - Email: {emp.get('adresse_courriel', 'N/A')}")
                        print()
                else:
                    print("⚠️ Aucun employé trouvé dans la base")
                
                # Vérifier si la colonne taux_horaire existe
                column_names = [col['name'] for col in structure]
                if 'taux_horaire' in column_names:
                    print("✅ Colonne 'taux_horaire' présente dans la structure")
                else:
                    print("❌ Colonne 'taux_horaire' MANQUANTE dans la structure")
                    print("   C'est pourquoi l'API retourne 0 employés !")
                    
            else:
                print(f"❌ Erreur dans la réponse: {data.get('error')}")
                
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 Debug structure employes - Interface CAH")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_employees_structure()
    
    print("\n" + "=" * 60)
    print("🏁 Analyse terminée")

