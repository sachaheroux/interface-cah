#!/usr/bin/env python3
"""
Test de création de locataires avec le format français
"""

import requests
import json

# URL de l'API Render
API_BASE_URL = "https://interface-cah-backend.onrender.com"

def test_tenant_creation_french():
    """Tester la création de locataires avec le format français"""
    
    print("🧪 Test de création de locataires avec le format français")
    print("=" * 60)
    
    # 1. Récupérer les unités disponibles
    print("\n1️⃣ Récupération des unités disponibles...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/units")
        if response.status_code == 200:
            units_data = response.json()
            units = units_data.get('data', [])
            print(f"✅ {len(units)} unités trouvées")
            
            if not units:
                print("❌ Aucune unité disponible pour le test")
                return
                
            # Afficher les unités disponibles
            for unit in units[:3]:  # Afficher les 3 premières
                print(f"   - ID: {unit.get('id_unite')}, Adresse: {unit.get('adresse_unite')}")
                
            # Utiliser la première unité pour le test
            test_unit = units[0]
            unit_id = test_unit.get('id_unite')
            print(f"   🎯 Utilisation de l'unité ID {unit_id}: {test_unit.get('adresse_unite')}")
            
        else:
            print(f"❌ Erreur lors de la récupération des unités: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des unités: {e}")
        return
    
    # 2. Tester la création d'un locataire avec le format français
    print(f"\n2️⃣ Test de création de locataire pour l'unité {unit_id}...")
    
    tenant_data = {
        "tenant": {
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean.dupont@email.com",
            "telephone": "514-123-4567",
            "statut": "actif",
            "notes": "Test avec format français"
        },
        "assignment": {
            "unitId": unit_id,
            "moveInDate": "2024-01-01",
            "moveOutDate": "",
            "rentAmount": 1200.00,
            "depositAmount": 600.00,
            "leaseStartDate": "2024-01-01",
            "leaseEndDate": "2024-12-31",
            "rentDueDay": 1,
            "notes": "Bail de test"
        }
    }
    
    print(f"📤 Données envoyées:")
    print(f"   - Nom: {tenant_data['tenant']['nom']}")
    print(f"   - Prénom: {tenant_data['tenant']['prenom']}")
    print(f"   - Email: {tenant_data['tenant']['email']}")
    print(f"   - Téléphone: {tenant_data['tenant']['telephone']}")
    print(f"   - Statut: {tenant_data['tenant']['statut']}")
    print(f"   - Unité ID: {tenant_data['assignment']['unitId']}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/tenants/create-with-assignment",
            json=tenant_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Réponse reçue:")
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Locataire créé avec succès!")
            print(f"   - Données: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Vérifier que les données sont bien en français
            if 'data' in result and 'tenant' in result['data']:
                tenant = result['data']['tenant']
                print(f"\n🔍 Vérification du format français:")
                print(f"   - ID: {tenant.get('id_locataire')}")
                print(f"   - Nom: {tenant.get('nom')}")
                print(f"   - Prénom: {tenant.get('prenom')}")
                print(f"   - Email: {tenant.get('email')}")
                print(f"   - Téléphone: {tenant.get('telephone')}")
                print(f"   - Statut: {tenant.get('statut')}")
                print(f"   - ID Unité: {tenant.get('id_unite')}")
                
        else:
            print(f"❌ Erreur lors de la création du locataire:")
            print(f"   - Status: {response.status_code}")
            print(f"   - Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création du locataire: {e}")
    
    # 3. Vérifier que le locataire a été créé
    print(f"\n3️⃣ Vérification de la création...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/tenants")
        if response.status_code == 200:
            tenants_data = response.json()
            tenants = tenants_data.get('data', [])
            print(f"✅ {len(tenants)} locataires trouvés au total")
            
            # Chercher le locataire créé
            created_tenant = None
            for tenant in tenants:
                if (tenant.get('nom') == 'Dupont' and 
                    tenant.get('prenom') == 'Jean' and 
                    tenant.get('email') == 'jean.dupont@email.com'):
                    created_tenant = tenant
                    break
            
            if created_tenant:
                print(f"✅ Locataire trouvé dans la base de données:")
                print(f"   - ID: {created_tenant.get('id_locataire')}")
                print(f"   - Nom complet: {created_tenant.get('nom')} {created_tenant.get('prenom')}")
                print(f"   - Email: {created_tenant.get('email')}")
                print(f"   - Téléphone: {created_tenant.get('telephone')}")
                print(f"   - Statut: {created_tenant.get('statut')}")
                print(f"   - ID Unité: {created_tenant.get('id_unite')}")
            else:
                print(f"❌ Locataire non trouvé dans la base de données")
                
        else:
            print(f"❌ Erreur lors de la récupération des locataires: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

if __name__ == "__main__":
    test_tenant_creation_french()
