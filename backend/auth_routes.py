#!/usr/bin/env python3
"""
Routes d'authentification pour Interface CAH
Inscription, connexion, validation, récupération mot de passe
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

# Services
import auth_service
import email_service
from models_auth import Compagnie, Utilisateur, DemandeAcces
from auth_database_service import get_auth_db, get_company_database_path

# Router
router = APIRouter(tags=["Authentication"])

# ==========================================
# MODÈLES PYDANTIC (Validation des données)
# ==========================================

class RegisterRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str
    nom: str
    prenom: str
    date_naissance: Optional[date] = None
    sexe: Optional[str] = None
    telephone: Optional[str] = None
    poste: Optional[str] = None

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str

class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str

class CompanySetupRequest(BaseModel):
    action: str = Field(..., description="'create' ou 'join'")
    # Pour créer une compagnie
    nom_compagnie: Optional[str] = None
    email_compagnie: Optional[str] = None
    telephone_compagnie: Optional[str] = None
    adresse_compagnie: Optional[str] = None
    site_web: Optional[str] = None
    numero_entreprise: Optional[str] = None
    # Pour rejoindre une compagnie
    id_compagnie: Optional[int] = None
    code_acces: Optional[str] = None  # Code d'accès de la compagnie
    role: str = Field(default="employe", description="'admin' ou 'employe'")

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    nouveau_mot_de_passe: str

class ApprovalAction(BaseModel):
    id_demande: int
    action: str = Field(..., description="'approve' ou 'reject'")
    commentaire_refus: Optional[str] = None

# ==========================================
# DÉPENDANCES
# ==========================================
# Note: get_auth_db est maintenant importé de auth_database_service

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_auth_db)) -> Utilisateur:
    """
    Middleware pour obtenir l'utilisateur connecté à partir du token JWT
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant ou invalide")
    
    token = authorization.replace("Bearer ", "")
    payload = auth_service.decode_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Token expiré ou invalide")
    
    # Le token contient 'sub' (email) ou 'user_id'
    user_id = payload.get("user_id")
    email = payload.get("sub")
    
    if not user_id and not email:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    # Chercher l'utilisateur par ID ou par email
    if user_id:
        user = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == user_id).first()
    else:
        user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Vérifier le statut (sauf pour les utilisateurs en attente qui peuvent rejoindre une compagnie)
    if user.statut not in ["actif", "en_attente"]:
        if user.statut == "refuse":
            raise HTTPException(status_code=403, detail="Votre demande d'accès a été refusée")
        elif user.statut == "inactif":
            raise HTTPException(status_code=403, detail="Votre compte est inactif")
        else:
            raise HTTPException(status_code=403, detail="Compte non actif")
    
    return user

