#!/usr/bin/env python3
"""
Script pour supprimer tous les fallbacks localStorage du fichier api.js
"""

import re

# Lire le fichier
with open('src/services/api.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Supprimer les fallbacks localStorage
patterns_to_remove = [
    # Fallback vers localStorage dans getTenants
    r'console\.warn\(''API tenants failed, using fallback data:'', error\.message\)\s*// Retourner les données du localStorage en cas d'échec API\s*const localTenants = JSON\.parse\(localStorage\.getItem\(''localTenants''\) \|\| ''\[\]''\)\s*if \(localTenants\.length === 0\) \{\s*// Si pas de données locales, utiliser les données par défaut\s*return \{ data: fallbackTenants \}\s*\}\s*return \{ data: localTenants \}',
    
    # Fallback vers localStorage dans createTenant
    r'console\.warn\(''API create tenant failed, saving locally''\)\s*// Fallback vers localStorage\s*const localTenants = JSON\.parse\(localStorage\.getItem\(''localTenants''\) \|\| ''\[\]''\)\s*const newTenant = \{\s*\.\.\.data,\s*id: Date\.now\(\),\s*createdAt: new Date\(\)\.toISOString\(\),\s*updatedAt: new Date\(\)\.toISOString\(\)\s*\}\s*localTenants\.push\(newTenant\)\s*localStorage\.setItem\(''localTenants'', JSON\.stringify\(localTenants\)\)\s*return \{ data: newTenant \}',
    
    # Fallback vers localStorage dans updateTenant
    r'console\.warn\(''⚠️ API update tenant failed, updating locally:'', error\.message\)\s*// Fallback vers localStorage\s*const localTenants = JSON\.parse\(localStorage\.getItem\(''localTenants''\) \|\| ''\[\]''\)\s*const index = localTenants\.findIndex\(t => t\.id === parseInt\(id\)\)\s*if \(index !== -1\) \{\s*localTenants\[index\] = \{ \.\.\.localTenants\[index\], \.\.\.data, updatedAt: new Date\(\)\.toISOString\(\) \}\s*localStorage\.setItem\(''localTenants'', JSON\.stringify\(localTenants\)\)\s*console\.log\(''Tenant updated locally:'', localTenants\[index\]\)\s*return \{ data: localTenants\[index\] \}\s*\}\s*throw error',
    
    # Fallback vers localStorage dans deleteTenant
    r'console\.warn\(''API delete tenant failed, deleting locally''\)\s*// Fallback vers localStorage\s*const localTenants = JSON\.parse\(localStorage\.getItem\(''localTenants''\) \|\| ''\[\]''\)\s*const filteredTenants = localTenants\.filter\(t => t\.id !== parseInt\(id\)\)\s*localStorage\.setItem\(''localTenants'', JSON\.stringify\(filteredTenants\)\)\s*return \{ success: true, fallback: true \}',
]

# Remplacer par des erreurs simples
replacements = [
    'console.error(\'❌ Error getting tenants from Render:\', error)\n      throw error',
    'console.error(\'❌ Error creating tenant on Render:\', error)\n      throw error',
    'console.error(\'❌ Error updating tenant on Render:\', error)\n      throw error',
    'console.error(\'❌ Error deleting tenant on Render:\', error)\n      throw error',
]

# Appliquer les remplacements
for i, pattern in enumerate(patterns_to_remove):
    content = re.sub(pattern, replacements[i], content, flags=re.DOTALL)

# Écrire le fichier modifié
with open('src/services/api.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fallbacks localStorage supprimés du fichier api.js")
