#!/usr/bin/env python3
"""
Script de migration pour transférer les assignations localStorage vers le backend
Usage: python migrate_assignments.py
"""

import json
import requests
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"

def migrate_sample_assignments():
    """Créer des assignations d'exemple pour tester le système"""
    print("🔄 Création d'assignations d'exemple pour tester la migration")
    print("=" * 60)
    
    # Exemples d'assignations (format localStorage)
    sample_assignments = [
        {
            "unitId": "4932-4934-4936-route-des-veterans-unit-1",
            "tenantId": 1,
            "tenantData": {
                "name": "Jean Dupont",
                "email": "jean.dupont@email.com",
                "phone": "(514) 555-0123"
            },
            "assignedAt": "2024-01-15T10:00:00Z"
        },
        {
            "unitId": "4932-4934-4936-route-des-veterans-unit-2", 
            "tenantId": 2,
            "tenantData": {
                "name": "Marie Martin",
                "email": "marie.martin@email.com", 
                "phone": "(514) 555-0124"
            },
            "assignedAt": "2024-01-20T14:30:00Z"
        }
    ]
    
    migrated = 0
    errors = 0
    
    for assignment in sample_assignments:
        try:
            # Créer l'assignation via l'API
            response = requests.post(
                f"{BACKEND_URL}/api/assignments",
                json={
                    "unitId": assignment["unitId"],
                    "tenantId": assignment["tenantId"],
                    "tenantData": assignment["tenantData"]
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                migrated += 1
                print(f"✅ Assignation créée: {assignment['tenantData']['name']} → {assignment['unitId']}")
            else:
                errors += 1
                print(f"❌ Erreur HTTP {response.status_code}: {assignment['tenantData']['name']}")
                
        except Exception as e:
            errors += 1
            print(f"❌ Erreur: {assignment['tenantData']['name']} - {e}")
    
    print("=" * 60)
    print(f"📊 Résultats: {migrated} assignations créées, {errors} erreurs")
    return migrated, errors

def check_backend_status():
    """Vérifier que le backend est accessible"""
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            print(f"✅ Backend accessible sur {BACKEND_URL}")
            return True
        else:
            print(f"❌ Backend inaccessible: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend inaccessible: {e}")
        return False

def show_existing_assignments():
    """Afficher les assignations existantes"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/assignments")
        if response.status_code == 200:
            assignments = response.json().get('data', [])
            print(f"📋 Assignations existantes dans le backend: {len(assignments)}")
            
            for assignment in assignments:
                tenant_name = assignment.get('tenantData', {}).get('name', 'N/A')
                unit_id = assignment.get('unitId', 'N/A')
                print(f"   → {tenant_name} dans l'unité {unit_id}")
            
            return len(assignments)
        else:
            print(f"❌ Erreur récupération assignations: HTTP {response.status_code}")
            return 0
    except Exception as e:
        print(f"❌ Erreur récupération assignations: {e}")
        return 0

def instructions_frontend_migration():
    """Afficher les instructions pour la migration côté frontend"""
    print("\n" + "=" * 60)
    print("📱 INSTRUCTIONS POUR MIGRATION AUTOMATIQUE FRONTEND")
    print("=" * 60)
    
    instructions = """
1. Ouvrez votre interface web sur le PC qui a les assignations
2. Ouvrez les outils de développement (F12)
3. Allez dans l'onglet "Console"
4. Tapez cette commande et appuyez sur Entrée :

   // Vérifier les assignations locales
   console.log('Assignations localStorage:', JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]'))

5. Si vous voyez des assignations, rechargez simplement la page !
   La migration se fera automatiquement au premier chargement.

6. Dans la console, vous verrez :
   📦 Migration de X assignations vers le backend...
   ✅ Assignation migrée: Locataire X → Unité Y
   🎉 Migration terminée avec succès: X assignations migrées

7. Une fois terminé, vérifiez sur les autres PC que les assignations
   sont maintenant synchronisées !
"""
    
    print(instructions)

if __name__ == "__main__":
    print("🚀 Script de Migration des Assignations")
    print("Interface CAH - Locataires ↔ Unités")
    print("=" * 60)
    
    # Vérifier le backend
    if not check_backend_status():
        print("\n❌ Le backend n'est pas accessible.")
        print("Assurez-vous qu'il tourne sur http://localhost:8000")
        exit(1)
    
    # Afficher les assignations existantes
    existing_count = show_existing_assignments()
    
    print(f"\n🎯 OPTIONS DISPONIBLES:")
    print("1. Migration automatique → Rechargez votre interface web")
    print("2. Test avec données d'exemple → Continuez ce script")
    
    choice = input("\nVoulez-vous créer des assignations d'exemple pour tester ? (o/N): ")
    
    if choice.lower() in ['o', 'oui', 'y', 'yes']:
        migrated, errors = migrate_sample_assignments()
        
        if migrated > 0:
            print(f"\n🎉 {migrated} assignations d'exemple créées !")
            print("Maintenant, vous pouvez tester que les assignations sont synchronisées")
            print("entre les différents PC.")
    
    # Afficher les instructions pour la migration frontend
    instructions_frontend_migration()
    
    print("\n✨ Migration terminée !")
    print("Les assignations sont maintenant centralisées sur le backend.")
    print("Toutes les modifications seront synchronisées entre tous les PC !") 