#!/usr/bin/env python3
"""
Nettoyer les anciennes tables en anglais et garder seulement les tables françaises
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
from sqlalchemy import text

def cleanup_old_tables():
    """Supprimer toutes les anciennes tables en anglais"""
    
    print("🧹 Nettoyage des anciennes tables en anglais")
    print("=" * 50)
    
    # Tables à supprimer (anciennes en anglais)
    old_tables = [
        'assignments',
        'building_reports', 
        'buildings',
        'invoices',
        'tenants',
        'unit_reports',
        'units'
    ]
    
    # Tables à garder (nouvelles en français)
    french_tables = [
        'immeubles',
        'unites', 
        'locataires',
        'baux',
        'factures',
        'rapports_immeuble'
    ]
    
    try:
        with db_manager.engine.connect() as conn:
            # Lister toutes les tables existantes
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            existing_tables = [row[0] for row in result.fetchall()]
            
            print(f"📋 Tables existantes: {existing_tables}")
            
            # Supprimer les anciennes tables
            for table in old_tables:
                if table in existing_tables:
                    print(f"🗑️ Suppression de la table '{table}'...")
                    conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    conn.commit()
                    print(f"✅ Table '{table}' supprimée")
                else:
                    print(f"ℹ️ Table '{table}' n'existe pas")
            
            # Vérifier les tables restantes
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            remaining_tables = [row[0] for row in result.fetchall()]
            
            print(f"\n📋 Tables restantes: {remaining_tables}")
            
            # Vérifier que seules les tables françaises restent
            for table in remaining_tables:
                if table not in french_tables and table != 'sqlite_sequence':
                    print(f"⚠️ Table inattendue restante: '{table}'")
            
            print(f"\n✅ Nettoyage terminé! {len(remaining_tables)} tables restantes")
            
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cleanup_old_tables()
