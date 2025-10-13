#!/usr/bin/env python3
"""
Script pour ajouter un code d'accès à CAH Immobilier
"""

from auth_database_service import SessionLocal
from models_auth import Compagnie
import auth_service

def add_code_acces():
    db = SessionLocal()
    try:
        # Trouver CAH Immobilier
        company = db.query(Compagnie).filter_by(nom_compagnie="CAH Immobilier").first()
        
        if company:
            if company.code_acces:
                print(f"✅ Code d'accès existant: {company.code_acces}")
            else:
                # Générer un nouveau code
                code_acces = auth_service.generate_company_access_code()
                company.code_acces = code_acces
                db.commit()
                print(f"✅ Code d'accès généré: {code_acces}")
        else:
            print("❌ Compagnie 'CAH Immobilier' non trouvée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_code_acces()

