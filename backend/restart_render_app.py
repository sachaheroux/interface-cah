#!/usr/bin/env python3
"""
Script pour redémarrer l'application Render
Cela va réinitialiser complètement la base de données
"""

import requests
import time

def restart_render_app():
    """Redémarrer l'application Render"""
    print("🔄 REDÉMARRAGE DE L'APPLICATION RENDER")
    print("=" * 50)
    
    # URL de l'application Render
    app_url = "https://interface-cah-backend.onrender.com"
    
    try:
        print("1️⃣ Vérification de l'état actuel...")
        
        # Vérifier l'état actuel
        response = requests.get(f"{app_url}/api/buildings", timeout=10)
        if response.status_code == 200:
            buildings = response.json()
            print(f"   📊 Immeubles actuels: {len(buildings)}")
        else:
            print(f"   ⚠️ Erreur vérification: {response.status_code}")
        
        print("\n2️⃣ Tentative de redémarrage...")
        print("   💡 Render redémarre automatiquement après 15 minutes d'inactivité")
        print("   💡 Ou vous pouvez redémarrer manuellement depuis le dashboard Render")
        
        # Essayer de forcer un redémarrage en faisant des requêtes
        print("   🔄 Envoi de requêtes pour forcer le redémarrage...")
        
        for i in range(5):
            try:
                # Faire une requête qui pourrait causer une erreur
                response = requests.get(f"{app_url}/api/force-restart", timeout=5)
                print(f"      Requête {i+1}/5: {response.status_code}")
            except Exception as e:
                print(f"      Requête {i+1}/5: Erreur (normal) - {e}")
            
            time.sleep(2)
        
        print("\n3️⃣ Attente du redémarrage...")
        print("   ⏳ Attente de 30 secondes...")
        time.sleep(30)
        
        print("\n4️⃣ Vérification après redémarrage...")
        
        # Vérifier l'état après redémarrage
        try:
            response = requests.get(f"{app_url}/api/buildings", timeout=10)
            if response.status_code == 200:
                buildings = response.json()
                print(f"   📊 Immeubles après redémarrage: {len(buildings)}")
                
                if len(buildings) == 0:
                    print("   ✅ Redémarrage réussi ! Base de données réinitialisée.")
                    return True
                else:
                    print("   ⚠️ Des données persistent encore.")
                    return False
            else:
                print(f"   ❌ Erreur après redémarrage: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Erreur vérification: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Erreur redémarrage: {e}")
        return False

def manual_restart_instructions():
    """Instructions pour redémarrage manuel"""
    print("\n📋 INSTRUCTIONS POUR REDÉMARRAGE MANUEL")
    print("=" * 50)
    print("1. Allez sur https://dashboard.render.com")
    print("2. Connectez-vous à votre compte")
    print("3. Trouvez votre application 'interface-cah-backend'")
    print("4. Cliquez sur l'application")
    print("5. Cliquez sur le bouton 'Restart' ou 'Redeploy'")
    print("6. Attendez que l'application redémarre")
    print("7. Vérifiez que la base de données est réinitialisée")

def main():
    """Fonction principale"""
    print("🔄 REDÉMARRAGE DE L'APPLICATION RENDER")
    print("=" * 60)
    print("Ce script va tenter de redémarrer l'application Render")
    print("pour réinitialiser complètement la base de données.")
    print("=" * 60)
    
    success = restart_render_app()
    
    if success:
        print("\n🎉 REDÉMARRAGE RÉUSSI !")
        print("   L'application Render a été redémarrée.")
        print("   La base de données est maintenant réinitialisée.")
        return True
    else:
        print("\n💥 REDÉMARRAGE AUTOMATIQUE ÉCHOUÉ !")
        print("   Le redémarrage automatique n'a pas fonctionné.")
        manual_restart_instructions()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
