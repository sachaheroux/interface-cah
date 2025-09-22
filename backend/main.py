from fastapi import FastAPI, HTTPException, UploadFile, File
# Test deploiement backend - ligne propre
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
from datetime import datetime
import json
import os
import platform
import shutil
import re

# Imports pour SQLite
from database import db_manager, init_database
from database_service_francais import db_service_francais
from backup_service import backup_service
from validation_service import data_validator, consistency_checker, ValidationLevel
from monitoring_service import database_monitor

app = FastAPI(
    title="Interface CAH API",
    description="API pour la gestion de construction - Interface CAH",
    version="1.0.0"
)

# Initialiser la base de données au démarrage
@app.on_event("startup")
async def startup_event():
    """Initialiser la base de données au démarrage de l'application"""
    print("🚀 Démarrage de l'application Interface CAH...")
    print("🗄️ Initialisation de la base de données SQLite...")
    
    if init_database():
        print("✅ Base de données initialisée avec succès")
    else:
        print("❌ Erreur lors de l'initialisation de la base de données")
        raise Exception("Impossible d'initialiser la base de données")

# Configuration CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser toutes les origines pour éviter les problèmes CORS
    allow_credentials=False,  # Doit être False quand allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ========================================
# ENDPOINT POUR LES CONSTANTES (défini tôt pour éviter les erreurs)
# ========================================


# Modèles Pydantic pour la validation des données

# Modèles Pydantic français pour toutes les entités

class BuildingCreateFrancais(BaseModel):
    nom_immeuble: str
    adresse: str
    ville: str
    province: str
    code_postal: str
    pays: str = "Canada"
    nbr_unite: int
    annee_construction: int
    prix_achete: float = 0
    mise_de_fond: float = 0
    taux_interet: float = 0
    valeur_actuel: float = 0
    proprietaire: str = ""
    banque: str = ""
    contracteur: str = ""
    notes: str = ""

class BuildingUpdate_transactionFrancais(BaseModel):
    nom_immeuble: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    province: Optional[str] = None
    code_postal: Optional[str] = None
    pays: Optional[str] = None
    nbr_unite: Optional[int] = None
    annee_construction: Optional[int] = None
    prix_achete: Optional[float] = None
    mise_de_fond: Optional[float] = None
    taux_interet: Optional[float] = None
    valeur_actuel: Optional[float] = None
    proprietaire: Optional[str] = None
    banque: Optional[str] = None
    contracteur: Optional[str] = None
    notes: Optional[str] = None

class UnitCreateFrancais(BaseModel):
    id_immeuble: int
    adresse_unite: str
    type: str
    nbr_chambre: int
    nbr_salle_de_bain: float
    notes: str = ""

class UnitUpdate_transactionFrancais(BaseModel):
    id_immeuble: Optional[int] = None
    adresse_unite: Optional[str] = None
    type: Optional[str] = None
    nbr_chambre: Optional[int] = None
    nbr_salle_de_bain: Optional[float] = None
    notes: Optional[str] = None

class TenantCreateFrancais(BaseModel):
    id_unite: int
    nom: str
    prenom: str
    email: str = ""
    telephone: str = ""
    statut: str = "actif"
    notes: str = ""

class TenantUpdate_transactionFrancais(BaseModel):
    id_unite: Optional[int] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None

class TransactionCreateFrancais(BaseModel):
    id_immeuble: int
    type: str
    categorie: str
    montant: float
    date_de_transaction: str
    reference: str = ""
    source: str = ""
    pdf_transaction: str = ""
    methode_de_paiement: str = ""
    notes: str = ""

class TransactionUpdateFrancais(BaseModel):
    id_immeuble: Optional[int] = None
    type: Optional[str] = None
    categorie: Optional[str] = None
    montant: Optional[float] = None
    date_de_transaction: Optional[str] = None
    reference: Optional[str] = None
    source: Optional[str] = None
    pdf_transaction: Optional[str] = None
    methode_de_paiement: Optional[str] = None
    notes: Optional[str] = None

class LeaseCreateFrancais(BaseModel):
    id_locataire: int
    date_transaction_debut: str
    date_transaction_fin: str
    prix_loyer: float
    methode_paiement: str = "Virement bancaire"
    pdf_bail: str = ""

class LeaseUpdate_transactionFrancais(BaseModel):
    id_locataire: Optional[int] = None
    date_transaction_debut: Optional[str] = None
    date_transaction_fin: Optional[str] = None
    prix_loyer: Optional[float] = None
    methode_paiement: Optional[str] = None
    pdf_bail: Optional[str] = None

# Configuration du répertoire de données pour les documents
if platform.system() == "Windows" or os.environ.get("ENVIRONMENT") == "development":
    DATA_DIR = os.environ.get("DATA_DIR", "./data")
else:
    DATA_DIR = os.environ.get("DATA_DIR", "/opt/render/project/src/data")

# Créer le répertoire de données s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# Route de test de base
@app.get("/")
async def root():
    return {"message": "Interface CAH API - Système de gestion de construction"}

# Route de santé pour vérifier que l'API fonctionne
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API fonctionnelle"}

# ========================================
# ROUTES POUR LES BAUX
# ========================================

