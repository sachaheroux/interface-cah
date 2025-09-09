from fastapi import FastAPI, HTTPException, UploadFile, File
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

# Constantes pour les factures
INVOICE_CATEGORIES = {
    "municipal_taxes": "Taxes municipales",
    "school_taxes": "Taxes scolaire", 
    "insurance": "Assurance",
    "snow_removal": "Déneigement",
    "lawn_care": "Gazon",
    "management": "Gestion",
    "renovations": "Rénovations",
    "repairs": "Réparations",
    "wifi": "WiFi",
    "electricity": "Électricité",
    "other": "Autres"
}

PAYMENT_TYPES = {
    "bank_transfer": "Virement bancaire",
    "check": "Chèque",
    "cash": "Espèces"
}

INVOICE_TYPES = {
    "rental_building": "Immeuble en location",
    "construction_project": "Projet de construction"
}

# ========================================
# ENDPOINT POUR LES CONSTANTES (défini tôt pour éviter les erreurs)
# ========================================

@app.get("/api/invoices/constants")
async def get_invoice_constants():
    """Récupérer les constantes pour les factures (catégories, types de paiement, etc.)"""
    try:
        print("🔧 Récupération des constantes de factures...")
        print(f"📊 Catégories: {len(INVOICE_CATEGORIES)}")
        print(f"💳 Types de paiement: {len(PAYMENT_TYPES)}")
        print(f"📋 Types de facture: {len(INVOICE_TYPES)}")
        
        # Retourner directement les constantes sans wrapper
        return {
            "categories": INVOICE_CATEGORIES,
            "paymentTypes": PAYMENT_TYPES,
            "invoiceTypes": INVOICE_TYPES
        }
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des constantes: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des constantes: {str(e)}")

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
    unitData: Optional[dict] = None  # Données personnalisées des unités
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
    unitData: Optional[dict] = None  # Données personnalisées des unités

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
    unitData: Optional[dict] = None  # Données personnalisées des unités

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

# Modèles pour les données de bail (définis avant Tenant)
class LeaseInfo(BaseModel):
    startDate: str = ""
    endDate: str = ""
    monthlyRent: float = 0
    paymentMethod: str = "Virement bancaire"
    leasePdf: str = ""  # URL ou nom du fichier PDF
    amenities: Optional[dict] = None  # Conditions du bail (wifi, heating, etc.)

class LeaseRenewal(BaseModel):
    isActive: bool = False
    startDate: str = ""
    endDate: str = ""
    monthlyRent: float = 0
    renewalPdf: str = ""  # URL ou nom du fichier PDF
    amenities: Optional[dict] = None  # Conditions du renouvellement

class Tenant(BaseModel):
    id: Optional[int] = None
    name: str
    email: str = ""
    phone: str = ""
    status: str = "active"  # active, pending, inactive, former
    personalAddress: Optional[PersonalAddress] = None
    emergencyContact: Optional[EmergencyContact] = None
    financial: Optional[TenantFinancial] = None
    lease: Optional[LeaseInfo] = None
    leaseRenewals: Optional[list] = None  # Liste des renouvellements au lieu d'un seul
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
    lease: Optional[LeaseInfo] = None
    leaseRenewals: Optional[list] = None  # Liste des renouvellements
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
    lease: Optional[LeaseInfo] = None
    leaseRenewals: Optional[list] = None  # Liste des renouvellements
    building: Optional[str] = None
    unit: Optional[str] = None
    notes: Optional[str] = None

# Modèles pour les factures
class Invoice(BaseModel):
    id: Optional[int] = None
    invoiceNumber: str
    category: str  # municipal_taxes, school_taxes, insurance, etc.
    source: str = ""  # D'où vient la facture (texte libre)
    date: str  # Format YYYY-MM-DD
    amount: float
    paymentType: str  # bank_transfer, check, cash
    buildingId: Optional[int] = None
    unitId: Optional[str] = None  # null si facture pour tout l'immeuble
    pdfFilename: str = ""
    notes: str = ""
    type: str = "rental_building"  # rental_building ou construction_project
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class InvoiceCreate(BaseModel):
    invoiceNumber: str
    category: str
    source: str = ""
    date: str
    amount: float
    paymentType: str
    buildingId: Optional[int] = None
    unitId: Optional[str] = None
    pdfFilename: str = ""
    notes: str = ""
    type: str = "rental_building"

