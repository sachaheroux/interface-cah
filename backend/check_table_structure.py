#!/usr/bin/env python3
"""
Script pour vérifier la structure de la table immeubles
"""

import requests
import json

# URL de l'API Render
API_BASE_URL = "https://interface-cah-backend.onrender.com"

def check_table_structure():
    """Vérifier la structure de la table immeubles"""
    try:
        print("🔍 Vérification de la structure de la table immeubles")
        
        # Récupérer un immeuble pour voir tous les champs
        response = requests.get(f"{API_BASE_URL}/api/buildings/1")
        
        if response.status_code == 200:
            building = response.json()
            print("📋 Structure de la table immeubles:")
            print(json.dumps(building, indent=2, default=str))
            
            # Vérifier spécifiquement dette_restante
            if 'dette_restante' in building:
                print(f"✅ Champ 'dette_restante' présent: {building['dette_restante']}")
            else:
                print("❌ Champ 'dette_restante' absent")
                
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

def test_direct_sql():
    """Tester une requête SQL directe pour vérifier la colonne"""
    try:
        print("\n🔍 Test de requête SQL directe")
        
        # Créer un endpoint temporaire pour tester SQL
        test_data = {
            "query": "SELECT column_name FROM information_schema.columns WHERE table_name = 'immeubles' AND column_name = 'dette_restante'"
        }
        
        # Note: Cette approche ne fonctionnera pas car nous n'avons pas d'endpoint SQL direct
        # Mais on peut essayer de créer un endpoint temporaire
        print("⚠️ Impossible de tester SQL directement via l'API")
        
    except Exception as e:
        print(f"❌ Erreur lors du test SQL: {e}")

if __name__ == "__main__":
    check_table_structure()
    test_direct_sql()
