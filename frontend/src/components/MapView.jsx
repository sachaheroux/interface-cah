import React, { useEffect, useState, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import { Building2, MapPin, DollarSign, Users, X, Eye, Edit } from 'lucide-react'
import { geocodeAddress, getApproximateCoordinates } from '../services/geocoding'
import { getBuildingTypeLabel } from '../types/building'

// Fix pour les icônes Leaflet avec React
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Icône personnalisée pour les immeubles
const buildingIcon = new L.DivIcon({
  html: `
    <div style="
      background: #2563eb;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 3px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    ">
      <svg width="16" height="16" fill="white" viewBox="0 0 24 24">
        <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.92-.3 4-1.79 6-4.5V7l-10-5z"/>
      </svg>
    </div>
  `,
  className: 'custom-building-marker',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
})

// Composant pour ajuster la vue de la carte
function MapViewAdjuster({ buildings, coordinates }) {
  const map = useMap()

  useEffect(() => {
    if (coordinates && coordinates.length > 0) {
      // Créer un groupe de marqueurs pour ajuster la vue
      const validCoords = coordinates.filter(coord => coord.coords)
      
      if (validCoords.length === 1) {
        // Un seul point, centrer dessus
        map.setView([validCoords[0].coords.lat, validCoords[0].coords.lng], 13)
      } else if (validCoords.length > 1) {
        // Plusieurs points, ajuster pour tous les voir
        const bounds = L.latLngBounds(validCoords.map(coord => [coord.coords.lat, coord.coords.lng]))
        map.fitBounds(bounds, { padding: [20, 20] })
      }
    }
  }, [map, coordinates])

  return null
}

export default function MapView({ 
  buildings, 
  isOpen, 
  onClose, 
  onViewBuilding, 
  onEditBuilding 
}) {
  const [coordinates, setCoordinates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const mapRef = useRef()

  useEffect(() => {
    if (isOpen && buildings.length > 0) {
      geocodeBuildings()
    }
  }, [isOpen, buildings])

  const geocodeBuildings = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const coordsPromises = buildings.map(async (building) => {
        let coords = null
        
        try {
          // Essayer le géocodage précis d'abord
          coords = await geocodeAddress(building.address)
          
          // Si échec, utiliser les coordonnées approximatives
          if (!coords) {
            const city = typeof building.address === 'string' 
              ? building.address.split(',')[1]?.trim() 
              : building.address.city
            coords = getApproximateCoordinates(city)
          }
        } catch (err) {
          console.warn(`Erreur géocodage pour ${building.name}:`, err)
          // Utiliser coordonnées par défaut
          coords = getApproximateCoordinates('montreal')
        }
        
        return {
          building,
          coords,
          id: building.id
        }
      })

      const results = await Promise.all(coordsPromises)
      setCoordinates(results)
    } catch (err) {
      setError('Erreur lors du chargement des coordonnées')
      console.error('Erreur géocodage:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const formatAddress = (address) => {
    if (typeof address === 'string') return address
    return `${address.street}, ${address.city}, ${address.province}`
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full h-full max-w-7xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center">
            <MapPin className="h-6 w-6 text-primary-600 mr-2" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">Vue Carte des Immeubles</h2>
              <p className="text-sm text-gray-600">
                {buildings.length} immeuble{buildings.length > 1 ? 's' : ''} • Cliquez sur les marqueurs pour plus d'infos
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Map Container */}
        <div className="flex-1 relative">
          {loading && (
            <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Chargement des emplacements...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="absolute top-4 left-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 z-10">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          <MapContainer
            center={[45.5017, -73.5673]} // Montréal par défaut
            zoom={10}
            style={{ height: '100%', width: '100%' }}
            ref={mapRef}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            
            {/* Ajusteur de vue */}
            <MapViewAdjuster buildings={buildings} coordinates={coordinates} />
            
            {/* Marqueurs pour chaque immeuble */}
            {coordinates.map(({ building, coords }) => {
              if (!coords) return null
              
              return (
                <Marker
                  key={building.id}
                  position={[coords.lat, coords.lng]}
                  icon={buildingIcon}
                >
                  <Popup className="custom-popup" minWidth={300}>
                    <div className="p-2">
                      {/* En-tête */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center">
                          <div className="p-2 bg-primary-100 rounded-lg mr-3">
                            <Building2 className="h-5 w-5 text-primary-600" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">{building.name}</h3>
                            <p className="text-sm text-gray-600">{getBuildingTypeLabel(building.type)}</p>
                          </div>
                        </div>
                      </div>

                      {/* Informations */}
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center text-sm text-gray-600">
                          <MapPin className="h-4 w-4 mr-2" />
                          <span>{formatAddress(building.address)}</span>
                        </div>
                        
                        <div className="flex items-center text-sm text-gray-600">
                          <Users className="h-4 w-4 mr-2" />
                          <span>{building.units} unités • {building.floors} étage{building.floors > 1 ? 's' : ''}</span>
                        </div>

                        {building.financials?.currentValue && (
                          <div className="flex items-center text-sm text-gray-600">
                            <DollarSign className="h-4 w-4 mr-2" />
                            <span className="font-medium text-green-600">
                              {formatCurrency(building.financials.currentValue)}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            onViewBuilding(building)
                            onClose()
                          }}
                          className="flex-1 btn-primary text-sm py-2 flex items-center justify-center"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          Détails
                        </button>
                        <button
                          onClick={() => {
                            onEditBuilding(building)
                            onClose()
                          }}
                          className="flex-1 btn-secondary text-sm py-2 flex items-center justify-center"
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Modifier
                        </button>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              )
            })}
          </MapContainer>
        </div>

        {/* Footer avec statistiques */}
        <div className="border-t p-4 bg-gray-50">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center space-x-6">
              <span>📍 {coordinates.filter(c => c.coords).length} emplacements trouvés</span>
              <span>🏢 {buildings.length} immeubles au total</span>
              <span>🏠 {buildings.reduce((sum, b) => sum + b.units, 0)} unités totales</span>
            </div>
            <div className="text-xs text-gray-500">
              Utilisez la molette pour zoomer • Glissez pour déplacer la carte
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 