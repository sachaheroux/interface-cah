# Fonctionnement du Système de Réinitialisation de Mot de Passe

## 1. Stockage des Mots de Passe

### 1.1 Hachage avec bcrypt

Les mots de passe ne sont **jamais stockés en clair** dans la base de données. Ils sont hachés avec **bcrypt**, un algorithme de hachage sécurisé.

**Code dans `auth_service.py` :**

```python
def hash_password(password: str) -> str:
    # Bcrypt a une limite de 72 bytes
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()  # Génère un "sel" aléatoire unique
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')
```

**Explication :**
- `bcrypt.gensalt()` génère un "sel" aléatoire unique pour chaque mot de passe
- Le sel est combiné avec le mot de passe avant le hachage
- Le résultat est un hash unique, même pour le même mot de passe
- Exemple : `"MonMotDePasse123!"` → `"$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5K5K5K5K5K5K5K"`

**Stockage dans la base de données :**

Dans le modèle `Utilisateur` (`models_auth.py`) :
```python
mot_de_passe_hash = Column(String(255), nullable=False)  # Hashé avec bcrypt
```

Le mot de passe original n'est **jamais stocké**, seulement le hash.

### 1.2 Vérification d'un Mot de Passe

Quand un utilisateur se connecte, on compare le mot de passe saisi avec le hash stocké :

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)
```

**Explication :**
- `bcrypt.checkpw()` prend le mot de passe en clair et le hash stocké
- Bcrypt extrait automatiquement le sel du hash
- Il re-hache le mot de passe avec ce sel et compare
- Retourne `True` si les deux correspondent, `False` sinon

**Pourquoi c'est sécurisé :**
- Même si quelqu'un vole la base de données, il ne peut pas retrouver le mot de passe original
- Le hash est unidirectionnel : impossible de "décrypter" le hash pour obtenir le mot de passe
- Chaque hash est unique grâce au sel aléatoire

## 2. Système de Réinitialisation de Mot de Passe

### 2.1 Stockage du Code de Réinitialisation

Dans le modèle `Utilisateur`, deux colonnes sont utilisées pour la réinitialisation :

```python
code_reset_mdp = Column(String(10))  # Code de réinitialisation (ex: "A3B7C9D2")
code_reset_mdp_expiration = Column(DateTime)  # Date d'expiration du code
```

**Ces codes sont stockés en clair** (pas hachés) car :
- Ils sont temporaires (expirent après 15 minutes)
- Ils sont envoyés par email
- Ils sont à usage unique (supprimés après utilisation)

### 2.2 Génération du Code

**Code dans `auth_service.py` :**

```python
def generate_reset_code(length: int = 8) -> str:
    characters = string.ascii_uppercase + string.digits  # A-Z et 0-9
    code = ''.join(secrets.choice(characters) for _ in range(length))
    return code
```

**Explication :**
- Utilise `secrets.choice()` (cryptographiquement sécurisé) au lieu de `random`
- Génère un code aléatoire de 8 caractères (ex: `"A3B7C9D2"`)
- Le code est alphanumérique en majuscules

### 2.3 Processus de Réinitialisation

#### Étape 1 : Demande de Réinitialisation (`/api/auth/forgot-password`)

```python
@router.post("/forgot-password")
async def forgot_password(data: PasswordResetRequest, db: Session = Depends(get_auth_db)):
    # 1. Chercher l'utilisateur par email
    user = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
    
    if not user:
        # Sécurité : ne pas révéler si l'email existe
        return {"success": True, "message": "Si cet email existe, un code a été envoyé"}
    
    # 2. Générer un code de réinitialisation
    reset_code = auth_service.generate_reset_code()  # Ex: "A3B7C9D2"
    code_expiration = auth_service.get_code_expiration(15)  # Expire dans 15 minutes
    
    # 3. Stocker le code dans la base de données
    user.code_reset_mdp = reset_code
    user.code_reset_mdp_expiration = code_expiration
    
    db.commit()  # Sauvegarder dans la base
    
    # 4. Envoyer l'email avec le code
    email_service.send_password_reset_email(
        user.email,
        user.nom,
        user.prenom,
        reset_code
    )
    
    return {"success": True, "message": "Code envoyé"}
```

**Ce qui se passe :**
1. L'utilisateur entre son email
2. Le backend génère un code aléatoire (ex: `"A3B7C9D2"`)
3. Le code est stocké dans `user.code_reset_mdp` avec une date d'expiration (15 minutes)
4. Le code est envoyé par email à l'utilisateur
5. Le code est sauvegardé dans la base de données SQLite (`auth.db`)

**Dans la base de données :**
```
Table: utilisateurs
- email: "user@example.com"
- code_reset_mdp: "A3B7C9D2"
- code_reset_mdp_expiration: "2025-01-15 14:30:00"
```

#### Étape 2 : Vérification et Réinitialisation (`/api/auth/reset-password`)

```python
@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_auth_db)):
    # 1. Chercher l'utilisateur
    user = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # 2. Vérifier le code
    if not user.code_reset_mdp or user.code_reset_mdp != data.code:
        raise HTTPException(status_code=400, detail="Code incorrect")
    
    # 3. Vérifier l'expiration
    if auth_service.is_code_expired(user.code_reset_mdp_expiration):
        raise HTTPException(status_code=400, detail="Code expiré")
    
    # 4. Valider le nouveau mot de passe (force, longueur, etc.)
    is_valid, error_msg = auth_service.is_strong_password(data.nouveau_mot_de_passe)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 5. Hacher le nouveau mot de passe
    user.mot_de_passe_hash = auth_service.hash_password(data.nouveau_mot_de_passe)
    
    # 6. Supprimer le code (usage unique)
    user.code_reset_mdp = None
    user.code_reset_mdp_expiration = None
    
    db.commit()  # Sauvegarder les changements
    
    return {"success": True, "message": "Mot de passe réinitialisé"}
