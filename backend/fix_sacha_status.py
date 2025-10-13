#!/usr/bin/env python3
"""
Script pour corriger le statut de l'utilisateur Sacha
"""

from auth_database_service import SessionLocal
from models_auth import Utilisateur

def fix_sacha_status():
    db = SessionLocal()
    try:
        # Trouver Sacha
        sacha = db.query(Utilisateur).filter_by(email="sacha.heroux87@gmail.com").first()
        
        if sacha:
            print(f"📝 Utilisateur trouvé: {sacha.prenom} {sacha.nom}")
            print(f"   Statut actuel: {sacha.statut}")
            print(f"   Role actuel: {sacha.role}")
            print(f"   Admin principal: {sacha.est_admin_principal}")
            
            # Mettre à jour
            sacha.statut = "actif"
            sacha.est_admin_principal = True
            
            db.commit()
            
            print(f"\n✅ Statut mis à jour:")
            print(f"   Nouveau statut: {sacha.statut}")
            print(f"   Admin principal: {sacha.est_admin_principal}")
        else:
            print("❌ Utilisateur Sacha non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_sacha_status()

