#!/usr/bin/env python3
"""
Script pour supprimer TOUTES les données proprement
Supprime les données du cloud ET local
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_service import db_service
from sqlalchemy import text

def delete_cloud_data():
    """Supprimer toutes les données du cloud via l'API"""
    print("☁️ SUPPRESSION DES DONNÉES CLOUD")
    print("=" * 40)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        # 1. Supprimer tous les immeubles (cela supprimera aussi les unités, assignations, etc.)
        print("1️⃣ Suppression de tous les immeubles...")
        
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"   📊 {len(buildings)} immeubles trouvés")
            
            for building in buildings:
                building_id = building.get('id')
                if building_id:
                    print(f"   🗑️ Suppression immeuble {building_id}...")
                    delete_response = requests.delete(f"{base_url}/buildings/{building_id}")
                    if delete_response.status_code == 200:
                        print(f"   ✅ Immeuble {building_id} supprimé")
                    else:
                        print(f"   ❌ Erreur suppression immeuble {building_id}: {delete_response.status_code}")
        else:
            print("   ℹ️ Aucun immeuble trouvé")
        
        # 2. Supprimer tous les locataires restants
        print("\n2️⃣ Suppression de tous les locataires...")
        
        tenants_response = requests.get(f"{base_url}/tenants")
        if tenants_response.status_code == 200:
            tenants_data = tenants_response.json()
            if isinstance(tenants_data, dict) and 'data' in tenants_data:
                tenants = tenants_data['data']
            else:
                tenants = tenants_data if isinstance(tenants_data, list) else []
            
            print(f"   📊 {len(tenants)} locataires trouvés")
            
            for tenant in tenants:
                if isinstance(tenant, dict):
                    tenant_id = tenant.get('id')
                    if tenant_id:
                        print(f"   🗑️ Suppression locataire {tenant_id}...")
                        delete_response = requests.delete(f"{base_url}/tenants/{tenant_id}")
                        if delete_response.status_code == 200:
                            print(f"   ✅ Locataire {tenant_id} supprimé")
                        else:
                            print(f"   ❌ Erreur suppression locataire {tenant_id}: {delete_response.status_code}")
        else:
            print("   ℹ️ Aucun locataire trouvé")
        
        # 3. Supprimer toutes les unités restantes
        print("\n3️⃣ Suppression de toutes les unités...")
        
        units_response = requests.get(f"{base_url}/units")
        if units_response.status_code == 200:
            units_data = units_response.json()
            if isinstance(units_data, dict) and 'data' in units_data:
                units = units_data['data']
            else:
                units = units_data if isinstance(units_data, list) else []
            
            print(f"   📊 {len(units)} unités trouvées")
            
            for unit in units:
                if isinstance(unit, dict):
                    unit_id = unit.get('id')
                    if unit_id:
                        print(f"   🗑️ Suppression unité {unit_id}...")
                        delete_response = requests.delete(f"{base_url}/units/{unit_id}")
                        if delete_response.status_code == 200:
                            print(f"   ✅ Unité {unit_id} supprimée")
                        else:
                            print(f"   ❌ Erreur suppression unité {unit_id}: {delete_response.status_code}")
        else:
            print("   ℹ️ Aucune unité trouvée")
        
        # 4. Supprimer toutes les assignations restantes
        print("\n4️⃣ Suppression de toutes les assignations...")
        
        assignments_response = requests.get(f"{base_url}/assignments")
        if assignments_response.status_code == 200:
            assignments_data = assignments_response.json()
            if isinstance(assignments_data, dict) and 'data' in assignments_data:
                assignments = assignments_data['data']
            else:
                assignments = assignments_data if isinstance(assignments_data, list) else []
            
            print(f"   📊 {len(assignments)} assignations trouvées")
            
            for assignment in assignments:
                if isinstance(assignment, dict):
                    assignment_id = assignment.get('id')
                    if assignment_id:
                        print(f"   🗑️ Suppression assignation {assignment_id}...")
                        delete_response = requests.delete(f"{base_url}/assignments/{assignment_id}")
                        if delete_response.status_code == 200:
                            print(f"   ✅ Assignation {assignment_id} supprimée")
                        else:
                            print(f"   ❌ Erreur suppression assignation {assignment_id}: {delete_response.status_code}")
        else:
            print("   ℹ️ Aucune assignation trouvée")
        
        # 5. Supprimer tous les rapports d'immeubles
        print("\n5️⃣ Suppression de tous les rapports d'immeubles...")
        
        building_reports_response = requests.get(f"{base_url}/building-reports")
        if building_reports_response.status_code == 200:
            building_reports = building_reports_response.json()
            print(f"   📊 {len(building_reports)} rapports d'immeubles trouvés")
            
            for report in building_reports:
                if isinstance(report, dict):
                    report_id = report.get('id')
                    if report_id:
                        print(f"   🗑️ Suppression rapport immeuble {report_id}...")
                        delete_response = requests.delete(f"{base_url}/building-reports/{report_id}")
                        if delete_response.status_code == 200:
                            print(f"   ✅ Rapport immeuble {report_id} supprimé")
                        else:
                            print(f"   ❌ Erreur suppression rapport immeuble {report_id}: {delete_response.status_code}")
        else:
            print("   ℹ️ Aucun rapport d'immeuble trouvé")
        
        # 6. Supprimer toutes les factures
        print("\n6️⃣ Suppression de toutes les factures...")
        
        invoices_response = requests.get(f"{base_url}/invoices")
        if invoices_response.status_code == 200:
            invoices = invoices_response.json()
            print(f"   📊 {len(invoices)} factures trouvées")
            
            for invoice in invoices:
                if isinstance(invoice, dict):
                    invoice_id = invoice.get('id')
                    if invoice_id:
                        print(f"   🗑️ Suppression facture {invoice_id}...")
                        delete_response = requests.delete(f"{base_url}/invoices/{invoice_id}")
                        if delete_response.status_code == 200:
                            print(f"   ✅ Facture {invoice_id} supprimée")
                        else:
                            print(f"   ❌ Erreur suppression facture {invoice_id}: {delete_response.status_code}")
        else:
            print("   ℹ️ Aucune facture trouvée")
        
        print("\n   ✅ Suppression cloud terminée")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur suppression cloud: {e}")
        return False

