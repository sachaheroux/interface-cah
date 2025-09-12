#!/usr/bin/env python3
"""
Script pour réinitialiser complètement la base de données
Supprime toutes les tables et les recrée
"""

import requests
import json

def reset_database_schema():
    """Réinitialiser complètement la base de données"""
    print("🔄 RÉINITIALISATION COMPLÈTE DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        print("1️⃣ Vérification de l'état actuel...")
        
        # Vérifier l'état actuel
        endpoints = [
            ("buildings", "Immeubles"),
            ("units", "Unités"),
            ("tenants", "Locataires"),
            ("assignments", "Assignations"),
            ("building-reports", "Rapports d'immeubles"),
            ("invoices", "Factures")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{base_url}/{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and 'data' in data:
                        count = len(data['data'])
                    else:
                        count = len(data) if isinstance(data, list) else 0
                    print(f"   📊 {name}: {count} enregistrements")
                else:
                    print(f"   ❌ {name}: Erreur {response.status_code}")
            except Exception as e:
                print(f"   ❌ {name}: Erreur - {e}")
        
        print("\n2️⃣ Tentative de réinitialisation...")
        print("   💡 Envoi d'une requête de réinitialisation...")
        
        # Essayer de réinitialiser via une requête spéciale
        try:
            # Essayer plusieurs endpoints de réinitialisation
            reset_endpoints = [
                "/api/reset-database",
                "/api/init-database",
                "/api/recreate-tables",
                "/api/force-reset"
            ]
            
            for endpoint in reset_endpoints:
                try:
                    print(f"   🔄 Essai {endpoint}...")
                    response = requests.post(f"{base_url}{endpoint}", timeout=10)
                    print(f"      Status: {response.status_code}")
                    if response.status_code in [200, 201]:
                        print(f"      ✅ Réinitialisation réussie avec {endpoint}")
                        break
                except Exception as e:
                    print(f"      ❌ Erreur {endpoint}: {e}")
                    continue
        except Exception as e:
            print(f"   ❌ Erreur réinitialisation: {e}")
        
        print("\n3️⃣ Vérification après réinitialisation...")
        
        # Vérifier l'état après réinitialisation
        all_clean = True
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{base_url}/{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and 'data' in data:
                        count = len(data['data'])
                    else:
                        count = len(data) if isinstance(data, list) else 0
                    
                    if count == 0:
                        print(f"   ✅ {name}: 0 (propre)")
                    else:
                        print(f"   ⚠️ {name}: {count} (données restantes)")
                        all_clean = False
                else:
                    print(f"   ❌ {name}: Erreur {response.status_code}")
                    all_clean = False
            except Exception as e:
                print(f"   ❌ {name}: Erreur - {e}")
                all_clean = False
        
        return all_clean
        
    except Exception as e:
        print(f"❌ Erreur réinitialisation: {e}")
        return False

def create_reset_endpoint():
    """Créer un endpoint de réinitialisation dans l'application"""
    print("\n🔧 CRÉATION D'UN ENDPOINT DE RÉINITIALISATION")
    print("=" * 60)
    print("Pour résoudre le problème, nous devons ajouter un endpoint")
    print("de réinitialisation dans l'application backend.")
    print("\n📝 Ajoutez ce code dans backend/main.py :")
    print("""
@app.post("/api/reset-database")
async def reset_database():
    \"\"\"Réinitialiser complètement la base de données\"\"\"
    try:
        # Supprimer toutes les tables
        db_service.reset_database()
        return {"message": "Base de données réinitialisée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur réinitialisation: {str(e)}")
""")
    print("\n📝 Et ajoutez cette méthode dans backend/database_service.py :")
    print("""
def reset_database(self):
    \"\"\"Réinitialiser complètement la base de données\"\"\"
    session = self.get_session()
    try:
        # Désactiver les contraintes
        session.execute(text("PRAGMA foreign_keys = OFF"))
        
        # Supprimer toutes les tables
        tables = ['invoices', 'unit_reports', 'assignments', 'building_reports', 'units', 'tenants', 'buildings']
        for table in tables:
            try:
                session.execute(text(f"DROP TABLE IF EXISTS {table}"))
            except Exception as e:
                print(f"Erreur suppression table {table}: {e}")
        
        # Recréer les tables
        create_tables()
        
        # Réactiver les contraintes
        session.execute(text("PRAGMA foreign_keys = ON"))
        
        session.commit()
        print("Base de données réinitialisée avec succès")
        
    except Exception as e:
        session.rollback()
        print(f"Erreur réinitialisation: {e}")
        raise
    finally:
        session.close()
""")

def main():
    """Fonction principale"""
    print("🔄 RÉINITIALISATION COMPLÈTE DE LA BASE DE DONNÉES")
    print("=" * 60)
    print("Ce script va tenter de réinitialiser la base de données")
    print("en utilisant des endpoints spéciaux.")
    print("=" * 60)
    
    success = reset_database_schema()
    
    if success:
        print("\n🎉 RÉINITIALISATION RÉUSSIE !")
        print("   La base de données a été complètement réinitialisée.")
        return True
    else:
        print("\n💥 RÉINITIALISATION ÉCHOUÉE !")
        print("   La réinitialisation automatique n'a pas fonctionné.")
        create_reset_endpoint()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
