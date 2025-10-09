"""
Script pour appeler l'endpoint de suppression des paiements_loyers sur Render
"""
import requests

RENDER_URL = "https://interface-cah-backend.onrender.com"

def clear_paiements_loyers():
    """Appeler l'endpoint pour vider la table paiements_loyers"""
    print("=" * 80)
    print("⚠️  SUPPRESSION DE TOUTES LES DONNÉES paiements_loyers SUR RENDER")
    print("=" * 80)
    
    print(f"\n🌐 URL: {RENDER_URL}/api/paiements-loyers/clear-all")
    
    try:
        print("\n⏳ Envoi de la requête DELETE...")
        response = requests.delete(f"{RENDER_URL}/api/paiements-loyers/clear-all", timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ {data['message']}")
            print(f"📊 Enregistrements supprimés: {data['deleted_count']}")
            print(f"📊 Enregistrements restants: {data['remaining_count']}")
        else:
            print(f"\n❌ Erreur HTTP {response.status_code}")
            print(f"Réponse: {response.text[:500]}")
            
    except Exception as e:
        print(f"\n❌ ERREUR: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 80)
    print("✅ OPÉRATION TERMINÉE")
    print("=" * 80)

if __name__ == "__main__":
    # Demander confirmation
    print("\n⚠️  ATTENTION: Cette opération va supprimer TOUTES les données de paiements_loyers sur Render!")
    confirmation = input("Tapez 'OUI' pour confirmer: ")
    
    if confirmation == "OUI":
        clear_paiements_loyers()
    else:
        print("❌ Opération annulée")

