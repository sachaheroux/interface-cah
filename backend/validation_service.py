#!/usr/bin/env python3
"""
Service de validation et de cohérence des données pour Interface CAH
"""

import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from database import db_manager
from database_service_francais import db_service_francais as db_service

class ValidationLevel(Enum):
    """Niveaux de validation"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationResult:
    """Résultat d'une validation"""
    level: ValidationLevel
    message: str
    table: str
    record_id: Optional[int] = None
    field: Optional[str] = None
    suggested_fix: Optional[str] = None

class DataValidator:
    """Validateur de données pour Interface CAH"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def validate_all(self) -> List[ValidationResult]:
        """Valider toutes les données de la base"""
        self.results = []
        
        print("🔍 Début de la validation complète des données...")
        
        # Valider chaque table
        self._validate_buildings()
        self._validate_tenants()
        self._validate_assignments()
        self._validate_building_reports()
        self._validate_unit_reports()
        self._validate_transactions()
        
        # Valider les relations entre tables
        self._validate_relationships()
        
        # Valider l'intégrité globale
        self._validate_global_integrity()
        
        print(f"✅ Validation terminée : {len(self.results)} problèmes trouvés")
        return self.results
    
    def _validate_buildings(self):
        """Valider les immeubles"""
        print("  🏢 Validation des immeubles...")
        
        try:
            buildings = db_service.get_buildings()
            
            for building in buildings:
                building_id = building.get('id')
                
                # Validation des champs obligatoires
                if not building.get('name'):
                    self._add_result(ValidationLevel.ERROR, "Nom d'immeuble manquant", "buildings", building_id, "name")
                
                if not building.get('type'):
                    self._add_result(ValidationLevel.ERROR, "Type d'immeuble manquant", "buildings", building_id, "type")
                
                # Validation des valeurs numériques
                if building.get('units') is not None and building['units'] < 0:
                    self._add_result(ValidationLevel.ERROR, "Nombre d'unités négatif", "buildings", building_id, "units")
                
                if building.get('floors') is not None and building['floors'] < 1:
                    self._add_result(ValidationLevel.ERROR, "Nombre d'étages invalide", "buildings", building_id, "floors")
                
                if building.get('yearBuilt') is not None:
                    current_year = datetime.now().year
                    if building['yearBuilt'] < 1800 or building['yearBuilt'] > current_year + 5:
                        self._add_result(ValidationLevel.WARNING, f"Année de construction suspecte: {building['yearBuilt']}", "buildings", building_id, "yearBuilt")
                
                # Validation de l'adresse
                address = building.get('address', {})
                if isinstance(address, dict):
                    if not address.get('street'):
                        self._add_result(ValidationLevel.WARNING, "Rue manquante dans l'adresse", "buildings", building_id, "address.street")
                    
                    if not address.get('city'):
                        self._add_result(ValidationLevel.WARNING, "Ville manquante dans l'adresse", "buildings", building_id, "address.city")
                
                # Validation des données JSON
                self._validate_json_fields(building, "buildings", building_id)
                
        except Exception as e:
            self._add_result(ValidationLevel.CRITICAL, f"Erreur lors de la validation des immeubles: {e}", "buildings")
    
    def _validate_tenants(self):
        """Valider les locataires"""
        print("  👥 Validation des locataires...")
        
        try:
            tenants = db_service.get_tenants()
            
            for tenant in tenants:
                tenant_id = tenant.get('id')
                
                # Validation des champs obligatoires
                if not tenant.get('firstName'):
                    self._add_result(ValidationLevel.ERROR, "Prénom manquant", "tenants", tenant_id, "firstName")
                
                if not tenant.get('lastName'):
                    self._add_result(ValidationLevel.ERROR, "Nom manquant", "tenants", tenant_id, "lastName")
                
                # Validation de l'email
                email = tenant.get('email')
                if email and not self._is_valid_email(email):
                    self._add_result(ValidationLevel.ERROR, f"Email invalide: {email}", "tenants", tenant_id, "email")
                
                # Validation du téléphone
                phone = tenant.get('phone')
                if phone and not self._is_valid_phone(phone):
                    self._add_result(ValidationLevel.WARNING, f"Format de téléphone suspect: {phone}", "tenants", tenant_id, "phone")
                
                # Validation des dates
                if tenant.get('moveInDate'):
                    if not self._is_valid_date(tenant['moveInDate']):
                        self._add_result(ValidationLevel.ERROR, "Date d'emménagement invalide", "tenants", tenant_id, "moveInDate")
                
                if tenant.get('moveOutDate'):
                    if not self._is_valid_date(tenant['moveOutDate']):
                        self._add_result(ValidationLevel.ERROR, "Date de départ invalide", "tenants", tenant_id, "moveOutDate")
                
                # Validation des données JSON
                self._validate_json_fields(tenant, "tenants", tenant_id)
                
        except Exception as e:
            self._add_result(ValidationLevel.CRITICAL, f"Erreur lors de la validation des locataires: {e}", "tenants")
    
    def _validate_assignments(self):
        """Valider les assignations locataire-unité"""
        print("  🔗 Validation des assignations...")
        
        try:
            assignments = db_service.get_assignments()
            
            for assignment in assignments:
                assignment_id = assignment.get('id')
                
                # Validation des clés étrangères
                if not assignment.get('tenantId'):
                    self._add_result(ValidationLevel.ERROR, "ID locataire manquant", "assignments", assignment_id, "tenantId")
                else:
                    # Vérifier que le locataire existe
                    tenant = db_service.get_tenant(assignment['tenantId'])
                    if not tenant:
                        self._add_result(ValidationLevel.ERROR, f"Locataire inexistant (ID: {assignment['tenantId']})", "assignments", assignment_id, "tenantId")
                
                if not assignment.get('unitId'):
                    self._add_result(ValidationLevel.ERROR, "ID unité manquant", "assignments", assignment_id, "unitId")
                else:
                    # Vérifier que l'unité existe
                    unit = db_service.get_unit(assignment['unitId'])
                    if not unit:
                        self._add_result(ValidationLevel.ERROR, f"Unité inexistante (ID: {assignment['unitId']})", "assignments", assignment_id, "unitId")
                
                # Validation des dates
                if assignment.get('startDate'):
                    if not self._is_valid_date(assignment['startDate']):
                        self._add_result(ValidationLevel.ERROR, "Date de début invalide", "assignments", assignment_id, "startDate")
                
                if assignment.get('endDate'):
                    if not self._is_valid_date(assignment['endDate']):
                        self._add_result(ValidationLevel.ERROR, "Date de fin invalide", "assignments", assignment_id, "endDate")
                
                # Validation de la cohérence des dates
                if assignment.get('startDate') and assignment.get('endDate'):
                    if assignment['startDate'] > assignment['endDate']:
                        self._add_result(ValidationLevel.ERROR, "Date de début postérieure à la date de fin", "assignments", assignment_id)
                
        except Exception as e:
            self._add_result(ValidationLevel.CRITICAL, f"Erreur lors de la validation des assignations: {e}", "assignments")
    
    def _validate_building_reports(self):
        """Valider les rapports d'immeubles"""
        print("  📊 Validation des rapports d'immeubles...")
        
        try:
            reports = db_service.get_building_reports()
            
            for report in reports:
                report_id = report.get('id')
                
                # Validation des clés étrangères
                if not report.get('buildingId'):
                    self._add_result(ValidationLevel.ERROR, "ID immeuble manquant", "building_reports", report_id, "buildingId")
                else:
                    building = db_service.get_building(report['buildingId'])
                    if not building:
                        self._add_result(ValidationLevel.ERROR, f"Immeuble inexistant (ID: {report['buildingId']})", "building_reports", report_id, "buildingId")
                
                # Validation des champs obligatoires
                if not report.get('title'):
                    self._add_result(ValidationLevel.ERROR, "Titre de rapport manquant", "building_reports", report_id, "title")
                
                if not report.get('type'):
                    self._add_result(ValidationLevel.ERROR, "Type de rapport manquant", "building_reports", report_id, "type")
                
                # Validation des données JSON
                self._validate_json_fields(report, "building_reports", report_id)
                
        except Exception as e:
            self._add_result(ValidationLevel.CRITICAL, f"Erreur lors de la validation des rapports d'immeubles: {e}", "building_reports")
    
    def _validate_unit_reports(self):
        """Valider les rapports d'unités"""
        print("  🏠 Validation des rapports d'unités...")
        
        try:
            reports = db_service.get_unit_reports()
            
            for report in reports:
                report_id = report.get('id')
                
                # Validation des clés étrangères
                if not report.get('unitId'):
                    self._add_result(ValidationLevel.ERROR, "ID unité manquant", "unit_reports", report_id, "unitId")
                else:
                    unit = db_service.get_unit(report['unitId'])
                    if not unit:
                        self._add_result(ValidationLevel.ERROR, f"Unité inexistante (ID: {report['unitId']})", "unit_reports", report_id, "unitId")
                
                # Validation des champs obligatoires
                if not report.get('title'):
                    self._add_result(ValidationLevel.ERROR, "Titre de rapport manquant", "unit_reports", report_id, "title")
                
                if not report.get('type'):
                    self._add_result(ValidationLevel.ERROR, "Type de rapport manquant", "unit_reports", report_id, "type")
                
                # Validation des données JSON
                self._validate_json_fields(report, "unit_reports", report_id)
                
        except Exception as e:
            self._add_result(ValidationLevel.CRITICAL, f"Erreur lors de la validation des rapports d'unités: {e}", "unit_reports")
    
    def _validate_invoices(self):
        """Valider les factures"""
        print("  💰 Validation des factures...")
        
        try:
            invoices = db_service.get_invoices()
            
            for invoice in invoices:
                invoice_id = invoice.get('id')
                
                # Validation des champs obligatoires
                if not invoice.get('invoiceNumber'):
                    self._add_result(ValidationLevel.ERROR, "Numéro de facture manquant", "invoices", invoice_id, "invoiceNumber")
                
                if not invoice.get('category'):
                    self._add_result(ValidationLevel.ERROR, "Catégorie de facture manquante", "invoices", invoice_id, "category")
                
                if not invoice.get('amount'):
                    self._add_result(ValidationLevel.ERROR, "Montant de facture manquant", "invoices", invoice_id, "amount")
                elif invoice['amount'] <= 0:
                    self._add_result(ValidationLevel.ERROR, "Montant de facture invalide", "invoices", invoice_id, "amount")
                
                # Validation des clés étrangères
                if invoice.get('buildingId'):
                    building = db_service.get_building(invoice['buildingId'])
                    if not building:
                        self._add_result(ValidationLevel.ERROR, f"Immeuble inexistant (ID: {invoice['buildingId']})", "invoices", invoice_id, "buildingId")
                
                # Validation des dates
                if invoice.get('date'):
                    if not self._is_valid_date(invoice['date']):
                        self._add_result(ValidationLevel.ERROR, "Date de facture invalide", "invoices", invoice_id, "date")
                
                # Validation des données JSON
                self._validate_json_fields(invoice, "invoices", invoice_id)
                
        except Exception as e:
            self._add_result(ValidationLevel.CRITICAL, f"Erreur lors de la validation des factures: {e}", "invoices")
    
    def _validate_relationships(self):
        """Valider les relations entre tables"""
        print("  🔗 Validation des relations...")
        
        try:
            # Vérifier les assignations orphelines
            assignments = db_service.get_assignments()
            for assignment in assignments:
                tenant_id = assignment.get('tenantId')
                unit_id = assignment.get('unitId')
                
                if tenant_id and unit_id:
                    tenant = db_service.get_tenant(tenant_id)
                    unit = db_service.get_unit(unit_id)
                    
                    if not tenant:
                        self._add_result(ValidationLevel.ERROR, f"Assignation orpheline - locataire inexistant (ID: {tenant_id})", "assignments", assignment.get('id'))
                    
                    if not unit:
                        self._add_result(ValidationLevel.ERROR, f"Assignation orpheline - unité inexistante (ID: {unit_id})", "assignments", assignment.get('id'))
            
            # Vérifier les rapports orphelins
            building_reports = db_service.get_building_reports()
            for report in building_reports:
                building_id = report.get('buildingId')
                if building_id:
                    building = db_service.get_building(building_id)
                    if not building:
                        self._add_result(ValidationLevel.ERROR, f"Rapport d'immeuble orphelin - immeuble inexistant (ID: {building_id})", "building_reports", report.get('id'))
            
            unit_reports = db_service.get_unit_reports()
            for report in unit_reports:
                unit_id = report.get('unitId')
                if unit_id:
                    unit = db_service.get_unit(unit_id)
                    if not unit:
                        self._add_result(ValidationLevel.ERROR, f"Rapport d'unité orphelin - unité inexistante (ID: {unit_id})", "unit_reports", report.get('id'))
            
        except Exception as e:
            self._add_result(ValidationLevel.CRITICAL, f"Erreur lors de la validation des relations: {e}")
    
    def _validate_global_integrity(self):
        """Valider l'intégrité globale de la base de données"""
        print("  🌐 Validation de l'intégrité globale...")
        
        try:
            # Vérifier les contraintes de clés étrangères
            if db_manager.connect():
                cursor = db_manager.connection.cursor()
                cursor.execute("PRAGMA foreign_key_check")
                fk_errors = cursor.fetchall()
                
                if fk_errors:
                    for error in fk_errors:
                        self._add_result(ValidationLevel.CRITICAL, f"Violation de clé étrangère: {error}", "database")
                else:
                    self._add_result(ValidationLevel.INFO, "Aucune violation de clé étrangère détectée", "database")
                
                db_manager.disconnect()
            
            # Vérifier la cohérence des données
            self._check_data_consistency()
            
        except Exception as e:
            self._add_result(ValidationLevel.CRITICAL, f"Erreur lors de la validation globale: {e}")
    
    def _check_data_consistency(self):
        """Vérifier la cohérence des données"""
        try:
            # Vérifier que les unités appartiennent à des immeubles existants
            buildings = db_service.get_buildings()
            building_ids = {b['id'] for b in buildings}
            
            # Note: Cette vérification nécessiterait une méthode get_units() dans db_service
            # Pour l'instant, on se contente de vérifier les assignations
            
        except Exception as e:
            self._add_result(ValidationLevel.WARNING, f"Impossible de vérifier la cohérence des données: {e}")
    
    def _validate_json_fields(self, record: Dict, table: str, record_id: int):
        """Valider les champs JSON d'un enregistrement"""
        json_fields = ['address', 'characteristics', 'financials', 'contacts', 'unitData', 'metadata']
        
        for field in json_fields:
            if field in record and record[field]:
                try:
                    if isinstance(record[field], str):
                        json.loads(record[field])
                    elif isinstance(record[field], dict):
                        # Déjà un dict, c'est bon
                        pass
                    else:
                        self._add_result(ValidationLevel.WARNING, f"Champ JSON invalide: {field}", table, record_id, field)
                except json.JSONDecodeError:
                    self._add_result(ValidationLevel.ERROR, f"JSON invalide dans le champ: {field}", table, record_id, field)
    
    def _is_valid_email(self, email: str) -> bool:
        """Valider un email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Valider un numéro de téléphone"""
        import re
        # Pattern pour téléphone canadien/américain
        pattern = r'^[\+]?[1]?[\s\-\.]?[\(]?[0-9]{3}[\)]?[\s\-\.]?[0-9]{3}[\s\-\.]?[0-9]{4}$'
        return re.match(pattern, phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) is not None
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Valider une date"""
        try:
            if isinstance(date_str, str):
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except:
            return False
    
    def _add_result(self, level: ValidationLevel, message: str, table: str = "unknown", record_id: Optional[int] = None, field: Optional[str] = None, suggested_fix: Optional[str] = None):
        """Ajouter un résultat de validation"""
        result = ValidationResult(
            level=level,
            message=message,
            table=table,
            record_id=record_id,
            field=field,
            suggested_fix=suggested_fix
        )
        self.results.append(result)
        
        # Afficher le résultat
        icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "🚨"}[level.value]
        print(f"    {icon} {message}")

class DataConsistencyChecker:
    """Vérificateur de cohérence des données"""
    
    @staticmethod
    def check_orphaned_records() -> List[Dict]:
        """Vérifier les enregistrements orphelins"""
        issues = []
        
        try:
            # Vérifier les assignations orphelines
            assignments = db_service.get_assignments()
            for assignment in assignments:
                tenant_id = assignment.get('tenantId')
                unit_id = assignment.get('unitId')
                
                if tenant_id:
                    tenant = db_service.get_tenant(tenant_id)
                    if not tenant:
                        issues.append({
                            "type": "orphaned_assignment",
                            "table": "assignments",
                            "id": assignment.get('id'),
                            "message": f"Assignation orpheline - locataire {tenant_id} inexistant"
                        })
                
                if unit_id:
                    unit = db_service.get_unit(unit_id)
                    if not unit:
                        issues.append({
                            "type": "orphaned_assignment",
                            "table": "assignments",
                            "id": assignment.get('id'),
                            "message": f"Assignation orpheline - unité {unit_id} inexistante"
                        })
            
        except Exception as e:
            issues.append({
                "type": "check_error",
                "message": f"Erreur lors de la vérification des orphelins: {e}"
            })
        
        return issues

# Instance globale du validateur
data_validator = DataValidator()
consistency_checker = DataConsistencyChecker()

def get_data_validator():
    """Obtenir l'instance du validateur de données"""
    return data_validator

def get_consistency_checker():
    """Obtenir l'instance du vérificateur de cohérence"""
    return consistency_checker
