#!/usr/bin/env python3
"""
Script pour vérifier l'état actuel de la table transactions sur Render
"""

import requests

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def check_table_structure():
    """Vérifier la structure actuelle de la table transactions"""
    print("🔍 Vérification de la table transactions...")
    
    try:
        # Essayer de récupérer les transactions
        response = requests.get(f"{RENDER_API_URL}/api/transactions")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', [])
            print(f"✅ Table existe: {len(transactions)} transactions")
            if transactions:
                print(f"   Structure: {list(transactions[0].keys())}")
            return "exists_new"
        elif response.status_code == 500:
            error_text = response.text
            if "no such column: transactions.categorie" in error_text:
                print("⚠️  Table existe mais avec l'ancienne structure")
                return "exists_old"
            elif "no such table: transactions" in error_text:
                print("❌ Table n'existe pas")
                return "not_exists"
            else:
                print(f"❌ Autre erreur: {error_text}")
                return "error"
        else:
            print(f"❌ Erreur inattendue: {response.status_code}")
            return "error"
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return "error"

def main():
    """Fonction principale"""
    print("🚀 VÉRIFICATION DE LA TABLE TRANSACTIONS")
    print("=" * 50)
    
    status = check_table_structure()
    
    print(f"\n📊 RÉSULTAT: {status}")
    
    if status == "exists_new":
        print("✅ La table est déjà à jour avec la nouvelle structure!")
        print("💡 Le problème vient peut-être du frontend")
    elif status == "exists_old":
        print("⚠️  La table existe mais avec l'ancienne structure")
        print("💡 Il faut la migrer vers la nouvelle structure")
    elif status == "not_exists":
        print("❌ La table n'existe pas")
        print("💡 Il faut la créer avec la nouvelle structure")
    else:
        print("❌ Erreur lors de la vérification")
        print("💡 Il faut investiguer plus")

if __name__ == "__main__":
    main()
