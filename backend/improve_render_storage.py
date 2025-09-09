#!/usr/bin/env python3
"""
Améliorations pour le système de stockage Render existant
Ces améliorations s'ajoutent au système actuel sans le casser
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List

def create_backup(data_dir: str) -> str:
    """Créer une sauvegarde des données avant modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(data_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_info = {
        "timestamp": timestamp,
        "files_backed_up": []
    }
    
    data_files = [
        "buildings_data.json",
        "tenants_data.json", 
        "assignments_data.json",
        "building_reports_data.json",
        "unit_reports_data.json",
        "invoices_data.json"
    ]
    
    for filename in data_files:
        source_file = os.path.join(data_dir, filename)
        if os.path.exists(source_file):
            backup_file = os.path.join(backup_dir, f"{filename}_{timestamp}")
            shutil.copy2(source_file, backup_file)
            backup_info["files_backed_up"].append(filename)
    
    # Sauvegarder les métadonnées de backup
    backup_meta_file = os.path.join(backup_dir, f"backup_meta_{timestamp}.json")
    with open(backup_meta_file, 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Sauvegarde créée: {backup_dir}")
    return backup_dir

def atomic_save(data: Dict[str, Any], filepath: str) -> bool:
    """Sauvegarde atomique - évite la corruption des données"""
    temp_file = filepath + ".tmp"
    try:
        # Écrire d'abord dans un fichier temporaire
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Renommer seulement si l'écriture a réussi
        os.rename(temp_file, filepath)
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde atomique: {e}")
        # Nettoyer le fichier temporaire en cas d'erreur
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

def validate_data_consistency(data_dir: str) -> Dict[str, List[str]]:
    """Valider la cohérence des données entre les fichiers"""
    issues = {
        "orphaned_assignments": [],
        "missing_buildings": [],
        "missing_tenants": [],
        "invalid_references": []
    }
    
    try:
        # Charger toutes les données
        buildings_data = load_json_file(os.path.join(data_dir, "buildings_data.json"))
        tenants_data = load_json_file(os.path.join(data_dir, "tenants_data.json"))
        assignments_data = load_json_file(os.path.join(data_dir, "assignments_data.json"))
        invoices_data = load_json_file(os.path.join(data_dir, "invoices_data.json"))
        
        # Extraire les IDs
        building_ids = {b['id'] for b in buildings_data.get('buildings', [])}
        tenant_ids = {t['id'] for t in tenants_data.get('tenants', [])}
        
        # Vérifier les assignations
        for assignment in assignments_data.get('assignments', []):
            if assignment.get('buildingId') not in building_ids:
                issues["orphaned_assignments"].append(f"Assignment {assignment.get('id')} référence buildingId {assignment.get('buildingId')} inexistant")
            
            if assignment.get('tenantId') not in tenant_ids:
                issues["orphaned_assignments"].append(f"Assignment {assignment.get('id')} référence tenantId {assignment.get('tenantId')} inexistant")
        
        # Vérifier les factures
        for invoice in invoices_data.get('invoices', []):
            if invoice.get('buildingId') and invoice.get('buildingId') not in building_ids:
                issues["invalid_references"].append(f"Facture {invoice.get('id')} référence buildingId {invoice.get('buildingId')} inexistant")
        
        return issues
        
    except Exception as e:
        print(f"❌ Erreur validation cohérence: {e}")
        return issues

def load_json_file(filepath: str) -> Dict[str, Any]:
    """Charger un fichier JSON avec fallback"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Erreur chargement {filepath}: {e}")
    
    return {}

def cleanup_old_backups(data_dir: str, keep_days: int = 30):
    """Nettoyer les anciennes sauvegardes"""
    backup_dir = os.path.join(data_dir, "backups")
    if not os.path.exists(backup_dir):
        return
    
    cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
    
    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        if os.path.isfile(filepath):
            file_time = os.path.getmtime(filepath)
            if file_time < cutoff_date:
                os.remove(filepath)
                print(f"🗑️ Ancienne sauvegarde supprimée: {filename}")

def get_storage_stats(data_dir: str) -> Dict[str, Any]:
    """Obtenir des statistiques sur l'utilisation du stockage"""
    stats = {
        "total_files": 0,
        "total_size_bytes": 0,
        "file_details": {},
        "backup_count": 0
    }
    
    # Compter les fichiers de données
    data_files = [
        "buildings_data.json",
        "tenants_data.json", 
        "assignments_data.json",
        "building_reports_data.json",
        "unit_reports_data.json",
        "invoices_data.json"
    ]
    
    for filename in data_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            stats["total_files"] += 1
            stats["total_size_bytes"] += size
            stats["file_details"][filename] = {
                "size_bytes": size,
                "size_mb": round(size / (1024 * 1024), 2)
            }
    
    # Compter les sauvegardes
    backup_dir = os.path.join(data_dir, "backups")
    if os.path.exists(backup_dir):
        stats["backup_count"] = len([f for f in os.listdir(backup_dir) if f.endswith('.json')])
    
    stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)
    return stats

if __name__ == "__main__":
    # Test des améliorations
    data_dir = os.environ.get("DATA_DIR", "./data")
    
    print("🔧 Test des améliorations du stockage Render")
    print("=" * 50)
    
    # Créer une sauvegarde
    backup_dir = create_backup(data_dir)
    
    # Valider la cohérence
    issues = validate_data_consistency(data_dir)
    if any(issues.values()):
        print("⚠️ Problèmes de cohérence détectés:")
        for category, problems in issues.items():
            if problems:
                print(f"  {category}: {len(problems)} problèmes")
    else:
        print("✅ Données cohérentes")
    
    # Statistiques
    stats = get_storage_stats(data_dir)
    print(f"📊 Statistiques stockage:")
    print(f"  Fichiers: {stats['total_files']}")
    print(f"  Taille totale: {stats['total_size_mb']} MB")
    print(f"  Sauvegardes: {stats['backup_count']}")
    
    # Nettoyer les anciennes sauvegardes
    cleanup_old_backups(data_dir)
