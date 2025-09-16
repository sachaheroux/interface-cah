#!/usr/bin/env python3
"""
Script pour exporter directement le fichier de base de données SQLite depuis Render
Crée un fichier .db local que vous pouvez ouvrir avec DB Browser
"""

import os
import requests
import sqlite3
from datetime import datetime
from pathlib import Path

# Configuration
RENDER_API_URL = "https://interface-cah-backend.onrender.com"
LOCAL_DATA_DIR = Path("data")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOCAL_DB_PATH = LOCAL_DATA_DIR / f"cah_database_cloud_{TIMESTAMP}.db"

def create_data_directory():
    """Créer le répertoire data s'il n'existe pas"""
    LOCAL_DATA_DIR.mkdir(exist_ok=True)
    print(f"📁 Répertoire de données: {LOCAL_DATA_DIR.absolute()}")

def create_local_database():
    """Créer une base de données SQLite locale avec le schéma français"""
    try:
        print("🗄️ Création de la base de données locale...")
        
        # Créer la base de données
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        # Créer les tables avec le schéma français
        create_tables_sql = """
        -- Table immeubles
        CREATE TABLE IF NOT EXISTS immeubles (
            id_immeuble INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_immeuble TEXT NOT NULL,
            adresse TEXT NOT NULL,
            ville TEXT NOT NULL,
            province TEXT NOT NULL,
            code_postal TEXT NOT NULL,
            pays TEXT DEFAULT 'Canada',
            nbr_unite INTEGER DEFAULT 1,
            annee_construction INTEGER,
            prix_achete REAL DEFAULT 0,
            mise_de_fond REAL DEFAULT 0,
            taux_interet REAL DEFAULT 0,
            valeur_actuel REAL DEFAULT 0,
            proprietaire TEXT DEFAULT '',
            banque TEXT DEFAULT '',
            contracteur TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Table unites
        CREATE TABLE IF NOT EXISTS unites (
            id_unite INTEGER PRIMARY KEY AUTOINCREMENT,
            id_immeuble INTEGER NOT NULL,
            adresse_unite TEXT NOT NULL,
            type TEXT DEFAULT '4 1/2',
            nbr_chambre INTEGER DEFAULT 1,
            nbr_salle_de_bain INTEGER DEFAULT 1,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_immeuble) REFERENCES immeubles (id_immeuble)
        );

        -- Table locataires
        CREATE TABLE IF NOT EXISTS locataires (
            id_locataire INTEGER PRIMARY KEY AUTOINCREMENT,
            id_unite INTEGER NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT DEFAULT '',
            telephone TEXT DEFAULT '',
            statut TEXT DEFAULT 'actif',
            notes TEXT DEFAULT '',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_unite) REFERENCES unites (id_unite)
        );

        -- Table factures
        CREATE TABLE IF NOT EXISTS factures (
            id_facture INTEGER PRIMARY KEY AUTOINCREMENT,
            id_immeuble INTEGER NOT NULL,
            categorie TEXT NOT NULL,
            montant REAL NOT NULL,
            date DATE NOT NULL,
            no_facture TEXT DEFAULT '',
            source TEXT DEFAULT '',
            pdf_facture TEXT DEFAULT '',
            type_paiement TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_immeuble) REFERENCES immeubles (id_immeuble)
        );

        -- Table baux
        CREATE TABLE IF NOT EXISTS baux (
            id_bail INTEGER PRIMARY KEY AUTOINCREMENT,
            id_locataire INTEGER NOT NULL,
            date_debut DATE NOT NULL,
            date_fin DATE NOT NULL,
            prix_loyer REAL NOT NULL,
            methode_paiement TEXT DEFAULT '',
            pdf_bail TEXT DEFAULT '',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_locataire) REFERENCES locataires (id_locataire)
        );

        -- Table rapports_immeuble
        CREATE TABLE IF NOT EXISTS rapports_immeuble (
            id_rapport INTEGER PRIMARY KEY AUTOINCREMENT,
            id_immeuble INTEGER NOT NULL,
            annee INTEGER NOT NULL,
            mois INTEGER NOT NULL,
            revenus_totaux REAL DEFAULT 0,
            depenses_totales REAL DEFAULT 0,
            marge_nette REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_immeuble) REFERENCES immeubles (id_immeuble)
        );
        """
        
        cursor.executescript(create_tables_sql)
        conn.commit()
        print("✅ Tables créées avec succès")
        
        return conn, cursor
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la base: {e}")
        return None, None

def export_data_from_api(conn, cursor):
    """Exporter toutes les données depuis l'API Render"""
    try:
        print("📊 Export des données depuis l'API...")
        
        # Export des immeubles
        buildings = get_data_from_api("/api/buildings")
        if buildings:
            export_buildings(cursor, buildings)
            print(f"✅ {len(buildings)} immeubles exportés")
        
        # Export des unités
        units = get_data_from_api("/api/units")
        if units:
            export_units(cursor, units)
            print(f"✅ {len(units)} unités exportées")
        
        # Export des locataires
        tenants = get_data_from_api("/api/tenants")
        if tenants:
            export_tenants(cursor, tenants)
            print(f"✅ {len(tenants)} locataires exportés")
        
        # Export des factures
        invoices = get_data_from_api("/api/invoices")
        if invoices:
            export_invoices(cursor, invoices)
            print(f"✅ {len(invoices)} factures exportées")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_data_from_api(endpoint):
    """Récupérer les données depuis un endpoint de l'API"""
    try:
        url = f"{RENDER_API_URL}{endpoint}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Erreur {response.status_code} pour {endpoint}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur pour {endpoint}: {e}")
        return []