class InvoiceUpdate(BaseModel):
    invoiceNumber: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[float] = None
    paymentType: Optional[str] = None
    buildingId: Optional[int] = None
    unitId: Optional[str] = None
    pdfFilename: Optional[str] = None
    notes: Optional[str] = None
    type: Optional[str] = None

# Système de persistance avec fichier JSON
# Utilisation du répertoire recommandé par Render : /opt/render/project/src/data
# En local, utiliser un répertoire relatif pour éviter les problèmes de permissions
if platform.system() == "Windows" or os.environ.get("ENVIRONMENT") == "development":
    # En local (Windows) ou développement, utiliser un répertoire relatif
    DATA_DIR = os.environ.get("DATA_DIR", "./data")
else:
    # Sur Render ou production Linux, utiliser le répertoire recommandé
    DATA_DIR = os.environ.get("DATA_DIR", "/opt/render/project/src/data")

# Chemins des fichiers de données
BUILDINGS_DATA_FILE = os.path.join(DATA_DIR, "buildings_data.json")
TENANTS_DATA_FILE = os.path.join(DATA_DIR, "tenants_data.json")
ASSIGNMENTS_DATA_FILE = os.path.join(DATA_DIR, "assignments_data.json")
BUILDING_REPORTS_DATA_FILE = os.path.join(DATA_DIR, "building_reports_data.json")
UNIT_REPORTS_DATA_FILE = os.path.join(DATA_DIR, "unit_reports_data.json")
INVOICES_DATA_FILE = os.path.join(DATA_DIR, "invoices_data.json")

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

if os.path.exists(ASSIGNMENTS_DATA_FILE):
    print(f"📁 Fichier assignments trouvé: {ASSIGNMENTS_DATA_FILE}")
else:
    print(f"📁 Création du fichier assignments: {ASSIGNMENTS_DATA_FILE}")

if os.path.exists(BUILDING_REPORTS_DATA_FILE):
    print(f"📁 Fichier rapports immeubles trouvé: {BUILDING_REPORTS_DATA_FILE}")
else:
    print(f"📁 Création du fichier rapports immeubles: {BUILDING_REPORTS_DATA_FILE}")

if os.path.exists(UNIT_REPORTS_DATA_FILE):
    print(f"📁 Fichier rapports unités trouvé: {UNIT_REPORTS_DATA_FILE}")
else:
    print(f"📁 Création du fichier rapports unités: {UNIT_REPORTS_DATA_FILE}")

print("=" * 60)

# Cache pour les données
buildings_cache = None
tenants_cache = None
assignments_cache = None
building_reports_cache = None
unit_reports_cache = None
invoices_cache = None

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

def get_building_reports_cache():
    """Obtenir les données des rapports d'immeubles avec cache"""
    global building_reports_cache
    if building_reports_cache is None:
        building_reports_cache = load_building_reports_data()
    return building_reports_cache

def get_unit_reports_cache():
    """Obtenir les données des rapports d'unités avec cache"""
    global unit_reports_cache
    if unit_reports_cache is None:
        unit_reports_cache = load_unit_reports_data()
    return unit_reports_cache

def get_invoices_cache():
    """Obtenir les données des factures avec cache"""
    global invoices_cache
    if invoices_cache is None:
        invoices_cache = load_invoices_data()
    return invoices_cache

def invalidate_caches():
    """Invalider tous les caches"""
    global buildings_cache, tenants_cache, assignments_cache, building_reports_cache, unit_reports_cache, invoices_cache
    buildings_cache = None
    tenants_cache = None
    assignments_cache = None
    building_reports_cache = None
    unit_reports_cache = None
    invoices_cache = None

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

