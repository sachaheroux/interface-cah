from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
import json
import os
from datetime import datetime

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

# Système de stockage JSON
DATA_FILE = "buildings_data.json"

def load_buildings_data():
    """Charger les données des immeubles depuis le fichier JSON"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"buildings": [], "next_id": 1}
    return {"buildings": [], "next_id": 1}

def save_buildings_data(data):
    """Sauvegarder les données des immeubles dans le fichier JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
        return False

def get_default_buildings():
    """Retourner une liste vide - plus d'immeubles par défaut"""
    return []

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
        # Charger les données des immeubles
        data = load_buildings_data()
        buildings = data.get("buildings", [])
        
        # Calculer les statistiques réelles
        total_buildings = len(buildings)
        total_units = sum(building.get("units", 0) for building in buildings)
        total_portfolio_value = sum(building.get("financials", {}).get("currentValue", 0) for building in buildings)
        
        # Calculer le revenu mensuel estimé (estimation basée sur la valeur)
        # Estimation : 0.5% de la valeur du portfolio par mois
        monthly_revenue = total_portfolio_value * 0.005
        
        return {
            "totalBuildings": total_buildings,
            "totalUnits": total_units,
            "portfolioValue": total_portfolio_value,
            "monthlyRevenue": monthly_revenue,
            "recentActivity": [
                {
                    "type": "info",
                    "message": f"Portfolio actuel : {total_buildings} immeubles",
                    "timestamp": "2025-06-22T23:00:00Z"
                },
                {
                    "type": "success", 
                    "message": f"Total unités : {total_units}",
                    "timestamp": "2025-06-22T22:30:00Z"
                },
                {
                    "type": "info",
                    "message": f"Valeur portfolio : {total_portfolio_value:,.0f} $",
                    "timestamp": "2025-06-22T22:00:00Z"
                }
            ]
        }
    except Exception as e:
        return {
            "totalBuildings": 0,
            "totalUnits": 0, 
            "portfolioValue": 0,
            "monthlyRevenue": 0,
            "recentActivity": [
                {
                    "type": "info",
                    "message": "Aucun immeuble dans le portfolio",
                    "timestamp": "2025-06-22T23:00:00Z"
                }
            ]
        }

# Routes CRUD pour les immeubles avec persistance
@app.get("/api/buildings")
async def get_buildings():
    """Récupérer tous les immeubles (défaut + sauvegardés)"""
    try:
        # Charger les données sauvegardées
        data = load_buildings_data()
        
        # Combiner avec les immeubles par défaut
        default_buildings = get_default_buildings()
        all_buildings = default_buildings + data.get("buildings", [])
        
        return all_buildings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des immeubles: {str(e)}")

@app.get("/api/buildings/{building_id}")
async def get_building(building_id: int):
    """Récupérer un immeuble spécifique par ID"""
    try:
        # Vérifier d'abord dans les immeubles par défaut
        default_buildings = get_default_buildings()
        for building in default_buildings:
            if building["id"] == building_id:
                return building
        
        # Chercher dans les données sauvegardées
        data = load_buildings_data()
        for building in data.get("buildings", []):
            if building["id"] == building_id:
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
        # Charger les données existantes
        data = load_buildings_data()
        
        # Créer le nouvel immeuble avec un ID unique
        new_building = building_data.dict()
        new_building["id"] = data["next_id"]
        new_building["createdAt"] = datetime.now().isoformat() + "Z"
        new_building["updatedAt"] = datetime.now().isoformat() + "Z"
        
        # Ajouter aux données
        data["buildings"].append(new_building)
        data["next_id"] += 1
        
        # Sauvegarder
        if not save_buildings_data(data):
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde")
        
        return new_building
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'immeuble: {str(e)}")

@app.put("/api/buildings/{building_id}")
async def update_building(building_id: int, building_data: BuildingUpdate):
    """Mettre à jour un immeuble existant"""
    try:
        # Vérifier si c'est un immeuble par défaut (non modifiable)
        default_buildings = get_default_buildings()
        for building in default_buildings:
            if building["id"] == building_id:
                raise HTTPException(status_code=403, detail="Les immeubles par défaut ne peuvent pas être modifiés")
        
        # Charger les données sauvegardées
        data = load_buildings_data()
        
        # Trouver et mettre à jour l'immeuble
        building_found = False
        for i, building in enumerate(data["buildings"]):
            if building["id"] == building_id:
                # Mettre à jour seulement les champs fournis
                update_data = building_data.dict(exclude_unset=True)
                data["buildings"][i].update(update_data)
                data["buildings"][i]["updatedAt"] = datetime.now().isoformat() + "Z"
                building_found = True
                
                # Sauvegarder
                if not save_buildings_data(data):
                    raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde")
                
                return data["buildings"][i]
        
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
        # Charger les données
        data = load_buildings_data()
        buildings = data.get("buildings", [])
        
        # Trouver l'immeuble à supprimer
        building_to_delete = None
        for building in buildings:
            if building["id"] == building_id:
                building_to_delete = building
                break
        
        if not building_to_delete:
            raise HTTPException(status_code=404, detail="Immeuble non trouvé")
        
        # Supprimer l'immeuble
        data["buildings"] = [b for b in buildings if b["id"] != building_id]
        
        # Sauvegarder
        if not save_buildings_data(data):
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde")
        
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