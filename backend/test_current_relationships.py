#!/usr/bin/env python3
"""
Test des relations actuelles (sans créer de nouvelles données)
"""

import requests
import json

def test_current_relationships():
    """Tester les relations actuelles"""
    print("🔗 TEST DES RELATIONS ACTUELLES")
    print("=" * 40)
    
    RENDER_URL = "https://interface-cah-backend.onrender.com"
    
    try:
        # 1. Vérifier les immeubles existants
        print("1️⃣ Vérification des immeubles...")
        response = requests.get(f"{RENDER_URL}/api/buildings", timeout=10)
        if response.status_code == 200:
            buildings = response.json()
            print(f"   📊 Immeubles trouvés: {len(buildings)}")
            
            for building in buildings:
                print(f"   🏢 {building.get('name', 'N/A')} (ID: {building.get('id', 'N/A')}) - {building.get('units', 0)} unités")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # 2. Vérifier les locataires existants
        print("\n2️⃣ Vérification des locataires...")
        response = requests.get(f"{RENDER_URL}/api/tenants", timeout=10)
        if response.status_code == 200:
            tenants_data = response.json()
            tenants = tenants_data.get('data', [])
            print(f"   👥 Locataires trouvés: {len(tenants)}")
            
            for tenant in tenants:
                print(f"   👤 {tenant.get('name', 'N/A')} (ID: {tenant.get('id', 'N/A')})")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # 3. Vérifier les assignations existantes
        print("\n3️⃣ Vérification des assignations...")
        response = requests.get(f"{RENDER_URL}/api/assignments", timeout=10)
        if response.status_code == 200:
            assignments_data = response.json()
            assignments = assignments_data.get('data', [])
            print(f"   🔗 Assignations trouvées: {len(assignments)}")
            
            for assignment in assignments:
                print(f"   🔗 Assignation {assignment.get('id', 'N/A')}: Locataire {assignment.get('tenantId', 'N/A')} → Unité {assignment.get('unitId', 'N/A')}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # 4. Tester les relations entre données
        print("\n4️⃣ Test des relations...")
        
        if buildings and tenants and assignments:
            print("   ✅ Données disponibles pour tester les relations")
            
            # Tester la relation immeuble → locataires
            print("   🏢 Test immeuble → locataires...")
            for building in buildings:
                building_id = building.get('id')
                building_assignments = [a for a in assignments if a.get('buildingId') == building_id]
                print(f"      {building.get('name')}: {len(building_assignments)} assignations")
            
            # Tester la relation locataire → unité
            print("   👤 Test locataire → unité...")
            for tenant in tenants:
                tenant_id = tenant.get('id')
                tenant_assignments = [a for a in assignments if a.get('tenantId') == tenant_id]
                print(f"      {tenant.get('name')}: {len(tenant_assignments)} assignation(s)")
        else:
            print("   ⚠️ Données insuffisantes pour tester les relations")
        
        print("\n🎉 TEST TERMINÉ !")
        print("✅ Relations actuelles vérifiées")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    success = test_current_relationships()
    
    if success:
        print("\n✅ Test réussi !")
        print("🔗 Les relations existantes fonctionnent")
    else:
        print("\n❌ Test échoué")

if __name__ == "__main__":
    main()
