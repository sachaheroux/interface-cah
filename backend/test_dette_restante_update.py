#!/usr/bin/env python3
"""
Script pour tester la mise à jour de dette_restante directement via l'API
"""

import requests
import json

# URL de l'API Render
API_BASE_URL = "https://interface-cah-backend.onrender.com"

def test_update_dette_restante():
    """Tester la mise à jour de dette_restante"""
    try:
        print("🔍 Test de mise à jour de dette_restante")
        
        # Données de test
        test_data = {
            "nom_immeuble": "Vachon",
            "adresse": "56-58-60-62 rue Vachon",
            "ville": "Trois-Rivières",
            "province": "QC",
            "code_postal": "G8T 1Z7",
            "pays": "Canada",
            "nbr_unite": 4,
            "annee_construction": 2010,
            "prix_achete": 500000,
            "mise_de_fond": 100000,
            "taux_interet": 5,
            "valeur_actuel": 700000,
            "dette_restante": 200000,  # Valeur de test
            "proprietaire": "9250-1121 Québec Inc.",
            "banque": "Desjardins",
            "contracteur": "Construction Andy Héroux",
            "notes": ""
        }
        
        print(f"📤 Envoi des données: {json.dumps(test_data, indent=2)}")
        
        # Mettre à jour l'immeuble ID 1
        response = requests.put(f"{API_BASE_URL}/api/buildings/1", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Mise à jour réussie!")
            print(f"📥 Réponse: {json.dumps(result, indent=2, default=str)}")
            
            # Vérifier la valeur de dette_restante
            if 'dette_restante' in result:
                print(f"🔍 dette_restante dans la réponse: {result['dette_restante']}")
                if result['dette_restante'] == 200000:
                    print("✅ La valeur a été correctement sauvegardée!")
                else:
                    print(f"❌ Problème: attendu 200000, reçu {result['dette_restante']}")
            else:
                print("❌ Le champ dette_restante n'est pas dans la réponse")
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    test_update_dette_restante()
