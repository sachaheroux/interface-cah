import React, { useState } from 'react'
import { MapPin } from 'lucide-react'
import { geocodeAddress, getApproximateCoordinates } from '../services/geocoding'

export default function MapTestButton() {
  const [testing, setTesting] = useState(false)
  const [results, setResults] = useState([])

  const testAddresses = [
    { name: "Montréal Centre", address: "1000 Rue Sainte-Catherine, Montréal, QC, Canada" },
    { name: "Québec Vieux-Port", address: "400 Boulevard Jean-Lesage, Québec, QC, Canada" },
    { name: "Laval", address: "1555 Boulevard Chomedey, Laval, QC, Canada" },
    { name: "Test approximatif", address: { city: "montreal", street: "123 Test", province: "QC", country: "Canada" } }
  ]

  const runTest = async () => {
    setTesting(true)
    setResults([])
    
    console.log('🧪 Test du géocodage des adresses')
    
    for (const test of testAddresses) {
      try {
        console.log(`Testing: ${test.name}`)
        const coords = await geocodeAddress(test.address)
        
        const result = {
          name: test.name,
          address: test.address,
          coords,
          status: coords ? 'success' : 'failed'
        }
        
        console.log(`Result for ${test.name}:`, result)
        setResults(prev => [...prev, result])
        
        // Petite pause entre les requêtes
        await new Promise(resolve => setTimeout(resolve, 500))
        
      } catch (error) {
        console.error(`Error for ${test.name}:`, error)
        setResults(prev => [...prev, {
          name: test.name,
          address: test.address,
          coords: null,
          status: 'error',
          error: error.message
        }])
      }
    }
    
    setTesting(false)
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={runTest}
        disabled={testing}
        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2"
      >
        <MapPin className={`h-4 w-4 ${testing ? 'animate-spin' : ''}`} />
        <span>{testing ? 'Test en cours...' : 'Test Géocodage'}</span>
      </button>
      
      {results.length > 0 && (
        <div className="mt-2 bg-white border rounded-lg shadow-lg p-4 max-w-sm max-h-64 overflow-y-auto">
          <h4 className="font-semibold mb-2">Résultats du test :</h4>
          {results.map((result, index) => (
            <div key={index} className="mb-2 text-sm">
              <div className="flex items-center space-x-2">
                <span className={`w-2 h-2 rounded-full ${
                  result.status === 'success' ? 'bg-green-500' : 
                  result.status === 'failed' ? 'bg-yellow-500' : 'bg-red-500'
                }`}></span>
                <span className="font-medium">{result.name}</span>
              </div>
              {result.coords && (
                <div className="text-gray-600 ml-4">
                  {result.coords.lat.toFixed(4)}, {result.coords.lng.toFixed(4)}
                </div>
              )}
              {result.error && (
                <div className="text-red-600 ml-4 text-xs">
                  {result.error}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
} 