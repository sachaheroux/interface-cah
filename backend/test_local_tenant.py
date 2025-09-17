#!/usr/bin/env python3
"""
Test local de création de locataire
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_service_francais import DatabaseServiceFrancais
from database import DatabaseManager

def test_local_tenant_creation():
    """Test local de création de locataire"""
    
    print("🧪 Test local de création de locataire")
    print("=" * 50)
    
    try:
        # Initialiser le service de base de données
        db_manager = DatabaseManager()
        db_service = DatabaseServiceFrancais()
        
        # Données de test
        tenant_data = {
            "id_unite": 2,
            "nom": "Test",
            "prenom": "User",
            "email": "test@email.com",
            "telephone": "514-999-9999",
            "statut": "actif",
            "notes": "Test local"
        }
        
        print(f"📤 Données de test:")
        print(f"   - Nom: {tenant_data['nom']}")
        print(f"   - Prénom: {tenant_data['prenom']}")
        print(f"   - Email: {tenant_data['email']}")
        print(f"   - Téléphone: {tenant_data['telephone']}")
        print(f"   - ID Unité: {tenant_data['id_unite']}")
        
        # Créer le locataire
        print(f"\n🔄 Création du locataire...")
        result = db_service.create_tenant(tenant_data)
        
        print(f"✅ Locataire créé avec succès!")
        print(f"   - Résultat: {result}")
        
        # Vérifier que le locataire a été créé
        print(f"\n🔍 Vérification...")
        tenants = db_service.get_tenants()
        print(f"   - Nombre total de locataires: {len(tenants)}")
        
        # Chercher le locataire créé
        created_tenant = None
        for tenant in tenants:
            if (tenant.get('nom') == 'Test' and 
                tenant.get('prenom') == 'User' and 
                tenant.get('email') == 'test@email.com'):
                created_tenant = tenant
                break
        
        if created_tenant:
            print(f"✅ Locataire trouvé dans la base de données:")
            print(f"   - ID: {created_tenant.get('id_locataire')}")
            print(f"   - Nom complet: {created_tenant.get('nom')} {created_tenant.get('prenom')}")
            print(f"   - Email: {created_tenant.get('email')}")
            print(f"   - Téléphone: {created_tenant.get('telephone')}")
            print(f"   - Statut: {created_tenant.get('statut')}")
            print(f"   - ID Unité: {created_tenant.get('id_unite')}")
        else:
            print(f"❌ Locataire non trouvé dans la base de données")
            
    except Exception as e:
        print(f"❌ Erreur lors du test local: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_local_tenant_creation()
