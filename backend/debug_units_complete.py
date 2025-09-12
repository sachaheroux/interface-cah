#!/usr/bin/env python3
"""
Analyse complète du problème avec les unités
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_imports():
    """Vérifier tous les imports"""
    print("🔍 DIAGNOSTIC DES IMPORTS")
    print("=" * 50)
    
    try:
        print("1️⃣ Import des modèles...")
        from models import Unit, Building, Tenant
        print(f"   ✅ Unit: {Unit}")
        print(f"   ✅ Unit.__name__: {Unit.__name__}")
        print(f"   ✅ Unit.__tablename__: {Unit.__tablename__}")
        
        print("2️⃣ Import du service...")
        from database_service import db_service, DatabaseService
        print(f"   ✅ db_service: {db_service}")
        print(f"   ✅ DatabaseService: {DatabaseService}")
        
        print("3️⃣ Vérification des méthodes...")
        print(f"   ✅ get_units existe: {hasattr(db_service, 'get_units')}")
        print(f"   ✅ get_units callable: {callable(getattr(db_service, 'get_units', None))}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur d'import: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_database():
    """Vérifier la base de données"""
    print("\n🔍 DIAGNOSTIC DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    try:
        from database_service import db_service
        session = db_service.get_session()
        
        print("1️⃣ Vérification de la table units...")
        from sqlalchemy import text
        result = session.execute(text("SELECT COUNT(*) FROM units")).fetchone()
        print(f"   📊 Nombre d'unités: {result[0]}")
        
        print("2️⃣ Vérification des colonnes...")
        columns = session.execute(text("PRAGMA table_info(units)")).fetchall()
        print(f"   📊 Colonnes: {[col[1] for col in columns]}")
        
        print("3️⃣ Vérification des données...")
        units_data = session.execute(text("SELECT id, unit_number, building_id FROM units LIMIT 3")).fetchall()
        print(f"   📊 Données: {units_data}")
        
        session.close()
        return True
    except Exception as e:
        print(f"   ❌ Erreur base de données: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_sqlalchemy():
    """Vérifier SQLAlchemy direct"""
    print("\n🔍 DIAGNOSTIC SQLALCHEMY DIRECT")
    print("=" * 50)
    
    try:
        from database_service import db_service
        from models import Unit
        session = db_service.get_session()
        
        print("1️⃣ Requête SQLAlchemy directe...")
        units = session.query(Unit).all()
        print(f"   📊 Unités trouvées: {len(units)}")
        
        print("2️⃣ Vérification des attributs...")
        if units:
            unit = units[0]
            print(f"   📊 ID: {unit.id}")
            print(f"   📊 Numéro: {unit.unit_number}")
            print(f"   📊 Building ID: {unit.building_id}")
            print(f"   📊 Type: {unit.type}")
        
        print("3️⃣ Test de to_dict...")
        if units:
            try:
                unit_dict = units[0].to_dict()
                print(f"   ✅ to_dict fonctionne: {len(unit_dict)} clés")
            except Exception as e:
                print(f"   ❌ to_dict échoue: {e}")
                import traceback
                traceback.print_exc()
        
        session.close()
        return True
    except Exception as e:
        print(f"   ❌ Erreur SQLAlchemy: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_service_method():
    """Vérifier la méthode du service"""
    print("\n🔍 DIAGNOSTIC DE LA MÉTHODE DU SERVICE")
    print("=" * 50)
    
    try:
        from database_service import db_service
        
        print("1️⃣ Vérification de la méthode...")
        method = getattr(db_service, 'get_units', None)
        print(f"   📊 Méthode: {method}")
        print(f"   📊 Type: {type(method)}")
        print(f"   📊 Callable: {callable(method)}")
        
        print("2️⃣ Vérification du code source...")
        import inspect
        source = inspect.getsource(method)
        print(f"   📊 Code source (premiers 200 chars): {source[:200]}...")
        
        print("3️⃣ Test d'appel...")
        print("   🔍 Appel de db_service.get_units()...")
        result = db_service.get_units()
        print(f"   📊 Résultat: {len(result)} unités")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur méthode service: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_alternative():
    """Test alternatif"""
    print("\n🔍 TEST ALTERNATIF")
    print("=" * 50)
    
    try:
        from database_service import db_service
        from models import Unit
        
        print("1️⃣ Création d'une nouvelle instance...")
        from database_service import DatabaseService
        new_service = DatabaseService()
        
        print("2️⃣ Test avec nouvelle instance...")
        result = new_service.get_units()
        print(f"   📊 Résultat nouvelle instance: {len(result)} unités")
        
        print("3️⃣ Test direct de la méthode...")
        session = new_service.get_session()
        units = session.query(Unit).all()
        print(f"   📊 Unités directes: {len(units)}")
        session.close()
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur test alternatif: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale de diagnostic"""
    print("🚀 DIAGNOSTIC COMPLET DU PROBLÈME UNITS")
    print("=" * 60)
    
    results = []
    results.append(debug_imports())
    results.append(debug_database())
    results.append(debug_sqlalchemy())
    results.append(debug_service_method())
    results.append(debug_alternative())
    
    print("\n📊 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 30)
    print(f"Imports: {'✅' if results[0] else '❌'}")
    print(f"Base de données: {'✅' if results[1] else '❌'}")
    print(f"SQLAlchemy direct: {'✅' if results[2] else '❌'}")
    print(f"Méthode service: {'✅' if results[3] else '❌'}")
    print(f"Test alternatif: {'✅' if results[4] else '❌'}")
    
    if all(results):
        print("\n🎉 TOUS LES TESTS RÉUSSIS - Le problème est ailleurs")
    else:
        print("\n💥 PROBLÈME IDENTIFIÉ - Voir les détails ci-dessus")

if __name__ == "__main__":
    main()
