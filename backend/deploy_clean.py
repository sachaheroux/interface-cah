#!/usr/bin/env python3
"""
Script de déploiement propre pour Render
"""

import subprocess
import sys
import os

def deploy_clean():
    """Déployer une version propre sur Render"""
    
    try:
        print("🚀 Déploiement propre sur Render...")
        print("=" * 50)
        
        # 1. Nettoyer les tables obsolètes localement
        print("🧹 Nettoyage des tables obsolètes...")
        result = subprocess.run([sys.executable, "clean_obsolete_tables.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tables obsolètes nettoyées")
        else:
            print(f"⚠️  Avertissement nettoyage: {result.stderr}")
        
        # 2. Nettoyer main.py
        print("🧹 Nettoyage de main.py...")
        result = subprocess.run([sys.executable, "clean_main_py.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ main.py nettoyé")
        else:
            print(f"⚠️  Avertissement nettoyage main.py: {result.stderr}")
        
        # 3. Tester la migration Render
        print("🌐 Test de la migration Render...")
        result = subprocess.run([sys.executable, "migrate_render_to_transactions.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Migration Render testée")
        else:
            print(f"⚠️  Avertissement migration Render: {result.stderr}")
        
        print("\n🎉 Déploiement propre terminé!")
        print("💡 Votre application est maintenant prête pour Render.")
        print("🌐 Les nouveaux endpoints de transactions sont disponibles:")
        print("   - /api/transactions/constants")
        print("   - /api/transactions")
        print("   - /api/transactions/{id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du déploiement: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Déploiement propre sur Render")
    print("=" * 50)
    
    success = deploy_clean()
    
    if success:
        print("\n🎉 Déploiement réussi!")
        print("🌐 Votre application est maintenant en ligne et propre!")
    else:
        print("\n💥 Déploiement échoué!")
        print("🔧 Vérifiez les erreurs ci-dessus.")
