#!/usr/bin/env python3
"""
Script de migration des données JSON vers SQLite
Usage: python migrate_to_sqlite.py
"""

import os
import json
import sys
from datetime import datetime
from database import db_manager, init_database

# Configuration des chemins (même que dans main.py)
if os.environ.get("ENVIRONMENT") == "development" or os.name == 'nt':
    DATA_DIR = os.environ.get("DATA_DIR", "./data")
else:
    DATA_DIR = os.environ.get("DATA_DIR", "/opt/render/project/src/data")

# Chemins des fichiers JSON existants
BUILDINGS_DATA_FILE = os.path.join(DATA_DIR, "buildings_data.json")
TENANTS_DATA_FILE = os.path.join(DATA_DIR, "tenants_data.json")
ASSIGNMENTS_DATA_FILE = os.path.join(DATA_DIR, "assignments_data.json")
BUILDING_REPORTS_DATA_FILE = os.path.join(DATA_DIR, "building_reports_data.json")
UNIT_REPORTS_DATA_FILE = os.path.join(DATA_DIR, "unit_reports_data.json")
INVOICES_DATA_FILE = os.path.join(DATA_DIR, "invoices_data.json")

def load_json_data(file_path: str, default_structure: dict):
    """Charger les données JSON avec structure par défaut"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Données chargées depuis {file_path}: {len(data.get(list(default_structure.keys())[0], []))} éléments")
                return data
        else:
            print(f"⚠️ Fichier {file_path} n'existe pas, utilisation de la structure par défaut")
            return default_structure
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {file_path}: {e}")
        return default_structure

def migrate_buildings():
    """Migrer les immeubles vers SQLite"""
    print("\n🏢 Migration des immeubles...")
    
    buildings_data = load_json_data(BUILDINGS_DATA_FILE, {"buildings": [], "next_id": 1})
    buildings = buildings_data.get("buildings", [])
    
    if not buildings:
        print("⚠️ Aucun immeuble à migrer")
        return True
    
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        for building in buildings:
            # Extraire l'adresse
            address = building.get("address", {})
            if isinstance(address, dict):
                address_street = address.get("street", "")
                address_city = address.get("city", "")
                address_province = address.get("province", "")
                address_postal_code = address.get("postalCode", "")
                address_country = address.get("country", "Canada")
            else:
                address_street = str(address) if address else ""
                address_city = ""
                address_province = ""
                address_postal_code = ""
                address_country = "Canada"
            
            # Extraire les caractéristiques
            characteristics = building.get("characteristics", {})
            characteristics_json = json.dumps(characteristics) if characteristics else None
            
            # Extraire les informations financières
            financials = building.get("financials", {})
            financials_json = json.dumps(financials) if financials else None
            
            # Extraire les contacts
            contacts = building.get("contacts", {})
            contacts_json = json.dumps(contacts) if contacts else None
            
            # Extraire les données d'unités
            unit_data = building.get("unitData", {})
            unit_data_json = json.dumps(unit_data) if unit_data else None
            
            # Déterminer si c'est un immeuble par défaut
            is_default = building.get("id", 0) <= 3
            
            cursor.execute("""
                INSERT OR REPLACE INTO buildings (
                    id, name, address_street, address_city, address_province,
                    address_postal_code, address_country, type, units, floors,
                    year_built, total_area, characteristics, financials,
                    contacts, unit_data, notes, is_default, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                building.get("id"),
                building.get("name", ""),
                address_street,
                address_city,
                address_province,
                address_postal_code,
                address_country,
                building.get("type", ""),
                building.get("units", 0),
                building.get("floors", 1),
                building.get("yearBuilt"),
                building.get("totalArea"),
                characteristics_json,
                financials_json,
                contacts_json,
                unit_data_json,
                building.get("notes", ""),
                is_default,
                building.get("createdAt"),
                building.get("updatedAt")
            ))
        
        db_manager.connection.commit()
        print(f"✅ {len(buildings)} immeubles migrés avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration des immeubles : {e}")
        db_manager.connection.rollback()
        return False
    finally:
        db_manager.disconnect()

