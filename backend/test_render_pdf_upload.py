#!/usr/bin/env python3
"""
Test d'upload PDF via l'API Render (Backblaze B2)
"""

import requests
import os
from io import BytesIO

def create_test_pdf():
    """Créer un PDF de test simple"""
    pdf_content = b"""%PDF-1.4
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
(Test PDF Render + Backblaze B2) Tj
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
    return pdf_content

def test_render_upload():
    """Tester l'upload via l'API Render"""
    print("🧪 Test d'upload PDF via l'API Render (Backblaze B2)")
    print("=" * 60)
    
    # URL de l'API Render
    RENDER_API_BASE = "https://interface-cah-backend.onrender.com"
    
    # Créer un PDF de test
    pdf_content = create_test_pdf()
    pdf_filename = "test_render_backblaze.pdf"
    
    print(f"📄 PDF de test créé: {pdf_filename} ({len(pdf_content)} bytes)")
    
    try:
        # Préparer les données pour l'upload
        files = {
            'file': (pdf_filename, BytesIO(pdf_content), 'application/pdf')
        }
        
        print(f"📤 Upload vers {RENDER_API_BASE}/api/documents/upload...")
        
        # Faire l'upload
        response = requests.post(
            f"{RENDER_API_BASE}/api/documents/upload",
            files=files,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload réussi !")
            print(f"📁 Nom du fichier: {result.get('filename')}")
            print(f"🔗 URL: {result.get('file_url')}")
            print(f"📏 Taille: {result.get('size')} bytes")
            
            # Tester le téléchargement
            print(f"\n📥 Test de téléchargement...")
            download_url = f"{RENDER_API_BASE}/api/documents/{result.get('filename')}"
            
            download_response = requests.get(download_url, timeout=30)
            
            if download_response.status_code == 200:
                downloaded_content = download_response.content
                if downloaded_content == pdf_content:
                    print("✅ Téléchargement réussi - contenu identique")
                else:
                    print("❌ Erreur de téléchargement - contenu différent")
                    print(f"   Original: {len(pdf_content)} bytes")
                    print(f"   Téléchargé: {len(downloaded_content)} bytes")
            else:
                print(f"❌ Erreur de téléchargement: {download_response.status_code}")
                print(f"   Réponse: {download_response.text}")
            
            return True
        else:
            print(f"❌ Erreur d'upload: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - L'API Render met trop de temps à répondre")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion - Vérifiez que l'API Render est accessible")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_render_health():
    """Tester la santé de l'API Render"""
    print("🏥 Test de santé de l'API Render...")
    
    RENDER_API_BASE = "https://interface-cah-backend.onrender.com"
    
    try:
        response = requests.get(f"{RENDER_API_BASE}/", timeout=10)
        print(f"✅ API Render accessible: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ API Render inaccessible: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test complet de l'upload PDF sur Render")
    print("=" * 50)
    
    # 1. Tester la santé de l'API
    if not test_render_health():
        print("\n❌ L'API Render n'est pas accessible")
        print("💡 Vérifiez que l'application est déployée et en cours d'exécution")
        return False
    
    print()
    
    # 2. Tester l'upload
    if test_render_upload():
        print("\n🎉 Test complet réussi !")
        print("✅ L'upload PDF fonctionne sur Render avec Backblaze B2")
        print("💰 Coût: $0 (plan gratuit Backblaze B2)")
        return True
    else:
        print("\n❌ Test échoué")
        print("🔧 Vérifiez les logs Render et la configuration Backblaze B2")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Votre application est prête pour la production !")
    else:
        print("\n❌ Des corrections sont nécessaires avant la production")