def require_admin(current_user: Utilisateur = Depends(get_current_user)) -> Utilisateur:
    """Vérifier que l'utilisateur est admin"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return current_user

# ==========================================
# ENDPOINTS D'INSCRIPTION
# ==========================================

@router.post("/register")
async def register(data: RegisterRequest, db: Session = Depends(get_auth_db)):
    """
    Étape 1 : Inscription d'un nouvel utilisateur
    - Crée le compte utilisateur (en attente)
    - Envoie un code de vérification par email
    """
    try:
        # Vérifier si l'email existe déjà
        existing_user = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
        
        if existing_user:
            # Si l'utilisateur existe et est vérifié, refuser
            if existing_user.email_verifie:
                raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
            
            # Si l'utilisateur existe mais n'est pas vérifié, le supprimer pour permettre une nouvelle inscription
            db.delete(existing_user)
            db.commit()
        
        # Valider le mot de passe
        is_valid, error_msg = auth_service.is_strong_password(data.mot_de_passe)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Hasher le mot de passe
        hashed_password = auth_service.hash_password(data.mot_de_passe)
        
        # Générer un code de vérification
        verification_code = auth_service.generate_verification_code()
        code_expiration = auth_service.get_code_expiration(15)  # 15 minutes
        
        # Calculer l'âge si date de naissance fournie
        age = None
        if data.date_naissance:
            age = auth_service.calculate_age(datetime.combine(data.date_naissance, datetime.min.time()))
        
        # Créer l'utilisateur (sans compagnie pour l'instant)
        new_user = Utilisateur(
            id_compagnie=0,  # Temporaire, sera mis à jour après setup compagnie
            email=data.email,
            mot_de_passe_hash=hashed_password,
            nom=data.nom,
            prenom=data.prenom,
            date_naissance=data.date_naissance,
            age=age,
            sexe=data.sexe,
            telephone=data.telephone,
            poste=data.poste,
            role="employe",  # Par défaut, sera changé si crée une compagnie
            statut="en_attente",
            email_verifie=False,
            code_verification_email=verification_code,
            code_verification_expiration=code_expiration
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Envoyer l'email de vérification
        email_service.send_verification_email(
            data.email,
            data.nom,
            data.prenom,
            verification_code
        )
        
        return {
            "success": True,
            "message": "Inscription réussie. Veuillez vérifier votre email.",
            "user_id": new_user.id_utilisateur,
            "email": new_user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur inscription: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'inscription: {str(e)}")

@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_auth_db)):
    """
    Étape 2 : Vérifier l'email avec le code reçu
    """
    try:
        user = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        if user.email_verifie:
            raise HTTPException(status_code=400, detail="Email déjà vérifié")
        
        # Vérifier le code
        if user.code_verification_email != data.code:
            raise HTTPException(status_code=400, detail="Code de vérification incorrect")
        
        # Vérifier l'expiration
        if auth_service.is_code_expired(user.code_verification_expiration):
            raise HTTPException(status_code=400, detail="Code de vérification expiré")
        
        # Marquer l'email comme vérifié
        user.email_verifie = True
        user.code_verification_email = None
        user.code_verification_expiration = None
        
        db.commit()
        
        # Générer un token pour l'utilisateur vérifié
        access_token = auth_service.create_access_token(data={"sub": user.email})
        
        return {
            "success": True,
            "message": "Email vérifié avec succès",
            "access_token": access_token,
            "user": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur vérification email: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification: {str(e)}")

@router.post("/resend-verification")
async def resend_verification(email: EmailStr, db: Session = Depends(get_auth_db)):
    """
    Renvoyer un code de vérification
    """
    try:
        user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        if user.email_verifie:
            raise HTTPException(status_code=400, detail="Email déjà vérifié")
        
        # Générer un nouveau code
        verification_code = auth_service.generate_verification_code()
        code_expiration = auth_service.get_code_expiration(15)
        
        user.code_verification_email = verification_code
        user.code_verification_expiration = code_expiration
        
        db.commit()
        
        # Renvoyer l'email
        email_service.send_verification_email(
            user.email,
            user.nom,
            user.prenom,
            verification_code
        )
        
        return {
            "success": True,
            "message": "Code de vérification renvoyé"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur renvoi code: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du renvoi du code")

# ==========================================
# ENDPOINTS DE CONNEXION
# ==========================================

@router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_auth_db)):
    """
    Connexion d'un utilisateur
    Retourne un token JWT
    """
    try:
        # Trouver l'utilisateur
        user = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
        
        # Vérifier le mot de passe
        if not auth_service.verify_password(data.mot_de_passe, user.mot_de_passe_hash):
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
        
        # Vérifier que l'email est vérifié
        if not user.email_verifie:
            raise HTTPException(status_code=403, detail="Veuillez d'abord vérifier votre email")
        
        # Vérifier que l'utilisateur a une compagnie
        if user.id_compagnie == 0:
            raise HTTPException(status_code=403, detail="Veuillez d'abord configurer votre compagnie")
        
        # Vérifier le statut
        if user.statut == "en_attente":
            raise HTTPException(status_code=403, detail="Votre demande d'accès est en attente d'approbation")
        
        if user.statut == "refuse":
            raise HTTPException(status_code=403, detail="Votre demande d'accès a été refusée")
        
        if user.statut == "inactif":
            raise HTTPException(status_code=403, detail="Votre compte est inactif")
        
        # Mettre à jour la dernière connexion
        user.derniere_connexion = datetime.utcnow()
        db.commit()
        
        # Créer le token JWT
        token_data = {
            "user_id": user.id_utilisateur,
            "company_id": user.id_compagnie,
            "role": user.role,
            "is_admin_principal": user.est_admin_principal,
            "schema_name": user.compagnie.schema_name if user.compagnie else None
        }
        
        token = auth_service.create_access_token(token_data)
        
        return {
            "success": True,
            "token": token,
            "user": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la connexion")

@router.get("/me")
async def get_current_user_info(current_user: Utilisateur = Depends(get_current_user)):
    """
    Obtenir les informations de l'utilisateur connecté
    """
    return {
        "success": True,
        "user": current_user.to_dict()
    }

@router.post("/logout")
async def logout():
    """
    Déconnexion (côté client supprime le token)
    """
    return {
        "success": True,
        "message": "Déconnexion réussie"
    }

# ==========================================
# ENDPOINTS SETUP COMPAGNIE
# ==========================================

@router.post("/setup-company")
async def setup_company(
    data: CompanySetupRequest, 
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    """
    Étape 3 : Créer ou rejoindre une compagnie
    """
    try:
        if data.action == "create":
            # Créer une nouvelle compagnie
            if not data.nom_compagnie:
                raise HTTPException(status_code=400, detail="Le nom de la compagnie est requis")
            
            # Vérifier que le nom n'existe pas
            existing = db.query(Compagnie).filter(Compagnie.nom_compagnie == data.nom_compagnie).first()
            if existing:
                raise HTTPException(status_code=400, detail="Ce nom de compagnie existe déjà")
            
            # Générer un nom de schéma unique
            schema_name = auth_service.sanitize_schema_name(data.nom_compagnie)
            
            # Créer la compagnie
            new_company = Compagnie(
                nom_compagnie=data.nom_compagnie,
                email_compagnie=data.email_compagnie or current_user.email,
                telephone_compagnie=data.telephone_compagnie,
                adresse_compagnie=data.adresse_compagnie,
                site_web=data.site_web,
                numero_entreprise=data.numero_entreprise,
                schema_name=schema_name
            )
            
            db.add(new_company)
            db.flush()  # Pour obtenir l'ID
            
            # Mettre à jour l'utilisateur
            current_user.id_compagnie = new_company.id_compagnie
            current_user.role = "admin"
            current_user.est_admin_principal = True
            current_user.statut = "actif"  # Approuvé automatiquement car créateur
            
            db.commit()
            db.refresh(new_company)
            
            # TODO: Créer le schéma PostgreSQL et les tables
            # Cette partie sera dans le service multi-tenant
            
            # Envoyer email de bienvenue
            email_service.send_welcome_email(
                current_user.email,
                current_user.nom,
                current_user.prenom,
                new_company.nom_compagnie,
                True
            )
            
            return {
                "success": True,
                "message": "Compagnie créée avec succès",
                "company": new_company.to_dict(),
                "user": current_user.to_dict()
            }
            
        elif data.action == "join":
            # Rejoindre une compagnie existante avec code d'accès
            if not data.code_acces:
                raise HTTPException(status_code=400, detail="Le code d'accès est requis")
            
            company = db.query(Compagnie).filter(Compagnie.code_acces == data.code_acces).first()
            if not company:
                raise HTTPException(status_code=404, detail="Code d'accès invalide")
            
            # Mettre à jour l'utilisateur
            current_user.id_compagnie = company.id_compagnie
            current_user.role = data.role
            current_user.statut = "en_attente"  # En attente d'approbation
            
            # Créer une demande d'accès
            demande = DemandeAcces(
                id_compagnie=company.id_compagnie,
                id_utilisateur=current_user.id_utilisateur,
                statut="en_attente"
            )
            
            db.add(demande)
            db.commit()
            db.refresh(demande)
            
            # Notifier les admins principaux
            admins = db.query(Utilisateur).filter(
                Utilisateur.id_compagnie == company.id_compagnie,
                Utilisateur.est_admin_principal == True,
                Utilisateur.statut == "actif"
            ).all()
            
            user_info = {
                "nom": current_user.nom,
                "prenom": current_user.prenom,
                "email": current_user.email,
                "telephone": current_user.telephone,
                "poste": current_user.poste,
                "role": current_user.role
            }
            
            for admin in admins:
                email_service.send_access_request_notification(
                    admin.email,
                    admin.nom,
                    user_info,
                    company.nom_compagnie,
                    demande.id_demande
                )
            
            return {
                "success": True,
                "message": "Demande d'accès envoyée. En attente d'approbation.",
                "company": company.to_dict(),
                "demande_id": demande.id_demande
            }
        
        else:
            raise HTTPException(status_code=400, detail="Action invalide (create ou join)")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur setup compagnie: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/companies")
async def list_companies(db: Session = Depends(get_auth_db)):
    """
    Lister toutes les compagnies disponibles (pour rejoindre)
    """
    try:
        companies = db.query(Compagnie).all()
        return {
            "success": True,
            "companies": [c.to_dict() for c in companies]
        }
    except Exception as e:
        print(f"❌ Erreur liste compagnies: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement des compagnies")

# ==========================================
# ENDPOINTS RÉCUPÉRATION MOT DE PASSE
# ==========================================

@router.post("/forgot-password")
async def forgot_password(data: PasswordResetRequest, db: Session = Depends(get_auth_db)):
    """
    Demander un code de réinitialisation de mot de passe
    """
    try:
        user = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
        
        if not user:
            # Ne pas révéler que l'email n'existe pas (sécurité)
            return {
                "success": True,
                "message": "Si cet email existe, un code de réinitialisation a été envoyé"
            }
        
        # Générer un code de reset
        reset_code = auth_service.generate_reset_code()
        code_expiration = auth_service.get_code_expiration(15)  # 15 minutes
        
        user.code_reset_mdp = reset_code
        user.code_reset_mdp_expiration = code_expiration
        
        db.commit()
        
        # Envoyer l'email
        email_service.send_password_reset_email(
            user.email,
            user.nom,
            user.prenom,
            reset_code
        )
        
        return {
            "success": True,
            "message": "Un code de réinitialisation a été envoyé à votre email"
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur forgot password: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi du code")

@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_auth_db)):
    """
    Réinitialiser le mot de passe avec le code reçu
    """
    try:
        user = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Vérifier le code
        if not user.code_reset_mdp or user.code_reset_mdp != data.code:
            raise HTTPException(status_code=400, detail="Code de réinitialisation incorrect")
        
        # Vérifier l'expiration
        if auth_service.is_code_expired(user.code_reset_mdp_expiration):
            raise HTTPException(status_code=400, detail="Code de réinitialisation expiré")
        
        # Valider le nouveau mot de passe
        is_valid, error_msg = auth_service.is_strong_password(data.nouveau_mot_de_passe)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Mettre à jour le mot de passe
        user.mot_de_passe_hash = auth_service.hash_password(data.nouveau_mot_de_passe)
        user.code_reset_mdp = None
        user.code_reset_mdp_expiration = None
        
        db.commit()
        
        return {
            "success": True,
            "message": "Mot de passe réinitialisé avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur reset password: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la réinitialisation")

# ==========================================
# ENDPOINTS GESTION DES DEMANDES (ADMINS)
# ==========================================

@router.get("/pending-requests")
async def get_pending_requests(
    current_user: Utilisateur = Depends(require_admin),
    db: Session = Depends(get_auth_db)
):
    """
    Obtenir les demandes d'accès en attente pour la compagnie de l'admin
    """
    try:
        demandes = db.query(DemandeAcces).filter(
            DemandeAcces.id_compagnie == current_user.id_compagnie,
            DemandeAcces.statut == "en_attente"
        ).all()
        
        return {
            "success": True,
            "demandes": [d.to_dict() for d in demandes]
        }
        
    except Exception as e:
        print(f"❌ Erreur récupération demandes: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement des demandes")

@router.post("/approve-request")
async def approve_request(
    data: ApprovalAction,
    current_user: Utilisateur = Depends(require_admin),
    db: Session = Depends(get_auth_db)
):
    """
    Approuver ou refuser une demande d'accès
    """
    try:
        demande = db.query(DemandeAcces).filter(DemandeAcces.id_demande == data.id_demande).first()
        
        if not demande:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        # Vérifier que c'est pour la compagnie de l'admin
        if demande.id_compagnie != current_user.id_compagnie:
            raise HTTPException(status_code=403, detail="Vous ne pouvez pas traiter cette demande")
        
        user = demande.utilisateur
        
        if data.action == "approve":
            # Approuver
            demande.statut = "approuve"
            demande.traite_par = current_user.id_utilisateur
            demande.date_traitement = datetime.utcnow()
            
            user.statut = "actif"
            
            db.commit()
            
            # Envoyer email de confirmation
            email_service.send_approval_notification(
                user.email,
                user.nom,
                user.prenom,
                demande.compagnie.nom_compagnie
            )
            
            return {
                "success": True,
                "message": f"Demande de {user.prenom} {user.nom} approuvée"
            }
            
        elif data.action == "reject":
            # Refuser
            demande.statut = "refuse"
            demande.traite_par = current_user.id_utilisateur
            demande.date_traitement = datetime.utcnow()
            demande.commentaire_refus = data.commentaire_refus
            
            user.statut = "refuse"
            
            db.commit()
            
            # Envoyer email de refus
            email_service.send_rejection_notification(
                user.email,
                user.nom,
                user.prenom,
                demande.compagnie.nom_compagnie,
                data.commentaire_refus
            )
            
            return {
                "success": True,
                "message": f"Demande de {user.prenom} {user.nom} refusée"
            }
        
        else:
            raise HTTPException(status_code=400, detail="Action invalide (approve ou reject)")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur traitement demande: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/approve-request-email")
async def approve_request_from_email(request_id: int, action: str):
    """
    Approuver ou refuser une demande via lien email
    Redirige vers une page de confirmation
    """
    from fastapi.responses import HTMLResponse
    
    try:
        # Récupérer la demande
        # TODO: Implémenter avec la vraie DB
        # Pour l'instant, retourner une page HTML simple
        
        if action == "approve":
            # TODO: Approuver la demande
            html_content = """
            <html>
                <head>
                    <title>Demande approuvée</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
                        .container {{ background: white; color: #333; padding: 40px; border-radius: 10px; max-width: 500px; margin: 0 auto; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }}
                        h1 {{ color: #10B981; }}
                        .icon {{ font-size: 64px; margin-bottom: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">✓</div>
                        <h1>Demande approuvée !</h1>
                        <p>L'utilisateur a été notifié par email et peut maintenant se connecter.</p>
                        <p style="margin-top: 30px; color: #666; font-size: 14px;">Vous pouvez fermer cette page.</p>
                    </div>
                </body>
            </html>
            """
        elif action == "reject":
            # TODO: Refuser la demande
            html_content = """
            <html>
                <head>
                    <title>Demande refusée</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
                        .container {{ background: white; color: #333; padding: 40px; border-radius: 10px; max-width: 500px; margin: 0 auto; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }}
                        h1 {{ color: #EF4444; }}
                        .icon {{ font-size: 64px; margin-bottom: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">✗</div>
                        <h1>Demande refusée</h1>
                        <p>L'utilisateur a été notifié par email.</p>
                        <p style="margin-top: 30px; color: #666; font-size: 14px;">Vous pouvez fermer cette page.</p>
                    </div>
                </body>
            </html>
            """
        else:
            html_content = """
            <html>
                <head>
                    <title>Erreur</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f3f4f6; }}
                        .container {{ background: white; padding: 40px; border-radius: 10px; max-width: 500px; margin: 0 auto; }}
                        h1 {{ color: #EF4444; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Action invalide</h1>
                        <p>L'action demandée n'est pas reconnue.</p>
                    </div>
                </body>
            </html>
            """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        print(f"❌ Erreur approbation email: {e}")
        html_content = f"""
        <html>
            <head>
                <title>Erreur</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f3f4f6; }}
                    .container {{ background: white; padding: 40px; border-radius: 10px; max-width: 500px; margin: 0 auto; }}
                    h1 {{ color: #EF4444; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Erreur</h1>
                    <p>Une erreur est survenue: {str(e)}</p>
                </div>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=500)

# ==========================================
# ENDPOINT DE DIAGNOSTIC (TEMPORAIRE)
# ==========================================

@router.get("/debug/users")
async def debug_users(db: Session = Depends(get_auth_db)):
    """
    TEMPORAIRE: Voir les utilisateurs dans la DB auth
    """
    try:
        users = db.query(Utilisateur).all()
        return {
            "total_users": len(users),
            "users": [
                {
                    "id": u.id_utilisateur,
                    "email": u.email,
                    "nom": u.nom,
                    "prenom": u.prenom,
                    "role": u.role,
                    "statut": u.statut,
                    "email_verifie": u.email_verifie,
                    "est_admin_principal": u.est_admin_principal,
                    "id_compagnie": u.id_compagnie
                }
                for u in users
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/me")
async def get_current_user_info(current_user: Utilisateur = Depends(get_current_user)):
    """
    Obtenir les informations de l'utilisateur connecté
    """
    return {
        "success": True,
        "user": current_user.to_dict()
    }

@router.get("/approve-request-email")
async def approve_request_email(request_id: int, db: Session = Depends(get_auth_db)):
    """
    Endpoint pour approuver une demande d'accès via email
    """
    from fastapi.responses import HTMLResponse
    
    try:
        from models_auth import DemandeAcces, Utilisateur
        
        # Trouver la demande
        demande = db.query(DemandeAcces).filter(DemandeAcces.id_demande == request_id).first()
        
        if not demande:
            html_content = """
            <html>
                <head>
                    <title>Erreur</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: red; font-size: 24px; }
                    </style>
                </head>
                <body>
                    <h1 class="error">❌ Demande non trouvée</h1>
                    <p>Cette demande d'accès n'existe pas ou a déjà été traitée.</p>
                </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        # Trouver l'utilisateur
        user = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == demande.id_utilisateur).first()
        
        if not user:
            html_content = """
            <html>
                <head>
                    <title>Erreur</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: red; font-size: 24px; }
                    </style>
                </head>
                <body>
                    <h1 class="error">❌ Utilisateur non trouvé</h1>
                    <p>L'utilisateur associé à cette demande n'existe pas.</p>
                </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        # Approuver la demande
        demande.statut = "approuve"
        user.statut = "actif"
        
        db.commit()
        
        # Envoyer email de confirmation
        try:
            email_service.send_approval_notification(
                user.email,
                user.nom,
                user.prenom,
                "CAH Immobilier"
            )
            email_sent = True
        except Exception as e:
            email_sent = False
            print(f"Erreur envoi email: {e}")
        
        html_content = f"""
        <html>
            <head>
                <title>Demande approuvée</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .success {{ color: green; font-size: 24px; }}
                    .info {{ color: #666; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <h1 class="success">✅ Demande approuvée !</h1>
                <p>L'utilisateur <strong>{user.prenom} {user.nom}</strong> peut maintenant se connecter.</p>
                <p class="info">Email de confirmation: {'Envoyé' if email_sent else 'Erreur lors de l envoi'}</p>
                <p><a href="https://interface-cah.vercel.app/login">Se connecter à Interface CAH</a></p>
            </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        db.rollback()
        html_content = f"""
        <html>
            <head>
                <title>Erreur</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: red; font-size: 24px; }}
                </style>
            </head>
            <body>
                <h1 class="error">❌ Erreur</h1>
                <p>Une erreur s'est produite: {str(e)}</p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@router.get("/reject-request-email")
async def reject_request_email(request_id: int, db: Session = Depends(get_auth_db)):
    """
    Endpoint pour refuser une demande d'accès via email
    """
    from fastapi.responses import HTMLResponse
    
    try:
        from models_auth import DemandeAcces, Utilisateur
        
        # Trouver la demande
        demande = db.query(DemandeAcces).filter(DemandeAcces.id_demande == request_id).first()
        
        if not demande:
            html_content = """
            <html>
                <head>
                    <title>Erreur</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: red; font-size: 24px; }
                    </style>
                </head>
                <body>
                    <h1 class="error">❌ Demande non trouvée</h1>
                    <p>Cette demande d'accès n'existe pas ou a déjà été traitée.</p>
                </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        # Trouver l'utilisateur
        user = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == demande.id_utilisateur).first()
        
        if not user:
            html_content = """
            <html>
                <head>
                    <title>Erreur</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: red; font-size: 24px; }
                    </style>
                </head>
                <body>
                    <h1 class="error">❌ Utilisateur non trouvé</h1>
                    <p>L'utilisateur associé à cette demande n'existe pas.</p>
                </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        # Refuser la demande
        demande.statut = "refuse"
        user.statut = "refuse"
        
        db.commit()
        
        html_content = f"""
        <html>
            <head>
                <title>Demande refusée</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: red; font-size: 24px; }}
                </style>
            </head>
            <body>
                <h1 class="error">❌ Demande refusée</h1>
                <p>L'utilisateur <strong>{user.prenom} {user.nom}</strong> ne peut pas accéder au système.</p>
            </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        db.rollback()
        html_content = f"""
        <html>
            <head>
                <title>Erreur</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: red; font-size: 24px; }}
                </style>
            </head>
            <body>
                <h1 class="error">❌ Erreur</h1>
                <p>Une erreur s'est produite: {str(e)}</p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@router.post("/debug/approve-user-by-email")
async def approve_user_by_email(data: dict, db: Session = Depends(get_auth_db)):
    """
    TEMPORAIRE: Approuver un utilisateur par email
    """
    try:
        from models_auth import Utilisateur, DemandeAcces
        
        email = data.get("email")
        if not email:
            return {"error": "Email requis"}
        
        # Trouver l'utilisateur
        user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
        
        if not user:
            return {"error": f"Utilisateur {email} non trouvé"}
        
        # Trouver la demande d'accès
        demande = db.query(DemandeAcces).filter(DemandeAcces.id_utilisateur == user.id_utilisateur).first()
        
        if not demande:
            return {"error": f"Aucune demande d'accès trouvée pour {email}"}
        
        # Approuver la demande
        demande.statut = "approuve"
        user.statut = "actif"
        
        db.commit()
        
        # Envoyer email de confirmation
        try:
            email_service.send_approval_notification(
                user.email,
                user.nom,
                user.prenom,
                "CAH Immobilier"
            )
            email_sent = True
        except Exception as e:
            email_sent = False
            print(f"Erreur envoi email: {e}")
        
        return {
            "success": True,
            "message": f"Utilisateur {email} approuvé avec succès",
            "email_sent": email_sent,
            "user": user.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@router.get("/debug/env-check")
async def check_env():
    """
    TEMPORAIRE: Vérifier les variables d'environnement SMTP
    """
    import os
    return {
        "SMTP_SERVER": os.getenv("SMTP_SERVER"),
        "SMTP_PORT": os.getenv("SMTP_PORT"),
        "SMTP_USERNAME": os.getenv("SMTP_USERNAME"),
        "SMTP_PASSWORD": "***" if os.getenv("SMTP_PASSWORD") else None,
        "FROM_EMAIL": os.getenv("FROM_EMAIL"),
        "FROM_NAME": os.getenv("FROM_NAME")
    }

@router.post("/debug/send-test-email")
async def send_test_email(data: dict):
    """
    TEMPORAIRE: Envoyer un email de test
    """
    try:
        email = data.get("email")
        if not email:
            return {"error": "Email requis"}
        
        # Générer un code de test
        import auth_service
        test_code = auth_service.generate_verification_code()
        
        # Envoyer l'email
        email_service.send_verification_email(email, "Test", "User", test_code)
        
        return {
            "success": True,
            "message": f"Email de test envoyé à {email}",
            "test_code": test_code
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/debug/cleanup-pending-users")
async def cleanup_pending_users(db: Session = Depends(get_auth_db)):
    """
    TEMPORAIRE: Nettoyer les utilisateurs en attente (sauf Sacha)
    """
    try:
        from models_auth import Utilisateur
        
        # Trouver tous les utilisateurs en attente
        pending_users = db.query(Utilisateur).filter(
            Utilisateur.statut == "en_attente"
        ).all()
        
        deleted_count = 0
        deleted_emails = []
        
        for user in pending_users:
            # Ne pas supprimer Sacha
            if user.email != "sacha.heroux87@gmail.com":
                deleted_emails.append(user.email)
                db.delete(user)
                deleted_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Supprimé {deleted_count} utilisateurs en attente",
            "deleted_emails": deleted_emails
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@router.post("/debug/cleanup-all-users")
async def cleanup_all_users(db: Session = Depends(get_auth_db)):
    """
    TEMPORAIRE: Supprimer TOUS les utilisateurs (sauf Sacha)
    """
    try:
        from models_auth import Utilisateur
        
        # Trouver tous les utilisateurs
        all_users = db.query(Utilisateur).all()
        
        deleted_count = 0
        deleted_emails = []
        
        for user in all_users:
            # Ne pas supprimer Sacha
            if user.email != "sacha.heroux87@gmail.com":
                deleted_emails.append(user.email)
                db.delete(user)
                deleted_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Supprimé {deleted_count} utilisateurs",
            "deleted_emails": deleted_emails
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@router.post("/debug/delete-user-by-email")
async def delete_user_by_email(data: dict, db: Session = Depends(get_auth_db)):
    """
    TEMPORAIRE: Supprimer un utilisateur par email
    """
    try:
        from models_auth import Utilisateur
        
        email = data.get("email")
        if not email:
            return {"error": "Email requis"}
        
        # Trouver l'utilisateur
        user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
        
        if not user:
            return {"success": True, "message": f"Aucun utilisateur trouvé avec l'email {email}"}
        
        # Supprimer l'utilisateur
        db.delete(user)
        db.commit()
        
        return {
            "success": True,
            "message": f"Utilisateur {email} supprimé avec succès"
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@router.post("/debug/migrate-code-acces")
async def migrate_code_acces(db: Session = Depends(get_auth_db)):
    """
    TEMPORAIRE: Ajouter la colonne code_acces et générer un code pour CAH Immobilier
    """
    try:
        from sqlalchemy import text
        from auth_database_service import engine
        
        with engine.connect() as conn:
            # Vérifier si la colonne existe
            result = conn.execute(text("PRAGMA table_info(compagnies)"))
            columns = [row[1] for row in result]
            
            if 'code_acces' not in columns:
                # Ajouter la colonne
                conn.execute(text("ALTER TABLE compagnies ADD COLUMN code_acces VARCHAR(20)"))
                conn.commit()
        
        # Générer un code pour CAH Immobilier
        company = db.query(Compagnie).filter_by(nom_compagnie="CAH Immobilier").first()
        if company and not company.code_acces:
            code_acces = auth_service.generate_company_access_code()
            company.code_acces = code_acces
            db.commit()
            return {
                "success": True,
                "message": "Migration réussie",
                "code_acces": code_acces
            }
        elif company:
            return {
                "success": True,
                "message": "Code déjà existant",
                "code_acces": company.code_acces
            }
        else:
            return {"error": "Compagnie non trouvée"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/debug/create-sacha")
async def create_sacha(db: Session = Depends(get_auth_db)):
    """
    TEMPORAIRE: Créer l'utilisateur Sacha manuellement
    """
    try:
        # Vérifier si Sacha existe déjà
        existing = db.query(Utilisateur).filter_by(email="sacha.heroux87@gmail.com").first()
        if existing:
            # Mettre à jour son mot de passe avec le nouveau hash
            existing.mot_de_passe_hash = auth_service.hash_password("Champion2024!")
            existing.statut = "actif"
            existing.est_admin_principal = True
            existing.email_verifie = True
            db.commit()
            return {
                "message": "Sacha existe déjà - mot de passe mis à jour",
                "user_id": existing.id_utilisateur,
                "statut": existing.statut
            }
        
        # Trouver la compagnie CAH Immobilier
        company = db.query(Compagnie).filter_by(nom_compagnie="CAH Immobilier").first()
        if not company:
            return {"error": "Compagnie CAH Immobilier non trouvée"}
        
        # Créer Sacha
        sacha = Utilisateur(
            id_compagnie=company.id_compagnie,
            email="sacha.heroux87@gmail.com",
            mot_de_passe_hash=auth_service.hash_password("Champion2024!"),
            nom="Heroux",
            prenom="Sacha",
            role="admin",
            est_admin_principal=True,
            statut="actif",
            email_verifie=True,
            date_creation=datetime.utcnow()
        )
        
        db.add(sacha)
        db.commit()
        db.refresh(sacha)
        
        return {
            "success": True,
            "message": "Utilisateur Sacha créé avec succès",
            "user": {
                "id": sacha.id_utilisateur,
                "email": sacha.email,
                "role": sacha.role,
                "statut": sacha.statut
            }
        }
        
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

