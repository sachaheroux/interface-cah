from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
from datetime import datetime
import json
import os
import platform

app = FastAPI(
    title="Interface CAH API",
    description="API pour la gestion de construction - Interface CAH",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "https://interface-cahs.vercel.app"
    ],  # Frontend local (différents ports) et Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic pour la validation des données
class Address(BaseModel):
    street: str
    city: str
    province: str
    postalCode: str
    country: str

class Characteristics(BaseModel):
    parking: int = 0
    elevator: bool = False
    balconies: int = 0
    storage: bool = False
    laundry: bool = False
    airConditioning: bool = False
    heating: str = "electric"
    internet: bool = False
    security: bool = False

class Financials(BaseModel):
    purchasePrice: float = 0
    downPayment: float = 0
    interestRate: float = 0
    currentValue: float = 0

class Contacts(BaseModel):
    owner: str = ""
    bank: str = ""
    contractor: str = ""

class Building(BaseModel):
    id: Optional[int] = None
    name: str
    address: Address
    type: str
    units: int
    floors: int
    yearBuilt: int
    totalArea: Optional[int] = None
    characteristics: Optional[Characteristics] = None
    financials: Optional[Financials] = None
    contacts: Optional[Contacts] = None
    notes: str = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class BuildingCreate(BaseModel):
    name: str
    address: Address
    type: str
    units: int
    floors: int
    yearBuilt: int
    totalArea: Optional[int] = None
    characteristics: Optional[Characteristics] = None
    financials: Optional[Financials] = None
    contacts: Optional[Contacts] = None
    notes: str = ""

class BuildingUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[Address] = None
    type: Optional[str] = None
    units: Optional[int] = None
    floors: Optional[int] = None
    yearBuilt: Optional[int] = None
    totalArea: Optional[int] = None
    characteristics: Optional[Characteristics] = None
    financials: Optional[Financials] = None
    contacts: Optional[Contacts] = None
    notes: Optional[str] = None

# Modèles pour les locataires
class PersonalAddress(BaseModel):
    street: str = ""
    city: str = ""
    province: str = "QC"
    postalCode: str = ""
    country: str = "Canada"

