"""
Script de diagnostic pour l'analyse de rentabilité
"""
import sys
import traceback
from datetime import datetime
from database import SessionLocal
from models import Immeuble, Unite, Locataire, Bail, Transaction

def diagnose_profitability():
    """Diagnostiquer les problèmes potentiels de l'analyse de rentabilité"""
    print("=" * 80)
    print("🔍 DIAGNOSTIC DE L'ANALYSE DE RENTABILITÉ")
    print("=" * 80)
    
    session = SessionLocal()
    
    try:
        # 1. Vérifier les immeubles
        print("\n1️⃣ VÉRIFICATION DES IMMEUBLES")
        print("-" * 80)
        immeubles = session.query(Immeuble).all()
        print(f"✅ Nombre d'immeubles: {len(immeubles)}")
        
        for immeuble in immeubles:
            print(f"\n  📍 Immeuble #{immeuble.id_immeuble}")
            print(f"     Adresse: {immeuble.adresse}")
            print(f"     Unités: {immeuble.nbr_unite}")
            print(f"     Latitude: {immeuble.latitude}")
            print(f"     Longitude: {immeuble.longitude}")
        
        # 2. Vérifier les baux et leurs relations
        print("\n\n2️⃣ VÉRIFICATION DES BAUX")
        print("-" * 80)
        baux = session.query(Bail).all()
        print(f"✅ Nombre de baux: {len(baux)}")
        
        for bail in baux:
            print(f"\n  📄 Bail #{bail.id_bail}")
            print(f"     Prix loyer: {bail.prix_loyer}$")
            print(f"     Date début: {bail.date_debut}")
            print(f"     Date fin: {bail.date_fin}")
            print(f"     ID locataire: {bail.id_locataire}")
            
            # Vérifier la relation locataire
            if bail.locataire:
                print(f"     ✅ Locataire trouvé: {bail.locataire.nom} {bail.locataire.prenom}")
                print(f"     ID unité: {bail.locataire.id_unite}")
                
                # Vérifier la relation unité
                if bail.locataire.unite:
                    print(f"     ✅ Unité trouvée: {bail.locataire.unite.numero_unite}")
                    print(f"     ID immeuble: {bail.locataire.unite.id_immeuble}")
                    
                    # Vérifier la relation immeuble
                    if bail.locataire.unite.immeuble:
                        print(f"     ✅ Immeuble trouvé: {bail.locataire.unite.immeuble.adresse}")
                    else:
                        print(f"     ❌ ERREUR: Immeuble introuvable pour l'unité #{bail.locataire.unite.id_unite}")
                else:
                    print(f"     ❌ ERREUR: Unité introuvable pour le locataire #{bail.locataire.id_locataire}")
            else:
                print(f"     ❌ ERREUR: Locataire introuvable pour le bail #{bail.id_bail}")
        
        # 3. Vérifier les transactions
        print("\n\n3️⃣ VÉRIFICATION DES TRANSACTIONS")
        print("-" * 80)
        transactions = session.query(Transaction).all()
        print(f"✅ Nombre de transactions: {len(transactions)}")
        
        for transaction in transactions:
            print(f"\n  💰 Transaction #{transaction.id_transaction}")
            print(f"     Type: {transaction.type}")
            print(f"     Catégorie: {transaction.categorie}")
            print(f"     Montant: {transaction.montant}$")
            print(f"     Date: {transaction.date_de_transaction}")
            print(f"     ID immeuble: {transaction.id_immeuble}")
            
            if transaction.immeuble:
                print(f"     ✅ Immeuble trouvé: {transaction.immeuble.adresse}")
            else:
                print(f"     ❌ ERREUR: Immeuble introuvable pour la transaction #{transaction.id_transaction}")
        
        # 4. Tester la logique de l'analyse
        print("\n\n4️⃣ TEST DE LA LOGIQUE D'ANALYSE")
        print("-" * 80)
        
        # Simuler les paramètres d'une requête
        test_building_ids = [immeuble.id_immeuble for immeuble in immeubles[:2]]  # Prendre 2 premiers immeubles
        test_start_date = datetime(2024, 1, 1)
        test_end_date = datetime(2024, 12, 31)
        
        print(f"\nTest avec:")
        print(f"  - Immeubles: {test_building_ids}")
        print(f"  - Période: {test_start_date.strftime('%Y-%m-%d')} à {test_end_date.strftime('%Y-%m-%d')}")
        
        # Filtrer les baux
        from sqlalchemy.orm import joinedload
        baux_filtered = session.query(Bail).options(
            joinedload(Bail.locataire).joinedload(Locataire.unite).joinedload(Unite.immeuble)
        ).join(Locataire).join(Unite).filter(
            Unite.id_immeuble.in_(test_building_ids)
        ).all()
        
        print(f"\n  ✅ Baux trouvés: {len(baux_filtered)}")
        for bail in baux_filtered:
            if bail.locataire and bail.locataire.unite:
                print(f"     - Bail #{bail.id_bail}: {bail.prix_loyer}$ (Immeuble #{bail.locataire.unite.id_immeuble})")
        
        # Filtrer les transactions
        transactions_filtered = session.query(Transaction).filter(
            Transaction.id_immeuble.in_(test_building_ids)
        ).all()
        
        print(f"\n  ✅ Transactions trouvées: {len(transactions_filtered)}")
        for transaction in transactions_filtered:
            print(f"     - Transaction #{transaction.id_transaction}: {transaction.montant}$ ({transaction.type})")
        
        print("\n\n" + "=" * 80)
        print("✅ DIAGNOSTIC TERMINÉ")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n\n❌ ERREUR DURANT LE DIAGNOSTIC:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print(f"\nTraceback complet:")
        traceback.print_exc()
        
    finally:
        session.close()

if __name__ == "__main__":
    diagnose_profitability()

