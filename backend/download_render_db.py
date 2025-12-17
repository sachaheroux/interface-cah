#!/usr/bin/env python3
"""
Script pour télécharger la base de données Render en local pour inspection
"""

import requests
import sqlite3
import json
import os
from datetime import datetime

# Configuration
RENDER_API_BASE = "https://interface-cah-backend.onrender.com"
LOCAL_DB_PATH = "data/cah_database_render.db"

def create_local_db():
    """Créer la base de données locale"""
    os.makedirs("data", exist_ok=True)
    
    # Supprimer l'ancienne base si elle existe
    if os.path.exists(LOCAL_DB_PATH):
        os.remove(LOCAL_DB_PATH)
    
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    # Créer les tables avec la vraie structure de Render
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS immeubles (
            id_immeuble INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_immeuble TEXT NOT NULL,
            adresse TEXT NOT NULL,
            ville TEXT NOT NULL,
            province TEXT DEFAULT '',
            code_postal TEXT NOT NULL,
            pays TEXT DEFAULT '',
            nbr_unite INTEGER DEFAULT 0,
            annee_construction INTEGER,
            prix_achete DECIMAL(12, 2) DEFAULT 0,
            mise_de_fond DECIMAL(12, 2) DEFAULT 0,
            taux_interet DECIMAL(5, 2) DEFAULT 0,
            valeur_actuel DECIMAL(12, 2) DEFAULT 0,
            dette_restante DECIMAL(12, 2) DEFAULT 0,
            proprietaire TEXT DEFAULT '',
            banque TEXT DEFAULT '',
            contracteur TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_modification DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS unites (
            id_unite INTEGER PRIMARY KEY AUTOINCREMENT,
            id_immeuble INTEGER NOT NULL,
            adresse_unite TEXT NOT NULL,
            type TEXT NOT NULL,
            nbr_chambre INTEGER DEFAULT 0,
            nbr_salle_de_bain INTEGER DEFAULT 0,
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_immeuble) REFERENCES immeubles (id_immeuble) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locataires (
            id_locataire INTEGER PRIMARY KEY AUTOINCREMENT,
            id_unite INTEGER NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT DEFAULT '',
            telephone TEXT DEFAULT '',
            statut TEXT DEFAULT 'actif',
            notes TEXT DEFAULT '',
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_unite) REFERENCES unites (id_unite) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS baux (
            id_bail INTEGER PRIMARY KEY AUTOINCREMENT,
            id_locataire INTEGER NOT NULL,
            id_unite INTEGER NOT NULL,
            date_debut DATE NOT NULL,
            date_fin DATE NOT NULL,
            prix_loyer DECIMAL(10, 2) NOT NULL,
            methode_paiement TEXT DEFAULT '',
            pdf_bail TEXT DEFAULT '',
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_locataire) REFERENCES locataires (id_locataire) ON DELETE CASCADE,
            FOREIGN KEY (id_unite) REFERENCES unites (id_unite) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id_transaction INTEGER PRIMARY KEY AUTOINCREMENT,
            id_immeuble INTEGER NOT NULL,
            type TEXT NOT NULL,
            categorie TEXT NOT NULL,
            montant DECIMAL(12, 2) NOT NULL,
            date_de_transaction DATE NOT NULL,
            methode_de_paiement TEXT DEFAULT '',
            reference TEXT DEFAULT '',
            source TEXT DEFAULT '',
            pdf_transaction TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_immeuble) REFERENCES immeubles (id_immeuble) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paiements_loyers (
            id_paiement INTEGER PRIMARY KEY AUTOINCREMENT,
            id_bail INTEGER NOT NULL,
            mois INTEGER NOT NULL,
            annee INTEGER NOT NULL,
            date_paiement_reelle DATE NOT NULL,
            montant_paye DECIMAL(10, 2) NOT NULL,
            notes TEXT,
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_bail) REFERENCES baux (id_bail) ON DELETE CASCADE,
            UNIQUE (id_bail, mois, annee)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Base de données locale créée: {LOCAL_DB_PATH}")

