#!/usr/bin/env python3
"""
Service de base de données en français pour Interface CAH
Utilise les nouveaux modèles français
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json
import os
import platform

from database import db_manager
from models_francais import Immeuble, Locataire, Unite, Bail, Transaction

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
                # Utiliser directement les données françaises du frontend
                building = Immeuble(
                    nom_immeuble=building_data.get('nom_immeuble', ''),
                    adresse=building_data.get('adresse', ''),
                    ville=building_data.get('ville', ''),
                    province=building_data.get('province', ''),
                    code_postal=building_data.get('code_postal', ''),
                    pays=building_data.get('pays', 'Canada'),
                    nbr_unite=building_data.get('nbr_unite', 1),
                    annee_construction=building_data.get('annee_construction'),
                    prix_achete=building_data.get('prix_achete', 0),
                    mise_de_fond=building_data.get('mise_de_fond', 0),
                    taux_interet=building_data.get('taux_interet', 0),
                    valeur_actuel=building_data.get('valeur_actuel', 0),
                    proprietaire=building_data.get('proprietaire', ''),
                    banque=building_data.get('banque', ''),
                    contracteur=building_data.get('contracteur', ''),
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
        """Mettre à jour un immeuble avec les champs français"""
        try:
            with self.get_session() as session:
                building = session.query(Immeuble).filter(Immeuble.id_immeuble == building_id).first()
                if not building:
                    return None
                
                # Mettre à jour les champs français directement
                if 'nom_immeuble' in update_data:
                    building.nom_immeuble = update_data['nom_immeuble']
                if 'adresse' in update_data:
                    building.adresse = update_data['adresse']
                if 'ville' in update_data:
                    building.ville = update_data['ville']
                if 'province' in update_data:
                    building.province = update_data['province']
                if 'code_postal' in update_data:
                    building.code_postal = update_data['code_postal']
                if 'pays' in update_data:
                    building.pays = update_data['pays']
                if 'nbr_unite' in update_data:
                    building.nbr_unite = update_data['nbr_unite']
                if 'annee_construction' in update_data:
                    building.annee_construction = update_data['annee_construction']
                if 'prix_achete' in update_data:
                    building.prix_achete = update_data['prix_achete']
                if 'mise_de_fond' in update_data:
                    building.mise_de_fond = update_data['mise_de_fond']
                if 'taux_interet' in update_data:
                    building.taux_interet = update_data['taux_interet']
                if 'valeur_actuel' in update_data:
                    building.valeur_actuel = update_data['valeur_actuel']
                if 'proprietaire' in update_data:
                    building.proprietaire = update_data['proprietaire']
                if 'banque' in update_data:
                    building.banque = update_data['banque']
                if 'contracteur' in update_data:
                    building.contracteur = update_data['contracteur']
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
        """Récupérer toutes les unités avec les informations des locataires"""
        try:
            with self.get_session() as session:
                units = session.query(Unite).offset(skip).limit(limit).all()
                
                result = []
                for unit in units:
                    unit_dict = unit.to_dict()
                    
                    # Ajouter les informations de l'immeuble
                    if unit.immeuble:
                        unit_dict['immeuble'] = {
                            'id_immeuble': unit.immeuble.id_immeuble,
                            'nom_immeuble': unit.immeuble.nom_immeuble,
                            'adresse': unit.immeuble.adresse
                        }
                    
                    # Ajouter les informations des locataires
                    if unit.locataires:
                        unit_dict['locataires'] = []
                        for locataire in unit.locataires:
                            locataire_info = {
                                'id_locataire': locataire.id_locataire,
                                'nom': locataire.nom,
                                'prenom': locataire.prenom,
                                'email': locataire.email,
                                'telephone': locataire.telephone,
                                'statut': locataire.statut
                            }
                            unit_dict['locataires'].append(locataire_info)
                    else:
                        unit_dict['locataires'] = []
                    
                    result.append(unit_dict)
                
                return result
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
                    id_immeuble=unit_data.get('id_immeuble'),
                    adresse_unite=unit_data.get('adresse_unite', ''),
                    type=unit_data.get('type', '4 1/2'),
                    nbr_chambre=unit_data.get('nbr_chambre', 1),
                    nbr_salle_de_bain=unit_data.get('nbr_salle_de_bain', 1)
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
                
                # Mettre à jour les champs avec le format français
                if 'adresse_unite' in update_data:
                    unit.adresse_unite = update_data['adresse_unite']
                if 'type' in update_data:
                    unit.type = update_data['type']
                if 'nbr_chambre' in update_data:
                    unit.nbr_chambre = update_data['nbr_chambre']
                if 'nbr_salle_de_bain' in update_data:
                    unit.nbr_salle_de_bain = update_data['nbr_salle_de_bain']
                if 'id_immeuble' in update_data:
                    unit.id_immeuble = update_data['id_immeuble']
                
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
                # Utiliser directement les données françaises du frontend
                tenant = Locataire(
                    id_unite=tenant_data.get('id_unite'),
                    nom=tenant_data.get('nom', ''),
                    prenom=tenant_data.get('prenom', ''),
                    email=tenant_data.get('email', ''),
                    telephone=tenant_data.get('telephone', ''),
                    statut=tenant_data.get('statut', 'actif'),
                    notes=tenant_data.get('notes', '')
                )
                
                session.add(tenant)
                session.commit()
                session.refresh(tenant)
                
                print(f"✅ Locataire créé: {tenant.nom} {tenant.prenom} (ID: {tenant.id_locataire})")
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
                
                # Mettre à jour les champs avec le format français
                if 'nom' in update_data:
                    tenant.nom = update_data['nom']
                if 'prenom' in update_data:
                    tenant.prenom = update_data['prenom']
                if 'email' in update_data:
                    tenant.email = update_data['email']
                if 'telephone' in update_data:
                    tenant.telephone = update_data['telephone']
                if 'statut' in update_data:
                    tenant.statut = update_data['statut']
                if 'notes' in update_data:
                    tenant.notes = update_data['notes']
                if 'id_unite' in update_data:
                    tenant.id_unite = update_data['id_unite']
                
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
    
    def get_transactions(self) -> List[Dict[str, Any]]:
        """Récupérer toutes les transactions"""
        try:
            print("🔍 [DB] Début de get_transactions()")
            with self.get_session() as session:
                print("🔍 [DB] Session créée, requête en cours...")
                transactions = session.query(Transaction).all()
                print(f"🔍 [DB] {len(transactions)} transactions trouvées")
                result = [transaction.to_dict() for transaction in transactions]
                print(f"✅ [DB] Transactions converties: {len(result)}")
                return result
        except Exception as e:
            print(f"❌ [DB] Erreur dans get_transactions(): {e}")
            raise e
    
    def get_transaction(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer une transaction par ID"""
        try:
            with self.get_session() as session:
                transaction = session.query(Transaction).filter(Transaction.id_transaction == transaction_id).first()
                return transaction.to_dict() if transaction else None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de la transaction {transaction_id}: {e}")
            raise e
    
    def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer une nouvelle transaction"""
        try:
            with self.get_session() as session:
                transaction = Transaction(
                    id_immeuble=transaction_data.get('id_immeuble'),
                    type=transaction_data.get('type', ''),
                    categorie=transaction_data.get('categorie', ''),
                    montant=transaction_data.get('montant', 0),
                    date_de_transaction=datetime.strptime(transaction_data.get('date_de_transaction', ''), '%Y-%m-%d').date() if transaction_data.get('date_de_transaction') else datetime.now().date(),
                    methode_de_paiement=transaction_data.get('methode_de_paiement', ''),
                    reference=transaction_data.get('reference', ''),
                    source=transaction_data.get('source', ''),
                    pdf_transaction=transaction_data.get('pdf_transaction', ''),
                    notes=transaction_data.get('notes', '')
                )
                
                session.add(transaction)
                session.commit()
                session.refresh(transaction)
                
                print(f"✅ Transaction créée: {transaction.categorie} (ID: {transaction.id_transaction})")
                return transaction.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la création de la transaction: {e}")
            raise e
    
    def update_transaction(self, transaction_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mettre à jour une transaction"""
        try:
            with self.get_session() as session:
                transaction = session.query(Transaction).filter(Transaction.id_transaction == transaction_id).first()
                if not transaction:
                    return None
                
                # Mettre à jour les champs avec le format français
                if 'categorie' in update_data:
                    transaction.categorie = update_data['categorie']
                if 'montant' in update_data:
                    transaction.montant = update_data['montant']
                if 'date_de_transaction' in update_data:
                    transaction.date_de_transaction = datetime.strptime(update_data['date_de_transaction'], '%Y-%m-%d').date()
                if 'methode_de_paiement' in update_data:
                    transaction.methode_de_paiement = update_data['methode_de_paiement']
                if 'reference' in update_data:
                    transaction.reference = update_data['reference']
                if 'source' in update_data:
                    transaction.source = update_data['source']
                if 'pdf_transaction' in update_data:
                    transaction.pdf_transaction = update_data['pdf_transaction']
                if 'notes' in update_data:
                    transaction.notes = update_data['notes']
                if 'id_immeuble' in update_data:
                    transaction.id_immeuble = update_data['id_immeuble']
                
                transaction.date_modification = datetime.utcnow()
                session.commit()
                
                print(f"✅ Transaction mise à jour: {transaction.categorie} (ID: {transaction.id_transaction})")
                return transaction.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de la transaction {transaction_id}: {e}")
            raise e
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Supprimer une transaction"""
        try:
            with self.get_session() as session:
                transaction = session.query(Transaction).filter(Transaction.id_transaction == transaction_id).first()
                if not transaction:
                    return False
                
                session.delete(transaction)
                session.commit()
                
                print(f"✅ Transaction supprimée: {transaction.categorie} (ID: {transaction.id_transaction})")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de la transaction {transaction_id}: {e}")
            raise e
    
    # === MÉTHODES POUR LES BAUX ===
    
    def get_leases(self) -> List[Dict[str, Any]]:
        """Récupérer tous les baux avec les informations des locataires et unités"""
        try:
            with self.get_session() as session:
                # Faire une jointure pour récupérer les informations complètes
                leases = session.query(Bail).join(Locataire, Bail.id_locataire == Locataire.id_locataire).join(Unite, Locataire.id_unite == Unite.id_unite).all()
                
                result = []
                for lease in leases:
                    lease_dict = lease.to_dict()
                    
                    # Ajouter les informations du locataire
                    if lease.locataire:
                        lease_dict['locataire'] = {
                            'id_locataire': lease.locataire.id_locataire,
                            'nom': lease.locataire.nom,
                            'prenom': lease.locataire.prenom,
                            'email': lease.locataire.email,
                            'telephone': lease.locataire.telephone,
                            'statut': lease.locataire.statut
                        }
                    
                    # Ajouter les informations de l'unité
                    if lease.locataire and lease.locataire.unite:
                        lease_dict['unite'] = {
                            'id_unite': lease.locataire.unite.id_unite,
                            'adresse_unite': lease.locataire.unite.adresse_unite,
                            'type': lease.locataire.unite.type,
                            'nbr_chambre': lease.locataire.unite.nbr_chambre,
                            'nbr_salle_de_bain': lease.locataire.unite.nbr_salle_de_bain
                        }
                        
                        # Ajouter les informations de l'immeuble
                        if lease.locataire.unite.immeuble:
                            lease_dict['unite']['immeuble'] = {
                                'id_immeuble': lease.locataire.unite.immeuble.id_immeuble,
                                'nom_immeuble': lease.locataire.unite.immeuble.nom_immeuble,
                                'adresse': lease.locataire.unite.immeuble.adresse
                            }
                    
                    result.append(lease_dict)
                
                return result
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des baux: {e}")
            raise e
    
    def get_lease(self, lease_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer un bail par ID avec les informations des locataires et unités"""
        try:
            with self.get_session() as session:
                lease = session.query(Bail).join(Locataire, Bail.id_locataire == Locataire.id_locataire).join(Unite, Locataire.id_unite == Unite.id_unite).filter(Bail.id_bail == lease_id).first()
                
                if not lease:
                    return None
                
                lease_dict = lease.to_dict()
                
                # Ajouter les informations du locataire
                if lease.locataire:
                    lease_dict['locataire'] = {
                        'id_locataire': lease.locataire.id_locataire,
                        'nom': lease.locataire.nom,
                        'prenom': lease.locataire.prenom,
                        'email': lease.locataire.email,
                        'telephone': lease.locataire.telephone,
                        'statut': lease.locataire.statut
                    }
                
                # Ajouter les informations de l'unité
                if lease.locataire and lease.locataire.unite:
                    lease_dict['unite'] = {
                        'id_unite': lease.locataire.unite.id_unite,
                        'adresse_unite': lease.locataire.unite.adresse_unite,
                        'type': lease.locataire.unite.type,
                        'nbr_chambre': lease.locataire.unite.nbr_chambre,
                        'nbr_salle_de_bain': lease.locataire.unite.nbr_salle_de_bain
                    }
                    
                    # Ajouter les informations de l'immeuble
                    if lease.locataire.unite.immeuble:
                        lease_dict['unite']['immeuble'] = {
                            'id_immeuble': lease.locataire.unite.immeuble.id_immeuble,
                            'nom_immeuble': lease.locataire.unite.immeuble.nom_immeuble,
                            'adresse': lease.locataire.unite.immeuble.adresse
                        }
                
                return lease_dict
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du bail: {e}")
            raise e

    def create_lease(self, lease_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer un nouveau bail"""
        try:
            with self.get_session() as session:
                # Utiliser directement les données françaises du frontend
                lease = Bail(
                    id_locataire=lease_data.get('id_locataire'),
                    date_debut=datetime.strptime(lease_data.get('date_debut'), '%Y-%m-%d').date() if lease_data.get('date_debut') else None,
                    date_fin=datetime.strptime(lease_data.get('date_fin'), '%Y-%m-%d').date() if lease_data.get('date_fin') else None,
                    prix_loyer=lease_data.get('prix_loyer', 0),
                    methode_paiement=lease_data.get('methode_paiement', 'Virement bancaire'),
                    pdf_bail=lease_data.get('pdf_bail', '')
                )
                
                session.add(lease)
                session.commit()
                session.refresh(lease)
                
                print(f"✅ Bail créé: {lease.prix_loyer}$/mois (ID: {lease.id_bail})")
                return lease.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la création du bail: {e}")
            raise e
    
    def update_lease(self, lease_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mettre à jour un bail"""
        try:
            with self.get_session() as session:
                lease = session.query(Bail).filter(Bail.id_bail == lease_id).first()
                if not lease:
                    return None
                
                # Mettre à jour les champs
                if 'date_debut' in update_data:
                    lease.date_debut = datetime.strptime(update_data['date_debut'], '%Y-%m-%d').date()
                if 'date_fin' in update_data:
                    lease.date_fin = datetime.strptime(update_data['date_fin'], '%Y-%m-%d').date()
                if 'prix_loyer' in update_data:
                    lease.prix_loyer = update_data['prix_loyer']
                if 'methode_paiement' in update_data:
                    lease.methode_paiement = update_data['methode_paiement']
                if 'pdf_bail' in update_data:
                    lease.pdf_bail = update_data['pdf_bail']
                
                lease.date_modification = datetime.utcnow()
                session.commit()
                
                print(f"✅ Bail mis à jour: {lease.prix_loyer}$/mois (ID: {lease.id_bail})")
                return lease.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du bail: {e}")
            raise e
    
    def delete_lease(self, lease_id: int) -> bool:
        """Supprimer un bail"""
        try:
            with self.get_session() as session:
                lease = session.query(Bail).filter(Bail.id_bail == lease_id).first()
                if not lease:
                    return False
                
                session.delete(lease)
                session.commit()
                
                print(f"✅ Bail supprimé (ID: {lease_id})")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du bail: {e}")
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

    def get_leases_by_buildings_and_period(self, building_ids, start_date, end_date):
        """Récupérer les baux pour des immeubles et une période donnée via les unités"""
        try:
            with self.get_session() as session:
                print(f"🔍 DEBUG - Recherche baux pour immeubles: {building_ids}")
                print(f"🔍 DEBUG - Période: {start_date} à {end_date}")
                
                leases = session.query(Bail).join(Locataire, Bail.id_locataire == Locataire.id_locataire).join(Unite, Locataire.id_unite == Unite.id_unite).filter(
                    Unite.id_immeuble.in_(building_ids),
                    Bail.date_debut <= end_date,
                    or_(
                        Bail.date_fin >= start_date,
                        Bail.date_fin.is_(None)
                    )
                ).all()
                
                print(f"🔍 DEBUG - Baux trouvés: {len(leases)}")
                for lease in leases:
                    print(f"🔍 DEBUG - Bail ID: {lease.id_bail}, Prix: {lease.prix_loyer}, Début: {lease.date_debut}, Fin: {lease.date_fin}")
                
                return leases
        except Exception as e:
            print(f"Erreur lors de la récupération des baux: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_transactions_by_buildings_and_period(self, building_ids, start_date, end_date):
        """Récupérer les transactions pour des immeubles et une période donnée"""
        try:
            with self.get_session() as session:
                return session.query(Transaction).filter(
                    Transaction.id_immeuble.in_(building_ids),
                    Transaction.date_de_transaction >= start_date,
                    Transaction.date_de_transaction <= end_date
                ).all()
        except Exception as e:
            print(f"Erreur lors de la récupération des transactions: {e}")
            return []

    def get_buildings_by_ids(self, building_ids):
        """Récupérer les immeubles par IDs"""
        try:
            with self.get_session() as session:
                return session.query(Immeuble).filter(
                    Immeuble.id_immeuble.in_(building_ids)
                ).all()
        except Exception as e:
            print(f"Erreur lors de la récupération des immeubles: {e}")
            return []

# Instance globale du service
db_service_francais = DatabaseServiceFrancais()
