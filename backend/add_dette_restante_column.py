"""
Script pour ajouter la colonne dette_restante à la table immeubles
"""
from database import SessionLocal
from sqlalchemy import text

def add_dette_restante_column():
    """Ajouter la colonne dette_restante si elle n'existe pas"""
    print("=" * 80)
    print("🔧 AJOUT DE LA COLONNE dette_restante")
    print("=" * 80)
    
    session = SessionLocal()
    
    try:
        # Vérifier si la colonne existe déjà
        print("\n1️⃣ Vérification de l'existence de la colonne...")
        result = session.execute(text("PRAGMA table_info(immeubles)"))
        columns = [row[1] for row in result]
        
        print(f"✅ Colonnes actuelles: {', '.join(columns)}")
        
        if 'dette_restante' in columns:
            print("✅ La colonne dette_restante existe déjà!")
        else:
            print("\n2️⃣ Ajout de la colonne dette_restante...")
            session.execute(text("""
                ALTER TABLE immeubles 
                ADD COLUMN dette_restante DECIMAL(12, 2) DEFAULT 0
            """))
            session.commit()
            print("✅ Colonne dette_restante ajoutée avec succès!")
        
        # Vérifier à nouveau
        print("\n3️⃣ Vérification finale...")
        result = session.execute(text("PRAGMA table_info(immeubles)"))
        columns = [row[1] for row in result]
        
        if 'dette_restante' in columns:
            print("✅ La colonne dette_restante est maintenant présente!")
        else:
            print("❌ ERREUR: La colonne n'a pas été ajoutée correctement")
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION TERMINÉE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {type(e).__name__}: {e}")
        session.rollback()
        
    finally:
        session.close()

if __name__ == "__main__":
    add_dette_restante_column()

