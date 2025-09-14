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
import re

# Imports pour SQLite
from database import db_manager, init_database
from database_service import db_service
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
        
        # Migration automatique pour Render
        try:
            from migrate_render_database import migrate_render_database
            print("🔄 Exécution de la migration Render...")
            if migrate_render_database():
                print("✅ Migration Render terminée avec succès")
            else:
                print("⚠️  Migration Render échouée, mais l'application continue")
        except Exception as e:
            print(f"⚠️  Erreur lors de la migration Render: {e}")
            print("ℹ️  L'application continue sans migration")
    else:
        print("❌ Erreur lors de l'initialisation de la base de données")
        raise Exception("Impossible d'initialiser la base de données")

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
        
        # Utiliser le service SQLite
        constants = db_service.get_invoice_constants()
        
        print(f"📊 Catégories: {len(constants['categories'])}")
        print(f"💳 Types de paiement: {len(constants['paymentTypes'])}")
        print(f"📋 Types de facture: {len(constants['invoiceTypes'])}")
        
        return constants
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des constantes: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# Modèles Pydantic pour la validation des données
class Address(BaseModel):
    street: str
    city: str
    province: str
    postalCode: str
    country: str = "Canada"
    
    class Config:
        # Validation personnalisée
        validate_assignment = True

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

