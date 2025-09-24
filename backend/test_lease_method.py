#!/usr/bin/env python3
"""
Test direct de la méthode get_leases_by_buildings_and_period
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire backend au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_service_francais import db_service_francais

def test_lease_method():
    """Tester directement la méthode get_leases_by_buildings_and_period"""
    
    print("🔍 TEST DIRECT DE LA MÉTHODE get_leases_by_buildings_and_period")
    print("=" * 60)
    
    try:
        # Paramètres de test
        building_ids = [1]
        start_date = datetime(2025, 7, 1)
        end_date = datetime(2026, 6, 1)
        
        print(f"Paramètres:")
        print(f"  - Immeubles: {building_ids}")
        print(f"  - Période: {start_date} à {end_date}")
        
        # Tester la méthode
        leases = db_service_francais.get_leases_by_buildings_and_period(building_ids, start_date, end_date)
        
        print(f"\nRésultat:")
        print(f"  - Nombre de baux trouvés: {len(leases)}")
        
        for i, lease in enumerate(leases):
            print(f"  - Bail {i+1}:")
            print(f"    ID: {lease.id_bail}")
            print(f"    Prix loyer: {lease.prix_loyer}")
            print(f"    Date début: {lease.date_debut}")
            print(f"    Date fin: {lease.date_fin}")
            if hasattr(lease, 'locataire') and lease.locataire:
                print(f"    Locataire: {lease.locataire.nom}")
                if hasattr(lease.locataire, 'unite') and lease.locataire.unite:
                    print(f"    Unité: {lease.locataire.unite.adresse_unite}")
                    if hasattr(lease.locataire.unite, 'id_immeuble'):
                        print(f"    Immeuble ID: {lease.locataire.unite.id_immeuble}")
        
        # Tester aussi la méthode get_leases() pour comparaison
        print(f"\nComparaison avec get_leases():")
        all_leases = db_service_francais.get_leases()
        print(f"  - Nombre total de baux: {len(all_leases)}")
        
        for i, lease in enumerate(all_leases):
            print(f"  - Bail {i+1}:")
            print(f"    ID: {lease.get('id_bail')}")
            print(f"    Prix loyer: {lease.get('prix_loyer')}")
            print(f"    Date début: {lease.get('date_debut')}")
            print(f"    Date fin: {lease.get('date_fin')}")
            if 'unite' in lease and lease['unite']:
                unite = lease['unite']
                if 'immeuble' in unite and unite['immeuble']:
                    immeuble = unite['immeuble']
                    print(f"    Immeuble ID: {immeuble.get('id_immeuble')}")
                    print(f"    Immeuble nom: {immeuble.get('nom_immeuble')}")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_lease_method()
