#!/usr/bin/env python3
"""
Script de configuration initiale du système d'authentification
1. Crée les tables d'authentification (schéma public)
2. Crée la compagnie de Sacha
3. Crée l'utilisateur admin principal Sacha
4. Crée le schéma pour la compagnie de Sacha
5. Migre les données actuelles vers ce schéma
"""

import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime, date

# Services
import auth_service
from multitenant_service import multitenant_service
from models_auth import Base, Compagnie, Utilisateur

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL non configurée")
    sys.exit(1)

# ==========================================
# ÉTAPE 1: CRÉER LES TABLES D'AUTHENTIFICATION
# ==========================================

def create_auth_tables():
    """
    Créer les tables compagnies, utilisateurs, demandes_acces dans le schéma public
    """
    print("\n" + "="*60)
    print("ÉTAPE 1: Création des tables d'authentification")
    print("="*60)
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # SQL pour créer les tables
            sql = """
            -- Table compagnies
            CREATE TABLE IF NOT EXISTS compagnies (
                id_compagnie SERIAL PRIMARY KEY,
                nom_compagnie VARCHAR(255) NOT NULL UNIQUE,
                email_compagnie VARCHAR(255) NOT NULL,
                telephone_compagnie VARCHAR(50),
                adresse_compagnie TEXT,
                logo_compagnie VARCHAR(500),
                site_web VARCHAR(255),
                numero_entreprise VARCHAR(100),
                schema_name VARCHAR(100) NOT NULL UNIQUE,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Table utilisateurs
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id_utilisateur SERIAL PRIMARY KEY,
                id_compagnie INTEGER NOT NULL REFERENCES compagnies(id_compagnie) ON DELETE CASCADE,
                email VARCHAR(255) NOT NULL UNIQUE,
                mot_de_passe_hash VARCHAR(255) NOT NULL,
                nom VARCHAR(255) NOT NULL,
                prenom VARCHAR(255) NOT NULL,
                date_naissance DATE,
                age INTEGER,
                sexe VARCHAR(50),
                telephone VARCHAR(50),
                poste VARCHAR(255),
                role VARCHAR(50) NOT NULL DEFAULT 'employe',
                est_admin_principal BOOLEAN DEFAULT FALSE,
                statut VARCHAR(50) NOT NULL DEFAULT 'en_attente',
                email_verifie BOOLEAN DEFAULT FALSE,
                code_verification_email VARCHAR(10),
                code_verification_expiration TIMESTAMP,
                code_reset_mdp VARCHAR(10),
                code_reset_mdp_expiration TIMESTAMP,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                derniere_connexion TIMESTAMP
            );
            
            -- Table demandes_acces
            CREATE TABLE IF NOT EXISTS demandes_acces (
                id_demande SERIAL PRIMARY KEY,
                id_compagnie INTEGER NOT NULL REFERENCES compagnies(id_compagnie) ON DELETE CASCADE,
                id_utilisateur INTEGER NOT NULL REFERENCES utilisateurs(id_utilisateur) ON DELETE CASCADE,
                statut VARCHAR(50) NOT NULL DEFAULT 'en_attente',
                traite_par INTEGER REFERENCES utilisateurs(id_utilisateur),
                date_traitement TIMESTAMP,
                commentaire_refus TEXT,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Index
            CREATE INDEX IF NOT EXISTS idx_utilisateurs_compagnie ON utilisateurs(id_compagnie);
            CREATE INDEX IF NOT EXISTS idx_utilisateurs_email ON utilisateurs(email);
            CREATE INDEX IF NOT EXISTS idx_demandes_compagnie ON demandes_acces(id_compagnie);
            CREATE INDEX IF NOT EXISTS idx_demandes_statut ON demandes_acces(statut);
            """
            
            # Exécuter les commandes
            for statement in sql.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
            
            conn.commit()
            print("✅ Tables d'authentification créées avec succès")
            return True
            
    except Exception as e:
        print(f"❌ Erreur création tables: {e}")
        return False

# ==========================================
# ÉTAPE 2: CRÉER LA COMPAGNIE DE SACHA
# ==========================================

def create_sacha_company():
    """
    Créer la compagnie pour Sacha
    """
    print("\n" + "="*60)
    print("ÉTAPE 2: Création de la compagnie de Sacha")
    print("="*60)
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Vérifier si la compagnie existe déjà
            result = conn.execute(text(
                "SELECT id_compagnie, schema_name FROM compagnies WHERE email_compagnie = :email"
            ), {"email": "sacha.heroux87@gmail.com"})
            
            existing = result.fetchone()
            
            if existing:
                print(f"ℹ️  Compagnie existe déjà (ID: {existing[0]}, Schéma: {existing[1]})")
                return existing[0], existing[1]
            
            # Générer le schema name
            schema_name = auth_service.sanitize_schema_name("CAH Immobilier")
            
            # Insérer la compagnie
            result = conn.execute(text("""
                INSERT INTO compagnies (
                    nom_compagnie, email_compagnie, telephone_compagnie,
                    adresse_compagnie, schema_name
                ) VALUES (
                    :nom, :email, :tel, :adresse, :schema
                ) RETURNING id_compagnie
            """), {
                "nom": "CAH Immobilier",
                "email": "sacha.heroux87@gmail.com",
                "tel": "514-XXX-XXXX",
                "adresse": "Québec, Canada",
                "schema": schema_name
            })
            
            company_id = result.fetchone()[0]
            conn.commit()
            
            print(f"✅ Compagnie créée:")
            print(f"   ID: {company_id}")
            print(f"   Nom: CAH Immobilier")
            print(f"   Schéma: {schema_name}")
            
            return company_id, schema_name
            
    except Exception as e:
        print(f"❌ Erreur création compagnie: {e}")
        return None, None

