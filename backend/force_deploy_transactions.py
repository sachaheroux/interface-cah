#!/usr/bin/env python3
"""
Script pour forcer le déploiement des modifications de transactions sur Render
"""

import subprocess
import sys
import time

def run_command(command, description):
    """Exécuter une commande et afficher le résultat"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} réussi")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} échoué")
            if result.stderr:
                print(f"   Erreur: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de {description}: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Forçage du déploiement des modifications de transactions")
    print("=" * 60)
    
    # Vérifier qu'on est dans le bon répertoire
    try:
        result = subprocess.run("git status", shell=True, capture_output=True, text=True)
        if "interface-cah" not in result.stdout:
            print("❌ Veuillez exécuter ce script depuis le répertoire du projet")
            return False
    except:
        print("❌ Erreur lors de la vérification du répertoire Git")
        return False
    
    # 1. Ajouter tous les fichiers modifiés
    if not run_command("git add .", "Ajout des fichiers modifiés"):
        return False
    
    # 2. Créer un commit avec un message descriptif
    commit_message = "Backend: Migration table transactions vers structure française"
    if not run_command(f'git commit -m "{commit_message}"', "Création du commit"):
        return False
    
    # 3. Pousser vers le repository distant
    if not run_command("git push origin main", "Push vers le repository distant"):
        return False
    
    print("\n⏳ Attente du déploiement sur Render...")
    print("   (Cela peut prendre 2-3 minutes)")
    
    # 4. Attendre et tester le déploiement
    for i in range(12):  # 12 tentatives sur 2 minutes
        print(f"   Tentative {i+1}/12...")
        time.sleep(10)
        
        # Tester l'endpoint des constantes
        try:
            import requests
            response = requests.get("https://interface-cah-backend.onrender.com/api/transactions/constants")
            if response.status_code == 200:
                constants = response.json()
                if 'categories' in constants and constants['categories']:
                    print("✅ Déploiement réussi! Les nouvelles constantes sont disponibles")
                    return True
        except:
            pass
    
    print("⚠️ Le déploiement prend plus de temps que prévu")
    print("   Veuillez vérifier manuellement sur https://dashboard.render.com")
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Déploiement terminé avec succès!")
        print("✅ La page Transactions devrait maintenant fonctionner")
    else:
        print("\n❌ Problème lors du déploiement")
    sys.exit(0 if success else 1)
