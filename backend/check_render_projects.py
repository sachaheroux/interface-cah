#!/usr/bin/env python3
"""
Script pour récupérer les projets depuis l'API Render et voir quels champs sont utilisés
"""

import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"

def check_render_projects():
    """Récupérer les projets depuis Render et afficher leur structure"""
    print("=" * 60)
    print("VÉRIFICATION DES PROJETS SUR RENDER")
    print("=" * 60)
    print(f"🌐 URL Render: {RENDER_URL}")
    print()
    
    try:
        # Récupérer tous les projets
        print("1️⃣ RÉCUPÉRATION DES PROJETS")
        print("-" * 60)
        
        response = requests.get(f"{RENDER_URL}/api/construction/projets", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                projects = data.get('data', [])
                print(f"✅ {len(projects)} projet(s) trouvé(s)")
                print()
                
                if len(projects) > 0:
                    # Afficher la structure du premier projet
                    print("2️⃣ STRUCTURE DES CHAMPS (basée sur le premier projet)")
                    print("-" * 60)
                    
                    first_project = projects[0]
                    
                    # Grouper les champs par catégorie
                    categories = {
                        "Informations de base": [
                            "id_projet", "nom", "description", "statut", "progression_pourcentage"
                        ],
                        "Adresse": [
                            "adresse", "ville", "province", "code_postal"
                        ],
                        "Dates": [
                            "date_debut", "date_fin_prevue", "date_fin_reelle", 
                            "date_creation", "date_modification"
                        ],
                        "Financier": [
                            "budget_total", "cout_actuel", "marge_beneficiaire"
                        ],
                        "Client": [
                            "client_nom", "client_telephone", "client_email"
                        ],
                        "Équipe": [
                            "chef_projet", "architecte", "entrepreneur_principal"
                        ],
                        "Documents": [
                            "plans_pdf", "permis_construction", "numero_permis"
                        ],
                        "Notes": [
                            "notes", "risques_identifies", "ameliorations_futures"
                        ],
                        "Métadonnées": [
                            "cree_par", "modifie_par"
                        ]
                    }
                    
                    for category, fields in categories.items():
                        print(f"\n📋 {category}:")
                        for field in fields:
                            value = first_project.get(field)
                            if value is not None:
                                if isinstance(value, str) and len(value) > 50:
                                    print(f"   ✅ {field}: {value[:50]}...")
                                else:
                                    print(f"   ✅ {field}: {value}")
                            else:
                                print(f"   ⚪ {field}: (vide)")
                    
                    print()
                    print("3️⃣ TOUS LES PROJETS")
                    print("-" * 60)
                    
                    for idx, project in enumerate(projects, 1):
                        print(f"\n📋 PROJET #{idx}: {project.get('nom', 'Sans nom')}")
                        print(f"   ID: {project.get('id_projet')}")
                        print(f"   Statut: {project.get('statut', 'N/A')}")
                        print(f"   Progression: {project.get('progression_pourcentage', 0)}%")
                        if project.get('budget_total'):
                            print(f"   Budget: ${project.get('budget_total', 0):,.2f}")
                        if project.get('date_creation'):
                            print(f"   Créé le: {project.get('date_creation')}")
                    
                    print()
                    print("4️⃣ RÉSUMÉ DES CHAMPS UTILISÉS")
                    print("-" * 60)
                    
                    # Compter quels champs sont remplis dans au moins un projet
                    all_fields = set()
                    filled_fields = {}
                    
                    for project in projects:
                        for field, value in project.items():
                            all_fields.add(field)
                            if value is not None and value != "":
                                if field not in filled_fields:
                                    filled_fields[field] = 0
                                filled_fields[field] += 1
                    
                    print(f"📊 Total de champs dans le modèle: {len(all_fields)}")
                    print(f"📊 Champs remplis dans au moins un projet: {len(filled_fields)}")
                    print()
                    print("Champs utilisés (avec nombre de projets qui les remplissent):")
                    for field in sorted(all_fields):
                        count = filled_fields.get(field, 0)
                        status = "✅" if count > 0 else "⚪"
                        print(f"   {status} {field}: {count}/{len(projects)} projets")
                    
                else:
                    print("⚠️ Aucun projet trouvé dans la base de données")
                    print("\n📋 CHAMPS DISPONIBLES DANS LE MODÈLE:")
                    print("-" * 60)
                    print("""
Informations de base:
  - id_projet
  - nom
  - description
  - statut
  - progression_pourcentage

Adresse:
  - adresse
  - ville
  - province
  - code_postal

Dates:
  - date_debut
  - date_fin_prevue
  - date_fin_reelle
  - date_creation
  - date_modification

Financier:
  - budget_total
  - cout_actuel
  - marge_beneficiaire

Client:
  - client_nom
  - client_telephone
  - client_email

Équipe:
  - chef_projet
  - architecte
  - entrepreneur_principal

Documents:
  - plans_pdf
  - permis_construction
  - numero_permis

Notes:
  - notes
  - risques_identifies
  - ameliorations_futures

Métadonnées:
  - cree_par
  - modifie_par
                    """)
            else:
                print(f"❌ Erreur API: {data.get('message', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("✅ Vérification terminée")
    print("=" * 60)

if __name__ == "__main__":
    check_render_projects()

