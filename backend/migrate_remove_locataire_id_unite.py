#!/usr/bin/env python3
"""
Migration : Supprimer id_unite de la table locataires
Après la migration bail-add-id-unite, les baux ont maintenant id_unite directement.
Les locataires n'ont plus besoin de id_unite car on peut trouver leur unité via leur bail actif.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from sqlalchemy import text
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
    backup_file = BACKUP_DIR / f"remove_locataire_id_unite_backup_{timestamp}.db"
    
    print(f"\n📦 CRÉATION DE LA SAUVEGARDE")
    print(f"   - Répertoire : {BACKUP_DIR}")
    print(f"   - Fichier : {backup_file}")
    
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Répertoire de sauvegarde accessible")
    except Exception as dir_error:
        print(f"\n❌ ERREUR : Impossible de créer/accéder au répertoire de sauvegarde")
        print(f"   - Erreur : {dir_error}")
        raise
    
    if DATABASE_PATH and os.path.exists(DATABASE_PATH):
        try:
            import shutil
            print(f"   - Copie du fichier SQLite : {DATABASE_PATH}")
            shutil.copy2(DATABASE_PATH, backup_file)
            print(f"   ✅ Sauvegarde SQLite créée : {backup_file}")
            print(f"   - Taille : {os.path.getsize(backup_file)} octets")
        except Exception as copy_error:
            print(f"\n❌ ERREUR lors de la copie du fichier SQLite : {copy_error}")
            raise
    else:
        print(f"   ⚠️ Pas de fichier SQLite à sauvegarder (utilise engine directement)")
        backup_file = None
    
    return backup_file

def restore_backup(backup_file):
    """Restaurer la base de données depuis la sauvegarde"""
    if not backup_file or not os.path.exists(backup_file):
        print(f"⚠️ Fichier de sauvegarde non trouvé : {backup_file}")
        return False
    
    if DATABASE_PATH:
        try:
            import shutil
            shutil.copy2(backup_file, DATABASE_PATH)
            print(f"✅ Base de données restaurée depuis : {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la restauration : {e}")
            return False
    else:
        print(f"⚠️ Restauration manuelle nécessaire - fichier de sauvegarde : {backup_file}")
        return False

def migrate_remove_locataire_id_unite():
    """Migration principale : supprimer id_unite de locataires"""
    print("\n" + "="*70)
    print("🚀 DÉBUT DE LA MIGRATION : Supprimer id_unite de la table locataires")
    print("="*70)
    
    # Vérifier l'environnement
    is_render = os.environ.get("ENVIRONMENT") == "production" or os.path.exists("/opt/render")
    data_dir = DATA_DIR if DATA_DIR else "/opt/render/project/src/data"
    
    print(f"\n📊 INFORMATIONS SUR L'ENVIRONNEMENT:")
    print(f"   - Environnement : {'Render (Production)' if is_render else 'Local (Développement)'}")
    print(f"   - DATA_DIR : {data_dir}")
    print(f"   - DATABASE_PATH : {DATABASE_PATH if DATABASE_PATH else 'Non défini (utilise engine)'}")
    
    if not engine:
        print("\n❌ ERREUR CRITIQUE : Moteur de base de données non initialisé.")
        return False
    
    print(f"✅ Moteur de base de données initialisé")
    
    backup_file = None
    
    try:
        # ÉTAPE 1 : Créer la sauvegarde
        print(f"\n📦 ÉTAPE 1 : Création de la sauvegarde")
        try:
            backup_file = create_backup()
            if backup_file:
                print(f"   ✅ Sauvegarde créée : {backup_file}")
        except Exception as backup_error:
            print(f"\n❌ ERREUR lors de la création de la sauvegarde : {backup_error}")
            print(f"   ⚠️ ATTENTION : La migration continue sans sauvegarde.")
            backup_file = None
        
        # ÉTAPE 2 : Connexion à la base de données
        print(f"\n🔌 ÉTAPE 2 : Connexion à la base de données")
        try:
            connection = engine.connect()
            print(f"   ✅ Connexion établie")
        except Exception as conn_error:
            print(f"\n❌ ERREUR lors de la connexion : {conn_error}")
            return False
        
        try:
            # ÉTAPE 3 : Vérifier l'état actuel
            print(f"\n📊 ÉTAPE 3 : Vérification de l'état actuel")
            
            # Vérifier si la colonne id_unite existe dans locataires
            try:
                result = connection.execute(text("PRAGMA table_info(locataires)"))
                columns = result.fetchall()
                column_names = [col[1] for col in columns]
                print(f"   📋 Colonnes dans 'locataires' : {', '.join(column_names)}")
                id_unite_exists = 'id_unite' in column_names
                print(f"   - Colonne 'id_unite' existe : {id_unite_exists}")
            except Exception as pragma_error:
                print(f"\n❌ ERREUR lors de la vérification des colonnes : {pragma_error}")
                return False
            
            if not id_unite_exists:
                print(f"\n✅ La colonne 'id_unite' n'existe pas dans 'locataires'.")
                print(f"   La migration n'est pas nécessaire.")
                return True
            
            # Vérifier que tous les locataires ont des baux actifs pour leur unité
            print(f"\n🔍 ÉTAPE 4 : Vérification des baux actifs")
            try:
                # Compter les locataires avec id_unite
                result = connection.execute(text("SELECT COUNT(*) FROM locataires WHERE id_unite IS NOT NULL"))
                locataires_with_unite = result.scalar()
                print(f"   - Locataires avec id_unite : {locataires_with_unite}")
                
                # Vérifier que ces locataires ont des baux actifs pour cette unité
                today = datetime.now().date()
                result = connection.execute(text("""
                    SELECT COUNT(*) 
                    FROM locataires l
                    WHERE l.id_unite IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 
                        FROM baux b
                        WHERE b.id_locataire = l.id_locataire
                        AND b.id_unite = l.id_unite
                        AND b.date_debut <= :today
                        AND (b.date_fin IS NULL OR b.date_fin >= :today)
                    )
                """), {"today": today})
                locataires_sans_bail_actif = result.scalar()
                
                if locataires_sans_bail_actif > 0:
                    print(f"\n⚠️ ATTENTION : {locataires_sans_bail_actif} locataires ont une unité mais pas de bail actif pour cette unité.")
                    print(f"   Ces locataires perdront leur lien avec l'unité.")
                    print(f"   Vous devrez créer un bail pour ces locataires après la migration.")
                else:
                    print(f"   ✅ Tous les locataires avec id_unite ont un bail actif pour cette unité.")
            except Exception as check_error:
                print(f"\n❌ ERREUR lors de la vérification des baux : {check_error}")
                import traceback
                traceback.print_exc()
                return False
            
            # ÉTAPE 5 : Supprimer la colonne id_unite
            print(f"\n🔄 ÉTAPE 5 : Suppression de la colonne 'id_unite' de 'locataires'")
            print(f"   ℹ️ SQLite ne permet pas de supprimer directement une colonne")
            print(f"   ℹ️ On doit recréer la table sans cette colonne")
            
            # 1. Renommer l'ancienne table
            try:
                connection.execute(text("ALTER TABLE locataires RENAME TO old_locataires"))
                connection.commit()
                print("   ✅ Table 'locataires' renommée en 'old_locataires'.")
            except Exception as rename_error:
                print(f"\n❌ ERREUR lors du renommage : {rename_error}")
                if backup_file:
                    restore_backup(backup_file)
                return False
            
            # 2. Créer la nouvelle table sans id_unite
            try:
                create_table_sql = text("""
                    CREATE TABLE locataires (
                        id_locataire INTEGER PRIMARY KEY,
                        nom VARCHAR(255) NOT NULL,
                        prenom VARCHAR(255),
                        email VARCHAR(255),
                        telephone VARCHAR(50),
                        statut VARCHAR(50) DEFAULT 'actif',
                        notes TEXT DEFAULT '',
                        date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                        date_modification DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                connection.execute(create_table_sql)
                connection.commit()
                print("   ✅ Nouvelle table 'locataires' créée sans id_unite.")
            except Exception as create_error:
                print(f"\n❌ ERREUR lors de la création de la nouvelle table : {create_error}")
                # Restaurer
                try:
                    connection.execute(text("ALTER TABLE old_locataires RENAME TO locataires"))
                    connection.commit()
                    print(f"   ✅ Table restaurée")
                except:
                    pass
                if backup_file:
                    restore_backup(backup_file)
                return False
            
            # 3. Copier les données (sans id_unite)
            try:
                copy_data_sql = text("""
                    INSERT INTO locataires (
                        id_locataire, nom, prenom, email, telephone, 
                        statut, notes, date_creation, date_modification
                    )
                    SELECT 
                        id_locataire, nom, prenom, email, telephone, 
                        statut, notes, date_creation, date_modification
                    FROM old_locataires
                """)
                result = connection.execute(copy_data_sql)
                copied_count = result.rowcount
                connection.commit()
                print(f"   ✅ {copied_count} locataires copiés vers la nouvelle table.")
            except Exception as copy_error:
                print(f"\n❌ ERREUR lors de la copie des données : {copy_error}")
                # Restaurer
                try:
                    connection.execute(text("DROP TABLE IF EXISTS locataires"))
                    connection.execute(text("ALTER TABLE old_locataires RENAME TO locataires"))
                    connection.commit()
                    print(f"   ✅ Table restaurée")
                except:
                    pass
                if backup_file:
                    restore_backup(backup_file)
                return False
            
            # 4. Recréer les index
            try:
                connection.execute(text("CREATE INDEX IF NOT EXISTS ix_locataires_nom ON locataires(nom)"))
                connection.execute(text("CREATE INDEX IF NOT EXISTS ix_locataires_email ON locataires(email)"))
                connection.commit()
                print("   ✅ Index recréés.")
            except Exception as index_error:
                print(f"\n⚠️ ATTENTION : Erreur lors de la création des index : {index_error}")
            
            # 5. Supprimer l'ancienne table
            try:
                connection.execute(text("DROP TABLE old_locataires"))
                connection.commit()
                print("   ✅ Ancienne table supprimée.")
            except Exception as drop_error:
                print(f"\n⚠️ ATTENTION : Erreur lors de la suppression de l'ancienne table : {drop_error}")
            
            # Vérification finale
            result = connection.execute(text("SELECT COUNT(*) FROM locataires"))
            final_count = result.scalar()
            
            print(f"\n✅ Migration terminée avec succès !")
            print(f"   - {final_count} locataires migrés")
            if backup_file:
                print(f"   - Sauvegarde disponible : {backup_file}")
            
            return True
                
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
        import traceback
        print(f"\n📊 STACK TRACE COMPLET :")
        traceback.print_exc()
        
        if backup_file:
            print(f"\n🔄 TENTATIVE DE RESTAURATION...")
            try:
                restore_backup(backup_file)
                print(f"✅ Restauration réussie")
            except Exception as restore_error:
                print(f"❌ ERREUR lors de la restauration : {restore_error}")
        
        return False

if __name__ == "__main__":
    print("="*70)
    print("MIGRATION : Supprimer id_unite de la table locataires")
    print("="*70)
    
    success = migrate_remove_locataire_id_unite()
    
    print("="*70)
    if success:
        print("✅ Migration réussie !")
    else:
        print("❌ Migration échouée. Vérifiez les erreurs ci-dessus.")
    print("="*70)

