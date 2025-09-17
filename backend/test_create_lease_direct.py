#!/usr/bin/env python3
"""
Test direct de la création de bail
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_service_francais import DatabaseServiceFrancais

def test_create_lease_direct():
    """Tester directement la création de bail"""
    
    print("🧪 Test direct de création de bail")
    print("=" * 50)
    
    try:
        # Initialiser le service
        db_service = DatabaseServiceFrancais()
        
        # Données de test
        lease_data = {
            "id_locataire": 1,  # ID d'un locataire existant
            "date_debut": "2024-01-01",
            "date_fin": "2024-12-31",
            "prix_loyer": 1500.0,
            "methode_paiement": "Virement bancaire",
            "pdf_bail": ""
        }
        
        print(f"📤 Données de test: {lease_data}")
        
        # Tester la création
        result = db_service.create_lease(lease_data)
        
        print(f"✅ Résultat: {result}")
        print(f"✅ Type: {type(result)}")
        print(f"✅ Clés: {result.keys() if isinstance(result, dict) else 'N/A'}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_lease_direct()
