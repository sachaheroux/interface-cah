"""
Script pour vérifier le statut détaillé du backend Render
"""
import requests
import time

RENDER_URL = "https://interface-cah.onrender.com"

def check_status():
    """Vérifier le statut du backend"""
    print("=" * 80)
    print("🔍 VÉRIFICATION DU STATUT RENDER")
    print("=" * 80)
    print(f"\n🌐 URL: {RENDER_URL}")
    
    # Essayer plusieurs fois avec délai
    for attempt in range(1, 4):
        print(f"\n📡 Tentative {attempt}/3...")
        
        try:
            response = requests.get(
                f"{RENDER_URL}/health",
                timeout=30
            )
            
            print(f"   ✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Backend actif: {response.json()}")
                return True
            elif response.status_code == 404:
                print(f"   ❌ Endpoint non trouvé (404)")
                print(f"   💡 Le backend ne répond pas ou n'est pas démarré")
            else:
                print(f"   ⚠️  Réponse: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout après 30s")
        except requests.exceptions.ConnectionError as e:
            print(f"   🔌 Erreur de connexion: {e}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        if attempt < 3:
            print(f"   ⏳ Attente de 5 secondes...")
            time.sleep(5)
    
    print("\n" + "=" * 80)
    print("❌ LE BACKEND RENDER NE RÉPOND PAS")
    print("=" * 80)
    print("\n📋 Actions recommandées:")
    print("   1. Vérifier les logs Render (Dashboard > Logs)")
    print("   2. Vérifier que le déploiement est terminé")
    print("   3. Vérifier les erreurs de démarrage")
    print("   4. Redémarrer manuellement le service si nécessaire")
    print("\n" + "=" * 80)
    return False

if __name__ == "__main__":
    check_status()

