#!/usr/bin/env python3
"""
Script pour télécharger la base de données de construction depuis Render
et la sauvegarder localement en SQLite
"""

import requests
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"
LOCAL_DB_PATH = "data/construction_projects_local.db"

def create_local_database():
    """Créer la base de données SQLite locale"""
    print("🗄️ Création de la base de données locale...")
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    # Créer les tables de construction
    tables_sql = {
        'projets': '''
            CREATE TABLE IF NOT EXISTS projets (
                id_projet INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                date_debut TEXT,
                date_fin_prevue TEXT,
                date_fin_reelle TEXT,
                notes TEXT,
                date_creation TEXT,
                date_modification TEXT
            )
        ''',
        'fournisseurs': '''
            CREATE TABLE IF NOT EXISTS fournisseurs (
                id_fournisseur INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                rue TEXT,
                ville TEXT,
                province TEXT,
                code_postal TEXT,
                numero TEXT,
                adresse_courriel TEXT,
                date_creation TEXT,
                date_modification TEXT
            )
        ''',
        'matieres_premieres': '''
            CREATE TABLE IF NOT EXISTS matieres_premieres (
                id_matiere_premiere INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                notes TEXT,
                date_creation TEXT,
                date_modification TEXT
            )
        ''',
        'commandes': '''
            CREATE TABLE IF NOT EXISTS commandes (
                id_commande INTEGER PRIMARY KEY,
                id_projet INTEGER NOT NULL,
                id_fournisseur INTEGER,
                montant REAL NOT NULL,
                statut TEXT,
                type_de_paiement TEXT,
                notes TEXT,
                date_creation TEXT,
                date_modification TEXT,
                FOREIGN KEY (id_projet) REFERENCES projets (id_projet),
                FOREIGN KEY (id_fournisseur) REFERENCES fournisseurs (id_fournisseur)
            )
        ''',
        'lignes_commande': '''
            CREATE TABLE IF NOT EXISTS lignes_commande (
                id_ligne_commande INTEGER PRIMARY KEY,
                id_commande INTEGER NOT NULL,
                id_matiere_premiere INTEGER NOT NULL,
                quantite REAL NOT NULL,
                unite TEXT,
                montant REAL NOT NULL,
                section TEXT,
                date_creation TEXT,
                date_modification TEXT,
                FOREIGN KEY (id_commande) REFERENCES commandes (id_commande),
                FOREIGN KEY (id_matiere_premiere) REFERENCES matieres_premieres (id_matiere_premiere)
            )
        ''',
        'employes': '''
            CREATE TABLE IF NOT EXISTS employes (
                id_employe INTEGER PRIMARY KEY,
                prenom TEXT NOT NULL,
                nom TEXT NOT NULL,
                poste TEXT,
                numero TEXT,
                adresse_courriel TEXT,
                taux_horaire REAL,
                date_creation TEXT,
                date_modification TEXT
            )
        ''',
        'punchs_employes': '''
            CREATE TABLE IF NOT EXISTS punchs_employes (
                id_punch INTEGER PRIMARY KEY,
                id_employe INTEGER NOT NULL,
                id_projet INTEGER NOT NULL,
                date TEXT NOT NULL,
                heure_travaillee REAL NOT NULL,
                section TEXT,
                date_creation TEXT,
                date_modification TEXT,
                FOREIGN KEY (id_employe) REFERENCES employes (id_employe),
                FOREIGN KEY (id_projet) REFERENCES projets (id_projet)
            )
        ''',
        'sous_traitants': '''
            CREATE TABLE IF NOT EXISTS sous_traitants (
                id_st INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                rue TEXT,
                ville TEXT,
                province TEXT,
                code_postal TEXT,
                numero TEXT,
                adresse_courriel TEXT,
                date_creation TEXT,
                date_modification TEXT
            )
        ''',
        'factures_st': '''
            CREATE TABLE IF NOT EXISTS factures_st (
                id_facture INTEGER PRIMARY KEY,
                id_projet INTEGER NOT NULL,
                id_st INTEGER,
                montant REAL NOT NULL,
                section TEXT,
                notes TEXT,
                date_creation TEXT,
                date_modification TEXT,
                FOREIGN KEY (id_projet) REFERENCES projets (id_projet),
                FOREIGN KEY (id_st) REFERENCES sous_traitants (id_st)
            )
        '''
    }
    
    for table_name, sql in tables_sql.items():
        cursor.execute(sql)
        print(f"✅ Table '{table_name}' créée")
    
    conn.commit()
    conn.close()
    print(f"✅ Base de données locale créée : {LOCAL_DB_PATH}")

