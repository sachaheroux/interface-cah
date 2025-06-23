#!/usr/bin/env python3
"""
Script de test pour vérifier la persistance des données
Usage: python test_persistence.py
"""

import os
import json
import sys

# Configuration
DATA_DIR = os.environ.get("DATA_DIR", "./data")
BUILDINGS_DATA_FILE = os.path.join(DATA_DIR, "buildings_data.json")

def test_data_persistence():
    """Test la persistance des données"""
    print("🧪 Test de persistance des données")
    print(f"📂 Répertoire de données: {DATA_DIR}")
    print(f"📄 Fichier de données: {BUILDINGS_DATA_FILE}")
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"✅ Répertoire créé/vérifié: {DATA_DIR}")
    
    # Test d'écriture
    test_data = {
        "buildings": [
            {
                "id": 1,
                "name": "Test Building",
                "type": "Résidentiel",
                "units": 10
            }
        ],
        "next_id": 2
    }
    
    try:
        with open(BUILDINGS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        print("✅ Écriture des données de test réussie")
    except Exception as e:
        print(f"❌ Erreur d'écriture: {e}")
        return False
    
    # Test de lecture
    try:
        with open(BUILDINGS_DATA_FILE, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        print("✅ Lecture des données réussie")
        print(f"📊 Données chargées: {len(loaded_data.get('buildings', []))} immeubles")
    except Exception as e:
        print(f"❌ Erreur de lecture: {e}")
        return False
    
    # Vérification des permissions
    if os.access(DATA_DIR, os.R_OK | os.W_OK):
        print("✅ Permissions de lecture/écriture OK")
    else:
        print("❌ Problème de permissions")
        return False
    
    print("🎉 Test de persistance réussi !")
    return True

def show_environment():
    """Affiche les variables d'environnement importantes"""
    print("\n🔧 Variables d'environnement:")
    print(f"DATA_DIR: {os.environ.get('DATA_DIR', 'Non définie (utilise ./data)')}")
    print(f"PWD: {os.getcwd()}")
    
    if os.path.exists(BUILDINGS_DATA_FILE):
        stat = os.stat(BUILDINGS_DATA_FILE)
        print(f"📄 Fichier existe: {BUILDINGS_DATA_FILE} ({stat.st_size} bytes)")
    else:
        print(f"📄 Fichier n'existe pas encore: {BUILDINGS_DATA_FILE}")

if __name__ == "__main__":
    print("=" * 50)
    print("🏗️  Interface CAH - Test de Persistance")
    print("=" * 50)
    
    show_environment()
    print()
    
    if test_data_persistence():
        print("\n✅ Tous les tests sont passés !")
        sys.exit(0)
    else:
        print("\n❌ Certains tests ont échoué")
        sys.exit(1) 