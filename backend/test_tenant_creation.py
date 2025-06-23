#!/usr/bin/env python3
import json
import requests
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_tenant_creation():
    print("🧪 Test de création de locataire")
    print("=" * 50)
    
    # Données de test complètes
    tenant_data = {
        "name": "Test Locataire",
        "email": "test@example.com",
        "phone": "(514) 555-9999",
        "status": "active",
        "personalAddress": {
            "street": "123 Rue Test",
            "city": "Montréal",
            "province": "QC",
            "postalCode": "H1A 1A1",
            "country": "Canada"
        },
        "emergencyContact": {
            "name": "Contact Urgence",
            "phone": "(514) 555-8888",
            "email": "urgence@example.com",
            "relationship": "parent"
        },
        "financial": {
            "monthlyIncome": 5000,
            "creditScore": 750,
            "bankAccount": "Banque Test - ****1234",
            "employer": "Entreprise Test",
            "employerPhone": "(514) 555-7777"
        },
        "building": "Immeuble Test",
        "unit": "T-101",
        "notes": "Locataire de test créé par script"
    }
    
    print("📤 Données à envoyer:")
    print(json.dumps(tenant_data, indent=2, ensure_ascii=False))
    print()
    
    try:
        # Test de création
        print("🔄 Envoi de la requête POST...")
        response = requests.post(
            f"{API_BASE_URL}/api/tenants",
            json=tenant_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Création réussie!")
            print("📥 Réponse reçue:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Vérifier que les données sont complètes
            created_tenant = result.get("data", {})
            print("\n🔍 Vérification des données:")
            print(f"  - ID: {created_tenant.get('id')}")
            print(f"  - Nom: {created_tenant.get('name')}")
            print(f"  - Email: {created_tenant.get('email')}")
            print(f"  - Téléphone: {created_tenant.get('phone')}")
            print(f"  - Adresse personnelle: {created_tenant.get('personalAddress')}")
            print(f"  - Contact d'urgence: {created_tenant.get('emergencyContact')}")
            print(f"  - Infos financières: {created_tenant.get('financial')}")
            print(f"  - Notes: {created_tenant.get('notes')}")
            
            return created_tenant.get('id')
            
        else:
            print("❌ Erreur lors de la création")
            print(f"📥 Réponse d'erreur: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("💡 Assurez-vous que le backend est démarré sur http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_get_tenants():
    print("\n🧪 Test de récupération des locataires")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/tenants", timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            tenants = result.get("data", [])
            print(f"✅ {len(tenants)} locataires trouvés")
            
            for i, tenant in enumerate(tenants, 1):
                print(f"\n📋 Locataire {i}:")
                print(f"  - ID: {tenant.get('id')}")
                print(f"  - Nom: {tenant.get('name')}")
                print(f"  - Email: {tenant.get('email')}")
                print(f"  - Statut: {tenant.get('status')}")
                print(f"  - Données complètes: {len(str(tenant))} caractères")
                
        else:
            print("❌ Erreur lors de la récupération")
            print(f"📥 Réponse d'erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_minimal_tenant():
    print("\n🧪 Test de création minimale (nom seulement)")
    print("=" * 50)
    
    minimal_data = {
        "name": "Locataire Minimal"
    }
    
    print("📤 Données minimales:")
    print(json.dumps(minimal_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/tenants",
            json=minimal_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Création minimale réussie!")
            print("📥 Réponse:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ Erreur lors de la création minimale")
            print(f"📥 Réponse d'erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 Démarrage des tests de locataires")
    print("=" * 60)
    
    # Test 1: Récupération des locataires existants
    test_get_tenants()
    
    # Test 2: Création avec toutes les données
    tenant_id = test_tenant_creation()
    
    # Test 3: Création minimale
    test_minimal_tenant()
    
    # Test 4: Récupération après création
    if tenant_id:
        time.sleep(1)  # Attendre un peu
        test_get_tenants()
    
    print("\n�� Tests terminés") 