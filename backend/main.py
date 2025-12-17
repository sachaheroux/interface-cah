from fastapi import FastAPI, HTTPException, UploadFile, File, Query
# Test deploiement backend - ligne propre - API analysis ajoutée
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
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

# Imports pour SQLite
from database import db_manager, init_database
from database_service_francais import db_service_francais
from backup_service import backup_service
from validation_service import data_validator, consistency_checker, ValidationLevel
from monitoring_service import database_monitor

# Import des routes d'authentification
try:
    from auth_routes import router as auth_router
    from auth_database_service import init_auth_database
    AUTH_ENABLED = True
    print("✅ Routes d'authentification chargées")
except ImportError as e:
    AUTH_ENABLED = False
    print(f"⚠️ Routes d'authentification non disponibles: {e}")

# Import des services de construction
try:
    from database_construction import get_construction_db, init_construction_database
    from models_construction import Projet, Fournisseur, MatierePremiere, Commande, LigneCommande, Employe, PunchEmploye, SousTraitant, FactureST
    CONSTRUCTION_ENABLED = True
    print("✅ Services de construction chargés")
except ImportError as e:
    CONSTRUCTION_ENABLED = False
    print(f"⚠️ Services de construction non disponibles: {e}")

app = FastAPI(
    title="Interface CAH API",
    description="API pour la gestion de construction - Interface CAH",
    version="1.0.0"
)

# Inclure les routes d'authentification si disponibles
if AUTH_ENABLED:
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentification"])

# Initialiser la base de données au démarrage
@app.on_event("startup")
async def startup_event():
    """Initialiser la base de données au démarrage de l'application"""
    print("🚀 Démarrage de l'application Interface CAH...")
    print("🗄️ Initialisation de la base de données SQLite...")
    
    if init_database():
        print("✅ Base de données principale initialisée avec succès")
    else:
        print("❌ Erreur lors de l'initialisation de la base de données principale")
        raise Exception("Impossible d'initialiser la base de données")
    
    # Initialiser la base de données d'authentification (si activée)
    if AUTH_ENABLED:
        print("🔐 Initialisation de la base de données d'authentification...")
        if init_auth_database():
            print("✅ Base de données d'authentification initialisée avec succès")
        else:
            print("⚠️ Erreur lors de l'initialisation de la DB auth (non bloquant)")
    
    # Initialiser la base de données de construction (si activée)
    if CONSTRUCTION_ENABLED:
        print("🏗️ Initialisation de la base de données de construction...")
        if init_construction_database():
            print("✅ Base de données de construction initialisée avec succès")
        else:
            print("⚠️ Erreur lors de l'initialisation de la DB construction (non bloquant)")

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
    dette_restante: Optional[float] = None
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
    date_debut: str
    date_fin: str
    prix_loyer: float
    methode_paiement: str = "Virement bancaire"
    pdf_bail: str = ""

class LeaseUpdateFrancais(BaseModel):
    id_locataire: Optional[int] = None
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
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
async def update_lease(lease_id: int, lease_data: LeaseUpdateFrancais):
    """Mettre à jour un bail"""
    try:
        lease_dict = lease_data.dict(exclude_unset=True)
        updated_lease = db_service_francais.update_lease(lease_id, lease_dict)
        if not updated_lease:
            raise HTTPException(status_code=404, detail="Bail non trouvé")
        return {"data": updated_lease, "message": "Bail mis à jour avec succès"}
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
        print("📍 GET /api/buildings - Début")
        buildings = db_service_francais.get_buildings()
        print(f"📍 GET /api/buildings - {len(buildings)} immeubles récupérés")
        return buildings
    except Exception as e:
        print(f"❌ Erreur lors du chargement des immeubles: {e}")
        import traceback
        traceback.print_exc()
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
        print("📍 GET /api/tenants - Début")
        tenants = db_service_francais.get_tenants()
        print(f"📍 GET /api/tenants - {len(tenants)} locataires récupérés")
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
async def upload_document(file: UploadFile = File(...), context: str = "document"):
    """Uploader un document (PDF, image, etc.) vers Backblaze B2"""
    try:
        print(f"📤 Upload PDF reçu: {file.filename} ({file.size} bytes)")
        
        # Vérifier le type de fichier
        if not file.filename.lower().endswith('.pdf'):
            print(f"❌ Type de fichier non supporté: {file.filename}")
            raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
        
        # Lire le contenu du fichier
        file_content = await file.read()
        print(f"📄 Contenu lu: {len(file_content)} bytes")
        
        # Vérifier les variables d'environnement Backblaze B2
        import os
        b2_key_id = os.getenv('B2_APPLICATION_KEY_ID')
        b2_key = os.getenv('B2_APPLICATION_KEY')
        b2_bucket = os.getenv('B2_BUCKET_NAME')
        
        print(f"🔑 B2 Key ID: {b2_key_id[:8] if b2_key_id else 'MANQUANT'}...")
        print(f"🔑 B2 Key: {b2_key[:8] if b2_key else 'MANQUANT'}...")
        print(f"📦 B2 Bucket: {b2_bucket}")
        
        if not b2_key_id or not b2_key:
            print("❌ Variables d'environnement Backblaze B2 manquantes")
            raise HTTPException(status_code=500, detail="Configuration Backblaze B2 manquante")
        
        # Upload vers Backblaze B2
        from storage_service import get_storage_service
        storage_service = get_storage_service()
        
        print("🚀 Tentative d'upload vers Backblaze B2...")
        print(f"📝 Contexte: {context}")
        
        # Déterminer le dossier selon le contexte
        folder_map = {
            "bail": "bails",
            "transaction": "transactions",
            "facture": "factures",
            "commande": "commandes",
            "document": "documents"
        }
        folder = folder_map.get(context, "documents")
        
        result = storage_service.upload_pdf(
            file_content=file_content,
            original_filename=file.filename,
            folder=folder,
            context=context
        )
        
        print(f"📊 Résultat upload: {result}")
        
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
            print(f"❌ Erreur upload Backblaze B2: {result['error']}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload vers Backblaze B2: {result['error']}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur inattendue lors de l'upload: {e}")
        import traceback
        traceback.print_exc()
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
        from storage_service import get_storage_service
        storage_service = get_storage_service()
        
        # Si c'est une clé S3 complète (contient '/'), l'utiliser directement
        if '/' in filename:
            s3_key = filename
            file_content = storage_service.download_pdf(s3_key)
        else:
            # Chercher dans tous les dossiers possibles
            folders = ['documents', 'bails', 'transactions', 'factures', 'commandes']
            file_content = None
            s3_key = None
            
            for folder in folders:
                test_key = f"{folder}/{filename}"
                file_content = storage_service.download_pdf(test_key)
                if file_content is not None:
                    s3_key = test_key
                    print(f"✅ PDF trouvé dans: {s3_key}")
                    break
        
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
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")
        return {"data": transaction}
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
        transaction_dict = transaction_data.dict()
        
        # Créer la transaction via le service SQLite
        new_transaction = db_service_francais.create_transaction(transaction_dict)
        
        return {"data": new_transaction}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la création de la transaction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la transaction: {str(e)}")

@app.put("/api/transactions/{transaction_id}")
async def update_transaction(transaction_id: int, transaction_data: TransactionUpdateFrancais):
    """Mettre à jour une transaction existante avec le format français"""
    try:
        # Convertir en dictionnaire pour le service
        transaction_dict = transaction_data.dict(exclude_unset=True)
        
        # Mettre à jour via le service SQLite
        updated_transaction = db_service_francais.update_transaction(transaction_id, transaction_dict)
        
        if not updated_transaction:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")
        
        print(f"✅ Transaction mise à jour: {transaction_id}")
        return {"data": updated_transaction, "message": "Transaction mise à jour avec succès"}
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

