#!/usr/bin/env python3
"""
Script de diagnostic Backblaze B2
"""

import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

def debug_backblaze():
    """Diagnostic complet Backblaze B2"""
    print("🔍 Diagnostic Backblaze B2")
    print("=" * 40)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    key_id = os.getenv('B2_APPLICATION_KEY_ID')
    app_key = os.getenv('B2_APPLICATION_KEY')
    bucket_name = os.getenv('B2_BUCKET_NAME', 'interface-cah-pdfs')
    
    print(f"🔑 Key ID: {key_id}")
    print(f"🔑 App Key: {app_key[:8]}...")
    print(f"📦 Bucket: {bucket_name}")
    print()
    
    if not key_id or not app_key:
        print("❌ Variables d'environnement manquantes")
        return
    
    # Tester avec l'endpoint ca-east-006 (Canada Est)
    endpoint = 'https://s3.ca-east-006.backblazeb2.com'
    print(f"🌐 Endpoint: {endpoint}")
    
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=key_id,
            aws_secret_access_key=app_key
        )
        
        # Test 1: Lister les buckets
        print("\n📋 Test 1: Lister les buckets...")
        try:
            response = s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            print(f"✅ Buckets trouvés: {buckets}")
            
            if bucket_name not in buckets:
                print(f"❌ Bucket '{bucket_name}' non trouvé")
                print(f"💡 Buckets disponibles: {buckets}")
                return
            else:
                print(f"✅ Bucket '{bucket_name}' trouvé")
                
        except ClientError as e:
            print(f"❌ Erreur list_buckets: {e}")
            return
        
        # Test 2: Vérifier les permissions sur le bucket
        print(f"\n🔐 Test 2: Vérifier les permissions sur '{bucket_name}'...")
        try:
            response = s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Permissions OK sur '{bucket_name}'")
        except ClientError as e:
            print(f"❌ Erreur head_bucket: {e}")
            return
        
        # Test 3: Lister les objets dans le bucket
        print(f"\n📁 Test 3: Lister les objets dans '{bucket_name}'...")
        try:
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                MaxKeys=5
            )
            
            if 'Contents' in response:
                objects = [obj['Key'] for obj in response['Contents']]
                print(f"✅ Objets trouvés: {objects}")
            else:
                print("✅ Bucket vide (normal pour un nouveau bucket)")
                
        except ClientError as e:
            print(f"❌ Erreur list_objects_v2: {e}")
            return
        
        # Test 4: Upload d'un fichier de test
        print(f"\n📤 Test 4: Upload d'un fichier de test...")
        try:
            test_content = b"Test de connexion Backblaze B2"
            test_key = "test/connexion.txt"
            
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content,
                ContentType='text/plain'
            )
            print(f"✅ Upload réussi: {test_key}")
            
            # Nettoyer le fichier de test
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            print(f"✅ Fichier de test supprimé")
            
        except ClientError as e:
            print(f"❌ Erreur upload: {e}")
            return
        
        print(f"\n🎉 Tous les tests sont passés !")
        print(f"✅ Backblaze B2 est correctement configuré")
        print(f"✅ Endpoint fonctionnel: {endpoint}")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    debug_backblaze()