def load_building_reports_data():
    """Charger les données des rapports d'immeubles depuis le fichier JSON"""
    try:
        if os.path.exists(BUILDING_REPORTS_DATA_FILE):
            with open(BUILDING_REPORTS_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Données rapports immeubles chargées: {len(data.get('reports', []))} rapports")
                return data
    except Exception as e:
        print(f"Erreur chargement données rapports immeubles depuis fichier: {e}")
    
    # Retourner structure vide si pas de fichier ou erreur
    return {"reports": [], "next_id": 1}

def save_building_reports_data(data):
    """Sauvegarder les données des rapports d'immeubles dans le fichier JSON"""
    try:
        with open(BUILDING_REPORTS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Données rapports immeubles sauvegardées: {len(data.get('reports', []))} rapports")
        return True
    except Exception as e:
        print(f"Erreur sauvegarde rapports immeubles: {e}")
        return False

def load_unit_reports_data():
    """Charger les données des rapports d'unités depuis le fichier JSON"""
    try:
        if os.path.exists(UNIT_REPORTS_DATA_FILE):
            with open(UNIT_REPORTS_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Données rapports unités chargées: {len(data.get('reports', []))} rapports")
                return data
    except Exception as e:
        print(f"Erreur chargement données rapports unités depuis fichier: {e}")
    
    # Retourner structure vide si pas de fichier ou erreur
    return {"reports": [], "next_id": 1}

def save_unit_reports_data(data):
    """Sauvegarder les données des rapports d'unités dans le fichier JSON"""
    try:
        with open(UNIT_REPORTS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Données rapports unités sauvegardées: {len(data.get('reports', []))} rapports")
        return True
    except Exception as e:
        print(f"Erreur sauvegarde rapports unités: {e}")
        return False

def load_invoices_data():
    """Charger les données des factures depuis le fichier JSON"""
    try:
        if os.path.exists(INVOICES_DATA_FILE):
            with open(INVOICES_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Données factures chargées: {len(data.get('invoices', []))} factures")
                return data
    except Exception as e:
        print(f"Erreur chargement données factures depuis fichier: {e}")
    
    # Retourner structure vide si pas de fichier ou erreur
    return {"invoices": [], "next_id": 1}

def save_invoices_data(data):
    """Sauvegarder les données des factures dans le fichier JSON"""
    try:
        with open(INVOICES_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Données factures sauvegardées: {len(data.get('invoices', []))} factures")
        return True
    except Exception as e:
        print(f"Erreur sauvegarde factures: {e}")
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

def update_building_reports_cache(data):
    """Mettre à jour le cache mémoire des rapports d'immeubles"""
    global building_reports_cache
    building_reports_cache = data
    save_building_reports_data(data)

def update_unit_reports_cache(data):
    """Mettre à jour le cache mémoire des rapports d'unités"""
    global unit_reports_cache
    unit_reports_cache = data
    save_unit_reports_data(data)

def update_invoices_cache(data):
    """Mettre à jour le cache mémoire des factures"""
    global invoices_cache
    invoices_cache = data
    save_invoices_data(data)

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
        tenant_id = assignment_data.get("tenantId")
        
        # Validation : Vérifier que le locataire existe
        tenants_data = get_tenants_cache()
        tenant_exists = any(t.get("id") == tenant_id for t in tenants_data.get("tenants", []))
        
        if not tenant_exists:
            print(f"❌ Assignation rejetée: Locataire {tenant_id} n'existe pas")
            raise HTTPException(
                status_code=400, 
                detail=f"Le locataire avec l'ID {tenant_id} n'existe pas dans la base de données"
            )
        
        # Créer la nouvelle assignation avec un ID unique
        new_assignment = {
            "id": data["next_id"],
            "unitId": assignment_data.get("unitId"),
            "tenantId": tenant_id,
            "tenantData": assignment_data.get("tenantData", {}),
            "assignedAt": datetime.now().isoformat() + "Z",
            "createdAt": datetime.now().isoformat() + "Z",
            "updatedAt": datetime.now().isoformat() + "Z"
        }
        
        # Supprimer l'ancienne assignation pour ce locataire s'il y en a une
        data["assignments"] = [a for a in data["assignments"] if a.get("tenantId") != tenant_id]
        
        # Ajouter la nouvelle assignation
        data["assignments"].append(new_assignment)
        data["next_id"] += 1
        
        # Mettre à jour le cache
        update_assignments_cache(data)
        
        print(f"✅ Assignation créée: Locataire {tenant_id} → Unité {assignment_data.get('unitId')}")
        return {"data": new_assignment}
    except HTTPException:
        raise
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

@app.delete("/api/assignments/tenant/{tenant_id}/unit/{unit_id}")
async def remove_specific_assignment(tenant_id: int, unit_id: str):
    """Retirer un locataire d'une unité spécifique (ne supprime que cette assignation)"""
    try:
        data = get_assignments_cache()
        
        # Trouver et supprimer seulement l'assignation spécifique
        original_count = len(data["assignments"])
        data["assignments"] = [a for a in data["assignments"] 
                              if not (a.get("tenantId") == tenant_id and a.get("unitId") == unit_id)]
        removed_count = original_count - len(data["assignments"])
        
        if removed_count == 0:
            raise HTTPException(status_code=404, detail="Assignation non trouvée pour ce locataire et cette unité")
        
        # Mettre à jour le cache
        update_assignments_cache(data)
        
        print(f"Assignation spécifique supprimée: Locataire {tenant_id} retiré de l'unité {unit_id}")
        return {"message": f"Locataire {tenant_id} retiré de l'unité {unit_id} avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression de l'assignation spécifique: {e}")
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

# ========================================
# ROUTES POUR LES RAPPORTS D'IMMEUBLES
# ========================================

@app.get("/api/building-reports")
async def get_building_reports():
    """Récupérer tous les rapports d'immeubles"""
    try:
        data = get_building_reports_cache()
        reports = data.get("reports", [])
        return {"data": reports}
    except Exception as e:
        print(f"Erreur lors du chargement des rapports d'immeubles: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des rapports d'immeubles: {str(e)}")

@app.get("/api/building-reports/{building_id}")
async def get_building_report(building_id: int):
    """Récupérer le rapport d'un immeuble spécifique"""
    try:
        data = get_building_reports_cache()
        reports = data.get("reports", [])
        building_report = next((r for r in reports if r.get("buildingId") == building_id), None)
        return {"data": building_report}
    except Exception as e:
        print(f"Erreur lors du chargement du rapport d'immeuble: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement du rapport d'immeuble: {str(e)}")

@app.post("/api/building-reports")
async def create_building_report(report_data: dict):
    """Créer ou mettre à jour un rapport d'immeuble"""
    try:
        data = get_building_reports_cache()
        building_id = report_data.get("buildingId")
        year = report_data.get("year")
        
        # Vérifier si un rapport existe déjà pour cet immeuble et cette année
        reports = data.get("reports", [])
        existing_report = next((r for r in reports if r.get("buildingId") == building_id and r.get("year") == year), None)
        
        if existing_report:
            # Mettre à jour le rapport existant
            existing_report.update(report_data)
            existing_report["updatedAt"] = datetime.now().isoformat() + "Z"
            updated_report = existing_report
        else:
            # Créer un nouveau rapport
            new_report = {
                "id": data["next_id"],
                "buildingId": building_id,
                "year": year,
                "createdAt": datetime.now().isoformat() + "Z",
                "updatedAt": datetime.now().isoformat() + "Z",
                **report_data
            }
            data["reports"].append(new_report)
            data["next_id"] += 1
            updated_report = new_report
        
        update_building_reports_cache(data)
        print(f"Rapport immeuble sauvegardé: {building_id} - {year}")
        return {"data": updated_report}
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du rapport d'immeuble: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde du rapport d'immeuble: {str(e)}")

@app.delete("/api/building-reports/{report_id}")
async def delete_building_report(report_id: int):
    """Supprimer un rapport d'immeuble"""
    try:
        data = get_building_reports_cache()
        original_count = len(data["reports"])
        data["reports"] = [r for r in data["reports"] if r.get("id") != report_id]
        
        if len(data["reports"]) == original_count:
            raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
        update_building_reports_cache(data)
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

@app.get("/api/unit-reports")
async def get_unit_reports():
    """Récupérer tous les rapports d'unités"""
    try:
        data = get_unit_reports_cache()
        reports = data.get("reports", [])
        return {"data": reports}
    except Exception as e:
        print(f"Erreur lors du chargement des rapports d'unités: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des rapports d'unités: {str(e)}")

@app.get("/api/unit-reports/{unit_id}")
async def get_unit_report(unit_id: str):
    """Récupérer tous les rapports d'une unité spécifique"""
    try:
        data = get_unit_reports_cache()
        reports = data.get("reports", [])
        unit_reports = [r for r in reports if r.get("unitId") == unit_id]
        return {"data": unit_reports}
    except Exception as e:
        print(f"Erreur lors du chargement des rapports d'unité: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des rapports d'unité: {str(e)}")

@app.post("/api/unit-reports")
async def create_unit_report(report_data: dict):
    """Créer un nouveau rapport d'unité mensuel"""
    try:
        data = get_unit_reports_cache()
        
        new_report = {
            "id": data["next_id"],
            "unitId": report_data.get("unitId"),
            "year": report_data.get("year"),
            "month": report_data.get("month"),
            "tenantName": report_data.get("tenantName"),
            "paymentMethod": report_data.get("paymentMethod"),
            "isHeatedLit": report_data.get("isHeatedLit", False),
            "isFurnished": report_data.get("isFurnished", False),
            "wifiIncluded": report_data.get("wifiIncluded", False),
            "rentAmount": report_data.get("rentAmount", 0),
            "startDate": report_data.get("startDate"),
            "endDate": report_data.get("endDate"),
            "createdAt": datetime.now().isoformat() + "Z",
            "updatedAt": datetime.now().isoformat() + "Z"
        }
        
        data["reports"].append(new_report)
        data["next_id"] += 1
        
        update_unit_reports_cache(data)
        print(f"Rapport unité créé: {report_data.get('unitId')} - {report_data.get('year')}/{report_data.get('month')}")
        return {"data": new_report}
    except Exception as e:
        print(f"Erreur lors de la création du rapport d'unité: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du rapport d'unité: {str(e)}")

@app.delete("/api/unit-reports/{report_id}")
async def delete_unit_report(report_id: int):
    """Supprimer un rapport d'unité"""
    try:
        reports = load_unit_reports_data()
        reports = [r for r in reports if r.get('id') != report_id]
        save_unit_reports_data(reports)
        update_unit_reports_cache(reports)
        return {"message": "Rapport d'unité supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Uploader un document (PDF, image, etc.)"""
    try:
        # Créer le répertoire documents s'il n'existe pas
        documents_dir = os.path.join(DATA_DIR, "documents")
        os.makedirs(documents_dir, exist_ok=True)
        
        # Vérifier le type de fichier
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
        
        # Chemin complet du fichier
        file_path = os.path.join(documents_dir, file.filename)
        
        # Sauvegarder le fichier
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Document uploadé: {file.filename}")
        return {
            "message": "Document uploadé avec succès",
            "filename": file.filename,
            "size": os.path.getsize(file_path)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")

@app.get("/api/documents")
async def list_documents():
    """Lister tous les documents disponibles"""
    try:
        # Créer le répertoire documents s'il n'existe pas
        documents_dir = os.path.join(DATA_DIR, "documents")
        os.makedirs(documents_dir, exist_ok=True)
        
        # Lister les fichiers
        files = []
        if os.path.exists(documents_dir):
            for filename in os.listdir(documents_dir):
                if filename.lower().endswith('.pdf'):
                    file_path = os.path.join(documents_dir, filename)
                    files.append({
                        "filename": filename,
                        "size": os.path.getsize(file_path),
                        "uploaded_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                    })
        
        return {"documents": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des documents: {str(e)}")

@app.get("/api/documents/{filename}")
async def get_document(filename: str):
    """Servir un document (PDF, image, etc.)"""
    try:
        # Créer le répertoire documents s'il n'existe pas
        documents_dir = os.path.join(DATA_DIR, "documents")
        os.makedirs(documents_dir, exist_ok=True)
        
        # Chemin complet du fichier
        file_path = os.path.join(documents_dir, filename)
        
        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            # Lister les fichiers disponibles pour aider au diagnostic
            available_files = []
            if os.path.exists(documents_dir):
                available_files = [f for f in os.listdir(documents_dir) if f.lower().endswith('.pdf')]
            
            error_detail = {
                "error": "Document non trouvé",
                "requested_file": filename,
                "documents_dir": documents_dir,
                "available_files": available_files,
                "message": f"Le fichier '{filename}' n'existe pas. Fichiers disponibles: {available_files}"
            }
            
            raise HTTPException(
                status_code=404, 
                detail=error_detail
            )
        
        # Retourner le fichier
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du document: {str(e)}")

@app.get("/api/assignments/clean")
async def clean_invalid_assignments():
    """Nettoyer les assignations avec des tenantId invalides"""
    try:
        data = get_assignments_cache()
        tenants_data = get_tenants_cache()
        
        # Récupérer les IDs valides des locataires
        valid_tenant_ids = {t.get("id") for t in tenants_data.get("tenants", [])}
        
        # Analyser les assignations
        assignments = data.get("assignments", [])
        original_count = len(assignments)
        
        invalid_assignments = []
        valid_assignments = []
        
        for assignment in assignments:
            tenant_id = assignment.get("tenantId")
            
            # Vérifier si l'ID est valide
            if tenant_id in valid_tenant_ids:
                valid_assignments.append(assignment)
            else:
                invalid_assignments.append(assignment)
        
        # Sauvegarder les assignations valides seulement
        data["assignments"] = valid_assignments
        update_assignments_cache(data)
        
        return {
            "message": "Nettoyage terminé",
            "removed_count": len(invalid_assignments),
            "kept_count": len(valid_assignments),
            "total_original": original_count,
            "invalid_assignments": [
                {
                    "id": a.get("id"),
                    "tenantId": a.get("tenantId"),
                    "unitId": a.get("unitId")
                } for a in invalid_assignments
            ]
        }
    except Exception as e:
        print(f"Erreur lors du nettoyage des assignations: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du nettoyage: {str(e)}")

# ========================================
# ROUTES POUR LES FACTURES
# ========================================

@app.get("/api/invoices")
async def get_invoices():
    """Récupérer toutes les factures"""
    try:
        data = get_invoices_cache()
        invoices = data.get("invoices", [])
        return {"data": invoices}
    except Exception as e:
        print(f"Erreur lors du chargement des factures: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des factures: {str(e)}")

@app.get("/api/invoices/{invoice_id}")
async def get_invoice(invoice_id: int):
    """Récupérer une facture spécifique par ID"""
    try:
        data = get_invoices_cache()
        invoices = data.get("invoices", [])
        
        for invoice in invoices:
            if invoice.get("id") == invoice_id:
                return {"data": invoice}
        
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la récupération de la facture: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la facture: {str(e)}")

@app.post("/api/invoices")
async def create_invoice(invoice_data: InvoiceCreate):
    """Créer une nouvelle facture"""
    try:
        data = get_invoices_cache()
        
        # Vérifier l'unicité du numéro de facture
        existing_invoices = data.get("invoices", [])
        invoice_number = invoice_data.invoiceNumber
        
        if any(inv.get("invoiceNumber") == invoice_number for inv in existing_invoices):
            raise HTTPException(
                status_code=400, 
                detail=f"Une facture avec le numéro '{invoice_number}' existe déjà"
            )
        
        # Créer la nouvelle facture avec un ID unique
        new_invoice = invoice_data.dict()
        new_invoice["id"] = data["next_id"]
        new_invoice["createdAt"] = datetime.now().isoformat() + "Z"
        new_invoice["updatedAt"] = datetime.now().isoformat() + "Z"
        
        # Ajouter aux données
        data["invoices"].append(new_invoice)
        data["next_id"] += 1
        
        # Mettre à jour le cache
        update_invoices_cache(data)
        
        print(f"✅ Facture créée: {invoice_number} - {invoice_data.category}")
        return {"data": new_invoice}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la création de la facture: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la facture: {str(e)}")

@app.put("/api/invoices/{invoice_id}")
async def update_invoice(invoice_id: int, invoice_data: InvoiceUpdate):
    """Mettre à jour une facture existante"""
    try:
        data = get_invoices_cache()
        invoices = data.get("invoices", [])
        
        # Trouver et mettre à jour la facture
        invoice_found = False
        for i, invoice in enumerate(invoices):
            if invoice.get("id") == invoice_id:
                # Vérifier l'unicité du numéro de facture si modifié
                if invoice_data.invoiceNumber and invoice_data.invoiceNumber != invoice.get("invoiceNumber"):
                    existing_invoices = [inv for inv in invoices if inv.get("id") != invoice_id]
                    if any(inv.get("invoiceNumber") == invoice_data.invoiceNumber for inv in existing_invoices):
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Une facture avec le numéro '{invoice_data.invoiceNumber}' existe déjà"
                        )
                
                # Mettre à jour seulement les champs fournis
                update_data = invoice_data.dict(exclude_unset=True)
                invoices[i].update(update_data)
                invoices[i]["updatedAt"] = datetime.now().isoformat() + "Z"
                invoice_found = True
                
                # Mettre à jour le cache
                update_invoices_cache(data)
                
                print(f"✅ Facture mise à jour: {invoices[i].get('invoiceNumber')}")
                return {"data": invoices[i]}
        
        if not invoice_found:
            raise HTTPException(status_code=404, detail="Facture non trouvée")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la facture: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la facture: {str(e)}")

@app.delete("/api/invoices/{invoice_id}")
async def delete_invoice(invoice_id: int):
    """Supprimer une facture"""
    try:
        data = get_invoices_cache()
        invoices = data.get("invoices", [])
        
        # Trouver la facture à supprimer
        invoice_to_delete = None
        for invoice in invoices:
            if invoice.get("id") == invoice_id:
                invoice_to_delete = invoice
                break
        
        if not invoice_to_delete:
            raise HTTPException(status_code=404, detail="Facture non trouvée")
        
        # Supprimer la facture
        data["invoices"] = [inv for inv in invoices if inv.get("id") != invoice_id]
        
        # Mettre à jour le cache
        update_invoices_cache(data)
        
        print(f"✅ Facture supprimée: {invoice_to_delete.get('invoiceNumber')}")
        return {"message": "Facture supprimée avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression de la facture: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.get("/api/invoices/building/{building_id}")
async def get_building_invoices(building_id: int):
    """Récupérer toutes les factures d'un immeuble spécifique"""
    try:
        data = get_invoices_cache()
        invoices = data.get("invoices", [])
        
        # Filtrer les factures pour cet immeuble
        building_invoices = [inv for inv in invoices if inv.get("buildingId") == building_id]
        
        return {"data": building_invoices}
    except Exception as e:
        print(f"Erreur lors du chargement des factures d'immeuble: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des factures d'immeuble: {str(e)}")

@app.get("/api/invoices/building/{building_id}/category/{category}")
async def get_building_category_invoices(building_id: int, category: str):
    """Récupérer toutes les factures d'une catégorie spécifique pour un immeuble"""
    try:
        data = get_invoices_cache()
        invoices = data.get("invoices", [])
        
        # Filtrer les factures pour cet immeuble et cette catégorie
        category_invoices = [
            inv for inv in invoices 
            if inv.get("buildingId") == building_id and inv.get("category") == category
        ]
        
        return {"data": category_invoices}
    except Exception as e:
        print(f"Erreur lors du chargement des factures de catégorie: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des factures de catégorie: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 