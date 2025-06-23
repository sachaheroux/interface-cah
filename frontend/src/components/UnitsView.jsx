import React, { useState, useEffect } from 'react'
import { 
  Home, 
  Users, 
  DollarSign, 
  MapPin, 
  Phone, 
  Mail, 
  Calendar,
  Wifi,
  Zap,
  Thermometer,
  Car,
  Sofa,
  Droplets,
  Wind,
  Package,
  Plus,
  Edit,
  Eye,
  Search
} from 'lucide-react'
import { parseAddressAndGenerateUnits, getUnitStatusLabel, getUnitStatusColor, getUnitTypeLabel } from '../types/unit'

export default function UnitsView({ buildings }) {
  const [units, setUnits] = useState([])
  const [filteredUnits, setFilteredUnits] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [buildingFilter, setBuildingFilter] = useState('')

  // Générer toutes les unités à partir des immeubles
  useEffect(() => {
    const allUnits = []
    buildings.forEach(building => {
      const buildingUnits = parseAddressAndGenerateUnits(building)
      allUnits.push(...buildingUnits)
    })
    setUnits(allUnits)
    setFilteredUnits(allUnits)
  }, [buildings])

  // Filtrer les unités
  useEffect(() => {
    let filtered = [...units]

    // Filtre par terme de recherche
    if (searchTerm) {
      filtered = filtered.filter(unit => 
        unit.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
        unit.buildingName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        unit.tenant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        unit.unitNumber.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filtre par statut
    if (statusFilter) {
      filtered = filtered.filter(unit => unit.status === statusFilter)
    }

    // Filtre par immeuble
    if (buildingFilter) {
      filtered = filtered.filter(unit => unit.buildingId.toString() === buildingFilter)
    }

    setFilteredUnits(filtered)
  }, [units, searchTerm, statusFilter, buildingFilter])

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const getAmenityIcon = (amenity) => {
    switch (amenity) {
      case 'heating': return <Thermometer className="h-4 w-4" />
      case 'electricity': return <Zap className="h-4 w-4" />
      case 'wifi': return <Wifi className="h-4 w-4" />
      case 'furnished': return <Sofa className="h-4 w-4" />
      case 'parking': return <Car className="h-4 w-4" />
      case 'laundry': return <Droplets className="h-4 w-4" />
      case 'airConditioning': return <Wind className="h-4 w-4" />
      case 'storage': return <Package className="h-4 w-4" />
      default: return null
    }
  }

  const getAmenityLabel = (amenity) => {
    switch (amenity) {
      case 'heating': return 'Chauffage'
      case 'electricity': return 'Électricité'
      case 'wifi': return 'WiFi'
      case 'furnished': return 'Meublé'
      case 'parking': return 'Stationnement'
      case 'laundry': return 'Buanderie'
      case 'airConditioning': return 'Climatisation'
      case 'balcony': return 'Balcon'
      case 'storage': return 'Rangement'
      case 'dishwasher': return 'Lave-vaisselle'
      case 'washerDryer': return 'Laveuse-sécheuse'
      default: return amenity
    }
  }

  // Statistiques
  const totalUnits = filteredUnits.length
  const occupiedUnits = filteredUnits.filter(unit => unit.status === 'occupied').length
  const vacantUnits = filteredUnits.filter(unit => unit.status === 'vacant').length
  const totalRent = filteredUnits.reduce((sum, unit) => sum + (unit.rental?.monthlyRent || 0), 0)
  const occupancyRate = totalUnits > 0 ? Math.round((occupiedUnits / totalUnits) * 100) : 0

  return (
    <div className="space-y-6">
      {/* Statistiques des unités */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="card text-center">
          <Home className="h-6 w-6 lg:h-8 lg:w-8 text-primary-600 mx-auto mb-2" />
          <h3 className="text-sm lg:text-base font-semibold text-gray-900">Total Unités</h3>
          <p className="text-xl lg:text-2xl font-bold text-primary-600">{totalUnits}</p>
        </div>
        
        <div className="card text-center">
          <Users className="h-6 w-6 lg:h-8 lg:w-8 text-green-600 mx-auto mb-2" />
          <h3 className="text-sm lg:text-base font-semibold text-gray-900">Occupées</h3>
          <p className="text-xl lg:text-2xl font-bold text-green-600">{occupiedUnits}</p>
        </div>
        
        <div className="card text-center">
          <Home className="h-6 w-6 lg:h-8 lg:w-8 text-red-600 mx-auto mb-2" />
          <h3 className="text-sm lg:text-base font-semibold text-gray-900">Libres</h3>
          <p className="text-xl lg:text-2xl font-bold text-red-600">{vacantUnits}</p>
        </div>
        
        <div className="card text-center">
          <DollarSign className="h-6 w-6 lg:h-8 lg:w-8 text-blue-600 mx-auto mb-2" />
          <h3 className="text-sm lg:text-base font-semibold text-gray-900">Revenus Totaux</h3>
          <p className="text-lg lg:text-xl font-bold text-blue-600">{formatCurrency(totalRent)}</p>
        </div>
        
        <div className="card text-center">
          <Calendar className="h-6 w-6 lg:h-8 lg:w-8 text-yellow-600 mx-auto mb-2" />
          <h3 className="text-sm lg:text-base font-semibold text-gray-900">Taux Occupation</h3>
          <p className="text-xl lg:text-2xl font-bold text-yellow-600">{occupancyRate}%</p>
        </div>
      </div>

      {/* Filtres et recherche */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Filtres et Recherche</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Recherche */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Rechercher unité, adresse, locataire..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Filtre par statut */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Tous les statuts</option>
            <option value="occupied">Occupée</option>
            <option value="vacant">Libre</option>
            <option value="maintenance">Maintenance</option>
            <option value="reserved">Réservée</option>
          </select>

          {/* Filtre par immeuble */}
          <select
            value={buildingFilter}
            onChange={(e) => setBuildingFilter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Tous les immeubles</option>
            {buildings.map(building => (
              <option key={building.id} value={building.id.toString()}>
                {building.name}
              </option>
            ))}
          </select>

          {/* Bouton effacer filtres */}
          <button
            onClick={() => {
              setSearchTerm('')
              setStatusFilter('')
              setBuildingFilter('')
            }}
            className="btn-secondary"
          >
            Effacer filtres
          </button>
        </div>
      </div>

      {/* Liste des unités */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Liste des Unités ({filteredUnits.length})
          </h3>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredUnits.map((unit) => (
            <div key={unit.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              {/* En-tête de l'unité */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <Home className="h-5 w-5 text-primary-600" />
                  </div>
                  <div className="ml-3">
                    <h4 className="font-semibold text-gray-900">Unité #{unit.unitNumber}</h4>
                    <p className="text-sm text-gray-600">{unit.buildingName}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getUnitStatusColor(unit.status)}`}>
                  {getUnitStatusLabel(unit.status)}
                </span>
              </div>

              {/* Adresse */}
              <div className="flex items-center text-gray-600 mb-3">
                <MapPin className="h-4 w-4 mr-2" />
                <span className="text-sm">{unit.address}</span>
              </div>

              {/* Type et superficie */}
              <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
                <span>{getUnitTypeLabel(unit.type)}</span>
                {unit.area > 0 && <span>{unit.area} pi²</span>}
              </div>

              {/* Loyer */}
              {unit.rental?.monthlyRent > 0 && (
                <div className="flex items-center text-gray-600 mb-3">
                  <DollarSign className="h-4 w-4 mr-2" />
                  <span className="text-sm font-medium">{formatCurrency(unit.rental.monthlyRent)}/mois</span>
                </div>
              )}

              {/* Locataire */}
              {unit.tenant?.name && (
                <div className="bg-gray-50 rounded-lg p-3 mb-3">
                  <div className="flex items-center mb-2">
                    <Users className="h-4 w-4 mr-2 text-gray-600" />
                    <span className="text-sm font-medium text-gray-900">{unit.tenant.name}</span>
                  </div>
                  {unit.tenant.email && (
                    <div className="flex items-center mb-1">
                      <Mail className="h-3 w-3 mr-2 text-gray-400" />
                      <span className="text-xs text-gray-600">{unit.tenant.email}</span>
                    </div>
                  )}
                  {unit.tenant.phone && (
                    <div className="flex items-center">
                      <Phone className="h-3 w-3 mr-2 text-gray-400" />
                      <span className="text-xs text-gray-600">{unit.tenant.phone}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Services inclus */}
              <div className="mb-4">
                <h5 className="text-xs font-medium text-gray-700 mb-2">Services inclus:</h5>
                <div className="flex flex-wrap gap-1">
                  {Object.entries(unit.amenities).map(([amenity, included]) => {
                    if (!included) return null
                    const icon = getAmenityIcon(amenity)
                    return (
                      <span
                        key={amenity}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800"
                        title={getAmenityLabel(amenity)}
                      >
                        {icon && <span className="mr-1">{icon}</span>}
                        {getAmenityLabel(amenity)}
                      </span>
                    )
                  })}
                  {Object.values(unit.amenities).every(val => !val) && (
                    <span className="text-xs text-gray-500">Aucun service inclus</span>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-2">
                <button className="flex-1 btn-primary text-sm py-2">
                  <Eye className="h-4 w-4 mr-1" />
                  Détails
                </button>
                <button className="flex-1 btn-secondary text-sm py-2">
                  <Edit className="h-4 w-4 mr-1" />
                  Modifier
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredUnits.length === 0 && (
          <div className="text-center py-12">
            <Home className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {units.length === 0 ? 'Aucune unité' : 'Aucune unité correspondant aux filtres'}
            </h3>
            <p className="text-gray-600 mb-4">
              {units.length === 0 
                ? 'Les unités seront générées automatiquement à partir des immeubles.'
                : 'Essayez de modifier vos critères de recherche.'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  )
} 