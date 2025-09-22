#!/usr/bin/env python3
"""
Script de configuration Backblaze B2 pour le stockage des PDFs
"""

import os
import boto3
from botocore.exceptions import ClientError
import json

def setup_backblaze_b2():
    """Configurer Backblaze B2 pour le stockage des PDFs"""
    print("🔧 Configuration de Backblaze B2...")
    
    # Configuration Backblaze B2
    B2_APPLICATION_KEY_ID = os.getenv('B2_APPLICATION_KEY_ID')
    B2_APPLICATION_KEY = os.getenv('B2_APPLICATION_KEY')
    B2_BUCKET_NAME = os.getenv('B2_BUCKET_NAME', 'interface-cah-pdfs')
    
    if not B2_APPLICATION_KEY_ID or not B2_APPLICATION_KEY:
        print("❌ Variables d'environnement Backblaze B2 manquantes")
        print("📝 Créez un fichier .env avec :")
        print("B2_APPLICATION_KEY_ID=votre_key_id")
        print("B2_APPLICATION_KEY=votre_application_key")
        print("B2_BUCKET_NAME=interface-cah-pdfs")
        return False
    
    try:
        # Créer le client S3 compatible Backblaze B2
        s3_client = boto3.client(
            's3',
            endpoint_url='https://s3.us-west-004.backblazeb2.com',
            aws_access_key_id=B2_APPLICATION_KEY_ID,
            aws_secret_access_key=B2_APPLICATION_KEY
        )
        
        # Vérifier si le bucket existe
        try:
            s3_client.head_bucket(Bucket=B2_BUCKET_NAME)
            print(f"✅ Bucket '{B2_BUCKET_NAME}' existe déjà")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"📦 Création du bucket '{B2_BUCKET_NAME}'...")
                s3_client.create_bucket(Bucket=B2_BUCKET_NAME)
                print(f"✅ Bucket '{B2_BUCKET_NAME}' créé avec succès")
            else:
                raise e
        
        # Tester l'upload d'un fichier de test
        test_content = b"Test de configuration Backblaze B2"
        test_key = "test/configuration.txt"
        
        s3_client.put_object(
            Bucket=B2_BUCKET_NAME,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        print(f"✅ Test d'upload réussi : {test_key}")
        
        # Tester le téléchargement
        response = s3_client.get_object(Bucket=B2_BUCKET_NAME, Key=test_key)
        downloaded_content = response['Body'].read()
        
        if downloaded_content == test_content:
            print("✅ Test de téléchargement réussi")
        else:
            print("❌ Test de téléchargement échoué")
            return False
        
        # Nettoyer le fichier de test
        s3_client.delete_object(Bucket=B2_BUCKET_NAME, Key=test_key)
        print("✅ Fichier de test nettoyé")
        
        print(f"🎉 Configuration Backblaze B2 terminée !")
        print(f"📦 Bucket: {B2_BUCKET_NAME}")
        print(f"🌐 Endpoint: https://s3.us-west-004.backblazeb2.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration: {e}")
        return False

if __name__ == "__main__":
    setup_backblaze_b2()
