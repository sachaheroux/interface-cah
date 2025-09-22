#!/usr/bin/env python3
"""
Script pour déboguer la configuration Backblaze B2
Vérifie les variables d'environnement et la connexion
"""

import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def debug_backblaze_config():
    """Déboguer la configuration Backblaze B2"""
    print("🔍 Debug de la configuration Backblaze B2")
    print("=" * 50)
    
    # Vérifier les variables d'environnement
    print("📋 Variables d'environnement:")
    key_id = os.getenv('B2_APPLICATION_KEY_ID')
    app_key = os.getenv('B2_APPLICATION_KEY')
    bucket_name = os.getenv('B2_BUCKET_NAME', 'interface-cah-pdfs')
    
    print(f"  🔑 B2_APPLICATION_KEY_ID: {key_id[:8] if key_id else 'MANQUANT'}...")
    print(f"  🔑 B2_APPLICATION_KEY: {app_key[:8] if app_key else 'MANQUANT'}...")
    print(f"  📦 B2_BUCKET_NAME: {bucket_name}")
    
    if not key_id or not app_key:
        print("❌ Variables d'environnement manquantes")
        return
    
    # Tester la connexion
    print("\n🔌 Test de connexion:")
    
    try:
        # Utiliser l'endpoint ca-east-006
        endpoint_url = 'https://s3.ca-east-006.backblazeb2.com'
        print(f"  🌐 Endpoint: {endpoint_url}")
        
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=key_id,
            aws_secret_access_key=app_key
        )
        
        # Lister tous les buckets
        print("  📋 Test: Lister tous les buckets...")
        response = s3_client.list_buckets()
        buckets = [b['Name'] for b in response['Buckets']]
        print(f"  ✅ Buckets trouvés: {buckets}")
        
        if bucket_name in buckets:
            print(f"  ✅ Bucket '{bucket_name}' trouvé")
            
            # Tester l'accès au bucket
            print(f"  📋 Test: Accès au bucket '{bucket_name}'...")
            try:
                response = s3_client.head_bucket(Bucket=bucket_name)
                print("  ✅ Accès au bucket OK")
                
                # Lister les objets
                print(f"  📋 Test: Lister les objets dans '{bucket_name}'...")
                response = s3_client.list_objects_v2(Bucket=bucket_name)
                
                if 'Contents' in response:
                    print(f"  ✅ Objets trouvés: {len(response['Contents'])}")
                    for obj in response['Contents'][:5]:  # Afficher les 5 premiers
                        print(f"    - {obj['Key']} ({obj['Size']} bytes)")
                else:
                    print("  ⚠️ Aucun objet dans le bucket")
                    
            except ClientError as e:
                print(f"  ❌ Erreur d'accès au bucket: {e}")
        else:
            print(f"  ❌ Bucket '{bucket_name}' non trouvé")
            print(f"  💡 Buckets disponibles: {buckets}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_backblaze_config()
