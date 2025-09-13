#!/usr/bin/env python3
"""
Script pour corriger les unités sur Render
- Changer le type de 1 1/2 à 4 1/2
- Corriger les adresses doublées
"""

import os
import sys
import requests
import json
from datetime import datetime

# Configuration Render
RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def fix_render_units():
    """Corriger les unités sur Render"""
    print("🌐 CORRECTION DES UNITÉS SUR RENDER")
    print("=" * 60)
    
    try:
        # 1. Récupérer toutes les unités
        print("1️⃣ Récupération des unités depuis Render...")
        
        response = requests.get(f"{RENDER_API_URL}/api/units", timeout=30)
        if response.status_code != 200:
            print(f"   ❌ Erreur API: {response.status_code}")
            return False
        
        units = response.json()
        print(f"   📊 {len(units)} unités trouvées")
        
        if not units:
            print("   ✅ Aucune unité à corriger")
            return True
        
        # 2. Corriger chaque unité
        print("2️⃣ Correction des unités...")
        
        for unit in units:
            print(f"   🔄 Unité {unit['id']}: {unit['unitNumber']}")
            
            # Préparer les données de correction
            update_data = {}
            
            # Corriger le type (1 1/2 → 4 1/2)
            if unit.get('type') == "1 1/2":
                update_data['type'] = "4 1/2"
                print(f"      ✅ Type à changer: 1 1/2 → 4 1/2")
            
            # Corriger l'adresse doublée
            unit_address = unit.get('unitAddress', '')
            if unit_address and ' ' in unit_address:
                parts = unit_address.split(' ', 1)
                if len(parts) == 2:
                    unit_num = parts[0]
                    street_part = parts[1]
                    
                    # Vérifier si c'est une adresse doublée (ex: "56 56-58-60-62 rue Vachon")
                    if '-' in street_part and street_part.split(' ')[0].replace('-', '').isdigit():
                        # Extraire le nom de la rue (après le premier espace)
                        street_parts = street_part.split(' ', 1)
                        if len(street_parts) > 1:
                            street_name = street_parts[1]
                            update_data['unitAddress'] = f"{unit_num} {street_name}"
                            print(f"      ✅ Adresse à corriger: {unit_address} → {update_data['unitAddress']}")
            
            # Mettre à jour l'unité si nécessaire
            if update_data:
                try:
                    update_response = requests.put(
                        f"{RENDER_API_URL}/api/units/{unit['id']}",
                        json=update_data,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                    
                    if update_response.status_code == 200:
                        print(f"      ✅ Unité {unit['id']} mise à jour avec succès")
                    else:
                        print(f"      ❌ Erreur mise à jour unité {unit['id']}: {update_response.status_code}")
                        print(f"      📊 Réponse: {update_response.text}")
                except Exception as e:
                    print(f"      ❌ Erreur lors de la mise à jour unité {unit['id']}: {e}")
            else:
                print(f"      ⚪ Aucune correction nécessaire pour l'unité {unit['id']}")
        
        print("   ✅ Correction terminée!")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR lors de la correction: {e}")
        return False

def create_manual_sql():
    """Créer le SQL manuel pour corriger les unités"""
    print("📝 CRÉATION DU SQL DE CORRECTION")
    print("=" * 60)
    
    sql_commands = [
        "-- Correction des unités sur Render",
        "-- Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "-- 1. Changer le type de 1 1/2 à 4 1/2",
        "UPDATE units SET type = '4 1/2' WHERE type = '1 1/2';",
        "",
        "-- 2. Corriger les adresses doublées",
        "-- Exemple: '56 56-58-60-62 rue Vachon' → '56 rue Vachon'",
        "UPDATE units SET unit_address = ",
        "  CASE ",
        "    WHEN unit_address LIKE '% %' AND ",
        "         SUBSTR(unit_address, INSTR(unit_address, ' ') + 1) LIKE '%-%' AND ",
        "         SUBSTR(SUBSTR(unit_address, INSTR(unit_address, ' ') + 1), 1, INSTR(SUBSTR(unit_address, INSTR(unit_address, ' ') + 1), ' ') - 1) GLOB '*[0-9]*' ",
        "    THEN SUBSTR(unit_address, 1, INSTR(unit_address, ' ') - 1) || ' ' || ",
        "         SUBSTR(SUBSTR(unit_address, INSTR(unit_address, ' ') + 1), INSTR(SUBSTR(unit_address, INSTR(unit_address, ' ') + 1), ' ') + 1)",
        "    ELSE unit_address",
        "  END",
        "WHERE unit_address LIKE '% %' AND ",
        "      SUBSTR(unit_address, INSTR(unit_address, ' ') + 1) LIKE '%-%';",
        "",
        "-- 3. Vérifier le résultat",
        "SELECT id, unit_number, type, unit_address FROM units;"
    ]
    
    sql_content = "\n".join(sql_commands)
    
    # Sauvegarder dans un fichier
    with open("fix_render_units.sql", "w", encoding="utf-8") as f:
        f.write(sql_content)
    
    print("✅ SQL de correction créé: fix_render_units.sql")
    print("\n📋 COMMANDES SQL À EXÉCUTER SUR RENDER:")
    print("=" * 60)
    print(sql_content)
    
    return True

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DE LA CORRECTION RENDER")
    print("=" * 60)
    
    # Créer le SQL de correction
    if create_manual_sql():
        print("\n✅ SQL de correction créé")
    
    # Essayer la correction via API
    if fix_render_units():
        print("🎉 CORRECTION RENDER TERMINÉE AVEC SUCCÈS!")
    else:
        print("⚠️  Correction via API échouée, utilisez le SQL manuellement")
        print("📋 Exécutez le fichier fix_render_units.sql sur Render")
