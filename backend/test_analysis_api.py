#!/usr/bin/env python3
"""
Test simple de l'API d'analyse de rentabilité
"""

import requests

def test_analysis_api():
    """Tester l'API d'analyse de rentabilité"""
    
    print("🔍 TEST DE L'API D'ANALYSE DE RENTABILITÉ")
    print("=" * 50)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        # Test avec l'immeuble 1
        print("\n1. TEST AVEC L'IMMEUBLE 1:")
        response = requests.get(f"{base_url}/analysis/profitability?building_ids=1&start_year=2025&start_month=7&end_year=2026&end_month=6")
        
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"   ✅ API d'analyse fonctionne")
            print(f"   Nombre d'immeubles: {len(analysis_data.get('buildings', []))}")
            print(f"   Nombre de mois: {len(analysis_data.get('monthlyTotals', []))}")
            
            # Afficher les données détaillées
            if analysis_data.get('buildings'):
                print(f"   Immeubles trouvés:")
                for building in analysis_data['buildings']:
                    print(f"     - {building.get('name')}: Revenus: ${building.get('revenue', 0)}, Dépenses: ${building.get('expenses', 0)}, Cashflow: ${building.get('netCashflow', 0)}")
            
            if analysis_data.get('monthlyTotals'):
                print(f"   Données mensuelles:")
                for i, month in enumerate(analysis_data['monthlyTotals'][:3]):
                    print(f"     - {month.get('month')}: Revenus: ${month.get('revenue', 0)}, Dépenses: ${month.get('expenses', 0)}, Cashflow: ${month.get('netCashflow', 0)}")
                
                # Vérifier septembre 2025 (mois 2, index 2)
                if len(analysis_data['monthlyTotals']) > 2:
                    sept = analysis_data['monthlyTotals'][2]
                    print(f"   📊 Septembre 2025: Revenus: ${sept.get('revenue', 0)}, Dépenses: ${sept.get('expenses', 0)}, Cashflow: ${sept.get('netCashflow', 0)}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analysis_api()
