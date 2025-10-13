#!/usr/bin/env python3
"""
Script pour supprimer l'ancien endpoint conflictuel
"""

# Créons un script pour supprimer l'ancien endpoint
print("Suppression de l'ancien endpoint conflictuel...")

# Lisons le fichier
with open("auth_routes.py", "r", encoding="utf-8") as f:
    content = f.read()

# Trouvons les lignes à supprimer (lignes 729-830)
lines = content.split('\n')

# Supprimons les lignes 729-830 (index 728-829)
new_lines = lines[:728] + lines[830:]

# Écrivons le nouveau contenu
with open("auth_routes.py", "w", encoding="utf-8") as f:
    f.write('\n'.join(new_lines))

print("✅ Ancien endpoint supprimé !")
print("Le fichier a été nettoyé.")
