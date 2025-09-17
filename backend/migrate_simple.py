#!/usr/bin/env python3
"""
Script de migration simple pour créer la table transactions
"""

import sqlite3
import os

def migrate_database():
    """Créer la table transactions"""
    
    # Chemin vers la base de données
    db_path = "data/cah_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Création de la table transactions...")
        
        # Créer la table transactions
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
        
        # Supprimer les anciennes tables si elles existent
        print("🗑️  Suppression des anciennes tables...")
        cursor.execute("DROP TABLE IF EXISTS factures")
        cursor.execute("DROP TABLE IF EXISTS rapports_immeuble")
        
        # Valider les changements
        conn.commit()
        
        # Vérifier le résultat
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
    print("🚀 Migration simple vers transactions")
    print("=" * 50)
    
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration réussie!")
        print("💡 Vous pouvez maintenant déployer le nouveau code.")
    else:
        print("\n💥 Migration échouée!")
        print("🔧 Vérifiez les erreurs ci-dessus.")
