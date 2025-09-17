#!/usr/bin/env python3
"""
Script de migration pour remplacer les factures par des transactions
et supprimer la table rapports_immeuble
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrer la base de données vers le nouveau schéma"""
    
    # Chemin vers la base de données
    db_path = "data/cah_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Début de la migration vers le schéma transactions...")
        
        # 1. Créer la nouvelle table transactions
        print("📋 Création de la table transactions...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id_transaction INTEGER PRIMARY KEY AUTOINCREMENT,
                id_immeuble INTEGER NOT NULL,
                type_transaction TEXT NOT NULL,
                montant DECIMAL(12,2) NOT NULL,
                description TEXT,
                date_transaction DATE NOT NULL,
                methode_paiement TEXT,
                statut TEXT DEFAULT 'en_attente',
                reference TEXT,
                pdf_document TEXT,
                notes TEXT,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_immeuble) REFERENCES immeubles(id_immeuble)
            )
        """)
        
        # 2. Migrer les données de factures vers transactions (si la table factures existe)
        print("🔄 Migration des données factures vers transactions...")
        try:
            cursor.execute("SELECT * FROM factures")
            factures = cursor.fetchall()
            
            for facture in factures:
                # Mapper les colonnes factures vers transactions
                cursor.execute("""
                    INSERT INTO transactions (
                        id_immeuble, type_transaction, montant, description, 
                        date_transaction, methode_paiement, statut, reference, 
                        pdf_document, notes, date_creation, date_modification
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    facture[1],  # id_immeuble
                    'facture',   # type_transaction (par défaut)
                    facture[3],  # montant
                    f"Facture: {facture[5]}",  # description basée sur no_facture
                    facture[4],  # date_transaction (date)
                    facture[8],  # methode_paiement (type_paiement)
                    'paye',      # statut (par défaut)
                    facture[5],  # reference (no_facture)
                    facture[7],  # pdf_document (pdf_facture)
                    facture[9],  # notes
                    facture[10], # date_creation
                    facture[11]  # date_modification
                ))
            
            print(f"✅ {len(factures)} factures migrées vers transactions")
            
        except sqlite3.OperationalError as e:
            if "no such table: factures" in str(e):
                print("ℹ️  Table factures n'existe pas, pas de migration nécessaire")
            else:
                raise e
        
        # 3. Supprimer l'ancienne table factures
        print("🗑️  Suppression de l'ancienne table factures...")
        try:
            cursor.execute("DROP TABLE IF EXISTS factures")
            print("✅ Table factures supprimée")
        except Exception as e:
            print(f"⚠️  Erreur lors de la suppression de factures: {e}")
        
        # 4. Supprimer la table rapports_immeuble
        print("🗑️  Suppression de la table rapports_immeuble...")
        try:
            cursor.execute("DROP TABLE IF EXISTS rapports_immeuble")
            print("✅ Table rapports_immeuble supprimée")
        except Exception as e:
            print(f"⚠️  Erreur lors de la suppression de rapports_immeuble: {e}")
        
        # 5. Valider les changements
        conn.commit()
        
        # 6. Vérifier le résultat
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("\n📊 Tables après migration:")
        for table in sorted(tables):
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} enregistrements")
        
        conn.close()
        print("\n✅ Migration terminée avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Migration vers le schéma transactions")
    print("=" * 50)
    
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration réussie!")
        print("💡 Vous pouvez maintenant déployer le nouveau code.")
    else:
        print("\n💥 Migration échouée!")
        print("🔧 Vérifiez les erreurs ci-dessus.")
