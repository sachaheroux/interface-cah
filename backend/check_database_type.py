#!/usr/bin/env python3
"""
Script pour vérifier quelle base de données utilise la partie locative
"""

import os
import requests
import json

def check_database_type():
    """Vérifier le type de base de données utilisé"""
    
    print("🔍 VÉRIFICATION DU TYPE DE BASE DE DONNÉES")
    print("=" * 60)
    
    print("1️⃣ VÉRIFICATION DES VARIABLES D'ENVIRONNEMENT")
    print("-" * 40)
    
    # Vérifier les variables d'environnement
    database_url = os.environ.get('DATABASE_URL')
    print(f"DATABASE_URL: {database_url}")
    
    if database_url:
        if 'postgresql' in database_url.lower():
            print("✅ PostgreSQL détecté")
            db_type = "PostgreSQL"
        elif 'sqlite' in database_url.lower():
            print("✅ SQLite détecté")
            db_type = "SQLite"
        else:
            print(f"❓ Type de base inconnu: {database_url[:50]}...")
            db_type = "Inconnu"
    else:
        print("❌ DATABASE_URL non définie")
        db_type = "Non définie"
    
    print(f"\n📊 Type de base détecté: {db_type}")
    
    print("\n2️⃣ VÉRIFICATION DU CODE DATABASE.PY")
    print("-" * 40)
    
    try:
        with open('database.py', 'r') as f:
            content = f.read()
            
        if 'postgresql' in content.lower():
            print("✅ database.py utilise PostgreSQL")
            code_type = "PostgreSQL"
        elif 'sqlite' in content.lower():
            print("✅ database.py utilise SQLite")
            code_type = "SQLite"
        else:
            print("❓ Type de base non clair dans database.py")
            code_type = "Inconnu"
            
        print(f"📊 Type dans le code: {code_type}")
        
    except Exception as e:
        print(f"❌ Erreur lecture database.py: {e}")
        code_type = "Erreur"
    
    print("\n3️⃣ TEST DE L'API LOCATIVE")
    print("-" * 40)
    
    try:
        # Tester l'API locative
        response = requests.get("https://interface-cah-backend.onrender.com/api/buildings", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            buildings = data.get('data', [])
            print(f"✅ API locative fonctionne: {len(buildings)} immeubles")
            
            if buildings:
                print("   Exemples d'immeubles:")
                for i, building in enumerate(buildings[:3], 1):
                    print(f"   {i}. {building.get('nom', 'N/A')}")
            else:
                print("   ⚠️ Aucun immeuble trouvé")
                
        else:
            print(f"❌ Erreur API locative: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur test API locative: {e}")
    
    print("\n4️⃣ TEST DE L'API CONSTRUCTION")
    print("-" * 40)
    
    try:
        # Tester l'API construction
        response = requests.get("https://interface-cah-backend.onrender.com/api/construction/employes", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            employees = data.get('data', [])
            print(f"✅ API construction fonctionne: {len(employees)} employés")
            
            if employees:
                print("   Exemples d'employés:")
                for i, emp in enumerate(employees[:3], 1):
                    print(f"   {i}. {emp.get('prenom', 'N/A')} {emp.get('nom', 'N/A')}")
            else:
                print("   ⚠️ Aucun employé trouvé")
                
        else:
            print(f"❌ Erreur API construction: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur test API construction: {e}")
    
    print("\n5️⃣ ANALYSE DE LA PERSISTANCE")
    print("-" * 40)
    
    print("🔍 Analyse:")
    print(f"   - Variable DATABASE_URL: {db_type}")
    print(f"   - Code database.py: {code_type}")
    
    if db_type == "PostgreSQL" and code_type == "PostgreSQL":
        print("   ✅ Cohérence: PostgreSQL utilisé partout")
        print("   💡 La partie locative utilise PostgreSQL sur Render")
        print("   💡 La partie construction devrait aussi utiliser PostgreSQL")
    elif db_type == "SQLite" and code_type == "SQLite":
        print("   ✅ Cohérence: SQLite utilisé partout")
        print("   💡 La partie locative utilise SQLite")
        print("   💡 Problème: SQLite ne persiste pas sur Render")
    else:
        print("   ⚠️ Incohérence détectée")
        print("   💡 Vérification manuelle nécessaire")
    
    return db_type, code_type

def check_render_configuration():
    """Vérifier la configuration Render"""
    
    print("\n6️⃣ VÉRIFICATION DE LA CONFIGURATION RENDER")
    print("-" * 40)
    
    print("🔍 Points à vérifier sur Render:")
    print("   1. Aller sur https://dashboard.render.com")
    print("   2. Sélectionner le service 'interface-cah-backend'")
    print("   3. Vérifier la section 'Environment':")
    print("      - Y a-t-il une variable DATABASE_URL?")
    print("      - Quelle est sa valeur?")
    print("   4. Vérifier la section 'Services':")
    print("      - Y a-t-il un service de base de données PostgreSQL?")
    print("      - Ou utilise-t-on SQLite avec disque persistant?")
    
    print("\n💡 Si PostgreSQL:")
    print("   - La partie locative persiste correctement")
    print("   - La partie construction devrait utiliser la même base")
    
    print("\n💡 Si SQLite:")
    print("   - Problème de persistance sur Render")
    print("   - Besoin d'un disque persistant ou migration PostgreSQL")

def main():
    """Fonction principale"""
    
    db_type, code_type = check_database_type()
    check_render_configuration()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTIC TERMINÉ")
    print("=" * 60)
    
    if db_type == "PostgreSQL":
        print("✅ SOLUTION: Migrer la partie construction vers PostgreSQL")
        print("💡 Les deux parties utiliseront la même base PostgreSQL")
    elif db_type == "SQLite":
        print("⚠️ PROBLÈME: SQLite ne persiste pas sur Render")
        print("💡 Solutions possibles:")
        print("   1. Créer un service PostgreSQL sur Render")
        print("   2. Configurer un disque persistant pour SQLite")
        print("   3. Utiliser une base de données externe")
    else:
        print("❓ Configuration inconnue - vérification manuelle nécessaire")

if __name__ == "__main__":
    main()
