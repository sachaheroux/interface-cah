#!/usr/bin/env python3
"""
Script pour supprimer TOUTES les données de la base de données
Inclut : immeubles, locataires, assignations, rapports, factures, employés, projets
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def clean_local_database():
    """Nettoyer la base de données locale"""
    print("🧹 NETTOYAGE COMPLET DE LA BASE DE DONNÉES LOCALE")
    print("=" * 60)
    
    try:
        # 1. Supprimer tous les immeubles
        print("1️⃣ Suppression des immeubles...")
        response = requests.get(f"{API_BASE_URL}/api/buildings")
        if response.status_code == 200:
            data = response.json()
            buildings = data.get('data', []) if isinstance(data, dict) else data
            for building in buildings:
                try:
                    requests.delete(f"{API_BASE_URL}/api/buildings/{building['id']}")
                    print(f"   ✅ Immeuble {building['id']} supprimé")
                except:
                    print(f"   ❌ Erreur immeuble {building['id']}")
        
        # 2. Supprimer tous les locataires
        print("\n2️⃣ Suppression des locataires...")
        response = requests.get(f"{API_BASE_URL}/api/tenants")
        if response.status_code == 200:
            data = response.json()
            tenants = data.get('data', []) if isinstance(data, dict) else data
            for tenant in tenants:
                try:
                    requests.delete(f"{API_BASE_URL}/api/tenants/{tenant['id']}")
                    print(f"   ✅ Locataire {tenant['id']} supprimé")
                except:
                    print(f"   ❌ Erreur locataire {tenant['id']}")
        
        # 3. Supprimer toutes les assignations
        print("\n3️⃣ Suppression des assignations...")
        response = requests.get(f"{API_BASE_URL}/api/assignments")
        if response.status_code == 200:
            data = response.json()
            assignments = data.get('data', []) if isinstance(data, dict) else data
            for assignment in assignments:
                try:
                    requests.delete(f"{API_BASE_URL}/api/assignments/{assignment['id']}")
                    print(f"   ✅ Assignation {assignment['id']} supprimée")
                except:
                    print(f"   ❌ Erreur assignation {assignment['id']}")
        
        # 4. Supprimer tous les employés
        print("\n4️⃣ Suppression des employés...")
        response = requests.get(f"{API_BASE_URL}/api/employees")
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', []) if isinstance(data, dict) else data
            for employee in employees:
                try:
                    requests.delete(f"{API_BASE_URL}/api/employees/{employee['id']}")
                    print(f"   ✅ Employé {employee['id']} supprimé")
                except:
                    print(f"   ❌ Erreur employé {employee['id']}")
        
        # 5. Supprimer tous les projets
        print("\n5️⃣ Suppression des projets...")
        response = requests.get(f"{API_BASE_URL}/api/projects")
        if response.status_code == 200:
            data = response.json()
            projects = data.get('data', []) if isinstance(data, dict) else data
            for project in projects:
                try:
                    requests.delete(f"{API_BASE_URL}/api/projects/{project['id']}")
                    print(f"   ✅ Projet {project['id']} supprimé")
                except:
                    print(f"   ❌ Erreur projet {project['id']}")
        
        # 6. Supprimer tous les rapports d'immeubles
        print("\n6️⃣ Suppression des rapports d'immeubles...")
        try:
            response = requests.get(f"{API_BASE_URL}/api/building-reports")
            if response.status_code == 200:
                data = response.json()
                reports = data.get('data', []) if isinstance(data, dict) else data
                for report in reports:
                    try:
                        requests.delete(f"{API_BASE_URL}/api/building-reports/{report['id']}")
                        print(f"   ✅ Rapport immeuble {report['id']} supprimé")
                    except:
                        print(f"   ❌ Erreur rapport immeuble {report['id']}")
        except:
            print("   ⚠️ Aucun rapport d'immeuble à supprimer")
        
        # 7. Supprimer tous les rapports d'unités
        print("\n7️⃣ Suppression des rapports d'unités...")
        try:
            response = requests.get(f"{API_BASE_URL}/api/unit-reports")
            if response.status_code == 200:
                data = response.json()
                reports = data.get('data', []) if isinstance(data, dict) else data
                for report in reports:
                    try:
                        requests.delete(f"{API_BASE_URL}/api/unit-reports/{report['id']}")
                        print(f"   ✅ Rapport unité {report['id']} supprimé")
                    except:
                        print(f"   ❌ Erreur rapport unité {report['id']}")
        except:
            print("   ⚠️ Aucun rapport d'unité à supprimer")
        
        # 8. Supprimer toutes les factures
        print("\n8️⃣ Suppression des factures...")
        try:
            response = requests.get(f"{API_BASE_URL}/api/invoices")
            if response.status_code == 200:
                data = response.json()
                invoices = data.get('data', []) if isinstance(data, dict) else data
                for invoice in invoices:
                    try:
                        requests.delete(f"{API_BASE_URL}/api/invoices/{invoice['id']}")
                        print(f"   ✅ Facture {invoice['id']} supprimée")
                    except:
                        print(f"   ❌ Erreur facture {invoice['id']}")
        except:
            print("   ⚠️ Aucune facture à supprimer")
        
        print("\n🎉 NETTOYAGE LOCAL TERMINÉ !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage local: {e}")
        return False

def clean_render_database():
    """Nettoyer la base de données Render"""
    print("\n🌐 NETTOYAGE DE LA BASE DE DONNÉES RENDER")
    print("=" * 60)
    
    try:
        # 1. Supprimer tous les immeubles
        print("1️⃣ Suppression des immeubles...")
        response = requests.get(f"{RENDER_API_URL}/api/buildings")
        if response.status_code == 200:
            data = response.json()
            buildings = data.get('data', []) if isinstance(data, dict) else data
            for building in buildings:
                try:
                    requests.delete(f"{RENDER_API_URL}/api/buildings/{building['id']}")
                    print(f"   ✅ Immeuble {building['id']} supprimé")
                except:
                    print(f"   ❌ Erreur immeuble {building['id']}")
        
        # 2. Supprimer tous les locataires
        print("\n2️⃣ Suppression des locataires...")
        response = requests.get(f"{RENDER_API_URL}/api/tenants")
        if response.status_code == 200:
            data = response.json()
            tenants = data.get('data', []) if isinstance(data, dict) else data
            for tenant in tenants:
                try:
                    requests.delete(f"{RENDER_API_URL}/api/tenants/{tenant['id']}")
                    print(f"   ✅ Locataire {tenant['id']} supprimé")
                except:
                    print(f"   ❌ Erreur locataire {tenant['id']}")
        
        # 3. Supprimer toutes les assignations
        print("\n3️⃣ Suppression des assignations...")
        response = requests.get(f"{RENDER_API_URL}/api/assignments")
        if response.status_code == 200:
            data = response.json()
            assignments = data.get('data', []) if isinstance(data, dict) else data
            for assignment in assignments:
                try:
                    requests.delete(f"{RENDER_API_URL}/api/assignments/{assignment['id']}")
                    print(f"   ✅ Assignation {assignment['id']} supprimée")
                except:
                    print(f"   ❌ Erreur assignation {assignment['id']}")
        
        # 4. Supprimer tous les employés
        print("\n4️⃣ Suppression des employés...")
        response = requests.get(f"{RENDER_API_URL}/api/employees")
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', []) if isinstance(data, dict) else data
            for employee in employees:
                try:
                    requests.delete(f"{RENDER_API_URL}/api/employees/{employee['id']}")
                    print(f"   ✅ Employé {employee['id']} supprimé")
                except:
                    print(f"   ❌ Erreur employé {employee['id']}")
        
        # 5. Supprimer tous les projets
        print("\n5️⃣ Suppression des projets...")
        response = requests.get(f"{RENDER_API_URL}/api/projects")
        if response.status_code == 200:
            data = response.json()
            projects = data.get('data', []) if isinstance(data, dict) else data
            for project in projects:
                try:
                    requests.delete(f"{RENDER_API_URL}/api/projects/{project['id']}")
                    print(f"   ✅ Projet {project['id']} supprimé")
                except:
                    print(f"   ❌ Erreur projet {project['id']}")
        
        print("\n🎉 NETTOYAGE RENDER TERMINÉ !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage Render: {e}")
        return False

def verify_cleanup():
    """Vérifier que tout est bien supprimé"""
    print("\n🔍 VÉRIFICATION FINALE")
    print("=" * 60)
    
    try:
        # Vérifier local
        print("📊 Base de données locale:")
        response = requests.get(f"{API_BASE_URL}/api/buildings")
        if response.status_code == 200:
            data = response.json()
            buildings = data.get('data', []) if isinstance(data, dict) else data
        else:
            buildings = []
        print(f"   Immeubles restants: {len(buildings)}")
        
        response = requests.get(f"{API_BASE_URL}/api/tenants")
        if response.status_code == 200:
            data = response.json()
            tenants = data.get('data', []) if isinstance(data, dict) else data
        else:
            tenants = []
        print(f"   Locataires restants: {len(tenants)}")
        
        response = requests.get(f"{API_BASE_URL}/api/employees")
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', []) if isinstance(data, dict) else data
        else:
            employees = []
        print(f"   Employés restants: {len(employees)}")
        
        response = requests.get(f"{API_BASE_URL}/api/projects")
        if response.status_code == 200:
            data = response.json()
            projects = data.get('data', []) if isinstance(data, dict) else data
        else:
            projects = []
        print(f"   Projets restants: {len(projects)}")
        
        # Vérifier Render
        print("\n🌐 Base de données Render:")
        response = requests.get(f"{RENDER_API_URL}/api/buildings")
        if response.status_code == 200:
            data = response.json()
            buildings_render = data.get('data', []) if isinstance(data, dict) else data
        else:
            buildings_render = []
        print(f"   Immeubles restants: {len(buildings_render)}")
        
        response = requests.get(f"{RENDER_API_URL}/api/tenants")
        if response.status_code == 200:
            data = response.json()
            tenants_render = data.get('data', []) if isinstance(data, dict) else data
        else:
            tenants_render = []
        print(f"   Locataires restants: {len(tenants_render)}")
        
        response = requests.get(f"{RENDER_API_URL}/api/employees")
        if response.status_code == 200:
            data = response.json()
            employees_render = data.get('data', []) if isinstance(data, dict) else data
        else:
            employees_render = []
        print(f"   Employés restants: {len(employees_render)}")
        
        response = requests.get(f"{RENDER_API_URL}/api/projects")
        if response.status_code == 200:
            data = response.json()
            projects_render = data.get('data', []) if isinstance(data, dict) else data
        else:
            projects_render = []
        print(f"   Projets restants: {len(projects_render)}")
        
        total_remaining = len(buildings) + len(tenants) + len(employees) + len(projects) + len(buildings_render) + len(tenants_render) + len(employees_render) + len(projects_render)
        
        if total_remaining == 0:
            print("\n✅ SUCCÈS ! Toutes les données bidon supprimées")
            print("🚀 Votre application est complètement vide et prête pour le partage")
        else:
            print(f"\n⚠️ Il reste {total_remaining} éléments à supprimer")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

if __name__ == "__main__":
    print("🧹 NETTOYAGE COMPLET DE TOUTES LES DONNÉES BIDON")
    print("=" * 60)
    print("⚠️  ATTENTION: Cette opération va supprimer TOUTES les données !")
    print("   - Immeubles, Locataires, Assignations")
    print("   - Employés, Projets")
    print("   - Rapports, Factures")
    print("   - Local ET Render")
    print()
    
    confirm = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ").lower().strip()
    
    if confirm in ['oui', 'o', 'yes', 'y']:
        # Nettoyer local
        local_success = clean_local_database()
        
        # Nettoyer Render
        render_success = clean_render_database()
        
        # Vérifier
        verify_cleanup()
        
        if local_success and render_success:
            print("\n🎉 NETTOYAGE COMPLET TERMINÉ !")
        else:
            print("\n⚠️ Nettoyage partiel - vérifiez les erreurs ci-dessus")
    else:
        print("❌ Nettoyage annulé")
