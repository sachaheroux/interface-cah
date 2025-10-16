#!/usr/bin/env python3
"""
Script combiné pour nettoyer et préparer la base de données
"""

import os
import sqlite3
import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"
LOCAL_DB_PATH = "data/construction_projects_local.db"

def step1_delete_employees_on_render():
    """Étape 1: Supprimer tous les employés sur Render"""
    print("🗑️ ÉTAPE 1: Suppression des employés sur Render")
    print("=" * 60)
    
    try:
        # Lister les employés
        response = requests.get(f"{RENDER_URL}/api/construction/employes", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                employees = data.get('data', [])
                print(f"👥 {len(employees)} employé(s) trouvé(s)")
                
                if employees:
                    for emp in employees:
                        employee_name = f"{emp.get('prenom', 'N/A')} {emp.get('nom', 'N/A')}"
                        print(f"🗑️ Suppression de {employee_name}...")
                        
                        delete_response = requests.delete(
                            f"{RENDER_URL}/api/construction/employes/{emp.get('id_employe')}",
                            timeout=30
                        )
                        
                        if delete_response.status_code == 200:
                            print(f"✅ {employee_name} supprimé")
                        else:
                            print(f"❌ Erreur suppression {employee_name}")
                else:
                    print("✅ Aucun employé à supprimer")
            else:
                print(f"❌ Erreur API: {data.get('message')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def step2_recreate_local_database():
    """Étape 2: Recréer la base locale avec la nouvelle structure"""
    print("\n🗄️ ÉTAPE 2: Recréation de la base locale")
    print("=" * 60)
    
    # Sauvegarder l'ancienne base
    if os.path.exists(LOCAL_DB_PATH):
        backup_path = f"{LOCAL_DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"📁 Sauvegarde: {backup_path}")
        
        import shutil
        shutil.copy2(LOCAL_DB_PATH, backup_path)
        os.remove(LOCAL_DB_PATH)
        print("✅ Ancienne base supprimée")
    
    # Créer le dossier data
    os.makedirs("data", exist_ok=True)
    
    # Recréer la base avec la nouvelle structure
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    create_employes_sql = '''
        CREATE TABLE employes (
            id_employe INTEGER PRIMARY KEY,
            prenom TEXT NOT NULL,
            nom TEXT NOT NULL,
            poste TEXT,
            numero TEXT,
            adresse_courriel TEXT,
            taux_horaire REAL,
            date_creation TEXT,
            date_modification TEXT
        )
    '''
    
    cursor.execute(create_employes_sql)
    print("✅ Table 'employes' créée avec taux_horaire")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Base locale recréée: {LOCAL_DB_PATH}")

def step3_verify_structure():
    """Étape 3: Vérifier la structure"""
    print("\n🔍 ÉTAPE 3: Vérification de la structure")
    print("=" * 60)
    
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(employes)")
    columns = cursor.fetchall()
    
    print("📋 Structure de la table employes:")
    for col in columns:
        print(f"  - {col[1]}: {col[2]} (not_null: {col[3]})")
    
    column_names = [col[1] for col in columns]
    if 'taux_horaire' in column_names:
        print("✅ Colonne 'taux_horaire' présente")
    else:
        print("❌ Colonne 'taux_horaire' manquante")
    
    conn.close()

def step4_test_download():
    """Étape 4: Tester le téléchargement"""
    print("\n📥 ÉTAPE 4: Test du téléchargement")
    print("=" * 60)
    
    try:
        response = requests.get(f"{RENDER_URL}/api/construction/employes", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                employees = data.get('data', [])
                print(f"👥 {len(employees)} employé(s) sur Render")
                
                if employees:
                    print("📋 Employés sur Render:")
                    for emp in employees:
                        print(f"  - {emp.get('prenom')} {emp.get('nom')} (taux: ${emp.get('taux_horaire', 'N/A')})")
                else:
                    print("✅ Base Render vide - prête pour nouveaux employés")
            else:
                print(f"❌ Erreur API: {data.get('message')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 NETTOYAGE COMPLET - Interface CAH")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Exécuter toutes les étapes
    step1_delete_employees_on_render()
    step2_recreate_local_database()
    step3_verify_structure()
    step4_test_download()
    
    print("\n" + "=" * 60)
    print("🎉 NETTOYAGE TERMINÉ !")
    print()
    print("💡 Prochaines étapes:")
    print("   1. Aller sur le site → Section Employés")
    print("   2. Cliquer 'Nouvel Employé'")
    print("   3. Créer Sacha Héroux (taux: $35.00)")
    print("   4. Créer Daniel Baribeau (taux: $30.00)")
    print("   5. Tester le téléchargement avec download_construction_db.py")

