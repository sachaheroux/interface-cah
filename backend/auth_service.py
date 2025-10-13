#!/usr/bin/env python3
"""
Service d'authentification pour Interface CAH
Gestion JWT, bcrypt, codes de vérification
"""

import os
import secrets
import string
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30  # Token valide 30 jours (session persistante)


# ==========================================
# GESTION DES MOTS DE PASSE
# ==========================================

def hash_password(password: str) -> str:
    """
    Hasher un mot de passe avec bcrypt directement
    Limite à 72 bytes pour compatibilité bcrypt
    """
    # Bcrypt a une limite de 72 bytes
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifier un mot de passe contre son hash
    """
    # Même limitation à 72 bytes pour la vérification
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ==========================================
# GESTION DES TOKENS JWT
# ==========================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Créer un token JWT
    
    Args:
        data: Données à encoder dans le token (user_id, company_id, role, etc.)
        expires_delta: Durée de validité (par défaut 30 jours)
    
    Returns:
        Token JWT encodé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Décoder et valider un token JWT
    
    Args:
        token: Token JWT à décoder
    
    Returns:
        Données décodées ou None si invalide/expiré
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"❌ Erreur décodage JWT: {e}")
        return None


# ==========================================
# GÉNÉRATION DE CODES
# ==========================================

def generate_verification_code(length: int = 6) -> str:
    """
    Générer un code de vérification alphanumérique
    
    Args:
        length: Longueur du code (défaut 6)
    
    Returns:
        Code alphanumérique en majuscules
    """
    characters = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(characters) for _ in range(length))
    return code


def generate_reset_code(length: int = 8) -> str:
    """
    Générer un code de réinitialisation de mot de passe
    
    Args:
        length: Longueur du code (défaut 8)
    
    Returns:
        Code alphanumérique en majuscules
    """
    return generate_verification_code(length)


def is_code_expired(expiration_date: datetime) -> bool:
    """
    Vérifier si un code a expiré
    
    Args:
        expiration_date: Date d'expiration du code
    
    Returns:
        True si expiré, False sinon
    """
    return datetime.utcnow() > expiration_date


def get_code_expiration(minutes: int = 15) -> datetime:
    """
    Obtenir une date d'expiration pour un code
    
    Args:
        minutes: Nombre de minutes de validité (défaut 15)
    
    Returns:
        Datetime d'expiration
    """
    return datetime.utcnow() + timedelta(minutes=minutes)


# ==========================================
# VALIDATION DES DONNÉES
# ==========================================

def is_valid_email(email: str) -> bool:
    """
    Validation basique d'email
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_strong_password(password: str) -> tuple[bool, str]:
    """
    Vérifier la force d'un mot de passe
    
    Critères:
    - Au moins 8 caractères
    - Au moins une majuscule
    - Au moins une minuscule
    - Au moins un chiffre
    - Au moins un caractère spécial
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    if not any(c.isupper() for c in password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not any(c.islower() for c in password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if not any(c.isdigit() for c in password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial"
    
    return True, ""


def sanitize_schema_name(company_name: str) -> str:
    """
    Créer un nom de schéma PostgreSQL valide à partir du nom de compagnie
    
    Args:
        company_name: Nom de la compagnie
    
    Returns:
        Nom de schéma valide (company_xxx)
    """
    import re
    # Garder seulement les caractères alphanumériques
    clean_name = re.sub(r'[^a-zA-Z0-9]', '_', company_name.lower())
    # Limiter à 50 caractères
    clean_name = clean_name[:50]
    # Ajouter un préfixe et un suffixe unique
    unique_suffix = secrets.token_hex(4)
    return f"company_{clean_name}_{unique_suffix}"


# ==========================================
# UTILITAIRES
# ==========================================

def calculate_age(date_naissance: datetime) -> int:
    """
    Calculer l'âge à partir d'une date de naissance
    """
    today = datetime.utcnow()
    age = today.year - date_naissance.year
    
    # Ajuster si l'anniversaire n'est pas encore passé cette année
    if (today.month, today.day) < (date_naissance.month, date_naissance.day):
        age -= 1
    
    return age


if __name__ == "__main__":
    # Tests rapides
    print("🧪 Tests du service d'authentification")
    
    # Test hash password
    password = "Champion2024!"
    hashed = hash_password(password)
    print(f"✅ Hash: {hashed[:50]}...")
    print(f"✅ Vérification: {verify_password(password, hashed)}")
    
    # Test JWT
    token = create_access_token({"user_id": 1, "company_id": 1, "role": "admin"})
    print(f"✅ Token: {token[:50]}...")
    decoded = decode_access_token(token)
    print(f"✅ Décodé: {decoded}")
    
    # Test codes
    code_email = generate_verification_code()
    code_reset = generate_reset_code()
    print(f"✅ Code email: {code_email}")
    print(f"✅ Code reset: {code_reset}")
    
    # Test validation password
    valid, msg = is_strong_password("Champion2024!")
    print(f"✅ Password valide: {valid} - {msg}")
    
    # Test schema name
    schema = sanitize_schema_name("CAH Immobilier Inc.")
    print(f"✅ Schema name: {schema}")

