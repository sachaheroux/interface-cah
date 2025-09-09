#!/usr/bin/env python3
"""
Modèles SQLAlchemy pour Interface CAH
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, DECIMAL, Date, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()

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
    unit_data = Column(Text)       # JSON string
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_default = Column(Boolean, default=False)
    
    # Relations
    assignments = relationship("Assignment", back_populates="building")
    building_reports = relationship("BuildingReport", back_populates="building")
    unit_reports = relationship("UnitReport", back_populates="building")
    invoices = relationship("Invoice", back_populates="building")
    
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
            "characteristics": json.loads(self.characteristics) if self.characteristics else {},
            "financials": json.loads(self.financials) if self.financials else {},
            "contacts": json.loads(self.contacts) if self.contacts else {},
            "unitData": json.loads(self.unit_data) if self.unit_data else {},
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
    
    # Relations
    assignments = relationship("Assignment", back_populates="tenant")
    
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
            "financial": json.loads(self.financial_info) if self.financial_info else {},
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }

class Assignment(Base):
    """Modèle pour les assignations locataire-unité"""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_id = Column(String(50), nullable=False, index=True)
    unit_number = Column(String(50))
    unit_address = Column(String(255))
    move_in_date = Column(Date, nullable=False)
    move_out_date = Column(Date)
    rent_amount = Column(DECIMAL(10, 2))
    deposit_amount = Column(DECIMAL(10, 2))
    lease_start_date = Column(Date)
    lease_end_date = Column(Date)
    rent_due_day = Column(Integer, default=1)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    tenant = relationship("Tenant", back_populates="assignments")
    building = relationship("Building", back_populates="assignments")
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id": self.id,
            "tenantId": self.tenant_id,
            "buildingId": self.building_id,
            "unitId": self.unit_id,
            "unitNumber": self.unit_number,
            "unitAddress": self.unit_address,
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
            # Données enrichies
            "tenantData": self.tenant.to_dict() if self.tenant else None,
            "buildingData": self.building.to_dict() if self.building else None
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
    building = relationship("Building", back_populates="building_reports")
    
    # Contrainte unique
    __table_args__ = (UniqueConstraint('building_id', 'year', name='unique_building_year'),)
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id": self.id,
            "buildingId": self.building_id,
            "year": self.year,
            "municipalTaxes": float(self.municipal_taxes),
            "schoolTaxes": float(self.school_taxes),
            "insurance": float(self.insurance),
            "snowRemoval": float(self.snow_removal),
            "lawnCare": float(self.lawn_care),
            "management": float(self.management),
            "renovations": float(self.renovations),
            "repairs": float(self.repairs),
            "wifi": float(self.wifi),
            "electricity": float(self.electricity),
            "other": float(self.other),
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }

class UnitReport(Base):
    """Modèle pour les rapports d'unités"""
    __tablename__ = "unit_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_id = Column(String(50), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    rent_collected = Column(DECIMAL(10, 2), default=0)
    expenses = Column(DECIMAL(10, 2), default=0)
    maintenance = Column(DECIMAL(10, 2), default=0)
    utilities = Column(DECIMAL(10, 2), default=0)
    other_income = Column(DECIMAL(10, 2), default=0)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    building = relationship("Building", back_populates="unit_reports")
    
    # Contrainte unique
    __table_args__ = (UniqueConstraint('building_id', 'unit_id', 'year', name='unique_building_unit_year'),)
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            "id": self.id,
            "buildingId": self.building_id,
            "unitId": self.unit_id,
            "year": self.year,
            "rentCollected": float(self.rent_collected),
            "expenses": float(self.expenses),
            "maintenance": float(self.maintenance),
            "utilities": float(self.utilities),
            "otherIncome": float(self.other_income),
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
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
    
    # Relations
    building = relationship("Building", back_populates="invoices")
    
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
