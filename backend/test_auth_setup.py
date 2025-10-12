#!/usr/bin/env python3
"""
Script de test avant d'exécuter setup_authentication.py
Vérifie que tout est prêt
"""

import os
import sys

print("\n" + "="*70)
print("🔍 VÉRIFICATION PRÉ-SETUP AUTHENTICATION")
print("="*70)

# 1. Vérifier les variables d'environnement
print("\n1. Vérification des variables d'environnement...")
required_vars = [
    "DATABASE_URL",
    "JWT_SECRET_KEY",
    "SMTP_SERVER",
    "SMTP_USERNAME",
    "SMTP_PASSWORD"
]

missing_vars = []
for var in required_vars:
    value = os.getenv(var)
    if not value:
        missing_vars.append(var)
        print(f"   ❌ {var}: NON DÉFINIE")
    else:
        # Masquer les mots de passe
        if "PASSWORD" in var or "SECRET" in var:
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value[:50] + "..." if len(value) > 50 else value
        print(f"   ✅ {var}: {display_value}")

if missing_vars:
    print(f"\n❌ Variables manquantes: {', '.join(missing_vars)}")
    print("   Vérifie ton fichier .env !")
    sys.exit(1)

# 2. Tester la connexion à la base de données
print("\n2. Test de connexion à la base de données...")
try:
    from sqlalchemy import create_engine, text
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"   ✅ Connexion réussie!")
        print(f"   PostgreSQL version: {version[:50]}...")
except Exception as e:
    print(f"   ❌ Erreur de connexion: {e}")
    sys.exit(1)

# 3. Vérifier les imports
print("\n3. Vérification des imports...")
try:
    import auth_service
    print("   ✅ auth_service")
    import email_service
    print("   ✅ email_service")
    import multitenant_service
    print("   ✅ multitenant_service")
    from models_auth import Compagnie, Utilisateur, DemandeAcces
    print("   ✅ models_auth")
except Exception as e:
    print(f"   ❌ Erreur d'import: {e}")
    sys.exit(1)

# 4. Tester le hashage de mot de passe
print("\n4. Test du service d'authentification...")
try:
    import auth_service
    test_password = "TestPassword123!"
    hashed = auth_service.hash_password(test_password)
    verified = auth_service.verify_password(test_password, hashed)
    if verified:
        print("   ✅ Hashage et vérification de mot de passe: OK")
    else:
        print("   ❌ Problème avec la vérification de mot de passe")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Erreur service auth: {e}")
    sys.exit(1)

# 5. Tester la génération de JWT
print("\n5. Test de génération JWT...")
try:
    token = auth_service.create_access_token({"test": "data"})
    decoded = auth_service.decode_access_token(token)
    if decoded and decoded.get("test") == "data":
        print("   ✅ Génération et décodage JWT: OK")
    else:
        print("   ❌ Problème avec le décodage JWT")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Erreur JWT: {e}")
    sys.exit(1)

# Résumé
print("\n" + "="*70)
print("✅ TOUS LES TESTS SONT PASSÉS !")
print("="*70)
print("\nTu peux maintenant exécuter:")
print("   python setup_authentication.py")
print("\n" + "="*70)

