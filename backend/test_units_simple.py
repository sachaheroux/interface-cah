#!/usr/bin/env python3
"""
Test simple pour isoler le problème avec get_units
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, init_database
from database_service import db_service
from models import Unit
from sqlalchemy import text

def test_units_simple():
    """Test simple des unités"""
    print("🧪 TEST SIMPLE DES UNITÉS")
    print("=" * 40)
    
    session = db_service.get_session()
    try:
        # 1. Vérifier que la table existe
        print("1️⃣ Vérification de la table...")
        result = session.execute(text("SELECT COUNT(*) FROM units")).fetchone()
        print(f"   📊 Nombre d'unités dans la table: {result[0]}")
        
        # 2. Test direct avec SQLAlchemy
        print("2️⃣ Test direct avec SQLAlchemy...")
        units = session.query(Unit).all()
        print(f"   📊 Unités trouvées avec SQLAlchemy: {len(units)}")
        for unit in units:
            print(f"   - ID: {unit.id}, Numéro: {unit.unit_number}, Building: {unit.building_id}")
        
        # 3. Test avec le service
        print("3️⃣ Test avec le service...")
        try:
            print("   🔍 Debug - Appel de db_service.get_units()...")
            service_units = db_service.get_units()
            print(f"   📊 Unités trouvées avec le service: {len(service_units)}")
        except Exception as e:
            print(f"   ❌ Erreur avec le service: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. Test direct de la méthode
        print("4️⃣ Test direct de la méthode...")
        try:
            print("   🔍 Debug - Appel direct de get_units...")
            from database_service import DatabaseService
            new_service = DatabaseService()
            direct_units = new_service.get_units()
            print(f"   📊 Unités trouvées avec nouveau service: {len(direct_units)}")
        except Exception as e:
            print(f"   ❌ Erreur avec nouveau service: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    test_units_simple()