class EmergencyContact(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    relationship: str = ""

class TenantFinancial(BaseModel):
    monthlyIncome: int = 0
    creditScore: int = 0
    bankAccount: str = ""
    employer: str = ""
    employerPhone: str = ""

class Tenant(BaseModel):
    id: Optional[int] = None
    name: str
    email: str = ""
    phone: str = ""
    status: str = "active"  # active, pending, inactive, former
    personalAddress: Optional[PersonalAddress] = None
    emergencyContact: Optional[EmergencyContact] = None
    financial: Optional[TenantFinancial] = None
    building: str = ""
    unit: str = ""
    notes: str = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class TenantCreate(BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    status: str = "active"
    personalAddress: Optional[PersonalAddress] = None
    emergencyContact: Optional[EmergencyContact] = None
    financial: Optional[TenantFinancial] = None
    building: str = ""
    unit: str = ""
    notes: str = ""

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    personalAddress: Optional[PersonalAddress] = None
    emergencyContact: Optional[EmergencyContact] = None
    financial: Optional[TenantFinancial] = None
    building: Optional[str] = None
    unit: Optional[str] = None
    notes: Optional[str] = None

# Système de persistance avec fichier JSON
# Utilisation du répertoire recommandé par Render : /opt/render/project/src/data
# En local, utiliser un répertoire relatif pour éviter les problèmes de permissions
if platform.system() == "Windows" or os.environ.get("ENVIRONMENT") == "development":
    # En local (Windows) ou développement, utiliser un répertoire relatif
    DATA_DIR = os.environ.get("DATA_DIR", "./data")
else:
    # Sur Render ou production Linux, utiliser le répertoire recommandé
    DATA_DIR = os.environ.get("DATA_DIR", "/opt/render/project/src/data")

BUILDINGS_DATA_FILE = os.path.join(DATA_DIR, "buildings_data.json")
TENANTS_DATA_FILE = os.path.join(DATA_DIR, "tenants_data.json")
ASSIGNMENTS_DATA_FILE = os.path.join(DATA_DIR, "assignments_data.json")

# Créer le répertoire de données s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# DEBUGGING - Afficher les informations de persistance
print("=" * 60)
print("🔧 DIAGNOSTIC DISQUE PERSISTANT")
print("=" * 60)
print(f"📂 DATA_DIR (env): {os.environ.get('DATA_DIR', 'NON DÉFINIE')}")
print(f"📂 DATA_DIR (utilisé): {DATA_DIR}")
print(f"📄 Fichier immeubles: {BUILDINGS_DATA_FILE}")
print(f"📄 Fichier locataires: {TENANTS_DATA_FILE}")
print(f"📄 Fichier assignations: {ASSIGNMENTS_DATA_FILE}")
print(f"📁 Répertoire existe: {os.path.exists(DATA_DIR)}")
print(f"📝 Fichier immeubles existe: {os.path.exists(BUILDINGS_DATA_FILE)}")
print(f"📝 Fichier locataires existe: {os.path.exists(TENANTS_DATA_FILE)}")
print(f"📝 Fichier assignations existe: {os.path.exists(ASSIGNMENTS_DATA_FILE)}")
print(f"🔒 Permissions lecture: {os.access(DATA_DIR, os.R_OK)}")
print(f"🔒 Permissions écriture: {os.access(DATA_DIR, os.W_OK)}")
print(f"💾 Répertoire de travail: {os.getcwd()}")
print(f"🗂️  Contenu DATA_DIR: {os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else 'N/A'}")
print("=" * 60)

# Cache pour les données
buildings_cache = None
tenants_cache = None
assignments_cache = None

def get_buildings_cache():
    """Obtenir les données des immeubles avec cache"""
    global buildings_cache
    if buildings_cache is None:
        buildings_cache = load_buildings_data()
    return buildings_cache

def get_tenants_cache():
    """Obtenir les données des locataires avec cache"""
    global tenants_cache
    if tenants_cache is None:
        tenants_cache = load_tenants_data()
    return tenants_cache

def get_assignments_cache():
    """Obtenir les données des assignations avec cache"""
    global assignments_cache
    if assignments_cache is None:
        assignments_cache = load_assignments_data()
    return assignments_cache

def invalidate_caches():
    """Invalider tous les caches"""
    global buildings_cache, tenants_cache, assignments_cache
    buildings_cache = None
    tenants_cache = None
    assignments_cache = None

def load_buildings_data():
    """Charger les données depuis le fichier JSON"""
    try:
        if os.path.exists(BUILDINGS_DATA_FILE):
            with open(BUILDINGS_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Données immeubles chargées: {len(data.get('buildings', []))} immeubles")
                return data
    except Exception as e:
        print(f"Erreur chargement données immeubles depuis fichier: {e}")
    
    # Retourner structure vide si pas de fichier ou erreur
    return {"buildings": [], "next_id": 1}

def save_buildings_data(data):
    """Sauvegarder les données dans le fichier JSON"""
    try:
        with open(BUILDINGS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Données immeubles sauvegardées: {len(data.get('buildings', []))} immeubles")
        return True
    except Exception as e:
        print(f"Erreur sauvegarde immeubles: {e}")
        return False

def load_tenants_data():
    """Charger les données des locataires depuis le fichier JSON"""
    try:
        if os.path.exists(TENANTS_DATA_FILE):
            with open(TENANTS_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Données locataires chargées: {len(data.get('tenants', []))} locataires")
                return data
    except Exception as e:
        print(f"Erreur chargement données locataires depuis fichier: {e}")
    
    # Retourner structure vide avec quelques locataires fictifs pour commencer
    default_data = {
        "tenants": [
            {
                "id": 1,
                "name": "Jean Dupont",
                "email": "jean.dupont@email.com",
                "phone": "(514) 555-0123",
                "status": "active",
                "building": "Immeuble A",
                "unit": "A-101",
                "createdAt": "2024-01-15T10:00:00Z",
                "updatedAt": "2024-01-15T10:00:00Z"
            },
            {
                "id": 2,
                "name": "Marie Martin",
                "email": "marie.martin@email.com",
                "phone": "(514) 555-0124",
                "status": "active",
                "building": "Immeuble A",
                "unit": "A-102",
                "createdAt": "2024-01-20T14:30:00Z",
                "updatedAt": "2024-01-20T14:30:00Z"
            },
            {
                "id": 3,
                "name": "Pierre Durand",
                "email": "pierre.durand@email.com",
                "phone": "(514) 555-0125",
                "status": "pending",
                "building": "Immeuble B",
                "unit": "B-201",
                "createdAt": "2024-02-01T09:15:00Z",
                "updatedAt": "2024-02-01T09:15:00Z"
            }
        ],
        "next_id": 4
    }
    
    # Sauvegarder les données par défaut
    save_tenants_data(default_data)
    return default_data

def save_tenants_data(data):
    """Sauvegarder les données des locataires dans le fichier JSON"""
    try:
        with open(TENANTS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Données locataires sauvegardées: {len(data.get('tenants', []))} locataires")
        return True
    except Exception as e:
        print(f"Erreur sauvegarde locataires: {e}")
        return False

def load_assignments_data():
    """Charger les données des assignations depuis le fichier JSON"""
    try:
        if os.path.exists(ASSIGNMENTS_DATA_FILE):
            with open(ASSIGNMENTS_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Données assignations chargées: {len(data.get('assignments', []))} assignations")
                return data
    except Exception as e:
        print(f"Erreur chargement données assignations depuis fichier: {e}")
    
    # Retourner structure vide si pas de fichier ou erreur
    return {"assignments": [], "next_id": 1}

def save_assignments_data(data):
    """Sauvegarder les données des assignations dans le fichier JSON"""
    try:
        with open(ASSIGNMENTS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Données assignations sauvegardées: {len(data.get('assignments', []))} assignations")
        return True
    except Exception as e:
        print(f"Erreur sauvegarde assignations: {e}")
        return False

def update_buildings_cache(data):
    """Mettre à jour le cache mémoire des immeubles"""
    global buildings_cache
    buildings_cache = data
    save_buildings_data(data)

def update_tenants_cache(data):
    """Mettre à jour le cache mémoire des locataires"""
    global tenants_cache
    tenants_cache = data
    save_tenants_data(data)

def update_assignments_cache(data):
    """Mettre à jour le cache mémoire des assignations"""
    global assignments_cache
    assignments_cache = data
    save_assignments_data(data)

# Route de test de base
@app.get("/")
async def root():
    return {"message": "Interface CAH API - Système de gestion de construction"}

# Route de santé pour vérifier que l'API fonctionne
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API fonctionnelle"}

# Routes temporaires pour les modules (à développer plus tard)
@app.get("/api/dashboard")
async def get_dashboard_data():
    """Retourner les données du tableau de bord calculées à partir des vrais immeubles"""
    try:
        # Récupérer tous les immeubles du cache
        data = get_buildings_cache()
        buildings = data.get("buildings", [])
        
        # Calculer les statistiques réelles
        total_buildings = len(buildings)
        total_units = sum(building.get("units", 0) for building in buildings)
        total_portfolio_value = sum(
            building.get("financials", {}).get("currentValue", 0) 
            for building in buildings
        )
        
        # Calculer le taux d'occupation (simulation : 85-95% d'occupation selon l'âge)
        occupied_units = 0
        for building in buildings:
            units = building.get("units", 0)
            year_built = building.get("yearBuilt", 2020)
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

# Routes CRUD pour les immeubles avec persistance
@app.get("/api/buildings")
async def get_buildings():
    """Récupérer tous les immeubles"""
    try:
        data = get_buildings_cache()
        return data.get("buildings", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des immeubles: {str(e)}")

@app.get("/api/buildings/{building_id}")
async def get_building(building_id: int):
    """Récupérer un immeuble spécifique par ID"""
    try:
        data = get_buildings_cache()
        buildings = data.get("buildings", [])
        
        for building in buildings:
            if building.get("id") == building_id:
                return building
        
        raise HTTPException(status_code=404, detail="Immeuble non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'immeuble: {str(e)}")

@app.post("/api/buildings")
async def create_building(building_data: BuildingCreate):
    """Créer un nouvel immeuble"""
    try:
        data = get_buildings_cache()
        
        # Créer le nouvel immeuble avec un ID unique
        new_building = building_data.dict()
        new_building["id"] = data["next_id"]
        new_building["createdAt"] = datetime.now().isoformat() + "Z"
        new_building["updatedAt"] = datetime.now().isoformat() + "Z"
        
        # Ajouter aux données
        data["buildings"].append(new_building)
        data["next_id"] += 1
        
        # Mettre à jour le cache
        update_buildings_cache(data)
        
        return new_building
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'immeuble: {str(e)}")

@app.put("/api/buildings/{building_id}")
async def update_building(building_id: int, building_data: BuildingUpdate):
    """Mettre à jour un immeuble existant"""
    try:
        data = get_buildings_cache()
        buildings = data.get("buildings", [])
        
        # Trouver et mettre à jour l'immeuble
        building_found = False
        for i, building in enumerate(buildings):
            if building.get("id") == building_id:
                # Mettre à jour seulement les champs fournis
                update_data = building_data.dict(exclude_unset=True)
                buildings[i].update(update_data)
                buildings[i]["updatedAt"] = datetime.now().isoformat() + "Z"
                building_found = True
                
                # Mettre à jour le cache
                update_buildings_cache(data)
                
                return buildings[i]
        
        if not building_found:
            raise HTTPException(status_code=404, detail="Immeuble non trouvé")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de l'immeuble: {str(e)}")

@app.delete("/api/buildings/{building_id}")
async def delete_building(building_id: int):
    """Supprimer un immeuble"""
    try:
        data = get_buildings_cache()
        buildings = data.get("buildings", [])
        
        # Trouver l'immeuble à supprimer
        building_to_delete = None
        for building in buildings:
            if building.get("id") == building_id:
                building_to_delete = building
                break
        
        if not building_to_delete:
            raise HTTPException(status_code=404, detail="Immeuble non trouvé")
        
        # Supprimer l'immeuble
        data["buildings"] = [b for b in buildings if b.get("id") != building_id]
        
        # Mettre à jour le cache
        update_buildings_cache(data)
        
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
        data = get_tenants_cache()
        tenants = data.get("tenants", [])
        return {"data": tenants}
    except Exception as e:
        print(f"Erreur lors du chargement des locataires: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des locataires: {str(e)}")

@app.get("/api/tenants/{tenant_id}")
async def get_tenant(tenant_id: int):
    """Récupérer un locataire spécifique par ID"""
    try:
        data = get_tenants_cache()
        tenants = data.get("tenants", [])
        
        for tenant in tenants:
            if tenant.get("id") == tenant_id:
                return {"data": tenant}
        
        raise HTTPException(status_code=404, detail="Locataire non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du locataire: {str(e)}")

@app.post("/api/tenants")
async def create_tenant(tenant_data: TenantCreate):
    """Créer un nouveau locataire"""
    try:
        data = get_tenants_cache()
        
        # Créer le nouveau locataire avec un ID unique
        new_tenant = tenant_data.dict()
        new_tenant["id"] = data["next_id"]
        new_tenant["createdAt"] = datetime.now().isoformat() + "Z"
        new_tenant["updatedAt"] = datetime.now().isoformat() + "Z"
        
        # Ajouter aux données
        data["tenants"].append(new_tenant)
        data["next_id"] += 1
        
        # Mettre à jour le cache
        update_tenants_cache(data)
        
        return {"data": new_tenant}
    except Exception as e:
        print(f"Erreur lors de la création du locataire: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du locataire: {str(e)}")

@app.put("/api/tenants/{tenant_id}")
async def update_tenant(tenant_id: int, tenant_data: TenantUpdate):
    """Mettre à jour un locataire existant"""
    try:
        data = get_tenants_cache()
        tenants = data.get("tenants", [])
        
        # Trouver et mettre à jour le locataire
        tenant_found = False
        for i, tenant in enumerate(tenants):
            if tenant.get("id") == tenant_id:
                # Mettre à jour seulement les champs fournis
                update_data = tenant_data.dict(exclude_unset=True)
                tenants[i].update(update_data)
                tenants[i]["updatedAt"] = datetime.now().isoformat() + "Z"
                tenant_found = True
                
                # Mettre à jour le cache
                update_tenants_cache(data)
                
                return {"data": tenants[i]}
        
        if not tenant_found:
            raise HTTPException(status_code=404, detail="Locataire non trouvé")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la mise à jour du locataire: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du locataire: {str(e)}")

@app.delete("/api/tenants/{tenant_id}")
async def delete_tenant(tenant_id: int):
    """Supprimer un locataire"""
    try:
        data = get_tenants_cache()
        tenants = data.get("tenants", [])
        
        # Trouver le locataire à supprimer
        tenant_to_delete = None
        for tenant in tenants:
            if tenant.get("id") == tenant_id:
                tenant_to_delete = tenant
                break
        
        if not tenant_to_delete:
            raise HTTPException(status_code=404, detail="Locataire non trouvé")
        
        # Supprimer le locataire
        data["tenants"] = [t for t in tenants if t.get("id") != tenant_id]
        
        # Mettre à jour le cache
        update_tenants_cache(data)
        
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
@app.get("/api/assignments")
async def get_assignments():
    """Récupérer toutes les assignations locataires-unités"""
    try:
        data = get_assignments_cache()
        assignments = data.get("assignments", [])
        return {"data": assignments}
    except Exception as e:
        print(f"Erreur lors du chargement des assignations: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des assignations: {str(e)}")

@app.post("/api/assignments")
async def create_assignment(assignment_data: dict):
    """Créer une nouvelle assignation locataire-unité"""
    try:
        data = get_assignments_cache()
        
        # Créer la nouvelle assignation avec un ID unique
        new_assignment = {
            "id": data["next_id"],
            "unitId": assignment_data.get("unitId"),
            "tenantId": assignment_data.get("tenantId"),
            "tenantData": assignment_data.get("tenantData", {}),
            "assignedAt": datetime.now().isoformat() + "Z",
            "createdAt": datetime.now().isoformat() + "Z",
            "updatedAt": datetime.now().isoformat() + "Z"
        }
        
        # Supprimer l'ancienne assignation pour ce locataire s'il y en a une
        data["assignments"] = [a for a in data["assignments"] if a.get("tenantId") != assignment_data.get("tenantId")]
        
        # Ajouter la nouvelle assignation
        data["assignments"].append(new_assignment)
        data["next_id"] += 1
        
        # Mettre à jour le cache
        update_assignments_cache(data)
        
        print(f"Assignation créée: Locataire {assignment_data.get('tenantId')} → Unité {assignment_data.get('unitId')}")
        return {"data": new_assignment}
    except Exception as e:
        print(f"Erreur lors de la création de l'assignation: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'assignation: {str(e)}")

@app.delete("/api/assignments/tenant/{tenant_id}")
async def remove_tenant_assignment(tenant_id: int):
    """Retirer un locataire de toute unité"""
    try:
        data = get_assignments_cache()
        
        # Supprimer toutes les assignations pour ce locataire
        original_count = len(data["assignments"])
        data["assignments"] = [a for a in data["assignments"] if a.get("tenantId") != tenant_id]
        removed_count = original_count - len(data["assignments"])
        
        if removed_count == 0:
            raise HTTPException(status_code=404, detail="Aucune assignation trouvée pour ce locataire")
        
        # Mettre à jour le cache
        update_assignments_cache(data)
        
        print(f"Assignation supprimée pour le locataire {tenant_id}")
        return {"message": f"Locataire retiré de son unité ({removed_count} assignation(s) supprimée(s))"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression de l'assignation: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.get("/api/assignments/unit/{unit_id}")
async def get_unit_assignments(unit_id: str):
    """Récupérer toutes les assignations pour une unité spécifique"""
    try:
        data = get_assignments_cache()
        assignments = data.get("assignments", [])
        
        # Filtrer les assignations pour cette unité
        unit_assignments = [a for a in assignments if a.get("unitId") == unit_id]
        
        return {"data": unit_assignments}
    except Exception as e:
        print(f"Erreur lors du chargement des assignations d'unité: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des assignations d'unité: {str(e)}")

@app.get("/api/assignments/tenant/{tenant_id}")
async def get_tenant_assignment(tenant_id: int):
    """Récupérer l'assignation d'un locataire spécifique"""
    try:
        data = get_assignments_cache()
        assignments = data.get("assignments", [])
        
        # Trouver l'assignation pour ce locataire
        tenant_assignment = next((a for a in assignments if a.get("tenantId") == tenant_id), None)
        
        return {"data": tenant_assignment}
    except Exception as e:
        print(f"Erreur lors du chargement de l'assignation du locataire: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement de l'assignation du locataire: {str(e)}")

@app.get("/api/projects")
async def get_projects():
    """Liste des projets de construction"""
    return [
        {"id": 1, "name": "Nouveau Complexe D", "status": "planning", "progress": 10},
        {"id": 2, "name": "Rénovation Immeuble E", "status": "in_progress", "progress": 65},
        {"id": 3, "name": "Extension Immeuble F", "status": "completed", "progress": 100}
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 