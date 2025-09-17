#!/usr/bin/env python3
"""
Script pour forcer la mise à jour du code sur Render
"""

import subprocess
import sys
import os

def force_update_render():
    """Forcer la mise à jour sur Render"""
    
    try:
        print("🚀 Mise à jour forcée sur Render...")
        print("=" * 50)
        
        # 1. Vérifier le statut Git
        print("📋 Vérification du statut Git...")
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git status OK")
            print(result.stdout)
        else:
            print(f"❌ Erreur Git status: {result.stderr}")
            return False
        
        # 2. Ajouter tous les fichiers
        print("\n📁 Ajout des fichiers...")
        result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Fichiers ajoutés")
        else:
            print(f"❌ Erreur ajout fichiers: {result.stderr}")
            return False
        
        # 3. Commit avec message descriptif
        print("\n💾 Commit des changements...")
        commit_message = "Fix: Correction erreurs transactions - Utilisation service français uniquement"
        result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Commit créé")
            print(result.stdout)
        else:
            print(f"⚠️  Avertissement commit: {result.stderr}")
            # Continuer même si le commit échoue (peut-être rien à commiter)
        
        # 4. Push vers Render
        print("\n🌐 Push vers Render...")
        result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Push vers Render réussi")
            print("🔄 Déploiement en cours sur Render...")
            print("⏳ Attendez 2-3 minutes pour que le déploiement se termine")
        else:
            print(f"❌ Erreur push: {result.stderr}")
            return False
        
        print("\n🎉 Mise à jour forcée terminée!")
        print("🌐 Votre code est maintenant en cours de déploiement sur Render")
        print("💡 Testez dans quelques minutes avec: python debug_render_transactions.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Mise à jour forcée Render")
    print("=" * 50)
    
    success = force_update_render()
    
    if success:
        print("\n🎉 Mise à jour réussie!")
        print("🌐 Votre application sera mise à jour sur Render dans quelques minutes!")
    else:
        print("\n💥 Mise à jour échouée!")
        print("🔧 Vérifiez les erreurs ci-dessus.")
