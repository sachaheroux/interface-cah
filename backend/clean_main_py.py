#!/usr/bin/env python3
"""
Script pour nettoyer main.py et supprimer les références aux anciennes tables
"""

import re

def clean_main_py():
    """Nettoyer main.py des références obsolètes"""
    
    main_py_path = "main.py"
    
    try:
        # Lire le fichier
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🧹 Nettoyage de main.py...")
        
        # 1. Supprimer les endpoints obsolètes
        obsolete_endpoints = [
            r'@app\.get\("/api/assignments.*?"\).*?(?=@app\.|\Z)',
            r'@app\.post\("/api/assignments.*?"\).*?(?=@app\.|\Z)',
            r'@app\.delete\("/api/assignments.*?"\).*?(?=@app\.|\Z)',
            r'@app\.get\("/api/building-reports.*?"\).*?(?=@app\.|\Z)',
            r'@app\.get\("/api/unit-reports.*?"\).*?(?=@app\.|\Z)',
            r'@app\.get\("/api/invoices.*?"\).*?(?=@app\.|\Z)',
            r'@app\.post\("/api/invoices.*?"\).*?(?=@app\.|\Z)',
            r'@app\.put\("/api/invoices.*?"\).*?(?=@app\.|\Z)',
            r'@app\.delete\("/api/invoices.*?"\).*?(?=@app\.|\Z)',
        ]
        
        for pattern in obsolete_endpoints:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            print(f"  ✅ Endpoints obsolètes supprimés")
        
        # 2. Nettoyer les espaces multiples
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # 3. Supprimer les imports inutiles
        content = re.sub(r'from.*?assignments.*?\n', '', content)
        content = re.sub(r'from.*?reports.*?\n', '', content)
        
        # Écrire le fichier nettoyé
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ main.py nettoyé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage de main.py: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Nettoyage de main.py")
    print("=" * 50)
    
    success = clean_main_py()
    
    if success:
        print("\n🎉 Nettoyage réussi!")
        print("💡 Le fichier main.py est maintenant propre.")
    else:
        print("\n💥 Nettoyage échoué!")
