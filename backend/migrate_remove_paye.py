"""
Script pour supprimer la colonne 'paye' de la table paiements_loyers sur Render
"""
import requests

RENDER_URL = "https://interface-cah-backend.onrender.com"

def migrate_remove_paye():
    """Appeler l'endpoint de migration"""
    print("=" * 80)
    print("🔧 MIGRATION: Suppression de la colonne 'paye'")
    print("=" * 80)
    print(f"\n🌐 URL: {RENDER_URL}/api/migrate/remove-paye-column")
    
    try:
        print("\n⏳ Envoi de la requête POST...")
        response = requests.post(
            f"{RENDER_URL}/api/migrate/remove-paye-column",
            timeout=60
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ {result.get('message', 'Migration réussie')}")
        else:
            print(f"\n❌ Erreur HTTP {response.status_code}")
            print(f"Réponse: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("\n❌ Timeout après 60 secondes")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    migrate_remove_paye()

