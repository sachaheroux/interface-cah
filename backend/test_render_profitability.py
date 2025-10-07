"""
Script pour tester l'analyse de rentabilité sur Render et diagnostiquer les erreurs
"""
import requests
import json
import time

RENDER_URL = "https://interface-cah.onrender.com"

def test_render_health():
    """Vérifier que le backend Render répond"""
    print("=" * 80)
    print("🏥 TEST DE SANTÉ DU BACKEND RENDER")
    print("=" * 80)
    
    try:
        print(f"\n🌐 Connexion à {RENDER_URL}/health...")
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Réponse: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ ERREUR: {type(e).__name__}: {e}")
        return False

def test_get_buildings():
    """Récupérer les immeubles"""
    print("\n\n" + "=" * 80)
    print("🏢 TEST DE RÉCUPÉRATION DES IMMEUBLES")
    print("=" * 80)
    
    try:
        print(f"\n🌐 GET {RENDER_URL}/api/buildings...")
        response = requests.get(f"{RENDER_URL}/api/buildings", timeout=30)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            buildings = response.json()
            print(f"✅ {len(buildings)} immeubles récupérés")
            
            for i, building in enumerate(buildings[:3], 1):
                print(f"\n  {i}. Immeuble #{building.get('id_immeuble')}")
                print(f"     Adresse: {building.get('adresse', 'N/A')}")
                print(f"     Unités: {building.get('nbr_unite', 'N/A')}")
                print(f"     Dette restante: {building.get('dette_restante', 'MANQUANT')}")
            
            return buildings
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"Réponse: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ ERREUR: {type(e).__name__}: {e}")
        return None

def test_profitability_analysis(buildings):
    """Tester l'analyse de rentabilité"""
    print("\n\n" + "=" * 80)
    print("📊 TEST DE L'ANALYSE DE RENTABILITÉ")
    print("=" * 80)
    
    if not buildings or len(buildings) == 0:
        print("❌ Aucun immeuble disponible pour le test")
        return
    
    # Test avec le premier immeuble
    building_id = buildings[0]['id_immeuble']
    
    params = {
        "building_ids": str(building_id),
        "start_year": 2024,
        "start_month": 1,
        "end_year": 2024,
        "end_month": 12,
        "confirmed_payments_only": False
    }
    
    print(f"\n📋 Paramètres du test:")
    print(f"   - Immeuble: #{building_id}")
    print(f"   - Période: 2024-01 à 2024-12")
    
    try:
        print(f"\n⏳ Envoi de la requête...")
        start_time = time.time()
        
        response = requests.get(
            f"{RENDER_URL}/api/analysis/profitability",
            params=params,
            timeout=60
        )
        
        elapsed = time.time() - start_time
        print(f"⏱️ Temps de réponse: {elapsed:.2f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analyse réussie!")
            print(f"\n📈 Résumé:")
            print(f"   - Nombre d'immeubles: {len(data.get('buildings', []))}")
            print(f"   - Nombre de mois: {len(data.get('monthlyTotals', []))}")
            
            if data.get('buildings'):
                for building in data['buildings'][:3]:
                    print(f"\n   🏢 {building.get('name', 'N/A')}")
                    print(f"      Revenus: {building.get('totalRevenue', 0):.2f}$")
                    print(f"      Dépenses: {building.get('totalExpenses', 0):.2f}$")
                    print(f"      Net: {building.get('netCashflow', 0):.2f}$")
            
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"\n📄 Réponse complète:")
            print(response.text[:1000])
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT - La requête a dépassé 60 secondes")
        print(f"\n💡 Cela indique probablement:")
        print(f"   1. Une erreur dans le calcul de l'analyse")
        print(f"   2. Une boucle infinie dans le code")
        print(f"   3. Un problème de base de données (colonne manquante, etc.)")
        return False
        
    except Exception as e:
        print(f"❌ ERREUR: {type(e).__name__}: {e}")
        return False

def test_migration_endpoint():
    """Tester l'endpoint de migration dette_restante"""
    print("\n\n" + "=" * 80)
    print("🔧 TEST DE LA MIGRATION dette_restante")
    print("=" * 80)
    
    try:
        print(f"\n⏳ Appel de l'endpoint de migration...")
        response = requests.post(f"{RENDER_URL}/api/migrate/dette-restante", timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Migration réussie')}")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"Réponse: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {type(e).__name__}: {e}")
        return False

def main():
    """Exécuter tous les tests"""
    print("\n")
    print("🔬 DIAGNOSTIC COMPLET DU BACKEND RENDER")
    print("=" * 80)
    print(f"URL: {RENDER_URL}")
    print("=" * 80)
    
    # 1. Test de santé
    if not test_render_health():
        print("\n❌ Le backend ne répond pas. Arrêt des tests.")
        return
    
    # 2. Test de migration
    test_migration_endpoint()
    
    # 3. Récupération des immeubles
    buildings = test_get_buildings()
    
    # 4. Test de l'analyse de rentabilité
    if buildings:
        test_profitability_analysis(buildings)
    
    print("\n\n" + "=" * 80)
    print("✅ DIAGNOSTIC TERMINÉ")
    print("=" * 80)

if __name__ == "__main__":
    main()

