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
    
    print(f"\n📦 CRÉATION DE LA SAUVEGARDE")
    print(f"   - Répertoire : {BACKUP_DIR}")
    print(f"   - Fichier : {backup_file}")
    print(f"   - Répertoire existe : {os.path.exists(BACKUP_DIR)}")
    
    # Vérifier que le répertoire existe et est accessible
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Répertoire de sauvegarde accessible")
    except Exception as dir_error:
        print(f"\n❌ ERREUR : Impossible de créer/accéder au répertoire de sauvegarde")
        print(f"   - Erreur : {dir_error}")
        print(f"   - Chemin : {BACKUP_DIR}")
        print(f"   - Vérifiez les permissions d'écriture sur le disque Render")
        raise
    
    # Copier le fichier de base de données (seulement si SQLite et fichier existe)
    if DATABASE_PATH and os.path.exists(DATABASE_PATH):
        try:
            import shutil
            print(f"   - Copie du fichier SQLite : {DATABASE_PATH}")
            shutil.copy2(DATABASE_PATH, backup_file)
            print(f"   ✅ Sauvegarde SQLite créée : {backup_file}")
            print(f"   - Taille : {os.path.getsize(backup_file)} octets")
        except Exception as copy_error:
            print(f"\n❌ ERREUR lors de la copie du fichier SQLite : {copy_error}")
            print(f"   - Fichier source : {DATABASE_PATH}")
            print(f"   - Fichier destination : {backup_file}")
            raise
    else:
        print(f"   ⚠️ Pas de fichier SQLite à sauvegarder (utilise engine directement)")
        print(f"   - DATABASE_PATH : {DATABASE_PATH}")
        print(f"   - Fichier existe : {os.path.exists(DATABASE_PATH) if DATABASE_PATH else 'N/A'}")
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
        json_backup_file = None
    
    if backup_file:
        print(f"✅ Sauvegarde complète créée : {backup_file}")
    else:
        print(f"✅ Sauvegarde JSON créée (pas de fichier DB à copier)")
    
    return backup_file, json_backup_file

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
    print("\n" + "="*70)
    print("🚀 DÉBUT DE LA MIGRATION : Ajouter id_unite à la table baux")
    print("="*70)
    
    # Vérifier l'environnement et le disque Render
    is_render = os.environ.get("ENVIRONMENT") == "production" or os.path.exists("/opt/render")
    data_dir = DATA_DIR if DATA_DIR else "/opt/render/project/src/data"
    
    print(f"\n📊 INFORMATIONS SUR L'ENVIRONNEMENT:")
    print(f"   - Environnement : {'Render (Production)' if is_render else 'Local (Développement)'}")
    print(f"   - DATA_DIR : {data_dir}")
    print(f"   - DATA_DIR existe : {os.path.exists(data_dir) if data_dir else 'N/A'}")
    print(f"   - DATABASE_PATH : {DATABASE_PATH if DATABASE_PATH else 'Non défini (utilise engine)'}")
    
    db_info = DATABASE_PATH if DATABASE_PATH else "Render Persistent Disk (via engine)"
    print(f"\n📁 Base de données : {db_info}")
    
    if not engine:
        print("\n❌ ERREUR CRITIQUE : Moteur de base de données non initialisé.")
        print("   Cause possible :")
        print("   - La connexion à la base de données n'a pas pu être établie")
        print("   - Le disque persistant Render n'est pas monté correctement")
        print("   - La variable d'environnement DATA_DIR n'est pas configurée")
        return False
    
    print(f"✅ Moteur de base de données initialisé")
    
    backup_file = None
    json_backup_file = None
    
    try:
        # ÉTAPE 1 : Créer la sauvegarde
        print(f"\n📦 ÉTAPE 1 : Création de la sauvegarde")
        print(f"   - Répertoire de sauvegarde : {BACKUP_DIR}")
        print(f"   - Répertoire existe : {os.path.exists(BACKUP_DIR)}")
        
        try:
            backup_file, json_backup_file = create_backup()
            if backup_file:
                print(f"   ✅ Sauvegarde créée : {backup_file}")
            if json_backup_file:
                print(f"   ✅ Sauvegarde JSON créée : {json_backup_file}")
        except Exception as backup_error:
            print(f"\n❌ ERREUR lors de la création de la sauvegarde : {backup_error}")
            print(f"   Type d'erreur : {type(backup_error).__name__}")
            import traceback
            print(f"   Détails : {traceback.format_exc()}")
            print(f"\n⚠️ ATTENTION : La migration continue sans sauvegarde.")
            print(f"   Il est recommandé d'arrêter et de corriger le problème de sauvegarde.")
            backup_file = None
            json_backup_file = None
        
        print(f"\n🔌 ÉTAPE 2 : Connexion à la base de données")
        try:
            connection = engine.connect()
            print(f"   ✅ Connexion établie")
        except Exception as conn_error:
            print(f"\n❌ ERREUR lors de la connexion à la base de données : {conn_error}")
            print(f"   Type d'erreur : {type(conn_error).__name__}")
            import traceback
            print(f"   Détails : {traceback.format_exc()}")
            print(f"\n💡 SOLUTIONS POSSIBLES :")
            print(f"   1. Vérifier que le disque persistant Render est monté sur {data_dir}")
            print(f"   2. Vérifier les permissions d'écriture sur {data_dir}")
            print(f"   3. Vérifier que la base de données existe et est accessible")
            return False
        
        try:
            # ÉTAPE 3 : Vérifier l'état actuel
            print("\n📊 ÉTAPE 3 : Vérification de l'état actuel de la base de données")
            
            # Vérifier si la table baux existe
            try:
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='baux'"))
                table_exists = result.fetchone() is not None
                if not table_exists:
                    print(f"\n❌ ERREUR : La table 'baux' n'existe pas dans la base de données.")
                    print(f"   La migration ne peut pas continuer.")
                    return False
                print(f"   ✅ Table 'baux' existe")
            except Exception as table_check_error:
                print(f"\n❌ ERREUR lors de la vérification de la table : {table_check_error}")
                import traceback
                print(f"   Détails : {traceback.format_exc()}")
                return False
            
            # Vérifier si id_unite existe déjà dans baux
            try:
                result = connection.execute(text("PRAGMA table_info(baux)"))
                columns = result.fetchall()
                column_names = [col[1] for col in columns]
                print(f"   📋 Colonnes dans 'baux' : {', '.join(column_names)}")
                id_unite_exists = 'id_unite' in column_names
                print(f"   - Colonne 'id_unite' existe : {id_unite_exists}")
            except Exception as pragma_error:
                print(f"\n❌ ERREUR lors de la vérification des colonnes : {pragma_error}")
                import traceback
                print(f"   Détails : {traceback.format_exc()}")
                return False
            
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
            
            # ÉTAPE 4 : Ajouter la colonne id_unite à baux (si elle n'existe pas)
            if not id_unite_exists:
                print("\n🔄 ÉTAPE 4 : Ajout de la colonne 'id_unite' à la table 'baux'...")
                try:
                    connection.execute(text("ALTER TABLE baux ADD COLUMN id_unite INTEGER"))
                    connection.commit()
                    print("   ✅ Colonne 'id_unite' ajoutée avec succès.")
                except Exception as alter_error:
                    print(f"\n❌ ERREUR lors de l'ajout de la colonne : {alter_error}")
                    print(f"   Type d'erreur : {type(alter_error).__name__}")
                    import traceback
                    print(f"   Détails : {traceback.format_exc()}")
                    print(f"\n💡 CAUSES POSSIBLES :")
                    print(f"   - La colonne existe déjà mais n'a pas été détectée")
                    print(f"   - Problème de permissions sur la base de données")
                    print(f"   - La base de données est verrouillée par une autre opération")
                    if backup_file:
                        restore_backup(backup_file)
                    return False
            
            # ÉTAPE 5 : Migrer les données depuis locataires vers baux
            print("\n🔄 ÉTAPE 5 : Migration des données id_unite depuis locataires vers baux...")
            
            try:
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
            except Exception as update_error:
                print(f"\n❌ ERREUR lors de la migration des données : {update_error}")
                print(f"   Type d'erreur : {type(update_error).__name__}")
                import traceback
                print(f"   Détails : {traceback.format_exc()}")
                print(f"\n💡 CAUSES POSSIBLES :")
                print(f"   - Des baux ont des locataires qui n'existent pas")
                print(f"   - Des baux ont des locataires sans unité assignée")
                print(f"   - Problème de contrainte de clé étrangère")
                if backup_file:
                    restore_backup(backup_file)
                return False
            
            # ÉTAPE 6 : Vérifier l'intégrité
            print("\n🔍 ÉTAPE 6 : Vérification de l'intégrité des données...")
            
            # Vérifier qu'il n'y a pas de NULL
            try:
                result = connection.execute(text("SELECT COUNT(*) FROM baux WHERE id_unite IS NULL"))
                null_count = result.scalar()
                
                if null_count > 0:
                    print(f"\n⚠️ ATTENTION : {null_count} baux ont encore id_unite NULL.")
                    print(f"   Ces baux seront exclus de la nouvelle table avec contraintes NOT NULL.")
                    print(f"   Vous devrez assigner une unité à ces baux après la migration.")
                else:
                    print(f"   ✅ Tous les baux ont un id_unite assigné.")
            except Exception as check_error:
                print(f"\n❌ ERREUR lors de la vérification des NULL : {check_error}")
                import traceback
                print(f"   Détails : {traceback.format_exc()}")
                if backup_file:
                    restore_backup(backup_file)
                return False
            
            # Vérifier que tous les id_unite existent dans la table unites
            try:
                result = connection.execute(text("""
                    SELECT COUNT(*) 
                    FROM baux b
                    LEFT JOIN unites u ON b.id_unite = u.id_unite
                    WHERE b.id_unite IS NOT NULL AND u.id_unite IS NULL
                """))
                invalid_unite_count = result.scalar()
                
                if invalid_unite_count > 0:
                    print(f"\n❌ ERREUR : {invalid_unite_count} baux ont un id_unite qui n'existe pas dans la table 'unites'.")
                    print(f"   Ces baux référencent des unités qui ont été supprimées.")
                    print(f"   Restauration de la sauvegarde...")
                    if backup_file:
                        restore_backup(backup_file)
                    return False
                else:
                    print(f"   ✅ Tous les id_unite sont valides.")
            except Exception as check_error:
                print(f"\n❌ ERREUR lors de la vérification des unités : {check_error}")
                import traceback
                print(f"   Détails : {traceback.format_exc()}")
                if backup_file:
                    restore_backup(backup_file)
                return False
            
            # ÉTAPE 7 : Ajouter la contrainte NOT NULL et ForeignKey
            print("\n🔄 ÉTAPE 7 : Ajout des contraintes (NOT NULL et ForeignKey)...")
            print("   ℹ️ SQLite ne permet pas de modifier directement une colonne pour ajouter NOT NULL")
            print("   ℹ️ On doit recréer la table avec les contraintes")
            
            # 1. Renommer l'ancienne table
            try:
                connection.execute(text("ALTER TABLE baux RENAME TO old_baux"))
                connection.commit()
                print("   ✅ Table 'baux' renommée en 'old_baux'.")
            except Exception as rename_error:
                print(f"\n❌ ERREUR lors du renommage de la table : {rename_error}")
                print(f"   Type d'erreur : {type(rename_error).__name__}")
                import traceback
                print(f"   Détails : {traceback.format_exc()}")
                if backup_file:
                    restore_backup(backup_file)
                return False
            
            # 2. Créer la nouvelle table avec id_unite NOT NULL et ForeignKey
            try:
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
                connection.commit()
                print("   ✅ Nouvelle table 'baux' créée avec contraintes.")
            except Exception as create_error:
                print(f"\n❌ ERREUR lors de la création de la nouvelle table : {create_error}")
                print(f"   Type d'erreur : {type(create_error).__name__}")
                import traceback
                print(f"   Détails : {traceback.format_exc()}")
                print(f"\n💡 TENTATIVE DE RESTAURATION...")
                # Essayer de restaurer en renommant old_baux en baux
                try:
                    connection.execute(text("ALTER TABLE old_baux RENAME TO baux"))
                    connection.commit()
                    print(f"   ✅ Table restaurée (old_baux -> baux)")
                except:
                    pass
                if backup_file:
                    restore_backup(backup_file)
                return False
            
            # 3. Copier les données (seulement les baux qui ont un id_unite)
            try:
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
                connection.commit()
                print(f"   ✅ {copied_count} baux copiés vers la nouvelle table.")
                
                # Vérifier s'il y a des baux sans unité qui n'ont pas été copiés
                result = connection.execute(text("SELECT COUNT(*) FROM old_baux WHERE id_unite IS NULL"))
                skipped_count = result.scalar()
                if skipped_count > 0:
                    print(f"   ⚠️ {skipped_count} baux sans unité n'ont pas été copiés (ils doivent avoir une unité assignée).")
            except Exception as copy_error:
                print(f"\n❌ ERREUR lors de la copie des données : {copy_error}")
                print(f"   Type d'erreur : {type(copy_error).__name__}")
                import traceback
                print(f"   Détails : {traceback.format_exc()}")
                print(f"\n💡 CAUSES POSSIBLES :")
                print(f"   - Des données ne respectent pas les contraintes NOT NULL")
                print(f"   - Des clés étrangères invalides")
                print(f"   - Problème de types de données")
                # Essayer de restaurer
                try:
                    connection.execute(text("DROP TABLE IF EXISTS baux"))
                    connection.execute(text("ALTER TABLE old_baux RENAME TO baux"))
                    connection.commit()
                    print(f"   ✅ Table restaurée (old_baux -> baux)")
                except:
                    pass
                if backup_file:
                    restore_backup(backup_file)
                return False
            
            # 4. Recréer les index
            try:
                connection.execute(text("CREATE INDEX IF NOT EXISTS ix_baux_id_locataire ON baux(id_locataire)"))
                connection.execute(text("CREATE INDEX IF NOT EXISTS ix_baux_id_unite ON baux(id_unite)"))
                connection.commit()
                print("   ✅ Index recréés.")
            except Exception as index_error:
                print(f"\n⚠️ ATTENTION : Erreur lors de la création des index : {index_error}")
                print(f"   La migration continue, mais les index ne sont pas créés.")
            
            # 5. Supprimer l'ancienne table
            try:
                connection.execute(text("DROP TABLE old_baux"))
                connection.commit()
                print("   ✅ Ancienne table supprimée.")
            except Exception as drop_error:
                print(f"\n⚠️ ATTENTION : Erreur lors de la suppression de l'ancienne table : {drop_error}")
                print(f"   La table 'old_baux' existe toujours. Vous pouvez la supprimer manuellement.")
            
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
                
        finally:
            connection.close()
            print(f"\n🔌 Connexion fermée")
                
    except Exception as e:
        print(f"\n" + "="*70)
        print(f"❌ ERREUR CRITIQUE LORS DE LA MIGRATION")
        print("="*70)
        print(f"\n📋 DÉTAILS DE L'ERREUR :")
        print(f"   - Type d'erreur : {type(e).__name__}")
        print(f"   - Message : {str(e)}")
        print(f"\n📊 STACK TRACE COMPLET :")
        import traceback
        traceback.print_exc()
        
        print(f"\n💡 DIAGNOSTIC :")
        if "no such table" in str(e).lower():
            print(f"   - La table 'baux' n'existe pas dans la base de données")
            print(f"   - Vérifiez que la base de données est correctement initialisée")
        elif "disk" in str(e).lower() or "i/o" in str(e).lower():
            print(f"   - Problème d'accès au disque persistant Render")
            print(f"   - Vérifiez que le disque est monté sur {data_dir}")
            print(f"   - Vérifiez les permissions d'écriture")
        elif "locked" in str(e).lower():
            print(f"   - La base de données est verrouillée")
            print(f"   - Une autre opération est peut-être en cours")
            print(f"   - Attendez quelques secondes et réessayez")
        elif "foreign key" in str(e).lower():
            print(f"   - Problème de contrainte de clé étrangère")
            print(f"   - Des données référencent des enregistrements qui n'existent pas")
        else:
            print(f"   - Erreur inconnue, consultez le stack trace ci-dessus")
        
        if backup_file:
            print(f"\n🔄 TENTATIVE DE RESTAURATION...")
            try:
                restore_backup(backup_file)
                print(f"✅ Restauration réussie depuis : {backup_file}")
            except Exception as restore_error:
                print(f"❌ ERREUR lors de la restauration : {restore_error}")
                print(f"⚠️ Sauvegarde manuelle disponible : {backup_file}")
                print(f"   Vous pouvez restaurer manuellement en copiant ce fichier")
        else:
            print(f"\n⚠️ Aucune sauvegarde disponible pour restauration")
        
        print(f"\n" + "="*70)
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

