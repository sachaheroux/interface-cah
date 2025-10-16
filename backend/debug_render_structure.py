#!/usr/bin/env python3
"""
Script pour vérifier la structure de la base de données sur Render
"""

import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"

def check_database_structure():
    """Vérifier la structure de la base de données sur Render"""
    print("🔍 Vérification de la structure de la base Render")
    print("=" * 60)
    
    try:
        # Créer un endpoint temporaire pour vérifier la structure
        print("📡 Test de l'API construction générale...")
        response = requests.get(f"{RENDER_URL}/api/construction/test", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Construction fonctionnelle: {data.get('success')}")
            print(f"📋 Tables disponibles: {len(data.get('tables', []))}")
            
            for table in data.get('tables', []):
                print(f"  - {table}")
        else:
            print(f"❌ Erreur API construction: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_employees_api_directly():
    """Tester directement l'API des employés"""
    print("\n👥 Test direct de l'API employés")
    print("=" * 60)
    
    try:
        print(f"📡 Test: {RENDER_URL}/api/construction/employes")
        response = requests.get(f"{RENDER_URL}/api/construction/employes", timeout=30)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Réponse complète:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                employees = data.get('data', [])
                print(f"\n👥 Nombre d'employés: {len(employees)}")
                
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
                    print("⚠️ Aucun employé dans la réponse")
            else:
                print(f"❌ API retourne success=False")
                print(f"   Message: {data.get('message', 'Aucun message')}")
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def create_debug_endpoint():
    """Créer le code pour un endpoint de debug"""
    print("\n📝 Code pour endpoint de debug")
    print("=" * 60)
    
    debug_code = '''
# Ajouter ceci dans backend/main.py dans la section CONSTRUCTION_ENABLED

@app.get("/api/construction/debug/employes-structure")
async def debug_employes_structure(db: Session = Depends(get_construction_db)):
    """Debug : Vérifier la structure de la table employes"""
    try:
        from sqlalchemy import text
        
        # Vérifier la structure de la table
        result = db.execute(text("PRAGMA table_info(employes)"))
        columns = result.fetchall()
        
        # Compter les employés
        count_result = db.execute(text("SELECT COUNT(*) FROM employes"))
        count = count_result.fetchone()[0]
        
        # Récupérer quelques employés
        employees_result = db.execute(text("SELECT * FROM employes LIMIT 5"))
        employees = employees_result.fetchall()
        
        return {
            "success": True,
            "structure": [{"name": col[1], "type": col[2], "not_null": col[3]} for col in columns],
            "count": count,
            "sample_data": [dict(zip([col[1] for col in columns], emp)) for emp in employees]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
'''
    
    print("📋 Code à ajouter dans main.py :")
    print(debug_code)

def suggest_solutions():
    """Suggérer des solutions"""
    print("\n💡 Solutions recommandées")
    print("=" * 60)
    
    print("🎯 Solution 1 - Debug avec endpoint :")
    print("   1. Ajouter l'endpoint de debug dans main.py")
    print("   2. Déployer sur Render")
    print("   3. Appeler l'endpoint pour voir la structure")
    print("   4. Identifier le problème exact")
    print()
    
    print("🎯 Solution 2 - Reset complet de la base construction :")
    print("   1. Supprimer construction_projects.db sur Render")
    print("   2. Redéployer le backend")
    print("   3. Recréer les employés avec le nouveau formulaire")
    print("   4. Tester l'API")
    print()
    
    print("🎯 Solution 3 - Migration manuelle :")
    print("   1. Créer un endpoint pour ajouter manuellement les employés")
    print("   2. Utiliser les données du téléchargement local")
    print("   3. Insérer les employés avec la bonne structure")

if __name__ == "__main__":
    print("🚀 Debug structure base Render - Interface CAH")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_database_structure()
    test_employees_api_directly()
    create_debug_endpoint()
    suggest_solutions()
    
    print("\n" + "=" * 60)
    print("🏁 Analyse terminée")
    print()
    print("🔍 Problème probable :")
    print("   La colonne 'taux_horaire' n'existe pas dans la base Render")
    print("   L'API essaie de la récupérer et échoue silencieusement")
    print()
    print("✅ Solution recommandée :")
    print("   Ajouter l'endpoint de debug pour confirmer le problème")
