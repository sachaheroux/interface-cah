#!/usr/bin/env python3
"""
Modèles SQLAlchemy en français pour Interface CAH
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, DECIMAL, Date, ForeignKey, UniqueConstraint, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()

# Méthodes utilitaires pour éviter la récursion et gérer les erreurs JSON
def safe_json_loads(json_string):
    """Charger JSON de manière sécurisée"""
    if not json_string:
        return {}
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return {}

class Immeuble(Base):
    """Modèle pour les immeubles"""
    __tablename__ = "immeubles"
    
    id_immeuble = Column(Integer, primary_key=True, index=True)
    nom_immeuble = Column(String(255), nullable=False, index=True)
    adresse = Column(String(255), nullable=False)
    ville = Column(String(255), nullable=False)
    province = Column(String(255), nullable=False)
    code_postal = Column(String(20), nullable=False)
    pays = Column(String(100), default="Canada")
    nbr_unite = Column(Integer, nullable=False, default=1)
    annee_construction = Column(Integer)
    prix_achete = Column(DECIMAL(12, 2), default=0)
    mise_de_fond = Column(DECIMAL(12, 2), default=0)
    taux_interet = Column(DECIMAL(5, 2), default=0)  # pourcentage
    valeur_actuel = Column(DECIMAL(12, 2), default=0)
    dette_restante = Column(DECIMAL(12, 2), default=0, nullable=True)
    proprietaire = Column(Text)
    banque = Column(Text)
    contracteur = Column(Text)
    notes = Column(Text, default="")
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    unites = relationship("Unite", back_populates="immeuble", lazy="select", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="immeuble", lazy="select", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id_immeuble": self.id_immeuble,
            "nom_immeuble": self.nom_immeuble,
            "adresse": self.adresse,
            "ville": self.ville,
            "province": self.province,
            "code_postal": self.code_postal,
            "pays": self.pays,
            "nbr_unite": self.nbr_unite,
            "annee_construction": self.annee_construction,
            "prix_achete": float(self.prix_achete) if self.prix_achete else 0.0,
            "mise_de_fond": float(self.mise_de_fond) if self.mise_de_fond else 0.0,
            "taux_interet": float(self.taux_interet) if self.taux_interet else 0.0,
            "valeur_actuel": float(self.valeur_actuel) if self.valeur_actuel else 0.0,
            "dette_restante": float(self.dette_restante) if self.dette_restante else 0.0,
            "proprietaire": self.proprietaire,
            "banque": self.banque,
            "contracteur": self.contracteur,
            "notes": self.notes,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class Unite(Base):
    """Modèle pour les unités"""
    __tablename__ = "unites"
    
    id_unite = Column(Integer, primary_key=True, index=True)
    id_immeuble = Column(Integer, ForeignKey("immeubles.id_immeuble", ondelete="CASCADE"), nullable=False, index=True)
    adresse_unite = Column(String(255), nullable=False)
    type = Column(String(50), default="4 1/2")  # 1 1/2, 2 1/2, 3 1/2, 4 1/2, 5 1/2
    nbr_chambre = Column(Integer, default=1)
    nbr_salle_de_bain = Column(Integer, default=1)
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    immeuble = relationship("Immeuble", back_populates="unites", lazy="select")
    locataires = relationship("Locataire", back_populates="unite", lazy="select")
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id_unite": self.id_unite,
            "id_immeuble": self.id_immeuble,
            "adresse_unite": self.adresse_unite,
            "type": self.type,
            "nbr_chambre": self.nbr_chambre,
            "nbr_salle_de_bain": self.nbr_salle_de_bain,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class Locataire(Base):
    """Modèle pour les locataires"""
    __tablename__ = "locataires"
    
    id_locataire = Column(Integer, primary_key=True, index=True)
    id_unite = Column(Integer, ForeignKey("unites.id_unite", ondelete="CASCADE"), nullable=True, index=True)
    nom = Column(String(255), nullable=False, index=True)
    prenom = Column(String(255), nullable=True)
    email = Column(String(255), index=True)
    telephone = Column(String(50))
    statut = Column(String(50), default="actif")  # actif, inactif, suspendu
    notes = Column(Text, default="")
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    unite = relationship("Unite", back_populates="locataires", lazy="select")
    baux = relationship("Bail", back_populates="locataire", lazy="select", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id_locataire": self.id_locataire,
            "id_unite": self.id_unite,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "telephone": self.telephone,
            "statut": self.statut,
            "notes": self.notes,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class Bail(Base):
    """Modèle pour les baux"""
    __tablename__ = "baux"
    
    id_bail = Column(Integer, primary_key=True, index=True)
    id_locataire = Column(Integer, ForeignKey("locataires.id_locataire", ondelete="CASCADE"), nullable=False, index=True)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=True)
    prix_loyer = Column(DECIMAL(10, 2), default=0)
    methode_paiement = Column(String(50), nullable=True)  # virement, chèque, etc.
    pdf_bail = Column(String(255), nullable=True)  # nom du fichier PDF
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    locataire = relationship("Locataire", back_populates="baux", lazy="select")
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id_bail": self.id_bail,
            "id_locataire": self.id_locataire,
            "date_debut": self.date_debut.isoformat() if self.date_debut else None,
            "date_fin": self.date_fin.isoformat() if self.date_fin else None,
            "prix_loyer": float(self.prix_loyer) if self.prix_loyer else 0.0,
            "methode_paiement": self.methode_paiement,
            "pdf_bail": self.pdf_bail,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class Transaction(Base):
    """Modèle pour les transactions financières"""
    __tablename__ = "transactions"
    
    id_transaction = Column(Integer, primary_key=True, index=True)
    id_immeuble = Column(Integer, ForeignKey("immeubles.id_immeuble", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # 'revenu', 'depense'
    categorie = Column(String(100), nullable=False)  # 'taxes_scolaires', 'taxes_municipales', 'electricite', 'entretien', 'reparation', etc.
    montant = Column(DECIMAL(12, 2), nullable=False)
    date_de_transaction = Column(Date, nullable=False, index=True)
    methode_de_paiement = Column(String(50), nullable=True)  # 'virement', 'cheque', 'especes', 'carte'
    reference = Column(String(100), nullable=True)  # numero de facture, reference de paiement
    source = Column(String(255), nullable=True)  # compagnie qui a émis la facture
    pdf_transaction = Column(String(255), nullable=True)  # nom du fichier PDF
    notes = Column(Text, default="")
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    immeuble = relationship("Immeuble", back_populates="transactions", lazy="select")
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id_transaction": self.id_transaction,
            "id_immeuble": self.id_immeuble,
            "type": self.type,
            "categorie": self.categorie,
            "montant": float(self.montant) if self.montant else 0.0,
            "date_de_transaction": self.date_de_transaction.isoformat() if self.date_de_transaction else None,
            "methode_de_paiement": self.methode_de_paiement,
            "reference": self.reference,
            "source": self.source,
            "pdf_transaction": self.pdf_transaction,
            "notes": self.notes,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class PaiementLoyer(Base):
    """Modèle pour le suivi des paiements de loyers
    Note: Si un paiement existe dans cette table, cela signifie qu'il est payé.
    Si un paiement n'existe pas, cela signifie qu'il n'est pas payé.
    """
    __tablename__ = "paiements_loyers"
    
    id_paiement = Column(Integer, primary_key=True, index=True)
    id_bail = Column(Integer, ForeignKey("baux.id_bail"), nullable=False, index=True)
    mois = Column(Integer, nullable=False)  # 1-12
    annee = Column(Integer, nullable=False)  # 2024, 2025, etc.
    date_paiement_reelle = Column(Date, nullable=False)  # Date de paiement (par défaut le 1er du mois)
    montant_paye = Column(DECIMAL(10, 2), nullable=False)  # Montant payé (par défaut le prix du bail)
    notes = Column(Text, nullable=True)  # Notes optionnelles
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    bail = relationship("Bail", backref="paiements")
    
    # Contrainte unique pour éviter les doublons
    __table_args__ = (
        UniqueConstraint('id_bail', 'mois', 'annee', name='unique_paiement_bail_mois_annee'),
    )
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id_paiement": self.id_paiement,
            "id_bail": self.id_bail,
            "mois": self.mois,
            "annee": self.annee,
            "date_paiement_reelle": self.date_paiement_reelle.isoformat() if self.date_paiement_reelle else None,
            "montant_paye": float(self.montant_paye) if self.montant_paye else None,
            "notes": self.notes,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

