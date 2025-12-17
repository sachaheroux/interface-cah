#!/usr/bin/env python3
"""
Service de base de données en français pour Interface CAH
Utilise les nouveaux modèles français
"""

from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine, text, or_, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json
import os
import platform

from database import db_manager
from models_francais import Immeuble, Locataire, Unite, Bail, Transaction, PaiementLoyer

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
                if 'dette_restante' in update_data:
                    building.dette_restante = update_data['dette_restante'] if update_data['dette_restante'] is not None else 0
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
                
                # Vérifier s'il y a des dépendances
                units_count = session.query(Unite).filter(Unite.id_immeuble == building_id).count()
                transactions_count = session.query(Transaction).filter(Transaction.id_immeuble == building_id).count()
                
                if units_count > 0 or transactions_count > 0:
                    print(f"⚠️ Impossible de supprimer l'immeuble {building.nom_immeuble}: {units_count} unités et {transactions_count} transactions associées")
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
                    # Permettre de mettre id_unite à None pour désélectionner l'unité
                    tenant.id_unite = update_data['id_unite'] if update_data['id_unite'] else None
                
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
    
    def get_transaction_by_reference(self, reference: str) -> Optional[Dict[str, Any]]:
        """Récupérer une transaction par référence"""
        try:
            with self.get_session() as session:
                transaction = session.query(Transaction).filter(Transaction.reference == reference).first()
                return transaction.to_dict() if transaction else None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de la transaction par référence {reference}: {e}")
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
                # Vérifier si la colonne id_unite existe dans la table baux
                # Si elle n'existe pas, utiliser l'ancienne méthode (via locataire)
                has_id_unite_column = False
                try:
                    # Utiliser PRAGMA table_info pour vérifier si la colonne existe
                    result = session.execute(text("PRAGMA table_info(baux)"))
                    columns = [row[1] for row in result]
                    has_id_unite_column = 'id_unite' in columns
                    if not has_id_unite_column:
                        print("⚠️ La colonne id_unite n'existe pas encore dans baux, utilisation de l'ancienne méthode")
                except Exception as pragma_error:
                    print(f"⚠️ Erreur lors de la vérification de la colonne id_unite: {pragma_error}")
                    # En cas d'erreur, supposer que la colonne n'existe pas
                    has_id_unite_column = False
                
                # Charger tous les baux avec leurs locataires
                if has_id_unite_column:
                    # Nouvelle méthode : utiliser id_unite directement sur le bail
                    try:
                        leases = session.query(Bail).options(
                            joinedload(Bail.locataire),
                            joinedload(Bail.unite).joinedload(Unite.immeuble)
                        ).all()
                    except Exception:
                        # Si la relation ne fonctionne pas, charger sans eager loading
                        leases = session.query(Bail).options(
                            joinedload(Bail.locataire)
                        ).all()
                else:
                    # Ancienne méthode : utiliser l'unité du locataire
                    leases = session.query(Bail).options(
                        joinedload(Bail.locataire).joinedload(Locataire.unite).joinedload(Unite.immeuble)
                    ).all()
                
                result = []
                for lease in leases:
                    try:
                        lease_dict = lease.to_dict()
                        
                        # Ajouter les informations du locataire
                        if lease.locataire:
                            locataire_data = {
                                'id_locataire': lease.locataire.id_locataire,
                                'nom': lease.locataire.nom,
                                'prenom': lease.locataire.prenom,
                                'email': lease.locataire.email,
                                'telephone': lease.locataire.telephone,
                                'statut': lease.locataire.statut
                            }
                            
                            # Gérer l'unité selon que la migration a été faite ou non
                            if has_id_unite_column:
                                # Nouvelle méthode : utiliser l'unité du bail
                                if hasattr(lease, 'id_unite') and lease.id_unite:
                                    # Charger l'unité depuis le bail
                                    if hasattr(lease, 'unite') and lease.unite:
                                        unite_data = {
                                            'id_unite': lease.unite.id_unite,
                                            'adresse_unite': lease.unite.adresse_unite,
                                            'type': lease.unite.type,
                                            'nbr_chambre': lease.unite.nbr_chambre,
                                            'nbr_salle_de_bain': lease.unite.nbr_salle_de_bain,
                                            'id_immeuble': lease.unite.id_immeuble
                                        }
                                        if lease.unite.immeuble:
                                            unite_data['immeuble'] = {
                                                'id_immeuble': lease.unite.immeuble.id_immeuble,
                                                'nom_immeuble': lease.unite.immeuble.nom_immeuble,
                                                'adresse': lease.unite.immeuble.adresse
                                            }
                                        locataire_data['unite'] = unite_data
                                    else:
                                        # Charger l'unité manuellement
                                        unite = session.query(Unite).filter(Unite.id_unite == lease.id_unite).first()
                                        if unite:
                                            unite_data = {
                                                'id_unite': unite.id_unite,
                                                'adresse_unite': unite.adresse_unite,
                                                'type': unite.type,
                                                'nbr_chambre': unite.nbr_chambre,
                                                'nbr_salle_de_bain': unite.nbr_salle_de_bain,
                                                'id_immeuble': unite.id_immeuble
                                            }
                                            if unite.immeuble:
                                                unite_data['immeuble'] = {
                                                    'id_immeuble': unite.immeuble.id_immeuble,
                                                    'nom_immeuble': unite.immeuble.nom_immeuble,
                                                    'adresse': unite.immeuble.adresse
                                                }
                                            locataire_data['unite'] = unite_data
                                elif lease.locataire.id_unite and lease.locataire.unite:
                                    # Fallback : utiliser l'unité du locataire si le bail n'a pas encore id_unite
                                    unite_data = {
                                        'id_unite': lease.locataire.unite.id_unite,
                                        'adresse_unite': lease.locataire.unite.adresse_unite,
                                        'type': lease.locataire.unite.type,
                                        'nbr_chambre': lease.locataire.unite.nbr_chambre,
                                        'nbr_salle_de_bain': lease.locataire.unite.nbr_salle_de_bain,
                                        'id_immeuble': lease.locataire.unite.id_immeuble
                                    }
                                    if lease.locataire.unite.immeuble:
                                        unite_data['immeuble'] = {
                                            'id_immeuble': lease.locataire.unite.immeuble.id_immeuble,
                                            'nom_immeuble': lease.locataire.unite.immeuble.nom_immeuble,
                                            'adresse': lease.locataire.unite.immeuble.adresse
                                        }
                                    locataire_data['unite'] = unite_data
                            else:
                                # Ancienne méthode : utiliser l'unité du locataire
                                if lease.locataire.id_unite and lease.locataire.unite:
                                    unite_data = {
                                        'id_unite': lease.locataire.unite.id_unite,
                                        'adresse_unite': lease.locataire.unite.adresse_unite,
                                        'type': lease.locataire.unite.type,
                                        'nbr_chambre': lease.locataire.unite.nbr_chambre,
                                        'nbr_salle_de_bain': lease.locataire.unite.nbr_salle_de_bain,
                                        'id_immeuble': lease.locataire.unite.id_immeuble
                                    }
                                    if lease.locataire.unite.immeuble:
                                        unite_data['immeuble'] = {
                                            'id_immeuble': lease.locataire.unite.immeuble.id_immeuble,
                                            'nom_immeuble': lease.locataire.unite.immeuble.nom_immeuble,
                                            'adresse': lease.locataire.unite.immeuble.adresse
                                        }
                                    locataire_data['unite'] = unite_data
                            
                            lease_dict['locataire'] = locataire_data
                        
                        result.append(lease_dict)
                    except Exception as lease_error:
                        print(f"⚠️ Erreur lors du traitement du bail {lease.id_bail}: {lease_error}")
                        import traceback
                        traceback.print_exc()
                        # Continuer avec les autres baux même si celui-ci échoue
                        continue
                
                return result
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des baux: {e}")
            import traceback
            traceback.print_exc()
            raise e
    
    def get_lease(self, lease_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer un bail par ID avec les informations des locataires et unités"""
        try:
            with self.get_session() as session:
                # Utiliser joinedload au lieu de join pour éviter les problèmes
                lease = session.query(Bail).options(
                    joinedload(Bail.locataire),
                    joinedload(Bail.unite).joinedload(Unite.immeuble)
                ).filter(Bail.id_bail == lease_id).first()
                
                if not lease:
                    return None
                
                lease_dict = lease.to_dict()
                
                # Ajouter les informations du locataire
                if lease.locataire:
                    locataire_data = {
                        'id_locataire': lease.locataire.id_locataire,
                        'nom': lease.locataire.nom,
                        'prenom': lease.locataire.prenom,
                        'email': lease.locataire.email,
                        'telephone': lease.locataire.telephone,
                        'statut': lease.locataire.statut
                    }
                    lease_dict['locataire'] = locataire_data
                
                # Ajouter les informations de l'unité directement depuis le bail
                if lease.unite:
                    unite_data = {
                        'id_unite': lease.unite.id_unite,
                        'adresse_unite': lease.unite.adresse_unite,
                        'type': lease.unite.type,
                        'nbr_chambre': lease.unite.nbr_chambre,
                        'nbr_salle_de_bain': lease.unite.nbr_salle_de_bain,
                        'id_immeuble': lease.unite.id_immeuble
                    }
                    
                    # Ajouter les informations de l'immeuble
                    if lease.unite.immeuble:
                        unite_data['immeuble'] = {
                            'id_immeuble': lease.unite.immeuble.id_immeuble,
                            'nom_immeuble': lease.unite.immeuble.nom_immeuble,
                            'adresse': lease.unite.immeuble.adresse
                        }
                    
                    # Ajouter l'unité dans le locataire pour compatibilité avec le frontend
                    if lease_dict.get('locataire'):
                        lease_dict['locataire']['unite'] = unite_data
                    else:
                        lease_dict['unite'] = unite_data
                
                return lease_dict
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du bail: {e}")
            raise e

    def check_lease_overlap(self, session, id_unite: int, date_debut, date_fin, exclude_lease_id: int = None) -> bool:
        """Vérifier s'il y a un chevauchement de baux pour une unité"""
        if not id_unite:
            return False  # Pas d'unité, pas de chevauchement possible
        
        # Chercher tous les baux pour la même unité (maintenant directement depuis Bail.id_unite)
        query = session.query(Bail).filter(
            Bail.id_unite == id_unite,
            Bail.date_debut.isnot(None),
            Bail.date_fin.isnot(None)
        )
        
        # Exclure le bail en cours de modification
        if exclude_lease_id:
            query = query.filter(Bail.id_bail != exclude_lease_id)
        
        existing_leases = query.all()
        
        # Vérifier les chevauchements
        for existing_lease in existing_leases:
            # Chevauchement si:
            # - Le nouveau bail commence pendant un bail existant
            # - Le nouveau bail se termine pendant un bail existant
            # - Le nouveau bail englobe complètement un bail existant
            if (date_debut <= existing_lease.date_fin and date_fin >= existing_lease.date_debut):
                print(f"⚠️ Chevauchement détecté avec le bail #{existing_lease.id_bail} ({existing_lease.date_debut} - {existing_lease.date_fin})")
                return True
        
        return False
    
    def create_lease(self, lease_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer un nouveau bail"""
        try:
            with self.get_session() as session:
                # Parser les dates
                date_debut = datetime.strptime(lease_data.get('date_debut'), '%Y-%m-%d').date() if lease_data.get('date_debut') else None
                date_fin = datetime.strptime(lease_data.get('date_fin'), '%Y-%m-%d').date() if lease_data.get('date_fin') else None
                id_locataire = lease_data.get('id_locataire')
                
                # Récupérer id_unite depuis lease_data (maintenant requis)
                id_unite = lease_data.get('id_unite')
                if not id_unite:
                    raise ValueError("id_unite est requis pour créer un bail")
                
                # Vérifier les chevauchements
                if date_debut and date_fin and id_unite:
                    if self.check_lease_overlap(session, id_unite, date_debut, date_fin):
                        raise ValueError("Un bail existe déjà pour cette unité durant cette période. Les baux ne peuvent pas se chevaucher.")
                
                # Utiliser directement les données françaises du frontend
                lease = Bail(
                    id_locataire=id_locataire,
                    id_unite=id_unite,
                    date_debut=date_debut,
                    date_fin=date_fin,
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
                
                # Préparer les nouvelles dates pour validation
                new_date_debut = datetime.strptime(update_data['date_debut'], '%Y-%m-%d').date() if 'date_debut' in update_data else lease.date_debut
                new_date_fin = datetime.strptime(update_data['date_fin'], '%Y-%m-%d').date() if 'date_fin' in update_data else lease.date_fin
                
                # Utiliser id_unite depuis update_data si modifié, sinon depuis le bail existant
                id_unite_to_check = update_data.get('id_unite', lease.id_unite)
                
                # Vérifier les chevauchements si les dates changent
                if ('date_debut' in update_data or 'date_fin' in update_data) and new_date_debut and new_date_fin and id_unite_to_check:
                    if self.check_lease_overlap(session, id_unite_to_check, new_date_debut, new_date_fin, exclude_lease_id=lease_id):
                        raise ValueError("Un bail existe déjà pour cette unité durant cette période. Les baux ne peuvent pas se chevaucher.")
                
                # Mettre à jour les champs
                if 'id_unite' in update_data:
                    lease.id_unite = update_data['id_unite']
                if 'date_debut' in update_data:
                    lease.date_debut = new_date_debut
                if 'date_fin' in update_data:
                    lease.date_fin = new_date_fin
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
                
                # Approche SQLAlchemy ORM simple avec eager loading
                # Maintenant l'unité est directement sur le bail
                leases = session.query(Bail).join(Unite, Bail.id_unite == Unite.id_unite).filter(
                    Unite.id_immeuble.in_(building_ids),
                    Bail.date_debut <= end_date,
                    or_(Bail.date_fin >= start_date, Bail.date_fin.is_(None))
                ).options(
                    joinedload(Bail.locataire),
                    joinedload(Bail.unite).joinedload(Unite.immeuble)
                ).all()
                
                print(f"🔍 DEBUG - Baux trouvés: {len(leases)}")
                for lease in leases:
                    building_id = lease.unite.id_immeuble if lease.unite else None
                    print(f"🔍 DEBUG - Bail: ID {lease.id_bail}, Immeuble: {building_id}, Loyer: {lease.prix_loyer}")
                
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
                buildings = session.query(Immeuble).filter(
                    Immeuble.id_immeuble.in_(building_ids)
                ).all()
                return [building.to_dict() for building in buildings]
        except Exception as e:
            print(f"Erreur lors de la récupération des immeubles: {e}")
            return []
    
    def get_buildings_by_ids_objects(self, building_ids):
        """Récupérer les immeubles par IDs comme objets SQLAlchemy"""
        try:
            with self.get_session() as session:
                buildings = session.query(Immeuble).filter(
                    Immeuble.id_immeuble.in_(building_ids)
                ).all()
                return buildings
        except Exception as e:
            print(f"Erreur lors de la récupération des immeubles: {e}")
            return []

    # ========================================
    # OPÉRATIONS POUR LES PAIEMENTS DE LOYERS
    # ========================================
    
    def create_paiement_loyer(self, paiement_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Créer un paiement de loyer (existence = payé)"""
        try:
            with self.get_session() as session:
                print(f"🔍 Création paiement pour bail {paiement_data['id_bail']}, {paiement_data['mois']}/{paiement_data['annee']}")
                
                # Récupérer le bail pour obtenir le prix du loyer
                bail = session.query(Bail).filter(Bail.id_bail == paiement_data['id_bail']).first()
                if not bail:
                    raise ValueError(f"Bail {paiement_data['id_bail']} non trouvé")
                
                print(f"🔍 Bail trouvé: prix_loyer = {bail.prix_loyer}")
                
                # Montant payé: utiliser celui fourni ou le prix du bail par défaut
                montant_paye = paiement_data.get('montant_paye')
                if not montant_paye:
                    if not bail.prix_loyer:
                        raise ValueError(f"Le bail {bail.id_bail} n'a pas de prix_loyer défini")
                    montant_paye = float(bail.prix_loyer)
                    print(f"✅ Montant payé auto-rempli: {montant_paye}$ (depuis bail #{bail.id_bail})")
                
                # Date de paiement: utiliser celle fournie ou le 1er du mois par défaut
                date_paiement_reelle = paiement_data.get('date_paiement_reelle')
                if not date_paiement_reelle:
                    from datetime import date
                    date_paiement_reelle = date(paiement_data['annee'], paiement_data['mois'], 1)
                    print(f"✅ Date de paiement auto-remplie: {date_paiement_reelle}")
                
                print(f"🔍 Création avec: montant={montant_paye}, date={date_paiement_reelle}")
                
                paiement = PaiementLoyer(
                    id_bail=paiement_data['id_bail'],
                    mois=paiement_data['mois'],
                    annee=paiement_data['annee'],
                    date_paiement_reelle=date_paiement_reelle,
                    montant_paye=montant_paye,
                    notes=paiement_data.get('notes')
                )
                session.add(paiement)
                session.commit()
                session.refresh(paiement)
                
                print(f"✅ Paiement de loyer créé: Bail {paiement.id_bail}, {paiement.mois}/{paiement.annee}, Montant: {paiement.montant_paye}$")
                return paiement.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la création du paiement de loyer: {e}")
            import traceback
            traceback.print_exc()
            raise e
    
    def update_paiement_loyer(self, paiement_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mettre à jour un paiement de loyer"""
        try:
            with self.get_session() as session:
                paiement = session.query(PaiementLoyer).filter(PaiementLoyer.id_paiement == paiement_id).first()
                if not paiement:
                    return None
                
                # Mettre à jour les champs
                if 'date_paiement_reelle' in update_data:
                    paiement.date_paiement_reelle = update_data['date_paiement_reelle']
                if 'montant_paye' in update_data:
                    paiement.montant_paye = update_data['montant_paye']
                if 'notes' in update_data:
                    paiement.notes = update_data['notes']
                
                paiement.date_modification = datetime.utcnow()
                session.commit()
                
                print(f"✅ Paiement de loyer mis à jour: ID {paiement_id}, Montant: {paiement.montant_paye}$")
                return paiement.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du paiement de loyer {paiement_id}: {e}")
            raise e
    
    def delete_paiement_loyer(self, paiement_id: int) -> bool:
        """Supprimer un paiement de loyer"""
        try:
            with self.get_session() as session:
                paiement = session.query(PaiementLoyer).filter(PaiementLoyer.id_paiement == paiement_id).first()
                if not paiement:
                    return False
                
                session.delete(paiement)
                session.commit()
                
                print(f"✅ Paiement de loyer supprimé: ID {paiement_id}")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du paiement de loyer {paiement_id}: {e}")
            raise e
    
    def get_paiements_by_bail(self, bail_id: int) -> List[Dict[str, Any]]:
        """Récupérer tous les paiements pour un bail"""
        try:
            with self.get_session() as session:
                paiements = session.query(PaiementLoyer).filter(
                    PaiementLoyer.id_bail == bail_id
                ).order_by(PaiementLoyer.annee, PaiementLoyer.mois).all()
                
                return [paiement.to_dict() for paiement in paiements]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des paiements pour le bail {bail_id}: {e}")
            return []
    
    def get_paiements_by_building_and_period(self, building_ids: List[int], start_year: int, start_month: int, end_year: int, end_month: int) -> List[Dict[str, Any]]:
        """Récupérer les paiements de loyers pour des immeubles et une période donnée"""
        try:
            with self.get_session() as session:
                # Construire la condition de période
                start_date = date(start_year, start_month, 1)
                end_date = date(end_year, end_month, 28)  # Utiliser 28 pour éviter les problèmes de mois
                
                # Maintenant l'unité est directement sur le bail, pas sur le locataire
                paiements = session.query(PaiementLoyer).join(Bail).join(Unite, Bail.id_unite == Unite.id_unite).filter(
                    Unite.id_immeuble.in_(building_ids),
                    PaiementLoyer.annee >= start_year,
                    PaiementLoyer.annee <= end_year,
                    or_(
                        PaiementLoyer.annee > start_year,
                        and_(PaiementLoyer.annee == start_year, PaiementLoyer.mois >= start_month)
                    ),
                    or_(
                        PaiementLoyer.annee < end_year,
                        and_(PaiementLoyer.annee == end_year, PaiementLoyer.mois <= end_month)
                    )
                ).options(
                    joinedload(PaiementLoyer.bail).joinedload(Bail.locataire),
                    joinedload(PaiementLoyer.bail).joinedload(Bail.unite).joinedload(Unite.immeuble)
                ).all()
                
                return [paiement.to_dict() for paiement in paiements]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des paiements par immeuble et période: {e}")
            return []
    
    def get_or_create_paiement(self, bail_id: int, mois: int, annee: int) -> Dict[str, Any]:
        """Récupérer ou créer un paiement pour un bail, mois et année donnés"""
        try:
            with self.get_session() as session:
                paiement = session.query(PaiementLoyer).filter(
                    PaiementLoyer.id_bail == bail_id,
                    PaiementLoyer.mois == mois,
                    PaiementLoyer.annee == annee
                ).first()
                
                if paiement:
                    return paiement.to_dict()
                
                # Récupérer le bail pour obtenir le prix du loyer
                bail = session.query(Bail).filter(Bail.id_bail == bail_id).first()
                if not bail:
                    raise ValueError(f"Bail {bail_id} non trouvé")
                
                montant_loyer = float(bail.prix_loyer) if bail.prix_loyer else 0
                
                # Créer un nouveau paiement avec le montant du bail et la date par défaut
                from datetime import date
                nouveau_paiement = PaiementLoyer(
                    id_bail=bail_id,
                    mois=mois,
                    annee=annee,
                    date_paiement_reelle=date(annee, mois, 1),
                    montant_paye=montant_loyer
                )
                session.add(nouveau_paiement)
                session.commit()
                session.refresh(nouveau_paiement)
                
                print(f"✅ Nouveau paiement créé: Bail {bail_id}, {mois}/{annee}, Montant: {montant_loyer}$")
                return nouveau_paiement.to_dict()
        except Exception as e:
            print(f"❌ Erreur lors de la récupération/création du paiement: {e}")
            raise e

# Instance globale du service
db_service_francais = DatabaseServiceFrancais()
