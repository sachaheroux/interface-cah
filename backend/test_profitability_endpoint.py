"""
Script pour tester l'endpoint d'analyse de rentabilité
"""
import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah.onrender.com"
LOCAL_URL = "http://localhost:8000"

# Utiliser Render par défaut
BASE_URL = RENDER_URL

def test_profitability_endpoint():
    """Tester l'endpoint d'analyse de rentabilité"""
    print("=" * 80)
    print("🧪 TEST DE L'ENDPOINT D'ANALYSE DE RENTABILITÉ")
    print("=" * 80)
    print(f"\n🌐 URL de base: {BASE_URL}")
    
    # 1. Récupérer les immeubles disponibles
    print("\n1️⃣ Récupération des immeubles...")
    print("-" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/buildings", timeout=30)
        response.raise_for_status()
        buildings = response.json()
        print(f"✅ {len(buildings)} immeubles trouvés")
        
        if not buildings:
            print("❌ Aucun immeuble disponible pour le test")
            return
        
        # Afficher les immeubles
        for building in buildings[:5]:  # Limiter à 5
            print(f"   - Immeuble #{building['id_immeuble']}: {building.get('adresse', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des immeubles: {e}")
        return
    
    # 2. Tester l'analyse de rentabilité avec différents scénarios
    test_cases = [
        {
            "name": "Test avec 1 immeuble",
            "building_ids": str(buildings[0]['id_immeuble']),
            "start_year": 2024,
            "start_month": 1,
            "end_year": 2024,
            "end_month": 12,
            "confirmed_payments_only": False
        },
        {
            "name": "Test avec tous les immeubles",
            "building_ids": ",".join(str(b['id_immeuble']) for b in buildings),
            "start_year": 2024,
            "start_month": 1,
            "end_year": 2024,
            "end_month": 12,
            "confirmed_payments_only": False
        },
        {
            "name": "Test avec paiements confirmés uniquement",
            "building_ids": str(buildings[0]['id_immeuble']),
            "start_year": 2024,
            "start_month": 1,
            "end_year": 2024,
            "end_month": 12,
            "confirmed_payments_only": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{i}️⃣ {test_case['name']}")
        print("-" * 80)
        
        params = {
            "building_ids": test_case["building_ids"],
            "start_year": test_case["start_year"],
            "start_month": test_case["start_month"],
            "end_year": test_case["end_year"],
            "end_month": test_case["end_month"],
            "confirmed_payments_only": test_case["confirmed_payments_only"]
        }
        
        print(f"Paramètres: {json.dumps(params, indent=2)}")
        
        try:
            print("\n⏳ Envoi de la requête...")
            response = requests.get(
                f"{BASE_URL}/api/analysis/profitability",
                params=params,
                timeout=60
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Réponse reçue avec succès!")
                print(f"\n📈 Résumé des données:")
                print(f"   - Nombre d'immeubles: {len(data.get('buildings', []))}")
                print(f"   - Nombre de mois: {len(data.get('monthlyTotals', []))}")
                print(f"   - Période: {data.get('period', {}).get('start')} à {data.get('period', {}).get('end')}")
                
                # Afficher quelques détails
                if data.get('buildings'):
                    for building in data['buildings'][:3]:
                        print(f"\n   🏢 {building.get('name', 'N/A')}")
                        print(f"      Revenus: {building.get('totalRevenue', 0):.2f}$")
                        print(f"      Dépenses: {building.get('totalExpenses', 0):.2f}$")
                        print(f"      Net: {building.get('netCashflow', 0):.2f}$")
            else:
                print(f"❌ Erreur HTTP {response.status_code}")
                print(f"Réponse: {response.text[:500]}")
                
        except requests.exceptions.Timeout:
            print(f"❌ TIMEOUT - La requête a pris plus de 60 secondes")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ ERREUR DE CONNEXION: {e}")
        except Exception as e:
            print(f"❌ ERREUR: {type(e).__name__}: {e}")
    
    print("\n\n" + "=" * 80)
    print("✅ TESTS TERMINÉS")
    print("=" * 80)

if __name__ == "__main__":
    test_profitability_endpoint()