@app.get("/api/analysis/profitability")
async def get_profitability_analysis(
    building_ids: str = Query(..., description="IDs des immeubles séparés par des virgules"),
    start_year: int = Query(..., description="Année de début"),
    start_month: int = Query(..., description="Mois de début (1-12)"),
    end_year: int = Query(..., description="Année de fin"),
    end_month: int = Query(..., description="Mois de fin (1-12)"),
    confirmed_payments_only: bool = Query(True, description="Ne compter que les loyers confirmés payés")
):
    """Récupérer l'analyse de rentabilité avec les vraies données"""
    try:
        print(f"🔍 DEBUG - Début de l'analyse de rentabilité")
        print(f"🔍 DEBUG - Paramètres reçus: building_ids={building_ids}, start_year={start_year}, start_month={start_month}, end_year={end_year}, end_month={end_month}")
        
        # Convertir les IDs des immeubles
        building_id_list = [int(id.strip()) for id in building_ids.split(',') if id.strip()]
        print(f"🔍 DEBUG - IDs des immeubles convertis: {building_id_list}")
        
        # Créer les dates de début et fin
        start_date = datetime(start_year, start_month, 1)
        end_date = datetime(end_year, end_month, 1)
        print(f"🔍 DEBUG - Dates créées: {start_date} à {end_date}")
        
        # Récupérer les données des baux pour les revenus
        print(f"🔍 DEBUG - Récupération des baux...")
        leases = db_service_francais.get_leases_by_buildings_and_period(building_id_list, start_date, end_date)
        print(f"🔍 DEBUG - Baux récupérés: {len(leases)}")
        
        # Récupérer les données des transactions
        print(f"🔍 DEBUG - Récupération des transactions...")
        transactions = db_service_francais.get_transactions_by_buildings_and_period(building_id_list, start_date, end_date)
        print(f"🔍 DEBUG - Transactions récupérées: {len(transactions)}")
        
        # Récupérer les immeubles
        print(f"🔍 DEBUG - Récupération des immeubles...")
        buildings = db_service_francais.get_buildings_by_ids_objects(building_id_list)
        print(f"🔍 DEBUG - Immeubles récupérés: {len(buildings)}")
        
        # Debug: Afficher les données récupérées
        if transactions:
            print(f"🔍 DEBUG - Première transaction: {transactions[0].__dict__ if hasattr(transactions[0], '__dict__') else transactions[0]}")
        if leases:
            print(f"🔍 DEBUG - Premier bail: {leases[0].__dict__ if hasattr(leases[0], '__dict__') else leases[0]}")
        
        # Calculer les données d'analyse
        print(f"🔍 DEBUG - Début du calcul de l'analyse...")
        analysis_data = calculate_profitability_analysis(buildings, leases, transactions, start_date, end_date, confirmed_payments_only)
        print(f"🔍 DEBUG - Analyse calculée avec succès")
        
        return analysis_data
        
    except Exception as e:
        print(f"❌ ERREUR dans l'analyse de rentabilité: {str(e)}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        logger.error(f"Erreur lors de l'analyse de rentabilité: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse de rentabilité: {str(e)}")

def calculate_profitability_analysis(buildings, leases, transactions, start_date, end_date, confirmed_payments_only=False):
    """Calculer l'analyse de rentabilité avec les vraies données"""
    try:
        print(f"🔍 DEBUG - calculate_profitability_analysis: Début")
        print(f"🔍 DEBUG - Paramètres: {len(buildings)} immeubles, {len(leases)} baux, {len(transactions)} transactions")
        
        # Debug: Vérifier le type des objets
        print(f"🔍 DEBUG - Type de buildings: {type(buildings)}")
        if buildings:
            print(f"🔍 DEBUG - Type du premier building: {type(buildings[0])}")
            print(f"🔍 DEBUG - Premier building: {buildings[0]}")
            print(f"🔍 DEBUG - Premier building __dict__: {buildings[0].__dict__ if hasattr(buildings[0], '__dict__') else 'Pas de __dict__'}")
        
        print(f"🔍 DEBUG - Type de leases: {type(leases)}")
        if leases:
            print(f"🔍 DEBUG - Type du premier lease: {type(leases[0])}")
        
        print(f"🔍 DEBUG - Type de transactions: {type(transactions)}")
        if transactions:
            print(f"🔍 DEBUG - Type de la première transaction: {type(transactions[0])}")
        
        from collections import defaultdict
        import calendar
        
        # Initialiser les données
        analysis_data = {
            "buildings": [],
            "monthlyTotals": [],
            "period": {
                "start": start_date.strftime("%Y-%m"),
                "end": end_date.strftime("%Y-%m")
            }
        }
        
        # Créer des dictionnaires pour les données mensuelles et par immeuble
        monthly_data = defaultdict(lambda: {"revenue": 0, "expenses": 0, "netCashflow": 0})
        building_data = defaultdict(lambda: {"revenue": 0, "expenses": 0, "netCashflow": 0})
        
        # Traiter les paiements de loyers comme revenus
        print(f"🔍 Récupération des paiements de loyers...")
        try:
            building_ids_list = [building.id_immeuble for building in buildings]
            
            payments_response = db_service_francais.get_paiements_by_building_and_period(
                building_ids_list, 
                start_date.year, start_date.month, 
                end_date.year, end_date.month
            )
            
            print(f"✅ {len(payments_response)} paiements récupérés")
            
            # Traiter chaque paiement comme un revenu
            for payment_dict in payments_response:
                try:
                    montant = float(payment_dict.get('montant_paye', 0))
                    annee = payment_dict.get('annee')
                    mois = payment_dict.get('mois')
                    id_bail = payment_dict.get('id_bail')
                    
                    # Trouver le bail correspondant pour obtenir l'immeuble
                    lease = next((l for l in leases if l.id_bail == id_bail), None)
                    if lease:
                        # Utiliser l'unité directement depuis le bail (nouvelle structure)
                        building_id = None
                        if hasattr(lease, 'unite') and lease.unite:
                            building_id = lease.unite.id_immeuble
                        elif hasattr(lease, 'id_unite') and lease.id_unite:
                            # Fallback : chercher l'unité si la relation n'est pas chargée
                            # Utiliser la session du service pour chercher l'unité
                            try:
                                from database_service_francais import DatabaseServiceFrancais
                                temp_service = DatabaseServiceFrancais()
                                with temp_service.get_session() as session:
                                    from models_francais import Unite
                                    unite = session.query(Unite).filter(Unite.id_unite == lease.id_unite).first()
                                    if unite:
                                        building_id = unite.id_immeuble
                            except Exception as e:
                                print(f"⚠️ Erreur lors de la récupération de l'unité: {e}")
                                building_id = None
                        
                        if building_id and montant > 0:
                            month_key = f"{annee}-{mois:02d}"
                            
                            # Ajouter le revenu (tous les paiements dans la table sont confirmés)
                            monthly_data[month_key]["revenue"] += montant
                            monthly_data[month_key]["netCashflow"] += montant
                            building_data[building_id]["revenue"] += montant
                            building_data[building_id]["netCashflow"] += montant
                            
                            print(f"✅ Revenu ajouté: {month_key}, Immeuble {building_id}, Montant: {montant}$")
                    else:
                        print(f"⚠️ Paiement ignoré - bail {id_bail} non trouvé")
                        
                except Exception as e:
                    print(f"❌ Erreur traitement paiement: {e}")
                    
        except Exception as e:
            print(f"❌ ERREUR récupération paiements: {e}")
            import traceback
            traceback.print_exc()
        
        # Traiter les transactions
        print(f"🔍 DEBUG - Traitement des transactions...")
        for transaction in transactions:
            building_id = transaction.id_immeuble
            montant = float(transaction.montant or 0)
            type_transaction = transaction.type  # Utiliser le type (revenu/depense) au lieu de la catégorie
            
            print(f"🔍 DEBUG - Transaction: Immeuble {building_id}, Montant: {montant}, Type: {type_transaction}")
            
            # Déterminer le mois de la transaction
            transaction_date = transaction.date_de_transaction
            if transaction_date:
                month_key = transaction_date.strftime("%Y-%m")
                
                # Déterminer si c'est un revenu ou une dépense basé sur le type
                if type_transaction and type_transaction.lower() == "revenu":
                    # Revenu : montant positif
                    monthly_data[month_key]["revenue"] += abs(montant)
                    monthly_data[month_key]["netCashflow"] += abs(montant)
                    building_data[building_id]["revenue"] += abs(montant)
                    building_data[building_id]["netCashflow"] += abs(montant)
                    print(f"✅ Revenu transaction ajouté: {month_key}, Immeuble {building_id}, Montant: {abs(montant)}$")
                else:
                    # Dépense : montant négatif
                    monthly_data[month_key]["expenses"] += abs(montant)
                    monthly_data[month_key]["netCashflow"] -= abs(montant)
                    building_data[building_id]["expenses"] += abs(montant)
                    building_data[building_id]["netCashflow"] -= abs(montant)
                    print(f"✅ Dépense transaction ajoutée: {month_key}, Immeuble {building_id}, Montant: {abs(montant)}$")
        
        # Construire les données des immeubles
        print(f"🔍 DEBUG - Données finales par immeuble:")
        print(f"🔍 DEBUG - Nombre d'immeubles à traiter: {len(buildings)}")
        for i, building in enumerate(buildings):
            print(f"🔍 DEBUG - Traitement immeuble {i}: type={type(building)}")
            print(f"🔍 DEBUG - Building {i}: {building}")
            
            try:
                building_id = building.id_immeuble
                print(f"🔍 DEBUG - building_id récupéré: {building_id}")
            except Exception as e:
                print(f"❌ ERREUR lors de l'accès à building.id_immeuble: {e}")
                print(f"❌ Building type: {type(building)}")
                print(f"❌ Building content: {building}")
                raise e
            
            data = building_data[building_id]
            
            try:
                building_name = building.nom_immeuble
                print(f"🔍 DEBUG - building_name récupéré: {building_name}")
            except Exception as e:
                print(f"❌ ERREUR lors de l'accès à building.nom_immeuble: {e}")
                print(f"❌ Building type: {type(building)}")
                print(f"❌ Building content: {building}")
                raise e
            
            print(f"🔍 DEBUG - Immeuble {building_id} ({building_name}): Revenus: ${data['revenue']}, Dépenses: ${data['expenses']}, Cashflow: ${data['netCashflow']}")
            
            analysis_data["buildings"].append({
                "id": building_id,
                "name": building_name,
                "summary": {
                    "totalRevenue": data["revenue"],
                    "totalExpenses": data["expenses"],
                    "netCashflow": data["netCashflow"]
                }
            })
        
        # Construire les données mensuelles
        current_date = start_date
        while current_date <= end_date:
            month_key = current_date.strftime("%Y-%m")
            month_name = calendar.month_name[current_date.month][:3].lower() + f". {current_date.year}"
            
            data = monthly_data[month_key]
            analysis_data["monthlyTotals"].append({
                "month": month_name,
                "revenue": data["revenue"],
                "expenses": data["expenses"],
                "netCashflow": data["netCashflow"]
            })
            
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Calculer le résumé global
        total_revenue = sum(data["revenue"] for data in monthly_data.values())
        total_expenses = sum(data["expenses"] for data in monthly_data.values())
        total_net_cashflow = sum(data["netCashflow"] for data in monthly_data.values())
        
        # Calculer la valeur totale des immeubles pour le ROI
        print(f"🔍 DEBUG - Calcul de la valeur totale des immeubles...")
        print(f"🔍 DEBUG - Nombre d'immeubles pour le calcul: {len(buildings)}")
        total_property_value = 0
        for i, building in enumerate(buildings):
            print(f"🔍 DEBUG - Calcul valeur immeuble {i}: type={type(building)}")
            try:
                valeur = building.valeur_actuel or 0
                print(f"🔍 DEBUG - Valeur immeuble {i}: {valeur}")
                total_property_value += valeur
            except Exception as e:
                print(f"❌ ERREUR lors de l'accès à building.valeur_actuel: {e}")
                print(f"❌ Building type: {type(building)}")
                print(f"❌ Building content: {building}")
                raise e
        print(f"🔍 DEBUG - Valeur totale calculée: {total_property_value}")
        
        # Calculer le ROI (Return on Investment)
        # ROI = (Cashflow net / Valeur totale des immeubles) * 100
        roi_percentage = (total_net_cashflow / float(total_property_value) * 100) if total_property_value > 0 else 0
        
        analysis_data["summary"] = {
            "totalRevenue": total_revenue,
            "totalExpenses": total_expenses,
            "netCashflow": total_net_cashflow,
            "roi": round(roi_percentage, 2),
            "totalPropertyValue": total_property_value
        }
        
        # Calculer les catégories de dépenses pour le pie chart
        expense_categories = defaultdict(float)
        for transaction in transactions:
            if transaction.categorie and not ("loyer" in transaction.categorie.lower()):
                expense_categories[transaction.categorie] += abs(float(transaction.montant or 0))
        
        analysis_data["categories"] = dict(expense_categories)
        
        print(f"🔍 DEBUG - calculate_profitability_analysis: Succès")
        print(f"🔍 DEBUG - Résumé: Revenus: ${total_revenue}, Dépenses: ${total_expenses}, Cashflow: ${total_net_cashflow}")
        print(f"🔍 DEBUG - Catégories: {analysis_data['categories']}")
        return analysis_data
        
    except Exception as e:
        print(f"❌ ERREUR dans calculate_profitability_analysis: {str(e)}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        raise e

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

@app.get("/api/transactions/check-reference/{reference}")
async def check_transaction_reference(reference: str):
    """Vérifier si une référence de transaction existe déjà"""
    try:
        existing_transaction = db_service_francais.get_transaction_by_reference(reference)
        return {
            "exists": existing_transaction is not None,
            "transaction": existing_transaction
        }
    except Exception as e:
        print(f"Erreur lors de la vérification de la référence: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification de la référence: {str(e)}")

@app.get("/api/analysis/mortgage")
async def get_mortgage_analysis(
    building_ids: str = Query(..., description="IDs des immeubles séparés par des virgules")
):
    """Analyser la dette hypothécaire pour les immeubles sélectionnés"""
    try:
        # Parser les IDs des immeubles
        building_ids_list = [int(id.strip()) for id in building_ids.split(',') if id.strip()]
        
        # Récupérer les immeubles
        buildings = db_service_francais.get_buildings_by_ids(building_ids_list)
        
        # Calculer les données de dette pour chaque immeuble
        mortgage_data = []
        for building in buildings:
            prix_achete = float(building.get('prix_achete', 0) or 0)
            mise_de_fond = float(building.get('mise_de_fond', 0) or 0)
            valeur_actuel = float(building.get('valeur_actuel', 0) or 0)
            dette_restante = float(building.get('dette_restante', 0) or 0)
            
            # Calculer les montants
            dette_initiale = prix_achete - mise_de_fond  # Dette de base (bleu)
            montant_rembourse = dette_initiale - dette_restante  # Montant remboursé (vert)
            gain_valeur = valeur_actuel - prix_achete  # Gain de valeur (bleu)
            
            mortgage_data.append({
                "id_immeuble": building['id_immeuble'],
                "nom_immeuble": building['nom_immeuble'],
                "prix_achete": prix_achete,
                "mise_de_fond": mise_de_fond,
                "valeur_actuel": valeur_actuel,
                "dette_restante": dette_restante,
                "dette_initiale": dette_initiale,
                "montant_rembourse": montant_rembourse,
                "gain_valeur": gain_valeur
            })
        
        return {
            "buildings": mortgage_data,
            "summary": {
                "total_buildings": len(mortgage_data),
                "total_dette_restante": sum(b['dette_restante'] for b in mortgage_data),
                "total_montant_rembourse": sum(b['montant_rembourse'] for b in mortgage_data),
                "total_gain_valeur": sum(b['gain_valeur'] for b in mortgage_data),
                "total_valeur_actuel": sum(b['valeur_actuel'] for b in mortgage_data)
            }
        }
    except Exception as e:
        print(f"Erreur lors de l'analyse de dette hypothécaire: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse de dette hypothécaire: {str(e)}")

@app.post("/api/migrate/dette-restante")
async def migrate_dette_restante():
    """Migration pour ajouter la colonne dette_restante à la table immeubles"""
    try:
        from sqlalchemy import text
        
        with db_service_francais.get_session() as session:
            # Vérifier si la colonne existe déjà
            if os.environ.get("DATABASE_URL"):
                # PostgreSQL sur Render
                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'immeubles' 
                    AND column_name = 'dette_restante'
                """)
            else:
                # SQLite local
                check_query = text("PRAGMA table_info(immeubles)")
            
            result = session.execute(check_query)
            
            if os.environ.get("DATABASE_URL"):
                # PostgreSQL
                column_exists = result.fetchone() is not None
            else:
                # SQLite
                columns = [row[1] for row in result.fetchall()]
                column_exists = 'dette_restante' in columns
            
            if column_exists:
                return {"message": "La colonne 'dette_restante' existe déjà", "success": True}
            
            # Ajouter la colonne
            if os.environ.get("DATABASE_URL"):
                # PostgreSQL
                alter_query = text("""
                    ALTER TABLE immeubles 
                    ADD COLUMN dette_restante DECIMAL(12, 2) DEFAULT 0
                """)
            else:
                # SQLite
                alter_query = text("""
                    ALTER TABLE immeubles 
                    ADD COLUMN dette_restante DECIMAL(12, 2) DEFAULT 0
                """)
            
            session.execute(alter_query)
            session.commit()
            
            return {"message": "Colonne 'dette_restante' ajoutée avec succès", "success": True}
            
    except Exception as e:
        print(f"Erreur lors de la migration: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la migration: {str(e)}")


@app.get("/api/test-endpoint")
async def test_endpoint():
    """Endpoint de test pour vérifier le déploiement"""
    return {"message": "Test endpoint fonctionne", "timestamp": datetime.now().isoformat()}

# ========================================
# ENDPOINTS POUR LES PAIEMENTS DE LOYERS
# ========================================

class PaiementLoyerCreate(BaseModel):
    id_bail: int
    mois: int
    annee: int
    date_paiement_reelle: Optional[str] = None
    montant_paye: Optional[float] = None
    notes: Optional[str] = None

class PaiementLoyerUpdate(BaseModel):
    date_paiement_reelle: Optional[str] = None
    montant_paye: Optional[float] = None
    notes: Optional[str] = None

@app.post("/api/paiements-loyers")
async def create_paiement_loyer(paiement_data: PaiementLoyerCreate):
    """Créer un paiement de loyer"""
    try:
        paiement_dict = paiement_data.dict()
        if paiement_dict.get('date_paiement_reelle'):
            paiement_dict['date_paiement_reelle'] = datetime.fromisoformat(paiement_dict['date_paiement_reelle']).date()
        
        result = db_service_francais.create_paiement_loyer(paiement_dict)
        return result
    except Exception as e:
        print(f"Erreur lors de la création du paiement de loyer: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du paiement de loyer: {str(e)}")

@app.put("/api/paiements-loyers/{paiement_id}")
async def update_paiement_loyer(paiement_id: int, update_data: PaiementLoyerUpdate):
    """Mettre à jour un paiement de loyer"""
    try:
        update_dict = update_data.dict(exclude_unset=True)
        if update_dict.get('date_paiement_reelle'):
            update_dict['date_paiement_reelle'] = datetime.fromisoformat(update_dict['date_paiement_reelle']).date()
        
        result = db_service_francais.update_paiement_loyer(paiement_id, update_dict)
        if not result:
            raise HTTPException(status_code=404, detail="Paiement de loyer non trouvé")
        return result
    except Exception as e:
        print(f"Erreur lors de la mise à jour du paiement de loyer: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du paiement de loyer: {str(e)}")

@app.delete("/api/paiements-loyers/{paiement_id}")
async def delete_paiement_loyer(paiement_id: int):
    """Supprimer un paiement de loyer"""
    try:
        result = db_service_francais.delete_paiement_loyer(paiement_id)
        if not result:
            raise HTTPException(status_code=404, detail="Paiement de loyer non trouvé")
        return {"success": True, "message": "Paiement supprimé avec succès"}
    except Exception as e:
        print(f"Erreur lors de la suppression du paiement de loyer: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression du paiement de loyer: {str(e)}")

@app.get("/api/paiements-loyers")
async def get_all_paiements():
    """Récupérer tous les paiements de loyers (optimisé)"""
    try:
        from models_francais import PaiementLoyer
        from sqlalchemy.orm import Session
        from database import SessionLocal
        
        db = SessionLocal()
        try:
            paiements = db.query(PaiementLoyer).order_by(PaiementLoyer.annee, PaiementLoyer.mois).all()
            return {"data": [p.to_dict() for p in paiements]}
        finally:
            db.close()
    except Exception as e:
        print(f"Erreur lors de la récupération de tous les paiements: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des paiements: {str(e)}")

@app.get("/api/paiements-loyers/bail/{bail_id}")
async def get_paiements_by_bail(bail_id: int):
    """Récupérer tous les paiements pour un bail"""
    try:
        paiements = db_service_francais.get_paiements_by_bail(bail_id)
        return {"data": paiements}
    except Exception as e:
        print(f"Erreur lors de la récupération des paiements pour le bail {bail_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des paiements: {str(e)}")

@app.get("/api/paiements-loyers/building/{building_id}")
async def get_paiements_by_building(
    building_id: int,
    start_year: int = Query(..., description="Année de début"),
    start_month: int = Query(..., description="Mois de début (1-12)"),
    end_year: int = Query(..., description="Année de fin"),
    end_month: int = Query(..., description="Mois de fin (1-12)")
):
    """Récupérer les paiements de loyers pour un immeuble et une période"""
    try:
        paiements = db_service_francais.get_paiements_by_building_and_period(
            [building_id], start_year, start_month, end_year, end_month
        )
        return {"data": paiements}
    except Exception as e:
        print(f"Erreur lors de la récupération des paiements pour l'immeuble {building_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des paiements: {str(e)}")

@app.get("/api/paiements-loyers/get-or-create")
async def get_or_create_paiement(
    bail_id: int = Query(..., description="ID du bail"),
    mois: int = Query(..., description="Mois (1-12)"),
    annee: int = Query(..., description="Année")
):
    """Récupérer ou créer un paiement pour un bail, mois et année donnés"""
    try:
        paiement = db_service_francais.get_or_create_paiement(bail_id, mois, annee)
        return paiement
    except Exception as e:
        print(f"Erreur lors de la récupération/création du paiement: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération/création du paiement: {str(e)}")

@app.delete("/api/paiements-loyers/clear-all")
async def clear_all_paiements_loyers():
    """DANGER: Supprimer TOUTES les données de la table paiements_loyers"""
    try:
        from sqlalchemy import text
        
        with db_service_francais.get_session() as session:
            # Compter avant suppression
            result = session.execute(text("SELECT COUNT(*) FROM paiements_loyers"))
            count_before = result.scalar()
            
            print(f"⚠️  Suppression de {count_before} paiements de loyers...")
            
            # Supprimer toutes les données
            session.execute(text("DELETE FROM paiements_loyers"))
            session.commit()
            
            # Vérifier après suppression
            result = session.execute(text("SELECT COUNT(*) FROM paiements_loyers"))
            count_after = result.scalar()
            
            print(f"✅ Table paiements_loyers vidée. {count_before} enregistrements supprimés, {count_after} restants")
            
            return {
                "message": f"Table paiements_loyers vidée avec succès",
                "deleted_count": count_before,
                "remaining_count": count_after,
                "success": True
            }
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

@app.post("/api/migrate/remove-paye-column")
async def migrate_remove_paye_column():
    """Migration pour supprimer la colonne 'paye' de paiements_loyers"""
    try:
        from sqlalchemy import text
        
        with db_service_francais.get_session() as session:
            # Vérifier si la colonne existe
            if os.environ.get("DATABASE_URL"):
                # PostgreSQL sur Render
                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'paiements_loyers' AND column_name = 'paye'
                """)
                result = session.execute(check_query)
                column_exists = result.fetchone() is not None
                
                if column_exists:
                    # Supprimer la colonne
                    drop_query = text("ALTER TABLE paiements_loyers DROP COLUMN paye")
                    session.execute(drop_query)
                    session.commit()
                    print("✅ Colonne 'paye' supprimée de paiements_loyers sur PostgreSQL")
                    return {"message": "Colonne 'paye' supprimée avec succès", "success": True}
                else:
                    return {"message": "La colonne 'paye' n'existe pas", "success": True}
            else:
                # SQLite local - plus complexe, il faut recréer la table
                check_query = text("PRAGMA table_info(paiements_loyers)")
                result = session.execute(check_query)
                columns = [row[1] for row in result.fetchall()]
                
                if 'paye' in columns:
                    # SQLite ne supporte pas DROP COLUMN facilement, on doit recréer la table
                    print("⚠️  SQLite: Recréation de la table sans la colonne 'paye'")
                    
                    # 1. Créer une nouvelle table temporaire sans 'paye'
                    session.execute(text("""
                        CREATE TABLE paiements_loyers_new (
                            id_paiement INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_bail INTEGER NOT NULL,
                            mois INTEGER NOT NULL,
                            annee INTEGER NOT NULL,
                            date_paiement_reelle DATE NOT NULL,
                            montant_paye DECIMAL(10, 2) NOT NULL,
                            notes TEXT,
                            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (id_bail) REFERENCES baux(id_bail),
                            UNIQUE(id_bail, mois, annee)
                        )
                    """))
                    
                    # 2. Copier les données (sans la colonne 'paye')
                    session.execute(text("""
                        INSERT INTO paiements_loyers_new 
                        (id_paiement, id_bail, mois, annee, date_paiement_reelle, montant_paye, notes, date_creation, date_modification)
                        SELECT id_paiement, id_bail, mois, annee, date_paiement_reelle, montant_paye, notes, date_creation, date_modification
                        FROM paiements_loyers
                    """))
                    
                    # 3. Supprimer l'ancienne table
                    session.execute(text("DROP TABLE paiements_loyers"))
                    
                    # 4. Renommer la nouvelle table
                    session.execute(text("ALTER TABLE paiements_loyers_new RENAME TO paiements_loyers"))
                    
                    session.commit()
                    print("✅ Colonne 'paye' supprimée de paiements_loyers sur SQLite")
                    return {"message": "Colonne 'paye' supprimée avec succès (SQLite)", "success": True}
                else:
                    return {"message": "La colonne 'paye' n'existe pas", "success": True}
                    
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la migration: {str(e)}")

@app.post("/api/migrate/paiements-loyers")
async def migrate_paiements_loyers():
    """Migration pour créer la table paiements_loyers"""
    try:
        from sqlalchemy import text
        
        with db_service_francais.get_session() as session:
            # Vérifier si la table existe déjà
            if os.environ.get("DATABASE_URL"):
                # PostgreSQL sur Render
                check_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'paiements_loyers'
                """)
            else:
                # SQLite local
                check_query = text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='paiements_loyers'
                """)
            
            result = session.execute(check_query)
            
            if os.environ.get("DATABASE_URL"):
                # PostgreSQL
                table_exists = result.fetchone() is not None
            else:
                # SQLite
                table_exists = result.fetchone() is not None
            
            if table_exists:
                return {"message": "La table 'paiements_loyers' existe déjà", "success": True}
            
            # Créer la table
            if os.environ.get("DATABASE_URL"):
                # PostgreSQL
                create_query = text("""
                    CREATE TABLE paiements_loyers (
                        id_paiement SERIAL PRIMARY KEY,
                        id_bail INTEGER NOT NULL,
                        mois INTEGER NOT NULL,
                        annee INTEGER NOT NULL,
                        paye BOOLEAN NOT NULL DEFAULT FALSE,
                        date_paiement_reelle DATE,
                        montant_paye DECIMAL(10, 2),
                        notes TEXT,
                        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT unique_paiement_bail_mois_annee UNIQUE (id_bail, mois, annee),
                        FOREIGN KEY (id_bail) REFERENCES baux(id_bail)
                    )
                """)
            else:
                # SQLite
                create_query = text("""
                    CREATE TABLE paiements_loyers (
                        id_paiement INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_bail INTEGER NOT NULL,
                        mois INTEGER NOT NULL,
                        annee INTEGER NOT NULL,
                        paye BOOLEAN NOT NULL DEFAULT FALSE,
                        date_paiement_reelle DATE,
                        montant_paye DECIMAL(10, 2),
                        notes TEXT,
                        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id_bail) REFERENCES baux(id_bail),
                        UNIQUE (id_bail, mois, annee)
                    )
                """)
            
            session.execute(create_query)
            session.commit()
            
            return {"message": "Table 'paiements_loyers' créée avec succès", "success": True}
            
    except Exception as e:
        print(f"Erreur lors de la migration paiements_loyers: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la migration: {str(e)}")

