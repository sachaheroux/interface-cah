#!/usr/bin/env python3
"""
Script pour diagnostiquer et corriger le problème de suppression des baux
"""

import sqlite3
from database_service_francais import DatabaseServiceFrancais
from database import engine
from sqlalchemy import text

def check_lease_deletion_issues():
    """Diagnostiquer les problèmes de suppression des baux"""
    print("🔍 DIAGNOSTIC DES PROBLÈMES DE SUPPRESSION DES BAILS")
    print("=" * 60)
    
    db_service = DatabaseServiceFrancais()
    
    # 1. Lister tous les baux
    print("\n📋 1. BAUX EXISTANTS:")
    baux = db_service.get_leases()
    if not baux:
        print("   ❌ Aucun bail trouvé")
        return
    
    for bail in baux:
        print(f"   - ID: {bail['id_bail']}, Locataire: {bail.get('id_locataire', 'N/A')}, Prix: {bail.get('prix_loyer', 0)}$")
    
    # 2. Vérifier les paiements associés
    print("\n💰 2. PAIEMENTS ASSOCIÉS:")
    with engine.connect() as conn:
        # Compter tous les paiements
        result = conn.execute(text('SELECT COUNT(*) FROM paiements_loyers'))
        total_payments = result.scalar()
        print(f"   Total paiements: {total_payments}")
        
        if total_payments > 0:
            # Grouper par bail
            result = conn.execute(text('SELECT id_bail, COUNT(*) FROM paiements_loyers GROUP BY id_bail'))
            for row in result:
                bail_id, count = row
                print(f"   - Bail ID {bail_id}: {count} paiements")
    
    # 3. Vérifier les contraintes de clés étrangères
    print("\n🔗 3. CONTRAINTES DE CLÉS ÉTRANGÈRES:")
    with engine.connect() as conn:
        # Vérifier les contraintes sur paiements_loyers
        result = conn.execute(text("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='paiements_loyers'
        """))
        table_sql = result.scalar()
        if table_sql:
            print("   Structure de paiements_loyers:")
            print(f"   {table_sql}")
        
        # Vérifier les contraintes sur baux
        result = conn.execute(text("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='baux'
        """))
        table_sql = result.scalar()
        if table_sql:
            print("\n   Structure de baux:")
            print(f"   {table_sql}")

def fix_foreign_key_constraints():
    """Corriger les contraintes de clés étrangères pour permettre la suppression en cascade"""
    print("\n🔧 CORRECTION DES CONTRAINTES DE CLÉS ÉTRANGÈRES")
    print("=" * 60)
    
    try:
        with engine.connect() as conn:
            # 1. Vérifier si la contrainte CASCADE existe déjà
            result = conn.execute(text("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='paiements_loyers'
            """))
            table_sql = result.scalar()
            
            if table_sql and 'ON DELETE CASCADE' in table_sql:
                print("✅ La contrainte CASCADE existe déjà")
                return True
            
            print("⚠️ La contrainte CASCADE n'existe pas, correction nécessaire...")
            
            # 2. Créer une nouvelle table avec CASCADE
            print("📝 Création d'une nouvelle table avec CASCADE...")
            
            # Sauvegarder les données existantes
            result = conn.execute(text('SELECT * FROM paiements_loyers'))
            existing_data = result.fetchall()
            print(f"   Sauvegarde de {len(existing_data)} paiements existants")
            
            # Supprimer l'ancienne table
            conn.execute(text('DROP TABLE IF EXISTS paiements_loyers'))
            
            # Créer la nouvelle table avec CASCADE
            conn.execute(text("""
                CREATE TABLE paiements_loyers (
                    id_paiement INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_bail INTEGER NOT NULL,
                    mois INTEGER NOT NULL,
                    annee INTEGER NOT NULL,
                    date_paiement_reelle DATE NOT NULL,
                    montant_paye DECIMAL(10, 2) NOT NULL,
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_bail) REFERENCES baux(id_bail) ON DELETE CASCADE,
                    UNIQUE (id_bail, mois, annee)
                )
            """))
            
            # Restaurer les données
            if existing_data:
                for row in existing_data:
                    conn.execute(text("""
                        INSERT INTO paiements_loyers 
                        (id_paiement, id_bail, mois, annee, date_paiement_reelle, montant_paye, notes, date_creation, date_modification)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """), row)
            
            conn.commit()
            print("✅ Table paiements_loyers recréée avec CASCADE")
            print(f"✅ {len(existing_data)} paiements restaurés")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

def test_lease_deletion():
    """Tester la suppression d'un bail"""
    print("\n🧪 TEST DE SUPPRESSION D'UN BAIL")
    print("=" * 60)
    
    db_service = DatabaseServiceFrancais()
    
    # Récupérer le premier bail pour le test
    baux = db_service.get_leases()
    if not baux:
        print("❌ Aucun bail disponible pour le test")
        return
    
    test_bail = baux[0]
    bail_id = test_bail['id_bail']
    
    print(f"🎯 Test avec le bail ID: {bail_id}")
    
    # Vérifier les paiements avant suppression
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM paiements_loyers WHERE id_bail = ?'), (bail_id,))
        payment_count = result.scalar()
        print(f"💰 Paiements associés: {payment_count}")
    
    # Demander confirmation
    response = input(f"\n❓ Voulez-vous vraiment supprimer le bail ID {bail_id} ? (oui/non): ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Test annulé")
        return
    
    try:
        # Tenter la suppression
        success = db_service.delete_lease(bail_id)
        if success:
            print("✅ Suppression réussie !")
            
            # Vérifier que les paiements ont été supprimés aussi
            with engine.connect() as conn:
                result = conn.execute(text('SELECT COUNT(*) FROM paiements_loyers WHERE id_bail = ?'), (bail_id,))
                remaining_payments = result.scalar()
                print(f"💰 Paiements restants pour ce bail: {remaining_payments}")
                
                if remaining_payments == 0:
                    print("✅ Les paiements ont été supprimés automatiquement (CASCADE)")
                else:
                    print("⚠️ Des paiements restent encore (problème CASCADE)")
        else:
            print("❌ Échec de la suppression")
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")

def main():
    """Fonction principale"""
    print("🚀 SCRIPT DE DIAGNOSTIC ET CORRECTION DES BAILS")
    print("=" * 60)
    
    # 1. Diagnostic
    check_lease_deletion_issues()
    
    # 2. Correction des contraintes
    fix_success = fix_foreign_key_constraints()
    
    if fix_success:
        print("\n✅ CORRECTION TERMINÉE")
        print("Les baux peuvent maintenant être supprimés avec suppression automatique des paiements associés")
        
        # 3. Test optionnel
        test_response = input("\n❓ Voulez-vous tester la suppression d'un bail ? (oui/non): ")
        if test_response.lower() in ['oui', 'o', 'yes', 'y']:
            test_lease_deletion()
    else:
        print("\n❌ ÉCHEC DE LA CORRECTION")
        print("Vérifiez les logs pour plus de détails")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Script interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

