#!/usr/bin/env python3
"""
Modèles SQLAlchemy pour Interface CAH
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

class Building(Base):
    """Modèle pour les immeubles"""
    __tablename__ = "buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    address_street = Column(String(255))
    address_city = Column(String(255))
    address_province = Column(String(255))
    address_postal_code = Column(String(20))
    address_country = Column(String(100), default="Canada")
    type = Column(String(100), nullable=False)
    units = Column(Integer, default=0)
    floors = Column(Integer, default=1)
    year_built = Column(Integer)
    total_area = Column(Integer)
    characteristics = Column(Text)  # JSON string
    financials = Column(Text)      # JSON string
    contacts = Column(Text)        # JSON string
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_default = Column(Boolean, default=False)
    
    # Relations avec lazy loading optimisé
    units_rel = relationship("Unit", back_populates="building", lazy="select", cascade="all, delete-orphan")
    building_reports = relationship("BuildingReport", back_populates="building", lazy="select")
    invoices = relationship("Invoice", back_populates="building", lazy="select")
    
    # Relations indirectes via les unités
    @property
    def assignments(self):
        """Récupérer toutes les assignations via les unités"""
        assignments = []
        for unit in self.units_rel:
            assignments.extend(unit.assignments)
        return assignments
    
    @property
    def unit_reports(self):
        """Récupérer tous les rapports d'unités via les unités"""
        unit_reports = []
        for unit in self.units_rel:
            unit_reports.extend(unit.unit_reports)
        return unit_reports
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id": self.id,
            "name": self.name,
            "address": {
                "street": self.address_street or "",
                "city": self.address_city or "",
                "province": self.address_province or "",
                "postalCode": self.address_postal_code or "",
                "country": self.address_country or "Canada"
            },
            "type": self.type,
            "units": self.units,
            "floors": self.floors,
            "yearBuilt": self.year_built,
            "totalArea": self.total_area,
            "characteristics": safe_json_loads(self.characteristics),
            "financials": safe_json_loads(self.financials),
            "contacts": safe_json_loads(self.contacts),
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }

class Tenant(Base):
    """Modèle pour les locataires"""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(50))
    emergency_contact_relationship = Column(String(100))
    move_in_date = Column(Date)
    move_out_date = Column(Date)
    financial_info = Column(Text)  # JSON string
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations - Un locataire peut avoir plusieurs assignations (historique)
    assignments = relationship("Assignment", back_populates="tenant", lazy="select")
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "emergencyContact": {
                "name": self.emergency_contact_name or "",
                "phone": self.emergency_contact_phone or "",
                "relationship": self.emergency_contact_relationship or ""
            },
            "moveInDate": self.move_in_date.isoformat() if self.move_in_date else None,
            "moveOutDate": self.move_out_date.isoformat() if self.move_out_date else None,
            "financial": safe_json_loads(self.financial_info),
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            # Ne pas retourner de données de bail par défaut - elles seront chargées depuis les assignations
            "lease": None
        }

class Unit(Base):
    """Modèle pour les unités"""
    __tablename__ = "units"
    
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_number = Column(String(50), nullable=False, index=True)
    unit_address = Column(String(255))
    type = Column(String(50), default="4 1/2")  # 1 1/2, 2 1/2, 3 1/2, 4 1/2, 5 1/2
    area = Column(Integer, default=0)  # en pieds carrés
    bedrooms = Column(Integer, default=1)
    bathrooms = Column(Integer, default=1)
    amenities = Column(Text)  # JSON string pour les équipements
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    building = relationship("Building", back_populates="units_rel", lazy="select")
    assignments = relationship("Assignment", back_populates="unit", lazy="select", cascade="all, delete-orphan")
    unit_reports = relationship("UnitReport", back_populates="unit", lazy="select", cascade="all, delete-orphan")
    
    # Contrainte unique pour éviter les doublons d'unités dans le même immeuble
    __table_args__ = (UniqueConstraint('building_id', 'unit_number', name='unique_building_unit_number'),)
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id": self.id,
            "buildingId": self.building_id,
            "unitNumber": self.unit_number,
            "unitAddress": self.unit_address,
            "type": self.type,
            "area": self.area,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "amenities": safe_json_loads(self.amenities),
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            # Données enrichies
            "buildingData": self._get_building_data()
        }
    
    def _get_building_data(self):
        """Obtenir les données de l'immeuble de manière sécurisée"""
        if not hasattr(self, 'building') or not self.building:
            return None
        return {
            "id": self.building.id,
            "name": self.building.name,
            "address": {
                "street": self.building.address_street or "",
                "city": self.building.address_city or "",
                "province": self.building.address_province or "",
                "postalCode": self.building.address_postal_code or "",
                "country": self.building.address_country or "Canada"
            }
        }

