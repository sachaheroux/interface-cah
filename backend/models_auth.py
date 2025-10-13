#!/usr/bin/env python3
"""
Modèles d'authentification et multi-tenant pour Interface CAH
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from models_francais import Base

# ==========================================
# MODÈLES D'AUTHENTIFICATION ET MULTI-TENANT
# ==========================================

class Compagnie(Base):
    """Modèle pour les compagnies (multi-tenant)"""
    __tablename__ = "compagnies"
    
    id_compagnie = Column(Integer, primary_key=True, index=True)
    nom_compagnie = Column(String(255), nullable=False, unique=True, index=True)
    email_compagnie = Column(String(255), nullable=False)
    telephone_compagnie = Column(String(50))
    adresse_compagnie = Column(Text)
    logo_compagnie = Column(String(500))  # URL ou chemin du fichier
    site_web = Column(String(255))
    numero_entreprise = Column(String(100))  # NEQ ou autre
    schema_name = Column(String(100), nullable=False, unique=True, index=True)  # Nom du schéma PostgreSQL
    code_acces = Column(String(20), unique=True, index=True)  # Code unique pour rejoindre la compagnie
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    utilisateurs = relationship("Utilisateur", back_populates="compagnie", lazy="select")
    demandes_acces = relationship("DemandeAcces", back_populates="compagnie", lazy="select")
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id_compagnie": self.id_compagnie,
            "nom_compagnie": self.nom_compagnie,
            "email_compagnie": self.email_compagnie,
            "telephone_compagnie": self.telephone_compagnie,
            "adresse_compagnie": self.adresse_compagnie,
            "logo_compagnie": self.logo_compagnie,
            "site_web": self.site_web,
            "numero_entreprise": self.numero_entreprise,
            "schema_name": self.schema_name,
            "code_acces": self.code_acces,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class Utilisateur(Base):
    """Modèle pour les utilisateurs (employés et admins)"""
    __tablename__ = "utilisateurs"
    
    id_utilisateur = Column(Integer, primary_key=True, index=True)
    id_compagnie = Column(Integer, ForeignKey("compagnies.id_compagnie", ondelete="CASCADE"), nullable=False, index=True)
    
    # Informations de connexion
    email = Column(String(255), nullable=False, unique=True, index=True)
    mot_de_passe_hash = Column(String(255), nullable=False)  # Hashé avec bcrypt
    
    # Informations personnelles
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    date_naissance = Column(Date)
    age = Column(Integer)
    sexe = Column(String(50))  # Homme, Femme, Autre, etc.
    telephone = Column(String(50))
    poste = Column(String(255))  # Titre du poste
    
    # Rôle et statut
    role = Column(String(50), nullable=False, default="employe")  # "admin" ou "employe"
    est_admin_principal = Column(Boolean, default=False)  # Admin principal de la compagnie
    statut = Column(String(50), nullable=False, default="en_attente")  # "en_attente", "actif", "inactif", "refuse"
    
    # Validation email
    email_verifie = Column(Boolean, default=False)
    code_verification_email = Column(String(10))
    code_verification_expiration = Column(DateTime)
    
    # Récupération mot de passe
    code_reset_mdp = Column(String(10))
    code_reset_mdp_expiration = Column(DateTime)
    
    # Dates
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    derniere_connexion = Column(DateTime)
    
    # Relations
    compagnie = relationship("Compagnie", back_populates="utilisateurs", lazy="select")
    
    def to_dict(self, include_sensitive=False):
        """Convertir en dictionnaire pour l'API"""
        data = {
            "id_utilisateur": self.id_utilisateur,
            "id_compagnie": self.id_compagnie,
            "email": self.email,
            "nom": self.nom,
            "prenom": self.prenom,
            "date_naissance": self.date_naissance.isoformat() if self.date_naissance else None,
            "age": self.age,
            "sexe": self.sexe,
            "telephone": self.telephone,
            "poste": self.poste,
            "role": self.role,
            "est_admin_principal": self.est_admin_principal,
            "statut": self.statut,
            "email_verifie": self.email_verifie,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "derniere_connexion": self.derniere_connexion.isoformat() if self.derniere_connexion else None,
            "compagnie": self.compagnie.to_dict() if self.compagnie else None
        }
        
        if include_sensitive:
            data["code_verification_email"] = self.code_verification_email
            data["code_reset_mdp"] = self.code_reset_mdp
        
        return data

class DemandeAcces(Base):
    """Modèle pour les demandes d'accès à une compagnie"""
    __tablename__ = "demandes_acces"
    
    id_demande = Column(Integer, primary_key=True, index=True)
    id_compagnie = Column(Integer, ForeignKey("compagnies.id_compagnie", ondelete="CASCADE"), nullable=False, index=True)
    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur", ondelete="CASCADE"), nullable=False, index=True)
    
    # Statut de la demande
    statut = Column(String(50), nullable=False, default="en_attente")  # "en_attente", "approuve", "refuse"
    
    # Informations sur le traitement
    traite_par = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"))  # ID de l'admin qui a traité
    date_traitement = Column(DateTime)
    commentaire_refus = Column(Text)  # Si refusé, raison du refus
    
    # Dates
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    compagnie = relationship("Compagnie", back_populates="demandes_acces", lazy="select")
    utilisateur = relationship("Utilisateur", foreign_keys=[id_utilisateur], lazy="select")
    admin_traiteur = relationship("Utilisateur", foreign_keys=[traite_par], lazy="select")
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id_demande": self.id_demande,
            "id_compagnie": self.id_compagnie,
            "id_utilisateur": self.id_utilisateur,
            "statut": self.statut,
            "traite_par": self.traite_par,
            "date_traitement": self.date_traitement.isoformat() if self.date_traitement else None,
            "commentaire_refus": self.commentaire_refus,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "utilisateur": self.utilisateur.to_dict() if self.utilisateur else None,
            "compagnie": self.compagnie.to_dict() if self.compagnie else None,
            "admin_traiteur": self.admin_traiteur.to_dict() if self.admin_traiteur else None
        }

