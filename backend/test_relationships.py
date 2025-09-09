#!/usr/bin/env python3
"""
Test de validation des relations entre les données SQLite
"""

import json
from datetime import datetime
from database import db_manager
from database_service import db_service

def test_building_tenant_relationships():
    """Tester les relations immeubles-locataires"""
    print("🏢 TEST DES RELATIONS IMMEUBLES-LOCATAIRES")
    print("=" * 50)
    
    try:
        # 1. Créer un immeuble
        print("1️⃣ Création d'un immeuble...")
        building_data = {
            "name": "Immeuble Test Relations",
            "address": {
                "street": "123 Rue Test",
                "city": "Montréal",
                "province": "QC",
                "postalCode": "H1A 1A1",
                "country": "Canada"
            },
            "type": "Résidentiel",
            "units": 3,
            "floors": 2,
            "yearBuilt": 2023,
            "totalArea": 800,
            "notes": "Immeuble de test pour les relations"
        }
        
        building = db_service.create_building(building_data)
        building_id = building["id"]
        print(f"✅ Immeuble créé avec ID: {building_id}")
        
        # 2. Créer des locataires
        print("\n2️⃣ Création de locataires...")
        tenants_data = [
            {
                "name": "Jean Dupont",
                "email": "jean.dupont@test.com",
                "phone": "(514) 555-0001",
                "status": "active",
                "notes": "Locataire test 1"
            },
            {
                "name": "Marie Martin",
                "email": "marie.martin@test.com",
                "phone": "(514) 555-0002",
                "status": "active",
                "notes": "Locataire test 2"
            }
        ]
        
        tenant_ids = []
        for tenant_data in tenants_data:
            tenant = db_service.create_tenant(tenant_data)
            tenant_ids.append(tenant["id"])
            print(f"✅ Locataire créé avec ID: {tenant['id']} - {tenant['name']}")
        
        # 3. Créer des assignations (relations)
        print("\n3️⃣ Création d'assignations...")
        assignments_data = [
            {
                "tenantId": tenant_ids[0],
                "buildingId": building_id,
                "unitId": "101",
                "unitNumber": "101",
                "unitAddress": "123 Rue Test, Montréal, QC",
                "moveInDate": datetime.now().isoformat(),
                "rentAmount": 1200.00,
                "depositAmount": 600.00,
                "leaseStartDate": datetime.now().isoformat(),
                "leaseEndDate": (datetime.now().replace(year=datetime.now().year + 1)).isoformat(),
                "rentDueDay": 1,
                "notes": "Assignation test 1"
            },
            {
                "tenantId": tenant_ids[1],
                "buildingId": building_id,
                "unitId": "102",
                "unitNumber": "102",
                "unitAddress": "123 Rue Test, Montréal, QC",
                "moveInDate": datetime.now().isoformat(),
                "rentAmount": 1300.00,
                "depositAmount": 650.00,
                "leaseStartDate": datetime.now().isoformat(),
                "leaseEndDate": (datetime.now().replace(year=datetime.now().year + 1)).isoformat(),
                "rentDueDay": 1,
                "notes": "Assignation test 2"
            }
        ]
        
        assignment_ids = []
        for assignment_data in assignments_data:
            assignment = db_service.create_assignment(assignment_data)
            assignment_ids.append(assignment["id"])
            print(f"✅ Assignation créée avec ID: {assignment['id']}")
        
        # 4. Vérifier les relations
        print("\n4️⃣ Vérification des relations...")
        
        # Récupérer l'immeuble avec ses relations
        building_with_relations = db_service.get_building(building_id)
        print(f"✅ Immeuble récupéré: {building_with_relations['name']}")
        
        # Récupérer les locataires
        tenants = db_service.get_tenants()
        print(f"✅ {len(tenants)} locataires trouvés")
        
        # Récupérer les assignations
        assignments = db_service.get_assignments()
        print(f"✅ {len(assignments)} assignations trouvées")
        
        # Vérifier la cohérence des données
        print("\n5️⃣ Vérification de la cohérence...")
        
        # Vérifier que les assignations pointent vers des locataires existants
        for assignment in assignments:
            tenant_id = assignment.get('tenantId')
            if tenant_id:
                tenant = db_service.get_tenant(tenant_id)
                if tenant:
                    print(f"✅ Assignation {assignment['id']} → Locataire {tenant['name']}")
                else:
                    print(f"❌ Assignation {assignment['id']} → Locataire {tenant_id} INEXISTANT")
        
        print("\n🎉 TEST DES RELATIONS RÉUSSI !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des relations: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_integrity():
    """Tester l'intégrité des données"""
    print("\n🔍 TEST D'INTÉGRITÉ DES DONNÉES")
    print("=" * 50)
    
    try:
        # Vérifier les contraintes de clés étrangères
        print("1️⃣ Vérification des contraintes de clés étrangères...")
        if db_manager.connect():
            cursor = db_manager.connection.cursor()
            cursor.execute("PRAGMA foreign_key_check")
            fk_errors = cursor.fetchall()
            
            if fk_errors:
                print(f"❌ {len(fk_errors)} violations de clés étrangères trouvées")
                for error in fk_errors:
                    print(f"   - {error}")
                return False
            else:
                print("✅ Aucune violation de clés étrangères")
            
            db_manager.disconnect()
        
        # Vérifier la cohérence des données
        print("\n2️⃣ Vérification de la cohérence des données...")
        
        # Compter les enregistrements
        buildings = db_service.get_buildings()
        tenants = db_service.get_tenants()
        assignments = db_service.get_assignments()
        
        print(f"   📊 Immeubles: {len(buildings)}")
        print(f"   👥 Locataires: {len(tenants)}")
        print(f"   🔗 Assignations: {len(assignments)}")
        
        # Vérifier que les assignations pointent vers des locataires existants
        orphaned_assignments = 0
        for assignment in assignments:
            tenant_id = assignment.get('tenantId')
            if tenant_id:
                tenant = db_service.get_tenant(tenant_id)
                if not tenant:
                    orphaned_assignments += 1
                    print(f"   ⚠️ Assignation orpheline: {assignment['id']} → Locataire {tenant_id} inexistant")
        
        if orphaned_assignments == 0:
            print("✅ Aucune assignation orpheline")
        else:
            print(f"❌ {orphaned_assignments} assignations orphelines")
            return False
        
        print("\n🎉 TEST D'INTÉGRITÉ RÉUSSI !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'intégrité: {e}")
        return False

def test_crud_operations():
    """Tester les opérations CRUD"""
    print("\n🔄 TEST DES OPÉRATIONS CRUD")
    print("=" * 50)
    
    try:
        # Test CREATE
        print("1️⃣ Test CREATE...")
        building_data = {
            "name": "Immeuble CRUD Test",
            "address": {
                "street": "456 Rue CRUD",
                "city": "Montréal",
                "province": "QC",
                "postalCode": "H2B 2B2",
                "country": "Canada"
            },
            "type": "Commercial",
            "units": 5,
            "floors": 3,
            "yearBuilt": 2024,
            "totalArea": 1200,
            "notes": "Test CRUD"
        }
        
        building = db_service.create_building(building_data)
        building_id = building["id"]
        print(f"✅ CREATE réussi - ID: {building_id}")
        
        # Test READ
        print("\n2️⃣ Test READ...")
        retrieved_building = db_service.get_building(building_id)
        if retrieved_building and retrieved_building["name"] == "Immeuble CRUD Test":
            print("✅ READ réussi")
        else:
            print("❌ READ échoué")
            return False
        
        # Test UPDATE
        print("\n3️⃣ Test UPDATE...")
        update_data = {"name": "Immeuble CRUD Test Modifié"}
        updated_building = db_service.update_building(building_id, update_data)
        if updated_building and updated_building["name"] == "Immeuble CRUD Test Modifié":
            print("✅ UPDATE réussi")
        else:
            print("❌ UPDATE échoué")
            return False
        
        # Test DELETE
        print("\n4️⃣ Test DELETE...")
        success = db_service.delete_building(building_id)
        if success:
            print("✅ DELETE réussi")
        else:
            print("❌ DELETE échoué")
            return False
        
        # Vérifier que l'immeuble est supprimé
        deleted_building = db_service.get_building(building_id)
        if deleted_building is None:
            print("✅ Vérification suppression réussie")
        else:
            print("❌ L'immeuble n'a pas été supprimé")
            return False
        
        print("\n🎉 TEST CRUD RÉUSSI !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test CRUD: {e}")
        return False

def test_data_consistency():
    """Tester la cohérence des données"""
    print("\n📊 TEST DE COHÉRENCE DES DONNÉES")
    print("=" * 50)
    
    try:
        # Créer des données de test avec relations
        print("1️⃣ Création de données de test...")
        
        # Immeuble
        building = db_service.create_building({
            "name": "Immeuble Cohérence",
            "address": {"street": "789 Rue Cohérence", "city": "Montréal", "province": "QC", "postalCode": "H3C 3C3", "country": "Canada"},
            "type": "Résidentiel",
            "units": 2,
            "floors": 1,
            "yearBuilt": 2023,
            "totalArea": 600,
            "notes": "Test cohérence"
        })
        
        # Locataires
        tenant1 = db_service.create_tenant({
            "name": "Alice Test",
            "email": "alice@test.com",
            "phone": "(514) 555-1001",
            "status": "active"
        })
        
        tenant2 = db_service.create_tenant({
            "name": "Bob Test",
            "email": "bob@test.com",
            "phone": "(514) 555-1002",
            "status": "active"
        })
        
        # Assignations
        assignment1 = db_service.create_assignment({
            "tenantId": tenant1["id"],
            "buildingId": building["id"],
            "unitId": "201",
            "unitNumber": "201",
            "unitAddress": "456 Rue Cohérence, Montréal, QC",
            "moveInDate": datetime.now().isoformat(),
            "rentAmount": 1400.00,
            "depositAmount": 700.00,
            "leaseStartDate": datetime.now().isoformat(),
            "leaseEndDate": (datetime.now().replace(year=datetime.now().year + 1)).isoformat(),
            "rentDueDay": 1,
            "notes": "Test cohérence 1"
        })
        
        assignment2 = db_service.create_assignment({
            "tenantId": tenant2["id"],
            "buildingId": building["id"],
            "unitId": "202",
            "unitNumber": "202",
            "unitAddress": "456 Rue Cohérence, Montréal, QC",
            "moveInDate": datetime.now().isoformat(),
            "rentAmount": 1500.00,
            "depositAmount": 750.00,
            "leaseStartDate": datetime.now().isoformat(),
            "leaseEndDate": (datetime.now().replace(year=datetime.now().year + 1)).isoformat(),
            "rentDueDay": 1,
            "notes": "Test cohérence 2"
        })
        
        print("✅ Données de test créées")
        
        # Vérifier la cohérence
        print("\n2️⃣ Vérification de la cohérence...")
        
        # Vérifier que les assignations pointent vers des locataires existants
        assignments = db_service.get_assignments()
        for assignment in assignments:
            tenant_id = assignment.get('tenantId')
            if tenant_id:
                tenant = db_service.get_tenant(tenant_id)
                if tenant:
                    print(f"✅ Assignation {assignment['id']} → Locataire {tenant['name']}")
                else:
                    print(f"❌ Assignation {assignment['id']} → Locataire {tenant_id} INEXISTANT")
                    return False
        
        # Vérifier que les données sont cohérentes
        print("\n3️⃣ Vérification des données...")
        
        # Compter les enregistrements
        buildings = db_service.get_buildings()
        tenants = db_service.get_tenants()
        assignments = db_service.get_assignments()
        
        print(f"   📊 Immeubles: {len(buildings)}")
        print(f"   👥 Locataires: {len(tenants)}")
        print(f"   🔗 Assignations: {len(assignments)}")
        
        # Vérifier que les relations sont correctes
        if len(assignments) >= 2 and len(tenants) >= 2:
            print("✅ Relations correctes")
        else:
            print("❌ Relations incorrectes")
            return False
        
        print("\n🎉 TEST DE COHÉRENCE RÉUSSI !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de cohérence: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST COMPLET DE LA LOGIQUE SQL ET DES RELATIONS")
    print("=" * 70)
    
    tests = [
        ("Relations immeubles-locataires", test_building_tenant_relationships),
        ("Intégrité des données", test_data_integrity),
        ("Opérations CRUD", test_crud_operations),
        ("Cohérence des données", test_data_consistency)
    ]
    
    success_count = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            success_count += 1
            print(f"✅ {test_name}: RÉUSSI")
        else:
            print(f"❌ {test_name}: ÉCHOUÉ")
    
    print(f"\n📊 RÉSULTATS: {success_count}/{len(tests)} tests réussis")
    
    if success_count == len(tests):
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ La logique SQL fonctionne correctement")
        print("✅ Les relations entre données sont préservées")
        print("✅ L'intégrité des données est assurée")
        print("✅ Les opérations CRUD fonctionnent")
        print("✅ La cohérence des données est maintenue")
    else:
        print("\n⚠️ Certains tests ont échoué")
        print("❌ Vérifiez les erreurs ci-dessus")

if __name__ == "__main__":
    main()
