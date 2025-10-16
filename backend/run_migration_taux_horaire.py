#!/usr/bin/env python3
"""
Script pour exécuter la migration taux_horaire sur Render
"""

import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"

def execute_migration():
    """Exécuter la migration pour ajouter la colonne taux_horaire"""
    print("🔧 Exécution de la migration taux_horaire")
    print("=" * 50)
    
    try:
        print(f"📡 Appel de l'endpoint de migration...")
        print(f"   URL: {RENDER_URL}/api/construction/migrate/add-taux-horaire")
        
        response = requests.post(
            f"{RENDER_URL}/api/construction/migrate/add-taux-horaire",
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Résultat de la migration:")
            print(f"   - success: {data.get('success')}")
            print(f"   - message: {data.get('message')}")
            
            if data.get('success'):
                print("🎉 Migration réussie !")
                return True
            else:
                print("❌ Migration échouée")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Le serveur Render met trop de temps à répondre")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Erreur de connexion - Impossible de joindre le serveur")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_employees_after_migration():
    """Tester l'API des employés après la migration"""
    print("\n👥 Test des employés après migration")
    print("=" * 50)
    
    try:
        print(f"📡 Test de l'API: {RENDER_URL}/api/construction/employes")
        response = requests.get(f"{RENDER_URL}/api/construction/employes", timeout=30)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Structure de la réponse:")
            print(f"   - success: {data.get('success')}")
            print(f"   - data: {type(data.get('data'))}")
            
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
                    return True
                else:
                    print("⚠️ Aucun employé trouvé dans la réponse")
                    return False
            else:
                print(f"❌ API retourne success=False")
                print(f"   Message: {data.get('message', 'Aucun message')}")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Migration taux_horaire - Interface CAH")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Exécuter la migration
    migration_success = execute_migration()
    
    if migration_success:
        print("\n✅ Migration terminée avec succès")
        
        # Tester les employés après migration
        employees_success = test_employees_after_migration()
        
        if employees_success:
            print("\n🎉 PROBLÈME RÉSOLU !")
            print("   Les employés sont maintenant visibles dans l'interface")
        else:
            print("\n⚠️ Migration réussie mais problème persistant")
            print("   Vérifier les logs du backend sur Render")
    else:
        print("\n❌ Migration échouée")
        print("   Vérifier que le backend est déployé avec le nouvel endpoint")
    
    print("\n" + "=" * 50)
    print("🏁 Script terminé")