class Assignment(Base):
    """Modèle pour les assignations locataire-unité"""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_id = Column(Integer, ForeignKey("units.id", ondelete="CASCADE"), nullable=False, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False, index=True)
    move_in_date = Column(Date, nullable=False)
    move_out_date = Column(Date)
    rent_amount = Column(DECIMAL(10, 2))
    deposit_amount = Column(DECIMAL(10, 2))
    lease_start_date = Column(Date)
    lease_end_date = Column(Date)
    rent_due_day = Column(Integer, default=1)  # 1-31, validation au niveau applicatif
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations - Une assignation = un locataire + une unité + un immeuble
    tenant = relationship("Tenant", back_populates="assignments", lazy="select")
    unit = relationship("Unit", back_populates="assignments", lazy="select")
    building = relationship("Building", lazy="select")
    
    # Contrainte unique pour éviter les assignations multiples ACTIVES par locataire
    # Note: Cette contrainte sera gérée au niveau applicatif, pas au niveau base de données
    # car SQLite ne supporte pas les contraintes conditionnelles complexes
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id": self.id,
            "tenantId": self.tenant_id,
            "unitId": self.unit_id,
            "buildingId": self.building.id if self.building else None,
            "unitNumber": self.unit.unit_number if self.unit else None,
            "unitAddress": self.unit.unit_address if self.unit else None,
            "moveInDate": self.move_in_date.isoformat() if self.move_in_date else None,
            "moveOutDate": self.move_out_date.isoformat() if self.move_out_date else None,
            "rentAmount": float(self.rent_amount) if self.rent_amount else None,
            "depositAmount": float(self.deposit_amount) if self.deposit_amount else None,
            "leaseStartDate": self.lease_start_date.isoformat() if self.lease_start_date else None,
            "leaseEndDate": self.lease_end_date.isoformat() if self.lease_end_date else None,
            "rentDueDay": self.rent_due_day,
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            # Données enrichies (éviter la récursion infinie)
            "tenantData": self._get_tenant_data(),
            "unitData": self._get_unit_data(),
            "buildingData": self._get_building_data()
        }
    
    def _get_tenant_data(self):
        """Obtenir les données du locataire de manière sécurisée"""
        if not hasattr(self, 'tenant') or not self.tenant:
            return None
        return {
            "id": self.tenant.id,
            "name": self.tenant.name,
            "email": self.tenant.email,
            "phone": self.tenant.phone
        }
    
    def _get_unit_data(self):
        """Obtenir les données de l'unité de manière sécurisée"""
        if not hasattr(self, 'unit') or not self.unit:
            return None
        return {
            "id": self.unit.id,
            "unitNumber": self.unit.unit_number,
            "unitAddress": self.unit.unit_address,
            "type": self.unit.type,
            "area": self.unit.area,
            "bedrooms": self.unit.bedrooms,
            "bathrooms": self.unit.bathrooms
        }
    
    def _get_building_data(self):
        """Obtenir les données de l'immeuble de manière sécurisée"""
        if not hasattr(self, 'building') or not self.building:
            return None
        return {
            "id": self.building.id,
            "name": self.building.name,
            "address": {
                "street": self.building.address_street or "",
                "city": self.building.address_city or "",
                "province": self.building.address_province or "",
                "postalCode": self.building.address_postal_code or "",
                "country": self.building.address_country or "Canada"
            }
        }

class BuildingReport(Base):
    """Modèle pour les rapports d'immeubles"""
    __tablename__ = "building_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    municipal_taxes = Column(DECIMAL(10, 2), default=0)
    school_taxes = Column(DECIMAL(10, 2), default=0)
    insurance = Column(DECIMAL(10, 2), default=0)
    snow_removal = Column(DECIMAL(10, 2), default=0)
    lawn_care = Column(DECIMAL(10, 2), default=0)
    management = Column(DECIMAL(10, 2), default=0)
    renovations = Column(DECIMAL(10, 2), default=0)
    repairs = Column(DECIMAL(10, 2), default=0)
    wifi = Column(DECIMAL(10, 2), default=0)
    electricity = Column(DECIMAL(10, 2), default=0)
    other = Column(DECIMAL(10, 2), default=0)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    building = relationship("Building", back_populates="building_reports", lazy="select")
    
    # Contrainte unique
    __table_args__ = (UniqueConstraint('building_id', 'year', name='unique_building_year'),)
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id": self.id,
            "buildingId": self.building_id,
            "year": self.year,
            "municipalTaxes": float(self.municipal_taxes) if self.municipal_taxes else 0.0,
            "schoolTaxes": float(self.school_taxes) if self.school_taxes else 0.0,
            "insurance": float(self.insurance) if self.insurance else 0.0,
            "snowRemoval": float(self.snow_removal) if self.snow_removal else 0.0,
            "lawnCare": float(self.lawn_care) if self.lawn_care else 0.0,
            "management": float(self.management) if self.management else 0.0,
            "renovations": float(self.renovations) if self.renovations else 0.0,
            "repairs": float(self.repairs) if self.repairs else 0.0,
            "wifi": float(self.wifi) if self.wifi else 0.0,
            "electricity": float(self.electricity) if self.electricity else 0.0,
            "other": float(self.other) if self.other else 0.0,
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }

