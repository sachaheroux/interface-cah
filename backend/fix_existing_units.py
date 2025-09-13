#!/usr/bin/env python3
"""
Script pour corriger les unités existantes
- Changer le type de 1 1/2 à 4 1/2
- Corriger les adresses doublées
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, init_database
from database_service import db_service
from models import Unit
from sqlalchemy import text
import traceback

def fix_existing_units():
    """Corriger les unités existantes"""
    print("🔧 CORRECTION DES UNITÉS EXISTANTES")
    print("=" * 60)
    
    session = db_service.get_session()
    try:
        # 1. Récupérer toutes les unités
        print("1️⃣ Récupération des unités existantes...")
        
        units = session.query(Unit).all()
        print(f"   📊 {len(units)} unités trouvées")
        
        if not units:
            print("   ✅ Aucune unité à corriger")
            return True
        
        # 2. Corriger chaque unité
        print("2️⃣ Correction des unités...")
        
        for unit in units:
            print(f"   🔄 Unité {unit.id}: {unit.unit_number}")
            
            # Corriger le type (1 1/2 → 4 1/2)
            if unit.type == "1 1/2":
                unit.type = "4 1/2"
                print(f"      ✅ Type changé: 1 1/2 → 4 1/2")
            
            # Corriger l'adresse doublée
            if unit.unit_address and ' ' in unit.unit_address:
                parts = unit.unit_address.split(' ', 1)
                if len(parts) == 2:
                    unit_num = parts[0]
                    street_part = parts[1]
                    
                    # Vérifier si c'est une adresse doublée (ex: "56 56-58-60-62 rue Vachon")
                    if '-' in street_part and street_part.split(' ')[0].replace('-', '').isdigit():
                        # Extraire le nom de la rue (après le premier espace)
                        street_parts = street_part.split(' ', 1)
                        if len(street_parts) > 1:
                            street_name = street_parts[1]
                            unit.unit_address = f"{unit_num} {street_name}"
                            print(f"      ✅ Adresse corrigée: {unit.unit_address}")
            
            # Mettre à jour la date de modification
            from datetime import datetime
            unit.updated_at = datetime.utcnow()
        
        # 3. Sauvegarder les changements
        print("3️⃣ Sauvegarde des changements...")
        
        session.commit()
        print("   ✅ Changements sauvegardés")
        
        # 4. Vérifier le résultat
        print("4️⃣ Vérification du résultat...")
        
        corrected_units = session.query(Unit).all()
        for unit in corrected_units:
            print(f"   📊 Unité {unit.id}: {unit.unit_number} - {unit.type} - {unit.unit_address}")
        
        print("   ✅ Correction terminée avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR lors de la correction: {e}")
        print(f"📊 Traceback: {traceback.format_exc()}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DE LA CORRECTION")
    print("=" * 60)
    
    if init_database():
        print("✅ Base de données initialisée")
        
        if fix_existing_units():
            print("🎉 CORRECTION TERMINÉE AVEC SUCCÈS!")
        else:
            print("💥 CORRECTION ÉCHOUÉE!")
    else:
        print("❌ Impossible d'initialiser la base de données")
