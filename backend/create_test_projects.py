#!/usr/bin/env python3
"""
Script pour créer des projets de test pour les pointages
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def create_test_projects():
    """Créer des projets de test"""
    
    projets_test = [
        {
            "nom": "Maison Unifamiliale - 123 Rue Principale",
            "date_debut": (datetime.now() - timedelta(days=30)).isoformat(),
            "date_fin_prevue": (datetime.now() + timedelta(days=60)).isoformat(),
            "notes": "Construction d'une maison unifamiliale de 3 chambres"
        },
        {
            "nom": "Condominium - 456 Avenue Centrale",
            "date_debut": (datetime.now() - timedelta(days=15)).isoformat(),
            "date_fin_prevue": (datetime.now() + timedelta(days=90)).isoformat(),
            "notes": "Construction d'un bâtiment de 12 unités"
        },
        {
            "nom": "Rénovation Commerciale - Centre-Ville",
            "date_debut": (datetime.now() - timedelta(days=7)).isoformat(),
            "date_fin_prevue": (datetime.now() + timedelta(days=45)).isoformat(),
            "notes": "Rénovation complète d'un bâtiment commercial"
        },
        {
            "nom": "Garage Résidentiel - 789 Rue Secondaire",
            "date_debut": datetime.now().isoformat(),
            "date_fin_prevue": (datetime.now() + timedelta(days=21)).isoformat(),
            "notes": "Construction d'un garage double pour résidence"
        }
    ]
    
    projets_crees = []
    
    print("🏗️ CRÉATION DE PROJETS DE TEST")
    print("=" * 50)
    
    for i, projet_data in enumerate(projets_test, 1):
        print(f"\n{i}️⃣ Création du projet: {projet_data['nom']}")
        
        try:
            response = requests.post(
                f"{CONSTRUCTION_BASE}/projets",
                json=projet_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                projet_id = data['data']['id_projet']
                projets_crees.append(projet_id)
                print(f"✅ Projet créé avec succès: ID {projet_id}")
                print(f"   Nom: {data['data']['nom']}")
            else:
                print(f"❌ Erreur création: {response.status_code}")
                print(f"   Réponse: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    print(f"\n📊 RÉSUMÉ")
    print("=" * 50)
    print(f"✅ {len(projets_crees)} projet(s) créé(s) avec succès")
    print(f"📋 IDs des projets: {projets_crees}")
    
    return projets_crees

def verify_projects():
    """Vérifier que les projets ont été créés"""
    
    print("\n🔍 VÉRIFICATION DES PROJETS")
    print("=" * 50)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/projets", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            projets = data.get('data', [])
            
            print(f"✅ {len(projets)} projet(s) trouvé(s)")
            
            for projet in projets:
                print(f"   📋 ID: {projet['id_projet']} - {projet['nom']}")
                if projet.get('date_debut'):
                    print(f"      Début: {projet['date_debut'][:10]}")
                if projet.get('date_fin_prevue'):
                    print(f"      Fin prévue: {projet['date_fin_prevue'][:10]}")
            
            return projets
        else:
            print(f"❌ Erreur récupération: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

if __name__ == "__main__":
    print("🚀 SCRIPT DE CRÉATION DE PROJETS DE TEST")
    print("⏰", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Créer les projets
    projets_crees = create_test_projects()
    
    # Vérifier les projets
    projets_verifies = verify_projects()
    
    print("\n🎉 TERMINÉ!")
    print("=" * 50)
    print("💡 Les employés peuvent maintenant sélectionner ces projets")
    print("   lors de la création de pointages.")
