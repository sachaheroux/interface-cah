#!/usr/bin/env python3
"""
Test direct de l'endpoint d'upload PDF
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
(Test PDF Transaction) Tj
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

def test_upload_direct():
    """Tester l'upload directement avec requests"""
    print("🧪 Test direct de l'upload PDF")
    print("=" * 40)
    
    RENDER_API_BASE = "https://interface-cah-backend.onrender.com"
    
    # Créer un PDF de test
    pdf_content = create_test_pdf()
    pdf_filename = "test_transaction_direct.pdf"
    
    print(f"📄 PDF de test créé: {pdf_filename} ({len(pdf_content)} bytes)")
    
    try:
        # Préparer les données pour l'upload
        files = {
            'file': (pdf_filename, BytesIO(pdf_content), 'application/pdf')
        }
        
        print(f"📤 Upload vers {RENDER_API_BASE}/api/documents/upload...")
        
        # Faire l'upload avec requests (comme le frontend devrait le faire)
        response = requests.post(
            f"{RENDER_API_BASE}/api/documents/upload",
            files=files,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload réussi !")
            print(f"📁 Nom du fichier: {result.get('filename')}")
            print(f"🔗 URL: {result.get('file_url')}")
            print(f"📏 Taille: {result.get('size')} bytes")
            return True
        else:
            print(f"❌ Erreur d'upload: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = test_upload_direct()
    if success:
        print("\n🎉 L'endpoint fonctionne ! Le problème est côté frontend")
    else:
        print("\n❌ L'endpoint a un problème")
