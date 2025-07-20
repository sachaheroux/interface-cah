#!/usr/bin/env python3
"""
Script pour créer un fichier PDF de test
Usage: python create_test_pdf.py
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# Configuration
DATA_DIR = os.environ.get("DATA_DIR", "./data")
DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")

def create_test_pdf():
    """Créer un fichier PDF de test"""
    print("📄 Création d'un fichier PDF de test")
    print("=" * 50)
    
    # Créer le répertoire documents s'il n'existe pas
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    
    # Nom du fichier de test
    filename = "Objectifs de niveau des indicateurs.pdf"
    filepath = os.path.join(DOCUMENTS_DIR, filename)
    
    try:
        # Créer le PDF
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Titre
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Objectifs de niveau des indicateurs")
        
        # Sous-titre
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, "Document de test généré automatiquement")
        
        # Contenu
        c.setFont("Helvetica", 10)
        y_position = height - 120
        
        content = [
            "Ce document est un fichier PDF de test créé automatiquement",
            "pour vérifier le fonctionnement du système d'upload et d'affichage",
            "des documents dans l'interface CAH.",
            "",
            "Fonctionnalités testées :",
            "• Upload de fichiers PDF",
            "• Stockage sur le serveur",
            "• Affichage dans les rapports d'unités",
            "• Ouverture des PDFs depuis l'interface",
            "",
            "Ce fichier peut être supprimé une fois les tests terminés."
        ]
        
        for line in content:
            c.drawString(50, y_position, line)
            y_position -= 20
        
        # Pied de page
        c.setFont("Helvetica", 8)
        c.drawString(50, 50, f"Généré le : {os.popen('date').read().strip()}")
        
        c.save()
        
        print(f"✅ PDF créé avec succès : {filepath}")
        print(f"📏 Taille : {os.path.getsize(filepath)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du PDF : {e}")
        return False

if __name__ == "__main__":
    create_test_pdf() 