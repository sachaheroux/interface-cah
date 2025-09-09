#!/bin/bash
# Script de test API avec curl
# Usage: bash test_api_curl.sh

API_BASE="http://localhost:8000"

echo "🧪 TEST API SQLITE AVEC CURL"
echo "=============================="

# Test 1: Santé du serveur
echo "1. Test de santé du serveur..."
curl -s "$API_BASE/health" | jq '.' || echo "❌ Serveur non accessible"

# Test 2: Récupérer les immeubles
echo -e "\n2. Test GET /api/buildings..."
curl -s "$API_BASE/api/buildings" | jq 'length' || echo "❌ Erreur"

# Test 3: Récupérer les constantes de factures
echo -e "\n3. Test GET /api/invoices/constants..."
curl -s "$API_BASE/api/invoices/constants" | jq '.categories | length' || echo "❌ Erreur"

# Test 4: Créer un immeuble de test
echo -e "\n4. Test POST /api/buildings..."
BUILDING_ID=$(curl -s -X POST "$API_BASE/api/buildings" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Curl Building",
    "address": {
      "street": "123 Test St",
      "city": "Montreal",
      "province": "QC",
      "postalCode": "H1A 1A1",
      "country": "Canada"
    },
    "type": "Residential",
    "units": 3,
    "floors": 2,
    "yearBuilt": 2023,
    "notes": "Test building via curl"
  }' | jq -r '.id')

if [ "$BUILDING_ID" != "null" ] && [ "$BUILDING_ID" != "" ]; then
  echo "✅ Immeuble créé avec ID: $BUILDING_ID"
  
  # Test 5: Récupérer l'immeuble créé
  echo -e "\n5. Test GET /api/buildings/$BUILDING_ID..."
  curl -s "$API_BASE/api/buildings/$BUILDING_ID" | jq '.name' || echo "❌ Erreur"
  
  # Test 6: Mettre à jour l'immeuble
  echo -e "\n6. Test PUT /api/buildings/$BUILDING_ID..."
  curl -s -X PUT "$API_BASE/api/buildings/$BUILDING_ID" \
    -H "Content-Type: application/json" \
    -d '{"name": "Test Curl Building Updated"}' | jq '.name' || echo "❌ Erreur"
  
  # Test 7: Supprimer l'immeuble
  echo -e "\n7. Test DELETE /api/buildings/$BUILDING_ID..."
  curl -s -X DELETE "$API_BASE/api/buildings/$BUILDING_ID" | jq '.message' || echo "❌ Erreur"
else
  echo "❌ Échec de création de l'immeuble"
fi

# Test 8: Créer une facture de test
echo -e "\n8. Test POST /api/invoices..."
INVOICE_ID=$(curl -s -X POST "$API_BASE/api/invoices" \
  -H "Content-Type: application/json" \
  -d "{
    \"invoiceNumber\": \"CURL-TEST-$(date +%s)\",
    \"category\": \"municipal_taxes\",
    \"source\": \"Test City\",
    \"date\": \"$(date -I)\",
    \"amount\": 999.99,
    \"currency\": \"CAD\",
    \"paymentType\": \"bank_transfer\",
    \"notes\": \"Test invoice via curl\"
  }" | jq -r '.data.id')

if [ "$INVOICE_ID" != "null" ] && [ "$INVOICE_ID" != "" ]; then
  echo "✅ Facture créée avec ID: $INVOICE_ID"
  
  # Test 9: Récupérer la facture créée
  echo -e "\n9. Test GET /api/invoices/$INVOICE_ID..."
  curl -s "$API_BASE/api/invoices/$INVOICE_ID" | jq '.data.invoiceNumber' || echo "❌ Erreur"
else
  echo "❌ Échec de création de la facture"
fi

echo -e "\n🎉 Tests terminés !"
