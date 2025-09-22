#!/usr/bin/env python3
"""
Script pour vérifier l'état des PDFs
Compare les PDFs dans la base de données vs ceux stockés sur Backblaze B2
"""

import os
import requests
from dotenv import load_dotenv
from storage_service import get_storage_service

# Charger les variables d'environnement
load_dotenv()

def check_pdf_status():
    """Vérifier l'état des PDFs"""
    print("🔍 Vérification de l'état des PDFs")
    print("=" * 50)
    
    api_url = os.getenv('RENDER_API_URL', 'https://interface-cah-backend.onrender.com')
    
    # Récupérer les PDFs de la base de données
    db_pdfs = set()
    
    print("\n📋 PDFs dans la base de données:")
    
    try:
        # Transactions
        response = requests.get(f'{api_url}/api/transactions')
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', []) if isinstance(data, dict) else data
            print(f"  📄 Transactions: {len(transactions)}")
            for t in transactions:
                if t.get('pdf_transaction'):
                    db_pdfs.add(t['pdf_transaction'])
                    print(f"    - {t['pdf_transaction']}")
        
        # Baux
        response = requests.get(f'{api_url}/api/leases')
        if response.status_code == 200:
            data = response.json()
            leases = data.get('data', []) if isinstance(data, dict) else data
            print(f"  📄 Baux: {len(leases)}")
            for l in leases:
                if l.get('pdf_bail'):
                    db_pdfs.add(l['pdf_bail'])
                    print(f"    - {l['pdf_bail']}")
        
        print(f"\n✅ Total PDFs dans la DB: {len(db_pdfs)}")
        
    except Exception as e:
        print(f"❌ Erreur récupération DB: {e}")
        return
    
    # Récupérer les PDFs stockés
    print("\n📁 PDFs stockés sur Backblaze B2:")
    
    try:
        storage_service = get_storage_service()
        stored_pdfs = set()
        
        folders = ['documents', 'bails', 'transactions']
        for folder in folders:
            pdfs = storage_service.list_pdfs(folder)
            print(f"  📂 Dossier {folder}: {len(pdfs)} PDFs")
            for pdf in pdfs:
                filename = pdf['filename']
                stored_pdfs.add(filename)
                print(f"    - {filename}")
        
        print(f"\n✅ Total PDFs stockés: {len(stored_pdfs)}")
        
        # Analyser les différences
        print("\n📊 Analyse:")
        
        # PDFs dans la DB mais pas stockés
        missing_pdfs = db_pdfs - stored_pdfs
        if missing_pdfs:
            print(f"  ❌ PDFs manquants sur Backblaze B2: {len(missing_pdfs)}")
            for pdf in missing_pdfs:
                print(f"    - {pdf}")
        else:
            print("  ✅ Tous les PDFs de la DB sont stockés")
        
        # PDFs stockés mais pas dans la DB (orphelins)
        orphaned_pdfs = stored_pdfs - db_pdfs
        if orphaned_pdfs:
            print(f"  🗑️ PDFs orphelins: {len(orphaned_pdfs)}")
            for pdf in orphaned_pdfs:
                print(f"    - {pdf}")
        else:
            print("  ✅ Aucun PDF orphelin")
        
        # Taille totale
        total_size = 0
        for folder in folders:
            pdfs = storage_service.list_pdfs(folder)
            for pdf in pdfs:
                total_size += pdf.get('size', 0)
        
        print(f"\n💾 Taille totale stockée: {total_size / 1024:.2f} KB")
        
    except Exception as e:
        print(f"❌ Erreur récupération Backblaze B2: {e}")

if __name__ == "__main__":
    check_pdf_status()
