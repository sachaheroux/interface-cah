#!/usr/bin/env python3
"""
Script pour corriger le schéma de base de données sur Render
"""

import requests
import json
from datetime import datetime

# Configuration Render
RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def check_render_database():
    """Vérifier l'état de la base de données sur Render"""
    print("🔍 VÉRIFICATION DE LA BASE DE DONNÉES RENDER")
    print("=" * 50)
    
    try:
        # 1. Vérifier les assignations
        print("\n1. Assignations sur Render:")
        response = requests.get(f"{RENDER_API_URL}/api/assignments")
        if response.status_code == 200:
            data = response.json()
            assignments = data.get('data', [])
            print(f"   ✅ Nombre d'assignations: {len(assignments)}")
            for i, assignment in enumerate(assignments):
                print(f"   Assignation {i+1}: {assignment}")
        else:
            print(f"   ❌ Erreur HTTP {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    try:
        # 2. Vérifier les locataires
        print("\n2. Locataires sur Render:")
        response = requests.get(f"{RENDER_API_URL}/api/tenants")
        if response.status_code == 200:
            data = response.json()
            tenants = data.get('data', [])
            print(f"   ✅ Nombre de locataires: {len(tenants)}")
            for tenant in tenants:
                print(f"   ID: {tenant.get('id')}, Nom: {tenant.get('name')}")
        else:
            print(f"   ❌ Erreur HTTP {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    try:
        # 3. Vérifier les unités
        print("\n3. Unités sur Render:")
        response = requests.get(f"{RENDER_API_URL}/api/units")
        if response.status_code == 200:
            data = response.json()
            units = data.get('data', [])
            print(f"   ✅ Nombre d'unités: {len(units)}")
            for unit in units:
                print(f"   ID: {unit.get('id')}, Adresse: {unit.get('unitAddress')}")
        else:
            print(f"   ❌ Erreur HTTP {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_assignment_creation():
    """Tester la création d'une assignation sur Render"""
    print("\n4. Test de création d'assignation:")
    
    # Données de test
    test_assignment = {
        "unitId": 1,
        "tenantId": 1,
        "moveInDate": "2024-01-01",
        "moveOutDate": None,
        "rentAmount": 1000.0,
        "depositAmount": 500.0,
        "leaseStartDate": "2024-01-01",
        "leaseEndDate": "2024-12-31",
        "rentDueDay": 1,
        "notes": "Test assignment"
    }
    
    try:
        response = requests.post(
            f"{RENDER_API_URL}/api/assignments",
            json=test_assignment,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Assignation créée: {response.json()}")
        else:
            print(f"   ❌ Erreur: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

if __name__ == "__main__":
    check_render_database()
    test_assignment_creation()