def migrate_tenants():
    """Migrer les locataires vers SQLite"""
    print("\n👥 Migration des locataires...")
    
    tenants_data = load_json_data(TENANTS_DATA_FILE, {"tenants": [], "next_id": 1})
    tenants = tenants_data.get("tenants", [])
    
    if not tenants:
        print("⚠️ Aucun locataire à migrer")
        return True
    
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        for tenant in tenants:
            # Extraire les informations financières
            financial_info = tenant.get("financial", {})
            financial_json = json.dumps(financial_info) if financial_info else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO tenants (
                    id, name, email, phone, emergency_contact_name,
                    emergency_contact_phone, emergency_contact_relationship,
                    move_in_date, move_out_date, financial_info, notes,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tenant.get("id"),
                tenant.get("name", ""),
                tenant.get("email"),
                tenant.get("phone"),
                tenant.get("emergencyContact", {}).get("name"),
                tenant.get("emergencyContact", {}).get("phone"),
                tenant.get("emergencyContact", {}).get("relationship"),
                tenant.get("moveInDate"),
                tenant.get("moveOutDate"),
                financial_json,
                tenant.get("notes", ""),
                tenant.get("createdAt"),
                tenant.get("updatedAt")
            ))
        
        db_manager.connection.commit()
        print(f"✅ {len(tenants)} locataires migrés avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration des locataires : {e}")
        db_manager.connection.rollback()
        return False
    finally:
        db_manager.disconnect()

