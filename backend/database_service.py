#!/usr/bin/env python3me 
"""
Service de base de données pour Interface CAH
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json

from database import db_manager
from models import Building, Tenant, Unit, Assignment, BuildingReport, UnitReport, Invoice

class DatabaseService:
    """Service principal pour les opérations de base de données"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def get_session(self):
        """Obtenir une session de base de données"""
        return self.db_manager.SessionLocal()
    
    def _safe_parse_date(self, date_string):
        """Parser une date de manière sécurisée"""
        if not date_string:
            return None
        try:
            return datetime.fromisoformat(date_string).date()
        except (ValueError, TypeError):
            return None
    
    def _safe_parse_float(self, value, default=0.0):
        """Parser une valeur flottante de manière sécurisée"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    # ========================================
    # OPÉRATIONS SUR LES IMMEUBLES
    # ========================================
    
    def get_buildings(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupérer tous les immeubles"""
        session = self.get_session()
        try:
            buildings = session.query(Building).offset(skip).limit(limit).all()
            return [building.to_dict() for building in buildings]
        finally:
            session.close()
    
    def get_building(self, building_id: int) -> Optional[Dict]:
        """Récupérer un immeuble par ID"""
        session = self.get_session()
        try:
            building = session.query(Building).filter(Building.id == building_id).first()
            return building.to_dict() if building else None
        finally:
            session.close()
    
    def create_building(self, building_data: Dict) -> Dict:
        """Créer un nouvel immeuble"""
        session = self.get_session()
        try:
            # Extraire l'adresse
            address = building_data.get("address", {})
            if isinstance(address, dict):
                address_street = address.get("street", "")
                address_city = address.get("city", "")
                address_province = address.get("province", "")
                address_postal_code = address.get("postalCode", "")
                address_country = address.get("country", "Canada")
            else:
                address_street = str(address) if address else ""
                address_city = ""
                address_province = ""
                address_postal_code = ""
                address_country = "Canada"
            
            # Créer l'immeuble
            building = Building(
                name=building_data["name"],
                address_street=address_street,
                address_city=address_city,
                address_province=address_province,
                address_postal_code=address_postal_code,
                address_country=address_country,
                type=building_data.get("type", ""),
                units=building_data.get("units", 0),
                floors=building_data.get("floors", 1),
                year_built=building_data.get("yearBuilt"),
                total_area=building_data.get("totalArea"),
                characteristics=json.dumps(building_data.get("characteristics", {})),
                financials=json.dumps(building_data.get("financials", {})),
                contacts=json.dumps(building_data.get("contacts", {})),
                notes=building_data.get("notes", ""),
                is_default=False
            )
            
            session.add(building)
            session.commit()
            session.refresh(building)
            
            return building.to_dict()
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def update_building(self, building_id: int, building_data: Dict) -> Optional[Dict]:
        """Mettre à jour un immeuble"""
        session = self.get_session()
        try:
            building = session.query(Building).filter(Building.id == building_id).first()
            if not building:
                return None
            
            # Vérifier si c'est un immeuble par défaut
            if building.is_default:
                raise ValueError("Impossible de modifier un immeuble par défaut")
            
            # Mettre à jour les champs
            if "name" in building_data:
                building.name = building_data["name"]
            if "type" in building_data:
                building.type = building_data["type"]
            if "units" in building_data:
                building.units = building_data["units"]
            if "floors" in building_data:
                building.floors = building_data["floors"]
            if "yearBuilt" in building_data:
                building.year_built = building_data["yearBuilt"]
            if "totalArea" in building_data:
                building.total_area = building_data["totalArea"]
            if "notes" in building_data:
                building.notes = building_data["notes"]
            
            # Mettre à jour l'adresse
            if "address" in building_data:
                address = building_data["address"]
                if isinstance(address, dict):
                    building.address_street = address.get("street", "")
                    building.address_city = address.get("city", "")
                    building.address_province = address.get("province", "")
                    building.address_postal_code = address.get("postalCode", "")
                    building.address_country = address.get("country", "Canada")
            
            # Mettre à jour les données JSON
            if "characteristics" in building_data:
                building.characteristics = json.dumps(building_data["characteristics"])
            if "financials" in building_data:
                building.financials = json.dumps(building_data["financials"])
            if "contacts" in building_data:
                building.contacts = json.dumps(building_data["contacts"])
            if "unitData" in building_data:
                building.unit_data = json.dumps(building_data["unitData"])
            
            building.updated_at = datetime.utcnow()
            session.commit()
            
            return building.to_dict()
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def delete_building(self, building_id: int) -> bool:
        """Supprimer un immeuble"""
        session = self.get_session()
        try:
            building = session.query(Building).filter(Building.id == building_id).first()
            if not building:
                return False
            
            # Supprimer l'immeuble même s'il est marqué comme défaut
            # (pour permettre la suppression complète des données)
            session.delete(building)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    # ========================================
    # OPÉRATIONS SUR LES LOCATAIRES
    # ========================================
    
    def get_tenants(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupérer tous les locataires"""
        session = self.get_session()
        try:
            tenants = session.query(Tenant).offset(skip).limit(limit).all()
            return [tenant.to_dict() for tenant in tenants]
        finally:
            session.close()
    
    def get_tenant(self, tenant_id: int) -> Optional[Dict]:
        """Récupérer un locataire par ID"""
        session = self.get_session()
        try:
            tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
            return tenant.to_dict() if tenant else None
        finally:
            session.close()
    
    def create_tenant(self, tenant_data: Dict) -> Dict:
        """Créer un nouveau locataire"""
        session = self.get_session()
        try:
            # Extraire les contacts d'urgence
            emergency_contact = tenant_data.get("emergencyContact", {})
            
            tenant = Tenant(
                name=tenant_data["name"],
                email=tenant_data.get("email"),
                phone=tenant_data.get("phone"),
                emergency_contact_name=emergency_contact.get("name"),
                emergency_contact_phone=emergency_contact.get("phone"),
                emergency_contact_relationship=emergency_contact.get("relationship"),
                move_in_date=self._safe_parse_date(tenant_data.get("moveInDate")),
                move_out_date=self._safe_parse_date(tenant_data.get("moveOutDate")),
                financial_info=json.dumps(tenant_data.get("financial", {})),
                notes=tenant_data.get("notes", "")
            )
            
            session.add(tenant)
            session.commit()
            session.refresh(tenant)
            
            return tenant.to_dict()
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def update_tenant(self, tenant_id: int, tenant_data: Dict) -> Optional[Dict]:
        """Mettre à jour un locataire"""
        session = self.get_session()
        try:
            tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                return None
            
            # Mettre à jour les champs
            if "name" in tenant_data:
                tenant.name = tenant_data["name"]
            if "email" in tenant_data:
                tenant.email = tenant_data["email"]
            if "phone" in tenant_data:
                tenant.phone = tenant_data["phone"]
            if "notes" in tenant_data:
                tenant.notes = tenant_data["notes"]
            
            # Mettre à jour les contacts d'urgence
            if "emergencyContact" in tenant_data:
                emergency_contact = tenant_data["emergencyContact"]
                tenant.emergency_contact_name = emergency_contact.get("name")
                tenant.emergency_contact_phone = emergency_contact.get("phone")
                tenant.emergency_contact_relationship = emergency_contact.get("relationship")
            
            # Mettre à jour les dates
            if "moveInDate" in tenant_data:
                tenant.move_in_date = datetime.fromisoformat(tenant_data["moveInDate"]) if tenant_data["moveInDate"] else None
            if "moveOutDate" in tenant_data:
                tenant.move_out_date = datetime.fromisoformat(tenant_data["moveOutDate"]) if tenant_data["moveOutDate"] else None
            
            # Mettre à jour les informations financières
            if "financial" in tenant_data:
                tenant.financial_info = json.dumps(tenant_data["financial"])
            
            tenant.updated_at = datetime.utcnow()
            session.commit()
            
            return tenant.to_dict()
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def delete_tenant(self, tenant_id: int) -> bool:
        """Supprimer un locataire"""
        session = self.get_session()
        try:
            tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                return False
            
            session.delete(tenant)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    # ========================================
    # OPÉRATIONS SUR LES UNITÉS
    # ========================================
    
    def create_unit(self, unit_data: Dict) -> Dict:
        """Créer une nouvelle unité"""
        session = self.get_session()
        try:
            # Validation des clés étrangères
            building_id = unit_data["buildingId"]
            
            # Vérifier que l'immeuble existe
            building = session.query(Building).filter(Building.id == building_id).first()
            if not building:
                raise ValueError(f"L'immeuble avec l'ID {building_id} n'existe pas")
            
            unit = Unit(
                building_id=building_id,
                unit_number=unit_data["unitNumber"],
                unit_address=unit_data.get("unitAddress"),
                type=unit_data.get("type", "4 1/2"),
                area=unit_data.get("area", 0),
                bedrooms=unit_data.get("bedrooms", 1),
                bathrooms=unit_data.get("bathrooms", 1),
                amenities=json.dumps(unit_data.get("amenities", {})),
                notes=unit_data.get("notes", "")
            )
            
            session.add(unit)
            session.commit()
            session.refresh(unit)
            
            
            return unit.to_dict()
        except ValueError as e:
            session.rollback()
            raise e
        except Exception as e:
            session.rollback()
            raise ValueError(f"Erreur lors de la création de l'unité: {str(e)}")
        finally:
            session.close()
    
    def get_units(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupérer toutes les unités"""
        session = self.get_session()
        try:
            units = session.query(Unit).offset(skip).limit(limit).all()
            return [unit.to_dict() for unit in units]
        finally:
            session.close()
    
    def get_unit(self, unit_id: int) -> Optional[Dict]:
        """Récupérer une unité par ID"""
        session = self.get_session()
        try:
            unit = session.query(Unit).filter(Unit.id == unit_id).first()
            return unit.to_dict() if unit else None
        finally:
            session.close()
    
    def get_units_by_building(self, building_id: int) -> List[Dict]:
        """Récupérer toutes les unités d'un immeuble"""
        session = self.get_session()
        try:
            units = session.query(Unit).filter(Unit.building_id == building_id).all()
            return [unit.to_dict() for unit in units]
        finally:
            session.close()
    
    def update_unit(self, unit_id: int, unit_data: Dict) -> Optional[Dict]:
        """Mettre à jour une unité"""
        session = self.get_session()
        try:
            unit = session.query(Unit).filter(Unit.id == unit_id).first()
            if not unit:
                return None
            
            # Champs autorisés pour la mise à jour
            allowed_fields = [
                'unit_number', 'unit_address', 'type', 'area', 'bedrooms', 
                'bathrooms', 'amenities', 'rental_info', 'notes'
            ]
            
            for field, value in unit_data.items():
                if field in allowed_fields:
                    if field in ['amenities', 'rental_info']:
                        setattr(unit, field, json.dumps(value) if value else "{}")
                    else:
                        setattr(unit, field, value)
            
            unit.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(unit)
            
            return unit.to_dict()
        except Exception as e:
            session.rollback()
            raise ValueError(f"Erreur lors de la mise à jour de l'unité: {str(e)}")
        finally:
            session.close()
    
    def delete_unit(self, unit_id: int) -> bool:
        """Supprimer une unité"""
        session = self.get_session()
        try:
            unit = session.query(Unit).filter(Unit.id == unit_id).first()
            if not unit:
                return False
            
            session.delete(unit)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()

    # ========================================
    # OPÉRATIONS SUR LES FACTURES
    # ========================================
    
    def get_invoices(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupérer toutes les factures"""
        session = self.get_session()
        try:
            invoices = session.query(Invoice).offset(skip).limit(limit).all()
            return [invoice.to_dict() for invoice in invoices]
        finally:
            session.close()
    
    def get_invoice(self, invoice_id: int) -> Optional[Dict]:
        """Récupérer une facture par ID"""
        session = self.get_session()
        try:
            invoice = session.query(Invoice).filter(Invoice.id == invoice_id).first()
            return invoice.to_dict() if invoice else None
        finally:
            session.close()
    
    def create_invoice(self, invoice_data: Dict) -> Dict:
        """Créer une nouvelle facture"""
        session = self.get_session()
        try:
            # Vérifier l'unicité du numéro de facture
            existing = session.query(Invoice).filter(Invoice.invoice_number == invoice_data["invoiceNumber"]).first()
            if existing:
                raise ValueError("Le numéro de facture existe déjà")
            
            invoice = Invoice(
                invoice_number=invoice_data["invoiceNumber"],
                category=invoice_data["category"],
                source=invoice_data["source"],
                date=datetime.fromisoformat(invoice_data["date"]).date(),
                amount=self._safe_parse_float(invoice_data["amount"], 0.0),
                currency=invoice_data.get("currency", "CAD"),
                payment_type=invoice_data["paymentType"],
                building_id=invoice_data.get("buildingId"),
                unit_id=invoice_data.get("unitId"),
                pdf_filename=invoice_data.get("pdfFilename"),
                pdf_path=invoice_data.get("pdfPath"),
                notes=invoice_data.get("notes", ""),
                type=invoice_data.get("type", "rental")
            )
            
            session.add(invoice)
            session.commit()
            session.refresh(invoice)
            
            return invoice.to_dict()
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def update_invoice(self, invoice_id: int, invoice_data: Dict) -> Optional[Dict]:
        """Mettre à jour une facture"""
        session = self.get_session()
        try:
            invoice = session.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                return None
            
            # Vérifier l'unicité du numéro de facture si modifié
            if "invoiceNumber" in invoice_data and invoice_data["invoiceNumber"] != invoice.invoice_number:
                existing = session.query(Invoice).filter(Invoice.invoice_number == invoice_data["invoiceNumber"]).first()
                if existing:
                    raise ValueError("Le numéro de facture existe déjà")
                invoice.invoice_number = invoice_data["invoiceNumber"]
            
            # Mettre à jour les autres champs
            if "category" in invoice_data:
                invoice.category = invoice_data["category"]
            if "source" in invoice_data:
                invoice.source = invoice_data["source"]
            if "date" in invoice_data:
                invoice.date = datetime.fromisoformat(invoice_data["date"]).date()
            if "amount" in invoice_data:
                invoice.amount = invoice_data["amount"]
            if "currency" in invoice_data:
                invoice.currency = invoice_data["currency"]
            if "paymentType" in invoice_data:
                invoice.payment_type = invoice_data["paymentType"]
            if "buildingId" in invoice_data:
                invoice.building_id = invoice_data["buildingId"]
            if "unitId" in invoice_data:
                invoice.unit_id = invoice_data["unitId"]
            if "pdfFilename" in invoice_data:
                invoice.pdf_filename = invoice_data["pdfFilename"]
            if "pdfPath" in invoice_data:
                invoice.pdf_path = invoice_data["pdfPath"]
            if "notes" in invoice_data:
                invoice.notes = invoice_data["notes"]
            if "type" in invoice_data:
                invoice.type = invoice_data["type"]
            
            invoice.updated_at = datetime.utcnow()
            session.commit()
            
            return invoice.to_dict()
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def delete_invoice(self, invoice_id: int) -> bool:
        """Supprimer une facture"""
        session = self.get_session()
        try:
            invoice = session.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                return False
            
            session.delete(invoice)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def get_invoice_constants(self) -> Dict:
        """Récupérer les constantes pour les factures"""
        return {
            "categories": {
                "municipal_taxes": "Taxes municipales",
                "school_taxes": "Taxes scolaire",
                "insurance": "Assurance",
                "snow_removal": "Déneigement",
                "lawn_care": "Gazon",
                "management": "Gestion",
                "renovations": "Rénovations",
                "repairs": "Réparations",
                "wifi": "WiFi",
                "electricity": "Électricité",
                "other": "Autres"
            },
            "paymentTypes": {
                "cash": "Comptant",
                "check": "Chèque",
                "transfer": "Virement",
                "credit_card": "Carte de crédit",
                "other": "Autre"
            },
            "invoiceTypes": {
                "rental": "Immeuble en location",
                "construction": "Projet de construction"
            }
        }
    
    # ========================================
    # MÉTHODES MANQUANTES POUR LA VALIDATION
    # ========================================
    
    def create_assignment(self, assignment_data: Dict) -> Dict:
        """Créer une nouvelle assignation"""
        session = self.get_session()
        try:
            # Validation des clés étrangères
            tenant_id = assignment_data["tenantId"]
            unit_id = assignment_data["unitId"]
            
            # Vérifier que le locataire existe
            tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                raise ValueError(f"Le locataire avec l'ID {tenant_id} n'existe pas")
            
            # Vérifier que l'unité existe
            unit = session.query(Unit).filter(Unit.id == unit_id).first()
            if not unit:
                raise ValueError(f"L'unité avec l'ID {unit_id} n'existe pas")
            
            assignment = Assignment(
                tenant_id=tenant_id,
                unit_id=unit_id,
                move_in_date=self._safe_parse_date(assignment_data.get("moveInDate")),
                move_out_date=self._safe_parse_date(assignment_data.get("moveOutDate")),
                rent_amount=self._safe_parse_float(assignment_data.get("rentAmount"), 0.0),
                deposit_amount=self._safe_parse_float(assignment_data.get("depositAmount"), 0.0),
                lease_start_date=datetime.fromisoformat(assignment_data["leaseStartDate"]) if assignment_data.get("leaseStartDate") else None,
                lease_end_date=datetime.fromisoformat(assignment_data["leaseEndDate"]) if assignment_data.get("leaseEndDate") else None,
                rent_due_day=assignment_data.get("rentDueDay", 1),
                notes=assignment_data.get("notes", "")
            )
            
            session.add(assignment)
            session.commit()
            session.refresh(assignment)
            
            return assignment.to_dict()
        except ValueError as e:
            session.rollback()
            raise e
        except Exception as e:
            session.rollback()
            raise ValueError(f"Erreur lors de la création de l'assignation: {str(e)}")
        finally:
            session.close()
    
    def get_assignments(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupérer toutes les assignations"""
        session = self.get_session()
        try:
            assignments = session.query(Assignment).offset(skip).limit(limit).all()
            return [assignment.to_dict() for assignment in assignments]
        finally:
            session.close()
    
    def get_assignment(self, assignment_id: int) -> Optional[Dict]:
        """Récupérer une assignation par ID"""
        session = self.get_session()
        try:
            assignment = session.query(Assignment).filter(Assignment.id == assignment_id).first()
            return assignment.to_dict() if assignment else None
        finally:
            session.close()
    
    def delete_assignment(self, assignment_id: int) -> bool:
        """Supprimer une assignation"""
        session = self.get_session()
        try:
            assignment = session.query(Assignment).filter(Assignment.id == assignment_id).first()
            if not assignment:
                return False
            
            session.delete(assignment)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def get_building_reports(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupérer tous les rapports d'immeubles"""
        session = self.get_session()
        try:
            reports = session.query(BuildingReport).offset(skip).limit(limit).all()
            return [report.to_dict() for report in reports]
        finally:
            session.close()
    
    def get_building_report(self, report_id: int) -> Optional[Dict]:
        """Récupérer un rapport d'immeuble par ID"""
        session = self.get_session()
        try:
            report = session.query(BuildingReport).filter(BuildingReport.id == report_id).first()
            return report.to_dict() if report else None
        finally:
            session.close()
    
    def delete_building_report(self, report_id: int) -> bool:
        """Supprimer un rapport d'immeuble"""
        session = self.get_session()
        try:
            report = session.query(BuildingReport).filter(BuildingReport.id == report_id).first()
            if not report:
                return False
            
            session.delete(report)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def get_unit_reports(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupérer tous les rapports d'unités"""
        session = self.get_session()
        try:
            reports = session.query(UnitReport).offset(skip).limit(limit).all()
            return [report.to_dict() for report in reports]
        finally:
            session.close()
    
    def get_unit_report(self, report_id: int) -> Optional[Dict]:
        """Récupérer un rapport d'unité par ID"""
        session = self.get_session()
        try:
            report = session.query(UnitReport).filter(UnitReport.id == report_id).first()
            return report.to_dict() if report else None
        finally:
            session.close()
    
    def delete_unit_report(self, report_id: int) -> bool:
        """Supprimer un rapport d'unité"""
        session = self.get_session()
        try:
            report = session.query(UnitReport).filter(UnitReport.id == report_id).first()
            if not report:
                return False
            
            session.delete(report)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    
    def get_unit(self, unit_id: int) -> Optional[Dict]:
        """Récupérer une unité par ID"""
        session = self.get_session()
        try:
            unit = session.query(Unit).filter(Unit.id == unit_id).first()
            return unit.to_dict() if unit else None
        finally:
            session.close()
    
    def delete_unit(self, unit_id: int) -> bool:
        """Supprimer une unité"""
        session = self.get_session()
        try:
            unit = session.query(Unit).filter(Unit.id == unit_id).first()
            if not unit:
                return False
            
            session.delete(unit)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    # ========================================
    # MÉTHODES POUR LES CARDINALITÉS CORRIGÉES
    # ========================================
    
    def get_tenant_assignment(self, tenant_id: int) -> Optional[Dict]:
        """Récupérer l'assignation active d'un locataire (1:1)"""
        session = self.get_session()
        try:
            assignment = session.query(Assignment).filter(
                Assignment.tenant_id == tenant_id,
                Assignment.move_out_date.is_(None)  # Seulement les assignations actives
            ).first()
            return assignment.to_dict() if assignment else None
        finally:
            session.close()
    
    def get_unit_invoices(self, unit_id: str) -> List[Dict]:
        """Récupérer les factures d'une unité (N:1)"""
        session = self.get_session()
        try:
            invoices = session.query(Invoice).filter(Invoice.unit_id == unit_id).all()
            return [invoice.to_dict() for invoice in invoices]
        finally:
            session.close()
    
    def get_tenant_invoices(self, tenant_id: int) -> List[Dict]:
        """Récupérer les factures d'un locataire via son assignation active"""
        assignment = self.get_tenant_assignment(tenant_id)
        if assignment and assignment.get('unitId'):
            return self.get_unit_invoices(assignment['unitId'])
        return []
    
    def create_assignment_with_validation(self, assignment_data: Dict) -> Dict:
        """Créer une assignation avec validation des cardinalités"""
        session = self.get_session()
        try:
            tenant_id = assignment_data["tenantId"]
            
            # Vérifier qu'il n'y a pas déjà une assignation active pour ce locataire
            existing_assignment = session.query(Assignment).filter(
                Assignment.tenant_id == tenant_id,
                Assignment.move_out_date.is_(None)
            ).first()
            
            if existing_assignment:
                raise ValueError(f"Le locataire {tenant_id} a déjà une assignation active")
            
            # Créer la nouvelle assignation
            assignment = Assignment(
                tenant_id=tenant_id,
                building_id=assignment_data["buildingId"],
                unit_id=assignment_data["unitId"],
                unit_number=assignment_data.get("unitNumber"),
                unit_address=assignment_data.get("unitAddress"),
                move_in_date=self._safe_parse_date(assignment_data.get("moveInDate")),
                move_out_date=self._safe_parse_date(assignment_data.get("moveOutDate")),
                rent_amount=self._safe_parse_float(assignment_data.get("rentAmount"), 0.0),
                deposit_amount=self._safe_parse_float(assignment_data.get("depositAmount"), 0.0),
                lease_start_date=datetime.fromisoformat(assignment_data["leaseStartDate"]) if assignment_data.get("leaseStartDate") else None,
                lease_end_date=datetime.fromisoformat(assignment_data["leaseEndDate"]) if assignment_data.get("leaseEndDate") else None,
                rent_due_day=assignment_data.get("rentDueDay", 1),
                notes=assignment_data.get("notes", "")
            )
            
            session.add(assignment)
            session.commit()
            session.refresh(assignment)
            
            return assignment.to_dict()
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def move_out_tenant(self, tenant_id: int, move_out_date: str) -> bool:
        """Déménager un locataire (mettre à jour move_out_date)"""
        session = self.get_session()
        try:
            assignment = session.query(Assignment).filter(
                Assignment.tenant_id == tenant_id,
                Assignment.move_out_date.is_(None)
            ).first()
            
            if not assignment:
                return False
            
            assignment.move_out_date = datetime.fromisoformat(move_out_date).date()
            assignment.updated_at = datetime.utcnow()
            session.commit()
            
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def create_building_report(self, report_data: Dict) -> Dict:
        """Créer un nouveau rapport d'immeuble"""
        session = self.get_session()
        try:
            # Validation des clés étrangères
            building_id = report_data["buildingId"]
            
            # Vérifier que l'immeuble existe
            building = session.query(Building).filter(Building.id == building_id).first()
            if not building:
                raise ValueError(f"L'immeuble avec l'ID {building_id} n'existe pas")
            
            report = BuildingReport(
                building_id=building_id,
                year=report_data["year"],
                municipal_taxes=self._safe_parse_float(report_data.get("municipalTaxes"), 0.0),
                school_taxes=self._safe_parse_float(report_data.get("schoolTaxes"), 0.0),
                insurance=self._safe_parse_float(report_data.get("insurance"), 0.0),
                snow_removal=self._safe_parse_float(report_data.get("snowRemoval"), 0.0),
                lawn_care=self._safe_parse_float(report_data.get("lawnCare"), 0.0),
                management=self._safe_parse_float(report_data.get("management"), 0.0),
                renovations=self._safe_parse_float(report_data.get("renovations"), 0.0),
                repairs=self._safe_parse_float(report_data.get("repairs"), 0.0),
                wifi=self._safe_parse_float(report_data.get("wifi"), 0.0),
                electricity=self._safe_parse_float(report_data.get("electricity"), 0.0),
                other=self._safe_parse_float(report_data.get("other"), 0.0),
                notes=report_data.get("notes", "")
            )
            
            session.add(report)
            session.commit()
            session.refresh(report)
            
            return report.to_dict()
        except ValueError as e:
            session.rollback()
            raise e
        except Exception as e:
            session.rollback()
            raise ValueError(f"Erreur lors de la création du rapport d'immeuble: {str(e)}")
        finally:
            session.close()
    
    def update_building_report(self, report_id: int, report_data: Dict) -> Dict:
        """Mettre à jour un rapport d'immeuble"""
        session = self.get_session()
        try:
            report = session.query(BuildingReport).filter(BuildingReport.id == report_id).first()
            if not report:
                return None
            
            # Mettre à jour les champs de manière sécurisée
            allowed_fields = [
                'year', 'municipal_taxes', 'school_taxes', 'insurance', 
                'snow_removal', 'lawn_care', 'management', 'renovations', 
                'repairs', 'wifi', 'electricity', 'other', 'notes'
            ]
            
            for key, value in report_data.items():
                if key in allowed_fields and hasattr(report, key):
                    setattr(report, key, value)
            
            session.commit()
            session.refresh(report)
            
            return report.to_dict()
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            raise ValueError(f"Erreur lors de la suppression: {str(e)}")
        finally:
            session.close()
    
    def create_unit_report(self, report_data: Dict) -> Dict:
        """Créer un nouveau rapport d'unité"""
        session = self.get_session()
        try:
            # Validation des clés étrangères
            unit_id = report_data["unitId"]
            
            # Vérifier que l'unité existe
            unit = session.query(Unit).filter(Unit.id == unit_id).first()
            if not unit:
                raise ValueError(f"L'unité avec l'ID {unit_id} n'existe pas")
            
            report = UnitReport(
                unit_id=unit_id,
                year=report_data["year"],
                month=report_data["month"],
                tenant_name=report_data.get("tenantName"),
                payment_method=report_data.get("paymentMethod"),
                is_heated_lit=report_data.get("isHeatedLit", False),
                is_furnished=report_data.get("isFurnished", False),
                wifi_included=report_data.get("wifiIncluded", False),
                rent_amount=self._safe_parse_float(report_data.get("rentAmount"), 0.0),
                start_date=self._safe_parse_date(report_data.get("startDate")),
                end_date=self._safe_parse_date(report_data.get("endDate")),
                notes=report_data.get("notes", "")
            )
            
            session.add(report)
            session.commit()
            session.refresh(report)
            
            return report.to_dict()
        except ValueError as e:
            session.rollback()
            raise e
        except Exception as e:
            session.rollback()
            raise ValueError(f"Erreur lors de la création du rapport d'unité: {str(e)}")
        finally:
            session.close()
    

# Instance globale du service
db_service = DatabaseService()
