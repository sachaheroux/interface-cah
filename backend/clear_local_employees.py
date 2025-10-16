#!/usr/bin/env python3
"""
Script pour supprimer les employés de la base locale
"""

import sqlite3
import os
from datetime import datetime

def clear_local_employees():
    """Supprimer tous les employés de la base locale"""
    
    db_path = "data/construction_projects_local.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de données locale non trouvée")
        return
    
    print("🗑️ SUPPRESSION DES EMPLOYÉS LOCAUX")
    print("=" * 50)
    print(f"📁 Base: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Compter les employés avant suppression
        cursor.execute("SELECT COUNT(*) FROM employes")
        count_before = cursor.fetchone()[0]
        print(f"👥 {count_before} employé(s) trouvé(s) avant suppression")
        
        if count_before > 0:
            # Supprimer tous les employés
            cursor.execute("DELETE FROM employes")
            conn.commit()
            
            # Vérifier la suppression
            cursor.execute("SELECT COUNT(*) FROM employes")
            count_after = cursor.fetchone()[0]
            
            print(f"✅ {count_before} employé(s) supprimé(s)")
            print(f"📊 {count_after} employé(s) restant(s)")
        else:
            print("ℹ️ Aucun employé à supprimer")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def verify_local_employees():
    """Vérifier l'état de la base locale"""
    
    db_path = "data/construction_projects_local.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de données locale non trouvée")
        return
    
    print("\n🔍 VÉRIFICATION BASE LOCALE")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Compter les employés
        cursor.execute("SELECT COUNT(*) FROM employes")
        count = cursor.fetchone()[0]
        
        print(f"👥 {count} employé(s) dans la base locale")
        
        if count > 0:
            cursor.execute("SELECT id_employe, prenom, nom, poste, taux_horaire FROM employes")
            employes = cursor.fetchall()
            
            for employe in employes:
                print(f"   👤 ID: {employe[0]} - {employe[1]} {employe[2]} ({employe[3]}) - ${employe[4]}/h")
        else:
            print("✅ Base locale vide - prête pour synchronisation avec Render")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 NETTOYAGE BASE LOCALE")
    print("⏰", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Supprimer les employés locaux
    clear_local_employees()
    
    # Vérifier l'état
    verify_local_employees()
    
    print("\n🎉 TERMINÉ!")
    print("💡 Maintenant tout se passe sur Render uniquement")
