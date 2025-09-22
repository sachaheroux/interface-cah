#!/usr/bin/env python3
"""
Script de configuration Backblaze B2
"""

import os

def create_env_file():
    """Créer le fichier .env avec les variables Backblaze B2"""
    print("🔧 Configuration des variables d'environnement Backblaze B2")
    print("=" * 60)
    
    # Demander les clés à l'utilisateur
    print("📝 Veuillez entrer vos clés Backblaze B2 :")
    print("(Vous les trouverez dans votre dashboard Backblaze B2 > App Keys)")
    print()
    
    key_id = input("🔑 Application Key ID: ").strip()
    application_key = input("🔑 Application Key: ").strip()
    
    if not key_id or not application_key:
        print("❌ Les clés ne peuvent pas être vides")
        return False
    
    # Contenu du fichier .env
    env_content = f"""# Backblaze B2 Configuration
B2_APPLICATION_KEY_ID={key_id}
B2_APPLICATION_KEY={application_key}
B2_BUCKET_NAME=interface-cah-pdfs

# Autres variables d'environnement existantes
DATA_DIR=./data
"""
    
    # Écrire le fichier .env
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Fichier .env créé avec succès")
        print("📁 Fichier: backend/.env")
        print()
        print("🔒 IMPORTANT: Ne partagez jamais ce fichier .env !")
        print("   Il contient vos clés secrètes Backblaze B2")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier .env: {e}")
        return False

def test_configuration():
    """Tester la configuration Backblaze B2"""
    print("\n🧪 Test de la configuration...")
    
    try:
        # Charger les variables d'environnement
        from dotenv import load_dotenv
        load_dotenv()
        
        # Vérifier que les variables sont définies
        key_id = os.getenv('B2_APPLICATION_KEY_ID')
        app_key = os.getenv('B2_APPLICATION_KEY')
        bucket_name = os.getenv('B2_BUCKET_NAME')
        
        if not key_id or not app_key:
            print("❌ Variables d'environnement Backblaze B2 manquantes")
            return False
        
        print(f"✅ Application Key ID: {key_id[:8]}...")
        print(f"✅ Application Key: {app_key[:8]}...")
        print(f"✅ Bucket Name: {bucket_name}")
        
        # Tester la connexion
        from storage_service import get_storage_service
        storage_service = get_storage_service()
        
        # Test simple
        test_result = storage_service.list_pdfs(folder="documents", limit=1)
        print(f"✅ Connexion Backblaze B2 réussie !")
        print(f"📁 Fichiers trouvés: {len(test_result)}")
        
        return True
        
    except ImportError:
        print("📦 Installation des dépendances...")
        print("   pip install python-dotenv boto3")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Configuration Backblaze B2 pour Interface CAH")
    print("=" * 50)
    
    # 1. Créer le fichier .env
    if not create_env_file():
        return False
    
    # 2. Tester la configuration
    if not test_configuration():
        print("\n❌ Configuration échouée")
        print("🔧 Vérifiez vos clés Backblaze B2 et réessayez")
        return False
    
    print("\n🎉 Configuration terminée avec succès !")
    print("✅ Votre application est maintenant prête à utiliser Backblaze B2")
    print("💰 Coût: $0 (plan gratuit - 10 GB)")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Prochaine étape: Tester l'upload d'un PDF")
    else:
        print("\n❌ Veuillez corriger les erreurs et réessayer")
