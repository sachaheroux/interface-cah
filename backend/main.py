from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import uvicorn

app = FastAPI(
    title="Interface CAH API",
    description="API pour la gestion de construction - Interface CAH",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://*.vercel.app"],  # Frontend local et Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Données du tableau de bord"""
    return {
        "total_buildings": 20,
        "total_tenants": 150,
        "pending_maintenance": 5,
        "monthly_revenue": 85000,
        "alerts": [
            {"type": "maintenance", "message": "Entretien programmé - Immeuble A"},
            {"type": "payment", "message": "3 loyers en retard"}
        ]
    }

@app.get("/api/buildings")
async def get_buildings():
    """Liste des immeubles"""
    return [
        {
            "id": 1, 
            "name": "Immeuble Maple", 
            "address": {
                "street": "123 Rue Maple",
                "city": "Montréal",
                "province": "QC",
                "postalCode": "H1A 1A1",
                "country": "Canada"
            },
            "type": "residential",
            "status": "active",
            "units": 12,
            "floors": 3,
            "yearBuilt": 2018,
            "totalArea": 8500,
            "characteristics": {
                "parking": 15,
                "elevator": True,
                "balconies": 8,
                "storage": True,
                "laundry": True,
                "airConditioning": False,
                "heating": "electric",
                "internet": True,
                "security": True
            },
            "financials": {
                "purchasePrice": 850000,
                "currentValue": 950000,
                "monthlyRevenue": 8500,
                "monthlyExpenses": 2200,
                "taxes": 12000,
                "insurance": 3500
            },
            "contacts": {
                "manager": "Jean Dupont - 514-555-0123",
                "contractor": "Construction CAH - 514-555-0456",
                "insurance": "Assurance Desjardins - 1-800-555-0789"
            },
            "notes": "Immeuble récent en excellent état. Proche du métro."
        },
        {
            "id": 2, 
            "name": "Complexe Oak", 
            "address": {
                "street": "456 Avenue Oak",
                "city": "Laval",
                "province": "QC", 
                "postalCode": "H7T 2B2",
                "country": "Canada"
            },
            "type": "residential",
            "status": "active",
            "units": 8,
            "floors": 2,
            "yearBuilt": 2015,
            "totalArea": 6200,
            "characteristics": {
                "parking": 10,
                "elevator": False,
                "balconies": 6,
                "storage": True,
                "laundry": True,
                "airConditioning": True,
                "heating": "gas",
                "internet": False,
                "security": False
            },
            "financials": {
                "purchasePrice": 620000,
                "currentValue": 720000,
                "monthlyRevenue": 6400,
                "monthlyExpenses": 1800,
                "taxes": 8500,
                "insurance": 2800
            },
            "contacts": {
                "manager": "Marie Martin - 450-555-0234",
                "contractor": "Réno Plus - 450-555-0567",
                "insurance": "Intact Assurance - 1-800-555-0890"
            },
            "notes": "Bon potentiel d'amélioration. Rénovations prévues."
        },
        {
            "id": 3, 
            "name": "Tour Pine", 
            "address": {
                "street": "789 Boulevard Pine",
                "city": "Longueuil",
                "province": "QC",
                "postalCode": "J4K 3C3", 
                "country": "Canada"
            },
            "type": "residential",
            "status": "construction",
            "units": 15,
            "floors": 4,
            "yearBuilt": 2024,
            "totalArea": 12000,
            "characteristics": {
                "parking": 20,
                "elevator": True,
                "balconies": 12,
                "storage": True,
                "laundry": True,
                "airConditioning": True,
                "heating": "heat_pump",
                "internet": True,
                "security": True
            },
            "financials": {
                "purchasePrice": 0,
                "currentValue": 1200000,
                "monthlyRevenue": 0,
                "monthlyExpenses": 0,
                "taxes": 0,
                "insurance": 0
            },
            "contacts": {
                "manager": "",
                "contractor": "Construction CAH - 514-555-0456",
                "insurance": ""
            },
            "notes": "Nouvelle construction. Livraison prévue été 2024."
        }
    ]

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