# ==========================================
# ÉTAPE 3: CRÉER L'UTILISATEUR SACHA
# ==========================================

def create_sacha_user(company_id: int):
    """
    Créer l'utilisateur admin principal Sacha
    """
    print("\n" + "="*60)
    print("ÉTAPE 3: Création de l'utilisateur Sacha")
    print("="*60)
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Vérifier si l'utilisateur existe déjà
            result = conn.execute(text(
                "SELECT id_utilisateur FROM utilisateurs WHERE email = :email"
            ), {"email": "sacha.heroux87@gmail.com"})
            
            existing = result.fetchone()
            
            if existing:
                print(f"ℹ️  Utilisateur Sacha existe déjà (ID: {existing[0]})")
                return existing[0]
            
            # Hasher le mot de passe
            password_hash = auth_service.hash_password("Champion2024!")
            
            # Insérer l'utilisateur
            result = conn.execute(text("""
                INSERT INTO utilisateurs (
                    id_compagnie, email, mot_de_passe_hash,
                    nom, prenom, role, est_admin_principal,
                    statut, email_verifie
                ) VALUES (
                    :company_id, :email, :password,
                    :nom, :prenom, :role, :is_admin,
                    :statut, :email_verified
                ) RETURNING id_utilisateur
            """), {
                "company_id": company_id,
                "email": "sacha.heroux87@gmail.com",
                "password": password_hash,
                "nom": "Héroux",
                "prenom": "Sacha",
                "role": "admin",
                "is_admin": True,
                "statut": "actif",
                "email_verified": True
            })
            
            user_id = result.fetchone()[0]
            conn.commit()
            
            print(f"✅ Utilisateur créé:")
            print(f"   ID: {user_id}")
            print(f"   Email: sacha.heroux87@gmail.com")
            print(f"   Rôle: Admin Principal")
            print(f"   Mot de passe: Champion2024!")
            
            return user_id
            
    except Exception as e:
        print(f"❌ Erreur création utilisateur: {e}")
        return None

# ==========================================
# ÉTAPE 4: CRÉER LE SCHÉMA ET MIGRER LES DONNÉES
# ==========================================

def setup_company_schema_and_migrate(schema_name: str):
    """
    Créer le schéma pour la compagnie et migrer les données actuelles
    """
    print("\n" + "="*60)
    print("ÉTAPE 4: Création du schéma et migration des données")
    print("="*60)
    
    try:
        # 1. Vérifier si le schéma existe
        if multitenant_service.schema_exists(schema_name):
            print(f"ℹ️  Schéma '{schema_name}' existe déjà")
            return True
        
        # 2. Créer le schéma
        print(f"\n📦 Création du schéma '{schema_name}'...")
        success = multitenant_service.create_company_schema(schema_name)
        if not success:
            return False
        
        # 3. Migrer les données du schéma public vers le nouveau schéma
        print(f"\n📦 Migration des données vers '{schema_name}'...")
        
        tables = [
            "immeubles",
            "unites",
            "locataires",
            "baux",
            "transactions",
            "paiements_loyers"
        ]
        
        for table in tables:
            try:
                print(f"   Copie de {table}...")
                multitenant_service.migrate_data_to_schema("public", schema_name, table)
            except Exception as e:
                # Si la table n'existe pas dans public, c'est OK
                print(f"   ⚠️  {table}: {e}")
        
        print("\n✅ Schéma créé et données migrées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur setup schéma: {e}")
        return False

# ==========================================
# SCRIPT PRINCIPAL
# ==========================================

def main():
    """
    Exécuter toutes les étapes de configuration
    """
    print("\n" + "="*70)
    print("🔐 CONFIGURATION DU SYSTÈME D'AUTHENTIFICATION MULTI-TENANT")
    print("="*70)
    
    # Étape 1: Créer les tables d'auth
    if not create_auth_tables():
        print("\n❌ Échec à l'étape 1")
        return False
    
    # Étape 2: Créer la compagnie
    company_id, schema_name = create_sacha_company()
    if not company_id:
        print("\n❌ Échec à l'étape 2")
        return False
    
    # Étape 3: Créer l'utilisateur
    user_id = create_sacha_user(company_id)
    if not user_id:
        print("\n❌ Échec à l'étape 3")
        return False
    
    # Étape 4: Setup schéma et migration
    if not setup_company_schema_and_migrate(schema_name):
        print("\n❌ Échec à l'étape 4")
        return False
    
    # Résumé
    print("\n" + "="*70)
    print("✅ CONFIGURATION TERMINÉE AVEC SUCCÈS !")
    print("="*70)
    print(f"\n📊 Résumé:")
    print(f"   • Compagnie ID: {company_id}")
    print(f"   • Schéma: {schema_name}")
    print(f"   • Utilisateur ID: {user_id}")
    print(f"   • Email: sacha.heroux87@gmail.com")
    print(f"   • Mot de passe: Champion2024!")
    print(f"\n🎉 Tu peux maintenant te connecter au système !")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

