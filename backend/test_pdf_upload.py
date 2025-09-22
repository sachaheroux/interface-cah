#!/usr/bin/env python3
"""
Test d'upload d'un PDF vers Backblaze B2
"""

import os
from storage_service import get_storage_service
from dotenv import load_dotenv

def test_pdf_upload():
    """Tester l'upload d'un PDF"""
    print("📤 Test d'upload PDF vers Backblaze B2")
    print("=" * 40)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    try:
        # Initialiser le service de stockage
        storage_service = get_storage_service()
        
        # Créer un PDF de test simple
        test_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF Backblaze B2) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF"""
        
        print("📄 Création d'un PDF de test...")
        
        # Upload vers Backblaze B2
        result = storage_service.upload_pdf(
            file_content=test_pdf_content,
            original_filename="test_backblaze.pdf",
            folder="documents"
        )
        
        if result["success"]:
            print("✅ Upload réussi !")
            print(f"📁 Nom du fichier: {result['filename']}")
            print(f"🔗 URL: {result['file_url']}")
            print(f"📏 Taille: {result['size']} bytes")
            print(f"🗂️ Dossier: {result['folder']}")
            
            # Tester le téléchargement
            print("\n📥 Test de téléchargement...")
            downloaded_content = storage_service.download_pdf(result['s3_key'])
            
            if downloaded_content == test_pdf_content:
                print("✅ Téléchargement réussi - contenu identique")
            else:
                print("❌ Erreur de téléchargement - contenu différent")
                return False
            
            # Nettoyer le fichier de test
            print("\n🧹 Nettoyage du fichier de test...")
            if storage_service.delete_pdf(result['s3_key']):
                print("✅ Fichier de test supprimé")
            else:
                print("⚠️ Impossible de supprimer le fichier de test")
            
            print("\n🎉 Test complet réussi !")
            print("✅ Backblaze B2 est prêt pour votre application")
            return True
        else:
            print(f"❌ Erreur d'upload: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    success = test_pdf_upload()
    if success:
        print("\n🚀 Votre application est prête à utiliser Backblaze B2 !")
        print("💰 Coût: $0 (plan gratuit - 10 GB)")
    else:
        print("\n❌ Veuillez corriger les erreurs avant de continuer")
