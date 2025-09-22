#!/usr/bin/env python3
"""
Script de nettoyage des PDFs orphelins sur Backblaze B2
Supprime les PDFs qui ne sont plus référencés dans la base de données
"""

import os
import requests
from dotenv import load_dotenv
from storage_service import get_storage_service

# Charger les variables d'environnement
load_dotenv()

def get_referenced_pdfs():
    """Récupérer tous les PDFs référencés dans la base de données"""
    api_url = os.getenv('RENDER_API_URL', 'https://interface-cah-backend.onrender.com')
    referenced_pdfs = set()
    
    print("🔍 Récupération des PDFs référencés dans la base de données...")
    
    try:
        # Récupérer les transactions
        response = requests.get(f'{api_url}/api/transactions')
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', []) if isinstance(data, dict) else data
            for t in transactions:
                if t.get('pdf_transaction'):
                    referenced_pdfs.add(t['pdf_transaction'])
                    print(f"  📄 Transaction PDF: {t['pdf_transaction']}")
        
        # Récupérer les baux
        response = requests.get(f'{api_url}/api/leases')
        if response.status_code == 200:
            data = response.json()
            leases = data.get('data', []) if isinstance(data, dict) else data
            for l in leases:
                if l.get('pdf_bail'):
                    referenced_pdfs.add(l['pdf_bail'])
                    print(f"  📄 Bail PDF: {l['pdf_bail']}")
        
        print(f"✅ Total PDFs référencés: {len(referenced_pdfs)}")
        return referenced_pdfs
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des PDFs référencés: {e}")
        return set()

def get_stored_pdfs():
    """Récupérer tous les PDFs stockés sur Backblaze B2"""
    print("🔍 Récupération des PDFs stockés sur Backblaze B2...")
    
    try:
        storage_service = get_storage_service()
        
        # Lister tous les PDFs dans tous les dossiers
        all_pdfs = []
        folders = ['documents', 'bails', 'transactions']
        
        for folder in folders:
            pdfs = storage_service.list_pdfs(folder)
            for pdf in pdfs:
                # Extraire juste le nom du fichier (sans le chemin)
                filename = pdf['filename']
                all_pdfs.append(filename)
                print(f"  📁 {folder}/{filename}")
        
        print(f"✅ Total PDFs stockés: {len(all_pdfs)}")
        return all_pdfs
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des PDFs stockés: {e}")
        return []

def cleanup_orphaned_pdfs():
    """Nettoyer les PDFs orphelins"""
    print("🧹 Nettoyage des PDFs orphelins...")
    print("=" * 50)
    
    # Récupérer les PDFs référencés et stockés
    referenced_pdfs = get_referenced_pdfs()
    stored_pdfs = get_stored_pdfs()
    
    # Trouver les PDFs orphelins
    orphaned_pdfs = []
    for pdf in stored_pdfs:
        if pdf not in referenced_pdfs:
            orphaned_pdfs.append(pdf)
    
    print(f"\n📊 Résumé:")
    print(f"  📄 PDFs référencés: {len(referenced_pdfs)}")
    print(f"  📁 PDFs stockés: {len(stored_pdfs)}")
    print(f"  🗑️ PDFs orphelins: {len(orphaned_pdfs)}")
    
    if not orphaned_pdfs:
        print("✅ Aucun PDF orphelin trouvé !")
        return
    
    print(f"\n🗑️ PDFs orphelins à supprimer:")
    for pdf in orphaned_pdfs:
        print(f"  - {pdf}")
    
    # Demander confirmation
    confirm = input(f"\n❓ Voulez-vous supprimer ces {len(orphaned_pdfs)} PDFs orphelins ? (oui/non): ")
    
    if confirm.lower() in ['oui', 'o', 'yes', 'y']:
        print("\n🗑️ Suppression des PDFs orphelins...")
        
        storage_service = get_storage_service()
        deleted_count = 0
        
        for pdf in orphaned_pdfs:
            try:
                # Essayer de supprimer depuis différents dossiers
                folders = ['documents', 'bails', 'transactions']
                deleted = False
                
                for folder in folders:
                    pdf_key = f"{folder}/{pdf}"
                    if storage_service.delete_pdf(pdf_key):
                        print(f"  ✅ Supprimé: {pdf_key}")
                        deleted = True
                        deleted_count += 1
                        break
                
                if not deleted:
                    print(f"  ⚠️ Non trouvé: {pdf}")
                    
            except Exception as e:
                print(f"  ❌ Erreur suppression {pdf}: {e}")
        
        print(f"\n✅ Nettoyage terminé: {deleted_count}/{len(orphaned_pdfs)} PDFs supprimés")
        
    else:
        print("❌ Nettoyage annulé")

if __name__ == "__main__":
    print("🧹 Script de nettoyage des PDFs orphelins")
    print("=" * 50)
    cleanup_orphaned_pdfs()
