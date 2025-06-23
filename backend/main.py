from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
from datetime import datetime
from sqlalchemy.orm import Session

# Import des modules de base de données
from database import get_db, create_tables, init_default_buildings, BuildingDB

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

# Initialisation de la base de données au démarrage
@app.on_event("startup")
async def startup_event():
    create_tables()
    init_default_buildings()

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
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Retourner les données du tableau de bord calculées à partir des vrais immeubles"""
    try:
        # Récupérer tous les immeubles de la base de données
        buildings = db.query(BuildingDB).all()
        
        # Calculer les statistiques réelles
        total_buildings = len(buildings)
        total_units = sum(building.units for building in buildings)
        total_portfolio_value = sum(
            building.financials.get("currentValue", 0) if building.financials else 0 
            for building in buildings
        )
        
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
async def get_buildings(db: Session = Depends(get_db)):
    """Récupérer tous les immeubles"""
    try:
        buildings = db.query(BuildingDB).all()
        result = []
        for building in buildings:
            result.append({
                "id": building.id,
                "name": building.name,
                "address": building.address,
                "type": building.type,
                "units": building.units,
                "floors": building.floors,
                "yearBuilt": building.year_built,
                "totalArea": building.total_area,
                "characteristics": building.characteristics,
                "financials": building.financials,
                "contacts": building.contacts,
                "notes": building.notes,
                "createdAt": building.created_at.isoformat() + "Z" if building.created_at else None,
                "updatedAt": building.updated_at.isoformat() + "Z" if building.updated_at else None
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des immeubles: {str(e)}")

@app.get("/api/buildings/{building_id}")
async def get_building(building_id: int, db: Session = Depends(get_db)):
    """Récupérer un immeuble spécifique par ID"""
    try:
        building = db.query(BuildingDB).filter(BuildingDB.id == building_id).first()
        if not building:
            raise HTTPException(status_code=404, detail="Immeuble non trouvé")
        
        return {
            "id": building.id,
            "name": building.name,
            "address": building.address,
            "type": building.type,
            "units": building.units,
            "floors": building.floors,
            "yearBuilt": building.year_built,
            "totalArea": building.total_area,
            "characteristics": building.characteristics,
            "financials": building.financials,
            "contacts": building.contacts,
            "notes": building.notes,
            "createdAt": building.created_at.isoformat() + "Z" if building.created_at else None,
            "updatedAt": building.updated_at.isoformat() + "Z" if building.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'immeuble: {str(e)}")

@app.post("/api/buildings")
async def create_building(building_data: BuildingCreate, db: Session = Depends(get_db)):
    """Créer un nouvel immeuble"""
    try:
        # Créer le nouvel immeuble
        new_building = BuildingDB(
            name=building_data.name,
            address=building_data.address.dict(),
            type=building_data.type,
            units=building_data.units,
            floors=building_data.floors,
            year_built=building_data.yearBuilt,
            total_area=building_data.totalArea,
            characteristics=building_data.characteristics.dict() if building_data.characteristics else None,
            financials=building_data.financials.dict() if building_data.financials else None,
            contacts=building_data.contacts.dict() if building_data.contacts else None,
            notes=building_data.notes
        )
        
        db.add(new_building)
        db.commit()
        db.refresh(new_building)
        
        return {
            "id": new_building.id,
            "name": new_building.name,
            "address": new_building.address,
            "type": new_building.type,
            "units": new_building.units,
            "floors": new_building.floors,
            "yearBuilt": new_building.year_built,
            "totalArea": new_building.total_area,
            "characteristics": new_building.characteristics,
            "financials": new_building.financials,
            "contacts": new_building.contacts,
            "notes": new_building.notes,
            "createdAt": new_building.created_at.isoformat() + "Z",
            "updatedAt": new_building.updated_at.isoformat() + "Z"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'immeuble: {str(e)}")

@app.put("/api/buildings/{building_id}")
async def update_building(building_id: int, building_data: BuildingUpdate, db: Session = Depends(get_db)):
    """Mettre à jour un immeuble existant"""
    try:
        building = db.query(BuildingDB).filter(BuildingDB.id == building_id).first()
        if not building:
            raise HTTPException(status_code=404, detail="Immeuble non trouvé")
        
        # Mettre à jour seulement les champs fournis
        update_data = building_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "address" and value:
                setattr(building, field, value.dict())
            elif field in ["characteristics", "financials", "contacts"] and value:
                setattr(building, field, value.dict())
            elif field == "yearBuilt":
                setattr(building, "year_built", value)
            elif field == "totalArea":
                setattr(building, "total_area", value)
            else:
                setattr(building, field, value)
        
        building.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(building)
        
        return {
            "id": building.id,
            "name": building.name,
            "address": building.address,
            "type": building.type,
            "units": building.units,
            "floors": building.floors,
            "yearBuilt": building.year_built,
            "totalArea": building.total_area,
            "characteristics": building.characteristics,
            "financials": building.financials,
            "contacts": building.contacts,
            "notes": building.notes,
            "createdAt": building.created_at.isoformat() + "Z",
            "updatedAt": building.updated_at.isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de l'immeuble: {str(e)}")

@app.delete("/api/buildings/{building_id}")
async def delete_building(building_id: int, db: Session = Depends(get_db)):
    """Supprimer un immeuble"""
    try:
        building = db.query(BuildingDB).filter(BuildingDB.id == building_id).first()
        if not building:
            raise HTTPException(status_code=404, detail="Immeuble non trouvé")
        
        db.delete(building)
        db.commit()
        
        return {"message": "Immeuble supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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