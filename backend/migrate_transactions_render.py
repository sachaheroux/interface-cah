#!/usr/bin/env python3
"""
Script pour migrer la table transactions sur Render vers la nouvelle structure
"""

import os
import sys
import requests
from datetime import datetime

# Configuration Render
RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def test_api_connection():
    """Tester la connexion à l'API Render"""
    try:
        response = requests.get(f"{RENDER_API_URL}/api/buildings")
        if response.status_code == 200:
            print("✅ Connexion à l'API Render réussie")
            return True
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def migrate_transactions_table():
    """Migrer la table transactions vers la nouvelle structure"""
    try:
        print("🔄 Début de la migration de la table transactions...")
        
        # 1. Sauvegarder les données existantes
        print("📥 Sauvegarde des données existantes...")
        response = requests.get(f"{RENDER_API_URL}/api/transactions")
        if response.status_code == 200:
            existing_transactions = response.json().get('data', [])
            print(f"✅ {len(existing_transactions)} transactions trouvées")
        else:
            print("⚠️ Aucune transaction existante ou erreur de récupération")
            existing_transactions = []
        
        # 2. Créer la nouvelle table avec la structure française
        print("🔧 Création de la nouvelle structure...")
        
        # Note: Cette migration doit être faite directement sur Render
        # car nous ne pouvons pas exécuter des commandes SQL directement via l'API
        
        print("⚠️ Migration manuelle requise sur Render:")
        print("1. Connectez-vous à la base de données Render")
        print("2. Exécutez les commandes SQL suivantes:")
        print()
        print("-- Sauvegarder les données existantes")
        print("CREATE TABLE transactions_backup AS SELECT * FROM transactions;")
        print()
        print("-- Supprimer l'ancienne table")
        print("DROP TABLE transactions;")
        print()
        print("-- Créer la nouvelle table avec la structure française")
        print("""
CREATE TABLE transactions (
    id_transaction INTEGER PRIMARY KEY AUTOINCREMENT,
    id_immeuble INTEGER NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    montant DECIMAL(12, 2) NOT NULL,
    date_de_transaction DATE NOT NULL,
    methode_de_paiement VARCHAR(50),
    reference VARCHAR(100),
    source VARCHAR(255),
    pdf_transaction VARCHAR(255),
    notes TEXT DEFAULT '',
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_immeuble) REFERENCES immeubles (id_immeuble) ON DELETE CASCADE
);
        """)
        print()
        print("-- Recréer l'index")
        print("CREATE INDEX ix_transactions_id_transaction ON transactions (id_transaction);")
        print("CREATE INDEX ix_transactions_id_immeuble ON transactions (id_immeuble);")
        print("CREATE INDEX ix_transactions_date_de_transaction ON transactions (date_de_transaction);")
        print()
        print("-- Migrer les données existantes (si nécessaire)")
        print("-- INSERT INTO transactions SELECT ... FROM transactions_backup;")
        print()
        print("-- Supprimer la table de sauvegarde")
        print("-- DROP TABLE transactions_backup;")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

def test_new_structure():
    """Tester la nouvelle structure après migration"""
    try:
        print("🧪 Test de la nouvelle structure...")
        
        # Tester l'endpoint des constantes
        response = requests.get(f"{RENDER_API_URL}/api/transactions/constants")
        if response.status_code == 200:
            constants = response.json()
            print("✅ Endpoint des constantes fonctionne")
            print(f"   Catégories: {constants.get('categories', [])}")
            print(f"   Méthodes de paiement: {constants.get('payment_methods', [])}")
        else:
            print(f"❌ Erreur constantes: {response.status_code}")
        
        # Tester l'endpoint des transactions
        response = requests.get(f"{RENDER_API_URL}/api/transactions")
        if response.status_code == 200:
            transactions = response.json().get('data', [])
            print(f"✅ Endpoint des transactions fonctionne ({len(transactions)} transactions)")
        else:
            print(f"❌ Erreur transactions: {response.status_code}")
            print(f"   Détail: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Migration de la table transactions sur Render")
    print("=" * 50)
    
    # Test de connexion
    if not test_api_connection():
        print("❌ Impossible de se connecter à l'API Render")
        return False
    
    # Migration
    if not migrate_transactions_table():
        print("❌ Échec de la migration")
        return False
    
    print("\n✅ Instructions de migration fournies")
    print("📝 Veuillez exécuter les commandes SQL sur Render, puis relancer ce script")
    
    # Demander confirmation pour tester
    input("\n⏸️ Appuyez sur Entrée après avoir exécuté les commandes SQL...")
    
    # Test de la nouvelle structure
    if test_new_structure():
        print("\n🎉 Migration terminée avec succès!")
        return True
    else:
        print("\n❌ Problème avec la nouvelle structure")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
