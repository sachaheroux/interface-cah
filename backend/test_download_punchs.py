#!/usr/bin/env python3
"""
Script pour tester spécifiquement le téléchargement des punchs
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from download_construction_db import fetch_data_from_api, insert_data_to_local_db, LOCAL_DB_PATH
import sqlite3

RENDER_URL = "https://interface-cah-backend.onrender.com"

def test_download_punchs():
    """Tester le téléchargement des punchs"""
    print("=" * 60)
    print("TEST DE TÉLÉCHARGEMENT DES PUNCHS")
    print("=" * 60)
    print()
    
    # Récupérer les données depuis l'API
    print("1️⃣ RÉCUPÉRATION DEPUIS L'API")
    print("-" * 60)
    data = fetch_data_from_api('/api/construction/punchs-employes')
    
    if not data:
        print("❌ Aucune donnée récupérée")
        return
    
    print(f"✅ {len(data)} punch(s) récupéré(s)")
    print()
    
    # Afficher la structure
    if len(data) > 0:
        print("2️⃣ STRUCTURE DES DONNÉES")
        print("-" * 60)
        first_item = data[0]
        print("Colonnes dans les données API:")
        for key, value in first_item.items():
            if isinstance(value, dict):
                print(f"   - {key}: [OBJET IMBRIQUÉ - sera exclu]")
            else:
                print(f"   - {key}: {type(value).__name__}")
        print()
    
    # Tester l'insertion
    print("3️⃣ TEST D'INSERTION")
    print("-" * 60)
    try:
        insert_data_to_local_db('punchs_employes', data)
        print()
        
        # Vérifier dans la base locale
        print("4️⃣ VÉRIFICATION DANS LA BASE LOCALE")
        print("-" * 60)
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        # Vérifier la structure de la table
        cursor.execute("PRAGMA table_info(punchs_employes)")
        columns = cursor.fetchall()
        print("Colonnes dans la table locale:")
        for col in columns:
            print(f"   - {col[1]}: {col[2]}")
        print()
        
        # Compter les punchs
        cursor.execute("SELECT COUNT(*) FROM punchs_employes")
        count = cursor.fetchone()[0]
        print(f"📊 Nombre de punchs dans la base locale: {count}")
        
        # Afficher les punchs
        if count > 0:
            cursor.execute("SELECT * FROM punchs_employes")
            punchs = cursor.fetchall()
            print()
            print("Punchs dans la base locale:")
            for punch in punchs:
                print(f"   - ID: {punch[0]}, Employé: {punch[1]}, Projet: {punch[2]}, Date: {punch[3]}, Heures: {punch[4]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("✅ Test terminé")
    print("=" * 60)

if __name__ == "__main__":
    test_download_punchs()