```

**Ce qui se passe :**
1. L'utilisateur envoie son email, le code reçu, et son nouveau mot de passe
2. Le backend vérifie que le code correspond à celui stocké dans la base
3. Le backend vérifie que le code n'a pas expiré (moins de 15 minutes)
4. Le backend valide que le nouveau mot de passe est assez fort
5. Le nouveau mot de passe est haché avec bcrypt
6. Le hash est stocké dans `user.mot_de_passe_hash`
7. Le code de réinitialisation est supprimé (usage unique)

**Dans la base de données après réinitialisation :**
```
Table: utilisateurs
- email: "user@example.com"
- mot_de_passe_hash: "$2b$12$NouveauHashBcrypt..."  ← Nouveau hash
- code_reset_mdp: NULL  ← Code supprimé
- code_reset_mdp_expiration: NULL  ← Expiration supprimée
```

## 3. Sécurité

### 3.1 Pourquoi le Code n'est pas Haché ?

Le code de réinitialisation est stocké **en clair** dans la base de données, contrairement au mot de passe. Pourquoi ?

**Raisons :**
1. **Temporaire** : Le code expire après 15 minutes
2. **Usage unique** : Il est supprimé après utilisation
3. **Comparaison nécessaire** : On doit comparer le code reçu avec celui stocké
4. **Complexité** : Un code de 8 caractères aléatoires est déjà très difficile à deviner (36^8 = 2.8 billions de possibilités)

**Si on hashait le code :**
- On ne pourrait pas le comparer directement
- Il faudrait re-hacher chaque tentative, ce qui est moins efficace
- Le gain de sécurité serait minime car le code est déjà temporaire et unique

### 3.2 Validation du Mot de Passe

Le backend valide que le nouveau mot de passe est assez fort :

```python
def is_strong_password(password: str) -> tuple[bool, str]:
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
```

**Critères de validation :**
- Minimum 8 caractères
- Au moins une majuscule
- Au moins une minuscule
- Au moins un chiffre
- Au moins un caractère spécial

## 4. Flux Complet

```
1. Utilisateur clique "Mot de passe oublié ?"
   ↓
2. Frontend → POST /api/auth/forgot-password {email: "user@example.com"}
   ↓
3. Backend :
   - Génère code: "A3B7C9D2"
   - Stocke dans DB: code_reset_mdp = "A3B7C9D2", expiration = maintenant + 15min
   - Envoie email avec le code
   ↓
4. Utilisateur reçoit email avec code "A3B7C9D2"
   ↓
5. Frontend → POST /api/auth/reset-password {
     email: "user@example.com",
     code: "A3B7C9D2",
     nouveau_mot_de_passe: "NouveauMDP123!"
   }
   ↓
6. Backend :
   - Vérifie code == "A3B7C9D2" ✓
   - Vérifie expiration > maintenant ✓
   - Valide force du mot de passe ✓
   - Hache nouveau mot de passe avec bcrypt
   - Stocke hash dans mot_de_passe_hash
   - Supprime code_reset_mdp et expiration
   ↓
7. Utilisateur peut maintenant se connecter avec son nouveau mot de passe
```

## 5. Base de Données

Tout est stocké dans la base de données SQLite `auth.db` :

**Table `utilisateurs` :**
- `email` : Email de l'utilisateur (unique)
- `mot_de_passe_hash` : Hash bcrypt du mot de passe (jamais en clair)
- `code_reset_mdp` : Code de réinitialisation temporaire (en clair, nullable)
- `code_reset_mdp_expiration` : Date d'expiration du code (nullable)

**Exemple de données :**
```
email: "sacha.heroux87@gmail.com"
mot_de_passe_hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5K5K5K5K5K5K"
code_reset_mdp: NULL  (ou "A3B7C9D2" si réinitialisation en cours)
code_reset_mdp_expiration: NULL  (ou "2025-01-15 14:30:00" si réinitialisation en cours)
```

## Conclusion

- **Mots de passe** : Toujours hachés avec bcrypt, jamais en clair
- **Codes de réinitialisation** : Stockés en clair mais temporaires (15 min) et à usage unique
- **Sécurité** : Validation de force, expiration, usage unique
- **Base de données** : Tout est stocké dans `auth.db` (SQLite séparé de la base principale)

