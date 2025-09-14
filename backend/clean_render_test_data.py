#!/usr/bin/env python3
"""
Script pour nettoyer les données de test de Render
"""

import requests
import json

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def clean_render_test_data():
    """Nettoyer les données de test de Render"""
    print("🧹 Nettoyage des données de test de Render...")
    
    try:
        # 1. Récupérer toutes les assignations
        print("📋 Récupération des assignations...")
        response = requests.get(f"{RENDER_API_URL}/api/assignments")
        response.raise_for_status()
        
        assignments = response.json().get("data", [])
        print(f"📊 {len(assignments)} assignations trouvées")
        
        # 2. Supprimer les assignations de test
        for assignment in assignments:
            assignment_id = assignment.get("id")
            if assignment_id:
                print(f"🗑️ Suppression de l'assignation {assignment_id}...")
                
                # Supprimer l'assignation
                delete_response = requests.delete(f"{RENDER_API_URL}/api/assignments/{assignment_id}")
                if delete_response.status_code == 200:
                    print(f"✅ Assignation {assignment_id} supprimée")
                else:
                    print(f"❌ Erreur lors de la suppression de l'assignation {assignment_id}: {delete_response.status_code}")
        
        # 3. Vérifier que tout est nettoyé
        print("🔍 Vérification du nettoyage...")
        verify_response = requests.get(f"{RENDER_API_URL}/api/assignments")
        verify_response.raise_for_status()
        
        remaining_assignments = verify_response.json().get("data", [])
        print(f"📊 {len(remaining_assignments)} assignations restantes")
        
        if len(remaining_assignments) == 0:
            print("✅ Nettoyage terminé avec succès !")
        else:
            print("⚠️ Il reste des assignations à nettoyer")
            
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")

if __name__ == "__main__":
    clean_render_test_data()
