#!/usr/bin/env python3
"""
Migration: Ajouter la colonne code_acces à la table compagnies
"""

from sqlalchemy import text
from auth_database_service import engine, SessionLocal
from models_auth import Compagnie
import auth_service

def migrate_add_code_acces():
    print("\n" + "="*60)
    print("🔧 MIGRATION: Ajout colonne code_acces")
    print("="*60)
    
    with engine.connect() as conn:
        try:
            # Vérifier si la colonne existe déjà
            result = conn.execute(text("PRAGMA table_info(compagnies)"))
            columns = [row[1] for row in result]
            
            if 'code_acces' in columns:
                print("ℹ️ La colonne code_acces existe déjà")
            else:
                # Ajouter la colonne
                print("📝 Ajout de la colonne code_acces...")
                conn.execute(text("ALTER TABLE compagnies ADD COLUMN code_acces VARCHAR(20)"))
                conn.commit()
                print("✅ Colonne code_acces ajoutée")
            
            # Générer un code pour CAH Immobilier si elle n'en a pas
            db = SessionLocal()
            try:
                company = db.query(Compagnie).filter_by(nom_compagnie="CAH Immobilier").first()
                if company:
                    if not company.code_acces:
                        code_acces = auth_service.generate_company_access_code()
                        company.code_acces = code_acces
                        db.commit()
                        print(f"✅ Code d'accès généré pour CAH Immobilier: {code_acces}")
                    else:
                        print(f"ℹ️ Code d'accès existant: {company.code_acces}")
                else:
                    print("⚠️ Compagnie 'CAH Immobilier' non trouvée")
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            conn.rollback()
    
    print("="*60 + "\n")

if __name__ == "__main__":
    migrate_add_code_acces()

