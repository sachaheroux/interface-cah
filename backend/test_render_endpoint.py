"""
Script pour tester les endpoints Render
"""
import requests

RENDER_URL = "https://interface-cah.onrender.com"

def test_endpoints():
    """Tester différents endpoints"""
    print("=" * 80)
    print("🧪 TEST DES ENDPOINTS RENDER")
    print("=" * 80)
    
    # Test 1: Health check
    print("\n1️⃣ Test /health")
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ {response.json()}")
    except Exception as e:
        print(f"   ❌ {e}")
    
    # Test 2: Root
    print("\n2️⃣ Test /")
    try:
        response = requests.get(f"{RENDER_URL}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ {response.json()}")
    except Exception as e:
        print(f"   ❌ {e}")
    
    # Test 3: Buildings
    print("\n3️⃣ Test /api/buildings")
    try:
        response = requests.get(f"{RENDER_URL}/api/buildings", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            buildings = response.json()
            print(f"   ✅ {len(buildings)} immeubles")
    except Exception as e:
        print(f"   ❌ {e}")
    
    # Test 4: Clear paiements (DELETE)
    print("\n4️⃣ Test DELETE /api/paiements-loyers/clear-all")
    try:
        response = requests.delete(f"{RENDER_URL}/api/paiements-loyers/clear-all", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ {response.json()}")
        else:
            print(f"   ❌ {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_endpoints()

