#!/usr/bin/env python3
"""
Script pour télécharger la base de données SQLite de Render en local
Permet d'examiner les données avec DB Browser for SQLite
"""

import os
import requests
import gzip
import shutil
from datetime import datetime
from pathlib import Path

# Configuration
RENDER_API_URL = "https://interface-cah-backend.onrender.com"
LOCAL_DATA_DIR = Path("data")
LOCAL_DB_PATH = LOCAL_DATA_DIR / "cah_database_local.db"

def create_data_directory():
    """Créer le répertoire data s'il n'existe pas"""
    LOCAL_DATA_DIR.mkdir(exist_ok=True)
    print(f"📁 Répertoire de données: {LOCAL_DATA_DIR.absolute()}")

def download_database():
    """Télécharger la base de données depuis Render"""
    try:
        print("🔄 Téléchargement de la base de données depuis Render...")
        
        # Endpoint pour télécharger la base de données (à créer si nécessaire)
        # Pour l'instant, on va créer un script qui se connecte directement
        # et exporte les données via l'API
        
        # Vérifier la connectivité
        health_url = f"{RENDER_API_URL}/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Connexion à Render établie")
        else:
            print(f"⚠️  Connexion à Render: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion à Render: {e}")
        return False
    
    return True

def export_database_via_api():
    """Exporter les données via l'API et créer une base SQLite locale"""
    try:
        print("📊 Export des données via l'API...")
        
        # Importer les modules nécessaires
        import sqlite3
        from database_service_francais import DatabaseServiceFrancais
        from database import DatabaseManager
        
        # Créer une base de données locale
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        # Créer les tables avec le schéma français
        from models_francais import Base
        from sqlalchemy import create_engine
        
        # Créer l'engine pour la base locale
        local_engine = create_engine(f"sqlite:///{LOCAL_DB_PATH}")
        Base.metadata.create_all(local_engine)
        
        print("✅ Tables créées dans la base locale")
        
        # Récupérer les données depuis l'API
        buildings = get_data_from_api("/api/buildings")
        units = get_data_from_api("/api/units")
        tenants = get_data_from_api("/api/tenants")
        invoices = get_data_from_api("/api/invoices")
        
        # Insérer les données dans la base locale
        if buildings:
            insert_buildings(cursor, buildings)
            print(f"✅ {len(buildings)} immeubles exportés")
        
        if units:
            insert_units(cursor, units)
            print(f"✅ {len(units)} unités exportées")
            
        if tenants:
            insert_tenants(cursor, tenants)
            print(f"✅ {len(tenants)} locataires exportés")
            
        if invoices:
            insert_invoices(cursor, invoices)
            print(f"✅ {len(invoices)} factures exportées")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Base de données locale créée: {LOCAL_DB_PATH.absolute()}")
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
            data = response.json()
            print(f"🔍 DEBUG - {endpoint}: {type(data)} - {data[:2] if isinstance(data, list) and len(data) > 0 else data}")
            
            # Gérer le cas où l'API retourne {'data': []}
            if isinstance(data, dict) and 'data' in data:
                return data['data']
            elif isinstance(data, list):
                return data
            else:
                return []
        else:
            print(f"⚠️  Erreur {response.status_code} pour {endpoint}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur pour {endpoint}: {e}")
        return []

def insert_buildings(cursor, buildings):
    """Insérer les immeubles dans la base locale"""
    for building in buildings:
        cursor.execute("""
            INSERT OR REPLACE INTO immeubles (
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

def insert_units(cursor, units):
    """Insérer les unités dans la base locale"""
    for unit in units:
        # Vérifier que unit est un dictionnaire
        if not isinstance(unit, dict):
            print(f"⚠️  Unité ignorée (pas un dictionnaire): {unit}")
            continue
            
        cursor.execute("""
            INSERT OR REPLACE INTO unites (
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

def insert_tenants(cursor, tenants):
    """Insérer les locataires dans la base locale"""
    for tenant in tenants:
        # Vérifier que tenant est un dictionnaire
        if not isinstance(tenant, dict):
            print(f"⚠️  Locataire ignoré (pas un dictionnaire): {tenant}")
            continue
            
        cursor.execute("""
            INSERT OR REPLACE INTO locataires (
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

def insert_invoices(cursor, invoices):
    """Insérer les factures dans la base locale"""
    for invoice in invoices:
        # Vérifier que invoice est un dictionnaire
        if not isinstance(invoice, dict):
            print(f"⚠️  Facture ignorée (pas un dictionnaire): {invoice}")
            continue
            
        cursor.execute("""
            INSERT OR REPLACE INTO factures (
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

def show_database_info():
    """Afficher des informations sur la base de données locale"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        print("\n📊 Informations sur la base de données locale:")
        print("=" * 50)
        
        # Compter les enregistrements par table
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
        cursor.execute("SELECT id_immeuble, nom_immeuble, adresse, ville FROM immeubles LIMIT 5")
        buildings = cursor.fetchall()
        
        for building in buildings:
            print(f"  - ID {building[0]}: {building[1]} - {building[2]}, {building[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage des informations: {e}")

def main():
    """Fonction principale"""
    print("🚀 Téléchargement de la base de données Render")
    print("=" * 50)
    
    # Créer le répertoire de données
    create_data_directory()
    
    # Tester la connexion à Render
    if not download_database():
        print("❌ Impossible de se connecter à Render")
        return
    
    # Exporter les données via l'API
    if export_database_via_api():
        print("\n✅ Export terminé avec succès!")
        show_database_info()
        
        print(f"\n📁 Base de données locale: {LOCAL_DB_PATH.absolute()}")
        print("💡 Vous pouvez maintenant ouvrir ce fichier avec DB Browser for SQLite")
    else:
        print("❌ Échec de l'export")

if __name__ == "__main__":
    main()
