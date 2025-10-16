#!/usr/bin/env python3
"""
Script de test pour l'API Construction
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://interface-cah-backend.onrender.com"
CONSTRUCTION_BASE = f"{BASE_URL}/api/construction"

def test_construction_api():
    """Tester l'API construction"""
    print("🏗️ Test de l'API Construction")
    print("=" * 50)
    
    # Test 1: Endpoint de test
    print("\n1️⃣ Test de l'endpoint de test...")
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/test", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test réussi: {data['message']}")
            print(f"📊 Tables disponibles: {len(data['tables'])}")
            for table in data['tables']:
                print(f"   - {table}")
        else:
            print(f"❌ Test échoué: {response.status_code}")
            print(f"   Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    # Test 2: Récupérer les projets (vide au début)
    print("\n2️⃣ Test de récupération des projets...")
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/projets", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Projets récupérés: {len(data['data'])} projets")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 3: Créer un projet de test
    print("\n3️⃣ Test de création d'un projet...")
    try:
        projet_data = {
            "nom": "Projet Test Construction",
            "date_debut": datetime.now().isoformat(),
            "date_fin_prevue": "2024-12-31T23:59:59",
            "notes": "Projet de test pour l'API construction"
        }
        
        response = requests.post(
            f"{CONSTRUCTION_BASE}/projets",
            json=projet_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            projet_id = data['data']['id_projet']
            print(f"✅ Projet créé avec succès: ID {projet_id}")
            print(f"   Nom: {data['data']['nom']}")
            return projet_id
        else:
            print(f"❌ Erreur création: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_crud_operations(projet_id):
    """Tester les opérations CRUD"""
    if not projet_id:
        print("❌ Pas de projet ID pour les tests CRUD")
        return
    
    print(f"\n4️⃣ Test des opérations CRUD pour le projet {projet_id}...")
    
    # Test GET par ID
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/projets/{projet_id}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Projet récupéré: {data['data']['nom']}")
        else:
            print(f"❌ Erreur GET: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur GET: {e}")
    
    # Test UPDATE
    try:
        update_data = {
            "notes": "Projet mis à jour - Test réussi"
        }
        
        response = requests.put(
            f"{CONSTRUCTION_BASE}/projets/{projet_id}",
            json=update_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Projet mis à jour: {data['data']['notes']}")
        else:
            print(f"❌ Erreur UPDATE: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur UPDATE: {e}")
    
    # Test DELETE
    try:
        response = requests.delete(f"{CONSTRUCTION_BASE}/projets/{projet_id}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Projet supprimé: {data['message']}")
        else:
            print(f"❌ Erreur DELETE: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur DELETE: {e}")

def test_other_endpoints():
    """Tester les autres endpoints"""
    print("\n5️⃣ Test des autres endpoints...")
    
    endpoints = [
        ("fournisseurs", "GET"),
        ("matieres-premieres", "GET"),
        ("employes", "GET"),
        ("sous-traitants", "GET")
    ]
    
    for endpoint, method in endpoints:
        try:
            response = requests.get(f"{CONSTRUCTION_BASE}/{endpoint}", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: {len(data['data'])} éléments")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

if __name__ == "__main__":
    print("🚀 Démarrage des tests de l'API Construction")
    print(f"🌐 URL de base: {CONSTRUCTION_BASE}")
    
    # Tests principaux
    projet_id = test_construction_api()
    
    # Tests CRUD
    test_crud_operations(projet_id)
    
    # Tests autres endpoints
    test_other_endpoints()
    
    print("\n" + "=" * 50)
    print("🏁 Tests terminés")
    print("=" * 50)