@app.get("/api/leases")
async def get_leases():
    """Récupérer tous les baux"""
    try:
        leases = db_service_francais.get_leases()
        return {"data": leases}
    except Exception as e:
        print(f"Erreur lors de la récupération des baux: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.get("/api/leases/{lease_id}")
async def get_lease(lease_id: int):
    """Récupérer un bail par ID"""
    try:
        lease = db_service_francais.get_lease(lease_id)
        if not lease:
            raise HTTPException(status_code=404, detail="Bail non trouvé")
        return {"data": lease}
    except Exception as e:
        print(f"Erreur lors de la récupération du bail: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.post("/api/leases")
async def create_lease(lease_data: LeaseCreateFrancais):
    """Créer un nouveau bail"""
    try:
        lease_dict = lease_data.dict()
        created_lease = db_service_francais.create_lease(lease_dict)
        return {"data": created_lease, "message": "Bail créé avec succès"}
    except Exception as e:
        print(f"Erreur lors de la création du bail: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.put("/api/leases/{lease_id}")
async def update_transaction_lease(lease_id: int, lease_data: LeaseUpdate_transactionFrancais):
    """Mettre à jour un bail"""
    try:
        lease_dict = lease_data.dict(exclude_unset=True)
        update_transactiond_lease = db_service_francais.update_transaction_lease(lease_id, lease_dict)
        if not update_transactiond_lease:
            raise HTTPException(status_code=404, detail="Bail non trouvé")
        return {"data": update_transactiond_lease, "message": "Bail mis à jour avec succès"}
    except Exception as e:
        print(f"Erreur lors de la mise à jour du bail: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.delete("/api/leases/{lease_id}")
async def delete_lease(lease_id: int):
    """Supprimer un bail et son PDF associé"""
    try:
        # Récupérer le bail pour obtenir le nom du PDF
        lease = db_service_francais.get_lease(lease_id)
        if not lease:
            raise HTTPException(status_code=404, detail="Bail non trouvé")
        
        # Supprimer le PDF de Backblaze B2 s'il existe
        if lease.get('pdf_bail'):
            try:
                from storage_service import get_storage_service
                storage_service = get_storage_service()
                
                # Construire la clé S3 (peut être un nom simple ou une clé complète)
                pdf_key = lease['pdf_bail']
                if not '/' in pdf_key:
                    pdf_key = f"documents/{pdf_key}"
                
                # Supprimer le PDF
                if storage_service.delete_pdf(pdf_key):
                    print(f"✅ PDF du bail supprimé de Backblaze B2: {pdf_key}")
                else:
                    print(f"⚠️ PDF du bail non trouvé sur Backblaze B2: {pdf_key}")
            except Exception as pdf_error:
                print(f"⚠️ Erreur lors de la suppression du PDF du bail: {pdf_error}")
                # Continuer même si la suppression du PDF échoue
        
        # Supprimer le bail de la base de données
        success = db_service_francais.delete_lease(lease_id)
        if not success:
            raise HTTPException(status_code=404, detail="Bail non trouvé")
        
        return {"message": "Bail et PDF supprimés avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression du bail: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

# Routes temporaires pour les modules (à développer plus tard)
@app.get("/api/dashboard")
async def get_dashboard_data():
    """Retourner les données du tableau de bord calculées à partir des vrais immeubles"""
    try:
        # Récupérer tous les immeubles via le service SQLite
        buildings = db_service_francais.get_buildings()
        
        # Calculer les statistiques réelles
        total_buildings = len(buildings)
        total_units = sum(building.get("nbr_unite", 0) for building in buildings)
        total_portfolio_value = sum(building.get("valeur_actuel", 0) for building in buildings)
        
        # Calculer le taux d'occupation (simulation : 85-95% d'occupation selon l'âge)
        occupied_units = 0
        for building in buildings:
            units = building.get("nbr_unite", 0)
            year_built = building.get("annee_construction", 2020)
            current_year = 2024
            building_age = current_year - year_built
            
            # Taux d'occupation basé sur l'âge : plus récent = meilleur taux
            if building_age <= 2:
                occupancy_rate = 0.95  # 95% pour immeubles récents
            elif building_age <= 5:
                occupancy_rate = 0.90  # 90% pour immeubles moyens
            else:
                occupancy_rate = 0.85  # 85% pour immeubles plus anciens
            
            occupied_units += int(units * occupancy_rate)
        
        # Calculer le pourcentage global d'occupation
        occupancy_percentage = (occupied_units / total_units * 100) if total_units > 0 else 0
        
        return {
            "totalBuildings": total_buildings,
            "totalUnits": total_units,
            "portfolioValue": total_portfolio_value,
            "occupancyRate": round(occupancy_percentage, 1),
            "recentActivity": [
                {
                    "type": "info",
                    "message": f"Portfolio actuel : {total_buildings} immeubles",
                    "timestamp": "2025-06-23T12:00:00Z"
                },
                {
                    "type": "success", 
                    "message": f"Total unités : {total_units}",
                    "timestamp": "2025-06-23T11:30:00Z"
                },
                {
                    "type": "info",
                    "message": f"Valeur portfolio : {total_portfolio_value:,.0f} $",
                    "timestamp": "2025-06-23T11:00:00Z"
                },
                {
                    "type": "success",
                    "message": f"Taux d'occupation : {round(occupancy_percentage, 1)}%",
                    "timestamp": "2025-06-23T10:30:00Z"
                }
            ]
        }
    except Exception as e:
        return {
            "totalBuildings": 0,
            "totalUnits": 0, 
            "portfolioValue": 0,
            "occupancyRate": 0,
            "recentActivity": [
                {
                    "type": "info",
                    "message": "Aucun immeuble dans le portfolio",
                    "timestamp": "2025-06-23T12:00:00Z"
                }
            ]
        }

# Routes CRUD pour les immeubles avec SQLite

@app.get("/api/buildings")
async def get_buildings():
    """Récupérer tous les immeubles"""
    try:
        buildings = db_service_francais.get_buildings()
        return buildings
    except Exception as e:
        print(f"❌ Erreur lors du chargement des immeubles: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des immeubles: {str(e)}")

@app.get("/api/buildings/{building_id}")
async def get_building(building_id: int):
    """Récupérer un immeuble spécifique par ID"""
    try:
        building = db_service_francais.get_building(building_id)
        if not building:
            raise HTTPException(status_code=404, detail="Immeuble non trouvé")
        return building
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'immeuble: {str(e)}")

@app.post("/api/buildings")
async def create_building(building_data: BuildingCreateFrancais):
    """Créer un nouvel immeuble avec le format français"""
    try:
        # Debug: Afficher les données reçues
        print(f"🔍 DEBUG - Données reçues: {building_data}")
        print(f"🔍 DEBUG - Type: {type(building_data)}")
        
        # Convertir en dictionnaire pour le service
        building_dict = building_data.dict()
        print(f"🔍 DEBUG - Dictionnaire: {building_dict}")
        
        # Créer l'immeuble via le service SQLite
        new_building = db_service_francais.create_building(building_dict)
        
        return new_building
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'immeuble: {e}")
        print(f"❌ Type d'erreur: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'immeuble: {str(e)}")

@app.put("/api/buildings/{building_id}")
async def update_building(building_id: int, building_data: BuildingUpdate_transactionFrancais):
    """Mettre à jour un immeuble existant avec le format français"""
    try:
        # Convertir en dictionnaire pour le service
        building_dict = building_data.dict(exclude_unset=True)
        
        # Mettre à jour l'immeuble via le service SQLite
        updated_building = db_service_francais.update_building(building_id, building_dict)
        
        if not updated_building:
            raise HTTPException(status_code=404, detail="Immeuble non trouvé")
        
        return updated_building
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de l'immeuble: {str(e)}")

@app.delete("/api/buildings/{building_id}")
async def delete_building(building_id: int):
    """Supprimer un immeuble"""
    try:
        # Supprimer l'immeuble via le service SQLite
        success = db_service_francais.delete_building(building_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Immeuble non trouvé")
        
        return {"message": "Immeuble supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

# Routes CRUD pour les locataires avec persistance
@app.get("/api/tenants")
async def get_tenants():
    """Récupérer tous les locataires"""
    try:
        tenants = db_service_francais.get_tenants()
        return {"data": tenants}
    except Exception as e:
        print(f"Erreur lors du chargement des locataires: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.get("/api/tenants/{tenant_id}")
async def get_tenant(tenant_id: int):
    """Récupérer un locataire spécifique par ID"""
    try:
        tenant = db_service_francais.get_tenant(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Locataire non trouvé")
        return {"data": tenant}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du locataire: {str(e)}")

@app.post("/api/tenants")
async def create_tenant(tenant_data: TenantCreateFrancais):
    """Créer un nouveau locataire avec le format français"""
    try:
        # Convertir en dictionnaire pour le service
        tenant_dict = tenant_data.dict()
        
        # Créer le locataire via le service SQLite
        new_tenant = db_service_francais.create_tenant(tenant_dict)
        
        return {"data": new_tenant}
    except Exception as e:
        print(f"Erreur lors de la création du locataire: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du locataire: {str(e)}")

@app.put("/api/tenants/{tenant_id}")
async def update_tenant(tenant_id: int, tenant_data: TenantUpdate_transactionFrancais):
    """Mettre à jour un locataire existant avec le format français"""
    try:
        # Convertir en dictionnaire pour le service
        tenant_dict = tenant_data.dict(exclude_unset=True)
        
        # Mettre à jour via le service SQLite
        updated_tenant = db_service_francais.update_tenant(tenant_id, tenant_dict)
        
        if not updated_tenant:
            raise HTTPException(status_code=404, detail="Locataire non trouvé")
        
        print(f"Locataire mis à jour: {tenant_id}")
        return {"data": updated_tenant}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la mise à jour du locataire: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.delete("/api/tenants/{tenant_id}")
async def delete_tenant(tenant_id: int):
    """Supprimer un locataire"""
    try:
        # Supprimer le locataire via le service SQLite
        success = db_service_francais.delete_tenant(tenant_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Locataire non trouvé")
        
        return {"message": "Locataire supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression du locataire: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.get("/api/maintenance")
async def get_maintenance():
    """Liste des entretiens"""
    return [
        {"id": 1, "building": "Immeuble A", "type": "Plomberie", "status": "pending", "priority": "high"},
        {"id": 2, "building": "Immeuble B", "type": "Électricité", "status": "in_progress", "priority": "medium"},
        {"id": 3, "building": "Immeuble C", "type": "Peinture", "status": "completed", "priority": "low"}
    ]

@app.get("/api/employees")
async def get_employees():
    """Liste des employés"""
    return [
        {"id": 1, "name": "Marc Ouvrier", "role": "Contremaître", "status": "active"},
        {"id": 2, "name": "Sophie Tech", "role": "Électricienne", "status": "active"},
        {"id": 3, "name": "Paul Plombier", "role": "Plombier", "status": "active"}
    ]

# Routes CRUD pour les assignations locataires-unités avec persistance
@app.post("/api/tenants/create-with-lease")
async def create_tenant_with_lease(data: dict):
    """Créer un locataire avec son bail - LOGIQUE SIMPLE ET FIABLE"""
    try:
        print(f"🔍 DEBUG - create_tenant_with_lease reçu: {data}")
        
        # NOUVEAU FORMAT : data contient {tenant: {...}, lease: {...}}
        tenant_data = data.get("tenant", {})
        lease_data = data.get("lease", {})
        
        # Fallback pour l'ancien format
        if not tenant_data and not lease_data:
            tenant_data = {
                "name": data.get("name", "").strip(),
                "email": data.get("email", "").strip(),
                "phone": data.get("phone", "").strip(),
                "notes": data.get("notes", "")
            }
            lease_data = {
                "unitId": data.get("unitId"),
                "moveInDate": data.get("moveInDate"),
                "moveOutDate": data.get("moveOutDate"),
                "rentAmount": data.get("rentAmount", 0),
                "depositAmount": data.get("depositAmount", 0),
                "leaseStartDate": data.get("leaseStartDate"),
                "leaseEndDate": data.get("leaseEndDate"),
                "rentDueDay": data.get("rentDueDay", 1),
                "notes": data.get("notes", "")
            }
        
        # Validation basique - accepter le format français
        nom = tenant_data.get("nom", "").strip()
        prenom = tenant_data.get("prenom", "").strip()
        name = tenant_data.get("name", "").strip()
        
        print(f"🔍 DEBUG - Validation: nom='{nom}', prenom='{prenom}', name='{name}'")
        
        # Si on a nom et prenom, les combiner en name
        if nom and prenom:
            tenant_data["name"] = f"{nom} {prenom}"
            print(f"✅ Nom combiné: {tenant_data['name']}")
        elif not name and not (nom and prenom):
            print(f"❌ Validation échouée: nom='{nom}', prenom='{prenom}', name='{name}'")
            raise HTTPException(status_code=400, detail="Le nom et prénom du locataire sont obligatoires")
        
        if not lease_data.get("unitId"):
            raise HTTPException(status_code=400, detail="L'unité est obligatoire")
        
        # 1. CRÉER LE LOCATAIRE (informations personnelles uniquement)
        # Mapper les champs anglais vers français pour le service
        tenant_data_francais = {
            "id_unite": lease_data.get("unitId"),
            "nom": tenant_data.get("nom", ""),
            "prenom": tenant_data.get("prenom", ""),
            "email": tenant_data.get("email", ""),
            "telephone": tenant_data.get("telephone", ""),
            "statut": tenant_data.get("statut", "actif"),
            "notes": tenant_data.get("notes", "")
        }
        print(f"📝 Création du locataire: {tenant_data_francais['nom']} {tenant_data_francais['prenom']}")
        created_tenant = db_service_francais.create_tenant(tenant_data_francais)
        tenant_id = created_tenant["id_locataire"]
        print(f"✅ Locataire créé avec ID: {tenant_id}")
        
        # 2. CRÉER LE BAIL avec les données de bail
        print(f"🏠 Création du bail pour l'unité: {lease_data['unitId']}")
        lease_data["tenantId"] = tenant_id
        
        # Debug des données avant nettoyage
        print(f"🔍 DEBUG - lease_data avant nettoyage: {lease_data}")
        print(f"🔍 DEBUG - leaseStartDate: {lease_data.get('leaseStartDate')}")
        print(f"🔍 DEBUG - leaseEndDate: {lease_data.get('leaseEndDate')}")
        
        # Supprimer les valeurs None/vides SAUF pour les date_transactions obligatoires
        lease_data_cleaned = {k: v for k, v in lease_data.items() if v is not None and v != ""}
        
        # Debug des données après nettoyage
        print(f"🔍 DEBUG - lease_data après nettoyage: {lease_data_cleaned}")
        
        # Vérifier que les date_transactions obligatoires sont présentes
        if not lease_data_cleaned.get('leaseStartDate'):
            print(f"❌ ERREUR: leaseStartDate manquant dans lease_data")
            raise HTTPException(status_code=400, detail="La date_transaction de début du bail est obligatoire")
        
        if not lease_data_cleaned.get('leaseEndDate'):
            print(f"❌ ERREUR: leaseEndDate manquant dans lease_data")
            raise HTTPException(status_code=400, detail="La date_transaction de fin du bail est obligatoire")
        
        # Créer le bail via le service
        lease_data_francais = {
            "id_locataire": tenant_id,
            "date_transaction_debut": lease_data_cleaned.get("leaseStartDate"),
            "date_transaction_fin": lease_data_cleaned.get("leaseEndDate"),
            "prix_loyer": lease_data_cleaned.get("rentAmount", 0),
            "methode_paiement": lease_data_cleaned.get("paymentMethod", "Virement bancaire"),
            "pdf_bail": lease_data_cleaned.get("pdfLease", "")
        }
        
        print(f"🔍 DEBUG - Données envoyées au service create_lease: {lease_data_francais}")
        created_lease = db_service_francais.create_lease(lease_data_francais)
        print(f"🔍 DEBUG - Type de created_lease: {type(created_lease)}")
        print(f"🔍 DEBUG - Contenu de created_lease: {created_lease}")
        print(f"✅ Bail créé avec ID: {created_lease['id_bail']}")
        print(f"🔍 DEBUG - Bail créé complet: {created_lease}")
        
        return {
            "data": {
                "tenant": created_tenant,
                "lease": created_lease,
                "message": "Locataire et bail créés avec succès"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")

@app.get("/api/projects")
async def get_projects():
    """Liste des projets de construction"""
    return [
        {"id": 1, "name": "Nouveau Complexe D", "status": "planning", "progress": 10},
        {"id": 2, "name": "Rénovation Immeuble E", "status": "in_progress", "progress": 65},
        {"id": 3, "name": "Extension Immeuble F", "status": "completed", "progress": 100}
    ]

# ========================================
# ROUTES POUR LES RAPPORTS D'IMMEUBLES
# ========================================

@app.post("/api/building-reports")
async def create_building_report(report_data: dict):
    """Créer ou mettre à jour un rapport d'immeuble"""
    try:
        building_id = report_data.get("buildingId")
        year = report_data.get("year")
        
        # Vérifier si un rapport existe déjà pour cet immeuble et cette année
        reports = db_service_francais.get_building_reports()
        existing_report = next((r for r in reports if r.get("buildingId") == building_id and r.get("year") == year), None)
        
        if existing_report:
            # Mettre à jour le rapport existant via SQLite
            update_transactiond_report = db_service_francais.update_transaction_building_report(existing_report["id"], report_data)
        else:
            # Créer un nouveau rapport via SQLite
            update_transactiond_report = db_service_francais.create_building_report(report_data)
        
        print(f"Rapport immeuble sauvegardé: {building_id} - {year}")
        return {"data": update_transactiond_report}
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du rapport d'immeuble: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde du rapport d'immeuble: {str(e)}")

@app.delete("/api/building-reports/{report_id}")
async def delete_building_report(report_id: int):
    """Supprimer un rapport d'immeuble"""
    try:
        # Supprimer via le service SQLite
        success = db_service_francais.delete_building_report(report_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
        print(f"Rapport immeuble supprimé: {report_id}")
        return {"message": "Rapport supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression du rapport d'immeuble: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

# ========================================
# ROUTES POUR LES RAPPORTS D'UNITÉS
# ========================================

@app.post("/api/unit-reports")
async def create_unit_report(report_data: dict):
    """Créer un nouveau rapport d'unité mensuel"""
    try:
        # Créer le rapport via le service SQLite
        new_report = db_service_francais.create_unit_report(report_data)
        
        print(f"Rapport unité créé: {report_data.get('unitId')} - {report_data.get('year')}/{report_data.get('month')}")
        return {"data": new_report}
    except Exception as e:
        print(f"Erreur lors de la création du rapport d'unité: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du rapport d'unité: {str(e)}")

@app.delete("/api/unit-reports/{report_id}")
async def delete_unit_report(report_id: int):
    """Supprimer un rapport d'unité"""
    try:
        # Supprimer via le service SQLite
        success = db_service_francais.delete_unit_report(report_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
        print(f"Rapport d'unité supprimé: {report_id}")
        return {"message": "Rapport d'unité supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression du rapport d'unité: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

# ========================================
# ROUTES POUR LES UNITÉS
# ========================================

# Endpoint supprimé - doublon avec celui ci-dessous

@app.get("/api/units/{unit_id}")
async def get_unit(unit_id: int):
    """Récupérer une unité par ID"""
    try:
        unit = db_service_francais.get_unit(unit_id)
        if not unit:
            raise HTTPException(status_code=404, detail="Unité non trouvée")
        return {"data": unit}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors du chargement de l'unité: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.delete("/api/units/{unit_id}")
async def delete_unit(unit_id: int):
    """Supprimer une unité"""
    try:
        # Supprimer via le service SQLite
        success = db_service_francais.delete_unit(unit_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Unité non trouvée")
        
        print(f"Unité supprimée: {unit_id}")
        return {"message": "Unité supprimée avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression de l'unité: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Uploader un document (PDF, image, etc.) vers Backblaze B2"""
    try:
        # Vérifier le type de fichier
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
        
        # Lire le contenu du fichier
        file_content = await file.read()
        
        # Upload vers Backblaze B2
        from storage_service import get_storage_service
        storage_service = get_storage_service()
        
        result = storage_service.upload_pdf(
            file_content=file_content,
            original_filename=file.filename,
            folder="documents"
        )
        
        if result["success"]:
            print(f"✅ Document uploadé vers Backblaze B2: {result['filename']}")
            return {
                "message": "Document uploadé avec succès",
                "filename": result["filename"],
                "original_filename": result["original_filename"],
                "s3_key": result["s3_key"],
                "file_url": result["file_url"],
                "size": result["size"]
            }
        else:
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload vers Backblaze B2: {result['error']}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")

@app.get("/api/documents")
async def list_documents():
    """Lister tous les documents disponibles depuis Backblaze B2"""
    try:
        from storage_service import get_storage_service
        storage_service = get_storage_service()
        
        # Lister les fichiers depuis Backblaze B2
        files = storage_service.list_pdfs(folder="documents")
        
        return {"documents": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des documents: {str(e)}")

@app.get("/api/documents/{filename}")
async def get_document(filename: str):
    """Servir un document (PDF, image, etc.) depuis Backblaze B2"""
    try:
        # Le filename peut être soit un nom simple soit une clé S3 complète
        # Si c'est une clé S3 (contient '/'), l'utiliser directement
        # Sinon, chercher dans le dossier documents
        if '/' in filename:
            s3_key = filename
        else:
            s3_key = f"documents/{filename}"
        
        # Télécharger depuis Backblaze B2
        from storage_service import get_storage_service
        storage_service = get_storage_service()
        
        file_content = storage_service.download_pdf(s3_key)
        
        if file_content is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Document non trouvé: {filename}"
            )
        
        # Retourner le fichier en mémoire
        from fastapi.responses import Response
        return Response(
            content=file_content,
            media_type='application/pdf',
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Content-Length": str(len(file_content))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du document: {str(e)}")

@app.get("/api/units")
async def get_units(skip: int = 0, limit: int = 100):
    """Récupérer toutes les unités"""
    try:
        units = db_service_francais.get_units(skip=skip, limit=limit)
        return {"data": units}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des unités: {str(e)}")

@app.get("/api/units/{unit_id}")
async def get_unit(unit_id: int):
    """Récupérer une unité par ID"""
    try:
        unit = db_service_francais.get_unit(unit_id)
        if not unit:
            raise HTTPException(status_code=404, detail="Unité non trouvée")
        return {"unit": unit}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'unité: {str(e)}")

@app.get("/api/buildings/{building_id}/units")
async def get_units_by_building(building_id: int):
    """Récupérer toutes les unités d'un immeuble"""
    try:
        units = db_service_francais.get_units_by_building(building_id)
        return {"units": units, "total": len(units)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des unités: {str(e)}")

@app.post("/api/units")
async def create_unit(unit_data: UnitCreateFrancais):
    """Créer une nouvelle unité avec le format français"""
    try:
        unit_dict = unit_data.dict()
        unit = db_service_francais.create_unit(unit_dict)
        return {"unit": unit, "message": "Unité créée avec succès"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'unité: {str(e)}")

@app.put("/api/units/{unit_id}")
async def update_unit(unit_id: int, unit_data: UnitUpdate_transactionFrancais):
    """Mettre à jour une unité avec le format français"""
    try:
        unit_dict = unit_data.dict(exclude_unset=True)
        unit = db_service_francais.update_unit(unit_id, unit_dict)
        if not unit:
            raise HTTPException(status_code=404, detail="Unité non trouvée")
        return {"unit": unit, "message": "Unité mise à jour avec succès"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de l'unité: {str(e)}")

@app.delete("/api/units/{unit_id}")
async def delete_unit(unit_id: int):
    """Supprimer une unité"""
    try:
        success = db_service_francais.delete_unit(unit_id)
        if not success:
            raise HTTPException(status_code=404, detail="Unité non trouvée")
        return {"message": "Unité supprimée avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de l'unité: {str(e)}")

# ========================================
# ROUTES POUR LES FACTURES
# ========================================

@app.get("/api/transactions")
async def get_transactions():
    """Récupérer toutes les transactions"""
    try:
        transactions = db_service_francais.get_transactions()
        return {"data": transactions}
    except Exception as e:
        print(f"Erreur lors du chargement des transactions: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des transactions: {str(e)}")

@app.get("/api/transactions/{transaction_id}")
async def get_transaction(transaction_id: int):
    """Récupérer une transaction spécifique par ID"""
    try:
        transaction = db_service_francais.get_transaction(transaction_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")
        return {"data": invoice}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la récupération de la transaction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la transaction: {str(e)}")

@app.post("/api/transactions")
async def create_transaction(transaction_data: TransactionCreateFrancais):
    """Créer une nouvelle transaction avec le format français"""
    try:
        # Convertir en dictionnaire pour le service
        invoice_dict = transaction_data.dict()
        
        # Créer la transaction via le service SQLite
        new_transaction = db_service_francais.create_transaction(invoice_dict)
        
        return {"data": new_transaction}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la création de la transaction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la transaction: {str(e)}")

@app.put("/api/transactions/{transaction_id}")
async def update_transaction_transaction(transaction_id: int, transaction_data: TransactionUpdateFrancais):
    """Mettre à jour une transaction existante avec le format français"""
    try:
        # Convertir en dictionnaire pour le service
        update_transaction_dict = transaction_data.dict(exclude_unset=True)
        
        # Mettre à jour via le service SQLite
        update_transactiond_transaction = db_service_francais.update_transaction_transaction(transaction_id, update_transaction_dict)
        
        if not update_transactiond_invoice:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")
        
        print(f"✅ Transaction mise à jour: {update_transactiond_invoice.get('invoiceNumber')}")
        return {"data": update_transactiond_invoice}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la transaction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la transaction: {str(e)}")

@app.delete("/api/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int):
    """Supprimer une transaction et son PDF associé"""
    try:
        # Récupérer la transaction pour obtenir le nom du PDF
        transaction = db_service_francais.get_transaction(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")
        
        # Supprimer le PDF de Backblaze B2 s'il existe
        if transaction.get('pdf_transaction'):
            try:
                from storage_service import get_storage_service
                storage_service = get_storage_service()
                
                # Construire la clé S3 (peut être un nom simple ou une clé complète)
                pdf_key = transaction['pdf_transaction']
                if not '/' in pdf_key:
                    pdf_key = f"documents/{pdf_key}"
                
                # Supprimer le PDF
                if storage_service.delete_pdf(pdf_key):
                    print(f"✅ PDF supprimé de Backblaze B2: {pdf_key}")
                else:
                    print(f"⚠️ PDF non trouvé sur Backblaze B2: {pdf_key}")
            except Exception as pdf_error:
                print(f"⚠️ Erreur lors de la suppression du PDF: {pdf_error}")
                # Continuer même si la suppression du PDF échoue
        
        # Supprimer la transaction de la base de données
        success = db_service_francais.delete_transaction(transaction_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")
        
        return {"message": "Transaction et PDF supprimés avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression de la transaction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


# ========================================
# ENDPOINTS DE SAUVEGARDE
# ========================================

@app.post("/api/backup/create")
async def create_backup():
    """Créer une sauvegarde manuelle de la base de données"""
    try:
        backup_path = backup_service.create_backup("manual")
        if backup_path:
            return {
                "success": True,
                "message": "Sauvegarde créée avec succès",
                "backup_path": backup_path
            }
        else:
            raise HTTPException(status_code=500, detail="Échec de la création de la sauvegarde")
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la sauvegarde: {str(e)}")

@app.get("/api/backup/list")
async def list_backups():
    """Lister toutes les sauvegardes disponibles"""
    try:
        backups = backup_service.list_backups()
        return {
            "success": True,
            "backups": backups,
            "count": len(backups)
        }
    except Exception as e:
        print(f"Erreur lors du listing des sauvegardes: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du listing des sauvegardes: {str(e)}")

@app.post("/api/backup/restore")
async def restore_backup(backup_path: str):
    """Restaurer une sauvegarde"""
    try:
        success = backup_service.restore_backup(backup_path)
        if success:
            return {
                "success": True,
                "message": "Sauvegarde restaurée avec succès"
            }
        else:
            raise HTTPException(status_code=500, detail="Échec de la restauration de la sauvegarde")
    except Exception as e:
        print(f"Erreur lors de la restauration: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la restauration: {str(e)}")

@app.post("/api/backup/start-automatic")
async def start_automatic_backups():
    """Démarrer les sauvegardes automatiques"""
    try:
        backup_service.start_automatic_backups()
        return {
            "success": True,
            "message": "Sauvegardes automatiques démarrées"
        }
    except Exception as e:
        print(f"Erreur lors du démarrage des sauvegardes automatiques: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du démarrage des sauvegardes automatiques: {str(e)}")

@app.post("/api/backup/stop-automatic")
async def stop_automatic_backups():
    """Arrêter les sauvegardes automatiques"""
    try:
        backup_service.stop_automatic_backups()
        return {
            "success": True,
            "message": "Sauvegardes automatiques arrêtées"
        }
    except Exception as e:
        print(f"Erreur lors de l'arrêt des sauvegardes automatiques: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'arrêt des sauvegardes automatiques: {str(e)}")

# ========================================
# ENDPOINTS DE VALIDATION
# ========================================

@app.get("/api/validation/run")
async def run_validation():
    """Exécuter une validation complète des données"""
    try:
        results = data_validator.validate_transaction_all()
        
        # Compter les résultats par niveau
        counts = {
            "info": 0,
            "warning": 0,
            "error": 0,
            "critical": 0
        }
        
        for result in results:
            counts[result.level.value] += 1
        
        return {
            "success": True,
            "message": "Validation terminée",
            "summary": {
                "total_issues": len(results),
                "counts": counts
            },
            "results": [
                {
                    "level": result.level.value,
                    "message": result.message,
                    "table": result.table,
                    "record_id": result.record_id,
                    "field": result.field,
                    "suggested_fix": result.suggested_fix
                }
                for result in results
            ]
        }
    except Exception as e:
        print(f"Erreur lors de la validation: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la validation: {str(e)}")

@app.get("/api/validation/consistency")
async def check_consistency():
    """Vérifier la cohérence des données"""
    try:
        issues = consistency_checker.check_orphaned_records()
        
        return {
            "success": True,
            "message": "Vérification de cohérence terminée",
            "issues": issues,
            "count": len(issues)
        }
    except Exception as e:
        print(f"Erreur lors de la vérification de cohérence: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification de cohérence: {str(e)}")

@app.get("/api/validation/health")
async def get_validation_health():
    """Obtenir un résumé de la santé des données"""
    try:
        # Validation rapide
        results = data_validator.validate_transaction_all()
        
        # Compter les problèmes critiques
        critical_issues = [r for r in results if r.level == ValidationLevel.CRITICAL]
        error_issues = [r for r in results if r.level == ValidationLevel.ERROR]
        warning_issues = [r for r in results if r.level == ValidationLevel.WARNING]
        
        # Déterminer le statut global
        if critical_issues:
            status = "critical"
        elif error_issues:
            status = "error"
        elif warning_issues:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "success": True,
            "status": status,
            "summary": {
                "critical": len(critical_issues),
                "errors": len(error_issues),
                "warnings": len(warning_issues),
                "total": len(results)
            },
            "message": f"Données {'saines' if status == 'healthy' else 'problématiques'}"
        }
    except Exception as e:
        print(f"Erreur lors de l'évaluation de la santé: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'évaluation de la santé: {str(e)}")

# ========================================
# ENDPOINTS DE MONITORING
# ========================================

@app.get("/api/monitoring/health")
async def get_database_health():
    """Obtenir un résumé complet de la santé de la base de données"""
    try:
        health_summary = database_monitor.get_health_summary()
        return {
            "success": True,
            "data": health_summary
        }
    except Exception as e:
        print(f"Erreur lors de la récupération de la santé: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la santé: {str(e)}")

@app.get("/api/monitoring/metrics")
async def get_database_metrics():
    """Obtenir les métriques actuelles de la base de données"""
    try:
        db_metrics = database_monitor.get_database_metrics()
        system_metrics = database_monitor.get_system_metrics()
        
        return {
            "success": True,
            "database": {
                "timestamp": db_metrics.timestamp.isoformat(),
                "status": db_metrics.status.value,
                "health_score": db_metrics.health_score,
                "file_size": db_metrics.file_size,
                "file_size_mb": round(db_metrics.file_size / (1024 * 1024), 2),
                "response_time": round(db_metrics.response_time, 3),
                "record_counts": db_metrics.record_counts,
                "total_records": sum(db_metrics.record_counts.values())
            },
            "system": {
                "timestamp": system_metrics.timestamp.isoformat(),
                "cpu_percent": round(system_metrics.cpu_percent, 1),
                "memory_percent": round(system_metrics.memory_percent, 1),
                "disk_percent": round(system_metrics.disk_percent, 1),
                "available_memory_gb": round(system_metrics.available_memory / (1024**3), 2),
                "available_disk_gb": round(system_metrics.available_disk / (1024**3), 2)
            }
        }
    except Exception as e:
        print(f"Erreur lors de la récupération des métriques: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métriques: {str(e)}")

@app.get("/api/monitoring/history")
async def get_metrics_history(hours: int = 24):
    """Obtenir l'historique des métriques"""
    try:
        history = database_monitor.get_metrics_history(hours)
        return {
            "success": True,
            "data": history
        }
    except Exception as e:
        print(f"Erreur lors de la récupération de l'historique: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'historique: {str(e)}")

@app.post("/api/monitoring/start")
async def start_monitoring(interval: int = 60):
    """Démarrer le monitoring automatique"""
    try:
        database_monitor.start_monitoring(interval)
        return {
            "success": True,
            "message": f"Monitoring démarré avec un intervalle de {interval} secondes"
        }
    except Exception as e:
        print(f"Erreur lors du démarrage du monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du démarrage du monitoring: {str(e)}")

@app.post("/api/monitoring/stop")
async def stop_monitoring():
    """Arrêter le monitoring automatique"""
    try:
        database_monitor.stop_monitoring()
        return {
            "success": True,
            "message": "Monitoring arrêté"
        }
    except Exception as e:
        print(f"Erreur lors de l'arrêt du monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'arrêt du monitoring: {str(e)}")

@app.get("/api/monitoring/status")
async def get_monitoring_status():
    """Obtenir le statut du monitoring"""
    try:
        return {
            "success": True,
            "monitoring_active": database_monitor.monitoring_active,
            "metrics_count": len(database_monitor.metrics_history),
            "system_metrics_count": len(database_monitor.system_history)
        }
    except Exception as e:
        print(f"Erreur lors de la récupération du statut: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du statut: {str(e)}")

@app.put("/api/leases/{lease_id}")
async def update_transaction_lease(lease_id: int, lease_data: LeaseUpdate_transactionFrancais):
    """Mettre à jour un bail existant"""
    try:
        # Convertir les données en dictionnaire
        update_transaction_data = lease_data.dict(exclude_unset=True)
        
        # Mettre à jour le bail
        update_transactiond_lease = db_service_francais.update_transaction_lease(lease_id, update_transaction_data)
        
        if update_transactiond_lease:
            return {
                "message": "Bail mis à jour avec succès",
                "lease": update_transactiond_lease
            }
        else:
            raise HTTPException(status_code=404, detail="Bail non trouvé")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

# ========================================
# ENDPOINTS POUR LES TRANSACTIONS
# ========================================

@app.post("/api/migrate/transactions")
async def migrate_transactions_table():
    """Migrer la table transactions vers la nouvelle structure"""
    try:
        from sqlalchemy import text
        
        with db_service_francais.get_session() as session:
            # Vérifier si la table existe et a les bonnes colonnes
            result = session.execute(text("PRAGMA table_info(transactions)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'type' not in columns or 'categorie' not in columns:
                print("🔄 Migration de la table transactions...")
                
                # Sauvegarder les données existantes
                existing_data = []
                if 'id_transaction' in columns:
                    result = session.execute(text("SELECT * FROM transactions"))
                    existing_data = [dict(row._mapping) for row in result.fetchall()]
                    print(f"📦 Sauvegarde de {len(existing_data)} transactions existantes")
                
                # Supprimer l'ancienne table
                session.execute(text("DROP TABLE IF EXISTS transactions"))
                print("🗑️ Ancienne table supprimée")
                
                # Créer la nouvelle table avec la bonne structure
                session.execute(text("""
                    CREATE TABLE transactions (
                        id_transaction INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_immeuble INTEGER NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        categorie VARCHAR(100) NOT NULL,
                        montant DECIMAL(12, 2) NOT NULL,
                        date_de_transaction DATE NOT NULL,
                        methode_de_paiement VARCHAR(50),
                        reference VARCHAR(100),
                        source VARCHAR(255),
                        pdf_transaction VARCHAR(255),
                        notes TEXT DEFAULT '',
                        date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                        date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id_immeuble) REFERENCES immeubles (id_immeuble) ON DELETE CASCADE
                    )
                """))
                print("✅ Nouvelle table créée")
                
                # Réinsérer les données existantes avec des valeurs par défaut
                for data in existing_data:
                    session.execute(text("""
                        INSERT INTO transactions (
                            id_immeuble, type, categorie, montant, date_de_transaction,
                            methode_de_paiement, reference, source, pdf_transaction, notes,
                            date_creation, date_modification
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """), (
                        data.get('id_immeuble', 1),
                        'depense',  # Valeur par défaut
                        'autre',    # Valeur par défaut
                        data.get('montant', 0),
                        data.get('date_de_transaction', data.get('date_transaction', '2025-01-01')),
                        data.get('methode_de_paiement', ''),
                        data.get('reference', ''),
                        data.get('source', ''),
                        data.get('pdf_transaction', data.get('pdf_document', '')),
                        data.get('notes', ''),
                        data.get('date_creation', '2025-01-01 00:00:00'),
                        data.get('date_modification', '2025-01-01 00:00:00')
                    ))
                
                session.commit()
                print(f"✅ {len(existing_data)} transactions migrées")
                
                return {"message": f"Table transactions migrée avec succès. {len(existing_data)} transactions migrées."}
            else:
                return {"message": "Table transactions déjà à jour."}
                
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la migration: {str(e)}")

@app.get("/api/transactions-constants")
async def get_transaction_constants():
    """Récupérer les constantes pour les transactions"""
    try:
        return {
            "types": [
                "revenu",
                "depense"
            ],
            "categories": [
                "taxes_scolaires",
                "taxes_municipales", 
                "electricite",
                "gaz",
                "eau",
                "entretien",
                "reparation",
                "assurance",
                "loyer",
                "autre"
            ],
            "payment_methods": [
                "virement",
                "cheque", 
                "especes",
                "carte",
                "autre"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des constantes: {str(e)}")

@app.get("/api/transactions")
async def get_transactions():
    """Récupérer toutes les transactions"""
    try:
        transactions = db_service_francais.get_transactions()
        return {"data": transactions}
    except Exception as e:
        print(f"Erreur lors du chargement des transactions: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des transactions: {str(e)}")

@app.get("/api/transactions/{transaction_id}")
async def get_transaction(transaction_id: int):
    """Récupérer une transaction par ID"""
    try:
        transaction = db_service_francais.get_transaction(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")
        return {"data": transaction}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors du chargement de la transaction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement de la transaction: {str(e)}")

@app.post("/api/transactions")
async def create_transaction(transaction_data: dict):
    """Créer une nouvelle transaction"""
    try:
        created_transaction = db_service_francais.create_transaction(transaction_data)
        return {"data": created_transaction, "message": "Transaction créée avec succès"}
    except Exception as e:
        print(f"Erreur lors de la création de la transaction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la transaction: {str(e)}")

@app.put("/api/transactions/{transaction_id}")
async def update_transaction(transaction_id: int, transaction_data: dict):
    """Mettre à jour une transaction"""
    try:
        updated_transaction = db_service_francais.update_transaction(transaction_id, transaction_data)
        if not updated_transaction:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")
        return {"data": updated_transaction, "message": "Transaction mise à jour avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la transaction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la transaction: {str(e)}")


@app.get("/api/test-endpoint")
async def test_endpoint():
    """Endpoint de test pour vérifier le déploiement"""
    return {"message": "Test endpoint fonctionne", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 