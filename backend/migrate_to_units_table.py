#!/usr/bin/env python3
"""
Script de migration vers la nouvelle table units
Migre les données existantes vers la nouvelle architecture
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, init_database
from database_service import db_service
from models import Building, Tenant, Assignment, Unit, BuildingReport, UnitReport, Invoice
from sqlalchemy import text
import json
import traceback

def migrate_to_units_table():
    """Migrer vers la nouvelle table units"""
    print("🏗️ MIGRATION VERS LA NOUVELLE TABLE UNITS")
    print("=" * 60)
    
    session = db_service.get_session()
    try:
        # 1. Créer la nouvelle table units
        print("1️⃣ Création de la nouvelle table units...")
        
        # Supprimer l'ancienne table si elle existe
        session.execute(text("DROP TABLE IF EXISTS old_assignments"))
        session.execute(text("DROP TABLE IF EXISTS old_unit_reports"))
        session.execute(text("DROP TABLE IF EXISTS units"))
        
        # Créer la nouvelle table units
        session.execute(text("""
            CREATE TABLE units (
                id INTEGER PRIMARY KEY,
                building_id INTEGER NOT NULL,
                unit_number VARCHAR(50) NOT NULL,
                unit_address VARCHAR(255),
                type VARCHAR(50) DEFAULT '1 1/2',
                area INTEGER DEFAULT 0,
                bedrooms INTEGER DEFAULT 1,
                bathrooms INTEGER DEFAULT 1,
                amenities TEXT,
                rental_info TEXT,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE,
                UNIQUE (building_id, unit_number)
            )
        """))
        
        print("   ✅ Table units créée")
        
        # 2. Migrer les données d'unités depuis les assignations
        print("2️⃣ Migration des données d'unités...")
        
        # Récupérer toutes les assignations existantes
        assignments = session.query(Assignment).all()
        units_created = 0
        
        for assignment in assignments:
            # Vérifier si l'unité existe déjà
            existing_unit = session.execute(text("""
                SELECT id FROM units 
                WHERE building_id = :building_id AND unit_number = :unit_number
            """), {
                "building_id": assignment.building_id,
                "unit_number": assignment.unit_number
            }).fetchone()
            
            if not existing_unit:
                # Créer une nouvelle unité
                session.execute(text("""
                    INSERT INTO units (building_id, unit_number, unit_address, type, area, bedrooms, bathrooms, amenities, rental_info, notes, created_at, updated_at)
                    VALUES (:building_id, :unit_number, :unit_address, :type, :area, :bedrooms, :bathrooms, :amenities, :rental_info, :notes, :created_at, :updated_at)
                """), {
                    "building_id": assignment.building_id,
                    "unit_number": assignment.unit_number or f"UNIT-{assignment.id}",
                    "unit_address": assignment.unit_address,
                    "type": "1 1/2",  # Valeur par défaut
                    "area": 0,
                    "bedrooms": 1,
                    "bathrooms": 1,
                    "amenities": json.dumps({}),
                    "rental_info": json.dumps({
                        "monthlyRent": float(assignment.rent_amount) if assignment.rent_amount else 0,
                        "deposit": float(assignment.deposit_amount) if assignment.deposit_amount else 0,
                        "leaseStart": assignment.lease_start_date.isoformat() if assignment.lease_start_date else None,
                        "leaseEnd": assignment.lease_end_date.isoformat() if assignment.lease_end_date else None,
                        "rentDueDay": assignment.rent_due_day or 1
                    }),
                    "notes": assignment.notes or "",
                    "created_at": assignment.created_at or "CURRENT_TIMESTAMP",
                    "updated_at": assignment.updated_at or "CURRENT_TIMESTAMP"
                })
                units_created += 1
        
        print(f"   ✅ {units_created} unités créées")
        
        # 3. Mettre à jour les assignations
        print("3️⃣ Mise à jour des assignations...")
        
        # Créer une table temporaire pour les nouvelles assignations
        session.execute(text("""
            CREATE TABLE new_assignments (
                id INTEGER PRIMARY KEY,
                tenant_id INTEGER NOT NULL,
                unit_id INTEGER NOT NULL,
                move_in_date DATE NOT NULL,
                move_out_date DATE,
                rent_amount DECIMAL(10, 2),
                deposit_amount DECIMAL(10, 2),
                lease_start_date DATE,
                lease_end_date DATE,
                rent_due_day INTEGER DEFAULT 1,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
                FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
            )
        """))
        
        # Migrer les assignations
        for assignment in assignments:
            # Trouver l'ID de l'unité correspondante
            unit_result = session.execute(text("""
                SELECT id FROM units 
                WHERE building_id = :building_id AND unit_number = :unit_number
            """), {
                "building_id": assignment.building_id,
                "unit_number": assignment.unit_number
            }).fetchone()
            
            if unit_result:
                unit_id = unit_result[0]
                
                session.execute(text("""
                    INSERT INTO new_assignments (id, tenant_id, unit_id, move_in_date, move_out_date, rent_amount, deposit_amount, lease_start_date, lease_end_date, rent_due_day, notes, created_at, updated_at)
                    VALUES (:id, :tenant_id, :unit_id, :move_in_date, :move_out_date, :rent_amount, :deposit_amount, :lease_start_date, :lease_end_date, :rent_due_day, :notes, :created_at, :updated_at)
                """), {
                    "id": assignment.id,
                    "tenant_id": assignment.tenant_id,
                    "unit_id": unit_id,
                    "move_in_date": assignment.move_in_date,
                    "move_out_date": assignment.move_out_date,
                    "rent_amount": assignment.rent_amount,
                    "deposit_amount": assignment.deposit_amount,
                    "lease_start_date": assignment.lease_start_date,
                    "lease_end_date": assignment.lease_end_date,
                    "rent_due_day": assignment.rent_due_day,
                    "notes": assignment.notes,
                    "created_at": assignment.created_at,
                    "updated_at": assignment.updated_at
                })
        
        # Remplacer l'ancienne table par la nouvelle
        session.execute(text("DROP TABLE assignments"))
        session.execute(text("ALTER TABLE new_assignments RENAME TO assignments"))
        
        print("   ✅ Assignations mises à jour")
        
        # 4. Mettre à jour les rapports d'unités
        print("4️⃣ Mise à jour des rapports d'unités...")
        
        # Créer une table temporaire pour les nouveaux rapports
        session.execute(text("""
            CREATE TABLE new_unit_reports (
                id INTEGER PRIMARY KEY,
                unit_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                tenant_name VARCHAR(255),
                payment_method VARCHAR(100),
                is_heated_lit BOOLEAN DEFAULT FALSE,
                is_furnished BOOLEAN DEFAULT FALSE,
                wifi_included BOOLEAN DEFAULT FALSE,
                rent_amount DECIMAL(10, 2) DEFAULT 0.0,
                start_date DATE,
                end_date DATE,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE,
                UNIQUE (unit_id, year, month)
            )
        """))
        
        # Migrer les rapports d'unités
        unit_reports = session.query(UnitReport).all()
        for report in unit_reports:
            # Trouver l'ID de l'unité correspondante
            unit_result = session.execute(text("""
                SELECT id FROM units 
                WHERE building_id = :building_id AND unit_number = :unit_number
            """), {
                "building_id": report.building_id,
                "unit_number": report.unit_id  # Dans l'ancien système, unit_id était un string
            }).fetchone()
            
            if unit_result:
                unit_id = unit_result[0]
                
                session.execute(text("""
                    INSERT INTO new_unit_reports (id, unit_id, year, month, tenant_name, payment_method, is_heated_lit, is_furnished, wifi_included, rent_amount, start_date, end_date, notes, created_at, updated_at)
                    VALUES (:id, :unit_id, :year, :month, :tenant_name, :payment_method, :is_heated_lit, :is_furnished, :wifi_included, :rent_amount, :start_date, :end_date, :notes, :created_at, :updated_at)
                """), {
                    "id": report.id,
                    "unit_id": unit_id,
                    "year": report.year,
                    "month": report.month,
                    "tenant_name": report.tenant_name,
                    "payment_method": report.payment_method,
                    "is_heated_lit": report.is_heated_lit,
                    "is_furnished": report.is_furnished,
                    "wifi_included": report.wifi_included,
                    "rent_amount": report.rent_amount,
                    "start_date": report.start_date,
                    "end_date": report.end_date,
                    "notes": report.notes,
                    "created_at": report.created_at,
                    "updated_at": report.updated_at
                })
        
        # Remplacer l'ancienne table par la nouvelle
        session.execute(text("DROP TABLE unit_reports"))
        session.execute(text("ALTER TABLE new_unit_reports RENAME TO unit_reports"))
        
        print("   ✅ Rapports d'unités mis à jour")
        
        # 5. Nettoyer les anciennes colonnes
        print("5️⃣ Nettoyage des anciennes colonnes...")
        
        # Supprimer la colonne unit_data de la table buildings (si elle existe)
        try:
            session.execute(text("ALTER TABLE buildings DROP COLUMN unit_data"))
            print("   ✅ Colonne unit_data supprimée de buildings")
        except:
            print("   ℹ️ Colonne unit_data n'existait pas")
        
        # 6. Vérifier la migration
        print("6️⃣ Vérification de la migration...")
        
        # Compter les données
        buildings_count = session.execute(text("SELECT COUNT(*) FROM buildings")).fetchone()[0]
        units_count = session.execute(text("SELECT COUNT(*) FROM units")).fetchone()[0]
        assignments_count = session.execute(text("SELECT COUNT(*) FROM assignments")).fetchone()[0]
        unit_reports_count = session.execute(text("SELECT COUNT(*) FROM unit_reports")).fetchone()[0]
        
        print(f"   📊 Données migrées:")
        print(f"      - Immeubles: {buildings_count}")
        print(f"      - Unités: {units_count}")
        print(f"      - Assignations: {assignments_count}")
        print(f"      - Rapports d'unités: {unit_reports_count}")
        
        # 7. Commit des changements
        session.commit()
        print("7️⃣ Changements sauvegardés...")
        print("   ✅ Migration terminée avec succès")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE LA MIGRATION: {e}")
        traceback.print_exc()
        session.rollback()
        return False
    finally:
        session.close()

def verify_migration():
    """Vérifier que la migration s'est bien passée"""
    print("\n🔍 VÉRIFICATION DE LA MIGRATION")
    print("=" * 50)
    
    try:
        # Tester les nouvelles relations
        buildings = db_service.get_buildings()
        print(f"📊 Immeubles: {len(buildings)}")
        
        # Tester la création d'une unité
        if buildings:
            test_unit = db_service.create_unit({
                "buildingId": buildings[0]['id'],
                "unitNumber": "TEST-001",
                "unitAddress": "123 Test Street",
                "type": "2 1/2",
                "area": 800,
                "bedrooms": 2,
                "bathrooms": 1
            })
            print(f"✅ Test de création d'unité: ID {test_unit['id']}")
            
            # Supprimer l'unité de test
            db_service.delete_unit(test_unit['id'])
            print("✅ Test de suppression d'unité réussi")
        
        print("\n🎉 MIGRATION VÉRIFIÉE AVEC SUCCÈS !")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE LA VÉRIFICATION: {e}")
        traceback.print_exc()
        return False

def main():
    """Fonction principale de migration"""
    print("🚀 DÉMARRAGE DE LA MIGRATION")
    print("=" * 60)
    print("⚠️  ATTENTION: Cette migration va modifier la structure de la base de données !")
    print("=" * 60)
    
    # Demander confirmation
    try:
        confirmation = input("\nÊtes-vous sûr de vouloir continuer ? (tapez 'OUI' pour confirmer): ")
        if confirmation != "OUI":
            print("❌ Migration annulée par l'utilisateur")
            return False
    except KeyboardInterrupt:
        print("\n❌ Migration annulée par l'utilisateur")
        return False
    
    # Effectuer la migration
    if migrate_to_units_table():
        # Vérifier le résultat
        if verify_migration():
            print("\n🎉 MIGRATION COMPLÈTE RÉUSSI !")
            print("   Votre base de données utilise maintenant la nouvelle architecture avec la table units.")
            return True
        else:
            print("\n💥 MIGRATION INCOMPLÈTE !")
            print("   La migration s'est terminée mais la vérification a échoué.")
            return False
    else:
        print("\n💥 ÉCHEC DE LA MIGRATION !")
        print("   Une erreur s'est produite lors de la migration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