def export_buildings(cursor, buildings):
    """Exporter les immeubles"""
    for building in buildings:
        cursor.execute("""
            INSERT INTO immeubles (
                id_immeuble, nom_immeuble, adresse, ville, province, code_postal, pays,
                nbr_unite, annee_construction, prix_achete, mise_de_fond, taux_interet,
                valeur_actuel, proprietaire, banque, contracteur, notes,
                date_creation, date_modification
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            building.get('id_immeuble'),
            building.get('nom_immeuble'),
            building.get('adresse'),
            building.get('ville'),
            building.get('province'),
            building.get('code_postal'),
            building.get('pays'),
            building.get('nbr_unite'),
            building.get('annee_construction'),
            building.get('prix_achete'),
            building.get('mise_de_fond'),
            building.get('taux_interet'),
            building.get('valeur_actuel'),
            building.get('proprietaire'),
            building.get('banque'),
            building.get('contracteur'),
            building.get('notes'),
            building.get('date_creation'),
            building.get('date_modification')
        ))

def export_units(cursor, units):
    """Exporter les unités"""
    for unit in units:
        if isinstance(unit, dict):
            cursor.execute("""
                INSERT INTO unites (
                    id_unite, id_immeuble, adresse_unite, type, nbr_chambre,
                    nbr_salle_de_bain, date_creation, date_modification
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                unit.get('id_unite'),
                unit.get('id_immeuble'),
                unit.get('adresse_unite'),
                unit.get('type'),
                unit.get('nbr_chambre'),
                unit.get('nbr_salle_de_bain'),
                unit.get('date_creation'),
                unit.get('date_modification')
            ))

def export_tenants(cursor, tenants):
    """Exporter les locataires"""
    for tenant in tenants:
        if isinstance(tenant, dict):
            cursor.execute("""
                INSERT INTO locataires (
                    id_locataire, id_unite, nom, prenom, email, telephone,
                    statut, notes, date_creation, date_modification
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tenant.get('id_locataire'),
                tenant.get('id_unite'),
                tenant.get('nom'),
                tenant.get('prenom'),
                tenant.get('email'),
                tenant.get('telephone'),
                tenant.get('statut'),
                tenant.get('notes'),
                tenant.get('date_creation'),
                tenant.get('date_modification')
            ))

def export_invoices(cursor, invoices):
    """Exporter les factures"""
    for invoice in invoices:
        if isinstance(invoice, dict):
            cursor.execute("""
                INSERT INTO factures (
                    id_facture, id_immeuble, categorie, montant, date, no_facture,
                    source, pdf_facture, type_paiement, notes, date_creation, date_modification
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice.get('id_facture'),
                invoice.get('id_immeuble'),
                invoice.get('categorie'),
                invoice.get('montant'),
                invoice.get('date'),
                invoice.get('no_facture'),
                invoice.get('source'),
                invoice.get('pdf_facture'),
                invoice.get('type_paiement'),
                invoice.get('notes'),
                invoice.get('date_creation'),
                invoice.get('date_modification')
            ))

def show_database_summary(cursor):
    """Afficher un résumé de la base de données exportée"""
    print("\n📊 Résumé de la base de données exportée:")
    print("=" * 50)
    
    tables = ['immeubles', 'unites', 'locataires', 'factures', 'baux', 'rapports_immeuble']
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"📋 {table}: {count} enregistrements")
        except sqlite3.OperationalError:
            print(f"📋 {table}: Table non trouvée")
    
    # Afficher quelques exemples d'immeubles
    print("\n🏢 Exemples d'immeubles:")
    cursor.execute("SELECT id_immeuble, nom_immeuble, adresse, ville FROM immeubles LIMIT 3")
    buildings = cursor.fetchall()
    
    for building in buildings:
        print(f"  - ID {building[0]}: {building[1]} - {building[2]}, {building[3]}")

def main():
    """Fonction principale"""
    print("🚀 Export de la base de données Render")
    print("=" * 50)
    
    # Créer le répertoire de données
    create_data_directory()
    
    # Créer la base de données locale
    conn, cursor = create_local_database()
    if not conn:
        return
    
    try:
        # Exporter les données
        if export_data_from_api(conn, cursor):
            print("\n✅ Export terminé avec succès!")
            show_database_summary(cursor)
            
            print(f"\n📁 Fichier de base de données: {LOCAL_DB_PATH.absolute()}")
            print("💡 Vous pouvez maintenant ouvrir ce fichier avec DB Browser for SQLite")
        else:
            print("❌ Échec de l'export")
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