def migrate_assignments():
    """Migrer les assignations vers SQLite"""
    print("\n🔗 Migration des assignations...")
    
    assignments_data = load_json_data(ASSIGNMENTS_DATA_FILE, {"assignments": [], "next_id": 1})
    assignments = assignments_data.get("assignments", [])
    
    if not assignments:
        print("⚠️ Aucune assignation à migrer")
        return True
    
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        for assignment in assignments:
            cursor.execute("""
                INSERT OR REPLACE INTO assignments (
                    id, tenant_id, building_id, unit_id, unit_number,
                    unit_address, move_in_date, move_out_date, rent_amount,
                    deposit_amount, lease_start_date, lease_end_date,
                    rent_due_day, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assignment.get("id"),
                assignment.get("tenantId"),
                assignment.get("buildingId"),
                assignment.get("unitId"),
                assignment.get("unitNumber"),
                assignment.get("unitAddress"),
                assignment.get("moveInDate"),
                assignment.get("moveOutDate"),
                assignment.get("rentAmount"),
                assignment.get("depositAmount"),
                assignment.get("leaseStartDate"),
                assignment.get("leaseEndDate"),
                assignment.get("rentDueDay", 1),
                assignment.get("notes", ""),
                assignment.get("createdAt"),
                assignment.get("updatedAt")
            ))
        
        db_manager.connection.commit()
        print(f"✅ {len(assignments)} assignations migrées avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration des assignations : {e}")
        db_manager.connection.rollback()
        return False
    finally:
        db_manager.disconnect()

def migrate_building_reports():
    """Migrer les rapports d'immeubles vers SQLite"""
    print("\n📊 Migration des rapports d'immeubles...")
    
    reports_data = load_json_data(BUILDING_REPORTS_DATA_FILE, {"reports": [], "next_id": 1})
    reports = reports_data.get("reports", [])
    
    if not reports:
        print("⚠️ Aucun rapport d'immeuble à migrer")
        return True
    
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        for report in reports:
            cursor.execute("""
                INSERT OR REPLACE INTO building_reports (
                    id, building_id, year, municipal_taxes, school_taxes,
                    insurance, snow_removal, lawn_care, management,
                    renovations, repairs, wifi, electricity, other,
                    notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.get("id"),
                report.get("buildingId"),
                report.get("year"),
                report.get("municipalTaxes", 0),
                report.get("schoolTaxes", 0),
                report.get("insurance", 0),
                report.get("snowRemoval", 0),
                report.get("lawnCare", 0),
                report.get("management", 0),
                report.get("renovations", 0),
                report.get("repairs", 0),
                report.get("wifi", 0),
                report.get("electricity", 0),
                report.get("other", 0),
                report.get("notes", ""),
                report.get("createdAt"),
                report.get("updatedAt")
            ))
        
        db_manager.connection.commit()
        print(f"✅ {len(reports)} rapports d'immeubles migrés avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration des rapports d'immeubles : {e}")
        db_manager.connection.rollback()
        return False
    finally:
        db_manager.disconnect()

def migrate_unit_reports():
    """Migrer les rapports d'unités vers SQLite"""
    print("\n🏠 Migration des rapports d'unités...")
    
    reports_data = load_json_data(UNIT_REPORTS_DATA_FILE, {"reports": [], "next_id": 1})
    reports = reports_data.get("reports", [])
    
    if not reports:
        print("⚠️ Aucun rapport d'unité à migrer")
        return True
    
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        for report in reports:
            cursor.execute("""
                INSERT OR REPLACE INTO unit_reports (
                    id, building_id, unit_id, year, rent_collected,
                    expenses, maintenance, utilities, other_income,
                    notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.get("id"),
                report.get("buildingId"),
                report.get("unitId"),
                report.get("year"),
                report.get("rentCollected", 0),
                report.get("expenses", 0),
                report.get("maintenance", 0),
                report.get("utilities", 0),
                report.get("otherIncome", 0),
                report.get("notes", ""),
                report.get("createdAt"),
                report.get("updatedAt")
            ))
        
        db_manager.connection.commit()
        print(f"✅ {len(reports)} rapports d'unités migrés avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration des rapports d'unités : {e}")
        db_manager.connection.rollback()
        return False
    finally:
        db_manager.disconnect()

def migrate_invoices():
    """Migrer les factures vers SQLite"""
    print("\n💰 Migration des factures...")
    
    invoices_data = load_json_data(INVOICES_DATA_FILE, {"invoices": [], "next_id": 1})
    invoices = invoices_data.get("invoices", [])
    
    if not invoices:
        print("⚠️ Aucune facture à migrer")
        return True
    
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        for invoice in invoices:
            cursor.execute("""
                INSERT OR REPLACE INTO invoices (
                    id, invoice_number, category, source, date, amount,
                    currency, payment_type, building_id, unit_id,
                    pdf_filename, pdf_path, notes, type, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice.get("id"),
                invoice.get("invoiceNumber"),
                invoice.get("category"),
                invoice.get("source"),
                invoice.get("date"),
                invoice.get("amount"),
                invoice.get("currency", "CAD"),
                invoice.get("paymentType"),
                invoice.get("buildingId"),
                invoice.get("unitId"),
                invoice.get("pdfFilename"),
                invoice.get("pdfPath"),
                invoice.get("notes", ""),
                invoice.get("type", "rental"),
                invoice.get("createdAt"),
                invoice.get("updatedAt")
            ))
        
        db_manager.connection.commit()
        print(f"✅ {len(invoices)} factures migrées avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration des factures : {e}")
        db_manager.connection.rollback()
        return False
    finally:
        db_manager.disconnect()

def verify_migration():
    """Vérifier que la migration s'est bien passée"""
    print("\n🔍 Vérification de la migration...")
    
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        # Compter les enregistrements dans chaque table
        tables = [
            ("buildings", "Immeubles"),
            ("tenants", "Locataires"),
            ("assignments", "Assignations"),
            ("building_reports", "Rapports d'immeubles"),
            ("unit_reports", "Rapports d'unités"),
            ("invoices", "Factures")
        ]
        
        for table_name, display_name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {display_name}: {count} enregistrements")
        
        db_manager.disconnect()
        print("✅ Vérification terminée")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")
        return False

def main():
    """Fonction principale de migration"""
    print("🚀 MIGRATION JSON → SQLite")
    print("=" * 50)
    
    # Créer une sauvegarde avant la migration
    print("💾 Création d'une sauvegarde...")
    backup_path = db_manager.backup_database()
    if not backup_path:
        print("❌ Impossible de créer une sauvegarde, migration annulée")
        return False
    
    # Initialiser la base de données
    print("\n🏗️ Initialisation de la base de données...")
    if not init_database():
        print("❌ Échec de l'initialisation de la base de données")
        return False
    
    # Migrer toutes les données
    migrations = [
        migrate_buildings,
        migrate_tenants,
        migrate_assignments,
        migrate_building_reports,
        migrate_unit_reports,
        migrate_invoices
    ]
    
    success = True
    for migration_func in migrations:
        if not migration_func():
            success = False
            break
    
    if success:
        # Vérifier la migration
        verify_migration()
        print("\n🎉 MIGRATION TERMINÉE AVEC SUCCÈS !")
        print(f"💾 Sauvegarde créée : {backup_path}")
        print("✅ Vos données JSON ont été migrées vers SQLite")
        print("🔒 Base de données maintenant protégée contre la corruption")
    else:
        print("\n❌ MIGRATION ÉCHOUÉE")
        print("🔄 Restaurez depuis la sauvegarde si nécessaire")
    
    return success

if __name__ == "__main__":
    main()
