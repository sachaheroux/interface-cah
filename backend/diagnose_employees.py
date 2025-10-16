#!/usr/bin/env python3
"""
Script pour diagnostiquer le problème des employés qui ne s'affichent plus
"""

import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"

def test_employees_api():
    """Tester l'API des employés"""
    print("🔍 Diagnostic des employés")
    print("=" * 50)
    
    try:
        print(f"📡 Test de l'API: {RENDER_URL}/api/construction/employes")
        response = requests.get(f"{RENDER_URL}/api/construction/employes", timeout=30)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Structure de la réponse:")
            print(f"  - success: {data.get('success')}")
            print(f"  - data: {type(data.get('data'))}")
            
            if data.get('success'):
                employees = data.get('data', [])
                print(f"👥 Nombre d'employés: {len(employees)}")
                
                if employees:
                    print("\n📋 Détails des employés:")
                    for i, emp in enumerate(employees, 1):
                        print(f"  {i}. {emp.get('prenom', 'N/A')} {emp.get('nom', 'N/A')}")
                        print(f"     - ID: {emp.get('id_employe')}")
                        print(f"     - Poste: {emp.get('poste', 'N/A')}")
                        print(f"     - Taux horaire: ${emp.get('taux_horaire', 'N/A')}")
                        print(f"     - Email: {emp.get('adresse_courriel', 'N/A')}")
                        print()
                else:
                    print("⚠️ Aucun employé trouvé dans la réponse")
            else:
                print(f"❌ API retourne success=False")
                print(f"   Message: {data.get('message', 'Aucun message')}")
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Le serveur Render met trop de temps à répondre")
    except requests.exceptions.ConnectionError:
        print("🔌 Erreur de connexion - Impossible de joindre le serveur")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

def test_construction_api():
    """Tester l'API de construction générale"""
    print("\n🏗️ Test de l'API Construction générale")
    print("=" * 50)
    
    try:
        response = requests.get(f"{RENDER_URL}/api/construction/test", timeout=30)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 API Construction fonctionnelle: {data.get('success')}")
            print(f"📋 Tables disponibles: {len(data.get('tables', []))}")
            for table in data.get('tables', []):
                print(f"  - {table}")
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_database_direct():
    """Tester directement la base de données (si possible)"""
    print("\n🗄️ Test direct de la base de données")
    print("=" * 50)
    
    try:
        # Essayer de télécharger la base pour vérifier
        print("📥 Tentative de téléchargement de la base...")
        
        # Test avec le script de téléchargement
        import subprocess
        import sys
        import os
        
        script_path = os.path.join(os.path.dirname(__file__), 'download_construction_db.py')
        if os.path.exists(script_path):
            print("✅ Script de téléchargement trouvé")
            print("🔄 Exécution du script...")
            
            result = subprocess.run([sys.executable, script_path], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Script exécuté avec succès")
                # Chercher les informations sur les employés dans la sortie
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'employes:' in line and 'éléments' in line:
                        print(f"📊 {line.strip()}")
                    elif 'Exemples d\'employés:' in line:
                        print(f"👥 {line.strip()}")
                    elif line.strip().startswith('- ') and ('Héroux' in line or 'Baribeau' in line):
                        print(f"   {line.strip()}")
            else:
                print(f"❌ Erreur lors de l'exécution du script")
                print(f"   Code de retour: {result.returncode}")
                print(f"   Erreur: {result.stderr}")
        else:
            print("⚠️ Script de téléchargement non trouvé")
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout lors de l'exécution du script")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def check_frontend_api_call():
    """Vérifier comment le frontend appelle l'API"""
    print("\n🌐 Vérification de l'appel API frontend")
    print("=" * 50)
    
    print("📋 Le frontend devrait appeler:")
    print("   GET https://interface-cah-backend.onrender.com/api/construction/employes")
    print()
    print("📋 Structure attendue de la réponse:")
    print("   {")
    print('     "success": true,')
    print('     "data": [')
    print('       {')
    print('         "id_employe": 1,')
    print('         "prenom": "Sacha",')
    print('         "nom": "Héroux",')
    print('         "poste": "Charpentier",')
    print('         "taux_horaire": 35.0,')
    print('         ...')
    print('       }')
    print('     ]')
    print("   }")
    print()
    print("🔍 Vérifications à faire côté frontend:")
    print("   1. Ouvrir les DevTools (F12)")
    print("   2. Aller dans l'onglet Network")
    print("   3. Rafraîchir la page Employees")
    print("   4. Chercher la requête vers /api/construction/employes")
    print("   5. Vérifier la réponse reçue")

if __name__ == "__main__":
    print("🚀 Diagnostic des employés - Interface CAH")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_employees_api()
    test_construction_api()
    test_database_direct()
    check_frontend_api_call()
    
    print("\n" + "=" * 50)
    print("🏁 Diagnostic terminé")
    print()
    print("💡 Solutions possibles:")
    print("   1. Vérifier que le backend Render est bien démarré")
    print("   2. Vérifier les logs du backend sur Render")
    print("   3. Vérifier la console du navigateur pour les erreurs")
    print("   4. Tester l'API directement avec Postman/curl")
    print("   5. Redéployer le backend si nécessaire")
