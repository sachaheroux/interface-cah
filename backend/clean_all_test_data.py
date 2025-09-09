#!/usr/bin/env python3
"""
Script de nettoyage de TOUTES les données bidon
Supprime les données de test des sous-traitants, projets, etc.
"""

import requests
import time

def clean_all_test_data():
    """Nettoyer toutes les données bidon"""
    print("🧹 NETTOYAGE DE TOUTES LES DONNÉES BIDON")
    print("=" * 50)
    
    RENDER_URL = "https://interface-cah-backend.onrender.com"
    
    try:
        # 1. Supprimer tous les immeubles
        print("1️⃣ Suppression des immeubles...")
        try:
            response = requests.get(f"{RENDER_URL}/api/buildings", timeout=10)
            if response.status_code == 200:
                buildings = response.json()
                for building in buildings:
                    try:
                        delete_response = requests.delete(f"{RENDER_URL}/api/buildings/{building['id']}", timeout=10)
                        if delete_response.status_code == 200:
                            print(f"   ✅ {building.get('name', 'Inconnu')}")
                        else:
                            print(f"   ❌ Erreur {building.get('name', 'Inconnu')}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Erreur {building.get('name', 'Inconnu')}: {e}")
            else:
                print(f"   ❌ Impossible de récupérer les immeubles: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur connexion immeubles: {e}")
        
        # 2. Supprimer tous les locataires
        print("\n2️⃣ Suppression des locataires...")
        try:
            response = requests.get(f"{RENDER_URL}/api/tenants", timeout=10)
            if response.status_code == 200:
                tenants_data = response.json()
                tenants = tenants_data.get('data', [])
                for tenant in tenants:
                    try:
                        delete_response = requests.delete(f"{RENDER_URL}/api/tenants/{tenant['id']}", timeout=10)
                        if delete_response.status_code == 200:
                            print(f"   ✅ {tenant.get('name', 'Inconnu')}")
                        else:
                            print(f"   ❌ Erreur {tenant.get('name', 'Inconnu')}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Erreur {tenant.get('name', 'Inconnu')}: {e}")
            else:
                print(f"   ❌ Impossible de récupérer les locataires: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur connexion locataires: {e}")
        
        # 3. Supprimer toutes les assignations
        print("\n3️⃣ Suppression des assignations...")
        try:
            response = requests.get(f"{RENDER_URL}/api/assignments", timeout=10)
            if response.status_code == 200:
                assignments_data = response.json()
                assignments = assignments_data.get('data', [])
                for assignment in assignments:
                    try:
                        delete_response = requests.delete(f"{RENDER_URL}/api/assignments/{assignment['id']}", timeout=10)
                        if delete_response.status_code == 200:
                            print(f"   ✅ Assignation {assignment.get('id', 'Inconnu')}")
                        else:
                            print(f"   ❌ Erreur assignation {assignment.get('id', 'Inconnu')}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Erreur assignation {assignment.get('id', 'Inconnu')}: {e}")
            else:
                print(f"   ❌ Impossible de récupérer les assignations: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur connexion assignations: {e}")
        
        # 4. Supprimer tous les rapports d'immeubles
        print("\n4️⃣ Suppression des rapports d'immeubles...")
        try:
            response = requests.get(f"{RENDER_URL}/api/building-reports", timeout=10)
            if response.status_code == 200:
                reports_data = response.json()
                reports = reports_data.get('data', [])
                for report in reports:
                    try:
                        delete_response = requests.delete(f"{RENDER_URL}/api/building-reports/{report['id']}", timeout=10)
                        if delete_response.status_code == 200:
                            print(f"   ✅ Rapport {report.get('id', 'Inconnu')}")
                        else:
                            print(f"   ❌ Erreur rapport {report.get('id', 'Inconnu')}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Erreur rapport {report.get('id', 'Inconnu')}: {e}")
            else:
                print(f"   ❌ Impossible de récupérer les rapports: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur connexion rapports: {e}")
        
        # 5. Supprimer tous les rapports d'unités
        print("\n5️⃣ Suppression des rapports d'unités...")
        try:
            response = requests.get(f"{RENDER_URL}/api/unit-reports", timeout=10)
            if response.status_code == 200:
                reports_data = response.json()
                reports = reports_data.get('data', [])
                for report in reports:
                    try:
                        delete_response = requests.delete(f"{RENDER_URL}/api/unit-reports/{report['id']}", timeout=10)
                        if delete_response.status_code == 200:
                            print(f"   ✅ Rapport unité {report.get('id', 'Inconnu')}")
                        else:
                            print(f"   ❌ Erreur rapport unité {report.get('id', 'Inconnu')}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Erreur rapport unité {report.get('id', 'Inconnu')}: {e}")
            else:
                print(f"   ❌ Impossible de récupérer les rapports d'unités: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur connexion rapports d'unités: {e}")
        
        # 6. Supprimer toutes les factures
        print("\n6️⃣ Suppression des factures...")
        try:
            response = requests.get(f"{RENDER_URL}/api/invoices", timeout=10)
            if response.status_code == 200:
                invoices_data = response.json()
                invoices = invoices_data.get('data', [])
                for invoice in invoices:
                    try:
                        delete_response = requests.delete(f"{RENDER_URL}/api/invoices/{invoice['id']}", timeout=10)
                        if delete_response.status_code == 200:
                            print(f"   ✅ Facture {invoice.get('id', 'Inconnu')}")
                        else:
                            print(f"   ❌ Erreur facture {invoice.get('id', 'Inconnu')}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Erreur facture {invoice.get('id', 'Inconnu')}: {e}")
            else:
                print(f"   ❌ Impossible de récupérer les factures: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur connexion factures: {e}")
        
        # 7. Vérification finale
        print("\n7️⃣ Vérification finale...")
        
        # Vérifier les immeubles
        try:
            response = requests.get(f"{RENDER_URL}/api/buildings", timeout=10)
            if response.status_code == 200:
                buildings = response.json()
                print(f"   📊 Immeubles restants: {len(buildings)}")
            else:
                print(f"   ❌ Erreur vérification immeubles: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur vérification immeubles: {e}")
        
        # Vérifier les locataires
        try:
            response = requests.get(f"{RENDER_URL}/api/tenants", timeout=10)
            if response.status_code == 200:
                tenants_data = response.json()
                tenants = tenants_data.get('data', [])
                print(f"   👥 Locataires restants: {len(tenants)}")
            else:
                print(f"   ❌ Erreur vérification locataires: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur vérification locataires: {e}")
        
        print("\n🎉 NETTOYAGE TERMINÉ !")
        print("✅ Toutes les données bidon supprimées")
        print("✅ Application complètement vide")
        print("✅ Prête pour le partage")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧹 NETTOYAGE DE TOUTES LES DONNÉES BIDON")
    print("=" * 50)
    print()
    print("⚠️  ATTENTION: Cette opération va supprimer TOUTES les données !")
    print("   - Immeubles")
    print("   - Locataires")
    print("   - Assignations")
    print("   - Rapports")
    print("   - Factures")
    print()
    
    response = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ").lower().strip()
    
    if response in ['oui', 'o', 'yes', 'y']:
        success = clean_all_test_data()
        if success:
            print("\n✅ Nettoyage réussi !")
            print("🚀 Votre application est prête pour le partage")
        else:
            print("\n❌ Erreur lors du nettoyage")
    else:
        print("\n❌ Opération annulée")

if __name__ == "__main__":
    main()
