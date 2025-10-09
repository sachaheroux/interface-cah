"""
Script pour vider complètement la table paiements_loyers
ATTENTION : Ce script supprime TOUTES les données de paiements_loyers
"""
from database import SessionLocal
from sqlalchemy import text

def clear_paiements_loyers():
    """Vider la table paiements_loyers"""
    print("=" * 80)
    print("⚠️  SUPPRESSION DE TOUTES LES DONNÉES DE paiements_loyers")
    print("=" * 80)
    
    session = SessionLocal()
    
    try:
        # Compter les enregistrements avant suppression
        print("\n1️⃣ Comptage des enregistrements...")
        result = session.execute(text("SELECT COUNT(*) FROM paiements_loyers"))
        count_before = result.scalar()
        print(f"📊 Nombre de paiements actuels: {count_before}")
        
        if count_before == 0:
            print("✅ La table est déjà vide!")
            return
        
        # Demander confirmation
        print(f"\n⚠️  ATTENTION: Vous allez supprimer {count_before} enregistrements!")
        confirmation = input("Tapez 'OUI' pour confirmer la suppression: ")
        
        if confirmation != "OUI":
            print("❌ Suppression annulée")
            return
        
        # Supprimer toutes les données
        print("\n2️⃣ Suppression en cours...")
        session.execute(text("DELETE FROM paiements_loyers"))
        session.commit()
        print("✅ Toutes les données ont été supprimées!")
        
        # Vérifier que la table est vide
        print("\n3️⃣ Vérification...")
        result = session.execute(text("SELECT COUNT(*) FROM paiements_loyers"))
        count_after = result.scalar()
        print(f"📊 Nombre de paiements après suppression: {count_after}")
        
        if count_after == 0:
            print("✅ La table paiements_loyers est maintenant vide!")
        else:
            print(f"⚠️  Il reste encore {count_after} enregistrements")
        
        print("\n" + "=" * 80)
        print("✅ OPÉRATION TERMINÉE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {type(e).__name__}: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
        
    finally:
        session.close()

if __name__ == "__main__":
    clear_paiements_loyers()