@app.post("/api/migrate/dette-restante")
async def migrate_dette_restante():
    """Migration pour ajouter la colonne dette_restante à la table immeubles"""
    try:
        from sqlalchemy import text
        
        with db_service_francais.get_session() as session:
            # Vérifier si la colonne existe déjà
            if os.environ.get("DATABASE_URL"):
                # PostgreSQL sur Render
                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'immeubles' AND column_name = 'dette_restante'
                """)
                result = session.execute(check_query)
                column_exists = result.fetchone() is not None
                
                if not column_exists:
                    print("📝 Ajout de la colonne dette_restante à la table immeubles (PostgreSQL)...")
                    alter_query = text("""
                        ALTER TABLE immeubles 
                        ADD COLUMN dette_restante DECIMAL(12, 2) DEFAULT 0
                    """)
                    session.execute(alter_query)
                    session.commit()
                    print("✅ Colonne dette_restante ajoutée avec succès!")
                    return {"message": "Colonne 'dette_restante' ajoutée avec succès", "success": True}
                else:
                    print("ℹ️ La colonne dette_restante existe déjà")
                    return {"message": "La colonne 'dette_restante' existe déjà", "success": True}
            else:
                # SQLite local
                check_query = text("PRAGMA table_info(immeubles)")
                result = session.execute(check_query)
                columns = [row[1] for row in result]
                
                if 'dette_restante' not in columns:
                    print("📝 Ajout de la colonne dette_restante à la table immeubles (SQLite)...")
                    alter_query = text("""
                        ALTER TABLE immeubles 
                        ADD COLUMN dette_restante DECIMAL(12, 2) DEFAULT 0
                    """)
                    session.execute(alter_query)
                    session.commit()
                    print("✅ Colonne dette_restante ajoutée avec succès!")
                    return {"message": "Colonne 'dette_restante' ajoutée avec succès", "success": True}
                else:
                    print("ℹ️ La colonne dette_restante existe déjà")
                    return {"message": "La colonne 'dette_restante' existe déjà", "success": True}
            
    except Exception as e:
        print(f"Erreur lors de la migration dette_restante: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la migration: {str(e)}")

# ==========================================
# ENDPOINT MIGRATION BAIL ID_UNITE
# ==========================================

@app.post("/api/migrate/remove-locataire-id-unite")
async def migrate_remove_locataire_id_unite_endpoint():
    """
    Endpoint pour exécuter la migration : supprimer id_unite de la table locataires
    Après la migration bail-add-id-unite, les baux ont maintenant id_unite directement.
    Les locataires n'ont plus besoin de id_unite car on peut trouver leur unité via leur bail actif.
    """
    try:
        from migrate_remove_locataire_id_unite import migrate_remove_locataire_id_unite
        
        print("\n" + "="*70)
        print("🚀 DÉMARRAGE DE LA MIGRATION : Supprimer id_unite de locataires")
        print("="*70)
        
        success = migrate_remove_locataire_id_unite()
        
        if success:
            return {
                "success": True,
                "message": "Migration réussie ! La colonne id_unite a été supprimée de locataires.",
                "details": "Les locataires sont maintenant liés aux unités uniquement via leurs baux actifs."
            }
        else:
            return {
                "success": False,
                "message": "Migration échouée. Vérifiez les logs pour plus de détails.",
                "details": "Une sauvegarde a été créée dans le répertoire de migrations."
            }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Erreur lors de la migration: {e}")
        print(error_details)
        return {
            "success": False,
            "message": f"Erreur lors de la migration: {str(e)}",
            "error": error_details
        }

@app.post("/api/migrate/bail-add-id-unite")
async def migrate_bail_add_id_unite_endpoint():
    """
    Endpoint pour exécuter la migration : ajouter id_unite à la table baux
    Cette migration migre les données depuis locataires.id_unite vers baux.id_unite
    Exécute directement sur la base de données Render (disque persistant)
    
    IMPORTANT : Cette migration doit être exécutée manuellement une seule fois.
    Elle est disponible dans Paramètres > Sauvegarde > Migration Base de Données
    """
    try:
        from migrate_bail_add_id_unite import migrate_bail_add_id_unite
        
        print("\n" + "="*70)
        print("🚀 DÉMARRAGE DE LA MIGRATION BAIL ID_UNITE VIA API")
        print("="*70)
        
        success = migrate_bail_add_id_unite()
        
        if success:
            return {
                "success": True,
                "message": "Migration réussie ! La colonne id_unite a été ajoutée à baux et les données ont été migrées.",
                "details": "Tous les baux ont maintenant un id_unite lié directement à l'unité."
            }
        else:
            return {
                "success": False,
                "message": "Migration échouée. Vérifiez les logs pour plus de détails.",
                "details": "Une sauvegarde a été créée dans le répertoire de migrations."
            }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Erreur lors de la migration: {e}")
        print(error_details)
        return {
            "success": False,
            "message": f"Erreur lors de la migration: {str(e)}",
            "error": error_details
        }

# ============================================================================
# ENDPOINT TEMPORAIRE POUR SETUP AUTHENTIFICATION (À SUPPRIMER APRÈS USAGE)
# ============================================================================

@app.post("/api/setup-authentication")
async def setup_authentication():
    """
    Endpoint temporaire pour initialiser le système d'authentification
    Crée les tables, la compagnie de Sacha, son compte admin, et migre les données
    ⚠️ À SUPPRIMER APRÈS LA PREMIÈRE EXÉCUTION RÉUSSIE
    """
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        import bcrypt
        from datetime import datetime
        
        print("\n" + "="*70)
        print("🚀 DÉBUT DU SETUP D'AUTHENTIFICATION SUR RENDER")
        print("="*70)
        
        # Récupérer l'URL de la base de données
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise Exception("DATABASE_URL non configurée")
        
        print(f"📊 Connexion à la base de données...")
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # ÉTAPE 1: Créer les tables d'authentification dans le schéma public
            print("\n1️⃣ Création des tables d'authentification (schéma public)...")
            
            # Table compagnies
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS public.compagnies (
                    id_compagnie SERIAL PRIMARY KEY,
                    nom_compagnie VARCHAR(255) NOT NULL UNIQUE,
                    email_compagnie VARCHAR(255),
                    telephone_compagnie VARCHAR(50),
                    adresse_compagnie VARCHAR(255),
                    site_web VARCHAR(255),
                    numero_entreprise VARCHAR(50),
                    schema_name VARCHAR(255) NOT NULL UNIQUE,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Table utilisateurs
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS public.utilisateurs (
                    id_utilisateur SERIAL PRIMARY KEY,
                    id_compagnie INTEGER REFERENCES public.compagnies(id_compagnie) ON DELETE CASCADE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    mot_de_passe_hash VARCHAR(255) NOT NULL,
                    nom VARCHAR(255) NOT NULL,
                    prenom VARCHAR(255) NOT NULL,
                    age INTEGER,
                    sexe VARCHAR(50),
                    date_de_naissance DATE,
                    telephone VARCHAR(50),
                    poste VARCHAR(255),
                    role VARCHAR(50) DEFAULT 'employe',
                    statut VARCHAR(50) DEFAULT 'en_attente',
                    est_admin_principal BOOLEAN DEFAULT FALSE,
                    code_verification_email VARCHAR(6),
                    code_verification_email_expiration TIMESTAMP,
                    code_reset_mdp VARCHAR(6),
                    code_reset_mdp_expiration TIMESTAMP,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Table demandes_acces
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS public.demandes_acces (
                    id_demande SERIAL PRIMARY KEY,
                    id_compagnie INTEGER NOT NULL REFERENCES public.compagnies(id_compagnie) ON DELETE CASCADE,
                    id_utilisateur INTEGER NOT NULL REFERENCES public.utilisateurs(id_utilisateur) ON DELETE CASCADE,
                    statut VARCHAR(50) DEFAULT 'en_attente',
                    traite_par INTEGER REFERENCES public.utilisateurs(id_utilisateur),
                    date_traitement TIMESTAMP,
                    commentaire_refus TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            session.commit()
            print("✅ Tables d'authentification créées")
            
            # ÉTAPE 2: Créer la compagnie de Sacha
            print("\n2️⃣ Création de la compagnie 'CAH Immobilier'...")
            
            # Vérifier si la compagnie existe déjà
            check_company = session.execute(text("""
                SELECT id_compagnie FROM public.compagnies WHERE nom_compagnie = 'CAH Immobilier'
            """)).fetchone()
            
            if check_company:
                company_id = check_company[0]
                print(f"ℹ️ Compagnie existe déjà (ID: {company_id})")
            else:
                session.execute(text("""
                    INSERT INTO public.compagnies 
                    (nom_compagnie, email_compagnie, schema_name, date_creation)
                    VALUES ('CAH Immobilier', 'sacha.heroux87@gmail.com', 'cah_immobilier', CURRENT_TIMESTAMP)
                """))
                session.commit()
                
                company_id = session.execute(text("""
                    SELECT id_compagnie FROM public.compagnies WHERE nom_compagnie = 'CAH Immobilier'
                """)).fetchone()[0]
                
                print(f"✅ Compagnie 'CAH Immobilier' créée (ID: {company_id})")
            
            # ÉTAPE 3: Créer le compte admin de Sacha
            print("\n3️⃣ Création du compte admin pour Sacha...")
            
            # Vérifier si l'utilisateur existe déjà
            check_user = session.execute(text("""
                SELECT id_utilisateur FROM public.utilisateurs WHERE email = 'sacha.heroux87@gmail.com'
            """)).fetchone()
            
            if check_user:
                print(f"ℹ️ Utilisateur existe déjà (ID: {check_user[0]})")
            else:
                # Hasher le mot de passe
                password = "Champion2024!"
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                session.execute(text("""
                    INSERT INTO public.utilisateurs 
                    (id_compagnie, email, mot_de_passe_hash, nom, prenom, role, statut, est_admin_principal, date_creation)
                    VALUES (:company_id, 'sacha.heroux87@gmail.com', :password_hash, 'Heroux', 'Sacha', 'admin', 'actif', TRUE, CURRENT_TIMESTAMP)
                """), {"company_id": company_id, "password_hash": password_hash})
                session.commit()
                
                print("✅ Compte admin créé pour sacha.heroux87@gmail.com")
            
            # ÉTAPE 4: Créer le schéma dédié pour CAH Immobilier
            print("\n4️⃣ Création du schéma 'cah_immobilier'...")
            
            session.execute(text("CREATE SCHEMA IF NOT EXISTS cah_immobilier"))
            session.commit()
            print("✅ Schéma 'cah_immobilier' créé")
            
            # ÉTAPE 5: Créer les tables dans le nouveau schéma
            print("\n5️⃣ Création des tables de données dans 'cah_immobilier'...")
            
            session.execute(text("SET search_path TO cah_immobilier, public"))
            
            # Créer toutes les tables (immeubles, unites, locataires, baux, transactions, paiements_loyers)
            # (Je vais copier le schéma actuel du public vers le nouveau schéma)
            
            # Table immeubles
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS cah_immobilier.immeubles (
                    id_immeuble SERIAL PRIMARY KEY,
                    adresse TEXT NOT NULL,
                    ville TEXT,
                    code_postal TEXT,
                    nombre_unites INTEGER,
                    annee_construction INTEGER,
                    type_batiment TEXT,
                    superficie_terrain DECIMAL(10, 2),
                    prix_achete DECIMAL(12, 2),
                    valeur_actuel DECIMAL(12, 2),
                    dette_restante DECIMAL(12, 2) DEFAULT 0,
                    mise_de_fond DECIMAL(12, 2),
                    taux_interet DECIMAL(5, 2),
                    duree_hypotheque INTEGER,
                    banque TEXT,
                    proprietaire TEXT,
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Table unites
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS cah_immobilier.unites (
                    id_unite SERIAL PRIMARY KEY,
                    id_immeuble INTEGER REFERENCES cah_immobilier.immeubles(id_immeuble) ON DELETE CASCADE,
                    numero_unite TEXT NOT NULL,
                    nombre_chambres INTEGER,
                    nombre_salles_bain DECIMAL(3, 1),
                    superficie DECIMAL(10, 2),
                    loyer_mensuel DECIMAL(10, 2),
                    statut TEXT,
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Table locataires
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS cah_immobilier.locataires (
                    id_locataire SERIAL PRIMARY KEY,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    email TEXT,
                    telephone TEXT,
                    date_naissance DATE,
                    profession TEXT,
                    employeur TEXT,
                    revenu_annuel DECIMAL(12, 2),
                    statut TEXT DEFAULT 'actif',
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Table baux
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS cah_immobilier.baux (
                    id_bail SERIAL PRIMARY KEY,
                    id_locataire INTEGER REFERENCES cah_immobilier.locataires(id_locataire) ON DELETE CASCADE,
                    id_unite INTEGER REFERENCES cah_immobilier.unites(id_unite) ON DELETE CASCADE,
                    date_debut DATE NOT NULL,
                    date_fin DATE NOT NULL,
                    prix_loyer DECIMAL(10, 2) NOT NULL,
                    depot_garantie DECIMAL(10, 2),
                    conditions_speciales TEXT,
                    pdf_bail TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Table transactions
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS cah_immobilier.transactions (
                    id_transaction SERIAL PRIMARY KEY,
                    id_immeuble INTEGER REFERENCES cah_immobilier.immeubles(id_immeuble) ON DELETE CASCADE,
                    type TEXT NOT NULL,
                    categorie TEXT,
                    montant DECIMAL(12, 2) NOT NULL,
                    date_de_transaction DATE NOT NULL,
                    methode_de_paiement TEXT,
                    reference TEXT,
                    source TEXT,
                    pdf_transaction TEXT,
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Table paiements_loyers
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS cah_immobilier.paiements_loyers (
                    id_paiement SERIAL PRIMARY KEY,
                    id_bail INTEGER REFERENCES cah_immobilier.baux(id_bail) ON DELETE CASCADE,
                    mois INTEGER NOT NULL,
                    annee INTEGER NOT NULL,
                    date_paiement_reelle DATE NOT NULL,
                    montant_paye DECIMAL(10, 2) NOT NULL,
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(id_bail, mois, annee)
                )
            """))
            
            session.commit()
            print("✅ Tables de données créées dans 'cah_immobilier'")
            
            # ÉTAPE 6: Migrer les données existantes depuis public vers cah_immobilier
            print("\n6️⃣ Migration des données existantes...")
            
            # Compter les données à migrer
            counts = {}
            for table in ['immeubles', 'unites', 'locataires', 'baux', 'transactions', 'paiements_loyers']:
                count = session.execute(text(f"SELECT COUNT(*) FROM public.{table}")).scalar()
                counts[table] = count
                print(f"   📊 {table}: {count} entrées")
            
            # Migrer les données
            if counts['immeubles'] > 0:
                session.execute(text("""
                    INSERT INTO cah_immobilier.immeubles 
                    SELECT * FROM public.immeubles
                    ON CONFLICT DO NOTHING
                """))
            
            if counts['unites'] > 0:
                session.execute(text("""
                    INSERT INTO cah_immobilier.unites 
                    SELECT * FROM public.unites
                    ON CONFLICT DO NOTHING
                """))
            
            if counts['locataires'] > 0:
                session.execute(text("""
                    INSERT INTO cah_immobilier.locataires 
                    SELECT * FROM public.locataires
                    ON CONFLICT DO NOTHING
                """))
            
            if counts['baux'] > 0:
                session.execute(text("""
                    INSERT INTO cah_immobilier.baux 
                    SELECT * FROM public.baux
                    ON CONFLICT DO NOTHING
                """))
            
            if counts['transactions'] > 0:
                session.execute(text("""
                    INSERT INTO cah_immobilier.transactions 
                    SELECT * FROM public.transactions
                    ON CONFLICT DO NOTHING
                """))
            
            if counts['paiements_loyers'] > 0:
                session.execute(text("""
                    INSERT INTO cah_immobilier.paiements_loyers 
                    SELECT * FROM public.paiements_loyers
                    ON CONFLICT DO NOTHING
                """))
            
            session.commit()
            print("✅ Données migrées avec succès")
            
            # Réinitialiser le search_path
            session.execute(text("SET search_path TO public"))
            session.commit()
        
        print("\n" + "="*70)
        print("✅ SETUP D'AUTHENTIFICATION TERMINÉ AVEC SUCCÈS !")
        print("="*70)
        
        return {
            "success": True,
            "message": "Setup d'authentification terminé avec succès",
            "details": {
                "compagnie_creee": "CAH Immobilier",
                "schema": "cah_immobilier",
                "admin_email": "sacha.heroux87@gmail.com",
                "donnees_migrees": counts
            }
        }
        
    except Exception as e:
        print(f"\n❌ ERREUR DURANT LE SETUP: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur durant le setup: {str(e)}")

