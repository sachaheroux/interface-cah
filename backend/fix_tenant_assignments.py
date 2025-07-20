#!/usr/bin/env python3
"""
Script pour corriger le problème d'assignation en supprimant et recréant le locataire
Usage: python fix_tenant_assignments.py
"""

import json
import os
import requests
from datetime import datetime

# Configuration
DATA_DIR = os.environ.get("DATA_DIR", "./data")
ASSIGNMENTS_DATA_FILE = os.path.join(DATA_DIR, "assignments_data.json")
TENANTS_DATA_FILE = os.path.join(DATA_DIR, "tenants_data.json")
API_BASE_URL = "http://localhost:8000"

def load_json_file(file_path):
    """Charger un fichier JSON"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Erreur chargement {file_path}: {e}")
    return None

def save_json_file(file_path, data):
    """Sauvegarder un fichier JSON"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde {file_path}: {e}")
        return False

def fix_tenant_assignments():
    """Corriger le problème d'assignation"""
    print("🔧 Correction du problème d'assignation")
    print("=" * 60)
    
    # Charger les données
    assignments_data = load_json_file(ASSIGNMENTS_DATA_FILE)
    tenants_data = load_json_file(TENANTS_DATA_FILE)
    
    if not assignments_data or not tenants_data:
        print("❌ Impossible de charger les données")
        return
    
    print(f"📊 Assignations totales: {len(assignments_data.get('assignments', []))}")
    print(f"📊 Locataires totaux: {len(tenants_data.get('tenants', []))}")
    
    # Trouver l'assignation problématique
    problematic_assignment = None
    for assignment in assignments_data.get("assignments", []):
        if assignment.get("tenantId") == 1752878177987:
            problematic_assignment = assignment
            break
    
    if not problematic_assignment:
        print("✅ Aucune assignation problématique trouvée")
        return
    
    print(f"❌ Assignation problématique trouvée: {problematic_assignment}")
    
    # Supprimer l'assignation problématique
    assignments_data["assignments"] = [
        a for a in assignments_data.get("assignments", [])
        if a.get("tenantId") != 1752878177987
    ]
    
    if save_json_file(ASSIGNMENTS_DATA_FILE, assignments_data):
        print("✅ Assignation problématique supprimée")
    else:
        print("❌ Erreur lors de la suppression de l'assignation")
        return
    
    # Créer un nouveau locataire propre via l'API
    print("\n🔄 Création d'un nouveau locataire propre...")
    
    new_tenant_data = {
        "name": "Sacha Héroux",
        "email": "sacha.heroux@email.com",
        "phone": "(514) 555-0126",
        "status": "active",
        "building": "56 Vachon",
        "unit": "8-1",
        "lease": {
            "startDate": "2025-07-01",
            "endDate": "2026-06-30",
            "monthlyRent": 1350,
            "paymentMethod": "Virement bancaire",
            "amenities": {
                "heating": True,
                "electricity": True,
                "wifi": True,
                "furnished": True,
                "parking": False
            }
        },
        "notes": "Locataire recréé pour corriger l'assignation"
    }
    
    try:
        # Créer le locataire via l'API
        response = requests.post(
            f"{API_BASE_URL}/api/tenants",
            json=new_tenant_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            new_tenant = response.json().get("data")
            print(f"✅ Nouveau locataire créé: {new_tenant.get('name')} (ID: {new_tenant.get('id')})")
            
            # Créer une nouvelle assignation propre
            new_assignment_data = {
                "unitId": "8-1",
                "tenantId": new_tenant.get("id"),
                "tenantData": {
                    "name": new_tenant.get("name"),
                    "email": new_tenant.get("email"),
                    "phone": new_tenant.get("phone")
                }
            }
            
            assignment_response = requests.post(
                f"{API_BASE_URL}/api/assignments",
                json=new_assignment_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if assignment_response.status_code == 200:
                print("✅ Nouvelle assignation créée proprement")
                print("🎉 Problème résolu !")
            else:
                print(f"❌ Erreur création assignation: {assignment_response.status_code}")
        else:
            print(f"❌ Erreur création locataire: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")

if __name__ == "__main__":
    fix_tenant_assignments() 