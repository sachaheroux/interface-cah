#!/usr/bin/env python3
"""
Service de base de données en français pour Interface CAH
Utilise les nouveaux modèles français
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json
import os
import platform

from database import db_manager
from models_francais import Immeuble, Locataire, Unite, Bail, Facture, RapportImmeuble

class DatabaseServiceFrancais:
    """Service principal pour les opérations de base de données en français"""
    
    def __init__(self):
        self.engine = db_manager.engine
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Obtenir une session de base de données"""
        return self.SessionLocal()
    
    # ========================================
    # OPÉRATIONS POUR LES IMMEUBLES
    # ========================================
    
    def get_buildings(self) -> List[Dict[str, Any]]:
        """Récupérer tous les immeubles"""
        try:
            with self.get_session() as session:
                buildings = session.query(Immeuble).all()
                return [building.to_dict() for building in buildings]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des immeubles: {e}")
            raise e
    
    def get_building(self, building_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer un immeuble par ID"""
        try:
            with self.get_session() as session:
                building = session.query(Immeuble).filter(Immeuble.id_immeuble == building_id).first()
                return building.to_dict() if building else None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de l'immeuble {building_id}: {e}")
            raise e
    
    def create_building(self, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer un nouvel immeuble"""
        try:
            with self.get_session() as session:
                # Convertir les données du frontend vers le modèle français
                building = Immeuble(
                    nom_immeuble=building_data.get('name', ''),
                    adresse=building_data.get('address', {}).get('street', '') if isinstance(building_data.get('address'), dict) else building_data.get('address', ''),
                    ville=building_data.get('address', {}).get('city', '') if isinstance(building_data.get('address'), dict) else '',
                    province=building_data.get('address', {}).get('province', '') if isinstance(building_data.get('address'), dict) else '',
                    code_postal=building_data.get('address', {}).get('postalCode', '') if isinstance(building_data.get('address'), dict) else '',
                    pays=building_data.get('address', {}).get('country', 'Canada') if isinstance(building_data.get('address'), dict) else 'Canada',
                    nbr_unite=building_data.get('units', 1),
                    annee_construction=building_data.get('yearBuilt'),
                    prix_achete=building_data.get('financials', {}).get('purchasePrice', 0) if isinstance(building_data.get('financials'), dict) else 0,
                    mise_de_fond=building_data.get('financials', {}).get('downPayment', 0) if isinstance(building_data.get('financials'), dict) else 0,
                    taux_interet=building_data.get('financials', {}).get('interestRate', 0) if isinstance(building_data.get('financials'), dict) else 0,
                    valeur_actuel=building_data.get('financials', {}).get('currentValue', 0) if isinstance(building_data.get('financials'), dict) else 0,
                    proprietaire=building_data.get('contacts', {}).get('owner', '') if isinstance(building_data.get('contacts'), dict) else '',
                    banque=building_data.get('contacts', {}).get('bank', '') if isinstance(building_data.get('contacts'), dict) else '',
                    contracteur=building_data.get('contacts', {}).get('contractor', '') if isinstance(building_data.get('contacts'), dict) else '',
                    notes=building_data.get('notes', '')
                )
                
                session.add(building)
                session.commit()
                session.refresh(building)
                
                print(f"✅ Immeuble créé: {building.nom_immeuble} (ID: {building.id_immeuble})")
                return building.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'immeuble: {e}")
            raise e
    
    def update_building(self, building_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mettre à jour un immeuble"""
        try:
            with self.get_session() as session:
                building = session.query(Immeuble).filter(Immeuble.id_immeuble == building_id).first()
                if not building:
                    return None
                
                # Mettre à jour les champs
                if 'name' in update_data:
                    building.nom_immeuble = update_data['name']
                if 'address' in update_data and isinstance(update_data['address'], dict):
                    addr = update_data['address']
                    building.adresse = addr.get('street', building.adresse)
                    building.ville = addr.get('city', building.ville)
                    building.province = addr.get('province', building.province)
                    building.code_postal = addr.get('postalCode', building.code_postal)
                    building.pays = addr.get('country', building.pays)
                if 'units' in update_data:
                    building.nbr_unite = update_data['units']
                if 'yearBuilt' in update_data:
                    building.annee_construction = update_data['yearBuilt']
                if 'financials' in update_data and isinstance(update_data['financials'], dict):
                    fin = update_data['financials']
                    building.prix_achete = fin.get('purchasePrice', building.prix_achete)
                    building.mise_de_fond = fin.get('downPayment', building.mise_de_fond)
                    building.taux_interet = fin.get('interestRate', building.taux_interet)
                    building.valeur_actuel = fin.get('currentValue', building.valeur_actuel)
                if 'contacts' in update_data and isinstance(update_data['contacts'], dict):
                    cont = update_data['contacts']
                    building.proprietaire = cont.get('owner', building.proprietaire)
                    building.banque = cont.get('bank', building.banque)
                    building.contracteur = cont.get('contractor', building.contracteur)
                if 'notes' in update_data:
                    building.notes = update_data['notes']
                
                building.date_modification = datetime.utcnow()
                session.commit()
                
                print(f"✅ Immeuble mis à jour: {building.nom_immeuble} (ID: {building.id_immeuble})")
                return building.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de l'immeuble {building_id}: {e}")
            raise e
    
    def delete_building(self, building_id: int) -> bool:
        """Supprimer un immeuble"""
        try:
            with self.get_session() as session:
                building = session.query(Immeuble).filter(Immeuble.id_immeuble == building_id).first()
                if not building:
                    return False
                
                session.delete(building)
                session.commit()
                
                print(f"✅ Immeuble supprimé: {building.nom_immeuble} (ID: {building.id_immeuble})")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de l'immeuble {building_id}: {e}")
            raise e
    
    # ========================================
    # OPÉRATIONS POUR LES UNITÉS
    # ========================================
    
    def get_units(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Récupérer toutes les unités"""
        try:
            with self.get_session() as session:
                units = session.query(Unite).offset(skip).limit(limit).all()
                return [unit.to_dict() for unit in units]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des unités: {e}")
            raise e
    
    def get_unit(self, unit_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer une unité par ID"""
        try:
            with self.get_session() as session:
                unit = session.query(Unite).filter(Unite.id_unite == unit_id).first()
                return unit.to_dict() if unit else None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de l'unité {unit_id}: {e}")
            raise e
    
    def get_units_by_building(self, building_id: int) -> List[Dict[str, Any]]:
        """Récupérer toutes les unités d'un immeuble"""
        try:
            with self.get_session() as session:
                units = session.query(Unite).filter(Unite.id_immeuble == building_id).all()
                return [unit.to_dict() for unit in units]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des unités de l'immeuble {building_id}: {e}")
            raise e
    
    def create_unit(self, unit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer une nouvelle unité"""
        try:
            with self.get_session() as session:
                unit = Unite(
                    id_immeuble=unit_data.get('buildingId'),
                    adresse_unite=unit_data.get('unitAddress', ''),
                    type=unit_data.get('type', '4 1/2'),
                    nbr_chambre=unit_data.get('bedrooms', 1),
                    nbr_salle_de_bain=unit_data.get('bathrooms', 1),
                    notes=unit_data.get('notes', '')
                )
                
                session.add(unit)
                session.commit()
                session.refresh(unit)
                
                print(f"✅ Unité créée: {unit.adresse_unite} (ID: {unit.id_unite})")
                return unit.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'unité: {e}")
            raise e
    
    def update_unit(self, unit_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mettre à jour une unité"""
        try:
            with self.get_session() as session:
                unit = session.query(Unite).filter(Unite.id_unite == unit_id).first()
                if not unit:
                    return None
                
                # Mettre à jour les champs
                if 'unitAddress' in update_data:
                    unit.adresse_unite = update_data['unitAddress']
                if 'type' in update_data:
                    unit.type = update_data['type']
                if 'bedrooms' in update_data:
                    unit.nbr_chambre = update_data['bedrooms']
                if 'bathrooms' in update_data:
                    unit.nbr_salle_de_bain = update_data['bathrooms']
                if 'notes' in update_data:
                    unit.notes = update_data['notes']
                
                unit.date_modification = datetime.utcnow()
                session.commit()
                
                print(f"✅ Unité mise à jour: {unit.adresse_unite} (ID: {unit.id_unite})")
                return unit.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de l'unité {unit_id}: {e}")
            raise e
    
    def delete_unit(self, unit_id: int) -> bool:
        """Supprimer une unité"""
        try:
            with self.get_session() as session:
                unit = session.query(Unite).filter(Unite.id_unite == unit_id).first()
                if not unit:
                    return False
                
                session.delete(unit)
                session.commit()
                
                print(f"✅ Unité supprimée: {unit.adresse_unite} (ID: {unit.id_unite})")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de l'unité {unit_id}: {e}")
            raise e
    
    # ========================================
    # OPÉRATIONS POUR LES LOCATAIRES
    # ========================================
    
    def get_tenants(self) -> List[Dict[str, Any]]:
        """Récupérer tous les locataires"""
        try:
            with self.get_session() as session:
                tenants = session.query(Locataire).all()
                return [tenant.to_dict() for tenant in tenants]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des locataires: {e}")
            raise e
    
    def get_tenant(self, tenant_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer un locataire par ID"""
        try:
            with self.get_session() as session:
                tenant = session.query(Locataire).filter(Locataire.id_locataire == tenant_id).first()
                return tenant.to_dict() if tenant else None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du locataire {tenant_id}: {e}")
            raise e
    
    def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer un nouveau locataire"""
        try:
            with self.get_session() as session:
                # Diviser le nom complet en nom et prénom
                full_name = tenant_data.get('name', '')
                name_parts = full_name.split(' ', 1)
                nom = name_parts[0] if name_parts else ''
                prenom = name_parts[1] if len(name_parts) > 1 else ''
                
                tenant = Locataire(
                    id_unite=tenant_data.get('unitId'),
                    nom=nom,
                    prenom=prenom,
                    email=tenant_data.get('email', ''),
                    telephone=tenant_data.get('phone', ''),
                    statut=tenant_data.get('status', 'actif'),
                    notes=tenant_data.get('notes', '')
                )
                
                session.add(tenant)
                session.commit()
                session.refresh(tenant)
                
                print(f"✅ Locataire créé: {nom} {prenom} (ID: {tenant.id_locataire})")
                return tenant.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la création du locataire: {e}")
            raise e
    
    def update_tenant(self, tenant_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mettre à jour un locataire"""
        try:
            with self.get_session() as session:
                tenant = session.query(Locataire).filter(Locataire.id_locataire == tenant_id).first()
                if not tenant:
                    return None
                
                # Mettre à jour les champs
                if 'name' in update_data:
                    full_name = update_data['name']
                    name_parts = full_name.split(' ', 1)
                    tenant.nom = name_parts[0] if name_parts else ''
                    tenant.prenom = name_parts[1] if len(name_parts) > 1 else ''
                if 'email' in update_data:
                    tenant.email = update_data['email']
                if 'phone' in update_data:
                    tenant.telephone = update_data['phone']
                if 'status' in update_data:
                    tenant.statut = update_data['status']
                if 'notes' in update_data:
                    tenant.notes = update_data['notes']
                
                tenant.date_modification = datetime.utcnow()
                session.commit()
                
                print(f"✅ Locataire mis à jour: {tenant.nom} {tenant.prenom} (ID: {tenant.id_locataire})")
                return tenant.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du locataire {tenant_id}: {e}")
            raise e
    
    def delete_tenant(self, tenant_id: int) -> bool:
        """Supprimer un locataire"""
        try:
            with self.get_session() as session:
                tenant = session.query(Locataire).filter(Locataire.id_locataire == tenant_id).first()
                if not tenant:
                    return False
                
                session.delete(tenant)
                session.commit()
                
                print(f"✅ Locataire supprimé: {tenant.nom} {tenant.prenom} (ID: {tenant.id_locataire})")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du locataire {tenant_id}: {e}")
            raise e
    
    # ========================================
    # OPÉRATIONS POUR LES FACTURES
    # ========================================
    
    def get_invoices(self) -> List[Dict[str, Any]]:
        """Récupérer toutes les factures"""
        try:
            with self.get_session() as session:
                invoices = session.query(Facture).all()
                return [invoice.to_dict() for invoice in invoices]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des factures: {e}")
            raise e
    
    def get_invoice(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer une facture par ID"""
        try:
            with self.get_session() as session:
                invoice = session.query(Facture).filter(Facture.id_facture == invoice_id).first()
                return invoice.to_dict() if invoice else None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de la facture {invoice_id}: {e}")
            raise e
    
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer une nouvelle facture"""
        try:
            with self.get_session() as session:
                invoice = Facture(
                    id_immeuble=invoice_data.get('buildingId'),
                    categorie=invoice_data.get('category', ''),
                    montant=invoice_data.get('amount', 0),
                    date=datetime.strptime(invoice_data.get('date', ''), '%Y-%m-%d').date() if invoice_data.get('date') else datetime.now().date(),
                    no_facture=invoice_data.get('invoiceNumber', ''),
                    source=invoice_data.get('source', ''),
                    pdf_facture=invoice_data.get('pdfFilename', ''),
                    type_paiement=invoice_data.get('paymentType', ''),
                    notes=invoice_data.get('notes', '')
                )
                
                session.add(invoice)
                session.commit()
                session.refresh(invoice)
                
                print(f"✅ Facture créée: {invoice.no_facture} (ID: {invoice.id_facture})")
                return invoice.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la création de la facture: {e}")
            raise e
    
    def update_invoice(self, invoice_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mettre à jour une facture"""
        try:
            with self.get_session() as session:
                invoice = session.query(Facture).filter(Facture.id_facture == invoice_id).first()
                if not invoice:
                    return None
                
                # Mettre à jour les champs
                if 'category' in update_data:
                    invoice.categorie = update_data['category']
                if 'amount' in update_data:
                    invoice.montant = update_data['amount']
                if 'date' in update_data:
                    invoice.date = datetime.strptime(update_data['date'], '%Y-%m-%d').date()
                if 'invoiceNumber' in update_data:
                    invoice.no_facture = update_data['invoiceNumber']
                if 'source' in update_data:
                    invoice.source = update_data['source']
                if 'pdfFilename' in update_data:
                    invoice.pdf_facture = update_data['pdfFilename']
                if 'paymentType' in update_data:
                    invoice.type_paiement = update_data['paymentType']
                if 'notes' in update_data:
                    invoice.notes = update_data['notes']
                
                invoice.date_modification = datetime.utcnow()
                session.commit()
                
                print(f"✅ Facture mise à jour: {invoice.no_facture} (ID: {invoice.id_facture})")
                return invoice.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de la facture {invoice_id}: {e}")
            raise e
    
    def delete_invoice(self, invoice_id: int) -> bool:
        """Supprimer une facture"""
        try:
            with self.get_session() as session:
                invoice = session.query(Facture).filter(Facture.id_facture == invoice_id).first()
                if not invoice:
                    return False
                
                session.delete(invoice)
                session.commit()
                
                print(f"✅ Facture supprimée: {invoice.no_facture} (ID: {invoice.id_facture})")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de la facture {invoice_id}: {e}")
            raise e
    
    # ========================================
    # OPÉRATIONS POUR LES ASSIGNATIONS (COMPATIBILITÉ)
    # ========================================
    
    def get_assignments(self) -> List[Dict[str, Any]]:
        """Récupérer toutes les assignations (compatibilité avec l'ancien système)"""
        try:
            with self.get_session() as session:
                # Pour l'instant, retourner une liste vide car nous n'avons pas encore de table assignations
                # Dans le nouveau système, les locataires sont directement liés aux unités
                return []
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des assignations: {e}")
            raise e
    
    def create_assignment_with_validation(self, assignment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer une assignation avec validation (compatibilité)"""
        try:
            # Dans le nouveau système, nous créons directement le locataire avec son unité
            # Cette méthode est maintenue pour la compatibilité
            return {"id": 1, "message": "Assignation créée (nouveau système)"}
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'assignation: {e}")
            raise e
    
    def delete_assignment(self, assignment_id: int) -> bool:
        """Supprimer une assignation (compatibilité)"""
        try:
            # Dans le nouveau système, nous supprimons directement le locataire
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de l'assignation {assignment_id}: {e}")
            raise e
    
    def delete_tenant_assignments(self, tenant_id: int) -> bool:
        """Supprimer toutes les assignations d'un locataire (compatibilité)"""
        try:
            # Dans le nouveau système, nous supprimons directement le locataire
            return self.delete_tenant(tenant_id)
        except Exception as e:
            print(f"❌ Erreur lors de la suppression des assignations du locataire {tenant_id}: {e}")
            raise e
    
    # ========================================
    # OPÉRATIONS POUR LES RAPPORTS (COMPATIBILITÉ)
    # ========================================
    
    def get_building_reports(self) -> List[Dict[str, Any]]:
        """Récupérer tous les rapports d'immeubles (compatibilité)"""
        try:
            with self.get_session() as session:
                reports = session.query(RapportImmeuble).all()
                return [report.to_dict() for report in reports]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des rapports d'immeubles: {e}")
            raise e
    
    def create_building_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer un rapport d'immeuble (compatibilité)"""
        try:
            with self.get_session() as session:
                report = RapportImmeuble(
                    id_immeuble=report_data.get('buildingId'),
                    annee=report_data.get('year'),
                    mois=report_data.get('month', 1),
                    revenus_totaux=report_data.get('totalRevenue', 0),
                    depenses_totales=report_data.get('totalExpenses', 0),
                    marge_nette=report_data.get('netMargin', 0),
                    notes=report_data.get('notes', '')
                )
                
                session.add(report)
                session.commit()
                session.refresh(report)
                
                print(f"✅ Rapport d'immeuble créé: {report.annee}-{report.mois} (ID: {report.id_rapport})")
                return report.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la création du rapport d'immeuble: {e}")
            raise e
    
    def update_building_report(self, report_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mettre à jour un rapport d'immeuble (compatibilité)"""
        try:
            with self.get_session() as session:
                report = session.query(RapportImmeuble).filter(RapportImmeuble.id_rapport == report_id).first()
                if not report:
                    return None
                
                # Mettre à jour les champs
                if 'totalRevenue' in update_data:
                    report.revenus_totaux = update_data['totalRevenue']
                if 'totalExpenses' in update_data:
                    report.depenses_totales = update_data['totalExpenses']
                if 'netMargin' in update_data:
                    report.marge_nette = update_data['netMargin']
                if 'notes' in update_data:
                    report.notes = update_data['notes']
                
                report.date_modification = datetime.utcnow()
                session.commit()
                
                print(f"✅ Rapport d'immeuble mis à jour: {report.annee}-{report.mois} (ID: {report.id_rapport})")
                return report.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du rapport d'immeuble {report_id}: {e}")
            raise e
    
    def delete_building_report(self, report_id: int) -> bool:
        """Supprimer un rapport d'immeuble (compatibilité)"""
        try:
            with self.get_session() as session:
                report = session.query(RapportImmeuble).filter(RapportImmeuble.id_rapport == report_id).first()
                if not report:
                    return False
                
                session.delete(report)
                session.commit()
                
                print(f"✅ Rapport d'immeuble supprimé: {report.annee}-{report.mois} (ID: {report.id_rapport})")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du rapport d'immeuble {report_id}: {e}")
            raise e
    
    def get_unit_reports(self) -> List[Dict[str, Any]]:
        """Récupérer tous les rapports d'unités (compatibilité)"""
        try:
            # Pour l'instant, retourner une liste vide car nous n'avons pas encore de table unit_reports
            return []
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des rapports d'unités: {e}")
            raise e
    
    def create_unit_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer un rapport d'unité (compatibilité)"""
        try:
            # Pour l'instant, retourner un objet vide car nous n'avons pas encore de table unit_reports
            return {"id": 1, "message": "Rapport d'unité créé (nouveau système)"}
        except Exception as e:
            print(f"❌ Erreur lors de la création du rapport d'unité: {e}")
            raise e
    
    def delete_unit_report(self, report_id: int) -> bool:
        """Supprimer un rapport d'unité (compatibilité)"""
        try:
            # Pour l'instant, retourner True car nous n'avons pas encore de table unit_reports
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du rapport d'unité {report_id}: {e}")
            raise e
    
    # ========================================
    # MÉTHODES UTILITAIRES
    # ========================================
    
    def get_invoice_constants(self) -> Dict[str, Any]:
        """Récupérer les constantes pour les factures"""
        return {
            "categories": {
                "municipal_taxes": "Taxes municipales",
                "school_taxes": "Taxes scolaires",
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
                "bank_transfer": "Virement bancaire",
                "check": "Chèque",
                "cash": "Espèces"
            },
            "invoiceTypes": {
                "rental_building": "Immeuble en location",
                "construction_project": "Projet de construction"
            }
        }

# Instance globale du service
db_service_francais = DatabaseServiceFrancais()
