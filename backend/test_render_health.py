#!/usr/bin/env python3
"""
Script pour tester la santé du backend Render
"""

import requests
import time

def test_render_health():
    """Tester la santé du backend Render"""
    
    base_url = "https://interface-cah-backend.onrender.com"
    
    print("🏥 Test de santé du backend Render...")
    print(f"🔗 URL: {base_url}")
    
    # Test 1: Health check
    try:
        print("\n1️⃣ Test health check...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health check OK")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Root endpoint
    try:
        print("\n2️⃣ Test root endpoint...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Root endpoint OK")
        else:
            print(f"   ❌ Root endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test 3: API endpoint
    try:
        print("\n3️⃣ Test API endpoint...")
        response = requests.get(f"{base_url}/api/tenants", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API endpoint OK")
        else:
            print(f"   ❌ API endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ API endpoint error: {e}")

if __name__ == "__main__":
    test_render_health()
