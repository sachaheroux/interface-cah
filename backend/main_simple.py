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

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de données
class TenantCreate(BaseModel):
    name: str
    email: str
    phone: str
    notes: Optional[str] = None
    unitId: int
    lease: Optional[Dict[str, Any]] = None
    moveInDate: Optional[str] = None
    moveOutDate: Optional[str] = None
    rentAmount: Optional[float] = None
    leaseStartDate: Optional[str] = None
    leaseEndDate: Optional[str] = None
    rentDueDay: Optional[int] = 1

# Endpoints de base
@app.get("/")
async def root():
    return {"message": "Interface CAH API - Version 1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/tenants")
async def get_tenants():
    return {"tenants": [], "message": "Endpoint temporaire - base de données non initialisée"}

@app.post("/api/tenants/create-with-assignment")
async def create_tenant_with_assignment(tenant_data: TenantCreate):
    return {
        "message": "Endpoint temporaire - base de données non initialisée",
        "data": {
            "tenant": {
                "id": 1,
                "name": tenant_data.name,
                "email": tenant_data.email,
                "phone": tenant_data.phone,
                "notes": tenant_data.notes
            }
        }
    }

if __name__ == "__main__":
    print("🚀 Démarrage de l'application Interface CAH (version simple)...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
