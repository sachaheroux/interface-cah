#!/usr/bin/env python3
"""
Script pour supprimer TOUTES les données (cloud + local)
Nettoyage complet pour repartir de zéro
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_service import db_service
from sqlalchemy import text

def clean_cloud_data():
    """Supprimer toutes les données du cloud via l'API"""
    print("☁️ NETTOYAGE DES DONNÉES CLOUD")
    print("=" * 40)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        # 1. Récupérer tous les immeubles
        print("1️⃣ Récupération des immeubles...")
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"   📊 {len(buildings)} immeubles trouvés")
            
            # Supprimer chaque immeuble
            for building in buildings:
                building_id = building.get('id')
                if building_id:
                    delete_response = requests.delete(f"{base_url}/buildings/{building_id}")
                    if delete_response.status_code == 200:
                        print(f"   ✅ Immeuble {building_id} supprimé")
                    else:
                        print(f"   ❌ Erreur suppression immeuble {building_id}")
        else:
            print("   ℹ️ Aucun immeuble à supprimer")
        
        # 2. Récupérer toutes les unités
        print("2️⃣ Récupération des unités...")
        units_response = requests.get(f"{base_url}/units")
        if units_response.status_code == 200:
            units = units_response.json()
            print(f"   📊 {len(units)} unités trouvées")
            
            # Supprimer chaque unité
            for unit in units:
                if isinstance(unit, dict):
                    unit_id = unit.get('id')
                    if unit_id:
                        delete_response = requests.delete(f"{base_url}/units/{unit_id}")
                        if delete_response.status_code == 200:
                            print(f"   ✅ Unité {unit_id} supprimée")
                        else:
                            print(f"   ❌ Erreur suppression unité {unit_id}")
        else:
            print("   ℹ️ Aucune unité à supprimer")
        
        # 3. Récupérer tous les locataires
        print("3️⃣ Récupération des locataires...")
        tenants_response = requests.get(f"{base_url}/tenants")
        if tenants_response.status_code == 200:
            tenants = tenants_response.json()
            print(f"   📊 {len(tenants)} locataires trouvés")
            
            # Supprimer chaque locataire
            for tenant in tenants:
                if isinstance(tenant, dict):
                    tenant_id = tenant.get('id')
                    if tenant_id:
                        delete_response = requests.delete(f"{base_url}/tenants/{tenant_id}")
                        if delete_response.status_code == 200:
                            print(f"   ✅ Locataire {tenant_id} supprimé")
                        else:
                            print(f"   ❌ Erreur suppression locataire {tenant_id}")
        else:
            print("   ℹ️ Aucun locataire à supprimer")
        
        # 4. Récupérer toutes les assignations
        print("4️⃣ Récupération des assignations...")
        assignments_response = requests.get(f"{base_url}/assignments")
        if assignments_response.status_code == 200:
            assignments = assignments_response.json()
            print(f"   📊 {len(assignments)} assignations trouvées")
            
            # Supprimer chaque assignation
            for assignment in assignments:
                if isinstance(assignment, dict):
                    assignment_id = assignment.get('id')
                    if assignment_id:
                        delete_response = requests.delete(f"{base_url}/assignments/{assignment_id}")
                        if delete_response.status_code == 200:
                            print(f"   ✅ Assignation {assignment_id} supprimée")
                        else:
                            print(f"   ❌ Erreur suppression assignation {assignment_id}")
        else:
            print("   ℹ️ Aucune assignation à supprimer")
        
        print("   ✅ Nettoyage cloud terminé")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur nettoyage cloud: {e}")
        return False

def clean_local_data():
    """Supprimer toutes les données locales"""
    print("\n💻 NETTOYAGE DES DONNÉES LOCALES")
    print("=" * 40)
    
    session = db_service.get_session()
    try:
        # 1. Désactiver les contraintes de clés étrangères
        print("1️⃣ Désactivation des contraintes...")
        session.execute(text("PRAGMA foreign_keys = OFF"))
        
        # 2. Supprimer toutes les données
        print("2️⃣ Suppression des données...")
        
        tables = ['invoices', 'unit_reports', 'assignments', 'building_reports', 'units', 'tenants', 'buildings']
        
        for table in tables:
            try:
                result = session.execute(text(f"DELETE FROM {table}"))
                deleted_count = result.rowcount
                print(f"   ✅ Table {table}: {deleted_count} enregistrements supprimés")
            except Exception as e:
                print(f"   ℹ️ Table {table}: {e}")
        
        # 3. Réinitialiser les séquences
        print("3️⃣ Réinitialisation des séquences...")
        try:
            session.execute(text("DELETE FROM sqlite_sequence"))
            print("   ✅ Séquences réinitialisées")
        except Exception as e:
            print(f"   ℹ️ Pas de séquences à réinitialiser: {e}")
        
        # 4. Réactiver les contraintes
        print("4️⃣ Réactivation des contraintes...")
        session.execute(text("PRAGMA foreign_keys = ON"))
        
        # 5. Commit
        session.commit()
        print("   ✅ Nettoyage local terminé")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur nettoyage local: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def clean_export_files():
    """Supprimer les fichiers d'export temporaires"""
    print("\n🗑️ NETTOYAGE DES FICHIERS TEMPORAIRES")
    print("=" * 40)
    
    files_to_remove = [
        "cah_database_cloud.db",
        "export_for_db_browser.py",
        "explore_tables.py",
        "show_table.py",
        "verify_database.py"
    ]
    
    for file in files_to_remove:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"   ✅ Fichier {file} supprimé")
            else:
                print(f"   ℹ️ Fichier {file} n'existait pas")
        except Exception as e:
            print(f"   ❌ Erreur suppression {file}: {e}")

def main():
    """Fonction principale"""
    print("🧹 NETTOYAGE COMPLET - TOUTES LES DONNÉES")
    print("=" * 50)
    print("⚠️  ATTENTION: Cette opération va supprimer TOUTES les données !")
    print("   - Toutes les données du cloud (Render)")
    print("   - Toutes les données locales")
    print("   - Tous les fichiers temporaires")
    print("=" * 50)
    
    # Demander confirmation
    try:
        confirmation = input("\nÊtes-vous sûr de vouloir tout supprimer ? (tapez 'SUPPRIMER TOUT' pour confirmer): ")
        if confirmation != "SUPPRIMER TOUT":
            print("❌ Opération annulée")
            return False
    except KeyboardInterrupt:
        print("\n❌ Opération annulée")
        return False
    
    # Nettoyage cloud
    cloud_success = clean_cloud_data()
    
    # Nettoyage local
    local_success = clean_local_data()
    
    # Nettoyage fichiers
    clean_export_files()
    
    if cloud_success and local_success:
        print("\n🎉 NETTOYAGE COMPLET RÉUSSI !")
        print("   Toutes les données ont été supprimées.")
        print("   Vous pouvez maintenant repartir de zéro.")
        return True
    else:
        print("\n💥 NETTOYAGE PARTIEL !")
        print("   Certaines données ont pu être supprimées.")
        print("   Vérifiez manuellement si nécessaire.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
