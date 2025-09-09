#!/usr/bin/env python3
"""
Script de nettoyage COMPLET - Local + Render
Supprime TOUTES les données partout pour un partage propre
"""

import os
import shutil
import requests
from datetime import datetime

def clean_local_database():
    """Nettoyer la base de données locale"""
    print("🧹 NETTOYAGE LOCAL")
    print("=" * 30)
    
    try:
        # Supprimer complètement le dossier data
        data_dir = "./data"
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
            print("✅ Dossier data local supprimé")
        
        # Recréer le dossier data
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "backups"), exist_ok=True)
        print("✅ Dossier data local recréé")
        
        # Recréer la base de données vide
        from database import init_database
        if init_database():
            print("✅ Base de données locale vide créée")
        else:
            print("❌ Erreur création base locale")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur nettoyage local: {e}")
        return False

def clean_render_database(render_url):
    """Nettoyer la base de données Render"""
    print("\n🌐 NETTOYAGE RENDER")
    print("=" * 30)
    
    try:
        # Supprimer tous les locataires
        print("1️⃣ Suppression des locataires...")
        try:
            response = requests.get(f"{render_url}/api/tenants", timeout=10)
            if response.status_code == 200:
                tenants_data = response.json()
                tenants = tenants_data.get('data', [])
                
                for tenant in tenants:
                    try:
                        delete_response = requests.delete(f"{render_url}/api/tenants/{tenant['id']}", timeout=10)
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
        
        # Supprimer tous les immeubles
        print("2️⃣ Suppression des immeubles...")
        try:
            response = requests.get(f"{render_url}/api/buildings", timeout=10)
            if response.status_code == 200:
                buildings_data = response.json()
                buildings = buildings_data if isinstance(buildings_data, list) else buildings_data.get('data', [])
                
                for building in buildings:
                    try:
                        delete_response = requests.delete(f"{render_url}/api/buildings/{building['id']}", timeout=10)
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
        
        # Supprimer les assignations
        print("3️⃣ Suppression des assignations...")
        try:
            response = requests.get(f"{render_url}/api/assignments", timeout=10)
            if response.status_code == 200:
                assignments_data = response.json()
                assignments = assignments_data.get('data', [])
                
                for assignment in assignments:
                    try:
                        delete_response = requests.delete(f"{render_url}/api/assignments/{assignment['id']}", timeout=10)
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
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur nettoyage Render: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧹 NETTOYAGE COMPLET POUR PARTAGE")
    print("=" * 50)
    print()
    print("⚠️  ATTENTION: Cette opération va supprimer TOUTES les données !")
    print("   - Base de données locale")
    print("   - Base de données Render")
    print("   - Tous les fichiers de données")
    print()
    
    response = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ").lower().strip()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        return
    
    # 1. Nettoyer local
    local_success = clean_local_database()
    
    # 2. Demander l'URL Render
    render_url = input("\nEntrez l'URL de votre application Render (ou 'skip' pour ignorer): ").strip()
    
    if render_url.lower() != 'skip' and render_url:
        if not render_url.startswith('http'):
            render_url = f"https://{render_url}"
        
        render_success = clean_render_database(render_url)
    else:
        render_success = True
        print("⏭️ Nettoyage Render ignoré")
    
    # 3. Résumé
    print("\n🎉 NETTOYAGE TERMINÉ !")
    print("=" * 30)
    
    if local_success:
        print("✅ Base de données locale: Nettoyée")
    else:
        print("❌ Base de données locale: Erreur")
    
    if render_success:
        print("✅ Base de données Render: Nettoyée")
    else:
        print("❌ Base de données Render: Erreur")
    
    if local_success and render_success:
        print("\n🚀 VOTRE APPLICATION EST PRÊTE POUR LE PARTAGE !")
        print("✅ Interface complètement vide")
        print("✅ Prête pour de nouvelles données")
        print("✅ Parfaite pour le partage")
    else:
        print("\n⚠️ Nettoyage partiel - Vérifiez les erreurs ci-dessus")

if __name__ == "__main__":
    main()
