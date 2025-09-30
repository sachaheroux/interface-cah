#!/usr/bin/env python3
"""
Script de debug pour l'analyse de rentabilité
"""

import requests
import json
from datetime import datetime

def test_profitability_analysis():
    """Tester l'analyse de rentabilité avec des paramètres simples"""
    
    # URL de l'API Render
    base_url = "https://interface-cah-backend.onrender.com"
    
    # Paramètres de test
    building_ids = "1,2,3"  # Juste 3 immeubles pour commencer
    start_year = 2025
    start_month = 7
    end_year = 2026
    end_month = 6
    
    # Construire l'URL
    url = f"{base_url}/api/analysis/profitability"
    params = {
        "building_ids": building_ids,
        "start_year": start_year,
        "start_month": start_month,
        "end_year": end_year,
        "end_month": end_month
    }
    
    print(f"🚀 Test de l'analyse de rentabilité")
    print(f"🔍 URL: {url}")
    print(f"🔍 Paramètres: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès!")
            print(f"📋 Données reçues:")
            print(f"  - Nombre d'immeubles: {len(data.get('buildings', []))}")
            print(f"  - Nombre de mois: {len(data.get('monthlyTotals', []))}")
            print(f"  - Résumé: {data.get('summary', {})}")
            
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"📋 Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_profitability_analysis()
