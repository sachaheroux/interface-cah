#!/usr/bin/env python3
"""
Télécharger les données du cloud vers un fichier local pour DB Browser
"""

import requests
import sqlite3
import json
from datetime import datetime

def download_cloud_to_local():
    """Télécharger toutes les données du cloud et les sauvegarder localement"""
    
    print("🌐 TÉLÉCHARGEMENT CLOUD → LOCAL")
    print("=" * 50)
    
    # Créer un nom de fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_db_path = f"cah_database_cloud_{timestamp}.db"
    
    print(f"📁 Fichier local: {local_db_path}")
    
    # Créer la base de données locale
    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    
    try:
        # Créer les tables
        print("🏗️ Création des tables...")
        
        # Table buildings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address_street TEXT,
                address_city TEXT,
                address_province TEXT,
                address_postal_code TEXT,
                address_country TEXT DEFAULT 'Canada',
                type TEXT NOT NULL DEFAULT 'residential',
                units INTEGER NOT NULL DEFAULT 0,
                floors INTEGER NOT NULL DEFAULT 1,
                year_built INTEGER,
                total_area INTEGER,
                characteristics TEXT,
                -- Colonnes financières séparées
                purchase_price REAL DEFAULT 0.0,
                down_payment REAL DEFAULT 0.0,
                interest_rate REAL DEFAULT 0.0,
                current_value REAL DEFAULT 0.0,
                -- Colonnes de contacts séparées
                owner_name TEXT,
                bank_name TEXT,
                contractor_name TEXT,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_default BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Table units
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_id INTEGER NOT NULL,
                unit_number TEXT NOT NULL,
                unit_address TEXT,
                type TEXT,
                area REAL DEFAULT 0.0,
                bedrooms INTEGER DEFAULT 0,
                bathrooms INTEGER DEFAULT 0,
                amenities TEXT,
                rental_info TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE CASCADE,
                UNIQUE(building_id, unit_number)
            )
        """)
        
        # Table tenants
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address_street TEXT,
                address_city TEXT,
                address_province TEXT,
                address_postal_code TEXT,
                address_country TEXT,
                personal_info TEXT,
                emergency_contact TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table assignments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_id INTEGER NOT NULL,
                tenant_id INTEGER NOT NULL,
                start_date TEXT,
                end_date TEXT,
                rent_amount REAL DEFAULT 0.0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (unit_id) REFERENCES units (id) ON DELETE CASCADE,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
            )
        """)
        
        # Table unit_reports
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unit_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER,
                tenant_name TEXT,
                payment_method TEXT,
                is_heated_lit BOOLEAN DEFAULT 0,
                is_furnished BOOLEAN DEFAULT 0,
                wifi_included BOOLEAN DEFAULT 0,
                rent_amount REAL DEFAULT 0.0,
                start_date TEXT,
                end_date TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (unit_id) REFERENCES units (id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        print("✅ Tables créées")
        
        # Télécharger les données
        print("\n📥 Téléchargement des données...")
        
        # Buildings
        print("🏢 Téléchargement des immeubles...")
        response = requests.get('https://interface-cah-backend.onrender.com/api/buildings')
        print(f"   📊 Status: {response.status_code}")
        print(f"   📊 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            buildings = response.json()
            print(f"   📊 {len(buildings)} immeubles trouvés")
            print(f"   📊 Type: {type(buildings)}")
            print(f"   📊 Premier immeuble: {buildings[0] if buildings else 'Aucun'}")
            
            for building in buildings:
                print(f"   🏢 Insertion: {building['name']} (ID: {building['id']})")
                
                # Extraire les données d'adresse
                address = building.get('address', {})
                if isinstance(address, str):
                    address = json.loads(address) if address else {}
                
                # Extraire les données financières et de contacts
                financials = building.get('financials', {})
                contacts = building.get('contacts', {})
                
                cursor.execute("""
                    INSERT OR REPLACE INTO buildings (
                        id, name, address_street, address_city, address_province, 
                        address_postal_code, address_country, type, units, floors, 
                        year_built, total_area, characteristics,
                        purchase_price, down_payment, interest_rate, current_value,
                        owner_name, bank_name, contractor_name,
                        notes, created_at, updated_at, is_default
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    building['id'],
                    building['name'],
                    address.get('street', ''),
                    address.get('city', ''),
                    address.get('province', ''),
                    address.get('postalCode', ''),
                    address.get('country', 'Canada'),
                    building.get('type', 'residential'),
                    building.get('units', 0),
                    building.get('floors', 1),
                    building.get('yearBuilt'),
                    building.get('totalArea'),
                    json.dumps(building.get('characteristics', {})),
                    # Colonnes financières séparées
                    financials.get('purchasePrice', 0.0),
                    financials.get('downPayment', 0.0),
                    financials.get('interestRate', 0.0),
                    financials.get('currentValue', 0.0),
                    # Colonnes de contacts séparées
                    contacts.get('owner', ''),
                    contacts.get('bank', ''),
                    contacts.get('contractor', ''),
                    building.get('notes', ''),
                    building.get('createdAt', ''),
                    building.get('updatedAt', ''),
                    False  # is_default
                ))
        else:
            print(f"   ❌ Erreur immeubles: {response.status_code}")
        
        # Units
        print("🏠 Téléchargement des unités...")
        response = requests.get('https://interface-cah-backend.onrender.com/api/units')
        if response.status_code == 200:
            units_data = response.json()
            if isinstance(units_data, dict) and 'data' in units_data:
                units = units_data['data']
            else:
                units = units_data
                
            print(f"   📊 {len(units)} unités trouvées")
            
            for unit in units:
                cursor.execute("""
                    INSERT OR REPLACE INTO units (
                        id, building_id, unit_number, unit_address, type, area, 
                        bedrooms, bathrooms, amenities, rental_info, notes, 
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    unit['id'],
                    unit['buildingId'],
                    unit['unitNumber'],
                    unit['unitAddress'],
                    unit['type'],
                    float(unit.get('area', 0)),
                    int(unit.get('bedrooms', 0)),
                    int(unit.get('bathrooms', 0)),
                    unit.get('amenities', '{}'),
                    unit.get('rentalInfo', '{}'),
                    unit.get('notes', ''),
                    unit.get('createdAt', ''),
                    unit.get('updatedAt', '')
                ))
        else:
            print(f"   ❌ Erreur unités: {response.status_code}")
        
        # Tenants
        print("👥 Téléchargement des locataires...")
        response = requests.get('https://interface-cah-backend.onrender.com/api/tenants')
        print(f"   📊 Status: {response.status_code}")
        print(f"   📊 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            tenants_data = response.json()
            print(f"   📊 Type des données: {type(tenants_data)}")
            
            # Vérifier si c'est un dict avec une clé 'data'
            if isinstance(tenants_data, dict) and 'data' in tenants_data:
                tenants = tenants_data['data']
            else:
                tenants = tenants_data
                
            print(f"   📊 {len(tenants)} locataires trouvés")
            print(f"   📊 Type: {type(tenants)}")
            
            for tenant in tenants:
                # Diviser le nom en prénom et nom de famille
                full_name = tenant.get('name', '')
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0] if len(name_parts) > 0 else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                print(f"   👥 Insertion: {first_name} {last_name}")
                cursor.execute("""
                    INSERT OR REPLACE INTO tenants (
                        id, first_name, last_name, email, phone,
                        address_street, address_city, address_province, 
                        address_postal_code, address_country, personal_info,
                        emergency_contact, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tenant['id'],
                    first_name,
                    last_name,
                    tenant.get('email', ''),
                    tenant.get('phone', ''),
                    tenant.get('address', {}).get('street', ''),
                    tenant.get('address', {}).get('city', ''),
                    tenant.get('address', {}).get('province', ''),
                    tenant.get('address', {}).get('postalCode', ''),
                    tenant.get('address', {}).get('country', ''),
                    json.dumps(tenant.get('personalInfo', {})),
                    json.dumps(tenant.get('emergencyContact', {})),
                    tenant.get('createdAt', ''),
                    tenant.get('updatedAt', '')
                ))
        else:
            print(f"   ❌ Erreur locataires: {response.status_code}")
        
        conn.commit()
        print("\n✅ Téléchargement terminé !")
        print(f"📁 Fichier créé: {local_db_path}")
        print("\n🔍 Pour ouvrir dans DB Browser:")
        print(f"   1. Ouvrir DB Browser for SQLite")
        print(f"   2. Cliquer 'Open Database'")
        print(f"   3. Naviguer vers: {local_db_path}")
        print(f"   4. Explorer la table 'units'")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    download_cloud_to_local()
