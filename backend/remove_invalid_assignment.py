#!/usr/bin/env python3
"""
Script pour supprimer spécifiquement l'assignation invalide 1752878177987
Usage: python remove_invalid_assignment.py
"""

import json
import os

# Configuration
DATA_DIR = os.environ.get("DATA_DIR", "./data")
ASSIGNMENTS_DATA_FILE = os.path.join(DATA_DIR, "assignments_data.json")

def remove_invalid_assignment():
    """Supprimer l'assignation avec tenantId 1752878177987"""
    print("🧹 Suppression de l'assignation invalide 1752878177987")
    print("=" * 60)
    
    # Charger les données
    try:
        with open(ASSIGNMENTS_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erreur chargement {ASSIGNMENTS_DATA_FILE}: {e}")
        return
    
    assignments = data.get("assignments", [])
    print(f"📊 Assignations totales: {len(assignments)}")
    
    # Trouver l'assignation invalide
    invalid_assignment = None
    valid_assignments = []
    
    for assignment in assignments:
        if assignment.get("tenantId") == 1752878177987:
            invalid_assignment = assignment
            print(f"❌ Assignation invalide trouvée: ID {assignment.get('id')}, TenantID: {assignment.get('tenantId')}, Unité: {assignment.get('unitId')}")
        else:
            valid_assignments.append(assignment)
    
    if invalid_assignment:
        print(f"✅ Assignations valides: {len(valid_assignments)}")
        print(f"❌ Assignation invalide à supprimer: 1")
        
        # Sauvegarder sans l'assignation invalide
        data["assignments"] = valid_assignments
        
        try:
            with open(ASSIGNMENTS_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✅ Assignation invalide supprimée avec succès")
            print(f"✅ {len(valid_assignments)} assignations conservées")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
    else:
        print("✅ Aucune assignation invalide trouvée")

if __name__ == "__main__":
    remove_invalid_assignment() 