def fetch_and_insert_data():
    """Récupérer les données de Render et les insérer localement"""
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    # 1. Immeubles
    print("📥 Récupération des immeubles...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/buildings")
        if response.status_code == 200:
            buildings = response.json()
            print(f"   {len(buildings)} immeubles trouvés")
            
            cursor.execute("DELETE FROM immeubles")
            for building in buildings:
                cursor.execute("""
                    INSERT INTO immeubles (id_immeuble, nom_immeuble, adresse, ville, province, code_postal, pays,
                                         nbr_unite, annee_construction, prix_achete, mise_de_fond, taux_interet,
                                         valeur_actuel, dette_restante, proprietaire, banque, contracteur, notes, date_creation, date_modification)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    building.get('id_immeuble'),
                    building.get('nom_immeuble', ''),
                    building.get('adresse', ''),
                    building.get('ville', ''),
                    building.get('province', ''),
                    building.get('code_postal', ''),
                    building.get('pays', ''),
                    building.get('nbr_unite', 0),
                    building.get('annee_construction'),
                    building.get('prix_achete', 0),
                    building.get('mise_de_fond', 0),
                    building.get('taux_interet', 0),
                    building.get('valeur_actuel', 0),
                    building.get('dette_restante', 0),
                    building.get('proprietaire', ''),
                    building.get('banque', ''),
                    building.get('contracteur', ''),
                    building.get('notes', ''),
                    building.get('date_creation'),
                    building.get('date_modification')
                ))
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # 2. Unités
    print("📥 Récupération des unités...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/units")
        if response.status_code == 200:
            data = response.json()
            units = data.get('data', [])
            print(f"   {len(units)} unités trouvées")
            
            cursor.execute("DELETE FROM unites")
            for unit in units:
                cursor.execute("""
                    INSERT INTO unites (id_unite, id_immeuble, adresse_unite, type, nbr_chambre, 
                                      nbr_salle_de_bain, date_creation, date_modification)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    unit.get('id_unite'),
                    unit.get('id_immeuble'),
                    unit.get('adresse_unite', ''),
                    unit.get('type', ''),
                    unit.get('nbr_chambre', 0),
                    unit.get('nbr_salle_de_bain', 0),
                    unit.get('date_creation'),
                    unit.get('date_modification')
                ))
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # 3. Locataires
    print("📥 Récupération des locataires...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/tenants")
        if response.status_code == 200:
            data = response.json()
            tenants = data.get('data', [])
            print(f"   {len(tenants)} locataires trouvés")
            
            cursor.execute("DELETE FROM locataires")
            for tenant in tenants:
                cursor.execute("""
                    INSERT INTO locataires (id_locataire, id_unite, nom, prenom, email, 
                                          telephone, statut, notes, date_creation, date_modification)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tenant.get('id_locataire'),
                    tenant.get('id_unite'),
                    tenant.get('nom', ''),
                    tenant.get('prenom', ''),
                    tenant.get('email', ''),
                    tenant.get('telephone', ''),
                    tenant.get('statut', 'actif'),
                    tenant.get('notes', ''),
                    tenant.get('date_creation'),
                    tenant.get('date_modification')
                ))
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # 4. Baux
    print("📥 Récupération des baux...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/leases")
        if response.status_code == 200:
            data = response.json()
            leases = data.get('data', [])
            print(f"   {len(leases)} baux trouvés")
            
            cursor.execute("DELETE FROM baux")
            for lease in leases:
                cursor.execute("""
                    INSERT INTO baux (id_bail, id_locataire, id_unite, date_debut, date_fin, prix_loyer, 
                                    methode_paiement, pdf_bail, date_creation, date_modification)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lease.get('id_bail'),
                    lease.get('id_locataire'),
                    lease.get('id_unite'),  # Maintenant id_unite est directement sur le bail
                    lease.get('date_debut'),
                    lease.get('date_fin'),
                    lease.get('prix_loyer', 0),
                    lease.get('methode_paiement', ''),
                    lease.get('pdf_bail', ''),
                    lease.get('date_creation'),
                    lease.get('date_modification')
                ))
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # 5. Transactions
    print("📥 Récupération des transactions...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/transactions")
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', [])
            print(f"   {len(transactions)} transactions trouvées")
            
            cursor.execute("DELETE FROM transactions")
            for transaction in transactions:
                cursor.execute("""
                    INSERT INTO transactions (id_transaction, id_immeuble, type, categorie, montant, 
                                           date_de_transaction, methode_de_paiement, reference, source, 
                                           pdf_transaction, notes, date_creation, date_modification)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction.get('id_transaction'),
                    transaction.get('id_immeuble'),
                    transaction.get('type', ''),
                    transaction.get('categorie', ''),
                    transaction.get('montant', 0),
                    transaction.get('date_de_transaction'),
                    transaction.get('methode_de_paiement', ''),
                    transaction.get('reference', ''),
                    transaction.get('source', ''),
                    transaction.get('pdf_transaction', ''),
                    transaction.get('notes', ''),
                    transaction.get('date_creation'),
                    transaction.get('date_modification')
                ))
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # 6. Paiements de loyers
    print("📥 Récupération des paiements de loyers...")
    try:
        # Récupérer tous les baux pour obtenir leurs paiements
        response = requests.get(f"{RENDER_API_BASE}/api/leases")
        if response.status_code == 200:
            data = response.json()
            leases = data.get('data', [])
            print(f"   {len(leases)} baux trouvés, récupération des paiements...")
            
            cursor.execute("DELETE FROM paiements_loyers")
            paiements_count = 0
            
            for lease in leases:
                lease_id = lease.get('id_bail')
                if lease_id:
                    try:
                        paiements_response = requests.get(f"{RENDER_API_BASE}/api/paiements-loyers/bail/{lease_id}")
                        if paiements_response.status_code == 200:
                            paiements_data = paiements_response.json()
                            paiements = paiements_data.get('data', [])
                            
                            for paiement in paiements:
                                cursor.execute("""
                                    INSERT INTO paiements_loyers (id_paiement, id_bail, mois, annee, 
                                                               date_paiement_reelle, montant_paye, notes, 
                                                               date_creation, date_modification)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    paiement.get('id_paiement'),
                                    paiement.get('id_bail'),
                                    paiement.get('mois'),
                                    paiement.get('annee'),
                                    paiement.get('date_paiement_reelle'),
                                    paiement.get('montant_paye'),
                                    paiement.get('notes', ''),
                                    paiement.get('date_creation'),
                                    paiement.get('date_modification')
                                ))
                                paiements_count += 1
                    except Exception as e:
                        print(f"   ⚠️ Erreur pour le bail {lease_id}: {e}")
            
            print(f"   {paiements_count} paiements de loyers trouvés")
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Données insérées dans la base locale")

