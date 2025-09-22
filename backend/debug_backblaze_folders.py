#!/usr/bin/env python3
"""
Script pour déboguer les dossiers Backblaze B2
Vérifie tous les dossiers et fichiers disponibles
"""

import os
from dotenv import load_dotenv
from storage_service import get_storage_service

# Charger les variables d'environnement
load_dotenv()

def debug_all_folders():
    """Déboguer tous les dossiers Backblaze B2"""
    print("🔍 Debug complet des dossiers Backblaze B2")
    print("=" * 50)
    
    try:
        storage_service = get_storage_service()
        
        # Lister tous les objets dans le bucket (sans préfixe)
        print("📁 Contenu complet du bucket:")
        
        # Utiliser list_objects_v2 pour voir tout
        response = storage_service.s3_client.list_objects_v2(
            Bucket=storage_service.b2_bucket_name
        )
        
        if 'Contents' in response:
            print(f"  📊 Total objets: {len(response['Contents'])}")
            
            # Grouper par dossier
            folders = {}
            for obj in response['Contents']:
                key = obj['Key']
                folder = key.split('/')[0] if '/' in key else 'racine'
                
                if folder not in folders:
                    folders[folder] = []
                
                folders[folder].append({
                    'name': key,
                    'size': obj['Size'],
                    'modified': obj['LastModified']
                })
            
            # Afficher par dossier
            for folder, files in folders.items():
                print(f"\n  📂 Dossier '{folder}': {len(files)} fichiers")
                for file in files:
                    size_kb = file['size'] / 1024
                    print(f"    - {file['name']} ({size_kb:.1f} KB)")
        else:
            print("  ❌ Aucun objet trouvé dans le bucket")
            
    except Exception as e:
        print(f"❌ Erreur lors du debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_all_folders()
