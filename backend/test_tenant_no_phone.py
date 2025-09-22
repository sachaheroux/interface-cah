#!/usr/bin/env python3
"""
Script pour tester la création d'un locataire sans téléphone
"""

import requests
import json

# Configuration
RENDER_API_BASE = "https://interface-cah-backend.onrender.com"

def test_tenant_no_phone():
    """Tester la création d'un locataire sans téléphone"""
    print("🔍 Test de création de locataire sans téléphone...")
    
    # Données du locataire sans téléphone
    tenant_data = {
        "nom": "Test",
        "prenom": "Sans Téléphone",
        "email": "",  # Pas d'email non plus
        "telephone": "",  # Pas de téléphone
        "statut": "actif",
        "id_unite": 2,  # Utiliser une unité existante
        "notes": "Test de création sans téléphone"
    }
    
    print(f"Données du locataire: {tenant_data}")
    
    try:
        response = requests.post(
            f"{RENDER_API_BASE}/api/tenants",
            json=tenant_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Locataire créé avec succès: {result}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_tenant_no_phone()

