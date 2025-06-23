#!/usr/bin/env python3
"""
Script de test pour vérifier le nouveau chemin de données Render
Utilise /opt/render/project/src/data comme recommandé
"""

import os
import json
from datetime import datetime

# Configuration du chemin de données (même que dans main.py)
DATA_DIR = os.environ.get("DATA_DIR", "/opt/render/project/src/data")
BUILDINGS_DATA_FILE = os.path.join(DATA_DIR, "buildings_data.json")

def test_render_data_path():
    """Test du nouveau chemin de données Render"""
    print("=" * 60)
    print("🧪 TEST NOUVEAU CHEMIN DONNÉES RENDER")
    print("=" * 60)
    
    # Afficher les informations de configuration
    print(f"📂 DATA_DIR (env): {os.environ.get('DATA_DIR', 'NON DÉFINIE')}")
    print(f"📂 DATA_DIR (utilisé): {DATA_DIR}")
    print(f"📄 Fichier de données: {BUILDINGS_DATA_FILE}")
    print(f"💾 Répertoire de travail: {os.getcwd()}")
    
    # Tester la création du répertoire
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        print(f"✅ Répertoire créé/vérifié: {DATA_DIR}")
    except Exception as e:
        print(f"❌ Erreur création répertoire: {e}")
        return False
    
    # Vérifier les permissions
    print(f"📁 Répertoire existe: {os.path.exists(DATA_DIR)}")
    print(f"🔒 Permissions lecture: {os.access(DATA_DIR, os.R_OK)}")
    print(f"🔒 Permissions écriture: {os.access(DATA_DIR, os.W_OK)}")
    
    # Tester l'écriture d'un fichier de test
    test_data = {
        "test": True,
        "timestamp": datetime.now().isoformat(),
        "path": DATA_DIR,
        "buildings": []
    }
    
    try:
        with open(BUILDINGS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Fichier de test écrit avec succès")
    except Exception as e:
        print(f"❌ Erreur écriture fichier: {e}")
        return False
    
    # Tester la lecture du fichier
    try:
        with open(BUILDINGS_DATA_FILE, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        print(f"✅ Fichier de test lu avec succès")
        print(f"📊 Données chargées: {loaded_data.get('timestamp')}")
    except Exception as e:
        print(f"❌ Erreur lecture fichier: {e}")
        return False
    
    # Lister le contenu du répertoire
    try:
        contents = os.listdir(DATA_DIR)
        print(f"🗂️  Contenu du répertoire: {contents}")
    except Exception as e:
        print(f"❌ Erreur listage répertoire: {e}")
    
    print("=" * 60)
    print("✅ TEST TERMINÉ - Nouveau chemin configuré")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_render_data_path() 