#!/usr/bin/env python3
"""
Script de nettoyage pour supprimer les assignations avec des tenantId invalides
Usage: python clean_assignments.py
"""

import json
import os
from datetime import datetime

# Configuration
DATA_DIR = os.environ.get("DATA_DIR", "./data")
ASSIGNMENTS_DATA_FILE = os.path.join(DATA_DIR, "assignments_data.json")
TENANTS_DATA_FILE = os.path.join(DATA_DIR, "tenants_data.json")

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

def clean_invalid_assignments():
    """Nettoyer les assignations avec des tenantId invalides"""
    print("🧹 Nettoyage des assignations invalides")
    print("=" * 60)
    
    # Charger les données
    assignments_data = load_json_file(ASSIGNMENTS_DATA_FILE)
    tenants_data = load_json_file(TENANTS_DATA_FILE)
    
    if not assignments_data:
        print("❌ Impossible de charger les données d'assignations")
        return
    
    if not tenants_data:
        print("❌ Impossible de charger les données de locataires")
        return
    
    # Récupérer les IDs valides des locataires
    valid_tenant_ids = {t.get("id") for t in tenants_data.get("tenants", [])}
    print(f"✅ Locataires valides trouvés: {len(valid_tenant_ids)}")
    print(f"📋 IDs valides: {sorted(valid_tenant_ids)}")
    
    # Analyser les assignations
    assignments = assignments_data.get("assignments", [])
    print(f"📊 Assignations totales: {len(assignments)}")
    
    invalid_assignments = []
    valid_assignments = []
    
    for assignment in assignments:
        tenant_id = assignment.get("tenantId")
        
        # Vérifier si l'ID est valide
        if tenant_id in valid_tenant_ids:
            valid_assignments.append(assignment)
        else:
            invalid_assignments.append(assignment)
            print(f"❌ Assignation invalide trouvée: ID {tenant_id} (unité: {assignment.get('unitId')})")
    
    print(f"✅ Assignations valides: {len(valid_assignments)}")
    print(f"❌ Assignations invalides: {len(invalid_assignments)}")
    
    if invalid_assignments:
        print("\n🗑️ Assignations invalides à supprimer:")
        for assignment in invalid_assignments:
            print(f"  - ID: {assignment.get('id')}, TenantID: {assignment.get('tenantId')}, Unité: {assignment.get('unitId')}")
        
        # Demander confirmation
        response = input("\n❓ Voulez-vous supprimer ces assignations invalides ? (oui/non): ")
        
        if response.lower() in ['oui', 'yes', 'y', 'o']:
            # Sauvegarder les assignations valides seulement
            assignments_data["assignments"] = valid_assignments
            
            if save_json_file(ASSIGNMENTS_DATA_FILE, assignments_data):
                print(f"✅ Nettoyage terminé: {len(invalid_assignments)} assignations supprimées")
                print(f"✅ {len(valid_assignments)} assignations conservées")
            else:
                print("❌ Erreur lors de la sauvegarde")
        else:
            print("❌ Nettoyage annulé")
    else:
        print("✅ Aucune assignation invalide trouvée")

def main():
    """Fonction principale"""
    print("🔧 Script de nettoyage des assignations")
    print("=" * 60)
    
    # Vérifier que les fichiers existent
    if not os.path.exists(ASSIGNMENTS_DATA_FILE):
        print(f"❌ Fichier d'assignations non trouvé: {ASSIGNMENTS_DATA_FILE}")
        return
    
    if not os.path.exists(TENANTS_DATA_FILE):
        print(f"❌ Fichier de locataires non trouvé: {TENANTS_DATA_FILE}")
        return
    
    clean_invalid_assignments()

if __name__ == "__main__":
    main() 