# ==========================================
# ROUTES API CONSTRUCTION
# ==========================================

if CONSTRUCTION_ENABLED:
    from sqlalchemy.orm import Session
    from sqlalchemy import desc
    from fastapi import Depends
    
    # ==========================================
    # MODÈLES PYDANTIC POUR CONSTRUCTION
    # ==========================================
    
    class ProjetCreate(BaseModel):
        nom: str
        date_debut: Optional[str] = None  # Format YYYY-MM-DD
        date_fin_prevue: Optional[str] = None  # Format YYYY-MM-DD
        date_fin_reelle: Optional[str] = None  # Format YYYY-MM-DD
        notes: Optional[str] = None
        adresse: Optional[str] = None
        ville: Optional[str] = None
        province: Optional[str] = None
        code_postal: Optional[str] = None
        budget_total: Optional[float] = 0
    
    class ProjetUpdate(BaseModel):
        nom: Optional[str] = None
        description: Optional[str] = None
        adresse: Optional[str] = None
        ville: Optional[str] = None
        province: Optional[str] = None
        code_postal: Optional[str] = None
        date_debut: Optional[str] = None
        date_fin_prevue: Optional[str] = None
        date_fin_reelle: Optional[str] = None
        budget_total: Optional[float] = None
        cout_actuel: Optional[float] = None
        marge_beneficiaire: Optional[float] = None
        statut: Optional[str] = None
        progression_pourcentage: Optional[float] = None
        client_nom: Optional[str] = None
        client_telephone: Optional[str] = None
        client_email: Optional[str] = None
        chef_projet: Optional[str] = None
        architecte: Optional[str] = None
        entrepreneur_principal: Optional[str] = None
        plans_pdf: Optional[str] = None
        permis_construction: Optional[str] = None
        numero_permis: Optional[str] = None
        notes: Optional[str] = None
        risques_identifies: Optional[str] = None
        ameliorations_futures: Optional[str] = None
        modifie_par: Optional[str] = None
    
    class FournisseurCreate(BaseModel):
        nom: str
        rue: Optional[str] = None
        ville: Optional[str] = None
        province: Optional[str] = None
        code_postal: Optional[str] = None
        numero: Optional[str] = None
        adresse_courriel: Optional[str] = None
    
    class FournisseurUpdate(BaseModel):
        nom: Optional[str] = None
        rue: Optional[str] = None
        ville: Optional[str] = None
        province: Optional[str] = None
        code_postal: Optional[str] = None
        numero: Optional[str] = None
        adresse_courriel: Optional[str] = None
    
    class MatierePremiereCreate(BaseModel):
        nom: str
        notes: Optional[str] = None
    
    class MatierePremiereUpdate(BaseModel):
        nom: Optional[str] = None
        notes: Optional[str] = None
    
    class EmployeCreate(BaseModel):
        prenom: str
        nom: str
        poste: Optional[str] = None
        numero: Optional[str] = None
        adresse_courriel: Optional[str] = None
        taux_horaire: Optional[float] = None
    
    class EmployeUpdate(BaseModel):
        prenom: Optional[str] = None
        nom: Optional[str] = None
        poste: Optional[str] = None
        numero: Optional[str] = None
        adresse_courriel: Optional[str] = None
        taux_horaire: Optional[float] = None
    
    class SousTraitantCreate(BaseModel):
        nom: str
        rue: Optional[str] = None
        ville: Optional[str] = None
        province: Optional[str] = None
        code_postal: Optional[str] = None
        numero: Optional[str] = None
        adresse_courriel: Optional[str] = None
    
    class SousTraitantUpdate(BaseModel):
        nom: Optional[str] = None
        rue: Optional[str] = None
        ville: Optional[str] = None
        province: Optional[str] = None
        code_postal: Optional[str] = None
        numero: Optional[str] = None
        adresse_courriel: Optional[str] = None
    
    class FactureSTCreate(BaseModel):
        id_projet: int
        id_st: int
        montant: float
        section: Optional[str] = None
        notes: Optional[str] = None
        reference: Optional[str] = None
        date_de_paiement: Optional[str] = None  # Format YYYY-MM-DD
        pdf_facture: Optional[str] = None
    
    class FactureSTUpdate(BaseModel):
        id_projet: Optional[int] = None
        id_st: Optional[int] = None
        montant: Optional[float] = None
        section: Optional[str] = None
        notes: Optional[str] = None
        reference: Optional[str] = None
        date_de_paiement: Optional[str] = None  # Format YYYY-MM-DD
        pdf_facture: Optional[str] = None
    
    class CommandeCreate(BaseModel):
        id_projet: int
        id_fournisseur: int
        statut: Optional[str] = "en_attente"
        type_de_paiement: Optional[str] = None
        notes: Optional[str] = None
        pdf_commande: Optional[str] = None
        lignes_commande: List[Dict[str, Any]]  # Liste des lignes de commande
    
    class CommandeUpdate(BaseModel):
        id_projet: Optional[int] = None
        id_fournisseur: Optional[int] = None
        montant: Optional[float] = None
        statut: Optional[str] = None
        type_de_paiement: Optional[str] = None
        notes: Optional[str] = None
        pdf_commande: Optional[str] = None
    
    class LigneCommandeCreate(BaseModel):
        id_commande: int
        id_matiere_premiere: int
        quantite: float
        unite: str
        montant: float
        section: Optional[str] = None
    
    class LigneCommandeUpdate(BaseModel):
        id_matiere_premiere: Optional[int] = None
        quantite: Optional[float] = None
        unite: Optional[str] = None
        montant: Optional[float] = None
        section: Optional[str] = None
    
    class PunchEmployeCreate(BaseModel):
        id_employe: int
        id_projet: int
        date: str  # Format YYYY-MM-DD
        heure_travaillee: float
        section: Optional[str] = None
    
    class PunchEmployeUpdate(BaseModel):
        id_employe: Optional[int] = None
        id_projet: Optional[int] = None
        date: Optional[str] = None
        heure_travaillee: Optional[float] = None
        section: Optional[str] = None
    
    # ==========================================
    # ENDPOINTS DE MIGRATION CONSTRUCTION
    # ==========================================
    
    @app.post("/api/construction/migrate/add-projet-columns")
    async def migrate_add_projet_columns(db: Session = Depends(get_construction_db)):
        """Ajouter les colonnes manquantes à la table projets"""
        try:
            from sqlalchemy import text
            
            # Colonnes à ajouter
            columns_to_add = [
                ("adresse", "VARCHAR(255)"),
                ("ville", "VARCHAR(100)"),
                ("province", "VARCHAR(50)"),
                ("code_postal", "VARCHAR(10)"),
                ("budget_total", "FLOAT DEFAULT 0")
            ]
            
            # Vérifier quelles colonnes existent déjà
            result = db.execute(text("PRAGMA table_info(projets)"))
            existing_columns = [col[1] for col in result.fetchall()]
            
            added_columns = []
            skipped_columns = []
            
            for col_name, col_type in columns_to_add:
                if col_name not in existing_columns:
                    try:
                        db.execute(text(f"ALTER TABLE projets ADD COLUMN {col_name} {col_type}"))
                        added_columns.append(col_name)
                        print(f"✅ Colonne '{col_name}' ajoutée")
                    except Exception as e:
                        print(f"❌ Erreur lors de l'ajout de '{col_name}': {e}")
                else:
                    skipped_columns.append(col_name)
                    print(f"ℹ️ Colonne '{col_name}' existe déjà")
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Migration terminée: {len(added_columns)} colonne(s) ajoutée(s)",
                "added_columns": added_columns,
                "skipped_columns": skipped_columns
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur migration: {e}")
    
    @app.post("/api/construction/migrate/add-taux-horaire")
    async def migrate_add_taux_horaire(db: Session = Depends(get_construction_db)):
        """Migration : Ajouter la colonne taux_horaire à la table employes"""
        try:
            from sqlalchemy import text
            
            # Vérifier si la colonne existe déjà
            result = db.execute(text("PRAGMA table_info(employes)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'taux_horaire' in columns:
                return {"success": True, "message": "Colonne taux_horaire existe déjà"}
            
            # Ajouter la colonne
            db.execute(text("ALTER TABLE employes ADD COLUMN taux_horaire FLOAT"))
            db.commit()
            
            return {"success": True, "message": "Colonne taux_horaire ajoutée avec succès"}
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur migration: {e}")
    
    @app.get("/api/construction/debug/employes-structure")
    async def debug_employes_structure(db: Session = Depends(get_construction_db)):
        """Debug : Vérifier la structure de la table employes"""
        try:
            from sqlalchemy import text
            
            # Vérifier la structure de la table
            result = db.execute(text("PRAGMA table_info(employes)"))
            columns = result.fetchall()
            
            # Compter les employés
            count_result = db.execute(text("SELECT COUNT(*) FROM employes"))
            count = count_result.fetchone()[0]
            
            # Récupérer quelques employés
            employees_result = db.execute(text("SELECT * FROM employes LIMIT 5"))
            employees = employees_result.fetchall()
            
            return {
                "success": True,
                "structure": [{"name": col[1], "type": col[2], "not_null": col[3]} for col in columns],
                "count": count,
                "sample_data": [dict(zip([col[1] for col in columns], emp)) for emp in employees]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==========================================
    # ENDPOINTS PROJETS
    # ==========================================
    
    @app.get("/api/construction/projets")
    async def get_projets(db: Session = Depends(get_construction_db)):
        """Récupérer tous les projets"""
        try:
            from sqlalchemy import text
            
            # Vérifier quelles colonnes existent dans la table
            result = db.execute(text("PRAGMA table_info(projets)"))
            existing_columns = [col[1] for col in result.fetchall()]
            
            # Colonnes de base qui doivent exister
            base_columns = ['id_projet', 'nom', 'date_debut', 'date_fin_prevue', 'date_fin_reelle', 'notes', 'date_creation', 'date_modification']
            # Colonnes optionnelles à ajouter
            optional_columns = ['adresse', 'ville', 'province', 'code_postal', 'budget_total']
            
            # Construire la liste des colonnes à sélectionner
            columns_to_select = [col for col in base_columns if col in existing_columns]
            columns_to_select.extend([col for col in optional_columns if col in existing_columns])
            
            # Construire la requête SQL
            columns_str = ', '.join(columns_to_select)
            query = f"SELECT {columns_str} FROM projets ORDER BY date_creation DESC"
            
            result = db.execute(text(query))
            rows = result.fetchall()
            
            # Convertir les résultats en dictionnaires
            projets_data = []
            for row in rows:
                projet_dict = {}
                for idx, col_name in enumerate(columns_to_select):
                    value = row[idx]
                    # Formater les dates
                    if 'date' in col_name.lower() and value:
                        if isinstance(value, str):
                            projet_dict[col_name] = value
                        else:
                            projet_dict[col_name] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
                    else:
                        projet_dict[col_name] = value
                projets_data.append(projet_dict)
            
            return {"success": True, "data": projets_data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des projets: {e}")
    
    @app.post("/api/construction/projets")
    async def create_projet(projet_data: ProjetCreate, db: Session = Depends(get_construction_db)):
        """Créer un nouveau projet"""
        try:
            # Convertir les dates string en objets datetime
            date_debut = None
            date_fin_prevue = None
            date_fin_reelle = None
            
            if projet_data.date_debut:
                date_str = projet_data.date_debut.strip()
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                elif 'T' in date_str:
                    date_str = date_str.split('T')[0]
                date_debut = datetime.strptime(date_str, '%Y-%m-%d')
            if projet_data.date_fin_prevue:
                date_str = projet_data.date_fin_prevue.strip()
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                elif 'T' in date_str:
                    date_str = date_str.split('T')[0]
                date_fin_prevue = datetime.strptime(date_str, '%Y-%m-%d')
            if projet_data.date_fin_reelle:
                date_str = projet_data.date_fin_reelle.strip()
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                elif 'T' in date_str:
                    date_str = date_str.split('T')[0]
                date_fin_reelle = datetime.strptime(date_str, '%Y-%m-%d')
            
            nouveau_projet = Projet(
                nom=projet_data.nom,
                date_debut=date_debut,
                date_fin_prevue=date_fin_prevue,
                date_fin_reelle=date_fin_reelle,
                notes=projet_data.notes,
                adresse=projet_data.adresse,
                ville=projet_data.ville,
                province=projet_data.province,
                code_postal=projet_data.code_postal,
                budget_total=projet_data.budget_total or 0
            )
            
            db.add(nouveau_projet)
            db.commit()
            db.refresh(nouveau_projet)
            
            return {"success": True, "data": nouveau_projet.to_dict()}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la création du projet: {e}")
    
    @app.get("/api/construction/projets/{projet_id}")
    async def get_projet(projet_id: int, db: Session = Depends(get_construction_db)):
        """Récupérer un projet par ID"""
        try:
            projet = db.query(Projet).filter(Projet.id_projet == projet_id).first()
            if not projet:
                raise HTTPException(status_code=404, detail="Projet non trouvé")
            return {"success": True, "data": projet.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du projet: {e}")
    
    @app.get("/api/construction/projets/{projet_id}/analyse-depenses")
    async def get_analyse_depenses(projet_id: int, db: Session = Depends(get_construction_db)):
        """Analyser les dépenses d'un projet par section/catégorie"""
        try:
            # Vérifier que le projet existe
            projet = db.query(Projet).filter(Projet.id_projet == projet_id).first()
            if not projet:
                raise HTTPException(status_code=404, detail="Projet non trouvé")
            
            from collections import defaultdict
            from sqlalchemy import func
            
            # Dictionnaire pour regrouper les dépenses par section
            depenses_par_section = defaultdict(lambda: {
                "sous_traitants": 0.0,
                "commandes": 0.0,
                "employes": 0.0,
                "heures_travaillees": 0.0,  # Nombre d'heures travaillées
                "total": 0.0
            })
            
            # 1. Dépenses des factures ST (sous-traitants) par section
            factures_st = db.query(FactureST).filter(FactureST.id_projet == projet_id).all()
            for facture in factures_st:
                section = facture.section or "Non spécifié"
                depenses_par_section[section]["sous_traitants"] += facture.montant or 0.0
                depenses_par_section[section]["total"] += facture.montant or 0.0
            
            # 2. Dépenses des lignes de commande par section
            commandes = db.query(Commande).filter(Commande.id_projet == projet_id).all()
            for commande in commandes:
                for ligne in commande.lignes_commande:
                    section = ligne.section or "Non spécifié"
                    depenses_par_section[section]["commandes"] += ligne.montant or 0.0
                    depenses_par_section[section]["total"] += ligne.montant or 0.0
            
            # 3. Dépenses des punchs employés (heures * taux horaire) par section
            punchs = db.query(PunchEmploye).filter(PunchEmploye.id_projet == projet_id).all()
            for punch in punchs:
                section = punch.section or "Non spécifié"
                heures = punch.heure_travaillee or 0.0
                depenses_par_section[section]["heures_travaillees"] += heures
                # Calculer le coût : heures travaillées * taux horaire de l'employé
                if punch.employe and punch.employe.taux_horaire:
                    cout = heures * (punch.employe.taux_horaire or 0.0)
                    depenses_par_section[section]["employes"] += cout
                    depenses_par_section[section]["total"] += cout
            
            # Convertir en liste triée par total décroissant
            analyse = []
            for section, depenses in sorted(depenses_par_section.items(), key=lambda x: x[1]["total"], reverse=True):
                analyse.append({
                    "section": section,
                    "sous_traitants": round(depenses["sous_traitants"], 2),
                    "commandes": round(depenses["commandes"], 2),
                    "employes": round(depenses["employes"], 2),
                    "heures_travaillees": round(depenses["heures_travaillees"], 2),
                    "total": round(depenses["total"], 2)
                })
            
            # Calculer les totaux généraux
            total_sous_traitants = sum(d["sous_traitants"] for d in depenses_par_section.values())
            total_commandes = sum(d["commandes"] for d in depenses_par_section.values())
            total_employes = sum(d["employes"] for d in depenses_par_section.values())
            total_general = sum(d["total"] for d in depenses_par_section.values())
            
            return {
                "success": True,
                "data": {
                    "projet": projet.to_dict(),
                    "depenses_par_section": analyse,
                    "totaux": {
                        "sous_traitants": round(total_sous_traitants, 2),
                        "commandes": round(total_commandes, 2),
                        "employes": round(total_employes, 2),
                        "total": round(total_general, 2)
                    }
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse des dépenses: {e}")
    
    @app.put("/api/construction/projets/{projet_id}")
    async def update_projet(projet_id: int, projet_data: ProjetUpdate, db: Session = Depends(get_construction_db)):
        """Mettre à jour un projet"""
        try:
            projet = db.query(Projet).filter(Projet.id_projet == projet_id).first()
            if not projet:
                raise HTTPException(status_code=404, detail="Projet non trouvé")
            
            # Mettre à jour les champs fournis
            if projet_data.nom is not None:
                projet.nom = projet_data.nom
            
            # Gérer les champs optionnels (peuvent être None ou chaîne vide)
            if projet_data.adresse is not None:
                projet.adresse = projet_data.adresse if projet_data.adresse else None
            if projet_data.ville is not None:
                projet.ville = projet_data.ville if projet_data.ville else None
            if projet_data.province is not None:
                projet.province = projet_data.province if projet_data.province else None
            if projet_data.code_postal is not None:
                projet.code_postal = projet_data.code_postal if projet_data.code_postal else None
            if projet_data.notes is not None:
                projet.notes = projet_data.notes if projet_data.notes else None
            
            # Gérer les dates (peuvent être None ou chaîne vide)
            if projet_data.date_debut is not None:
                if projet_data.date_debut and projet_data.date_debut.strip():
                    # Extraire seulement la partie date (YYYY-MM-DD) si format complet
                    date_str = projet_data.date_debut.strip()
                    if ' ' in date_str:
                        date_str = date_str.split(' ')[0]
                    elif 'T' in date_str:
                        date_str = date_str.split('T')[0]
                    projet.date_debut = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    projet.date_debut = None
            if projet_data.date_fin_prevue is not None:
                if projet_data.date_fin_prevue and projet_data.date_fin_prevue.strip():
                    date_str = projet_data.date_fin_prevue.strip()
                    if ' ' in date_str:
                        date_str = date_str.split(' ')[0]
                    elif 'T' in date_str:
                        date_str = date_str.split('T')[0]
                    projet.date_fin_prevue = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    projet.date_fin_prevue = None
            if projet_data.date_fin_reelle is not None:
                if projet_data.date_fin_reelle and projet_data.date_fin_reelle.strip():
                    date_str = projet_data.date_fin_reelle.strip()
                    if ' ' in date_str:
                        date_str = date_str.split(' ')[0]
                    elif 'T' in date_str:
                        date_str = date_str.split('T')[0]
                    projet.date_fin_reelle = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    projet.date_fin_reelle = None
            
            # Gérer le budget
            if projet_data.budget_total is not None:
                projet.budget_total = projet_data.budget_total if projet_data.budget_total else 0
            
            projet.date_modification = datetime.utcnow()
            db.commit()
            
            return {"success": True, "data": projet.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du projet: {e}")
    
    @app.delete("/api/construction/projets/{projet_id}")
    async def delete_projet(projet_id: int, db: Session = Depends(get_construction_db)):
        """Supprimer un projet (avec vérification des dépendances)"""
        try:
            projet = db.query(Projet).filter(Projet.id_projet == projet_id).first()
            if not projet:
                raise HTTPException(status_code=404, detail="Projet non trouvé")
            
            # Vérifier s'il y a des dépendances
            commandes_count = db.query(Commande).filter(Commande.id_projet == projet_id).count()
            factures_count = db.query(FactureST).filter(FactureST.id_projet == projet_id).count()
            punchs_count = db.query(PunchEmploye).filter(PunchEmploye.id_projet == projet_id).count()
            
            if commandes_count > 0 or factures_count > 0 or punchs_count > 0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Impossible de supprimer le projet '{projet.nom}': {commandes_count} commandes, {factures_count} factures et {punchs_count} pointages associés. Supprimez d'abord ces éléments."
                )
            
            db.delete(projet)
            db.commit()
            
            return {"success": True, "message": f"Projet '{projet.nom}' supprimé avec succès"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression du projet: {e}")
    
    # ==========================================
    # ENDPOINTS FOURNISSEURS
    # ==========================================
    
    @app.get("/api/construction/fournisseurs")
    async def get_fournisseurs(db: Session = Depends(get_construction_db)):
        """Récupérer tous les fournisseurs"""
        try:
            fournisseurs = db.query(Fournisseur).order_by(Fournisseur.nom).all()
            return {"success": True, "data": [fournisseur.to_dict() for fournisseur in fournisseurs]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des fournisseurs: {e}")
    
    @app.get("/api/construction/fournisseurs/{fournisseur_id}")
    async def get_fournisseur(fournisseur_id: int, db: Session = Depends(get_construction_db)):
        """Récupérer un fournisseur par ID"""
        try:
            fournisseur = db.query(Fournisseur).filter(Fournisseur.id_fournisseur == fournisseur_id).first()
            if not fournisseur:
                raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
            return {"success": True, "data": fournisseur.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du fournisseur: {e}")
    
    @app.post("/api/construction/fournisseurs")
    async def create_fournisseur(fournisseur_data: FournisseurCreate, db: Session = Depends(get_construction_db)):
        """Créer un nouveau fournisseur"""
        try:
            nouveau_fournisseur = Fournisseur(**fournisseur_data.dict())
            db.add(nouveau_fournisseur)
            db.commit()
            db.refresh(nouveau_fournisseur)
            return {"success": True, "data": nouveau_fournisseur.to_dict()}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la création du fournisseur: {e}")
    
    @app.put("/api/construction/fournisseurs/{fournisseur_id}")
    async def update_fournisseur(fournisseur_id: int, fournisseur_data: FournisseurUpdate, db: Session = Depends(get_construction_db)):
        """Mettre à jour un fournisseur"""
        try:
            fournisseur = db.query(Fournisseur).filter(Fournisseur.id_fournisseur == fournisseur_id).first()
            if not fournisseur:
                raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
            
            # Mettre à jour les champs fournis
            if fournisseur_data.nom is not None:
                fournisseur.nom = fournisseur_data.nom
            if fournisseur_data.rue is not None:
                fournisseur.rue = fournisseur_data.rue if fournisseur_data.rue else None
            if fournisseur_data.ville is not None:
                fournisseur.ville = fournisseur_data.ville if fournisseur_data.ville else None
            if fournisseur_data.province is not None:
                fournisseur.province = fournisseur_data.province if fournisseur_data.province else None
            if fournisseur_data.code_postal is not None:
                fournisseur.code_postal = fournisseur_data.code_postal if fournisseur_data.code_postal else None
            if fournisseur_data.numero is not None:
                fournisseur.numero = fournisseur_data.numero if fournisseur_data.numero else None
            if fournisseur_data.adresse_courriel is not None:
                fournisseur.adresse_courriel = fournisseur_data.adresse_courriel if fournisseur_data.adresse_courriel else None
            
            fournisseur.date_modification = datetime.utcnow()
            db.commit()
            db.refresh(fournisseur)
            return {"success": True, "data": fournisseur.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du fournisseur: {e}")
    
    @app.delete("/api/construction/fournisseurs/{fournisseur_id}")
    async def delete_fournisseur(fournisseur_id: int, db: Session = Depends(get_construction_db)):
        """Supprimer un fournisseur (avec vérification des dépendances)"""
        try:
            fournisseur = db.query(Fournisseur).filter(Fournisseur.id_fournisseur == fournisseur_id).first()
            if not fournisseur:
                raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
            
            # Vérifier s'il y a des commandes associées
            commandes_count = db.query(Commande).filter(Commande.id_fournisseur == fournisseur_id).count()
            
            if commandes_count > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Impossible de supprimer ce fournisseur car {commandes_count} commande(s) y sont associée(s). Supprimez d'abord les commandes."
                )
            
            db.delete(fournisseur)
            db.commit()
            return {"success": True, "message": "Fournisseur supprimé avec succès"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression du fournisseur: {e}")
    
    # ==========================================
    # ENDPOINTS MATIÈRES PREMIÈRES
    # ==========================================
    
    @app.get("/api/construction/matieres-premieres")
    async def get_matieres_premieres(db: Session = Depends(get_construction_db)):
        """Récupérer toutes les matières premières"""
        try:
            matieres = db.query(MatierePremiere).order_by(MatierePremiere.nom).all()
            return {"success": True, "data": [matiere.to_dict() for matiere in matieres]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des matières premières: {e}")
    
    @app.get("/api/construction/matieres-premieres/{matiere_id}")
    async def get_matiere_premiere(matiere_id: int, db: Session = Depends(get_construction_db)):
        """Récupérer une matière première par ID"""
        try:
            matiere = db.query(MatierePremiere).filter(MatierePremiere.id_matiere_premiere == matiere_id).first()
            if not matiere:
                raise HTTPException(status_code=404, detail="Matière première non trouvée")
            return {"success": True, "data": matiere.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la matière première: {e}")
    
    @app.post("/api/construction/matieres-premieres")
    async def create_matiere_premiere(matiere_data: MatierePremiereCreate, db: Session = Depends(get_construction_db)):
        """Créer une nouvelle matière première"""
        try:
            nouvelle_matiere = MatierePremiere(**matiere_data.dict())
            db.add(nouvelle_matiere)
            db.commit()
            db.refresh(nouvelle_matiere)
            return {"success": True, "data": nouvelle_matiere.to_dict()}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la matière première: {e}")
    
    @app.put("/api/construction/matieres-premieres/{matiere_id}")
    async def update_matiere_premiere(matiere_id: int, matiere_data: MatierePremiereUpdate, db: Session = Depends(get_construction_db)):
        """Mettre à jour une matière première"""
        try:
            matiere = db.query(MatierePremiere).filter(MatierePremiere.id_matiere_premiere == matiere_id).first()
            if not matiere:
                raise HTTPException(status_code=404, detail="Matière première non trouvée")
            
            # Mettre à jour les champs fournis
            if matiere_data.nom is not None:
                matiere.nom = matiere_data.nom
            if matiere_data.notes is not None:
                matiere.notes = matiere_data.notes if matiere_data.notes else None
            
            matiere.date_modification = datetime.utcnow()
            db.commit()
            db.refresh(matiere)
            return {"success": True, "data": matiere.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la matière première: {e}")
    
    @app.delete("/api/construction/matieres-premieres/{matiere_id}")
    async def delete_matiere_premiere(matiere_id: int, db: Session = Depends(get_construction_db)):
        """Supprimer une matière première (avec vérification des dépendances)"""
        try:
            matiere = db.query(MatierePremiere).filter(MatierePremiere.id_matiere_premiere == matiere_id).first()
            if not matiere:
                raise HTTPException(status_code=404, detail="Matière première non trouvée")
            
            # Vérifier s'il y a des lignes de commande associées
            lignes_count = db.query(LigneCommande).filter(LigneCommande.id_matiere_premiere == matiere_id).count()
            
            if lignes_count > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Impossible de supprimer cette matière première car {lignes_count} ligne(s) de commande y sont associée(s). Supprimez d'abord les lignes de commande."
                )
            
            db.delete(matiere)
            db.commit()
            return {"success": True, "message": "Matière première supprimée avec succès"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de la matière première: {e}")
    
    # ==========================================
    # ENDPOINTS EMPLOYÉS
    # ==========================================
    
    @app.get("/api/construction/employes")
    async def get_employes(db: Session = Depends(get_construction_db)):
        """Récupérer tous les employés"""
        try:
            employes = db.query(Employe).order_by(Employe.nom, Employe.prenom).all()
            return {"success": True, "data": [employe.to_dict() for employe in employes]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des employés: {e}")
    
    @app.post("/api/construction/employes")
    async def create_employe(employe_data: EmployeCreate, db: Session = Depends(get_construction_db)):
        """Créer un nouvel employé"""
        try:
            nouvel_employe = Employe(**employe_data.dict())
            db.add(nouvel_employe)
            db.commit()
            db.refresh(nouvel_employe)
            return {"success": True, "data": nouvel_employe.to_dict()}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'employé: {e}")
    
    @app.get("/api/construction/employes/{employe_id}")
    async def get_employe(employe_id: int, db: Session = Depends(get_construction_db)):
        """Récupérer un employé par ID"""
        try:
            employe = db.query(Employe).filter(Employe.id_employe == employe_id).first()
            if not employe:
                raise HTTPException(status_code=404, detail="Employé non trouvé")
            return {"success": True, "data": employe.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'employé: {e}")
    
    @app.put("/api/construction/employes/{employe_id}")
    async def update_employe(employe_id: int, employe_data: EmployeUpdate, db: Session = Depends(get_construction_db)):
        """Mettre à jour un employé"""
        try:
            employe = db.query(Employe).filter(Employe.id_employe == employe_id).first()
            if not employe:
                raise HTTPException(status_code=404, detail="Employé non trouvé")
            
            for field, value in employe_data.dict(exclude_unset=True).items():
                setattr(employe, field, value)
            
            db.commit()
            db.refresh(employe)
            return {"success": True, "data": employe.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de l'employé: {e}")
    
    @app.delete("/api/construction/employes/{employe_id}")
    async def delete_employe(employe_id: int, db: Session = Depends(get_construction_db)):
        """Supprimer un employé"""
        try:
            employe = db.query(Employe).filter(Employe.id_employe == employe_id).first()
            if not employe:
                raise HTTPException(status_code=404, detail="Employé non trouvé")
            
            db.delete(employe)
            db.commit()
            return {"success": True, "message": "Employé supprimé avec succès"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de l'employé: {e}")
    
    # ==========================================
    # ENDPOINTS PUNCHS EMPLOYÉS
    # ==========================================
    
    @app.get("/api/construction/punchs-employes")
    async def get_punchs_employes(db: Session = Depends(get_construction_db)):
        """Récupérer tous les pointages d'employés"""
        try:
            punchs = db.query(PunchEmploye).order_by(desc(PunchEmploye.date)).all()
            return {"success": True, "data": [punch.to_dict() for punch in punchs]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des pointages: {e}")
    
    @app.get("/api/construction/punchs-employes/employe/{employe_id}")
    async def get_punchs_by_employe(employe_id: int, db: Session = Depends(get_construction_db)):
        """Récupérer les pointages d'un employé spécifique"""
        try:
            punchs = db.query(PunchEmploye).filter(PunchEmploye.id_employe == employe_id).order_by(desc(PunchEmploye.date)).all()
            return {"success": True, "data": [punch.to_dict() for punch in punchs]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des pointages: {e}")
    
    @app.post("/api/construction/punchs-employes")
    async def create_punch_employe(punch_data: PunchEmployeCreate, db: Session = Depends(get_construction_db)):
        """Créer un nouveau pointage d'employé"""
        try:
            # Convertir la date string en objet Date
            from datetime import datetime
            punch_date = datetime.strptime(punch_data.date, "%Y-%m-%d").date()
            
            nouveau_punch = PunchEmploye(
                id_employe=punch_data.id_employe,
                id_projet=punch_data.id_projet,
                date=punch_date,
                heure_travaillee=punch_data.heure_travaillee,
                section=punch_data.section
            )
            db.add(nouveau_punch)
            db.commit()
            db.refresh(nouveau_punch)
            return {"success": True, "data": nouveau_punch.to_dict()}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la création du pointage: {e}")
    
    @app.put("/api/construction/punchs-employes/{punch_id}")
    async def update_punch_employe(punch_id: int, punch_data: PunchEmployeUpdate, db: Session = Depends(get_construction_db)):
        """Mettre à jour un pointage d'employé"""
        try:
            punch = db.query(PunchEmploye).filter(PunchEmploye.id_punch == punch_id).first()
            if not punch:
                raise HTTPException(status_code=404, detail="Pointage non trouvé")
            
            # Mettre à jour les champs fournis
            if punch_data.id_employe is not None:
                punch.id_employe = punch_data.id_employe
            if punch_data.id_projet is not None:
                punch.id_projet = punch_data.id_projet
            if punch_data.date is not None:
                from datetime import datetime
                # Extraire seulement la partie date si format complet
                date_str = punch_data.date.strip()
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                elif 'T' in date_str:
                    date_str = date_str.split('T')[0]
                punch.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if punch_data.heure_travaillee is not None:
                punch.heure_travaillee = punch_data.heure_travaillee
            if punch_data.section is not None:
                punch.section = punch_data.section
            
            punch.date_modification = datetime.utcnow()
            db.commit()
            db.refresh(punch)
            return {"success": True, "data": punch.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du pointage: {e}")
    
    @app.delete("/api/construction/punchs-employes/{punch_id}")
    async def delete_punch_employe(punch_id: int, db: Session = Depends(get_construction_db)):
        """Supprimer un pointage d'employé"""
        try:
            punch = db.query(PunchEmploye).filter(PunchEmploye.id_punch == punch_id).first()
            if not punch:
                raise HTTPException(status_code=404, detail="Pointage non trouvé")
            
            db.delete(punch)
            db.commit()
            return {"success": True, "message": "Pointage supprimé avec succès"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression du pointage: {e}")
    
    # ==========================================
    # ENDPOINTS SOUS-TRAITANTS
    # ==========================================
    
    @app.get("/api/construction/sous-traitants")
    async def get_sous_traitants(db: Session = Depends(get_construction_db)):
        """Récupérer tous les sous-traitants"""
        try:
            sous_traitants = db.query(SousTraitant).order_by(SousTraitant.nom).all()
            return {"success": True, "data": [st.to_dict() for st in sous_traitants]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des sous-traitants: {e}")
    
    @app.post("/api/construction/sous-traitants")
    async def create_sous_traitant(st_data: SousTraitantCreate, db: Session = Depends(get_construction_db)):
        """Créer un nouveau sous-traitant"""
        try:
            nouveau_st = SousTraitant(**st_data.dict())
            db.add(nouveau_st)
            db.commit()
            db.refresh(nouveau_st)
            return {"success": True, "data": nouveau_st.to_dict()}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la création du sous-traitant: {e}")
    
    @app.get("/api/construction/sous-traitants/{st_id}")
    async def get_sous_traitant(st_id: int, db: Session = Depends(get_construction_db)):
        """Récupérer un sous-traitant par ID"""
        try:
            st = db.query(SousTraitant).filter(SousTraitant.id_st == st_id).first()
            if not st:
                raise HTTPException(status_code=404, detail="Sous-traitant non trouvé")
            return {"success": True, "data": st.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du sous-traitant: {e}")
    
    @app.put("/api/construction/sous-traitants/{st_id}")
    async def update_sous_traitant(st_id: int, st_data: SousTraitantUpdate, db: Session = Depends(get_construction_db)):
        """Mettre à jour un sous-traitant"""
        try:
            st = db.query(SousTraitant).filter(SousTraitant.id_st == st_id).first()
            if not st:
                raise HTTPException(status_code=404, detail="Sous-traitant non trouvé")
            
            # Mettre à jour les champs fournis
            if st_data.nom is not None:
                st.nom = st_data.nom
            if st_data.rue is not None:
                st.rue = st_data.rue if st_data.rue else None
            if st_data.ville is not None:
                st.ville = st_data.ville if st_data.ville else None
            if st_data.province is not None:
                st.province = st_data.province if st_data.province else None
            if st_data.code_postal is not None:
                st.code_postal = st_data.code_postal if st_data.code_postal else None
            if st_data.numero is not None:
                st.numero = st_data.numero if st_data.numero else None
            if st_data.adresse_courriel is not None:
                st.adresse_courriel = st_data.adresse_courriel if st_data.adresse_courriel else None
            
            st.date_modification = datetime.utcnow()
            db.commit()
            db.refresh(st)
            return {"success": True, "data": st.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du sous-traitant: {e}")
    
    @app.delete("/api/construction/sous-traitants/{st_id}")
    async def delete_sous_traitant(st_id: int, db: Session = Depends(get_construction_db)):
        """Supprimer un sous-traitant (avec vérification des dépendances)"""
        try:
            st = db.query(SousTraitant).filter(SousTraitant.id_st == st_id).first()
            if not st:
                raise HTTPException(status_code=404, detail="Sous-traitant non trouvé")
            
            # Vérifier s'il y a des factures associées
            factures_count = db.query(FactureST).filter(FactureST.id_st == st_id).count()
            
            if factures_count > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Impossible de supprimer ce sous-traitant car {factures_count} facture(s) y sont associée(s). Supprimez d'abord les factures."
                )
            
            db.delete(st)
            db.commit()
            return {"success": True, "message": "Sous-traitant supprimé avec succès"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression du sous-traitant: {e}")
    
    # ==========================================
    # ENDPOINTS FACTURES SOUS-TRAITANTS
    # ==========================================
    
    @app.get("/api/construction/factures-st")
    async def get_factures_st(db: Session = Depends(get_construction_db)):
        """Récupérer toutes les factures de sous-traitants"""
        try:
            from sqlalchemy import text, desc
            
            # Vérifier quelles colonnes existent dans la table
            result = db.execute(text("PRAGMA table_info(factures_st)"))
            existing_columns = [col[1] for col in result.fetchall()]
            
            # Colonnes de base qui doivent exister
            base_columns = ['id_facture', 'id_projet', 'id_st', 'montant', 'section', 'notes', 'date_creation', 'date_modification']
            # Colonnes optionnelles à ajouter
            optional_columns = ['reference', 'date_de_paiement', 'pdf_facture']
            
            # Construire la liste des colonnes à sélectionner
            columns_to_select = [col for col in base_columns if col in existing_columns]
            columns_to_select.extend([col for col in optional_columns if col in existing_columns])
            
            # Construire la requête SQL
            columns_str = ', '.join(columns_to_select)
            query = f"SELECT {columns_str} FROM factures_st ORDER BY date_creation DESC"
            
            result = db.execute(text(query))
            rows = result.fetchall()
            
            # Convertir les résultats en dictionnaires
            factures_data = []
            for row in rows:
                facture_dict = {}
                for idx, col_name in enumerate(columns_to_select):
                    value = row[idx]
                    # Formater les dates
                    if 'date' in col_name.lower() and value:
                        if isinstance(value, str):
                            facture_dict[col_name] = value
                        else:
                            facture_dict[col_name] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
                    else:
                        facture_dict[col_name] = value
                
                # Ajouter les relations si possible
                try:
                    facture_obj = db.query(FactureST).filter(FactureST.id_facture == facture_dict['id_facture']).first()
                    if facture_obj:
                        facture_dict['projet'] = facture_obj.projet.to_dict() if facture_obj.projet else None
                        facture_dict['sous_traitant'] = facture_obj.sous_traitant.to_dict() if facture_obj.sous_traitant else None
                except:
                    pass
                
                factures_data.append(facture_dict)
            
            return {"success": True, "data": factures_data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des factures: {e}")
    
    @app.get("/api/construction/factures-st/{facture_id}")
    async def get_facture_st(facture_id: int, db: Session = Depends(get_construction_db)):
        """Récupérer une facture par ID"""
        try:
            facture = db.query(FactureST).filter(FactureST.id_facture == facture_id).first()
            if not facture:
                raise HTTPException(status_code=404, detail="Facture non trouvée")
            return {"success": True, "data": facture.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la facture: {e}")
    
    @app.post("/api/construction/factures-st")
    async def create_facture_st(facture_data: FactureSTCreate, db: Session = Depends(get_construction_db)):
        """Créer une nouvelle facture de sous-traitant"""
        try:
            # Convertir la date de paiement si fournie
            date_de_paiement = None
            if facture_data.date_de_paiement:
                date_str = facture_data.date_de_paiement.strip()
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                elif 'T' in date_str:
                    date_str = date_str.split('T')[0]
                date_de_paiement = datetime.strptime(date_str, '%Y-%m-%d')
            
            nouvelle_facture = FactureST(
                id_projet=facture_data.id_projet,
                id_st=facture_data.id_st,
                montant=facture_data.montant,
                section=facture_data.section,
                notes=facture_data.notes,
                reference=facture_data.reference,
                date_de_paiement=date_de_paiement,
                pdf_facture=facture_data.pdf_facture
            )
            db.add(nouvelle_facture)
            db.commit()
            db.refresh(nouvelle_facture)
            return {"success": True, "data": nouvelle_facture.to_dict()}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la facture: {e}")
    
    @app.put("/api/construction/factures-st/{facture_id}")
    async def update_facture_st(facture_id: int, facture_data: FactureSTUpdate, db: Session = Depends(get_construction_db)):
        """Mettre à jour une facture de sous-traitant"""
        try:
            facture = db.query(FactureST).filter(FactureST.id_facture == facture_id).first()
            if not facture:
                raise HTTPException(status_code=404, detail="Facture non trouvée")
            
            # Mettre à jour les champs fournis
            if facture_data.id_projet is not None:
                facture.id_projet = facture_data.id_projet
            if facture_data.id_st is not None:
                facture.id_st = facture_data.id_st
            if facture_data.montant is not None:
                facture.montant = facture_data.montant
            if facture_data.section is not None:
                facture.section = facture_data.section if facture_data.section else None
            if facture_data.notes is not None:
                facture.notes = facture_data.notes if facture_data.notes else None
            if facture_data.reference is not None:
                facture.reference = facture_data.reference if facture_data.reference else None
            if facture_data.date_de_paiement is not None:
                if facture_data.date_de_paiement and facture_data.date_de_paiement.strip():
                    date_str = facture_data.date_de_paiement.strip()
                    if ' ' in date_str:
                        date_str = date_str.split(' ')[0]
                    elif 'T' in date_str:
                        date_str = date_str.split('T')[0]
                    facture.date_de_paiement = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    facture.date_de_paiement = None
            if facture_data.pdf_facture is not None:
                facture.pdf_facture = facture_data.pdf_facture if facture_data.pdf_facture else None
            
            facture.date_modification = datetime.utcnow()
            db.commit()
            db.refresh(facture)
            return {"success": True, "data": facture.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la facture: {e}")
    
    @app.delete("/api/construction/factures-st/{facture_id}")
    async def delete_facture_st(facture_id: int, db: Session = Depends(get_construction_db)):
        """Supprimer une facture de sous-traitant"""
        try:
            facture = db.query(FactureST).filter(FactureST.id_facture == facture_id).first()
            if not facture:
                raise HTTPException(status_code=404, detail="Facture non trouvée")
            
            # Supprimer le PDF de Backblaze si présent
            if facture.pdf_facture:
                try:
                    from storage_service import get_storage_service
                    storage_service = get_storage_service()
                    # Le pdf_facture contient le nom du fichier, on doit construire le s3_key
                    s3_key = f"factures/{facture.pdf_facture}"
                    storage_service.delete_pdf(s3_key)
                except Exception as e:
                    print(f"⚠️ Erreur lors de la suppression du PDF: {e}")
            
            db.delete(facture)
            db.commit()
            return {"success": True, "message": "Facture supprimée avec succès"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de la facture: {e}")
    
    # ==========================================
    # ENDPOINTS COMMANDES
    # ==========================================
    
    @app.get("/api/construction/commandes")
    async def get_commandes(db: Session = Depends(get_construction_db)):
        """Récupérer toutes les commandes"""
        try:
            commandes = db.query(Commande).order_by(Commande.date_creation.desc()).all()
            result = []
            for commande in commandes:
                cmd_dict = commande.to_dict()
                # Ajouter les lignes de commande
                cmd_dict['lignes_commande'] = [ligne.to_dict() for ligne in commande.lignes_commande]
                result.append(cmd_dict)
            return {"success": True, "data": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des commandes: {e}")
    
    @app.get("/api/construction/commandes/{commande_id}")
    async def get_commande(commande_id: int, db: Session = Depends(get_construction_db)):
        """Récupérer une commande par ID avec ses lignes"""
        try:
            commande = db.query(Commande).filter(Commande.id_commande == commande_id).first()
            if not commande:
                raise HTTPException(status_code=404, detail="Commande non trouvée")
            result = commande.to_dict()
            result['lignes_commande'] = [ligne.to_dict() for ligne in commande.lignes_commande]
            return {"success": True, "data": result}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la commande: {e}")
    
    @app.post("/api/construction/commandes")
    async def create_commande(commande_data: CommandeCreate, db: Session = Depends(get_construction_db)):
        """Créer une nouvelle commande avec ses lignes"""
        try:
            # Calculer le montant total depuis les lignes
            montant_total = sum(ligne.get('montant', 0) for ligne in commande_data.lignes_commande)
            
            # Créer la commande
            nouvelle_commande = Commande(
                id_projet=commande_data.id_projet,
                id_fournisseur=commande_data.id_fournisseur,
                montant=montant_total,
                statut=commande_data.statut or "en_attente",
                type_de_paiement=commande_data.type_de_paiement,
                notes=commande_data.notes,
                pdf_commande=commande_data.pdf_commande
            )
            db.add(nouvelle_commande)
            db.flush()  # Pour obtenir l'ID de la commande
            
            # Créer les lignes de commande
            for ligne_data in commande_data.lignes_commande:
                nouvelle_ligne = LigneCommande(
                    id_commande=nouvelle_commande.id_commande,
                    id_matiere_premiere=ligne_data['id_matiere_premiere'],
                    quantite=ligne_data['quantite'],
                    unite=ligne_data['unite'],
                    montant=ligne_data['montant'],
                    section=ligne_data.get('section')
                )
                db.add(nouvelle_ligne)
            
            db.commit()
            db.refresh(nouvelle_commande)
            
            # Retourner la commande avec ses lignes
            result = nouvelle_commande.to_dict()
            result['lignes_commande'] = [ligne.to_dict() for ligne in nouvelle_commande.lignes_commande]
            return {"success": True, "data": result}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la commande: {e}")
    
    @app.put("/api/construction/commandes/{commande_id}")
    async def update_commande(commande_id: int, commande_data: CommandeUpdate, db: Session = Depends(get_construction_db)):
        """Mettre à jour une commande"""
        try:
            commande = db.query(Commande).filter(Commande.id_commande == commande_id).first()
            if not commande:
                raise HTTPException(status_code=404, detail="Commande non trouvée")
            
            if commande_data.id_projet is not None:
                commande.id_projet = commande_data.id_projet
            if commande_data.id_fournisseur is not None:
                commande.id_fournisseur = commande_data.id_fournisseur
            if commande_data.montant is not None:
                commande.montant = commande_data.montant
            if commande_data.statut is not None:
                commande.statut = commande_data.statut
            if commande_data.type_de_paiement is not None:
                commande.type_de_paiement = commande_data.type_de_paiement if commande_data.type_de_paiement else None
            if commande_data.notes is not None:
                commande.notes = commande_data.notes if commande_data.notes else None
            if commande_data.pdf_commande is not None:
                commande.pdf_commande = commande_data.pdf_commande if commande_data.pdf_commande else None
            
            commande.date_modification = datetime.utcnow()
            db.commit()
            db.refresh(commande)
            
            result = commande.to_dict()
            result['lignes_commande'] = [ligne.to_dict() for ligne in commande.lignes_commande]
            return {"success": True, "data": result}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la commande: {e}")
    
    @app.delete("/api/construction/commandes/{commande_id}")
    async def delete_commande(commande_id: int, db: Session = Depends(get_construction_db)):
        """Supprimer une commande et ses lignes associées"""
        try:
            commande = db.query(Commande).filter(Commande.id_commande == commande_id).first()
            if not commande:
                raise HTTPException(status_code=404, detail="Commande non trouvée")
            
            # Supprimer manuellement les lignes de commande d'abord (pour éviter les problèmes de cascade)
            from models_construction import LigneCommande
            lignes = db.query(LigneCommande).filter(LigneCommande.id_commande == commande_id).all()
            for ligne in lignes:
                db.delete(ligne)
            
            # Supprimer le PDF de Backblaze si présent
            if commande.pdf_commande:
                try:
                    from storage_service import get_storage_service
                    storage_service = get_storage_service()
                    # Le pdf_commande contient le nom du fichier, on doit construire le s3_key
                    s3_key = f"commandes/{commande.pdf_commande}"
                    storage_service.delete_pdf(s3_key)
                except Exception as e:
                    print(f"⚠️ Erreur lors de la suppression du PDF: {e}")
            
            # Supprimer la commande
            db.delete(commande)
            db.commit()
            return {"success": True, "message": "Commande supprimée avec succès"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de la commande: {e}")
    
    # ==========================================
    # ENDPOINTS LIGNES DE COMMANDE
    # ==========================================
    
    @app.get("/api/construction/lignes-commande")
    async def get_lignes_commande(db: Session = Depends(get_construction_db)):
        """Récupérer toutes les lignes de commande"""
        try:
            lignes = db.query(LigneCommande).order_by(LigneCommande.id_commande, LigneCommande.id_ligne).all()
            return {"success": True, "data": [ligne.to_dict() for ligne in lignes]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des lignes de commande: {e}")
    
    @app.get("/api/construction/lignes-commande/commande/{commande_id}")
    async def get_lignes_by_commande(commande_id: int, db: Session = Depends(get_construction_db)):
        """Récupérer toutes les lignes d'une commande"""
        try:
            lignes = db.query(LigneCommande).filter(LigneCommande.id_commande == commande_id).all()
            return {"success": True, "data": [ligne.to_dict() for ligne in lignes]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des lignes de commande: {e}")
    
    @app.post("/api/construction/lignes-commande")
    async def create_ligne_commande(ligne_data: LigneCommandeCreate, db: Session = Depends(get_construction_db)):
        """Créer une nouvelle ligne de commande"""
        try:
            nouvelle_ligne = LigneCommande(**ligne_data.dict())
            db.add(nouvelle_ligne)
            
            # Mettre à jour le montant total de la commande
            from sqlalchemy import func
            commande = db.query(Commande).filter(Commande.id_commande == ligne_data.id_commande).first()
            if commande:
                # Recalculer le montant total
                total = db.query(func.sum(LigneCommande.montant)).filter(
                    LigneCommande.id_commande == ligne_data.id_commande
                ).scalar() or 0
                commande.montant = total
                commande.date_modification = datetime.utcnow()
            
            db.commit()
            db.refresh(nouvelle_ligne)
            return {"success": True, "data": nouvelle_ligne.to_dict()}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la ligne de commande: {e}")
    
    @app.put("/api/construction/lignes-commande/{ligne_id}")
    async def update_ligne_commande(ligne_id: int, ligne_data: LigneCommandeUpdate, db: Session = Depends(get_construction_db)):
        """Mettre à jour une ligne de commande"""
        try:
            ligne = db.query(LigneCommande).filter(LigneCommande.id_ligne == ligne_id).first()
            if not ligne:
                raise HTTPException(status_code=404, detail="Ligne de commande non trouvée")
            
            if ligne_data.id_matiere_premiere is not None:
                ligne.id_matiere_premiere = ligne_data.id_matiere_premiere
            if ligne_data.quantite is not None:
                ligne.quantite = ligne_data.quantite
            if ligne_data.unite is not None:
                ligne.unite = ligne_data.unite
            if ligne_data.montant is not None:
                ligne.montant = ligne_data.montant
            if ligne_data.section is not None:
                ligne.section = ligne_data.section if ligne_data.section else None
            
            ligne.date_modification = datetime.utcnow()
            
            # Mettre à jour le montant total de la commande
            from sqlalchemy import func
            commande = db.query(Commande).filter(Commande.id_commande == ligne.id_commande).first()
            if commande:
                total = db.query(func.sum(LigneCommande.montant)).filter(
                    LigneCommande.id_commande == ligne.id_commande
                ).scalar() or 0
                commande.montant = total
                commande.date_modification = datetime.utcnow()
            
            db.commit()
            db.refresh(ligne)
            return {"success": True, "data": ligne.to_dict()}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la ligne de commande: {e}")
    
    @app.delete("/api/construction/lignes-commande/{ligne_id}")
    async def delete_ligne_commande(ligne_id: int, db: Session = Depends(get_construction_db)):
        """Supprimer une ligne de commande"""
        try:
            ligne = db.query(LigneCommande).filter(LigneCommande.id_ligne == ligne_id).first()
            if not ligne:
                raise HTTPException(status_code=404, detail="Ligne de commande non trouvée")
            
            commande_id = ligne.id_commande
            db.delete(ligne)
            
            # Mettre à jour le montant total de la commande
            from sqlalchemy import func
            commande = db.query(Commande).filter(Commande.id_commande == commande_id).first()
            if commande:
                total = db.query(func.sum(LigneCommande.montant)).filter(
                    LigneCommande.id_commande == commande_id
                ).scalar() or 0
                commande.montant = total
                commande.date_modification = datetime.utcnow()
            
            db.commit()
            return {"success": True, "message": "Ligne de commande supprimée avec succès"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de la ligne de commande: {e}")
    
    # ==========================================
    # ENDPOINT DE TEST CONSTRUCTION
    # ==========================================
    
    @app.get("/api/construction/test")
    async def test_construction_api():
        """Test de l'API construction"""
        return {
            "success": True,
            "message": "API Construction fonctionnelle",
            "timestamp": datetime.utcnow().isoformat(),
            "tables": [
                "projets", "fournisseurs", "matieres_premieres", 
                "commandes", "lignes_commande", "employes", 
                "punchs_employes", "sous_traitants", "factures_st"
            ]
        }

else:
    print("⚠️ API Construction non disponible - modules non chargés")

# ============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 