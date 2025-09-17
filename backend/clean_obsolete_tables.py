#!/usr/bin/env python3
"""
Script pour nettoyer les tables obsolètes en anglais
"""

import sqlite3
import os

def clean_obsolete_tables():
    """Supprimer les tables obsolètes en anglais"""
    
    # Chemin vers la base de données
    db_path = "data/cah_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🧹 Nettoyage des tables obsolètes...")
        
        # Tables obsolètes à supprimer
        obsolete_tables = [
            "assignments",
            "building_reports", 
            "buildings",
            "invoices",
            "tenants",
            "unit_reports",
            "units"
        ]
        
        for table in obsolete_tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"✅ Table {table} supprimée")
            except Exception as e:
                print(f"⚠️  Erreur lors de la suppression de {table}: {e}")
        
        # Valider les changements
        conn.commit()
        
        # Vérifier le résultat
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("\n📊 Tables après nettoyage:")
        for table in sorted(tables):
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} enregistrements")
        
        conn.close()
        print("\n✅ Nettoyage terminé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🧹 Nettoyage des tables obsolètes")
    print("=" * 50)
    
    success = clean_obsolete_tables()
    
    if success:
        print("\n🎉 Nettoyage réussi!")
    else:
        print("\n💥 Nettoyage échoué!")
