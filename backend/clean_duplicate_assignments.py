#!/usr/bin/env python3
"""
Script pour nettoyer les assignations en double
"""

import requests
import json

def clean_duplicate_assignments():
    """Nettoyer les assignations en double"""
    print("🧹 Nettoyage des assignations en double...")
    
    try:
        # Récupérer toutes les assignations
        response = requests.get('https://interface-cah-backend.onrender.com/api/assignments')
        if response.status_code != 200:
            print(f"❌ Erreur API: {response.status_code}")
            return False
            
        data = response.json()
        assignments = data.get('data', [])
        print(f"📊 {len(assignments)} assignations trouvées")
        
        # Grouper par tenantId pour trouver les doublons
        tenant_assignments = {}
        for assignment in assignments:
            tenant_id = assignment.get('tenantId')
            if tenant_id not in tenant_assignments:
                tenant_assignments[tenant_id] = []
            tenant_assignments[tenant_id].append(assignment)
        
        # Identifier les doublons
        duplicates_to_remove = []
        for tenant_id, tenant_assigns in tenant_assignments.items():
            if len(tenant_assigns) > 1:
                print(f"🔄 Locataire {tenant_id} a {len(tenant_assigns)} assignations")
                # Garder la plus récente, supprimer les autres
                sorted_assigns = sorted(tenant_assigns, key=lambda x: x.get('createdAt', ''), reverse=True)
                for i, assignment in enumerate(sorted_assigns[1:], 1):  # Skip first (keep), remove rest
                    duplicates_to_remove.append(assignment['id'])
                    print(f"  ❌ À supprimer: assignation {assignment['id']}")
        
        # Supprimer les doublons
        for assignment_id in duplicates_to_remove:
            try:
                delete_response = requests.delete(f'https://interface-cah-backend.onrender.com/api/assignments/{assignment_id}')
                if delete_response.status_code == 200:
                    print(f"✅ Assignation {assignment_id} supprimée")
                else:
                    print(f"❌ Erreur suppression assignation {assignment_id}: {delete_response.status_code}")
            except Exception as e:
                print(f"❌ Erreur suppression assignation {assignment_id}: {e}")
        
        print(f"✅ Nettoyage terminé: {len(duplicates_to_remove)} assignations supprimées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return False

if __name__ == "__main__":
    clean_duplicate_assignments()
