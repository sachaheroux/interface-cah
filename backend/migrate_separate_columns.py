#!/usr/bin/env python3
"""
Script de migration pour séparer les colonnes financières et de contacts
"""

import sqlite3
import os
import json
from datetime import datetime

def migrate_separate_columns():
    """Migrer pour séparer les colonnes financières et de contacts"""
    
    # Chemin de la base de données
    db_path = os.getenv('DATABASE_URL', 'data/cah_database.db')
    
    # Si c'est une URL, extraire le chemin du fichier
    if db_path.startswith('sqlite:///'):
        db_path = db_path.replace('sqlite:///', '')
    
    print(f"🗄️ Base de données: {db_path}")
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 MIGRATION - SÉPARATION DES COLONNES")
        print("=" * 50)
        
        # Vérifier la structure actuelle
        cursor.execute("PRAGMA table_info(buildings)")
        current_columns = [row[1] for row in cursor.fetchall()]
        print(f"📊 Colonnes actuelles: {current_columns}")
        
        # Colonnes à ajouter
        new_columns = [
            ("purchase_price", "REAL DEFAULT 0.0"),
            ("down_payment", "REAL DEFAULT 0.0"),
            ("interest_rate", "REAL DEFAULT 0.0"),
            ("current_value", "REAL DEFAULT 0.0"),
            ("owner_name", "TEXT"),
            ("bank_name", "TEXT"),
            ("contractor_name", "TEXT")
        ]
        
        # Ajouter les nouvelles colonnes
        for column_name, column_type in new_columns:
            if column_name not in current_columns:
                try:
                    alter_sql = f"ALTER TABLE buildings ADD COLUMN {column_name} {column_type}"
                    cursor.execute(alter_sql)
                    print(f"✅ Colonne ajoutée: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"⚠️  Colonne déjà présente: {column_name}")
                    else:
                        print(f"❌ Erreur pour {column_name}: {e}")
            else:
                print(f"ℹ️  Colonne déjà présente: {column_name}")
        
        # Migrer les données existantes
        print("\n📊 Migration des données existantes...")
        
        # Récupérer tous les immeubles
        cursor.execute("SELECT id, financials, contacts FROM buildings WHERE financials IS NOT NULL OR contacts IS NOT NULL")
        buildings = cursor.fetchall()
        
        for building_id, financials_json, contacts_json in buildings:
            try:
                # Parser les données JSON
                financials = json.loads(financials_json) if financials_json else {}
                contacts = json.loads(contacts_json) if contacts_json else {}
                
                # Mettre à jour avec les nouvelles colonnes
                cursor.execute("""
                    UPDATE buildings SET
                        purchase_price = ?,
                        down_payment = ?,
                        interest_rate = ?,
                        current_value = ?,
                        owner_name = ?,
                        bank_name = ?,
                        contractor_name = ?
                    WHERE id = ?
                """, (
                    financials.get("purchasePrice", 0.0),
                    financials.get("downPayment", 0.0),
                    financials.get("interestRate", 0.0),
                    financials.get("currentValue", 0.0),
                    contacts.get("owner", ""),
                    contacts.get("bank", ""),
                    contacts.get("contractor", ""),
                    building_id
                ))
                
                print(f"✅ Données migrées pour l'immeuble {building_id}")
                
            except Exception as e:
                print(f"❌ Erreur migration immeuble {building_id}: {e}")
        
        # Vérifier la nouvelle structure
        cursor.execute("PRAGMA table_info(buildings)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"\n📊 Nouvelles colonnes: {new_columns}")
        
        # Sauvegarder les changements
        conn.commit()
        print("\n✅ Migration terminée avec succès!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 MIGRATION - SÉPARATION DES COLONNES")
    print("=" * 50)
    
    # Effectuer la migration
    success = migrate_separate_columns()
    
    if success:
        print(f"\n🎉 Migration réussie!")
    else:
        print(f"\n❌ Migration échouée!")
