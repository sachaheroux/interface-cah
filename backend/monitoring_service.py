#!/usr/bin/env python3
"""
Service de monitoring de la santé de la base de données pour Interface CAH
"""

import os
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import threading
import json

from database import db_manager, DATABASE_PATH
from database_service_francais import db_service_francais as db_service
from validation_service import data_validator, ValidationLevel

class HealthStatus(Enum):
    """Statuts de santé de la base de données"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"

@dataclass
class DatabaseMetrics:
    """Métriques de la base de données"""
    timestamp: datetime
    file_size: int
    record_counts: Dict[str, int]
    connection_count: int
    response_time: float
    memory_usage: float
    disk_usage: float
    health_score: int
    status: HealthStatus

@dataclass
class SystemMetrics:
    """Métriques du système"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    available_memory: int
    available_disk: int

class DatabaseMonitor:
    """Moniteur de santé de la base de données"""
    
    def __init__(self):
        self.metrics_history: List[DatabaseMetrics] = []
        self.system_history: List[SystemMetrics] = []
        self.max_history = 1000  # Garder 1000 points de données
        self.monitoring_active = False
        self.monitor_thread = None
        self.alert_thresholds = {
            "response_time": 5.0,  # secondes
            "memory_usage": 80.0,  # pourcentage
            "disk_usage": 90.0,    # pourcentage
            "health_score": 70     # score minimum
        }
    
    def get_database_metrics(self) -> DatabaseMetrics:
        """Obtenir les métriques actuelles de la base de données"""
        try:
            start_time = time.time()
            
            # Taille du fichier de base de données
            file_size = 0
            if os.path.exists(DATABASE_PATH):
                file_size = os.path.getsize(DATABASE_PATH)
            
            # Compter les enregistrements
            record_counts = self._get_record_counts()
            
            # Temps de réponse
            response_time = time.time() - start_time
            
            # Utilisation mémoire
            memory_usage = psutil.virtual_memory().percent
            
            # Utilisation disque
            disk_usage = psutil.disk_usage(os.path.dirname(DATABASE_PATH)).percent
            
            # Score de santé
            health_score = self._calculate_health_score(record_counts, response_time, memory_usage, disk_usage)
            
            # Statut de santé
            status = self._determine_health_status(health_score, response_time, memory_usage, disk_usage)
            
            metrics = DatabaseMetrics(
                timestamp=datetime.now(),
                file_size=file_size,
                record_counts=record_counts,
                connection_count=1,  # SQLite n'a pas de compteur de connexions
                response_time=response_time,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                health_score=health_score,
                status=status
            )
            
            return metrics
            
        except Exception as e:
            print(f"❌ Erreur lors de la collecte des métriques: {e}")
            return DatabaseMetrics(
                timestamp=datetime.now(),
                file_size=0,
                record_counts={},
                connection_count=0,
                response_time=999.0,
                memory_usage=100.0,
                disk_usage=100.0,
                health_score=0,
                status=HealthStatus.DOWN
            )
    
    def get_system_metrics(self) -> SystemMetrics:
        """Obtenir les métriques du système"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                available_memory=memory.available,
                available_disk=disk.free
            )
            
        except Exception as e:
            print(f"❌ Erreur lors de la collecte des métriques système: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=100.0,
                memory_percent=100.0,
                disk_percent=100.0,
                available_memory=0,
                available_disk=0
            )
    
    def _get_record_counts(self) -> Dict[str, int]:
        """Compter les enregistrements dans chaque table"""
        counts = {}
        
        try:
            # Tables principales
            tables = ['buildings', 'tenants', 'assignments', 'building_reports', 'unit_reports', 'invoices']
            
            for table in tables:
                try:
                    if table == 'buildings':
                        records = db_service.get_buildings()
                    elif table == 'tenants':
                        records = db_service.get_tenants()
                    elif table == 'assignments':
                        records = db_service.get_assignments()
                    elif table == 'building_reports':
                        records = db_service.get_building_reports()
                    elif table == 'unit_reports':
                        records = db_service.get_unit_reports()
                    elif table == 'invoices':
                        records = db_service.get_invoices()
                    else:
                        records = []
                    
                    counts[table] = len(records) if records else 0
                    
                except Exception as e:
                    print(f"⚠️ Erreur comptage table {table}: {e}")
                    counts[table] = 0
            
        except Exception as e:
            print(f"❌ Erreur lors du comptage des enregistrements: {e}")
        
        return counts
    
    def _calculate_health_score(self, record_counts: Dict[str, int], response_time: float, memory_usage: float, disk_usage: float) -> int:
        """Calculer un score de santé global (0-100)"""
        try:
            score = 100
            
            # Pénalité pour le temps de réponse
            if response_time > 1.0:
                score -= min(30, (response_time - 1.0) * 10)
            
            # Pénalité pour l'utilisation mémoire
            if memory_usage > 70:
                score -= (memory_usage - 70) * 0.5
            
            # Pénalité pour l'utilisation disque
            if disk_usage > 80:
                score -= (disk_usage - 80) * 0.3
            
            # Bonus pour avoir des données
            total_records = sum(record_counts.values())
            if total_records > 0:
                score += min(10, total_records / 10)
            
            # Validation des données
            validation_results = data_validator.validate_all()
            error_count = len([r for r in validation_results if r.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL]])
            if error_count > 0:
                score -= min(20, error_count * 2)
            
            return max(0, min(100, int(score)))
            
        except Exception as e:
            print(f"❌ Erreur calcul score de santé: {e}")
            return 0
    
    def _determine_health_status(self, health_score: int, response_time: float, memory_usage: float, disk_usage: float) -> HealthStatus:
        """Déterminer le statut de santé global"""
        if health_score >= 90 and response_time < 1.0 and memory_usage < 70:
            return HealthStatus.EXCELLENT
        elif health_score >= 80 and response_time < 2.0 and memory_usage < 80:
            return HealthStatus.GOOD
        elif health_score >= 60 and response_time < 5.0 and memory_usage < 90:
            return HealthStatus.WARNING
        elif health_score >= 30:
            return HealthStatus.CRITICAL
        else:
            return HealthStatus.DOWN
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Obtenir un résumé de la santé de la base de données"""
        try:
            # Métriques actuelles
            db_metrics = self.get_database_metrics()
            system_metrics = self.get_system_metrics()
            
            # Validation des données
            validation_results = data_validator.validate_all()
            validation_counts = {
                "info": len([r for r in validation_results if r.level == ValidationLevel.INFO]),
                "warning": len([r for r in validation_results if r.level == ValidationLevel.WARNING]),
                "error": len([r for r in validation_results if r.level == ValidationLevel.ERROR]),
                "critical": len([r for r in validation_results if r.level == ValidationLevel.CRITICAL])
            }
            
            # Tendances (si on a des données historiques)
            trends = self._calculate_trends()
            
            # Alertes
            alerts = self._check_alerts(db_metrics, system_metrics)
            
            return {
                "timestamp": db_metrics.timestamp.isoformat(),
                "database": {
                    "status": db_metrics.status.value,
                    "health_score": db_metrics.health_score,
                    "file_size": db_metrics.file_size,
                    "file_size_mb": round(db_metrics.file_size / (1024 * 1024), 2),
                    "response_time": round(db_metrics.response_time, 3),
                    "record_counts": db_metrics.record_counts,
                    "total_records": sum(db_metrics.record_counts.values())
                },
                "system": {
                    "cpu_percent": round(system_metrics.cpu_percent, 1),
                    "memory_percent": round(system_metrics.memory_percent, 1),
                    "disk_percent": round(system_metrics.disk_percent, 1),
                    "available_memory_gb": round(system_metrics.available_memory / (1024**3), 2),
                    "available_disk_gb": round(system_metrics.available_disk / (1024**3), 2)
                },
                "validation": {
                    "total_issues": sum(validation_counts.values()),
                    "counts": validation_counts,
                    "status": "healthy" if validation_counts["error"] == 0 and validation_counts["critical"] == 0 else "issues"
                },
                "trends": trends,
                "alerts": alerts
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération du résumé: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculer les tendances basées sur l'historique"""
        if len(self.metrics_history) < 2:
            return {"status": "insufficient_data"}
        
        try:
            recent = self.metrics_history[-1]
            previous = self.metrics_history[-2]
            
            trends = {
                "health_score": {
                    "current": recent.health_score,
                    "change": recent.health_score - previous.health_score,
                    "direction": "up" if recent.health_score > previous.health_score else "down"
                },
                "response_time": {
                    "current": recent.response_time,
                    "change": recent.response_time - previous.response_time,
                    "direction": "up" if recent.response_time > previous.response_time else "down"
                },
                "file_size": {
                    "current": recent.file_size,
                    "change": recent.file_size - previous.file_size,
                    "direction": "up" if recent.file_size > previous.file_size else "down"
                }
            }
            
            return trends
            
        except Exception as e:
            print(f"❌ Erreur calcul tendances: {e}")
            return {"status": "error", "message": str(e)}
    
    def _check_alerts(self, db_metrics: DatabaseMetrics, system_metrics: SystemMetrics) -> List[Dict[str, Any]]:
        """Vérifier les alertes"""
        alerts = []
        
        try:
            # Alerte temps de réponse
            if db_metrics.response_time > self.alert_thresholds["response_time"]:
                alerts.append({
                    "level": "warning",
                    "type": "response_time",
                    "message": f"Temps de réponse élevé: {db_metrics.response_time:.2f}s",
                    "value": db_metrics.response_time,
                    "threshold": self.alert_thresholds["response_time"]
                })
            
            # Alerte utilisation mémoire
            if system_metrics.memory_percent > self.alert_thresholds["memory_usage"]:
                alerts.append({
                    "level": "warning",
                    "type": "memory_usage",
                    "message": f"Utilisation mémoire élevée: {system_metrics.memory_percent:.1f}%",
                    "value": system_metrics.memory_percent,
                    "threshold": self.alert_thresholds["memory_usage"]
                })
            
            # Alerte utilisation disque
            if system_metrics.disk_percent > self.alert_thresholds["disk_usage"]:
                alerts.append({
                    "level": "critical",
                    "type": "disk_usage",
                    "message": f"Utilisation disque élevée: {system_metrics.disk_percent:.1f}%",
                    "value": system_metrics.disk_percent,
                    "threshold": self.alert_thresholds["disk_usage"]
                })
            
            # Alerte score de santé
            if db_metrics.health_score < self.alert_thresholds["health_score"]:
                alerts.append({
                    "level": "critical",
                    "type": "health_score",
                    "message": f"Score de santé faible: {db_metrics.health_score}",
                    "value": db_metrics.health_score,
                    "threshold": self.alert_thresholds["health_score"]
                })
            
            # Alerte statut critique
            if db_metrics.status == HealthStatus.CRITICAL:
                alerts.append({
                    "level": "critical",
                    "type": "database_status",
                    "message": "Base de données en état critique",
                    "value": db_metrics.status.value
                })
            
        except Exception as e:
            print(f"❌ Erreur vérification alertes: {e}")
        
        return alerts
    
    def start_monitoring(self, interval: int = 60):
        """Démarrer le monitoring automatique"""
        if self.monitoring_active:
            print("⚠️ Le monitoring est déjà actif")
            return
        
        print(f"🔄 Démarrage du monitoring (intervalle: {interval}s)")
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_worker, args=(interval,), daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Arrêter le monitoring automatique"""
        if not self.monitoring_active:
            print("⚠️ Le monitoring n'est pas actif")
            return
        
        print("🛑 Arrêt du monitoring")
        self.monitoring_active = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
    
    def _monitoring_worker(self, interval: int):
        """Worker thread pour le monitoring"""
        while self.monitoring_active:
            try:
                # Collecter les métriques
                db_metrics = self.get_database_metrics()
                system_metrics = self.get_system_metrics()
                
                # Ajouter à l'historique
                self.metrics_history.append(db_metrics)
                self.system_history.append(system_metrics)
                
                # Limiter la taille de l'historique
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history = self.metrics_history[-self.max_history:]
                if len(self.system_history) > self.max_history:
                    self.system_history = self.system_history[-self.max_history:]
                
                # Vérifier les alertes
                alerts = self._check_alerts(db_metrics, system_metrics)
                if alerts:
                    print(f"🚨 {len(alerts)} alerte(s) détectée(s)")
                    for alert in alerts:
                        print(f"   {alert['level'].upper()}: {alert['message']}")
                
                # Attendre l'intervalle
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ Erreur dans le worker de monitoring: {e}")
                time.sleep(interval)
    
    def get_metrics_history(self, hours: int = 24) -> Dict[str, List[Dict]]:
        """Obtenir l'historique des métriques"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            db_history = [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "health_score": m.health_score,
                    "status": m.status.value,
                    "response_time": m.response_time,
                    "file_size": m.file_size,
                    "record_counts": m.record_counts
                }
                for m in self.metrics_history
                if m.timestamp >= cutoff_time
            ]
            
            system_history = [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "disk_percent": m.disk_percent
                }
                for m in self.system_history
                if m.timestamp >= cutoff_time
            ]
            
            return {
                "database": db_history,
                "system": system_history,
                "period_hours": hours
            }
            
        except Exception as e:
            print(f"❌ Erreur récupération historique: {e}")
            return {"error": str(e)}

# Instance globale du moniteur
database_monitor = DatabaseMonitor()

def get_database_monitor():
    """Obtenir l'instance du moniteur de base de données"""
    return database_monitor
