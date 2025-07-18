#!/usr/bin/env python3
"""
Script de test pour vérifier le système d'assignations locataires-unités
Usage: python test_assignments.py
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_assignments_system():
    """Test complet du système d'assignations"""
    print("🧪 Test du système d'assignations locataires-unités")
    print("=" * 60)
    
    # Test 1: Vérifier que l'API est accessible
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ API accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ API non accessible: {e}")
        return False
    
    # Test 2: Récupérer les assignations existantes
    try:
        response = requests.get(f"{BASE_URL}/api/assignments")
        assignments = response.json()
        print(f"✅ Assignations récupérées: {len(assignments.get('data', []))} assignations")
    except Exception as e:
        print(f"❌ Erreur récupération assignations: {e}")
        return False
    
    # Test 3: Créer une assignation de test
    test_assignment = {
        "unitId": "test-unit-1",
        "tenantId": 999,
        "tenantData": {
            "name": "Test Locataire",
            "email": "test@example.com",
            "phone": "(514) 555-0000"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/assignments",
            json=test_assignment,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            created_assignment = response.json()
            assignment_id = created_assignment['data']['id']
            print(f"✅ Assignation créée: ID {assignment_id}")
        else:
            print(f"❌ Erreur création assignation: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur création assignation: {e}")
        return False
    
    # Test 4: Récupérer l'assignation par locataire
    try:
        response = requests.get(f"{BASE_URL}/api/assignments/tenant/999")
        tenant_assignment = response.json()
        
        if tenant_assignment['data']:
            print(f"✅ Assignation trouvée pour le locataire 999")
        else:
            print(f"❌ Aucune assignation trouvée pour le locataire 999")
    except Exception as e:
        print(f"❌ Erreur récupération assignation locataire: {e}")
    
    # Test 5: Récupérer les assignations par unité
    try:
        response = requests.get(f"{BASE_URL}/api/assignments/unit/test-unit-1")
        unit_assignments = response.json()
        
        if len(unit_assignments.get('data', [])) > 0:
            print(f"✅ Assignations trouvées pour l'unité test-unit-1: {len(unit_assignments['data'])}")
        else:
            print(f"❌ Aucune assignation trouvée pour l'unité test-unit-1")
    except Exception as e:
        print(f"❌ Erreur récupération assignations unité: {e}")
    
    # Test 6: Supprimer l'assignation de test
    try:
        response = requests.delete(f"{BASE_URL}/api/assignments/tenant/999")
        
        if response.status_code == 200:
            print(f"✅ Assignation supprimée pour le locataire 999")
        else:
            print(f"❌ Erreur suppression assignation: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur suppression assignation: {e}")
    
    # Test 7: Vérifier que l'assignation a été supprimée
    try:
        response = requests.get(f"{BASE_URL}/api/assignments/tenant/999")
        tenant_assignment = response.json()
        
        if not tenant_assignment['data']:
            print(f"✅ Assignation correctement supprimée")
        else:
            print(f"❌ Assignation toujours présente après suppression")
    except Exception as e:
        print(f"❌ Erreur vérification suppression: {e}")
    
    print("=" * 60)
    print("🎉 Tests d'assignations terminés !")
    return True

def test_integration_with_existing_data():
    """Test l'intégration avec les données existantes"""
    print("\n🔗 Test d'intégration avec les données existantes")
    print("=" * 60)
    
    # Récupérer les locataires existants
    try:
        response = requests.get(f"{BASE_URL}/api/tenants")
        tenants = response.json().get('data', [])
        print(f"📋 Locataires disponibles: {len(tenants)}")
        
        if tenants:
            tenant = tenants[0]
            print(f"   → Locataire test: {tenant.get('name', 'N/A')} (ID: {tenant.get('id')})")
    except Exception as e:
        print(f"❌ Erreur récupération locataires: {e}")
        return False
    
    # Récupérer les immeubles existants
    try:
        response = requests.get(f"{BASE_URL}/api/buildings")
        buildings = response.json().get('data', [])
        print(f"🏢 Immeubles disponibles: {len(buildings)}")
        
        if buildings:
            building = buildings[0]
            print(f"   → Immeuble test: {building.get('name', 'N/A')} (ID: {building.get('id')})")
    except Exception as e:
        print(f"❌ Erreur récupération immeubles: {e}")
        return False
    
    print("✅ Intégration testée avec succès")
    return True

if __name__ == "__main__":
    print("🚀 Démarrage des tests d'assignations")
    print("Assurez-vous que le backend est démarré sur http://localhost:8000")
    print()
    
    success = test_assignments_system()
    if success:
        test_integration_with_existing_data()
    
    print("\n✨ Tests terminés !") 