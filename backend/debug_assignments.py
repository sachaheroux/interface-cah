#!/usr/bin/env python3
"""
Script de diagnostic pour les assignations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_service import DatabaseService
from models import Assignment, Tenant, Unit, Building
from database import db_manager

def debug_assignments():
    """Diagnostiquer les assignations"""
    print("🔍 DIAGNOSTIC DES ASSIGNATIONS")
    print("=" * 50)
    
    db_service = DatabaseService()
    
    # 1. Vérifier les assignations via le service
    print("\n1. Assignations via DatabaseService:")
    try:
        assignments = db_service.get_assignments()
        print(f"   Nombre d'assignations: {len(assignments)}")
        for i, assignment in enumerate(assignments):
            print(f"   Assignation {i+1}: {assignment}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 2. Vérifier directement en base
    print("\n2. Assignations directement en base:")
    session = db_manager.SessionLocal()
    try:
        assignments = session.query(Assignment).all()
        print(f"   Nombre d'assignations: {len(assignments)}")
        for assignment in assignments:
            print(f"   ID: {assignment.id}")
            print(f"   Tenant ID: {assignment.tenant_id}")
            print(f"   Unit ID: {assignment.unit_id}")
            print(f"   Building ID: {assignment.building_id}")
            print(f"   Move In: {assignment.move_in_date}")
            print(f"   Move Out: {assignment.move_out_date}")
            print(f"   Rent: {assignment.rent_amount}")
            print("   ---")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    finally:
        session.close()
    
    # 3. Vérifier les locataires
    print("\n3. Locataires:")
    try:
        tenants = db_service.get_tenants()
        print(f"   Nombre de locataires: {len(tenants)}")
        for tenant in tenants:
            print(f"   ID: {tenant.get('id')}, Nom: {tenant.get('name')}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 4. Vérifier les unités
    print("\n4. Unités:")
    try:
        units = db_service.get_units()
        print(f"   Nombre d'unités: {len(units)}")
        for unit in units:
            print(f"   ID: {unit.get('id')}, Adresse: {unit.get('unitAddress')}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

if __name__ == "__main__":
    debug_assignments()
