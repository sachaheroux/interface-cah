#!/usr/bin/env python3
"""
Script pour tester les différents endpoints Backblaze B2
"""

import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

def test_endpoint(endpoint_url, key_id, app_key, bucket_name):
    """Tester un endpoint Backblaze B2"""
    try:
        print(f"🧪 Test de l'endpoint: {endpoint_url}")
        
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=key_id,
            aws_secret_access_key=app_key
        )
        
        # Test simple - lister les objets
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            MaxKeys=1
        )
        
        print(f"✅ Succès avec {endpoint_url}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ Erreur {error_code} avec {endpoint_url}")
        return False
    except Exception as e:
        print(f"❌ Exception avec {endpoint_url}: {e}")
        return False

def main():
    """Tester tous les endpoints Backblaze B2"""
    print("🔍 Recherche du bon endpoint Backblaze B2...")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    key_id = os.getenv('B2_APPLICATION_KEY_ID')
    app_key = os.getenv('B2_APPLICATION_KEY')
    bucket_name = os.getenv('B2_BUCKET_NAME', 'interface-cah-pdfs')
    
    if not key_id or not app_key:
        print("❌ Variables d'environnement manquantes")
        return
    
    # Endpoints Backblaze B2 à tester
    endpoints = [
        'https://s3.us-west-004.backblazeb2.com',
        'https://s3.us-west-002.backblazeb2.com',
        'https://s3.us-west-003.backblazeb2.com',
        'https://s3.us-west-001.backblazeb2.com',
        'https://s3.us-west-000.backblazeb2.com',
        'https://s3.us-west-005.backblazeb2.com'
    ]
    
    working_endpoint = None
    
    for endpoint in endpoints:
        if test_endpoint(endpoint, key_id, app_key, bucket_name):
            working_endpoint = endpoint
            break
    
    if working_endpoint:
        print(f"\n🎉 Endpoint fonctionnel trouvé: {working_endpoint}")
        print(f"📝 Mettez à jour storage_service.py avec cet endpoint")
        
        # Mettre à jour le fichier storage_service.py
        try:
            with open('storage_service.py', 'r') as f:
                content = f.read()
            
            # Remplacer l'endpoint
            old_endpoint = 'https://s3.us-west-004.backblazeb2.com'
            new_content = content.replace(old_endpoint, working_endpoint)
            
            with open('storage_service.py', 'w') as f:
                f.write(new_content)
            
            print(f"✅ storage_service.py mis à jour avec {working_endpoint}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour: {e}")
    else:
        print("\n❌ Aucun endpoint fonctionnel trouvé")
        print("🔧 Vérifiez vos clés Backblaze B2 et le nom du bucket")

if __name__ == "__main__":
    main()
