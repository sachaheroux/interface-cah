#!/usr/bin/env python3
"""
Script de nettoyage des données de test uniquement
Supprime seulement les données créées par les tests
"""

from database import db_manager

def clean_test_data():
    """Nettoyer seulement les données de test"""
    print("🧹 NETTOYAGE DES DONNÉES DE TEST")
    print("=" * 50)
    
    try:
        if not db_manager.connect():
            print("❌ Impossible de se connecter à la base de données")
            return False
        
        cursor = db_manager.connection.cursor()
        
        # 1. Supprimer les immeubles de test
        print("1️⃣ Suppression des immeubles de test...")
        cursor.execute("DELETE FROM buildings WHERE name LIKE '%Test%' OR name LIKE '%test%'")
        buildings_deleted = cursor.rowcount
        print(f"✅ {buildings_deleted} immeubles de test supprimés")
        
        # 2. Supprimer les locataires de test
        print("2️⃣ Suppression des locataires de test...")
        cursor.execute("DELETE FROM tenants WHERE name LIKE '%Test%' OR name LIKE '%test%' OR name LIKE '%Dupont%' OR name LIKE '%Martin%'")
        tenants_deleted = cursor.rowcount
        print(f"✅ {tenants_deleted} locataires de test supprimés")
        
        # 3. Supprimer les assignations de test
        print("3️⃣ Suppression des assignations de test...")
        cursor.execute("DELETE FROM assignments WHERE notes LIKE '%test%' OR notes LIKE '%Test%'")
        assignments_deleted = cursor.rowcount
        print(f"✅ {assignments_deleted} assignations de test supprimées")
        
        # 4. Supprimer les rapports de test
        print("4️⃣ Suppression des rapports de test...")
        cursor.execute("DELETE FROM building_reports WHERE notes LIKE '%test%' OR notes LIKE '%Test%'")
        building_reports_deleted = cursor.rowcount
        print(f"✅ {building_reports_deleted} rapports d'immeubles de test supprimés")
        
        cursor.execute("DELETE FROM unit_reports WHERE notes LIKE '%test%' OR notes LIKE '%Test%'")
        unit_reports_deleted = cursor.rowcount
        print(f"✅ {unit_reports_deleted} rapports d'unités de test supprimés")
        
        # 5. Supprimer les factures de test
        print("5️⃣ Suppression des factures de test...")
        cursor.execute("DELETE FROM invoices WHERE notes LIKE '%test%' OR notes LIKE '%Test%'")
        invoices_deleted = cursor.rowcount
        print(f"✅ {invoices_deleted} factures de test supprimées")
        
        # 6. Valider les changements
        db_manager.connection.commit()
        
        # 7. Vérifier le résultat
        print("\n6️⃣ Vérification du nettoyage...")
        tables = ["buildings", "tenants", "assignments", "building_reports", "unit_reports", "invoices"]
        total_records = 0
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"   📊 Table {table}: {count} enregistrements")
        
        db_manager.disconnect()
        
        print(f"\n🎉 NETTOYAGE TERMINÉ !")
        print(f"✅ {buildings_deleted} immeubles de test supprimés")
        print(f"✅ {tenants_deleted} locataires de test supprimés")
        print(f"✅ {assignments_deleted} assignations de test supprimées")
        print(f"✅ {building_reports_deleted} rapports d'immeubles de test supprimés")
        print(f"✅ {unit_reports_deleted} rapports d'unités de test supprimés")
        print(f"✅ {invoices_deleted} factures de test supprimées")
        print(f"📊 Total d'enregistrements restants: {total_records}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("⚠️  ATTENTION: Cette opération va supprimer les données de test !")
    print("   Les données de production ne seront pas touchées.")
    print()
    
    response = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ").lower().strip()
    
    if response in ['oui', 'o', 'yes', 'y']:
        success = clean_test_data()
        if success:
            print("\n✅ Nettoyage des données de test réussi !")
        else:
            print("\n❌ Erreur lors du nettoyage")
    else:
        print("\n❌ Opération annulée")

if __name__ == "__main__":
    main()
