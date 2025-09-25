#!/usr/bin/env python3
import requests

url = 'https://interface-cah-backend.onrender.com/api/analysis/profitability'
params = {
    'building_ids': '1',
    'start_year': 2025,
    'start_month': 7,
    'end_year': 2026,
    'end_month': 6
}

print('🔍 TEST API RENDER')
print('=' * 30)

response = requests.get(url, params=params)
print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    print(f'Summary: {data.get("summary", "NON TROUVÉ")}')
    print(f'Buildings: {len(data.get("buildings", []))}')
    
    for building in data.get('buildings', []):
        summary = building.get('summary', {})
        print(f'  - {building.get("name", "N/A")}: Revenus: ${summary.get("totalRevenue", 0)}, Dépenses: ${summary.get("totalExpenses", 0)}')
        
    print(f'Monthly data: {len(data.get("monthlyTotals", []))} mois')
    for month in data.get('monthlyTotals', [])[:3]:
        print(f'  - {month.get("month", "N/A")}: Revenus: ${month.get("revenue", 0)}, Dépenses: ${month.get("expenses", 0)}')
else:
    print(f'Erreur: {response.text}')
