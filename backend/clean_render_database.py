#!/usr/bin/env python3
"""
Script de nettoyage complet de la base de données sur Render
Supprime TOUTES les données pour un partage propre
"""

import os
import requests
import json
from datetime import datetime

def clean_render_database():
    """Nettoyer complètement la base de données sur Render"""
    print("🧹 NETTOYAGE COMPLET DE LA BASE DE DONNÉES RENDER")
    print("=" * 60)
    
    # URL de votre application Render (à modifier selon votre URL)
    RENDER_URL = input("Entrez l'URL de votre application Render (ex: https://votre-app.onrender.com): ").strip()
    
    if not RENDER_URL:
        print("❌ URL Render requise")
        return False
    
    if not RENDER_URL.startswith('http'):
        RENDER_URL = f"https://{RENDER_URL}"
    
    print(f"🎯 Cible: {RENDER_URL}")
    
    try:
        # 1. Vérifier l'état actuel
        print("\n1️⃣ Vérification de l'état actuel...")
        
        # Vérifier les locataires
        try:
            response = requests.get(f"{RENDER_URL}/api/tenants", timeout=10)
            if response.status_code == 200:
                tenants_data = response.json()
                tenants_count = len(tenants_data.get('data', []))
                print(f"   📊 Locataires actuels: {tenants_count}")
            else:
                print(f"   ❌ Erreur API locataires: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur connexion locataires: {e}")
        
        # Vérifier les immeubles
        try:
            response = requests.get(f"{RENDER_URL}/api/buildings", timeout=10)
            if response.status_code == 200:
                buildings_data = response.json()
                buildings_count = len(buildings_data)
                print(f"   🏢 Immeubles actuels: {buildings_count}")
            else:
                print(f"   ❌ Erreur API immeubles: {response.status_code}")
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
                            print(f"   ✅ Locataire supprimé: {tenant.get('name', 'Inconnu')}")
                        else:
                            print(f"   ❌ Erreur suppression locataire {tenant.get('name', 'Inconnu')}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Erreur suppression locataire {tenant.get('name', 'Inconnu')}: {e}")
            else:
                print(f"   ❌ Impossible de récupérer les locataires: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur lors de la suppression des locataires: {e}")
        
        # 3. Supprimer tous les immeubles
        print("\n3️⃣ Suppression des immeubles...")
        try:
            response = requests.get(f"{RENDER_URL}/api/buildings", timeout=10)
            if response.status_code == 200:
                buildings_data = response.json()
                buildings = buildings_data if isinstance(buildings_data, list) else buildings_data.get('data', [])
                
                for building in buildings:
                    try:
                        delete_response = requests.delete(f"{RENDER_URL}/api/buildings/{building['id']}", timeout=10)
                        if delete_response.status_code == 200:
                            print(f"   ✅ Immeuble supprimé: {building.get('name', 'Inconnu')}")
                        else:
                            print(f"   ❌ Erreur suppression immeuble {building.get('name', 'Inconnu')}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Erreur suppression immeuble {building.get('name', 'Inconnu')}: {e}")
            else:
                print(f"   ❌ Impossible de récupérer les immeubles: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur lors de la suppression des immeubles: {e}")
        
        # 4. Supprimer les assignations
        print("\n4️⃣ Suppression des assignations...")
        try:
            response = requests.get(f"{RENDER_URL}/api/assignments", timeout=10)
            if response.status_code == 200:
                assignments_data = response.json()
                assignments = assignments_data.get('data', [])
                
                for assignment in assignments:
                    try:
                        delete_response = requests.delete(f"{RENDER_URL}/api/assignments/{assignment['id']}", timeout=10)
                        if delete_response.status_code == 200:
                            print(f"   ✅ Assignation supprimée: {assignment.get('id', 'Inconnu')}")
                        else:
                            print(f"   ❌ Erreur suppression assignation {assignment.get('id', 'Inconnu')}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Erreur suppression assignation {assignment.get('id', 'Inconnu')}: {e}")
            else:
                print(f"   ❌ Impossible de récupérer les assignations: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur lors de la suppression des assignations: {e}")
        
        # 5. Vérification finale
        print("\n5️⃣ Vérification finale...")
        
        # Vérifier les locataires
        try:
            response = requests.get(f"{RENDER_URL}/api/tenants", timeout=10)
            if response.status_code == 200:
                tenants_data = response.json()
                tenants_count = len(tenants_data.get('data', []))
                print(f"   📊 Locataires restants: {tenants_count}")
            else:
                print(f"   ❌ Erreur vérification locataires: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur vérification locataires: {e}")
        
        # Vérifier les immeubles
        try:
            response = requests.get(f"{RENDER_URL}/api/buildings", timeout=10)
            if response.status_code == 200:
                buildings_data = response.json()
                buildings_count = len(buildings_data) if isinstance(buildings_data, list) else len(buildings_data.get('data', []))
                print(f"   🏢 Immeubles restants: {buildings_count}")
            else:
                print(f"   ❌ Erreur vérification immeubles: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur vérification immeubles: {e}")
        
        print("\n🎉 NETTOYAGE RENDER TERMINÉ !")
        print("✅ Base de données Render nettoyée")
        print("✅ Prête pour le partage")
        print("✅ Interface vide pour les nouveaux utilisateurs")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage Render: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("🧹 NETTOYAGE COMPLET POUR PARTAGE")
    print("=" * 40)
    print()
    print("⚠️  ATTENTION: Cette opération va supprimer TOUTES les données sur Render !")
    print("   Votre application sera complètement vide après cette opération.")
    print()
    
    response = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ").lower().strip()
    
    if response in ['oui', 'o', 'yes', 'y']:
        success = clean_render_database()
        if success:
            print("\n✅ Nettoyage Render réussi !")
            print("🚀 Votre application est prête pour le partage")
        else:
            print("\n❌ Erreur lors du nettoyage Render")
    else:
        print("\n❌ Opération annulée")

if __name__ == "__main__":
    main()
