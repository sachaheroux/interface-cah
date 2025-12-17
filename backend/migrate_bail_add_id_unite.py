#!/usr/bin/env python3
"""
Migration : Ajouter id_unite à la table baux et migrer les données depuis locataires
AVEC SAUVEGARDE ET RESTAURATION EN CAS D'ÉCHEC

Cette migration :
1. Sauvegarde les données actuelles
2. Ajoute id_unite à baux
3. Migre les données depuis locataires vers baux
4. Vérifie l'intégrité
5. Permet la restauration en cas d'échec
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from sqlalchemy import text, create_engine
from database import DATABASE_PATH, engine, DATA_DIR

# Chemin pour la sauvegarde (utilise DATA_DIR pour Render)
if os.environ.get("ENVIRONMENT") == "production" or not os.path.exists("./data"):
    BACKUP_DIR = Path(DATA_DIR) / "migrations_backup"
else:
    BACKUP_DIR = Path("./data/migrations_backup")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def create_backup():
    """Créer une sauvegarde complète de la base de données"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"bail_migration_backup_{timestamp}.db"
    
    print(f"📦 Création de la sauvegarde : {backup_file}")
    
    # Copier le fichier de base de données (seulement si SQLite et fichier existe)
    if DATABASE_PATH and os.path.exists(DATABASE_PATH):
        import shutil
        shutil.copy2(DATABASE_PATH, backup_file)
    else:
        print("⚠️ Pas de fichier SQLite à sauvegarder (utilise engine directement)")
        backup_file = None
    
    # Sauvegarder aussi les données critiques en JSON
    json_backup_file = BACKUP_DIR / f"bail_migration_backup_{timestamp}.json"
    
    try:
        with engine.connect() as connection:
            # Sauvegarder les baux
            baux_result = connection.execute(text("SELECT * FROM baux"))
            baux_data = [dict(row._mapping) for row in baux_result]
            
            # Sauvegarder les locataires (pour id_unite)
            locataires_result = connection.execute(text("SELECT id_locataire, id_unite FROM locataires"))
            locataires_data = [dict(row._mapping) for row in locataires_result]
            
            backup_data = {
                "timestamp": timestamp,
                "baux": baux_data,
                "locataires_id_unite": locataires_data
            }
            
            with open(json_backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            print(f"✅ Sauvegarde JSON créée : {json_backup_file}")
            
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde JSON : {e}")
    
    if backup_file_path:
        print(f"✅ Sauvegarde complète créée : {backup_file_path}")
    else:
        print(f"✅ Sauvegarde JSON créée (pas de fichier DB à copier)")
    return backup_file_path, str(json_backup_file)

def restore_backup(backup_file):
    """Restaurer la base de données depuis la sauvegarde"""
    if not backup_file:
        print("⚠️ Pas de fichier de sauvegarde à restaurer")
        return
    
    print(f"🔄 Restauration depuis : {backup_file}")
    if DATABASE_PATH and os.path.exists(backup_file):
        import shutil
        shutil.copy2(backup_file, DATABASE_PATH)
        print("✅ Restauration terminée")
    else:
        print("⚠️ Restauration manuelle nécessaire - fichier de sauvegarde : {backup_file}")

def migrate_bail_add_id_unite():
    """Migration principale"""
    db_info = DATABASE_PATH if DATABASE_PATH else "Render Persistent Disk (via engine)"
    print(f"🚀 Début de la migration pour ajouter id_unite à baux")
    print(f"📁 Base de données : {db_info}")
    
    if not engine:
        print("❌ Moteur de base de données non initialisé.")
        return False
    
    backup_file = None
    json_backup_file = None
    
    try:
        # ÉTAPE 1 : Créer la sauvegarde
        backup_file, json_backup_file = create_backup()
        
        with engine.connect() as connection:
            # ÉTAPE 2 : Vérifier l'état actuel
            print("\n📊 Vérification de l'état actuel...")
            
            # Vérifier si id_unite existe déjà dans baux
            result = connection.execute(text("PRAGMA table_info(baux)"))
            columns = result.fetchall()
            id_unite_exists = any(col[1] == 'id_unite' for col in columns)
            
            if id_unite_exists:
                print("⚠️ La colonne 'id_unite' existe déjà dans 'baux'. Vérification des données...")
                # Vérifier si toutes les valeurs sont NULL
                result = connection.execute(text("SELECT COUNT(*) FROM baux WHERE id_unite IS NULL"))
                null_count = result.scalar()
                if null_count > 0:
                    print(f"⚠️ {null_count} baux ont id_unite NULL. Migration des données...")
                else:
                    print("✅ Tous les baux ont déjà un id_unite. Migration peut-être déjà effectuée.")
                    return True
            
            # Compter les baux et locataires
            result = connection.execute(text("SELECT COUNT(*) FROM baux"))
            baux_count = result.scalar()
            
            result = connection.execute(text("SELECT COUNT(*) FROM locataires WHERE id_unite IS NOT NULL"))
            locataires_with_unite = result.scalar()
            
            print(f"   - Nombre de baux : {baux_count}")
            print(f"   - Nombre de locataires avec unité : {locataires_with_unite}")
            
            if baux_count == 0:
                print("⚠️ Aucun bail trouvé. Migration non nécessaire.")
                return True
            
            # Vérifier que tous les baux ont un locataire avec unité
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM baux b
                LEFT JOIN locataires l ON b.id_locataire = l.id_locataire
                WHERE l.id_unite IS NULL
            """))
            baux_sans_unite = result.scalar()
            
            if baux_sans_unite > 0:
                print(f"⚠️ ATTENTION : {baux_sans_unite} baux ont un locataire sans unité assignée.")
                print("   Ces baux ne pourront pas avoir d'id_unite. Continuation de la migration...")
                print("   Vous devrez assigner une unité à ces locataires après la migration.")
            
            # ÉTAPE 3 : Ajouter la colonne id_unite à baux (si elle n'existe pas)
            if not id_unite_exists:
                print("\n🔄 Ajout de la colonne 'id_unite' à la table 'baux'...")
                connection.execute(text("ALTER TABLE baux ADD COLUMN id_unite INTEGER"))
                connection.commit()
                print("   ✅ Colonne 'id_unite' ajoutée.")
            
            # ÉTAPE 4 : Migrer les données depuis locataires vers baux
            print("\n🔄 Migration des données id_unite depuis locataires vers baux...")
            
            update_query = text("""
                UPDATE baux
                SET id_unite = (
                    SELECT id_unite
                    FROM locataires
                    WHERE locataires.id_locataire = baux.id_locataire
                )
                WHERE id_unite IS NULL
            """)
            
            result = connection.execute(update_query)
            updated_count = result.rowcount
            connection.commit()
            
            print(f"   ✅ {updated_count} baux mis à jour avec id_unite.")
            
            # ÉTAPE 5 : Vérifier l'intégrité
            print("\n🔍 Vérification de l'intégrité des données...")
            
            # Vérifier qu'il n'y a pas de NULL
            result = connection.execute(text("SELECT COUNT(*) FROM baux WHERE id_unite IS NULL"))
            null_count = result.scalar()
            
            if null_count > 0:
                print(f"❌ ERREUR : {null_count} baux ont encore id_unite NULL.")
                print("   Restauration de la sauvegarde...")
                restore_backup(backup_file)
                return False
            
            # Vérifier que tous les id_unite existent dans la table unites
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM baux b
                LEFT JOIN unites u ON b.id_unite = u.id_unite
                WHERE u.id_unite IS NULL
            """))
            invalid_unite_count = result.scalar()
            
            if invalid_unite_count > 0:
                print(f"❌ ERREUR : {invalid_unite_count} baux ont un id_unite invalide.")
                print("   Restauration de la sauvegarde...")
                restore_backup(backup_file)
                return False
            
            # ÉTAPE 6 : Ajouter la contrainte NOT NULL et ForeignKey
            print("\n🔄 Ajout des contraintes (NOT NULL et ForeignKey)...")
            
            # SQLite ne permet pas de modifier directement une colonne pour ajouter NOT NULL
            # On doit recréer la table avec les contraintes
            
            # 1. Renommer l'ancienne table
            connection.execute(text("ALTER TABLE baux RENAME TO old_baux"))
            print("   ✅ Table 'baux' renommée en 'old_baux'.")
            
            # 2. Créer la nouvelle table avec id_unite NOT NULL et ForeignKey
            create_table_sql = text("""
                CREATE TABLE baux (
                    id_bail INTEGER PRIMARY KEY,
                    id_locataire INTEGER NOT NULL,
                    id_unite INTEGER NOT NULL,
                    date_debut DATE NOT NULL,
                    date_fin DATE,
                    prix_loyer DECIMAL(10, 2) DEFAULT 0,
                    methode_paiement VARCHAR(50),
                    pdf_bail VARCHAR(255),
                    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                    date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_locataire) REFERENCES locataires (id_locataire) ON DELETE CASCADE,
                    FOREIGN KEY (id_unite) REFERENCES unites (id_unite) ON DELETE CASCADE
                )
            """)
            connection.execute(create_table_sql)
            print("   ✅ Nouvelle table 'baux' créée avec contraintes.")
            
            # 3. Copier les données (seulement les baux qui ont un id_unite)
            copy_data_sql = text("""
                INSERT INTO baux (
                    id_bail, id_locataire, id_unite, date_debut, date_fin,
                    prix_loyer, methode_paiement, pdf_bail, date_creation, date_modification
                )
                SELECT 
                    id_bail, id_locataire, id_unite, date_debut, date_fin,
                    prix_loyer, methode_paiement, pdf_bail, date_creation, date_modification
                FROM old_baux
                WHERE id_unite IS NOT NULL
            """)
            result = connection.execute(copy_data_sql)
            copied_count = result.rowcount
            print(f"   ✅ {copied_count} baux copiés vers la nouvelle table.")
            
            # Vérifier s'il y a des baux sans unité qui n'ont pas été copiés
            result = connection.execute(text("SELECT COUNT(*) FROM old_baux WHERE id_unite IS NULL"))
            skipped_count = result.scalar()
            if skipped_count > 0:
                print(f"   ⚠️ {skipped_count} baux sans unité n'ont pas été copiés (ils doivent avoir une unité assignée).")
            
            # 4. Recréer les index
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_baux_id_locataire ON baux(id_locataire)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_baux_id_unite ON baux(id_unite)"))
            print("   ✅ Index recréés.")
            
            # 5. Supprimer l'ancienne table
            connection.execute(text("DROP TABLE old_baux"))
            print("   ✅ Ancienne table supprimée.")
            
            connection.commit()
            
            # Vérification finale
            result = connection.execute(text("SELECT COUNT(*) FROM baux"))
            final_count = result.scalar()
            
            if final_count == baux_count:
                print(f"\n✅ Migration terminée avec succès !")
                print(f"   - {final_count} baux migrés")
                print(f"   - Sauvegarde disponible : {backup_file}")
                print(f"   - Sauvegarde JSON disponible : {json_backup_file}")
                return True
            else:
                print(f"\n❌ ERREUR : Nombre de baux différent ({final_count} vs {baux_count})")
                print("   Restauration de la sauvegarde...")
                restore_backup(backup_file)
                return False
                
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        
        if backup_file:
            print("\n🔄 Tentative de restauration...")
            try:
                restore_backup(backup_file)
                print("✅ Restauration réussie")
            except Exception as restore_error:
                print(f"❌ Erreur lors de la restauration: {restore_error}")
                print(f"⚠️ Sauvegarde manuelle disponible : {backup_file}")
        
        return False

if __name__ == "__main__":
    print("="*70)
    print("MIGRATION : Ajouter id_unite à la table baux")
    print("="*70)
    
    success = migrate_bail_add_id_unite()
    
    print("="*70)
    if success:
        print("✅ Migration réussie !")
    else:
        print("❌ Migration échouée. Vérifiez les erreurs ci-dessus.")
        print("💾 Une sauvegarde a été créée dans ./data/migrations_backup/")
    print("="*70)

