#!/usr/bin/env python3
"""
Script pour ajouter la colonne taux_horaire à la table employes sur Render
"""

import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"

def add_taux_horaire_column():
    """Ajouter la colonne taux_horaire à la table employes"""
    print("🔧 Migration : Ajout de la colonne taux_horaire")
    print("=" * 50)
    
    try:
        # Créer un endpoint temporaire pour la migration
        migration_data = {
            "action": "add_column",
            "table": "employes",
            "column": "taux_horaire",
            "type": "FLOAT",
            "default_value": None
        }
        
        print(f"📡 Envoi de la requête de migration...")
        print(f"   Table: employes")
        print(f"   Colonne: taux_horaire")
        print(f"   Type: FLOAT")
        
        # Pour l'instant, on va créer un endpoint temporaire dans le backend
        # ou utiliser une approche alternative
        
        print("⚠️ Cette migration nécessite un endpoint spécial dans le backend")
        print("💡 Solution alternative :")
        print("   1. Créer un endpoint /api/construction/migrate/add-taux-horaire")
        print("   2. Ou redéployer le backend avec la nouvelle structure")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_employees_with_fallback():
    """Tester les employés avec une requête alternative"""
    print("\n🔄 Test alternatif des employés")
    print("=" * 50)
    
    try:
        # Essayer de récupérer les employés avec une requête SQL brute
        print("📡 Tentative de récupération directe...")
        
        # Créer un endpoint temporaire pour tester
        test_data = {
            "query": "SELECT * FROM employes LIMIT 10"
        }
        
        print("⚠️ Nécessite un endpoint de test SQL dans le backend")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def create_migration_endpoint():
    """Créer le code pour l'endpoint de migration"""
    print("\n📝 Code pour l'endpoint de migration")
    print("=" * 50)
    
    migration_code = '''
# Ajouter ceci dans backend/main.py dans la section CONSTRUCTION_ENABLED

@app.post("/api/construction/migrate/add-taux-horaire")
async def migrate_add_taux_horaire(db: Session = Depends(get_construction_db)):
    """Migration : Ajouter la colonne taux_horaire à la table employes"""
    try:
        # Vérifier si la colonne existe déjà
        cursor = db.execute("PRAGMA table_info(employes)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'taux_horaire' in columns:
            return {"success": True, "message": "Colonne taux_horaire existe déjà"}
        
        # Ajouter la colonne
        db.execute("ALTER TABLE employes ADD COLUMN taux_horaire FLOAT")
        db.commit()
        
        return {"success": True, "message": "Colonne taux_horaire ajoutée avec succès"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur migration: {e}")
'''
    
    print("📋 Code à ajouter dans main.py :")
    print(migration_code)

def suggest_solutions():
    """Suggérer des solutions"""
    print("\n💡 Solutions recommandées")
    print("=" * 50)
    
    print("🎯 Solution 1 - Migration via endpoint :")
    print("   1. Ajouter l'endpoint de migration dans main.py")
    print("   2. Déployer sur Render")
    print("   3. Appeler l'endpoint pour migrer")
    print("   4. Tester l'API des employés")
    print()
    
    print("🎯 Solution 2 - Redéploiement complet :")
    print("   1. S'assurer que models_construction.py a la colonne taux_horaire")
    print("   2. Redéployer le backend sur Render")
    print("   3. La migration se fera automatiquement")
    print("   4. Tester l'API des employés")
    print()
    
    print("🎯 Solution 3 - Reset de la base construction :")
    print("   1. Supprimer la base construction_projects.db sur Render")
    print("   2. Redéployer le backend")
    print("   3. Recréer les employés avec le nouveau formulaire")
    print("   4. Tester l'API des employés")

if __name__ == "__main__":
    print("🚀 Migration taux_horaire - Interface CAH")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    add_taux_horaire_column()
    test_employees_with_fallback()
    create_migration_endpoint()
    suggest_solutions()
    
    print("\n" + "=" * 50)
    print("🏁 Analyse terminée")
    print()
    print("🔍 Problème identifié :")
    print("   La colonne 'taux_horaire' n'existe pas dans la table employes sur Render")
    print("   Cela cause une erreur SQL lors de la récupération des employés")
    print()
    print("✅ Solution recommandée :")
    print("   Ajouter l'endpoint de migration et l'exécuter sur Render")
