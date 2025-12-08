#!/usr/bin/env python3
"""
Script pour vérifier les baux existants sur Render avant toute action
"""

import requests
import json
from datetime import datetime

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"

def check_render_leases():
    """Vérifier les baux existants sur Render"""
    print("🌐 VÉRIFICATION DES BAUX SUR RENDER")
    print("=" * 60)
    print(f"🔗 URL: {RENDER_URL}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 1. Vérifier la santé de l'API
        print("\n🏥 1. VÉRIFICATION DE LA SANTÉ DE L'API:")
        try:
            health_response = requests.get(f"{RENDER_URL}/api/health", timeout=10)
            if health_response.status_code == 200:
                print("   ✅ API Render accessible")
            else:
                print(f"   ⚠️ API Render répond avec code: {health_response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur de connexion à l'API: {e}")
            return False
        
        # 2. Récupérer tous les baux
        print("\n📋 2. RÉCUPÉRATION DES BAUX:")
        try:
            leases_response = requests.get(f"{RENDER_URL}/api/leases", timeout=30)
            print(f"   Status Code: {leases_response.status_code}")
            
            if leases_response.status_code == 200:
                leases_data = leases_response.json()
                print(f"   Response Keys: {list(leases_data.keys())}")
                
                if 'data' in leases_data:
                    leases = leases_data['data']
                    print(f"   📊 Nombre de baux trouvés: {len(leases)}")
                    
                    if leases:
                        print("\n   📝 DÉTAILS DES BAUX:")
                        for i, lease in enumerate(leases, 1):
                            print(f"   {i}. ID: {lease.get('id_bail', 'N/A')}")
                            print(f"      Locataire ID: {lease.get('id_locataire', 'N/A')}")
                            print(f"      Prix: {lease.get('prix_loyer', 0)}$")
                            print(f"      Début: {lease.get('date_debut', 'N/A')}")
                            print(f"      Fin: {lease.get('date_fin', 'N/A')}")
                            print(f"      PDF: {lease.get('pdf_bail', 'Aucun')}")
                            print(f"      Créé: {lease.get('date_creation', 'N/A')}")
                            print()
                    else:
                        print("   ❌ Aucun bail trouvé dans la réponse")
                else:
                    print(f"   ⚠️ Structure de réponse inattendue: {leases_data}")
            else:
                print(f"   ❌ Erreur HTTP {leases_response.status_code}")
                print(f"   Response: {leases_response.text}")
                
        except Exception as e:
            print(f"   ❌ Erreur lors de la récupération des baux: {e}")
            return False
        
        # 3. Vérifier les paiements associés
        print("\n💰 3. VÉRIFICATION DES PAIEMENTS:")
        try:
            # Essayer de récupérer les paiements (si l'endpoint existe)
            payments_response = requests.get(f"{RENDER_URL}/api/paiements-loyers", timeout=30)
            if payments_response.status_code == 200:
                payments_data = payments_response.json()
                if 'data' in payments_data:
                    payments = payments_data['data']
                    print(f"   📊 Nombre de paiements trouvés: {len(payments)}")
                    
                    if payments:
                        print("\n   📝 DÉTAILS DES PAIEMENTS:")
                        for i, payment in enumerate(payments, 1):
                            print(f"   {i}. ID: {payment.get('id_paiement', 'N/A')}")
                            print(f"      Bail ID: {payment.get('id_bail', 'N/A')}")
                            print(f"      Mois/Année: {payment.get('mois', 'N/A')}/{payment.get('annee', 'N/A')}")
                            print(f"      Montant: {payment.get('montant_paye', 0)}$")
                            print(f"      Payé: {payment.get('paye', False)}")
                            print()
                    else:
                        print("   ❌ Aucun paiement trouvé")
                else:
                    print(f"   ⚠️ Structure de réponse paiements inattendue: {payments_data}")
            else:
                print(f"   ⚠️ Endpoint paiements non disponible (code: {payments_response.status_code})")
                
        except Exception as e:
            print(f"   ⚠️ Erreur lors de la vérification des paiements: {e}")
        
        # 4. Vérifier les locataires associés
        print("\n👥 4. VÉRIFICATION DES LOCATAIRES:")
        try:
            tenants_response = requests.get(f"{RENDER_URL}/api/tenants", timeout=30)
            if tenants_response.status_code == 200:
                tenants_data = tenants_response.json()
                if 'data' in tenants_data:
                    tenants = tenants_data['data']
                    print(f"   📊 Nombre de locataires trouvés: {len(tenants)}")
                    
                    if tenants:
                        print("\n   📝 DÉTAILS DES LOCATAIRES:")
                        for i, tenant in enumerate(tenants, 1):
                            print(f"   {i}. ID: {tenant.get('id_locataire', 'N/A')}")
                            print(f"      Nom: {tenant.get('nom', 'N/A')} {tenant.get('prenom', 'N/A')}")
                            print(f"      Email: {tenant.get('email', 'N/A')}")
                            print(f"      Téléphone: {tenant.get('telephone', 'N/A')}")
                            print()
                    else:
                        print("   ❌ Aucun locataire trouvé")
                else:
                    print(f"   ⚠️ Structure de réponse locataires inattendue: {tenants_data}")
            else:
                print(f"   ❌ Erreur HTTP {tenants_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erreur lors de la vérification des locataires: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

def download_render_leases():
    """Télécharger les baux de Render vers le local pour inspection"""
    print("\n📥 TÉLÉCHARGEMENT DES BAUX POUR INSPECTION LOCALE")
    print("=" * 60)
    
    try:
        leases_response = requests.get(f"{RENDER_URL}/api/leases", timeout=30)
        if leases_response.status_code == 200:
            leases_data = leases_response.json()
            
            if 'data' in leases_data and leases_data['data']:
                # Sauvegarder dans un fichier JSON pour inspection
                filename = f"render_leases_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(leases_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Données sauvegardées dans: {filename}")
                print(f"📊 {len(leases_data['data'])} baux téléchargés")
                
                return filename
            else:
                print("❌ Aucune donnée à télécharger")
                return None
        else:
            print(f"❌ Erreur lors du téléchargement: {leases_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        return None

def main():
    """Fonction principale"""
    print("🔍 SCRIPT DE VÉRIFICATION DES BAUX SUR RENDER")
    print("=" * 60)
    
    # Vérifier les données sur Render
    if check_render_leases():
        print("\n✅ VÉRIFICATION TERMINÉE")
        
        # Proposer de télécharger les données
        download_response = input("\n❓ Voulez-vous télécharger les baux pour inspection locale ? (oui/non): ")
        if download_response.lower() in ['oui', 'o', 'yes', 'y']:
            download_render_leases()
    else:
        print("\n❌ ÉCHEC DE LA VÉRIFICATION")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Script interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

