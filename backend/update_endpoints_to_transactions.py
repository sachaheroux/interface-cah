#!/usr/bin/env python3
"""
Script pour mettre à jour les endpoints de factures vers transactions dans main.py
"""

import re

def update_main_py():
    """Mettre à jour main.py pour remplacer les endpoints de factures par des transactions"""
    
    main_py_path = "main.py"
    
    try:
        # Lire le fichier
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔄 Mise à jour des endpoints factures vers transactions...")
        
        # 1. Remplacer les constantes
        content = re.sub(
            r'# Constantes pour les factures.*?INVOICE_TYPES = \{.*?\}\n',
            '''# Constantes pour les transactions
TRANSACTION_TYPES = [
    "loyer",
    "facture", 
    "maintenance",
    "revenus",
    "depenses",
    "investissement",
    "frais",
    "autre"
]

TRANSACTION_PAYMENT_METHODS = [
    "virement",
    "cheque", 
    "especes",
    "carte",
    "autre"
]

TRANSACTION_STATUSES = [
    "en_attente",
    "paye",
    "annule"
]

''',
            content,
            flags=re.DOTALL
        )
        
        # 2. Remplacer l'endpoint des constantes
        content = re.sub(
            r'@app\.get\("/api/invoices/constants"\).*?raise HTTPException\(status_code=500, detail="Erreur interne du serveur"\)',
            '''@app.get("/api/transactions/constants")
async def get_transaction_constants():
    """Récupérer les constantes pour les transactions (types, méthodes de paiement, statuts, etc.)"""
    try:
        print("🔧 Récupération des constantes de transactions...")
        return {
            "types": TRANSACTION_TYPES,
            "payment_methods": TRANSACTION_PAYMENT_METHODS,
            "statuses": TRANSACTION_STATUSES
        }
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des constantes de transactions: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")''',
            content,
            flags=re.DOTALL
        )
        
        # 3. Remplacer tous les endpoints /api/invoices par /api/transactions
        content = re.sub(r'/api/invoices', '/api/transactions', content)
        
        # 4. Remplacer les noms de fonctions et variables
        content = re.sub(r'get_invoices', 'get_transactions', content)
        content = re.sub(r'get_invoice', 'get_transaction', content)
        content = re.sub(r'create_invoice', 'create_transaction', content)
        content = re.sub(r'update_invoice', 'update_transaction', content)
        content = re.sub(r'delete_invoice', 'delete_transaction', content)
        
        content = re.sub(r'invoice_id', 'transaction_id', content)
        content = re.sub(r'invoice_data', 'transaction_data', content)
        content = re.sub(r'update_data', 'update_data', content)
        
        content = re.sub(r'invoices =', 'transactions =', content)
        content = re.sub(r'invoice =', 'transaction =', content)
        
        # 5. Remplacer les commentaires et descriptions
        content = re.sub(r'factures', 'transactions', content)
        content = re.sub(r'Factures', 'Transactions', content)
        content = re.sub(r'facture', 'transaction', content)
        content = re.sub(r'Facture', 'Transaction', content)
        
        # 6. Remplacer les champs spécifiques
        content = re.sub(r'id_facture', 'id_transaction', content)
        content = re.sub(r'categorie', 'type_transaction', content)
        content = re.sub(r'no_facture', 'reference', content)
        content = re.sub(r'pdf_facture', 'pdf_document', content)
        content = re.sub(r'type_paiement', 'methode_paiement', content)
        
        # 7. Ajouter les nouveaux champs pour les transactions
        # Remplacer les anciens champs par les nouveaux
        content = re.sub(r'date', 'date_transaction', content)
        
        # Écrire le fichier modifié
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ main.py mis à jour avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour de main.py: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Mise à jour des endpoints vers transactions")
    print("=" * 50)
    
    success = update_main_py()
    
    if success:
        print("\n🎉 Mise à jour réussie!")
        print("💡 Vérifiez le fichier main.py avant de déployer.")
    else:
        print("\n💥 Mise à jour échouée!")
        print("🔧 Vérifiez les erreurs ci-dessus.")