def show_summary():
    """Afficher un résumé des données"""
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    print("\n📊 RÉSUMÉ DES DONNÉES:")
    
    # Compter les enregistrements
    tables = ['immeubles', 'unites', 'locataires', 'baux', 'transactions', 'paiements_loyers']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   {table}: {count} enregistrements")
    
    # Afficher quelques exemples
    print("\n🏢 EXEMPLES D'IMMEUBLES:")
    cursor.execute("SELECT id_immeuble, nom_immeuble, adresse FROM immeubles LIMIT 3")
    for row in cursor.fetchall():
        print(f"   ID: {row[0]}, Nom: {row[1]}, Adresse: {row[2]}")
    
    print("\n🏠 EXEMPLES D'UNITÉS:")
    cursor.execute("SELECT id_unite, adresse_unite, type FROM unites LIMIT 3")
    for row in cursor.fetchall():
        print(f"   ID: {row[0]}, Adresse: {row[1]}, Type: {row[2]}")
    
    print("\n💰 EXEMPLES DE PAIEMENTS DE LOYERS:")
    cursor.execute("SELECT id_paiement, id_bail, mois, annee, montant_paye FROM paiements_loyers LIMIT 3")
    for row in cursor.fetchall():
        print(f"   ID: {row[0]}, Bail: {row[1]}, {row[2]}/{row[3]}: {row[4]}$ ✅ Payé")
    
    conn.close()

if __name__ == "__main__":
    print("🔄 Téléchargement de la base de données Render...")
    create_local_db()
    fetch_and_insert_data()
    show_summary()
    print(f"\n✅ Base de données téléchargée: {LOCAL_DB_PATH}")
    print("💡 Tu peux maintenant ouvrir ce fichier avec DB Browser for SQLite")
