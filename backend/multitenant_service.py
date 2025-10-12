#!/usr/bin/env python3
"""
Service Multi-Tenant pour Interface CAH
Gestion de l'isolation des données par schémas PostgreSQL
"""

import os
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# Import des modèles
from models_francais import Base, Immeuble, Unite, Locataire, Bail, Transaction, PaiementLoyer

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# ==========================================
# GESTION DES SCHÉMAS POSTGRESQL
# ==========================================

class MultiTenantService:
    """
    Service pour gérer l'isolation multi-tenant avec des schémas PostgreSQL séparés
    """
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or DATABASE_URL
        if not self.database_url:
            raise ValueError("DATABASE_URL non configurée")
        
        # Créer l'engine principal
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        
        # Session factory pour le schéma public (authentification)
        self.SessionPublic = sessionmaker(bind=self.engine)
    
    # ==========================================
    # CRÉATION DE SCHÉMAS
    # ==========================================
    
    def create_company_schema(self, schema_name: str) -> bool:
        """
        Créer un nouveau schéma PostgreSQL pour une compagnie
        
        Args:
            schema_name: Nom du schéma (ex: 'company_cah_abc123')
        
        Returns:
            True si succès, False sinon
        """
        try:
            with self.engine.connect() as conn:
                # Créer le schéma
                conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
                conn.commit()
                
                print(f"✅ Schéma '{schema_name}' créé")
                
                # Créer toutes les tables dans ce schéma
                self._create_tables_in_schema(schema_name)
                
                return True
                
        except Exception as e:
            print(f"❌ Erreur création schéma '{schema_name}': {e}")
            return False
    
    def _create_tables_in_schema(self, schema_name: str):
        """
        Créer toutes les tables métier dans un schéma spécifique
        """
        try:
            with self.engine.connect() as conn:
                # Set le search_path pour créer les tables dans le bon schéma
                conn.execute(text(f'SET search_path TO "{schema_name}", public'))
                
                # SQL pour créer les tables
                tables_sql = f"""
                -- Table immeubles
                CREATE TABLE IF NOT EXISTS "{schema_name}".immeubles (
                    id_immeuble SERIAL PRIMARY KEY,
                    nom_immeuble VARCHAR(255) NOT NULL,
                    adresse VARCHAR(255) NOT NULL,
                    ville VARCHAR(100),
                    code_postal VARCHAR(20),
                    province VARCHAR(50),
                    pays VARCHAR(50) DEFAULT 'Canada',
                    prix_achete DECIMAL(15, 2),
                    mise_de_fond DECIMAL(15, 2),
                    valeur_actuel DECIMAL(15, 2),
                    dette_restante DECIMAL(15, 2),
                    annee_construction INTEGER,
                    nombre_unites INTEGER DEFAULT 1,
                    surface_totale DECIMAL(10, 2),
                    type_propriete VARCHAR(100),
                    statut VARCHAR(50) DEFAULT 'actif',
                    notes TEXT,
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    proprietaire VARCHAR(255),
                    banque VARCHAR(255),
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Table unites
                CREATE TABLE IF NOT EXISTS "{schema_name}".unites (
                    id_unite SERIAL PRIMARY KEY,
                    id_immeuble INTEGER NOT NULL REFERENCES "{schema_name}".immeubles(id_immeuble) ON DELETE CASCADE,
                    numero_unite VARCHAR(50),
                    adresse_unite VARCHAR(255),
                    superficie DECIMAL(10, 2),
                    nombre_chambres INTEGER,
                    nombre_salles_bain DECIMAL(3, 1),
                    loyer_mensuel DECIMAL(10, 2),
                    type_unite VARCHAR(100),
                    etage INTEGER,
                    statut VARCHAR(50) DEFAULT 'disponible',
                    description TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Table locataires
                CREATE TABLE IF NOT EXISTS "{schema_name}".locataires (
                    id_locataire SERIAL PRIMARY KEY,
                    id_unite INTEGER NOT NULL REFERENCES "{schema_name}".unites(id_unite) ON DELETE CASCADE,
                    nom VARCHAR(255) NOT NULL,
                    prenom VARCHAR(255),
                    email VARCHAR(255),
                    telephone VARCHAR(50),
                    statut VARCHAR(50) DEFAULT 'actif',
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Table baux
                CREATE TABLE IF NOT EXISTS "{schema_name}".baux (
                    id_bail SERIAL PRIMARY KEY,
                    id_locataire INTEGER NOT NULL REFERENCES "{schema_name}".locataires(id_locataire) ON DELETE CASCADE,
                    date_debut DATE NOT NULL,
                    date_fin DATE,
                    prix_loyer DECIMAL(10, 2) DEFAULT 0,
                    methode_paiement VARCHAR(50),
                    pdf_bail VARCHAR(255),
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Table transactions
                CREATE TABLE IF NOT EXISTS "{schema_name}".transactions (
                    id_transaction SERIAL PRIMARY KEY,
                    id_immeuble INTEGER NOT NULL REFERENCES "{schema_name}".immeubles(id_immeuble) ON DELETE CASCADE,
                    type VARCHAR(50) NOT NULL,
                    categorie VARCHAR(100),
                    montant DECIMAL(10, 2) NOT NULL,
                    date_de_transaction DATE NOT NULL,
                    methode_de_paiement VARCHAR(50),
                    reference VARCHAR(255),
                    source VARCHAR(255),
                    pdf_transaction VARCHAR(255),
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Table paiements_loyers
                CREATE TABLE IF NOT EXISTS "{schema_name}".paiements_loyers (
                    id_paiement SERIAL PRIMARY KEY,
                    id_bail INTEGER NOT NULL REFERENCES "{schema_name}".baux(id_bail) ON DELETE CASCADE,
                    mois INTEGER NOT NULL,
                    annee INTEGER NOT NULL,
                    date_paiement_reelle DATE NOT NULL,
                    montant_paye DECIMAL(10, 2) NOT NULL,
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(id_bail, mois, annee)
                );
                
                -- Index pour performance
                CREATE INDEX IF NOT EXISTS idx_{schema_name}_unites_immeuble ON "{schema_name}".unites(id_immeuble);
                CREATE INDEX IF NOT EXISTS idx_{schema_name}_locataires_unite ON "{schema_name}".locataires(id_unite);
                CREATE INDEX IF NOT EXISTS idx_{schema_name}_baux_locataire ON "{schema_name}".baux(id_locataire);
                CREATE INDEX IF NOT EXISTS idx_{schema_name}_transactions_immeuble ON "{schema_name}".transactions(id_immeuble);
                CREATE INDEX IF NOT EXISTS idx_{schema_name}_paiements_bail ON "{schema_name}".paiements_loyers(id_bail);
                """
                
                # Exécuter toutes les commandes SQL
                for statement in tables_sql.split(';'):
                    if statement.strip():
                        conn.execute(text(statement))
                
                conn.commit()
                print(f"✅ Tables créées dans le schéma '{schema_name}'")
                
        except Exception as e:
            print(f"❌ Erreur création tables dans '{schema_name}': {e}")
            raise
    
    def schema_exists(self, schema_name: str) -> bool:
        """
        Vérifier si un schéma existe
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"
                ), {"schema": schema_name})
                return result.fetchone() is not None
        except Exception as e:
            print(f"❌ Erreur vérification schéma: {e}")
            return False
    
    def delete_company_schema(self, schema_name: str) -> bool:
        """
        Supprimer un schéma complet (ATTENTION: supprime toutes les données!)
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))
                conn.commit()
                print(f"✅ Schéma '{schema_name}' supprimé")
                return True
        except Exception as e:
            print(f"❌ Erreur suppression schéma '{schema_name}': {e}")
            return False
    
    # ==========================================
    # SESSIONS PAR SCHÉMA
    # ==========================================
    
    @contextmanager
    def get_tenant_session(self, schema_name: str):
        """
        Obtenir une session configurée pour un schéma spécifique
        
        Usage:
            with mt_service.get_tenant_session('company_cah_abc123') as session:
                immeubles = session.query(Immeuble).all()
        """
        # Créer une session
        session = self.SessionPublic()
        
        try:
            # Set le search_path pour ce schéma
            session.execute(text(f'SET search_path TO "{schema_name}", public'))
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur session tenant '{schema_name}': {e}")
            raise
        finally:
            session.close()
    
    def get_tenant_session_direct(self, schema_name: str) -> Session:
        """
        Obtenir une session pour un schéma (sans context manager)
        IMPORTANT: Appeler session.close() après utilisation !
        """
        session = self.SessionPublic()
        session.execute(text(f'SET search_path TO "{schema_name}", public'))
        return session
    
    # ==========================================
    # MIGRATION DE DONNÉES
    # ==========================================
    
    def migrate_data_to_schema(self, source_schema: str, target_schema: str, table_name: str) -> bool:
        """
        Migrer les données d'un schéma à un autre pour une table spécifique
        """
        try:
            with self.engine.connect() as conn:
                # Copier toutes les données
                conn.execute(text(f"""
                    INSERT INTO "{target_schema}".{table_name}
                    SELECT * FROM "{source_schema}".{table_name}
                """))
                conn.commit()
                print(f"✅ Données de {table_name} migrées de '{source_schema}' vers '{target_schema}'")
                return True
        except Exception as e:
            print(f"❌ Erreur migration {table_name}: {e}")
            return False


# ==========================================
# INSTANCE GLOBALE
# ==========================================

# Créer une instance globale du service
multitenant_service = MultiTenantService()


if __name__ == "__main__":
    print("🧪 Test du service multi-tenant")
    
    # Test de création de schéma
    test_schema = "company_test_abc123"
    
    print(f"\n1. Vérification si le schéma '{test_schema}' existe...")
    exists = multitenant_service.schema_exists(test_schema)
    print(f"   Existe: {exists}")
    
    if not exists:
        print(f"\n2. Création du schéma '{test_schema}'...")
        success = multitenant_service.create_company_schema(test_schema)
        print(f"   Succès: {success}")
    
    print(f"\n3. Test de session pour le schéma '{test_schema}'...")
    try:
        with multitenant_service.get_tenant_session(test_schema) as session:
            # Test query
            result = session.execute(text("SELECT current_schema()"))
            current = result.fetchone()[0]
            print(f"   ✅ Schéma actif: {current}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n✅ Tests terminés!")

