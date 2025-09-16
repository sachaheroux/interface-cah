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
    proprietaire = Column(Text)
    banque = Column(Text)
    contracteur = Column(Text)
    notes = Column(Text, default="")
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    unites = relationship("Unite", back_populates="immeuble", lazy="select", cascade="all, delete-orphan")
    factures = relationship("Facture", back_populates="immeuble", lazy="select", cascade="all, delete-orphan")
    rapports_immeuble = relationship("RapportImmeuble", back_populates="immeuble", lazy="select", cascade="all, delete-orphan")
    
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
    id_unite = Column(Integer, ForeignKey("unites.id_unite", ondelete="CASCADE"), nullable=False, index=True)
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

class Facture(Base):
    """Modèle pour les factures"""
    __tablename__ = "factures"
    
    id_facture = Column(Integer, primary_key=True, index=True)
    id_immeuble = Column(Integer, ForeignKey("immeubles.id_immeuble", ondelete="CASCADE"), nullable=False, index=True)
    categorie = Column(String(100), nullable=False)  # taxes municipales, taxes scolaires, électricité, etc.
    montant = Column(DECIMAL(12, 2), nullable=False)
    date = Column(Date, nullable=False, index=True)
    no_facture = Column(String(100), nullable=False, index=True)
    source = Column(String(255), nullable=True)  # ex: Hydro Québec
    pdf_facture = Column(String(255), nullable=True)  # nom du fichier PDF
    type_paiement = Column(String(50), nullable=True)  # virement, chèque, etc.
    notes = Column(Text, default="")
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    immeuble = relationship("Immeuble", back_populates="factures", lazy="select")
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id_facture": self.id_facture,
            "id_immeuble": self.id_immeuble,
            "categorie": self.categorie,
            "montant": float(self.montant) if self.montant else 0.0,
            "date": self.date.isoformat() if self.date else None,
            "no_facture": self.no_facture,
            "source": self.source,
            "pdf_facture": self.pdf_facture,
            "type_paiement": self.type_paiement,
            "notes": self.notes,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class RapportImmeuble(Base):
    """Modèle pour les rapports de rentabilité des immeubles"""
    __tablename__ = "rapports_immeuble"
    
    id_rapport = Column(Integer, primary_key=True, index=True)
    id_immeuble = Column(Integer, ForeignKey("immeubles.id_immeuble", ondelete="CASCADE"), nullable=False, index=True)
    annee = Column(Integer, nullable=False, index=True)
    mois = Column(Integer, nullable=False, index=True)  # 1-12
    revenus_totaux = Column(DECIMAL(12, 2), default=0)
    depenses_totales = Column(DECIMAL(12, 2), default=0)
    marge_nette = Column(DECIMAL(12, 2), default=0)
    notes = Column(Text, default="")
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    immeuble = relationship("Immeuble", back_populates="rapports_immeuble", lazy="select")
    
    # Contrainte unique
    __table_args__ = (UniqueConstraint('id_immeuble', 'annee', 'mois', name='unique_immeuble_annee_mois'),)
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id_rapport": self.id_rapport,
            "id_immeuble": self.id_immeuble,
            "annee": self.annee,
            "mois": self.mois,
            "revenus_totaux": float(self.revenus_totaux) if self.revenus_totaux else 0.0,
            "depenses_totales": float(self.depenses_totales) if self.depenses_totales else 0.0,
            "marge_nette": float(self.marge_nette) if self.marge_nette else 0.0,
            "notes": self.notes,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }
