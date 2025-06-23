import React, { useState, useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { Icon } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { geocodeBuildings, calculateBounds } from '../services/geocoding'
import { buildingService } from '../services/api'
import { Building2, MapPin, DollarSign, Users, X, Eye, Edit } from 'lucide-react'
import { getBuildingTypeLabel } from '../types/building'

// Corriger l'icône par défaut de Leaflet
delete Icon.Default.prototype._getIconUrl
Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Icône personnalisée pour les immeubles
const buildingIcon = new Icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

const MapView = () => {
  const [buildings, setBuildings] = useState([])
  const [buildingsWithCoords, setBuildingsWithCoords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [mapCenter, setMapCenter] = useState([46.8139, -71.2080]) // Québec par défaut
  const [mapZoom, setMapZoom] = useState(8)
  const mapRef = useRef()

  // Charger les immeubles depuis l'API
  const fetchBuildings = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('🔄 Chargement des immeubles depuis l\'API...')
      const response = await buildingService.getAll()
      
      console.log(`📊 ${response.length} immeubles récupérés:`, response)
      setBuildings(response)
      
      if (response.length === 0) {
        setError('Aucun immeuble trouvé. Créez des immeubles pour les voir sur la carte.')
        setLoading(false)
        return
      }
      
      // Géocoder les immeubles
      console.log('🗺️ Géocodage des immeubles...')
      const geocodedBuildings = await geocodeBuildings(response)
      
      if (geocodedBuildings.length === 0) {
        setError('Impossible de localiser les immeubles. Vérifiez les adresses.')
        setLoading(false)
        return
      }
      
      setBuildingsWithCoords(geocodedBuildings)
      
      // Calculer les limites et ajuster la vue
      const bounds = calculateBounds(geocodedBuildings)
      if (bounds) {
        // Centrer la carte sur le milieu des immeubles
        const centerLat = (bounds.north + bounds.south) / 2
        const centerLng = (bounds.east + bounds.west) / 2
        setMapCenter([centerLat, centerLng])
        
        // Calculer un zoom approprié basé sur la distance
        const latDiff = bounds.north - bounds.south
        const lngDiff = bounds.east - bounds.west
        const maxDiff = Math.max(latDiff, lngDiff)
        
        let zoom = 10 // Zoom par défaut
        if (maxDiff < 0.01) zoom = 15 // Très proche
        else if (maxDiff < 0.05) zoom = 13 // Proche
        else if (maxDiff < 0.1) zoom = 11 // Moyen
        else if (maxDiff < 0.5) zoom = 9 // Éloigné
        else zoom = 7 // Très éloigné
        
        setMapZoom(zoom)
        
        console.log(`🎯 Carte centrée sur: ${centerLat}, ${centerLng} (zoom: ${zoom})`)
      }
      
    } catch (err) {
      console.error('❌ Erreur lors du chargement:', err)
      setError(`Erreur lors du chargement des immeubles: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBuildings()
  }, [])

  // Formater la valeur financière
  const formatCurrency = (value) => {
    if (!value) return 'N/A'
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  // Formater l'adresse complète
  const formatAddress = (address) => {
    if (!address) return 'Adresse non disponible'
    
    const parts = []
    if (address.street) parts.push(address.street)
    if (address.city) parts.push(address.city)
    if (address.province) parts.push(address.province)
    if (address.postalCode) parts.push(address.postalCode)
    
    return parts.join(', ')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement de la carte...</p>
          <p className="text-sm text-gray-500 mt-2">Géolocalisation des immeubles en cours...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <div className="text-red-600 mb-4">
          <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-semibold">Erreur de chargement</h3>
        </div>
        <p className="text-red-700 mb-4">{error}</p>
        <button
          onClick={fetchBuildings}
          className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
        >
          Réessayer
        </button>
      </div>
    )
  }

  return (
    <div className="h-full w-full">
      {/* Informations sur la carte */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-blue-800">
              Carte des Immeubles - Portfolio CAH
            </h3>
            <p className="text-blue-600">
              {buildingsWithCoords.length} immeuble{buildingsWithCoords.length > 1 ? 's' : ''} géolocalisé{buildingsWithCoords.length > 1 ? 's' : ''}
              {buildings.length > buildingsWithCoords.length && (
                <span className="text-orange-600 ml-2">
                  ({buildings.length - buildingsWithCoords.length} non localisé{buildings.length - buildingsWithCoords.length > 1 ? 's' : ''})
                </span>
              )}
            </p>
          </div>
          <button
            onClick={fetchBuildings}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Actualiser
          </button>
        </div>
      </div>

      {/* Carte */}
      <div className="rounded-lg overflow-hidden shadow-lg" style={{ height: '600px' }}>
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          style={{ height: '100%', width: '100%' }}
          ref={mapRef}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {buildingsWithCoords.map((building) => (
            <Marker
              key={building.id}
              position={[building.coordinates.lat, building.coordinates.lng]}
              icon={buildingIcon}
            >
              <Popup className="building-popup">
                <div className="p-2 min-w-64">
                  <h3 className="font-bold text-lg text-blue-800 mb-2">
                    {building.name}
                  </h3>
                  
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-semibold text-gray-700">📍 Adresse:</span>
                      <br />
                      <span className="text-gray-600">{formatAddress(building.address)}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <div>
                        <span className="font-semibold text-gray-700">🏠 Unités:</span>
                        <span className="ml-1 text-gray-600">{building.units || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="font-semibold text-gray-700">🏢 Étages:</span>
                        <span className="ml-1 text-gray-600">{building.floors || 'N/A'}</span>
                      </div>
                    </div>
                    
                    <div>
                      <span className="font-semibold text-gray-700">💰 Valeur:</span>
                      <span className="ml-1 text-green-600 font-semibold">
                        {formatCurrency(building.financials?.currentValue)}
                      </span>
                    </div>
                    
                    <div>
                      <span className="font-semibold text-gray-700">📅 Année:</span>
                      <span className="ml-1 text-gray-600">{building.yearBuilt || 'N/A'}</span>
                    </div>
                    
                    <div>
                      <span className="font-semibold text-gray-700">🏷️ Type:</span>
                      <span className="ml-1 text-gray-600 capitalize">{building.type || 'N/A'}</span>
                    </div>
                  </div>
                  
                  <div className="mt-3 pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-500">
                      Coordonnées: {building.coordinates.lat.toFixed(6)}, {building.coordinates.lng.toFixed(6)}
                    </p>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
      
      {/* Statistiques */}
      {buildingsWithCoords.length > 0 && (
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-semibold text-green-800">Immeubles Localisés</h4>
            <p className="text-2xl font-bold text-green-600">{buildingsWithCoords.length}</p>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-800">Total Unités</h4>
            <p className="text-2xl font-bold text-blue-600">
              {buildingsWithCoords.reduce((sum, b) => sum + (b.units || 0), 0)}
            </p>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h4 className="font-semibold text-purple-800">Valeur Portfolio</h4>
            <p className="text-2xl font-bold text-purple-600">
              {formatCurrency(buildingsWithCoords.reduce((sum, b) => sum + (b.financials?.currentValue || 0), 0))}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default MapView 