def fetch_data_from_api(endpoint: str) -> List[Dict[str, Any]]:
    """Récupérer les données depuis l'API Render"""
    try:
        print(f"📡 Récupération des données depuis {endpoint}...")
        response = requests.get(f"{RENDER_URL}{endpoint}", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                items = data.get('data', [])
                print(f"✅ {len(items)} éléments récupérés")
                return items
            else:
                print(f"❌ Erreur API: {data.get('message', 'Erreur inconnue')}")
                return []
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return []

def insert_data_to_local_db(table_name: str, data: List[Dict[str, Any]]):
    """Insérer les données dans la base locale"""
    if not data:
        print(f"⚠️ Aucune donnée à insérer pour '{table_name}'")
        return
    
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    # Vider la table avant d'insérer
    cursor.execute(f"DELETE FROM {table_name}")
    print(f"🗑️ Table '{table_name}' vidée")
    
    # Préparer les colonnes et valeurs
    first_item = data[0]
    columns = list(first_item.keys())
    placeholders = ', '.join(['?' for _ in columns])
    
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    # Insérer chaque élément
    for item in data:
        values = [item.get(col) for col in columns]
        cursor.execute(insert_sql, values)
    
    conn.commit()
    conn.close()
    print(f"✅ {len(data)} éléments insérés dans '{table_name}'")

def download_all_construction_data():
    """Télécharger toutes les données de construction"""
    print("🚀 Début du téléchargement de la base de données construction...")
    print(f"🌐 URL Render: {RENDER_URL}")
    print(f"📁 Base locale: {LOCAL_DB_PATH}")
    print("=" * 60)
    
    # Créer la base locale
    create_local_database()
    
    # Endpoints à télécharger
    endpoints = {
        'projets': '/api/construction/projets',
        'fournisseurs': '/api/construction/fournisseurs',
        'matieres_premieres': '/api/construction/matieres-premieres',
        'commandes': '/api/construction/commandes',
        'lignes_commande': '/api/construction/lignes-commande',
        'employes': '/api/construction/employes',
        'punchs_employes': '/api/construction/punchs-employes',
        'sous_traitants': '/api/construction/sous-traitants',
        'factures_st': '/api/construction/factures-st'
    }
    
    total_items = 0
    
    for table_name, endpoint in endpoints.items():
        print(f"\n📊 Traitement de '{table_name}'...")
        
        # Récupérer les données
        data = fetch_data_from_api(endpoint)
        
        # Insérer dans la base locale
        insert_data_to_local_db(table_name, data)
        
        total_items += len(data)
    
    print("\n" + "=" * 60)
    print("🏁 Téléchargement terminé !")
    print(f"📊 Total d'éléments téléchargés: {total_items}")
    print(f"📁 Base de données locale: {LOCAL_DB_PATH}")
    
    # Afficher un résumé
    print("\n📋 Résumé des données:")
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    for table_name in endpoints.keys():
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  - {table_name}: {count} éléments")
    
    conn.close()

def test_local_database():
    """Tester la base de données locale"""
    print("\n🧪 Test de la base de données locale...")
    
    if not os.path.exists(LOCAL_DB_PATH):
        print("❌ Base de données locale non trouvée")
        return
    
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    # Lister les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"📊 Tables trouvées: {len(tables)}")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  - {table_name}: {count} éléments")
    
    # Afficher quelques exemples d'employés
    print("\n👥 Exemples d'employés:")
    cursor.execute("SELECT prenom, nom, poste FROM employes LIMIT 3")
    employees = cursor.fetchall()
    
    for emp in employees:
        print(f"  - {emp[0]} {emp[1]} ({emp[2] or 'Poste non défini'})")
    
    conn.close()

if __name__ == "__main__":
    try:
        download_all_construction_data()
        test_local_database()
    except KeyboardInterrupt:
        print("\n⏹️ Téléchargement interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
