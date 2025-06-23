#!/usr/bin/env python3
"""
Script de diagnostic pour identifier le problème de disque persistant Render
"""

import os
import json
from datetime import datetime

def test_path(path, description):
    """Tester un chemin spécifique"""
    print(f"\n🧪 Test: {description}")
    print(f"📂 Chemin: {path}")
    
    try:
        # Vérifier si le chemin existe
        exists = os.path.exists(path)
        print(f"📁 Existe: {exists}")
        
        if not exists:
            print("❌ Chemin n'existe pas")
            return False
        
        # Vérifier les permissions
        readable = os.access(path, os.R_OK)
        writable = os.access(path, os.W_OK)
        print(f"🔒 Lecture: {readable}")
        print(f"🔒 Écriture: {writable}")
        
        if not writable:
            print("❌ Pas de permission d'écriture")
            return False
        
        # Tenter d'écrire un fichier de test
        test_file = os.path.join(path, "test_persistence.json")
        test_data = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "path": path
        }
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Vérifier qu'on peut le relire
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        
        print("✅ Écriture/lecture réussie")
        print(f"📄 Fichier test créé: {test_file}")
        
        # Lister le contenu du répertoire
        try:
            contents = os.listdir(path)
            print(f"📋 Contenu: {contents}")
        except:
            print("📋 Contenu: Non accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("🔍 DIAGNOSTIC DISQUE PERSISTANT RENDER")
    print("=" * 50)
    
    # Informations de base
    print(f"💾 Répertoire de travail: {os.getcwd()}")
    print(f"🔧 Variable DATA_DIR: {os.environ.get('DATA_DIR', 'Non définie')}")
    
    # Chemins à tester (basés sur les cas de succès dans la communauté)
    paths_to_test = [
        ("/var/data", "Chemin configuré dans le guide"),
        ("/data", "Chemin alternatif simple"),
        ("/opt/render/project/src/data", "Chemin communauté Render (cas de succès)"),
        ("./data", "Chemin relatif local"),
        ("/tmp/data", "Chemin temporaire (test)"),
    ]
    
    # Créer les répertoires s'ils n'existent pas
    for path, desc in paths_to_test:
        if not path.startswith('./') and not path.startswith('/tmp'):
            try:
                os.makedirs(path, exist_ok=True)
            except:
                pass
    
    successful_paths = []
    
    for path, description in paths_to_test:
        if test_path(path, description):
            successful_paths.append(path)
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS")
    print("=" * 50)
    
    if successful_paths:
        print("✅ Chemins fonctionnels:")
        for path in successful_paths:
            print(f"   - {path}")
        print(f"\n🎯 RECOMMANDATION: Utilisez {successful_paths[0]}")
    else:
        print("❌ Aucun chemin fonctionnel trouvé")
        print("💡 Vérifiez que le disque est bien configuré sur Render")
    
    # Afficher les variables d'environnement importantes
    print("\n🔧 Variables d'environnement:")
    for var in ['DATA_DIR', 'RENDER_SERVICE_NAME', 'RENDER_EXTERNAL_URL']:
        value = os.environ.get(var, 'Non définie')
        print(f"   {var}: {value}")

if __name__ == "__main__":
    main() 