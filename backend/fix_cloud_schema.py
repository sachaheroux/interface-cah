#!/usr/bin/env python3
"""
Script pour corriger le schéma de la base de données cloud
Ajoute les colonnes manquantes
"""

import requests
import json

def fix_cloud_schema():
    """Corriger le schéma de la base de données cloud"""
    print("🔧 CORRECTION DU SCHÉMA CLOUD")
    print("=" * 50)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        print("1️⃣ Vérification du schéma actuel...")
        
        # Essayer de créer un endpoint de migration
        migration_endpoints = [
            "/api/migrate-schema",
            "/api/fix-schema",
            "/api/update-database",
            "/api/init-database"
        ]
        
        for endpoint in migration_endpoints:
            try:
                print(f"   🔄 Essai {endpoint}...")
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
                print(f"      Status: {response.status_code}")
                if response.status_code in [200, 201]:
                    print(f"      ✅ Migration réussie avec {endpoint}")
                    return True
            except Exception as e:
                print(f"      ❌ Erreur {endpoint}: {e}")
                continue
        
        print("\n2️⃣ Aucun endpoint de migration trouvé")
        print("   💡 Il faut ajouter un endpoint de migration dans l'application")
        
        print("\n📝 CODE À AJOUTER DANS backend/main.py :")
        print("""
@app.post("/api/migrate-schema")
async def migrate_schema():
    \"\"\"Migrer le schéma de la base de données\"\"\"
    try:
        # Ajouter la colonne month à unit_reports
        session = db_service.get_session()
        try:
            # Vérifier si la colonne existe déjà
            result = session.execute(text("PRAGMA table_info(unit_reports)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'month' not in columns:
                print("Ajout de la colonne month à unit_reports...")
                session.execute(text("ALTER TABLE unit_reports ADD COLUMN month INTEGER"))
                session.commit()
                print("✅ Colonne month ajoutée")
            else:
                print("✅ Colonne month existe déjà")
            
            return {"message": "Migration du schéma réussie"}
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur migration: {str(e)}")
""")
        
        return False
        
    except Exception as e:
        print(f"❌ Erreur correction schéma: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔧 CORRECTION DU SCHÉMA CLOUD")
    print("=" * 60)
    print("Ce script va tenter de corriger le schéma de la base cloud.")
    print("=" * 60)
    
    success = fix_cloud_schema()
    
    if success:
        print("\n🎉 SCHÉMA CORRIGÉ !")
        print("   Le schéma de la base cloud a été corrigé.")
        return True
    else:
        print("\n💥 CORRECTION ÉCHOUÉE !")
        print("   Il faut ajouter un endpoint de migration dans l'application.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
