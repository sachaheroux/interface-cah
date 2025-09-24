#!/usr/bin/env python3
"""
Script pour diagnostiquer les données de rentabilité via l'API Render
"""

import requests
import json
from datetime import datetime

def debug_profitability_data():
    """Diagnostiquer les données de rentabilité via l'API Render"""
    
    print("🔍 DIAGNOSTIC DES DONNÉES DE RENTABILITÉ (RENDER)")
    print("=" * 50)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        # 1. Vérifier les immeubles
        print("\n1. IMMEUBLES DISPONIBLES:")
        response = requests.get(f"{base_url}/buildings")
        if response.status_code == 200:
            buildings = response.json()
            print(f"   Nombre total d'immeubles: {len(buildings)}")
            for i, building in enumerate(buildings[:5]):
                print(f"   ID: {building.get('id_immeuble')}, Nom: {building.get('nom_immeuble')}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # 2. Vérifier les transactions pour l'immeuble ID 1
        print(f"\n2. TRANSACTIONS POUR L'IMMEUBLE ID 1:")
        response = requests.get(f"{base_url}/transactions")
        if response.status_code == 200:
            transactions_data = response.json()
            print(f"   Type de données reçues: {type(transactions_data)}")
            print(f"   Clés disponibles: {list(transactions_data.keys()) if isinstance(transactions_data, dict) else 'N/A'}")
            
            # Si c'est un dictionnaire avec une clé 'data' ou 'transactions'
            if isinstance(transactions_data, dict):
                if 'data' in transactions_data:
                    transactions = transactions_data['data']
                elif 'transactions' in transactions_data:
                    transactions = transactions_data['transactions']
                else:
                    transactions = list(transactions_data.values())[0] if transactions_data else []
            else:
                transactions = transactions_data
            
            print(f"   Nombre total de transactions: {len(transactions)}")
            
            if isinstance(transactions, list) and transactions:
                building_1_transactions = [t for t in transactions if isinstance(t, dict) and t.get('id_immeuble') == 1]
                print(f"   Nombre de transactions trouvées pour l'immeuble 1: {len(building_1_transactions)}")
                for transaction in building_1_transactions[:5]:
                    print(f"   ID: {transaction.get('id_transaction')}, Immeuble: {transaction.get('id_immeuble')}, Catégorie: {transaction.get('categorie')}, Montant: {transaction.get('montant')}, Date: {transaction.get('date_de_transaction')}")
            else:
                print(f"   Format de données inattendu: {transactions}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # 3. Vérifier les baux pour l'immeuble ID 1
        print(f"\n3. BAUX POUR L'IMMEUBLE ID 1:")
        response = requests.get(f"{base_url}/leases")
        if response.status_code == 200:
            leases_data = response.json()
            print(f"   Type de données reçues: {type(leases_data)}")
            
            # Si c'est un dictionnaire avec une clé 'data' ou 'leases'
            if isinstance(leases_data, dict):
                if 'data' in leases_data:
                    leases = leases_data['data']
                elif 'leases' in leases_data:
                    leases = leases_data['leases']
                else:
                    leases = list(leases_data.values())[0] if leases_data else []
            else:
                leases = leases_data
            
            print(f"   Nombre total de baux: {len(leases)}")
            
            if isinstance(leases, list) and leases:
                building_1_leases = [l for l in leases if isinstance(l, dict) and l.get('id_immeuble') == 1]
                print(f"   Nombre de baux trouvés pour l'immeuble 1: {len(building_1_leases)}")
                for lease in building_1_leases[:5]:
                    print(f"   ID: {lease.get('id_bail')}, Immeuble: {lease.get('id_immeuble')}, Prix: {lease.get('prix_loyer')}, Début: {lease.get('date_debut')}, Fin: {lease.get('date_fin')}")
            else:
                print(f"   Format de données inattendu: {leases}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # 4. Vérifier les transactions dans la période juillet 2025 - juin 2026
        print(f"\n4. TRANSACTIONS DANS LA PÉRIODE JUILLET 2025 - JUIN 2026:")
        response = requests.get(f"{base_url}/transactions")
        if response.status_code == 200:
            transactions = response.json()
            period_transactions = []
            for transaction in transactions:
                date_str = transaction.get('date_de_transaction')
                if date_str:
                    try:
                        trans_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        if trans_date >= datetime(2025, 7, 1) and trans_date <= datetime(2026, 6, 30):
                            period_transactions.append(transaction)
                    except:
                        pass
            
            print(f"   Nombre de transactions dans la période: {len(period_transactions)}")
            for transaction in period_transactions[:5]:
                print(f"   ID: {transaction.get('id_transaction')}, Immeuble: {transaction.get('id_immeuble')}, Catégorie: {transaction.get('categorie')}, Montant: {transaction.get('montant')}, Date: {transaction.get('date_de_transaction')}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # 5. Tester l'API d'analyse de rentabilité
        print(f"\n5. TEST DE L'API D'ANALYSE DE RENTABILITÉ:")
        response = requests.get(f"{base_url}/analysis/profitability?building_ids=1&start_year=2025&start_month=7&end_year=2026&end_month=6")
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"   ✅ API d'analyse fonctionne")
            print(f"   Nombre d'immeubles dans l'analyse: {len(analysis_data.get('buildings', []))}")
            print(f"   Nombre de mois dans l'analyse: {len(analysis_data.get('monthlyTotals', []))}")
            
            # Afficher les données détaillées
            if analysis_data.get('buildings'):
                print(f"   Immeubles trouvés: {[b.get('name', 'N/A') for b in analysis_data['buildings']]}")
            if analysis_data.get('monthlyTotals'):
                print(f"   Premier mois: {analysis_data['monthlyTotals'][0]}")
        else:
            print(f"   ❌ Erreur API d'analyse: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
        # 6. Tester avec plusieurs immeubles
        print(f"\n6. TEST AVEC PLUSIEURS IMMEUBLES:")
        response = requests.get(f"{base_url}/analysis/profitability?building_ids=1,2&start_year=2025&start_month=7&end_year=2026&end_month=6")
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"   ✅ API d'analyse avec plusieurs immeubles fonctionne")
            print(f"   Nombre d'immeubles: {len(analysis_data.get('buildings', []))}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            print(f"   Réponse: {response.text}")
                
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_profitability_data()
