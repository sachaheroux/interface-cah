#!/usr/bin/env python3
"""
Script pour tester si l'endpoint API des punchs fonctionne et voir la structure des données
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def test_punchs_api():
    """Tester l'endpoint API des punchs"""
    print("=" * 60)
    print("TEST DE L'ENDPOINT API PUNCHS EMPLOYÉS")
    print("=" * 60)
    print(f"🌐 URL Render: {RENDER_URL}")
    print()
    
    try:
        # Récupérer tous les punchs
        print("1️⃣ RÉCUPÉRATION DES PUNCHS")
        print("-" * 60)
        
        response = requests.get(f"{RENDER_URL}/api/construction/punchs-employes", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                punchs = data.get('data', [])
                print(f"✅ {len(punchs)} punch(s) trouvé(s)")
                print()
                
                if len(punchs) > 0:
                    print("2️⃣ STRUCTURE DU PREMIER PUNCH")
                    print("-" * 60)
                    first_punch = punchs[0]
                    print(json.dumps(first_punch, indent=2, ensure_ascii=False))
                    print()
                    
                    print("3️⃣ TOUS LES PUNCHS")
                    print("-" * 60)
                    for idx, punch in enumerate(punchs, 1):
                        print(f"\n📋 PUNCH #{idx}")
                        print(f"   ID: {punch.get('id_punch')}")
                        print(f"   Employé ID: {punch.get('id_employe')}")
                        print(f"   Projet ID: {punch.get('id_projet')}")
                        print(f"   Date: {punch.get('date')}")
                        print(f"   Heures travaillées: {punch.get('heure_travaillee')}")
                        print(f"   Section: {punch.get('section')}")
                        
                        # Afficher les relations si présentes
                        if punch.get('employe'):
                            emp = punch['employe']
                            print(f"   Employé: {emp.get('prenom')} {emp.get('nom')}")
                        if punch.get('projet'):
                            proj = punch['projet']
                            print(f"   Projet: {proj.get('nom')}")
                else:
                    print("⚠️ Aucun punch trouvé dans la base de données")
            else:
                print(f"❌ Erreur API: {data.get('message', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("✅ Test terminé")
    print("=" * 60)

if __name__ == "__main__":
    test_punchs_api()

