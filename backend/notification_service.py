#!/usr/bin/env python3
"""
Service pour générer automatiquement les notifications
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models_auth import Notification, Utilisateur, DemandeAcces

def create_notification(
    db: Session,
    id_utilisateur: int,
    type: str,
    titre: str,
    message: str,
    priorite: str = "info",
    lien: Optional[str] = None,
    donnees: Optional[Dict[str, Any]] = None
) -> Notification:
    """
    Créer une notification pour un utilisateur
    """
    notification = Notification(
        id_utilisateur=id_utilisateur,
        type=type,
        titre=titre,
        message=message,
        priorite=priorite,
        lue=False,
        lien=lien,
        donnees=json.dumps(donnees) if donnees else None
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification

def generate_notifications_for_user(db: Session, user: Utilisateur):
    """
    Générer toutes les notifications pour un utilisateur
    Appelé lors de la connexion ou périodiquement
    """
    notifications_created = []
    
    # Seulement pour les admins
    if user.role != 'admin':
        return notifications_created
    
    # 1. Loyers non payés
    try:
        from database_service_francais import DatabaseServiceFrancais
        db_service = DatabaseServiceFrancais()
        
        # Récupérer tous les baux actifs
        leases = db_service.get_leases()
        
        # Obtenir le mois dernier
        today = datetime.now()
        last_month = today - timedelta(days=30)
        last_month_year = last_month.year
        last_month_month = last_month.month
        
        unpaid_count = 0
        for lease in leases:
            if not lease.get('date_debut') or not lease.get('date_fin'):
                continue
            
            lease_start = datetime.fromisoformat(lease['date_debut'].split('T')[0] if isinstance(lease['date_debut'], str) else lease['date_debut'].isoformat().split('T')[0])
            lease_end = datetime.fromisoformat(lease['date_fin'].split('T')[0] if isinstance(lease['date_fin'], str) else lease['date_fin'].isoformat().split('T')[0])
            check_date = datetime(last_month_year, last_month_month, 1)
            
            if check_date >= lease_start and check_date <= lease_end:
                payments = db_service.get_paiements_by_bail(lease['id_bail'])
                has_payment = any(p['annee'] == last_month_year and p['mois'] == last_month_month for p in payments)
                
                if not has_payment:
                    unpaid_count += 1
        
        if unpaid_count > 0:
            # Vérifier si une notification existe déjà pour ce mois
            existing = db.query(Notification).filter(
                Notification.id_utilisateur == user.id_utilisateur,
                Notification.type == "loyer_non_paye",
                Notification.lue == False
            ).first()
            
            if not existing:
                notification = create_notification(
                    db=db,
                    id_utilisateur=user.id_utilisateur,
                    type="loyer_non_paye",
                    titre=f"{unpaid_count} loyer(s) non payé(s)",
                    message=f"{unpaid_count} loyer(s) du mois dernier n'ont pas été payés.",
                    priorite="urgent",
                    lien="/",
                    donnees={"count": unpaid_count}
                )
                notifications_created.append(notification)
    
    except Exception as e:
        print(f"⚠️ Erreur génération notification loyers: {e}")
    
    # 2. Factures à payer
    try:
        from main import CONSTRUCTION_ENABLED
        if CONSTRUCTION_ENABLED:
            from database_construction import get_construction_db_context
            from models_construction import FactureST
            
            with get_construction_db_context() as construction_db:
                pending_invoices = construction_db.query(FactureST).filter(
                    FactureST.date_de_paiement == None
                ).all()
                
                if pending_invoices:
                    invoice_count = len(pending_invoices)
                    total_amount = sum(inv.montant for inv in pending_invoices)
                    
                    # Vérifier si une notification existe déjà
                    existing = db.query(Notification).filter(
                        Notification.id_utilisateur == user.id_utilisateur,
                        Notification.type == "facture_a_payer",
                        Notification.lue == False
                    ).first()
                    
                    if not existing:
                        notification = create_notification(
                            db=db,
                            id_utilisateur=user.id_utilisateur,
                            type="facture_a_payer",
                            titre=f"{invoice_count} facture(s) à payer",
                            message=f"{invoice_count} facture(s) de sous-traitants en attente de paiement (Total: {total_amount:.2f}$).",
                            priorite="important",
                            lien="/invoices-st",
                            donnees={"count": invoice_count, "total_amount": total_amount}
                        )
                        notifications_created.append(notification)
    
    except Exception as e:
        print(f"⚠️ Erreur génération notification factures: {e}")
    
    # 3. Demandes d'accès en attente (seulement pour admins principaux)
    try:
        if user.est_admin_principal:
            pending_requests = db.query(DemandeAcces).filter(
                DemandeAcces.id_compagnie == user.id_compagnie,
                DemandeAcces.statut == "en_attente"
            ).count()
            
            if pending_requests > 0:
                # Vérifier si une notification existe déjà
                existing = db.query(Notification).filter(
                    Notification.id_utilisateur == user.id_utilisateur,
                    Notification.type == "demande_acces",
                    Notification.lue == False
                ).first()
                
                if not existing:
                    notification = create_notification(
                        db=db,
                        id_utilisateur=user.id_utilisateur,
                        type="demande_acces",
                        titre=f"{pending_requests} demande(s) d'accès en attente",
                        message=f"{pending_requests} demande(s) d'accès à votre compagnie sont en attente d'approbation.",
                        priorite="important",
                        lien="/pending-approval",
                        donnees={"count": pending_requests}
                    )
                    notifications_created.append(notification)
    
    except Exception as e:
        print(f"⚠️ Erreur génération notification demandes: {e}")
    
    # 4. Baux qui expirent bientôt (30 jours)
    try:
        from database_service_francais import DatabaseServiceFrancais
        db_service = DatabaseServiceFrancais()
        
        leases = db_service.get_leases()
        today = datetime.now().date()
        expiration_date = today + timedelta(days=30)
        
        expiring_count = 0
        for lease in leases:
            if not lease.get('date_fin'):
                continue
            
            lease_end = datetime.fromisoformat(lease['date_fin'].split('T')[0] if isinstance(lease['date_fin'], str) else lease['date_fin'].isoformat().split('T')[0]).date()
            
            # Vérifier si le bail expire dans les 30 prochains jours
            if today <= lease_end <= expiration_date:
                expiring_count += 1
        
        if expiring_count > 0:
            # Vérifier si une notification existe déjà
            existing = db.query(Notification).filter(
                Notification.id_utilisateur == user.id_utilisateur,
                Notification.type == "bail_expire",
                Notification.lue == False
            ).first()
            
            if not existing:
                notification = create_notification(
                    db=db,
                    id_utilisateur=user.id_utilisateur,
                    type="bail_expire",
                    titre=f"{expiring_count} bail(s) expire(nt) bientôt",
                    message=f"{expiring_count} bail(s) expire(nt) dans les 30 prochains jours.",
                    priorite="important",
                    lien="/leases",
                    donnees={"count": expiring_count}
                )
                notifications_created.append(notification)
    
    except Exception as e:
        print(f"⚠️ Erreur génération notification baux: {e}")
    
    return notifications_created

