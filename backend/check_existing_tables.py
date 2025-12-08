#!/usr/bin/env python3
"""
Script pour vérifier les tables existantes dans la base de données
"""

import os
import sys
from datetime import datetime

# Ajouter le répertoire backend au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_existing_tables():
    """Vérifier les tables existantes dans la base de données"""
    
    print("🔍 VÉRIFICATION DES TABLES EXISTANTES")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from database_construction import get_construction_db_context
        from sqlalchemy import text
        
        print("1️⃣ CONNEXION À LA BASE DE DONNÉES")
        print("-" * 30)
        
        with get_construction_db_context() as db:
            print("✅ Connexion à la base de données établie")
            
            # Lister toutes les tables
            print("\n2️⃣ LISTE DE TOUTES LES TABLES")
            print("-" * 30)
            
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            
            print(f"📊 Tables trouvées: {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")
            
            # Vérifier spécifiquement les tables de construction
            print("\n3️⃣ VÉRIFICATION DES TABLES CONSTRUCTION")
            print("-" * 30)
            
            construction_tables = ['projets', 'employes', 'fournisseurs', 'matieres_premieres', 'commandes', 'punchs_employes']
            
            for table_name in construction_tables:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    print(f"✅ Table '{table_name}': {count} enregistrements")
                except Exception as e:
                    print(f"❌ Table '{table_name}': N'existe pas ({e})")
            
            # Vérifier les tables locatives
            print("\n4️⃣ VÉRIFICATION DES TABLES LOCATIVES")
            print("-" * 30)
            
            locative_tables = ['immeubles', 'locataires', 'unites', 'baux', 'transactions']
            
            for table_name in locative_tables:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    print(f"✅ Table '{table_name}': {count} enregistrements")
                except Exception as e:
                    print(f"❌ Table '{table_name}': N'existe pas ({e})")
            
            print("\n5️⃣ ANALYSE")
            print("-" * 30)
            
            if any('projets' in str(table) for table in tables):
                print("✅ La table 'projets' existe")
            else:
                print("❌ La table 'projets' n'existe pas")
                print("💡 Il faut créer les tables de construction")
            
            if any('immeubles' in str(table) for table in tables):
                print("✅ Les tables locatives existent")
            else:
                print("❌ Les tables locatives n'existent pas")
            
            return tables
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Fonction principale"""
    
    print("🚀 VÉRIFICATION DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    tables = check_existing_tables()
    
    print("\n" + "=" * 50)
    print("🎯 VÉRIFICATION TERMINÉE")
    print("=" * 50)
    
    if tables:
        print(f"📊 {len(tables)} tables trouvées dans la base")
    else:
        print("❌ Aucune table trouvée")

if __name__ == "__main__":
    main()


