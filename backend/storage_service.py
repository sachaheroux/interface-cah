#!/usr/bin/env python3
"""
Service de stockage pour Backblaze B2
"""

import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import uuid
from typing import Optional, Dict, Any

class BackblazeStorageService:
    """Service de stockage Backblaze B2 pour les PDFs"""
    
    def __init__(self):
        self.b2_application_key_id = os.getenv('B2_APPLICATION_KEY_ID')
        self.b2_application_key = os.getenv('B2_APPLICATION_KEY')
        self.b2_bucket_name = os.getenv('B2_BUCKET_NAME', 'interface-cah-pdfs')
        # Endpoint Backblaze B2 - région ca-east-006 (Canada Est)
        self.endpoint_url = 'https://s3.ca-east-006.backblazeb2.com'
        
        if not self.b2_application_key_id or not self.b2_application_key:
            raise ValueError("Variables d'environnement Backblaze B2 manquantes")
        
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.b2_application_key_id,
            aws_secret_access_key=self.b2_application_key
        )
    
    def upload_pdf(self, file_content: bytes, original_filename: str, folder: str = "documents", context: str = "document") -> Dict[str, Any]:
        """
        Uploader un PDF vers Backblaze B2
        
        Args:
            file_content: Contenu du fichier en bytes
            original_filename: Nom original du fichier
            folder: Dossier de destination (documents, bails, transactions)
        
        Returns:
            Dict avec les informations du fichier uploadé
        """
        try:
            # Générer un nom de fichier unique : nom_original_timestamp.pdf
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(original_filename)[1]
            base_name = os.path.splitext(original_filename)[0]
            
            # Nettoyer le nom de base (enlever caractères spéciaux)
            import re
            clean_base_name = re.sub(r'[^a-zA-Z0-9_-]', '_', base_name)
            clean_base_name = clean_base_name[:50]  # Limiter la longueur
            
            # Nettoyer les doubles underscores
            clean_base_name = re.sub(r'_+', '_', clean_base_name)
            clean_base_name = clean_base_name.strip('_')
            
            # Ajouter un préfixe contextuel
            context_prefix = {
                "bail": "bail",
                "transaction": "transaction",
                "facture": "facture",
                "document": "document"
            }.get(context, "document")
            
            new_filename = f"{context_prefix}_{clean_base_name}_{timestamp}{file_extension}"
            
            # Chemin complet dans le bucket
            s3_key = f"{folder}/{new_filename}"
            
            # Upload vers Backblaze B2
            self.s3_client.put_object(
                Bucket=self.b2_bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType='application/pdf',
                Metadata={
                    'original_filename': original_filename,
                    'upload_date': datetime.now().isoformat(),
                    'folder': folder
                }
            )
            
            # URL publique du fichier
            file_url = f"{self.endpoint_url}/{self.b2_bucket_name}/{s3_key}"
            
            print(f"✅ PDF uploadé vers Backblaze B2: {s3_key}")
            
            return {
                "success": True,
                "filename": new_filename,
                "original_filename": original_filename,
                "s3_key": s3_key,
                "file_url": file_url,
                "size": len(file_content),
                "folder": folder
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de l'upload: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def download_pdf(self, s3_key: str) -> Optional[bytes]:
        """
        Télécharger un PDF depuis Backblaze B2
        
        Args:
            s3_key: Clé S3 du fichier
        
        Returns:
            Contenu du fichier en bytes ou None si erreur
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.b2_bucket_name,
                Key=s3_key
            )
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                print(f"❌ Fichier non trouvé: {s3_key}")
            else:
                print(f"❌ Erreur lors du téléchargement: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement: {e}")
            return None
    
    def delete_pdf(self, s3_key: str) -> bool:
        """
        Supprimer un PDF depuis Backblaze B2
        
        Args:
            s3_key: Clé S3 du fichier
        
        Returns:
            True si succès, False sinon
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.b2_bucket_name,
                Key=s3_key
            )
            print(f"✅ PDF supprimé de Backblaze B2: {s3_key}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False
    
    def list_pdfs(self, folder: str = "documents", limit: int = 100) -> list:
        """
        Lister les PDFs dans un dossier
        
        Args:
            folder: Dossier à lister
            limit: Nombre maximum de fichiers à retourner
        
        Returns:
            Liste des fichiers
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.b2_bucket_name,
                Prefix=f"{folder}/",
                MaxKeys=limit
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['Key'].lower().endswith('.pdf'):
                        files.append({
                            "key": obj['Key'],
                            "filename": os.path.basename(obj['Key']),
                            "size": obj['Size'],
                            "last_modified": obj['LastModified'].isoformat(),
                            "url": f"{self.endpoint_url}/{self.b2_bucket_name}/{obj['Key']}"
                        })
            
            return files
            
        except Exception as e:
            print(f"❌ Erreur lors de la liste: {e}")
            return []
    
    def get_file_url(self, s3_key: str) -> str:
        """
        Obtenir l'URL publique d'un fichier
        
        Args:
            s3_key: Clé S3 du fichier
        
        Returns:
            URL publique du fichier
        """
        return f"{self.endpoint_url}/{self.b2_bucket_name}/{s3_key}"

# Instance globale du service
storage_service = None

def get_storage_service() -> BackblazeStorageService:
    """Obtenir l'instance du service de stockage"""
    global storage_service
    if storage_service is None:
        storage_service = BackblazeStorageService()
    return storage_service
