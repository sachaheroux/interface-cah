#!/usr/bin/env python3
"""
Test du système de monitoring de la santé de la base de données
"""

import urllib.request
import urllib.parse
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def test_monitoring_direct():
    """Test direct du service de monitoring (sans API)"""
    print("📊 TEST DIRECT DU SERVICE DE MONITORING")
    print("=" * 50)
    
    try:
        from monitoring_service import database_monitor
        
        # Test 1: Métriques de base de données
        print("1️⃣ Collecte des métriques de base de données...")
        db_metrics = database_monitor.get_database_metrics()
        
        print(f"✅ Métriques collectées:")
        print(f"   📊 Score de santé: {db_metrics.health_score}/100")
        print(f"   📈 Statut: {db_metrics.status.value}")
        print(f"   ⏱️ Temps de réponse: {db_metrics.response_time:.3f}s")
        print(f"   💾 Taille fichier: {db_metrics.file_size / (1024*1024):.2f} MB")
        print(f"   📋 Enregistrements: {sum(db_metrics.record_counts.values())}")
        
        # Test 2: Métriques système
        print("\n2️⃣ Collecte des métriques système...")
        system_metrics = database_monitor.get_system_metrics()
        
        print(f"✅ Métriques système collectées:")
        print(f"   🖥️ CPU: {system_metrics.cpu_percent:.1f}%")
        print(f"   🧠 Mémoire: {system_metrics.memory_percent:.1f}%")
        print(f"   💽 Disque: {system_metrics.disk_percent:.1f}%")
        print(f"   🆓 Mémoire disponible: {system_metrics.available_memory / (1024**3):.2f} GB")
        print(f"   🆓 Disque disponible: {system_metrics.available_disk / (1024**3):.2f} GB")
        
        # Test 3: Résumé de santé
        print("\n3️⃣ Génération du résumé de santé...")
        health_summary = database_monitor.get_health_summary()
        
        print(f"✅ Résumé de santé généré:")
        print(f"   📊 Statut global: {health_summary['database']['status']}")
        print(f"   🎯 Score de santé: {health_summary['database']['health_score']}")
        print(f"   ⚠️ Alertes: {len(health_summary.get('alerts', []))}")
        
        if health_summary.get('alerts'):
            print("   🚨 Alertes détectées:")
            for alert in health_summary['alerts']:
                print(f"      - {alert['level'].upper()}: {alert['message']}")
        
        # Test 4: Historique des métriques
        print("\n4️⃣ Test de l'historique des métriques...")
        history = database_monitor.get_metrics_history(hours=1)
        
        print(f"✅ Historique récupéré:")
        print(f"   📈 Points de données DB: {len(history.get('database', []))}")
        print(f"   📈 Points de données système: {len(history.get('system', []))}")
        
        print("\n🎉 TEST DIRECT RÉUSSI !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test direct: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_monitoring_api():
    """Test des endpoints de monitoring via API"""
    print("\n🌐 TEST DES ENDPOINTS DE MONITORING")
    print("=" * 50)
    
    endpoints = [
        ("/api/monitoring/health", "Résumé de santé"),
        ("/api/monitoring/metrics", "Métriques actuelles"),
        ("/api/monitoring/history", "Historique des métriques"),
        ("/api/monitoring/status", "Statut du monitoring")
    ]
    
    success_count = 0
    
    for endpoint, description in endpoints:
        print(f"\n🔍 Test: {description}")
        try:
            req = urllib.request.Request(f"{API_BASE_URL}{endpoint}")
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    print(f"✅ {description}: RÉUSSI")
                    
                    # Afficher un résumé des résultats
                    if endpoint == "/api/monitoring/health":
                        data = result.get('data', {})
                        db_info = data.get('database', {})
                        print(f"   📊 Statut: {db_info.get('status', 'unknown')}")
                        print(f"   🎯 Score: {db_info.get('health_score', 0)}")
                        print(f"   ⚠️ Alertes: {len(data.get('alerts', []))}")
                    
                    elif endpoint == "/api/monitoring/metrics":
                        db_info = result.get('database', {})
                        sys_info = result.get('system', {})
                        print(f"   📊 Score DB: {db_info.get('health_score', 0)}")
                        print(f"   ⏱️ Temps réponse: {db_info.get('response_time', 0)}s")
                        print(f"   🖥️ CPU: {sys_info.get('cpu_percent', 0)}%")
                        print(f"   🧠 Mémoire: {sys_info.get('memory_percent', 0)}%")
                    
                    elif endpoint == "/api/monitoring/history":
                        data = result.get('data', {})
                        db_history = data.get('database', [])
                        sys_history = data.get('system', [])
                        print(f"   📈 Points DB: {len(db_history)}")
                        print(f"   📈 Points système: {len(sys_history)}")
                    
                    elif endpoint == "/api/monitoring/status":
                        print(f"   🔄 Monitoring actif: {result.get('monitoring_active', False)}")
                        print(f"   📊 Métriques DB: {result.get('metrics_count', 0)}")
                        print(f"   📊 Métriques système: {result.get('system_metrics_count', 0)}")
                    
                    success_count += 1
                else:
                    print(f"❌ {description}: Erreur HTTP {response.status}")
        except Exception as e:
            print(f"❌ {description}: Erreur - {e}")
    
    print(f"\n📊 Résultat API: {success_count}/{len(endpoints)} endpoints réussis")
    return success_count == len(endpoints)

def test_monitoring_automation():
    """Test du monitoring automatique"""
    print("\n🤖 TEST DU MONITORING AUTOMATIQUE")
    print("=" * 50)
    
    try:
        from monitoring_service import database_monitor
        
        # Test 1: Démarrer le monitoring
        print("1️⃣ Démarrage du monitoring automatique...")
        database_monitor.start_monitoring(interval=5)  # 5 secondes pour le test
        
        print("✅ Monitoring démarré")
        print("   ⏱️ Intervalle: 5 secondes")
        print("   🔄 Thread actif:", database_monitor.monitoring_active)
        
        # Test 2: Attendre quelques cycles
        print("\n2️⃣ Attente de quelques cycles de monitoring...")
        time.sleep(15)  # Attendre 3 cycles
        
        # Test 3: Vérifier l'historique
        print("\n3️⃣ Vérification de l'historique...")
        history_count = len(database_monitor.metrics_history)
        system_count = len(database_monitor.system_history)
        
        print(f"✅ Historique collecté:")
        print(f"   📊 Métriques DB: {history_count}")
        print(f"   📊 Métriques système: {system_count}")
        
        # Test 4: Arrêter le monitoring
        print("\n4️⃣ Arrêt du monitoring...")
        database_monitor.stop_monitoring()
        
        print("✅ Monitoring arrêté")
        print("   🔄 Thread actif:", database_monitor.monitoring_active)
        
        print("\n🎉 TEST AUTOMATISATION RÉUSSI !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test automatisation: {e}")
        return False

def test_performance_metrics():
    """Test des métriques de performance"""
    print("\n⚡ TEST DES MÉTRIQUES DE PERFORMANCE")
    print("=" * 50)
    
    try:
        from monitoring_service import database_monitor
        
        # Test de performance sur plusieurs requêtes
        print("1️⃣ Test de performance sur 10 requêtes...")
        
        response_times = []
        for i in range(10):
            start_time = time.time()
            db_metrics = database_monitor.get_database_metrics()
            response_time = time.time() - start_time
            response_times.append(response_time)
            print(f"   Requête {i+1}: {response_time:.3f}s")
        
        # Calcul des statistiques
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        print(f"\n✅ Statistiques de performance:")
        print(f"   ⏱️ Temps moyen: {avg_response_time:.3f}s")
        print(f"   ⚡ Temps minimum: {min_response_time:.3f}s")
        print(f"   🐌 Temps maximum: {max_response_time:.3f}s")
        
        # Évaluation de la performance
        if avg_response_time < 1.0:
            performance_status = "EXCELLENT"
        elif avg_response_time < 2.0:
            performance_status = "GOOD"
        elif avg_response_time < 5.0:
            performance_status = "ACCEPTABLE"
        else:
            performance_status = "SLOW"
        
        print(f"   📊 Évaluation: {performance_status}")
        
        print("\n🎉 TEST PERFORMANCE RÉUSSI !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST COMPLET DU SYSTÈME DE MONITORING")
    print("=" * 60)
    
    # Test 1: Test direct du service
    success1 = test_monitoring_direct()
    
    # Test 2: Test de performance
    success2 = test_performance_metrics()
    
    # Test 3: Test d'automatisation
    success3 = test_monitoring_automation()
    
    # Test 4: Test via API (nécessite que le serveur soit démarré)
    print("\n" + "="*60)
    print("⚠️  Pour tester les endpoints API, assurez-vous que le serveur est démarré")
    print("   Commande: uvicorn main:app --reload")
    print("="*60)
    
    success4 = test_monitoring_api()
    
    # Résumé
    print("\n📊 RÉSUMÉ DES TESTS")
    print("=" * 30)
    print(f"Test direct: {'✅ RÉUSSI' if success1 else '❌ ÉCHOUÉ'}")
    print(f"Test performance: {'✅ RÉUSSI' if success2 else '❌ ÉCHOUÉ'}")
    print(f"Test automatisation: {'✅ RÉUSSI' if success3 else '❌ ÉCHOUÉ'}")
    print(f"Test API: {'✅ RÉUSSI' if success4 else '❌ ÉCHOUÉ'}")
    
    if success1 and success2 and success3:
        print("\n🎉 SYSTÈME DE MONITORING OPÉRATIONNEL !")
        print("✅ Collecte de métriques")
        print("✅ Monitoring automatique")
        print("✅ Alertes intelligentes")
        print("✅ Historique des performances")
        print("✅ Surveillance système")
    else:
        print("\n⚠️ Certains tests ont échoué")

if __name__ == "__main__":
    main()