def delete_local_data():
    """Supprimer toutes les données locales"""
    print("\n💻 SUPPRESSION DES DONNÉES LOCALES")
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
        print("   ✅ Suppression locale terminée")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur suppression locale: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def delete_export_files():
    """Supprimer les fichiers d'export temporaires"""
    print("\n🗑️ SUPPRESSION DES FICHIERS TEMPORAIRES")
    print("=" * 40)
    
    files_to_remove = [
        "cah_database_cloud.db",
        "download_cloud_to_local.py"
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

def verify_clean_state():
    """Vérifier que tout est propre"""
    print("\n🔍 VÉRIFICATION DE L'ÉTAT PROPRE")
    print("=" * 40)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        # Vérifier tous les endpoints
        endpoints = [
            ("buildings", "Immeubles"),
            ("tenants", "Locataires"),
            ("units", "Unités"),
            ("assignments", "Assignations"),
            ("building-reports", "Rapports d'immeubles"),
            ("invoices", "Factures")
        ]
        
        all_clean = True
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{base_url}/{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and 'data' in data:
                        count = len(data['data'])
                    else:
                        count = len(data) if isinstance(data, list) else 0
                    
                    if count == 0:
                        print(f"   ✅ {name}: 0 (propre)")
                    else:
                        print(f"   ⚠️ {name}: {count} (données restantes)")
                        all_clean = False
                else:
                    print(f"   ❌ {name}: Erreur {response.status_code}")
                    all_clean = False
            except Exception as e:
                print(f"   ❌ {name}: Erreur - {e}")
                all_clean = False
        
        return all_clean
        
    except Exception as e:
        print(f"   ❌ Erreur vérification: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧹 SUPPRESSION COMPLÈTE DE TOUTES LES DONNÉES")
    print("=" * 60)
    print("⚠️  ATTENTION: Cette opération va supprimer TOUTES les données !")
    print("   - Toutes les données du cloud (Render)")
    print("   - Toutes les données locales")
    print("   - Tous les fichiers temporaires")
    print("=" * 60)
    
    # Demander confirmation
    try:
        confirmation = input("\nÊtes-vous sûr de vouloir tout supprimer ? (tapez 'SUPPRIMER TOUT' pour confirmer): ")
        if confirmation != "SUPPRIMER TOUT":
            print("❌ Opération annulée")
            return False
    except KeyboardInterrupt:
        print("\n❌ Opération annulée")
        return False
    
    # Suppression cloud
    cloud_success = delete_cloud_data()
    
    # Suppression local
    local_success = delete_local_data()
    
    # Suppression fichiers
    delete_export_files()
    
    # Vérification finale
    if cloud_success and local_success:
        print("\n🎉 SUPPRESSION COMPLÈTE RÉUSSIE !")
        print("   Toutes les données ont été supprimées.")
        print("   Vous pouvez maintenant repartir de zéro.")
        
        # Vérification optionnelle
        try:
            verify = input("\nVoulez-vous vérifier que tout est propre ? (y/n): ")
            if verify.lower() == 'y':
                verify_clean_state()
        except KeyboardInterrupt:
            print("\n✅ Suppression terminée")
        
        return True
    else:
        print("\n💥 SUPPRESSION PARTIELLE !")
        print("   Certaines données ont pu être supprimées.")
        print("   Vérifiez manuellement si nécessaire.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
