"""
Script pour tester la création d'un paiement sur Render
"""
import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def test_create_payment():
    """Tester la création d'un paiement"""
    print("=" * 80)
    print("🧪 TEST CRÉATION PAIEMENT")
    print("=" * 80)
    
    # D'abord, récupérer un bail pour avoir un ID valide
    print("\n1️⃣ Récupération d'un bail...")
    try:
        response = requests.get(f"{RENDER_URL}/api/leases", timeout=30)
        if response.status_code == 200:
            leases = response.json()
            if leases:
                test_lease = leases[0]
                print(f"   ✅ Bail trouvé: ID {test_lease['id_bail']}")
                
                # Essayer de créer un paiement
                print("\n2️⃣ Création d'un paiement...")
                payment_data = {
                    "id_bail": test_lease['id_bail'],
                    "mois": 10,
                    "annee": 2025
                }
                print(f"   Données: {json.dumps(payment_data, indent=2)}")
                
                response = requests.post(
                    f"{RENDER_URL}/api/paiements-loyers",
                    json=payment_data,
                    timeout=30
                )
                
                print(f"\n   Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Paiement créé: {json.dumps(result, indent=2)}")
                else:
                    print(f"   ❌ Erreur HTTP {response.status_code}")
                    print(f"   Réponse: {response.text}")
            else:
                print("   ❌ Aucun bail trouvé")
        else:
            print(f"   ❌ Erreur lors de la récupération des baux: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_create_payment()

