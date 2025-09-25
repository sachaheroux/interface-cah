#!/usr/bin/env python3
"""
Test direct de l'API Render pour l'analyse de rentabilité
"""

import requests
import json

def test_render_api():
    """Test direct de l'API Render"""
    url = 'https://interface-cah-backend.onrender.com/api/analysis/profitability'
    params = {
        'building_ids': '1',
        'start_year': 2025,
        'start_month': 7,
        'end_year': 2026,
        'end_month': 6
    }

    print('🔍 TEST DIRECT DE L\'API RENDER')
    print('=' * 50)

    try:
        response = requests.get(url, params=params)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'Nombre d\'immeubles: {len(data.get("buildings", []))}')
            print(f'Nombre de mois: {len(data.get("monthlyTotals", []))}')
            
            if 'summary' in data:
                summary = data['summary']
                print(f'Résumé global: Revenus: ${summary.get("totalRevenue", 0)}, Dépenses: ${summary.get("totalExpenses", 0)}, Cashflow: ${summary.get("netCashflow", 0)}')
            
            print('Immeubles:')
            for building in data.get('buildings', []):
                summary = building.get('summary', {})
                print(f'  - {building.get("name", "N/A")}: Revenus: ${summary.get("totalRevenue", 0)}, Dépenses: ${summary.get("totalExpenses", 0)}, Cashflow: ${summary.get("netCashflow", 0)}')
                
            print('\nDonnées mensuelles (premiers 3 mois):')
            for i, month_data in enumerate(data.get('monthlyTotals', [])[:3]):
                print(f'  - {month_data.get("month", "N/A")}: Revenus: ${month_data.get("revenue", 0)}, Dépenses: ${month_data.get("expenses", 0)}, Cashflow: ${month_data.get("netCashflow", 0)}')
        else:
            print(f'Erreur: {response.text}')
            
    except Exception as e:
        print(f'Erreur: {e}')

if __name__ == "__main__":
    test_render_api()
