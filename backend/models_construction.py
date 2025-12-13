#!/usr/bin/env python3
"""
Modèles SQLAlchemy pour la gestion des projets de construction
Base de données : construction_projects.db
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database_construction import ConstructionBase

class Projet(ConstructionBase):
    """Modèle pour les projets de construction"""
    __tablename__ = "projets"
    
    id_projet = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False)
    
    # Dates importantes
    date_debut = Column(DateTime)
    date_fin_prevue = Column(DateTime)
    date_fin_reelle = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    
    # Adresse
    adresse = Column(String(255))
    ville = Column(String(100))
    province = Column(String(50))
    code_postal = Column(String(10))
    
    # Budget
    budget_total = Column(Float, default=0)
    
    # Métadonnées
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    commandes = relationship("Commande", back_populates="projet")
    factures_st = relationship("FactureST", back_populates="projet")
    punchs_employes = relationship("PunchEmploye", back_populates="projet")
    
    def to_dict(self):
        return {
            "id_projet": self.id_projet,
            "nom": self.nom,
            "date_debut": self.date_debut.isoformat() if self.date_debut else None,
            "date_fin_prevue": self.date_fin_prevue.isoformat() if self.date_fin_prevue else None,
            "date_fin_reelle": self.date_fin_reelle.isoformat() if self.date_fin_reelle else None,
            "notes": self.notes,
            "adresse": self.adresse,
            "ville": self.ville,
            "province": self.province,
            "code_postal": self.code_postal,
            "budget_total": self.budget_total,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class Fournisseur(ConstructionBase):
    """Modèle pour les fournisseurs"""
    __tablename__ = "fournisseurs"
    
    id_fournisseur = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False)
    rue = Column(String(255))
    ville = Column(String(100))
    province = Column(String(50))
    code_postal = Column(String(10))
    numero = Column(String(20))
    adresse_courriel = Column(String(255))
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    commandes = relationship("Commande", back_populates="fournisseur")
    
    def to_dict(self):
        return {
            "id_fournisseur": self.id_fournisseur,
            "nom": self.nom,
            "rue": self.rue,
            "ville": self.ville,
            "province": self.province,
            "code_postal": self.code_postal,
            "numero": self.numero,
            "adresse_courriel": self.adresse_courriel,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class MatierePremiere(ConstructionBase):
    """Modèle pour les matières premières"""
    __tablename__ = "matieres_premieres"
    
    id_matiere_premiere = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False)
    notes = Column(Text)
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    lignes_commande = relationship("LigneCommande", back_populates="matiere_premiere")
    
    def to_dict(self):
        return {
            "id_matiere_premiere": self.id_matiere_premiere,
            "nom": self.nom,
            "notes": self.notes,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class Commande(ConstructionBase):
    """Modèle pour les commandes"""
    __tablename__ = "commandes"
    
    id_commande = Column(Integer, primary_key=True, index=True)
    id_projet = Column(Integer, ForeignKey("projets.id_projet"), nullable=False)
    id_fournisseur = Column(Integer, ForeignKey("fournisseurs.id_fournisseur"), nullable=False)
    montant = Column(Float)
    statut = Column(String(50), default="en_attente")  # en_attente, confirmee, livree, facturee
    type_de_paiement = Column(String(50))  # comptant, credit, cheque
    notes = Column(Text)
    pdf_commande = Column(String(500))  # Nom du fichier PDF sur Backblaze
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    projet = relationship("Projet", back_populates="commandes")
    fournisseur = relationship("Fournisseur", back_populates="commandes")
    lignes_commande = relationship("LigneCommande", back_populates="commande", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id_commande": self.id_commande,
            "id_projet": self.id_projet,
            "id_fournisseur": self.id_fournisseur,
            "montant": self.montant,
            "statut": self.statut,
            "type_de_paiement": self.type_de_paiement,
            "notes": self.notes,
            "pdf_commande": self.pdf_commande,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "projet": self.projet.to_dict() if self.projet else None,
            "fournisseur": self.fournisseur.to_dict() if self.fournisseur else None
        }

class LigneCommande(ConstructionBase):
    """Modèle pour les lignes de commande (table de liaison N:N)"""
    __tablename__ = "lignes_commande"
    
    id_ligne = Column(Integer, primary_key=True, index=True)
    id_commande = Column(Integer, ForeignKey("commandes.id_commande", ondelete="CASCADE"), nullable=False)
    id_matiere_premiere = Column(Integer, ForeignKey("matieres_premieres.id_matiere_premiere"), nullable=False)
    quantite = Column(Float, nullable=False)
    unite = Column(String(20), nullable=False)  # kg, m², m³, pieces, etc.
    montant = Column(Float, nullable=False)
    section = Column(String(100))  # Section du projet
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    commande = relationship("Commande", back_populates="lignes_commande")
    matiere_premiere = relationship("MatierePremiere", back_populates="lignes_commande")
    
    def to_dict(self):
        return {
            "id_ligne": self.id_ligne,
            "id_commande": self.id_commande,
            "id_matiere_premiere": self.id_matiere_premiere,
            "quantite": self.quantite,
            "unite": self.unite,
            "montant": self.montant,
            "section": self.section,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "commande": self.commande.to_dict() if self.commande else None,
            "matiere_premiere": self.matiere_premiere.to_dict() if self.matiere_premiere else None
        }

class Employe(ConstructionBase):
    """Modèle pour les employés de construction"""
    __tablename__ = "employes"
    
    id_employe = Column(Integer, primary_key=True, index=True)
    prenom = Column(String(100), nullable=False)
    nom = Column(String(100), nullable=False)
    poste = Column(String(100))  # ouvrier, contremaitre, etc.
    numero = Column(String(20))
    adresse_courriel = Column(String(255))
    taux_horaire = Column(Float)  # Taux horaire en dollars
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    punchs_employes = relationship("PunchEmploye", back_populates="employe")
    
    def to_dict(self):
        return {
            "id_employe": self.id_employe,
            "prenom": self.prenom,
            "nom": self.nom,
            "poste": self.poste,
            "numero": self.numero,
            "adresse_courriel": self.adresse_courriel,
            "taux_horaire": self.taux_horaire,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class PunchEmploye(ConstructionBase):
    """Modèle pour les pointages des employés"""
    __tablename__ = "punchs_employes"
    
    id_punch = Column(Integer, primary_key=True, index=True)
    id_employe = Column(Integer, ForeignKey("employes.id_employe"), nullable=False)
    id_projet = Column(Integer, ForeignKey("projets.id_projet"), nullable=False)
    date = Column(DateTime, nullable=False)
    heure_travaillee = Column(Float, nullable=False)  # en heures
    section = Column(String(100))  # Section du projet
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    employe = relationship("Employe", back_populates="punchs_employes")
    projet = relationship("Projet", back_populates="punchs_employes")
    
    def to_dict(self):
        return {
            "id_punch": self.id_punch,
            "id_employe": self.id_employe,
            "id_projet": self.id_projet,
            "date": self.date.isoformat() if self.date else None,
            "heure_travaillee": self.heure_travaillee,
            "section": self.section,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "employe": self.employe.to_dict() if self.employe else None,
            "projet": self.projet.to_dict() if self.projet else None
        }

class SousTraitant(ConstructionBase):
    """Modèle pour les sous-traitants"""
    __tablename__ = "sous_traitants"
    
    id_st = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False)
    rue = Column(String(255))
    ville = Column(String(100))
    province = Column(String(50))
    code_postal = Column(String(10))
    numero = Column(String(20))
    adresse_courriel = Column(String(255))
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    factures_st = relationship("FactureST", back_populates="sous_traitant")
    
    def to_dict(self):
        return {
            "id_st": self.id_st,
            "nom": self.nom,
            "rue": self.rue,
            "ville": self.ville,
            "province": self.province,
            "code_postal": self.code_postal,
            "numero": self.numero,
            "adresse_courriel": self.adresse_courriel,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }

class FactureST(ConstructionBase):
    """Modèle pour les factures des sous-traitants"""
    __tablename__ = "factures_st"
    
    id_facture = Column(Integer, primary_key=True, index=True)
    id_projet = Column(Integer, ForeignKey("projets.id_projet"), nullable=False)
    id_st = Column(Integer, ForeignKey("sous_traitants.id_st"), nullable=False)
    montant = Column(Float, nullable=False)
    section = Column(String(100))  # Section du projet
    notes = Column(Text)
    reference = Column(String(100))  # Référence de la facture
    date_de_paiement = Column(DateTime)  # Date de paiement
    pdf_facture = Column(String(500))  # Nom du fichier PDF sur Backblaze
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    projet = relationship("Projet", back_populates="factures_st")
    sous_traitant = relationship("SousTraitant", back_populates="factures_st")
    
    def to_dict(self):
        return {
            "id_facture": self.id_facture,
            "id_projet": self.id_projet,
            "id_st": self.id_st,
            "montant": self.montant,
            "section": self.section,
            "notes": self.notes,
            "reference": self.reference,
            "date_de_paiement": self.date_de_paiement.isoformat() if self.date_de_paiement else None,
            "pdf_facture": self.pdf_facture,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "projet": self.projet.to_dict() if self.projet else None,
            "sous_traitant": self.sous_traitant.to_dict() if self.sous_traitant else None
        }

if __name__ == "__main__":
    # Test des modèles
    print("🧪 Test des modèles de construction...")
    
    from database_construction import init_construction_database
    if init_construction_database():
        print("✅ Modèles créés avec succès")
    else:
        print("❌ Échec de la création des modèles")