@app.post("/api/migrate/tenants")
async def migrate_tenants_table():
    """Migration de la table tenants - Ajouter les colonnes manquantes"""
    try:
        import sqlite3
        import os
        
        # Chemin de la base de données
        if os.environ.get("ENVIRONMENT") == "development" or os.name == 'nt':
            db_path = "./data/cah_database.db"
        else:
            db_path = "/opt/render/project/src/data/cah_database.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Colonnes à ajouter
        columns_to_add = [
            "address_street TEXT",
            "address_city TEXT", 
            "address_province TEXT",
            "address_postal_code TEXT",
            "address_country TEXT DEFAULT 'Canada'"
        ]
        
        # Vérifier quelles colonnes existent déjà
        cursor.execute("PRAGMA table_info(tenants)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        added_columns = []
        for col_def in columns_to_add:
            col_name = col_def.split()[0]
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE tenants ADD COLUMN {col_def}")
                    added_columns.append(col_name)
                    print(f"✅ Colonne ajoutée: {col_name}")
                except Exception as e:
                    print(f"❌ Erreur ajout colonne {col_name}: {e}")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Migration terminée. Colonnes ajoutées: {added_columns}",
            "added_columns": added_columns
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

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

# Routes CRUD pour les immeubles avec SQLite
def generate_units_from_address(building):
    """Générer automatiquement les unités basées sur l'adresse de l'immeuble"""
    try:
        address = building.get('address', {})
        if not address:
            return []
        
        street = address.get('street', '')
        if not street:
            return []
        
        # Parser l'adresse pour extraire les numéros d'unités
        # Format attendu: "56-58-60-62 rue Vachon" ou "56 rue Vachon"
        unit_numbers = []
        street_name = street
        
        # Chercher des numéros séparés par des tirets
        if '-' in street:
            # Extraire tous les numéros avant le premier espace
            street_part = street.split(' ')[0]
            numbers = street_part.split('-')
            for num in numbers:
                if num.strip().isdigit():
                    unit_numbers.append(num.strip())
            
            # Extraire le nom de la rue (tout après le premier espace)
            street_parts = street.split(' ', 1)
            if len(street_parts) > 1:
                street_name = street_parts[1]  # "rue Vachon"
        else:
            # Adresse simple, une seule unité
            unit_numbers = ['1']
        
        # Si pas de numéros trouvés, utiliser le nombre d'unités spécifié
        if not unit_numbers:
            units_count = building.get('units', 1)
            unit_numbers = [str(i) for i in range(1, units_count + 1)]
        
        # Créer les unités
        created_units = []
        for i, unit_num in enumerate(unit_numbers):
            unit_data = {
                "buildingId": building['id'],
                "unitNumber": unit_num,
                "unitAddress": f"{unit_num} {street_name}",
                "type": "4 1/2",  # Type par défaut pour les nouvelles unités
                "area": 0,
                "bedrooms": 1,
                "bathrooms": 1,
                "amenities": "{}",
                "notes": ""
            }
            
            try:
                created_unit = db_service.create_unit(unit_data)
                created_units.append(created_unit)
                print(f"   ✅ Unité {unit_num} créée (ID: {created_unit.get('id')})")
            except Exception as e:
                print(f"   ❌ Erreur création unité {unit_num}: {e}")
        
        return created_units
        
    except Exception as e:
        print(f"❌ Erreur génération unités: {e}")
        return []

@app.get("/api/buildings")
async def get_buildings():
    """Récupérer tous les immeubles"""
    try:
        buildings = db_service.get_buildings()
        return buildings
    except Exception as e:
        print(f"❌ Erreur lors du chargement des immeubles: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des immeubles: {str(e)}")

@app.get("/api/buildings/{building_id}")
async def get_building(building_id: int):
    """Récupérer un immeuble spécifique par ID"""
    try:
        building = db_service.get_building(building_id)
        if not building:
            raise HTTPException(status_code=404, detail="Immeuble non trouvé")
        return building
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'immeuble: {str(e)}")

@app.post("/api/buildings")
async def create_building(building_data: BuildingCreate):
    """Créer un nouvel immeuble"""
    try:
        # Convertir en dictionnaire pour le service
        building_dict = building_data.dict()
        
        # Créer l'immeuble via le service SQLite
        new_building = db_service.create_building(building_dict)
        
        # Générer automatiquement les unités basées sur l'adresse
        if new_building and new_building.get('id'):
            units_generated = generate_units_from_address(new_building)
            if units_generated:
                print(f"✅ {len(units_generated)} unités générées automatiquement pour l'immeuble {new_building['id']}")
        
        return new_building
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'immeuble: {str(e)}")

@app.put("/api/buildings/{building_id}")
async def update_building(building_id: int, building_data: BuildingUpdate):
    """Mettre à jour un immeuble existant"""
    try:
        # Convertir en dictionnaire pour le service
        update_dict = building_data.dict(exclude_unset=True)
        
        # Mettre à jour l'immeuble via le service SQLite
        updated_building = db_service.update_building(building_id, update_dict)
        
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
        success = db_service.delete_building(building_id)
        
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
        tenants = db_service.get_tenants()
        return {"data": tenants}
    except Exception as e:
        print(f"Erreur lors du chargement des locataires: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

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
        # Convertir en dictionnaire pour le service
        tenant_dict = tenant_data.dict()
        
        # Créer le locataire via le service SQLite
        new_tenant = db_service.create_tenant(tenant_dict)
        
        return {"data": new_tenant}
    except Exception as e:
        print(f"Erreur lors de la création du locataire: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du locataire: {str(e)}")

@app.put("/api/tenants/{tenant_id}")
async def update_tenant(tenant_id: int, tenant_data: TenantUpdate):
    """Mettre à jour un locataire existant"""
    try:
        # Convertir en dictionnaire pour le service
        update_dict = tenant_data.dict(exclude_unset=True)
        
        # Mettre à jour via le service SQLite
        updated_tenant = db_service.update_tenant(tenant_id, update_dict)
        
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
        success = db_service.delete_tenant(tenant_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Locataire non trouvé")
        
        return {"message": "Locataire supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression du locataire: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.delete("/api/assignments/tenant/{tenant_id}")
async def delete_tenant_assignments(tenant_id: int):
    """Supprimer toutes les assignations d'un locataire"""
    try:
        # Supprimer toutes les assignations du locataire
        success = db_service.delete_tenant_assignments(tenant_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Aucune assignation trouvée pour ce locataire")
        
        return {"message": f"Assignations du locataire {tenant_id} supprimées avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression des assignations: {e}")
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
        assignments = db_service.get_assignments()
        return {"data": assignments}
    except Exception as e:
        print(f"Erreur lors du chargement des assignations: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.post("/api/tenants/create-with-assignment")
async def create_tenant_with_assignment(data: dict):
    """Créer un locataire avec son assignation - LOGIQUE SIMPLE ET FIABLE"""
    try:
        print(f"🔍 DEBUG - create_tenant_with_assignment reçu: {data}")
        
        # NOUVEAU FORMAT : data contient {tenant: {...}, assignment: {...}}
        tenant_data = data.get("tenant", {})
        assignment_data = data.get("assignment", {})
        
        # Fallback pour l'ancien format
        if not tenant_data and not assignment_data:
            tenant_data = {
                "name": data.get("name", "").strip(),
                "email": data.get("email", "").strip(),
                "phone": data.get("phone", "").strip(),
                "notes": data.get("notes", "")
            }
            assignment_data = {
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
        
        # Validation basique
        if not tenant_data.get("name", "").strip():
            raise HTTPException(status_code=400, detail="Le nom du locataire est obligatoire")
        
        if not assignment_data.get("unitId"):
            raise HTTPException(status_code=400, detail="L'unité est obligatoire")
        
        # 1. CRÉER LE LOCATAIRE (informations personnelles uniquement)
        print(f"📝 Création du locataire: {tenant_data['name']}")
        created_tenant = db_service.create_tenant(tenant_data)
        tenant_id = created_tenant["id"]
        print(f"✅ Locataire créé avec ID: {tenant_id}")
        
        # 2. CRÉER L'ASSIGNATION avec les données de bail
        print(f"🏠 Création de l'assignation pour l'unité: {assignment_data['unitId']}")
        assignment_data["tenantId"] = tenant_id
        
        # Supprimer les valeurs None/vides
        assignment_data = {k: v for k, v in assignment_data.items() if v is not None and v != ""}
        
        created_assignment = db_service.create_assignment_with_validation(assignment_data)
        print(f"✅ Assignation créée avec ID: {created_assignment['id']}")
        
        return {
            "data": {
                "tenant": created_tenant,
                "assignment": created_assignment,
                "message": "Locataire et assignation créés avec succès"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")

@app.post("/api/assignments")
async def create_assignment(assignment_data: dict):
    """Créer une nouvelle assignation locataire-unité"""
    try:
        print(f"🔍 DEBUG - create_assignment reçu: {assignment_data}")
        tenant_id = assignment_data.get("tenantId")
        unit_id = assignment_data.get("unitId")
        print(f"🔍 DEBUG - tenant_id: {tenant_id}, unit_id: {unit_id}")
        
        # Validation : Vérifier que le locataire existe
        tenant = db_service.get_tenant(tenant_id)
        if not tenant:
            print(f"❌ Assignation rejetée: Locataire {tenant_id} n'existe pas")
            raise HTTPException(
                status_code=400, 
                detail=f"Le locataire avec l'ID {tenant_id} n'existe pas dans la base de données"
            )
        
        print(f"✅ Locataire trouvé: {tenant}")
        
        # Créer la nouvelle assignation via le service SQLite
        # Le service gère automatiquement la validation des assignations actives
        new_assignment = db_service.create_assignment_with_validation(assignment_data)
        
        print(f"✅ Assignation créée: Locataire {tenant_id} → Unité {unit_id}")
        return {"data": new_assignment}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'assignation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'assignation: {str(e)}")

@app.delete("/api/assignments/{assignment_id}")
async def delete_assignment_by_id(assignment_id: int):
    """Supprimer une assignation par son ID"""
    try:
        print(f"🗑️ Suppression de l'assignation {assignment_id}")
        
        # Supprimer via le service SQLite
        success = db_service.delete_assignment(assignment_id)
        
        if success:
            print(f"✅ Assignation {assignment_id} supprimée")
            return {"message": f"Assignation {assignment_id} supprimée avec succès"}
        else:
            raise HTTPException(status_code=404, detail=f"Assignation {assignment_id} non trouvée")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur lors de la suppression de l'assignation {assignment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.delete("/api/assignments/tenant/{tenant_id}")
async def remove_tenant_assignment(tenant_id: int):
    """Retirer un locataire de toute unité"""
    try:
        # Supprimer via le service SQLite
        assignments = db_service.get_assignments()
        tenant_assignments = [a for a in assignments if a.get("tenantId") == tenant_id]
        
        if not tenant_assignments:
            raise HTTPException(status_code=404, detail="Aucune assignation trouvée pour ce locataire")
        
        # Supprimer chaque assignation
        for assignment in tenant_assignments:
            db_service.delete_assignment(assignment["id"])
        
        print(f"Assignation supprimée pour le locataire {tenant_id}")
        return {"message": f"Locataire retiré de son unité ({len(tenant_assignments)} assignation(s) supprimée(s))"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la suppression de l'assignation: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.delete("/api/assignments/tenant/{tenant_id}/unit/{unit_id}")
async def remove_specific_assignment(tenant_id: int, unit_id: str):
    """Retirer un locataire d'une unité spécifique (ne supprime que cette assignation)"""
    try:
        # Supprimer via le service SQLite
        assignments = db_service.get_assignments()
        specific_assignment = None
        
        for assignment in assignments:
            if (assignment.get("tenantId") == tenant_id and 
                assignment.get("unitId") == unit_id):
                specific_assignment = assignment
                break
        
        if not specific_assignment:
            raise HTTPException(status_code=404, detail="Assignation non trouvée pour ce locataire et cette unité")
        
        # Supprimer l'assignation spécifique
        db_service.delete_assignment(specific_assignment["id"])
        
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
        reports = db_service.get_building_reports()
        return {"data": reports}
    except Exception as e:
        print(f"Erreur lors du chargement des rapports d'immeubles: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

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
        building_id = report_data.get("buildingId")
        year = report_data.get("year")
        
        # Vérifier si un rapport existe déjà pour cet immeuble et cette année
        reports = db_service.get_building_reports()
        existing_report = next((r for r in reports if r.get("buildingId") == building_id and r.get("year") == year), None)
        
        if existing_report:
            # Mettre à jour le rapport existant via SQLite
            updated_report = db_service.update_building_report(existing_report["id"], report_data)
        else:
            # Créer un nouveau rapport via SQLite
            updated_report = db_service.create_building_report(report_data)
        
        print(f"Rapport immeuble sauvegardé: {building_id} - {year}")
        return {"data": updated_report}
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du rapport d'immeuble: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde du rapport d'immeuble: {str(e)}")

@app.delete("/api/building-reports/{report_id}")
async def delete_building_report(report_id: int):
    """Supprimer un rapport d'immeuble"""
    try:
        # Supprimer via le service SQLite
        success = db_service.delete_building_report(report_id)
        
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

@app.get("/api/unit-reports")
async def get_unit_reports():
    """Récupérer tous les rapports d'unités"""
    try:
        reports = db_service.get_unit_reports()
        return {"data": reports}
    except Exception as e:
        print(f"Erreur lors du chargement des rapports d'unités: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

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
        # Créer le rapport via le service SQLite
        new_report = db_service.create_unit_report(report_data)
        
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
        success = db_service.delete_unit_report(report_id)
        
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
        unit = db_service.get_unit(unit_id)
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
        success = db_service.delete_unit(unit_id)
        
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
# ROUTES POUR LES UNITÉS
# ========================================

@app.get("/api/units")
async def get_units(skip: int = 0, limit: int = 100):
    """Récupérer toutes les unités"""
    try:
        units = db_service.get_units(skip=skip, limit=limit)
        return {"data": units}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des unités: {str(e)}")

@app.get("/api/units/{unit_id}")
async def get_unit(unit_id: int):
    """Récupérer une unité par ID"""
    try:
        unit = db_service.get_unit(unit_id)
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
        units = db_service.get_units_by_building(building_id)
        return {"units": units, "total": len(units)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des unités: {str(e)}")

@app.post("/api/units")
async def create_unit(unit_data: Dict[str, Any]):
    """Créer une nouvelle unité"""
    try:
        unit = db_service.create_unit(unit_data)
        return {"unit": unit, "message": "Unité créée avec succès"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'unité: {str(e)}")

@app.put("/api/units/{unit_id}")
async def update_unit(unit_id: int, unit_data: Dict[str, Any]):
    """Mettre à jour une unité"""
    try:
        unit = db_service.update_unit(unit_id, unit_data)
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
        success = db_service.delete_unit(unit_id)
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

@app.get("/api/invoices")
async def get_invoices():
    """Récupérer toutes les factures"""
    try:
        invoices = db_service.get_invoices()
        return {"data": invoices}
    except Exception as e:
        print(f"Erreur lors du chargement des factures: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des factures: {str(e)}")

@app.get("/api/invoices/{invoice_id}")
async def get_invoice(invoice_id: int):
    """Récupérer une facture spécifique par ID"""
    try:
        invoice = db_service.get_invoice(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Facture non trouvée")
        return {"data": invoice}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la récupération de la facture: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la facture: {str(e)}")

@app.post("/api/invoices")
async def create_invoice(invoice_data: InvoiceCreate):
    """Créer une nouvelle facture"""
    try:
        # Convertir en dictionnaire pour le service
        invoice_dict = invoice_data.dict()
        
        # Créer la facture via le service SQLite
        new_invoice = db_service.create_invoice(invoice_dict)
        
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
        # Convertir en dictionnaire pour le service
        update_dict = invoice_data.dict(exclude_unset=True)
        
        # Mettre à jour via le service SQLite
        updated_invoice = db_service.update_invoice(invoice_id, update_dict)
        
        if not updated_invoice:
            raise HTTPException(status_code=404, detail="Facture non trouvée")
        
        print(f"✅ Facture mise à jour: {updated_invoice.get('invoiceNumber')}")
        return {"data": updated_invoice}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la facture: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la facture: {str(e)}")

@app.delete("/api/invoices/{invoice_id}")
async def delete_invoice(invoice_id: int):
    """Supprimer une facture"""
    try:
        # Supprimer la facture via le service SQLite
        success = db_service.delete_invoice(invoice_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Facture non trouvée")
        
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
        results = data_validator.validate_all()
        
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
        results = data_validator.validate_all()
        
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

@app.post("/api/migrate-schema")
async def migrate_schema():
    """Migrer le schéma de la base de données"""
    try:
        from sqlalchemy import text
        
        session = db_service.get_session()
        try:
            # Recréer complètement la table unit_reports avec le bon schéma
            print("🔄 Recréation de la table unit_reports...")
            
            # Supprimer l'ancienne table
            session.execute(text("DROP TABLE IF EXISTS unit_reports"))
            
            # Créer la nouvelle table avec le bon schéma
            session.execute(text("""
                CREATE TABLE unit_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    tenant_name TEXT,
                    payment_method TEXT,
                    is_heated_lit BOOLEAN DEFAULT 0,
                    is_furnished BOOLEAN DEFAULT 0,
                    wifi_included BOOLEAN DEFAULT 0,
                    rent_amount REAL DEFAULT 0.0,
                    start_date TEXT,
                    end_date TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (unit_id) REFERENCES units (id) ON DELETE CASCADE
                )
            """))
            
            session.commit()
            print("✅ Table unit_reports recréée avec le bon schéma")
            
            return {"message": "Migration du schéma réussie - Table unit_reports recréée"}
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur migration: {str(e)}")

@app.post("/api/migrate-remove-building-id")
async def migrate_remove_building_id():
    """Supprimer la colonne building_id de la table assignments"""
    try:
        from migrate_remove_building_id import migrate_remove_building_id
        
        print("🔄 Début de la migration: suppression de building_id")
        success = migrate_remove_building_id()
        
        if success:
            print("✅ Migration building_id terminée avec succès")
            return {"message": "Migration building_id terminée avec succès"}
        else:
            print("❌ Migration building_id échouée")
            raise HTTPException(status_code=500, detail="Migration building_id échouée")
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration building_id: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur migration building_id: {str(e)}")

@app.get("/api/test-endpoint")
async def test_endpoint():
    """Endpoint de test pour vérifier le déploiement"""
    return {"message": "Test endpoint fonctionne", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 