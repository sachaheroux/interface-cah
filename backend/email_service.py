#!/usr/bin/env python3
"""
Service d'envoi d'emails pour Interface CAH
Templates professionnels en HTML
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

# Configuration SMTP (à configurer via variables d'environnement)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@interfacecah.com")
FROM_NAME = os.getenv("FROM_NAME", "Interface CAH")


# ==========================================
# TEMPLATES HTML
# ==========================================

def get_email_base_template(content: str) -> str:
    """Template de base pour tous les emails"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: 600;
                margin: 20px 0;
            }}
            .code-box {{
                background: #f8f9fa;
                border: 2px solid #667eea;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }}
            .code {{
                font-size: 32px;
                font-weight: bold;
                color: #667eea;
                letter-spacing: 5px;
                font-family: 'Courier New', monospace;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px 30px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
            .info-box {{
                background: #e8f4f8;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏢 Interface CAH</h1>
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                <p>© {datetime.now().year} Interface CAH - Gestion Immobilière Professionnelle</p>
                <p style="font-size: 12px; color: #999;">Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_verification_email_template(nom: str, prenom: str, code: str) -> str:
    """Template pour la vérification d'email"""
    content = f"""
        <h2>Bienvenue {prenom} {nom} ! 👋</h2>
        <p>Merci de vous être inscrit à Interface CAH. Pour activer votre compte, veuillez vérifier votre adresse email en utilisant le code ci-dessous :</p>
        
        <div class="code-box">
            <p style="margin: 0; color: #666; font-size: 14px;">Votre code de vérification :</p>
            <div class="code">{code}</div>
            <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">Ce code expire dans 15 minutes</p>
        </div>
        
        <p>Si vous n'avez pas créé de compte, vous pouvez ignorer cet email en toute sécurité.</p>
    """
    return get_email_base_template(content)


def get_access_request_email_template(admin_nom: str, user_info: dict, company_name: str, request_id: int) -> str:
    """Template pour notifier l'admin d'une nouvelle demande d'accès"""
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
    
    content = f"""
        <h2>Nouvelle demande d'accès 📬</h2>
        <p>Bonjour {admin_nom},</p>
        <p>Un nouvel utilisateur souhaite rejoindre votre compagnie <strong>{company_name}</strong> :</p>
        
        <div class="info-box">
            <p><strong>Nom complet:</strong> {user_info.get('prenom')} {user_info.get('nom')}</p>
            <p><strong>Email:</strong> {user_info.get('email')}</p>
            <p><strong>Téléphone:</strong> {user_info.get('telephone', 'Non fourni')}</p>
            <p><strong>Poste:</strong> {user_info.get('poste', 'Non spécifié')}</p>
            <p><strong>Rôle demandé:</strong> {user_info.get('role', 'employe').upper()}</p>
        </div>
        
        <p>Cliquez sur l'un des boutons ci-dessous pour traiter cette demande :</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{backend_url}/api/auth/approve-request-email?request_id={request_id}&action=approve" 
               class="button" 
               style="background-color: #10B981; margin-right: 10px;">
                ✓ Approuver
            </a>
            <a href="{backend_url}/api/auth/approve-request-email?request_id={request_id}&action=reject" 
               class="button" 
               style="background-color: #EF4444;">
                ✗ Refuser
            </a>
        </div>
    """
    return get_email_base_template(content)


def get_approval_email_template(nom: str, prenom: str, company_name: str) -> str:
    """Template pour notifier l'utilisateur que sa demande est approuvée"""
    content = f"""
        <h2>Demande approuvée ! 🎉</h2>
        <p>Félicitations {prenom} {nom},</p>
        <p>Votre demande d'accès à <strong>{company_name}</strong> a été approuvée !</p>
        
        <p>Vous pouvez maintenant vous connecter à votre compte et commencer à utiliser Interface CAH.</p>
        
        <a href="{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/login" class="button">
            Se connecter
        </a>
        
        <p>Si vous avez des questions, n'hésitez pas à contacter votre administrateur.</p>
    """
    return get_email_base_template(content)


def get_rejection_email_template(nom: str, prenom: str, company_name: str, reason: Optional[str] = None) -> str:
    """Template pour notifier l'utilisateur que sa demande est refusée"""
    content = f"""
        <h2>Demande refusée</h2>
        <p>Bonjour {prenom} {nom},</p>
        <p>Nous sommes désolés, mais votre demande d'accès à <strong>{company_name}</strong> a été refusée.</p>
    """
    
    if reason:
        content += f"""
        <div class="info-box">
            <p><strong>Raison:</strong> {reason}</p>
        </div>
        """
    
    content += """
        <p>Si vous pensez qu'il s'agit d'une erreur, veuillez contacter directement l'administrateur de la compagnie.</p>
    """
    return get_email_base_template(content)


def get_password_reset_email_template(nom: str, prenom: str, code: str) -> str:
    """Template pour la réinitialisation de mot de passe"""
    content = f"""
        <h2>Réinitialisation de mot de passe 🔐</h2>
        <p>Bonjour {prenom} {nom},</p>
        <p>Vous avez demandé à réinitialiser votre mot de passe. Utilisez le code ci-dessous pour créer un nouveau mot de passe :</p>
        
        <div class="code-box">
            <p style="margin: 0; color: #666; font-size: 14px;">Votre code de réinitialisation :</p>
            <div class="code">{code}</div>
            <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">Ce code expire dans 15 minutes</p>
        </div>
        
        <p><strong>⚠️ Important:</strong> Si vous n'avez pas demandé cette réinitialisation, ignorez cet email et votre mot de passe restera inchangé.</p>
    """
    return get_email_base_template(content)


def get_welcome_email_template(nom: str, prenom: str, company_name: str, is_admin_principal: bool) -> str:
    """Template de bienvenue après création de compagnie"""
    content = f"""
        <h2>Bienvenue dans Interface CAH ! 🚀</h2>
        <p>Félicitations {prenom} {nom},</p>
        <p>Votre compagnie <strong>{company_name}</strong> a été créée avec succès !</p>
    """
    
    if is_admin_principal:
        content += """
        <div class="info-box">
            <p><strong>🎯 Vous êtes l'administrateur principal</strong></p>
            <p>En tant qu'administrateur principal, vous pouvez :</p>
            <ul style="text-align: left;">
                <li>Approuver ou refuser les demandes d'accès</li>
                <li>Gérer les informations de votre compagnie</li>
                <li>Nommer d'autres administrateurs</li>
                <li>Accéder à toutes les fonctionnalités</li>
            </ul>
        </div>
        """
    
    content += """
        <p>Vous pouvez maintenant commencer à utiliser Interface CAH pour gérer votre portfolio immobilier.</p>
        
        <a href="{}" class="button">
            Accéder à mon compte
        </a>
    """.format(os.getenv('FRONTEND_URL', 'http://localhost:5173'))
    
    return get_email_base_template(content)


# ==========================================
# FONCTION D'ENVOI
# ==========================================

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Envoyer un email HTML
    
    Args:
        to_email: Adresse email du destinataire
        subject: Sujet de l'email
        html_content: Contenu HTML de l'email
    
    Returns:
        True si envoyé avec succès, False sinon
    """
    # Mode développement : afficher dans la console au lieu d'envoyer
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"\n{'='*60}")
        print(f"📧 EMAIL (Mode Développement)")
        print(f"{'='*60}")
        print(f"À: {to_email}")
        print(f"Sujet: {subject}")
        print(f"Contenu: [HTML - {len(html_content)} caractères]")
        print(f"{'='*60}\n")
        return True
    
    try:
        # Créer le message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message["To"] = to_email
        
        # Ajouter le contenu HTML
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Envoyer via SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Email envoyé à {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur envoi email à {to_email}: {e}")
        return False


# ==========================================
# FONCTIONS PRATIQUES
# ==========================================

def send_verification_email(to_email: str, nom: str, prenom: str, code: str) -> bool:
    """Envoyer un email de vérification"""
    subject = "Vérifiez votre adresse email - Interface CAH"
    html_content = get_verification_email_template(nom, prenom, code)
    return send_email(to_email, subject, html_content)


def send_access_request_notification(to_email: str, admin_nom: str, user_info: dict, company_name: str) -> bool:
    """Envoyer une notification de demande d'accès à l'admin"""
    subject = f"Nouvelle demande d'accès - {company_name}"
    html_content = get_access_request_email_template(admin_nom, user_info, company_name)
    return send_email(to_email, subject, html_content)


def send_approval_notification(to_email: str, nom: str, prenom: str, company_name: str) -> bool:
    """Envoyer une notification d'approbation"""
    subject = f"Votre accès à {company_name} est approuvé !"
    html_content = get_approval_email_template(nom, prenom, company_name)
    return send_email(to_email, subject, html_content)


def send_rejection_notification(to_email: str, nom: str, prenom: str, company_name: str, reason: Optional[str] = None) -> bool:
    """Envoyer une notification de refus"""
    subject = f"Demande d'accès à {company_name}"
    html_content = get_rejection_email_template(nom, prenom, company_name, reason)
    return send_email(to_email, subject, html_content)


def send_password_reset_email(to_email: str, nom: str, prenom: str, code: str) -> bool:
    """Envoyer un email de réinitialisation de mot de passe"""
    subject = "Réinitialisation de votre mot de passe - Interface CAH"
    html_content = get_password_reset_email_template(nom, prenom, code)
    return send_email(to_email, subject, html_content)


def send_welcome_email(to_email: str, nom: str, prenom: str, company_name: str, is_admin_principal: bool) -> bool:
    """Envoyer un email de bienvenue"""
    subject = f"Bienvenue dans Interface CAH - {company_name}"
    html_content = get_welcome_email_template(nom, prenom, company_name, is_admin_principal)
    return send_email(to_email, subject, html_content)


if __name__ == "__main__":
    # Test
    print("🧪 Test du service d'emails (mode développement)")
    send_verification_email(
        "test@example.com",
        "Héroux",
        "Sacha",
        "ABC123"
    )

