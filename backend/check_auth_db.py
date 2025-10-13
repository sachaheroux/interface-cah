#!/usr/bin/env python3
"""
Script pour vérifier le contenu de la base de données d'authentification
"""

from auth_database_service import SessionLocal
from models_auth import Compagnie, Utilisateur, DemandeAcces

def check_auth_database():
    db = SessionLocal()
    try:
        print("\n" + "="*60)
        print("📊 VÉRIFICATION BASE DE DONNÉES D'AUTHENTIFICATION")
        print("="*60)
        
        # Vérifier les compagnies
        print("\n🏢 COMPAGNIES:")
        companies = db.query(Compagnie).all()
        for company in companies:
            print(f"  - ID: {company.id_compagnie}")
            print(f"    Nom: {company.nom_compagnie}")
            print(f"    Email: {company.email_compagnie}")
            print(f"    Schema/DB: {company.schema_name}")
            print(f"    Date création: {company.date_creation}")
            print()
        
        # Vérifier les utilisateurs
        print("👤 UTILISATEURS:")
        users = db.query(Utilisateur).all()
        for user in users:
            print(f"  - ID: {user.id_utilisateur}")
            print(f"    Nom: {user.prenom} {user.nom}")
            print(f"    Email: {user.email}")
            print(f"    Rôle: {user.role}")
            print(f"    Email vérifié: {user.email_verifie}")
            print(f"    Compagnie ID: {user.id_compagnie}")
            print()
        
        # Vérifier les demandes d'accès
        print("📨 DEMANDES D'ACCÈS:")
        requests = db.query(DemandeAcces).all()
        if requests:
            for req in requests:
                print(f"  - ID: {req.id_demande}")
                print(f"    Email: {req.email}")
                print(f"    Statut: {req.statut}")
                print()
        else:
            print("  Aucune demande d'accès")
        
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_auth_database()