class UnitReport(Base):
    """Modèle pour les rapports d'unités"""
    __tablename__ = "unit_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id", ondelete="CASCADE"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)  # 1-12, validation au niveau applicatif
    tenant_name = Column(String(255))
    payment_method = Column(String(100))
    is_heated_lit = Column(Boolean, default=False)
    is_furnished = Column(Boolean, default=False)
    wifi_included = Column(Boolean, default=False)
    rent_amount = Column(DECIMAL(10, 2), default=0.0)
    start_date = Column(Date)
    end_date = Column(Date)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    unit = relationship("Unit", back_populates="unit_reports", lazy="select")
    
    # Propriété calculée pour l'immeuble (via l'unité)
    @property
    def building(self):
        return self.unit.building if self.unit else None
    
    # Propriété calculée pour l'immeuble ID (pour compatibilité)
    @property
    def building_id(self):
        return self.unit.building_id if self.unit else None
    
    # Contrainte unique
    __table_args__ = (UniqueConstraint('unit_id', 'year', 'month', name='unique_unit_year_month'),)
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id": self.id,
            "unitId": self.unit_id,
            "buildingId": self.building.id if self.building else None,
            "year": self.year,
            "month": self.month,
            "tenantName": self.tenant_name,
            "paymentMethod": self.payment_method,
            "isHeatedLit": self.is_heated_lit,
            "isFurnished": self.is_furnished,
            "wifiIncluded": self.wifi_included,
            "rentAmount": float(self.rent_amount) if self.rent_amount else None,
            "startDate": self.start_date.isoformat() if self.start_date else None,
            "endDate": self.end_date.isoformat() if self.end_date else None,
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            # Données enrichies
            "unitData": self._get_unit_data(),
            "buildingData": self._get_building_data()
        }
    
    def _get_unit_data(self):
        """Obtenir les données de l'unité de manière sécurisée"""
        if not hasattr(self, 'unit') or not self.unit:
            return None
        return {
            "id": self.unit.id,
            "unitNumber": self.unit.unit_number,
            "unitAddress": self.unit.unit_address,
            "type": self.unit.type
        }
    
    def _get_building_data(self):
        """Obtenir les données de l'immeuble de manière sécurisée"""
        if not hasattr(self, 'building') or not self.building:
            return None
        return {
            "id": self.building.id,
            "name": self.building.name,
            "address": {
                "street": self.building.address_street or "",
                "city": self.building.address_city or "",
                "province": self.building.address_province or "",
                "postalCode": self.building.address_postal_code or "",
                "country": self.building.address_country or "Canada"
            }
        }

class Invoice(Base):
    """Modèle pour les factures"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    source = Column(String(255), nullable=False)
    date = Column(Date, nullable=False, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(10), default="CAD")
    payment_type = Column(String(50), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="SET NULL"), index=True)
    unit_id = Column(String(50), index=True)
    pdf_filename = Column(String(255))
    pdf_path = Column(String(500))
    notes = Column(Text, default="")
    type = Column(String(50), default="rental")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations - Factures liées aux unités, pas aux locataires
    building = relationship("Building", back_populates="invoices", lazy="select")
    
    # Pas de relation directe avec les locataires
    # Les factures sont liées aux unités via unit_id
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id": self.id,
            "invoiceNumber": self.invoice_number,
            "category": self.category,
            "source": self.source,
            "date": self.date.isoformat() if self.date else None,
            "amount": float(self.amount),
            "currency": self.currency,
            "paymentType": self.payment_type,
            "buildingId": self.building_id,
            "unitId": self.unit_id,
            "pdfFilename": self.pdf_filename,
            "pdfPath": self.pdf_path,
            "notes": self.notes,
            "type": self.type,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
