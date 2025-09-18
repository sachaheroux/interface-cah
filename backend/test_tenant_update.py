#!/usr/bin/env python3
"""
Script pour tester la mise à jour des locataires
"""

import requests
import json

# Configuration
RENDER_API_BASE = "https://interface-cah-backend.onrender.com"

def test_tenant_update():
    """Tester la mise à jour d'un locataire"""
    print("🔍 Test de mise à jour des locataires...")
    
    # 1. Récupérer un locataire existant
    print("\n1. Récupération des locataires existants:")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/tenants")
        if response.status_code == 200:
            data = response.json()
            tenants = data.get('data', [])
            print(f"   ✅ {len(tenants)} locataires trouvés")
            
            if tenants:
                tenant = tenants[0]
                print(f"   Premier locataire: {tenant.get('nom')} {tenant.get('prenom')} (ID: {tenant.get('id_locataire')})")
                
                # 2. Tester la mise à jour
                print(f"\n2. Test de mise à jour du locataire {tenant.get('id_locataire')}:")
                update_data = {
                    "nom": tenant.get('nom'),
                    "prenom": tenant.get('prenom'),
                    "email": tenant.get('email', ''),
                    "telephone": tenant.get('telephone', ''),
                    "statut": tenant.get('statut', 'actif'),
                    "id_unite": tenant.get('id_unite'),
                    "notes": f"Test de mise à jour - {tenant.get('notes', '')}"
                }
                
                print(f"   Données de mise à jour: {update_data}")
                
                update_response = requests.put(
                    f"{RENDER_API_BASE}/api/tenants/{tenant.get('id_locataire')}",
                    json=update_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"   Status: {update_response.status_code}")
                if update_response.status_code == 200:
                    result = update_response.json()
                    print(f"   ✅ Mise à jour réussie: {result}")
                else:
                    print(f"   ❌ Erreur: {update_response.text}")
            else:
                print("   ❌ Aucun locataire trouvé pour le test")
        else:
            print(f"   ❌ Erreur GET: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_tenant_update()
