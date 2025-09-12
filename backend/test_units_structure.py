#!/usr/bin/env python3
"""
Script de test pour la nouvelle structure avec table units
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, init_database
from database_service import db_service
from models import Building, Tenant, Unit, Assignment, BuildingReport, UnitReport, Invoice
from sqlalchemy import text
import json
import traceback

def test_units_structure():
    """Tester la nouvelle structure avec table units"""
    print("🧪 TEST DE LA NOUVELLE STRUCTURE UNITS")
    print("=" * 60)
    
    session = db_service.get_session()
    try:
        # 1. Vérifier que la table units existe
        print("1️⃣ Vérification de la table units...")
        
        result = session.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='units'
        """)).fetchone()
        
        if not result:
            print("   ❌ Table units n'existe pas - Migration nécessaire")
            return False
        
        print("   ✅ Table units existe")
        
        # 2. Vérifier la structure de la table
        print("2️⃣ Vérification de la structure...")
        
        columns = session.execute(text("PRAGMA table_info(units)")).fetchall()
        expected_columns = [
            'id', 'building_id', 'unit_number', 'unit_address', 'type', 
            'area', 'bedrooms', 'bathrooms', 'amenities', 'rental_info', 
            'notes', 'created_at', 'updated_at'
        ]
        
        actual_columns = [col[1] for col in columns]
        missing_columns = set(expected_columns) - set(actual_columns)
        
        if missing_columns:
            print(f"   ❌ Colonnes manquantes: {missing_columns}")
            return False
        
        print("   ✅ Structure de la table correcte")
        
        # 3. Tester la création d'un immeuble
        print("3️⃣ Test de création d'immeuble...")
        
        building_data = {
            "name": "Immeuble Test",
            "address": {
                "street": "123 Test Street",
                "city": "Montréal",
                "province": "QC",
                "postalCode": "H1H 1H1",
                "country": "Canada"
            },
            "type": "Résidentiel",
            "units": 2,
            "floors": 1,
            "yearBuilt": 2020,
            "totalArea": 2000,
            "characteristics": {
                "heating": "Électrique",
                "parking": "Oui"
            },
            "financials": {
                "purchasePrice": 500000,
                "currentValue": 600000
            },
            "contacts": {
                "manager": "Jean Dupont",
                "phone": "514-123-4567"
            },
            "notes": "Immeuble de test"
        }
        
        building = db_service.create_building(building_data)
        building_id = building['id']
        print(f"   ✅ Immeuble créé: ID {building_id}")
        
        # 4. Tester la création d'unités
        print("4️⃣ Test de création d'unités...")
        
        # Unité 1
        unit1_data = {
            "buildingId": building_id,
            "unitNumber": "101",
            "unitAddress": "123 Test Street, Apt 101",
            "type": "2 1/2",
            "area": 800,
            "bedrooms": 2,
            "bathrooms": 1,
            "amenities": {
                "heating": True,
                "electricity": True,
                "wifi": False,
                "furnished": False,
                "parking": True
            },
            "rentalInfo": {
                "monthlyRent": 1200,
                "deposit": 600,
                "leaseStart": "2024-01-01",
                "leaseEnd": "2024-12-31",
                "rentDueDay": 1
            },
            "notes": "Unité de test 1"
        }
        
        unit1 = db_service.create_unit(unit1_data)
        unit1_id = unit1['id']
        print(f"   ✅ Unité 1 créée: ID {unit1_id}")
        
        # Unité 2
        unit2_data = {
            "buildingId": building_id,
            "unitNumber": "102",
            "unitAddress": "123 Test Street, Apt 102",
            "type": "3 1/2",
            "area": 1000,
            "bedrooms": 3,
            "bathrooms": 1,
            "amenities": {
                "heating": True,
                "electricity": True,
                "wifi": True,
                "furnished": True,
                "parking": True
            },
            "rentalInfo": {
                "monthlyRent": 1500,
                "deposit": 750,
                "leaseStart": "2024-02-01",
                "leaseEnd": "2025-01-31",
                "rentDueDay": 1
            },
            "notes": "Unité de test 2"
        }
        
        unit2 = db_service.create_unit(unit2_data)
        unit2_id = unit2['id']
        print(f"   ✅ Unité 2 créée: ID {unit2_id}")
        
        # 5. Tester la récupération des unités
        print("5️⃣ Test de récupération des unités...")
        
        # Toutes les unités
        print("   🔍 Debug - Appel de get_units()...")
        all_units = db_service.get_units()
        print(f"   ✅ {len(all_units)} unités récupérées")
        
        # Unités par immeuble
        building_units = db_service.get_units_by_building(building_id)
        print(f"   ✅ {len(building_units)} unités pour l'immeuble {building_id}")
        
        # Debug: Vérifier les IDs
        print(f"   🔍 Debug - unit1_id: {unit1_id}, unit2_id: {unit2_id}")
        print(f"   🔍 Debug - building_id: {building_id}")
        
        # Unité spécifique
        unit = db_service.get_unit(unit1_id)
        if unit:
            print(f"   ✅ Unité {unit1_id} récupérée: {unit['unitNumber']}")
        else:
            print(f"   ❌ Unité {unit1_id} non trouvée")
            # Essayer de récupérer toutes les unités pour debug
            debug_units = db_service.get_units()
            print(f"   🔍 Debug - Toutes les unités: {[u['id'] for u in debug_units]}")
            return False
        
        # 6. Tester la création d'un locataire
        print("6️⃣ Test de création de locataire...")
        
        tenant_data = {
            "name": "Jean Dupont",
            "email": "jean.dupont@email.com",
            "phone": "514-123-4567",
            "address": {
                "street": "456 Locataire Street",
                "city": "Montréal",
                "province": "QC",
                "postalCode": "H2H 2H2",
                "country": "Canada"
            },
            "personalInfo": {
                "dateOfBirth": "1990-01-01",
                "occupation": "Développeur",
                "employer": "Tech Corp"
            },
            "emergencyContact": {
                "name": "Marie Dupont",
                "relationship": "Épouse",
                "phone": "514-987-6543"
            },
            "financial": {
                "income": 5000,
                "creditScore": 750
            },
            "notes": "Locataire de test"
        }
        
        tenant = db_service.create_tenant(tenant_data)
        tenant_id = tenant['id']
        print(f"   ✅ Locataire créé: ID {tenant_id}")
        
        # 7. Tester la création d'une assignation
        print("7️⃣ Test de création d'assignation...")
        
        assignment_data = {
            "tenantId": tenant_id,
            "unitId": unit1_id,
            "moveInDate": "2024-01-01",
            "moveOutDate": None,
            "rentAmount": 1200,
            "depositAmount": 600,
            "leaseStartDate": "2024-01-01",
            "leaseEndDate": "2024-12-31",
            "rentDueDay": 1,
            "notes": "Assignation de test"
        }
        
        assignment = db_service.create_assignment(assignment_data)
        assignment_id = assignment['id']
        print(f"   ✅ Assignation créée: ID {assignment_id}")
        
        # 8. Vérifier les relations
        print("8️⃣ Vérification des relations...")
        
        # Vérifier que l'assignation a les bonnes relations
        if assignment['tenantId'] == tenant_id:
            print("   ✅ Relation tenant correcte")
        else:
            print(f"   ❌ Relation tenant incorrecte: {assignment['tenantId']} != {tenant_id}")
            return False
        
        if assignment['unitId'] == unit1_id:
            print("   ✅ Relation unit correcte")
        else:
            print(f"   ❌ Relation unit incorrecte: {assignment['unitId']} != {unit1_id}")
            return False
        
        # Vérifier que l'unité a l'assignation
        unit_with_assignments = db_service.get_unit(unit1_id)
        if 'assignments' in unit_with_assignments:
            print("   ✅ Relations bidirectionnelles fonctionnent")
        else:
            print("   ℹ️ Relations bidirectionnelles non testées (normal)")
        
        # 9. Tester la création d'un rapport d'unité
        print("9️⃣ Test de création de rapport d'unité...")
        
        report_data = {
            "unitId": unit1_id,
            "year": 2024,
            "month": 1,
            "tenantName": "Jean Dupont",
            "paymentMethod": "Virement bancaire",
            "isHeatedLit": True,
            "isFurnished": False,
            "wifiIncluded": False,
            "rentAmount": 1200,
            "startDate": "2024-01-01",
            "endDate": "2024-01-31",
            "notes": "Rapport de test"
        }
        
        report = db_service.create_unit_report(report_data)
        report_id = report['id']
        print(f"   ✅ Rapport d'unité créé: ID {report_id}")
        
        # 10. Vérifier les contraintes
        print("🔟 Test des contraintes...")
        
        # Tenter de créer une unité avec le même numéro dans le même immeuble
        try:
            duplicate_unit_data = {
                "buildingId": building_id,
                "unitNumber": "101",  # Même numéro que unit1
                "unitAddress": "123 Test Street, Apt 101",
                "type": "1 1/2"
            }
            db_service.create_unit(duplicate_unit_data)
            print("   ❌ Contrainte unique non respectée")
            return False
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                print("   ✅ Contrainte unique respectée")
            else:
                print(f"   ❌ Erreur inattendue: {e}")
                return False
        
        # 11. Nettoyage
        print("1️⃣1️⃣ Nettoyage des données de test...")
        
        # Supprimer dans l'ordre inverse des dépendances
        db_service.delete_unit_report(report_id)
        db_service.delete_assignment(assignment_id)
        db_service.delete_tenant(tenant_id)
        db_service.delete_unit(unit1_id)
        db_service.delete_unit(unit2_id)
        db_service.delete_building(building_id)
        
        print("   ✅ Données de test supprimées")
        
        # 12. Résumé
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("   ✅ Table units créée et fonctionnelle")
        print("   ✅ Relations correctes")
        print("   ✅ Contraintes respectées")
        print("   ✅ CRUD operations fonctionnelles")
        print("   ✅ Architecture améliorée")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DU TEST: {e}")
        traceback.print_exc()
        return False
    finally:
        session.close()

def main():
    """Fonction principale de test"""
    print("🚀 DÉMARRAGE DES TESTS")
    print("=" * 60)
    
    if test_units_structure():
        print("\n🎉 MIGRATION ET TESTS RÉUSSIS !")
        print("   Votre système utilise maintenant la nouvelle architecture avec la table units.")
        return True
    else:
        print("\n💥 ÉCHEC DES TESTS !")
        print("   Des problèmes ont été détectés.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
