#!/usr/bin/env python3
"""
Test de debug pour la création de locataire avec bail
"""

import requests
import json

# URL de l'API Render
API_BASE_URL = "https://interface-cah-backend.onrender.com"

def test_debug_lease_creation():
    """Tester la création de locataire avec bail avec debug"""
    
    print("🧪 Test de debug pour la création de locataire avec bail")
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
                
            # Utiliser la première unité pour le test
            test_unit = units[0]
            unit_id = test_unit.get('id_unite')
            print(f"   🎯 Utilisation de l'unité ID {unit_id}: {test_unit.get('adresse_unite')}")
            
        else:
            print(f"❌ Erreur lors de la récupération des unités: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des unités: {e}")
        return
    
    # 2. Tester la création d'un locataire avec bail
    print(f"\n2️⃣ Test de création de locataire avec bail pour l'unité {unit_id}...")
    
    # Données exactement comme le frontend les envoie
    tenant_data = {
        "tenant": {
            "nom": "Test",
            "prenom": "Debug",
            "email": "debug@test.com",
            "telephone": "514-555-9999",
            "statut": "actif",
            "notes": "Test de debug"
        },
        "lease": {
            "unitId": unit_id,
            "moveInDate": "2024-01-01",
            "moveOutDate": "2024-12-31",
            "rentAmount": 1500.00,
            "depositAmount": 0,
            "leaseStartDate": "2024-01-01",
            "leaseEndDate": "2024-12-31",
            "rentDueDay": 1,
            "notes": "Test de debug",
            "paymentMethod": "Virement bancaire",
            "pdfLease": ""
        }
    }
    
    print(f"📤 Données envoyées:")
    print(f"   - Nom: {tenant_data['tenant']['nom']}")
    print(f"   - Prénom: {tenant_data['tenant']['prenom']}")
    print(f"   - Email: {tenant_data['tenant']['email']}")
    print(f"   - Téléphone: {tenant_data['tenant']['telephone']}")
    print(f"   - Statut: {tenant_data['tenant']['statut']}")
    print(f"   - Unité ID: {tenant_data['lease']['unitId']}")
    print(f"   - Loyer: {tenant_data['lease']['rentAmount']}$/mois")
    print(f"   - Date début: {tenant_data['lease']['leaseStartDate']}")
    print(f"   - Date fin: {tenant_data['lease']['leaseEndDate']}")
    print(f"   - Méthode paiement: {tenant_data['lease']['paymentMethod']}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/tenants/create-with-lease",
            json=tenant_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Réponse reçue:")
        print(f"   - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Locataire et bail créés avec succès!")
            print(f"   - Données: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
        else:
            print(f"❌ Erreur lors de la création:")
            print(f"   - Status: {response.status_code}")
            print(f"   - Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")

if __name__ == "__main__":
    test_debug_lease_creation()
