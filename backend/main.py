from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
from datetime import datetime
import json
import os

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

# Système de persistance avec fichier JSON
# Utilisation d'un disque persistant monté sur /var/data
DATA_DIR = os.environ.get("DATA_DIR", "/var/data")
BUILDINGS_DATA_FILE = os.path.join(DATA_DIR, "buildings_data.json")

# Créer le répertoire de données s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# DEBUGGING - Afficher les informations de persistance
print("=" * 60)
print("🔧 DIAGNOSTIC DISQUE PERSISTANT")
print("=" * 60)
print(f"📂 DATA_DIR (env): {os.environ.get('DATA_DIR', 'NON DÉFINIE')}")
print(f"📂 DATA_DIR (utilisé): {DATA_DIR}")
print(f"📄 Fichier de données: {BUILDINGS_DATA_FILE}")
print(f"📁 Répertoire existe: {os.path.exists(DATA_DIR)}")
print(f"📝 Fichier existe: {os.path.exists(BUILDINGS_DATA_FILE)}")
print(f"🔒 Permissions lecture: {os.access(DATA_DIR, os.R_OK)}")
print(f"🔒 Permissions écriture: {os.access(DATA_DIR, os.W_OK)}")
print(f"💾 Répertoire de travail: {os.getcwd()}")
print(f"🗂️  Contenu DATA_DIR: {os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else 'N/A'}")
print("=" * 60)

def load_buildings_data():
    """Charger les données depuis le fichier JSON"""
    try:
        if os.path.exists(BUILDINGS_DATA_FILE):
            with open(BUILDINGS_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Données chargées: {len(data.get('buildings', []))} immeubles")
                return data
    except Exception as e:
        print(f"Erreur chargement données depuis fichier: {e}")
    
    # Retourner structure vide si pas de fichier ou erreur
    return {"buildings": [], "next_id": 1}

def save_buildings_data(data):
    """Sauvegarder les données dans le fichier JSON"""
    try:
        with open(BUILDINGS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Données sauvegardées: {len(data.get('buildings', []))} immeubles")
        return True
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")
        return False

# Cache en mémoire pour cette session
_memory_cache = None

def get_buildings_cache():
    """Obtenir les données depuis le cache mémoire"""
    global _memory_cache
    if _memory_cache is None:
        _memory_cache = load_buildings_data()
    return _memory_cache

def update_buildings_cache(data):
    """Mettre à jour le cache mémoire"""
    global _memory_cache
    _memory_cache = data
    save_buildings_data(data)

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

@app.get("/api/tenants")
async def get_tenants():
    """Liste des locataires"""
    return [
        {"id": 1, "name": "Jean Dupont", "building": "Immeuble A", "unit": "A-101", "status": "active"},
        {"id": 2, "name": "Marie Martin", "building": "Immeuble A", "unit": "A-102", "status": "active"},
        {"id": 3, "name": "Pierre Durand", "building": "Immeuble B", "unit": "B-201", "status": "pending"}
    ]

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