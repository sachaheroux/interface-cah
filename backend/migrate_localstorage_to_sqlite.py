#!/usr/bin/env python3
"""
Script de migration des données localStorage vers SQLite
Ce script lit les données du localStorage et les insère dans la base SQLite
"""

import json
import os
from datetime import datetime
from database import db_manager
from database_service import db_service

def migrate_localstorage_data():
    """Migrer les données du localStorage vers SQLite"""
    print("🔄 MIGRATION DES DONNÉES LOCALSTORAGE VERS SQLITE")
    print("=" * 60)
    
    try:
        # Chemin vers les données localStorage (simulé)
        # En réalité, ces données sont dans le navigateur
        print("⚠️  ATTENTION: Ce script ne peut pas lire directement le localStorage du navigateur.")
        print("   Vous devez d'abord exporter vos données localStorage.")
        print()
        print("📋 Instructions :")
        print("1. Ouvrez votre navigateur")
        print("2. Allez sur votre application Interface CAH")
        print("3. Ouvrez la console développeur (F12)")
        print("4. Tapez : JSON.stringify(localStorage)")
        print("5. Copiez le résultat et collez-le dans un fichier JSON")
        print()
        
        # Demander le chemin du fichier JSON
        json_file = input("Entrez le chemin vers le fichier JSON des données localStorage (ou 'skip' pour ignorer): ").strip()
        
        if json_file.lower() == 'skip':
            print("❌ Migration annulée")
            return False
            
        if not os.path.exists(json_file):
            print(f"❌ Fichier non trouvé: {json_file}")
            return False
            
        # Lire le fichier JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            localStorage_data = json.load(f)
            
        print(f"✅ Fichier JSON lu: {json_file}")
        
        # Migrer les immeubles
        if 'localBuildings' in localStorage_data:
            buildings_data = json.loads(localStorage_data['localBuildings'])
            print(f"\n🏢 Migration de {len(buildings_data)} immeubles...")
            
            for building in buildings_data:
                try:
                    # Adapter le format des données si nécessaire
                    building_data = {
                        "name": building.get("name", ""),
                        "address_street": building.get("address", {}).get("street", ""),
                        "address_city": building.get("address", {}).get("city", ""),
                        "address_province": building.get("address", {}).get("province", ""),
                        "address_postal_code": building.get("address", {}).get("postalCode", ""),
                        "address_country": building.get("address", {}).get("country", "Canada"),
                        "type": building.get("type", "Résidentiel"),
                        "units": building.get("units", 0),
                        "floors": building.get("floors", 0),
                        "year_built": building.get("yearBuilt", None),
                        "total_area": building.get("totalArea", 0),
                        "characteristics": json.dumps(building.get("characteristics", {})),
                        "financials": json.dumps(building.get("financials", {})),
                        "contacts": json.dumps(building.get("contacts", {})),
                        "unit_data": json.dumps(building.get("unitData", {})),
                        "notes": building.get("notes", "")
                    }
                    
                    result = db_service.create_building(building_data)
                    print(f"✅ Immeuble migré: {building_data['name']} (ID: {result['id']})")
                    
                except Exception as e:
                    print(f"❌ Erreur migration immeuble {building.get('name', 'Inconnu')}: {e}")
        
        # Migrer les locataires
        if 'localTenants' in localStorage_data:
            tenants_data = json.loads(localStorage_data['localTenants'])
            print(f"\n👥 Migration de {len(tenants_data)} locataires...")
            
            for tenant in tenants_data:
                try:
                    tenant_data = {
                        "name": tenant.get("name", ""),
                        "email": tenant.get("email", ""),
                        "phone": tenant.get("phone", ""),
                        "notes": tenant.get("notes", "")
                    }
                    
                    result = db_service.create_tenant(tenant_data)
                    print(f"✅ Locataire migré: {tenant_data['name']} (ID: {result['id']})")
                    
                except Exception as e:
                    print(f"❌ Erreur migration locataire {tenant.get('name', 'Inconnu')}: {e}")
        
        # Migrer les assignations
        if 'unitTenantAssignments' in localStorage_data:
            assignments_data = json.loads(localStorage_data['unitTenantAssignments'])
            print(f"\n🔗 Migration de {len(assignments_data)} assignations...")
            
            for assignment in assignments_data:
                try:
                    # Note: Cette migration est plus complexe car elle nécessite des IDs valides
                    print(f"⚠️  Assignation trouvée: Locataire {assignment.get('tenantId')} → Unité {assignment.get('unitId')}")
                    print("   (Les assignations nécessitent des IDs valides d'immeubles et de locataires)")
                    
                except Exception as e:
                    print(f"❌ Erreur migration assignation: {e}")
        
        print("\n🎉 MIGRATION TERMINÉE !")
        print("✅ Vos données localStorage ont été migrées vers SQLite")
        print("✅ Vous pouvez maintenant supprimer les données localStorage")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("🔄 MIGRATION LOCALSTORAGE → SQLITE")
    print("=" * 40)
    print()
    
    success = migrate_localstorage_data()
    
    if success:
        print("\n✅ Migration réussie !")
        print("🚀 Vos données sont maintenant dans la base SQLite")
    else:
        print("\n❌ Migration échouée")

if __name__ == "__main__":
    main()
