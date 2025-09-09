#!/bin/bash
# Script de build pour Render

echo "🚀 BUILD INTERFACE CAH BACKEND"
echo "================================"

# Vérifier la version Python
echo "🐍 Version Python:"
python --version

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer le répertoire de données
echo "📁 Création du répertoire de données..."
mkdir -p /opt/render/project/src/data

# Tester l'import de l'API
echo "🔍 Test de l'API..."
python -c "from main import app; print('✅ API importée avec succès')"

echo "✅ Build terminé avec succès"
