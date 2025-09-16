#!/usr/bin/env python3
"""
Script pour créer une unité directement dans la base de données locale
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# Configuration
LOCAL_DB_PATH = Path("data/cah_database_local.db")

def create_local_unit():
    """Créer une unité dans la base de données locale"""
    try:
        print("🔄 Création d'une unité locale...")
        
        # Vérifier que la base existe
        if not LOCAL_DB_PATH.exists():
            print(f"❌ Base de données locale non trouvée: {LOCAL_DB_PATH}")
            return False
        
        # Se connecter à la base
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        # Vérifier que l'immeuble existe
        cursor.execute("SELECT id_immeuble, nom_immeuble FROM immeubles WHERE id_immeuble = 1")
        building = cursor.fetchone()
        
        if not building:
            print("❌ Aucun immeuble trouvé avec l'ID 1")
            return False
        
        print(f"✅ Immeuble trouvé: {building[1]} (ID: {building[0]})")
        
        # Créer l'unité
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO unites (
                id_immeuble, adresse_unite, type, nbr_chambre, nbr_salle_de_bain,
                date_creation, date_modification
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            1,  # id_immeuble
            "56 rue Vachon, Appartement 1",  # adresse_unite
            "4 1/2",  # type
            2,  # nbr_chambre
            1,  # nbr_salle_de_bain
            now,  # date_creation
            now   # date_modification
        ))
        
        unit_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Unité créée avec l'ID: {unit_id}")
        
        # Vérifier la création
        cursor.execute("SELECT * FROM unites WHERE id_unite = ?", (unit_id,))
        unit = cursor.fetchone()
        
        if unit:
            print("📋 Détails de l'unité créée:")
            cursor.execute("PRAGMA table_info(unites)")
            columns = [col[1] for col in cursor.fetchall()]
            
            for i, value in enumerate(unit):
                print(f"  - {columns[i]}: {value}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Création d'une unité locale")
    print("=" * 40)
    
    if create_local_unit():
        print("\n✅ Unité créée avec succès!")
        print("💡 Vous pouvez maintenant tester la page des unités")
    else:
        print("\n❌ Échec de la création")

if __name__ == "__main__":
    main()
