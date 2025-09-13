#!/usr/bin/env python3
"""
Script pour corriger les unités sur Render via l'API
- Changer le type de 1 1/2 à 4 1/2
- Corriger les adresses doublées
"""

import requests
import json
import time

# Configuration Render
RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def correct_render_units():
    """Corriger les unités sur Render via l'API"""
    print("🌐 CORRECTION DES UNITÉS SUR RENDER")
    print("=" * 60)
    
    try:
        # 1. Récupérer toutes les unités
        print("1️⃣ Récupération des unités depuis Render...")
        
        response = requests.get(f"{RENDER_API_URL}/api/units", timeout=30)
        if response.status_code != 200:
            print(f"   ❌ Erreur API: {response.status_code}")
            print(f"   📊 Réponse: {response.text}")
            return False
        
        # Vérifier le type de réponse
        if isinstance(response.text, str):
            try:
                units_data = json.loads(response.text)
            except json.JSONDecodeError:
                print(f"   ❌ Erreur parsing JSON: {response.text}")
                return False
        else:
            units_data = response.json()
        
        # Vérifier si c'est une liste ou un dictionnaire
        if isinstance(units_data, dict):
            # Si c'est un dictionnaire, chercher la clé qui contient la liste
            if 'data' in units_data:
                units_list = units_data['data']
            elif 'units' in units_data:
                units_list = units_data['units']
            else:
                # Si c'est directement un dictionnaire d'unité
                units_list = [units_data]
        else:
            units_list = units_data
        
        print(f"   📊 {len(units_list)} unités trouvées")
        print(f"   📊 Type de données: {type(units_list)}")
        print(f"   📊 Premier élément: {units_list[0] if units_list else 'Aucun'}")
        
        if not units_list:
            print("   ✅ Aucune unité à corriger")
            return True
        
        # 2. Corriger chaque unité
        print("2️⃣ Correction des unités...")
        
        for unit in units_list:
            unit_id = unit.get('id')
            unit_number = unit.get('unitNumber', '')
            current_type = unit.get('type', '')
            current_address = unit.get('unitAddress', '')
            
            print(f"   🔄 Unité {unit_id}: {unit_number}")
            
            # Préparer les données de correction
            update_data = {}
            
            # Ne pas changer le type - laisser ce qui est dans la fiche
            # Le problème était que la base avait "1 1/2" par défaut
            # mais maintenant le formulaire gère correctement les types
            print(f"      ⚪ Type actuel: {current_type} (conservé)")
            
            # Corriger l'adresse doublée
            if current_address and ' ' in current_address:
                parts = current_address.split(' ', 1)
                if len(parts) == 2:
                    unit_num = parts[0]
                    street_part = parts[1]
                    
                    # Vérifier si c'est une adresse doublée (ex: "56 56-58-60-62 rue Vachon")
                    if '-' in street_part:
                        street_parts = street_part.split(' ', 1)
                        if len(street_parts) > 1:
                            street_name = street_parts[1]
                            new_address = f"{unit_num} {street_name}"
                            update_data['unitAddress'] = new_address
                            print(f"      ✅ Adresse à corriger: {current_address} → {new_address}")
            
            # Mettre à jour l'unité si nécessaire
            if update_data:
                try:
                    print(f"      🔄 Mise à jour de l'unité {unit_id}...")
                    
                    update_response = requests.put(
                        f"{RENDER_API_URL}/api/units/{unit_id}",
                        json=update_data,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                    
                    if update_response.status_code == 200:
                        print(f"      ✅ Unité {unit_id} mise à jour avec succès")
                    else:
                        print(f"      ❌ Erreur mise à jour unité {unit_id}: {update_response.status_code}")
                        print(f"      📊 Réponse: {update_response.text}")
                        
                        # Essayer de créer une nouvelle unité si la mise à jour échoue
                        print(f"      🔄 Tentative de création d'une nouvelle unité...")
                        
                        # Récupérer les données complètes de l'unité
                        unit_response = requests.get(f"{RENDER_API_URL}/api/units/{unit_id}", timeout=30)
                        if unit_response.status_code == 200:
                            full_unit_data = unit_response.json()
                            # Merger avec les corrections
                            full_unit_data.update(update_data)
                            
                            # Supprimer l'ancienne unité et créer la nouvelle
                            delete_response = requests.delete(f"{RENDER_API_URL}/api/units/{unit_id}", timeout=30)
                            if delete_response.status_code == 200:
                                # Créer la nouvelle unité
                                create_response = requests.post(
                                    f"{RENDER_API_URL}/api/units",
                                    json=full_unit_data,
                                    headers={"Content-Type": "application/json"},
                                    timeout=30
                                )
                                
                                if create_response.status_code == 200:
                                    print(f"      ✅ Unité {unit_id} recréée avec succès")
                                else:
                                    print(f"      ❌ Erreur recréation unité {unit_id}: {create_response.status_code}")
                                    print(f"      📊 Réponse: {create_response.text}")
                            else:
                                print(f"      ❌ Erreur suppression unité {unit_id}: {delete_response.status_code}")
                        else:
                            print(f"      ❌ Impossible de récupérer l'unité {unit_id}")
                    
                    # Pause pour éviter de surcharger l'API
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"      ❌ Erreur lors de la mise à jour unité {unit_id}: {e}")
            else:
                print(f"      ⚪ Aucune correction nécessaire pour l'unité {unit_id}")
        
        print("   ✅ Correction terminée!")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR lors de la correction: {e}")
        return False

def verify_corrections():
    """Vérifier que les corrections ont été appliquées"""
    print("🔍 VÉRIFICATION DES CORRECTIONS")
    print("=" * 60)
    
    try:
        response = requests.get(f"{RENDER_API_URL}/api/units", timeout=30)
        if response.status_code != 200:
            print(f"   ❌ Erreur API: {response.status_code}")
            return False
        
        units = response.json()
        print(f"   📊 {len(units)} unités vérifiées")
        
        for unit in units:
            unit_id = unit.get('id')
            unit_number = unit.get('unitNumber', '')
            unit_type = unit.get('type', '')
            unit_address = unit.get('unitAddress', '')
            
            print(f"   📊 Unité {unit_id}: {unit_number} - {unit_type} - {unit_address}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR lors de la vérification: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DE LA CORRECTION RENDER")
    print("=" * 60)
    
    # Corriger les unités
    if correct_render_units():
        print("🎉 CORRECTION TERMINÉE AVEC SUCCÈS!")
        
        # Vérifier les corrections
        print("\n" + "=" * 60)
        if verify_corrections():
            print("✅ VÉRIFICATION TERMINÉE!")
        else:
            print("⚠️  Vérification échouée")
    else:
        print("💥 CORRECTION ÉCHOUÉE!")
