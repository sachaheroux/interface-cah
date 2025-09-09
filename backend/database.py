#!/usr/bin/env python3
"""
Configuration de la base de données SQLite pour Interface CAH
"""

import os
import sqlite3
from datetime import datetime
from typing import Optional
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuration du chemin de la base de données
if os.environ.get("ENVIRONMENT") == "development" or os.name == 'nt':
    # En local (Windows) ou développement
    DATA_DIR = os.environ.get("DATA_DIR", "./data")
else:
    # Sur Render ou production Linux
    DATA_DIR = os.environ.get("DATA_DIR", "/opt/render/project/src/data")

# Créer le répertoire s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# Chemin de la base de données SQLite
DATABASE_PATH = os.path.join(DATA_DIR, "cah_database.db")

print(f"🗄️ Base de données SQLite : {DATABASE_PATH}")

# Créer le moteur SQLAlchemy
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    echo=False,  # Mettre à True pour voir les requêtes SQL
    pool_pre_ping=True,
    connect_args={
        "check_same_thread": False,
        "timeout": 30.0
    }
)

# Créer la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseManager:
    """Gestionnaire de base de données SQLite"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.connection = None
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def connect(self):
        """Établir une connexion à la base de données"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,  # Permet l'utilisation multi-thread
                timeout=30.0  # Timeout de 30 secondes
            )
            # Activer les contraintes de clés étrangères
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Optimiser les performances
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.connection.execute("PRAGMA synchronous = NORMAL")
            self.connection.execute("PRAGMA cache_size = 1000")
            self.connection.execute("PRAGMA temp_store = MEMORY")
            
            print(f"✅ Connexion à la base de données établie : {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion à la base de données : {e}")
            return False
    
    def disconnect(self):
        """Fermer la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("🔌 Connexion à la base de données fermée")
    
    def create_tables(self):
        """Créer toutes les tables de la base de données"""
        if not self.connection:
            print("❌ Pas de connexion à la base de données")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Table des immeubles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS buildings (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    address_street TEXT,
                    address_city TEXT,
                    address_province TEXT,
                    address_postal_code TEXT,
                    address_country TEXT DEFAULT 'Canada',
                    type TEXT NOT NULL,
                    units INTEGER NOT NULL DEFAULT 0,
                    floors INTEGER NOT NULL DEFAULT 1,
                    year_built INTEGER,
                    total_area INTEGER,
                    characteristics TEXT,  -- JSON string
                    financials TEXT,      -- JSON string
                    contacts TEXT,        -- JSON string
                    unit_data TEXT,       -- JSON string
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_default BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Table des locataires
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tenants (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    emergency_contact_name TEXT,
                    emergency_contact_phone TEXT,
                    emergency_contact_relationship TEXT,
                    move_in_date DATE,
                    move_out_date DATE,
                    financial_info TEXT,  -- JSON string
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des assignations locataire-unité
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY,
                    tenant_id INTEGER NOT NULL,
                    building_id INTEGER NOT NULL,
                    unit_id TEXT NOT NULL,
                    unit_number TEXT,
                    unit_address TEXT,
                    move_in_date DATE NOT NULL,
                    move_out_date DATE,
                    rent_amount DECIMAL(10,2),
                    deposit_amount DECIMAL(10,2),
                    lease_start_date DATE,
                    lease_end_date DATE,
                    rent_due_day INTEGER DEFAULT 1,
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
                    FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE
                )
            """)
            
            # Table des rapports d'immeubles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS building_reports (
                    id INTEGER PRIMARY KEY,
                    building_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    municipal_taxes DECIMAL(10,2) DEFAULT 0,
                    school_taxes DECIMAL(10,2) DEFAULT 0,
                    insurance DECIMAL(10,2) DEFAULT 0,
                    snow_removal DECIMAL(10,2) DEFAULT 0,
                    lawn_care DECIMAL(10,2) DEFAULT 0,
                    management DECIMAL(10,2) DEFAULT 0,
                    renovations DECIMAL(10,2) DEFAULT 0,
                    repairs DECIMAL(10,2) DEFAULT 0,
                    wifi DECIMAL(10,2) DEFAULT 0,
                    electricity DECIMAL(10,2) DEFAULT 0,
                    other DECIMAL(10,2) DEFAULT 0,
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE,
                    UNIQUE(building_id, year)
                )
            """)
            
            # Table des rapports d'unités
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unit_reports (
                    id INTEGER PRIMARY KEY,
                    building_id INTEGER NOT NULL,
                    unit_id TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    rent_collected DECIMAL(10,2) DEFAULT 0,
                    expenses DECIMAL(10,2) DEFAULT 0,
                    maintenance DECIMAL(10,2) DEFAULT 0,
                    utilities DECIMAL(10,2) DEFAULT 0,
                    other_income DECIMAL(10,2) DEFAULT 0,
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE,
                    UNIQUE(building_id, unit_id, year)
                )
            """)
            
            # Table des factures
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY,
                    invoice_number TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    source TEXT NOT NULL,
                    date DATE NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    currency TEXT DEFAULT 'CAD',
                    payment_type TEXT NOT NULL,
                    building_id INTEGER,
                    unit_id TEXT,
                    pdf_filename TEXT,
                    pdf_path TEXT,
                    notes TEXT DEFAULT '',
                    type TEXT DEFAULT 'rental',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE SET NULL
                )
            """)
            
            # Créer les index pour améliorer les performances
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_buildings_name ON buildings(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tenants_name ON tenants(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tenants_email ON tenants(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_tenant ON assignments(tenant_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_building ON assignments(building_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_unit ON assignments(unit_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_building ON invoices(building_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_category ON invoices(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(date)")
            
            self.connection.commit()
            print("✅ Toutes les tables créées avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables : {e}")
            self.connection.rollback()
            return False
    
    def get_connection(self):
        """Obtenir la connexion actuelle"""
        if not self.connection:
            self.connect()
        return self.connection
    
    def execute_query(self, query: str, params: tuple = ()):
        """Exécuter une requête SQL"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de la requête : {e}")
            self.connection.rollback()
            return None
    
    def backup_database(self, backup_path: Optional[str] = None):
        """Créer une sauvegarde de la base de données"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(DATA_DIR, "backups", f"cah_backup_{timestamp}.db")
        
        # Créer le répertoire de sauvegarde
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        try:
            # Fermer la connexion actuelle
            if self.connection:
                self.connection.close()
            
            # Copier le fichier de base de données
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            # Rétablir la connexion
            self.connect()
            
            print(f"✅ Sauvegarde créée : {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")
            return None

# Instance globale du gestionnaire de base de données
db_manager = DatabaseManager()

def get_database():
    """Obtenir l'instance de la base de données"""
    return db_manager

def init_database():
    """Initialiser la base de données (créer les tables)"""
    if db_manager.connect():
        success = db_manager.create_tables()
        db_manager.disconnect()
        return success
    return False

if __name__ == "__main__":
    print("🚀 Initialisation de la base de données SQLite...")
    if init_database():
        print("✅ Base de données initialisée avec succès !")
    else:
        print("❌ Erreur lors de l'initialisation de la base de données")
