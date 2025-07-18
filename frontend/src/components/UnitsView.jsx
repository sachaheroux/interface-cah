import React, { useState, useEffect } from 'react'
import { 
  Users, MapPin, Eye, Edit3, Trash2, Search, Filter, Home, Mail, Phone, DollarSign, 
  Building2, Bed, Bath, Car, Wifi, Wind, CheckCircle, Clock, AlertCircle, UserMinus
} from 'lucide-react'
import { parseAddressAndGenerateUnits } from '../types/unit'
import { calculateUnitStatus, getUnitStatusLabel, getUnitStatusColor, getUnitTypeLabel } from '../types/unit'
import { assignmentsService } from '../services/api'
import UnitForm from './UnitForm'
import UnitDetails from './UnitDetails'

export default function UnitsView({ buildings }) {
  const [units, setUnits] = useState([])
  const [filteredUnits, setFilteredUnits] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [buildingFilter, setBuildingFilter] = useState('')
  
  // États pour les modales
  const [selectedUnit, setSelectedUnit] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [showDetails, setShowDetails] = useState(false)
  const [assignments, setAssignments] = useState([])
  const [loadingAssignments, setLoadingAssignments] = useState(true)

  // Charger les assignations depuis le backend
  const loadAssignments = async () => {
    try {
      setLoadingAssignments(true)
      const response = await assignmentsService.getAssignments()
      const assignmentsData = response.data || []
      console.log('Assignments loaded from backend:', assignmentsData)
      setAssignments(assignmentsData)
    } catch (error) {
      console.error('Error loading assignments:', error)
      // Fallback vers localStorage
      const localAssignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      setAssignments(localAssignments)
    } finally {
      setLoadingAssignments(false)
    }
  }

  // Charger les unités et les assignations
  useEffect(() => {
    loadAssignments()
    
    // Écouter l'événement de suppression de locataire
    const handleTenantDeleted = (event) => {
      console.log(`📢 Événement tenantDeleted reçu:`, event.detail)
      console.log(`🔄 Rechargement des assignations suite à la suppression...`)
      loadAssignments()
    }
    
    window.addEventListener('tenantDeleted', handleTenantDeleted)
    
    return () => {
      window.removeEventListener('tenantDeleted', handleTenantDeleted)
    }
  }, [])

  useEffect(() => {
    if (loadingAssignments) return // Attendre que les assignations soient chargées
    
    const loadUnitsAndAssignments = () => {
      // Générer les unités depuis les immeubles
      const allUnits = []
      buildings.forEach(building => {
        if (building && typeof building === 'object') {
          try {
            const buildingUnits = parseAddressAndGenerateUnits(building)
            
            // Calculer le statut dynamique pour chaque unité
            const unitsWithStatus = buildingUnits.map(unit => {
              const unitAssignments = assignments.filter(a => a.unitId === unit.id)
              const currentTenants = unitAssignments.map(a => ({
                ...a.tenantData,
                id: a.tenantData?.id || a.tenantId // S'assurer que l'ID est présent
              }))
              
              return {
                ...unit,
                status: calculateUnitStatus(unit, assignments),
                currentTenants: currentTenants
              }
            })
            
            allUnits.push(...unitsWithStatus)
          } catch (error) {
            console.error('Erreur lors de la génération des unités pour l\'immeuble:', building, error)
          }
        }
      })
      
      setUnits(allUnits)
    }

    loadUnitsAndAssignments()
  }, [buildings, assignments, loadingAssignments])

  // Filtrer les unités
  useEffect(() => {
    let filtered = units

    // Filtrer par terme de recherche
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase()
      filtered = filtered.filter(unit =>
        unit.address?.toLowerCase().includes(searchLower) ||
        unit.buildingName?.toLowerCase().includes(searchLower) ||
        unit.currentTenants?.some(tenant => 
          tenant.name?.toLowerCase().includes(searchLower)
        )
      )
    }

    // Filtrer par statut
    if (statusFilter) {
      filtered = filtered.filter(unit => unit.status === statusFilter)
    }

    // Filtrer par immeuble
    if (buildingFilter) {
      filtered = filtered.filter(unit => unit.buildingId.toString() === buildingFilter)
    }

    setFilteredUnits(filtered)
  }, [units, searchTerm, statusFilter, buildingFilter])

  // Gestionnaires d'événements
  const handleViewUnit = (unit) => {
    setSelectedUnit(unit)
    setShowDetails(true)
  }

  const handleEditUnit = (unit) => {
    setSelectedUnit(unit)
    setShowForm(true)
  }

  const handleSaveUnit = async (updatedUnit) => {
    try {
      // Mettre à jour l'unité dans la liste
      const updatedUnits = units.map(unit => 
        unit.id === updatedUnit.id ? updatedUnit : unit
      )
      setUnits(updatedUnits)
      
      // Ici, vous pourriez ajouter la logique pour sauvegarder dans une API
      console.log('Unité sauvegardée:', updatedUnit)
      
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
      throw error
    }
  }

  const handleDeleteUnit = async (unit) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer l'unité #${unit.unitNumber} ?`)) {
      try {
        // Supprimer l'unité de la liste
        const updatedUnits = units.filter(u => u.id !== unit.id)
        setUnits(updatedUnits)
        setShowDetails(false)
        
        // Ici, vous pourriez ajouter la logique pour supprimer de l'API
        console.log('Unité supprimée:', unit)
        
      } catch (error) {
        console.error('Erreur lors de la suppression:', error)
      }
    }
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setSelectedUnit(null)
  }

  const handleCloseDetails = () => {
    setShowDetails(false)
    setSelectedUnit(null)
  }

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

  // Statistiques simples
  const totalUnits = units.length
  const occupiedUnits = units.filter(unit => 
    unit.currentTenants?.length > 0 || unit.status === 'occupied'
  ).length
  const vacantUnits = totalUnits - occupiedUnits
  const totalRent = units.reduce((sum, unit) => sum + (unit.rental?.monthlyRent || 0), 0)
  
  // Calcul simple : (nombre d'unités occupées / nombre d'unités total) * 100
  const occupancyRate = totalUnits > 0 ? Math.round((occupiedUnits / totalUnits) * 100) : 0

  // Fonction pour supprimer une assignation spécifique
  const handleRemoveFromUnit = async (tenantId, unitId, tenantName, unitName) => {
    const confirmMessage = `Êtes-vous sûr de vouloir retirer "${tenantName}" de l'unité "${unitName}" ?\n\nLe locataire restera dans le système, seule l'assignation à cette unité sera supprimée.`
    
    if (window.confirm(confirmMessage)) {
      try {
        console.log(`🔗 Suppression assignation: ${tenantName} (${tenantId}) de ${unitName} (${unitId})`)
        
        await assignmentsService.removeSpecificAssignment(tenantId, unitId)
        
        console.log(`✅ ${tenantName} retiré de ${unitName} avec succès`)
        
        // Recharger les assignations pour mettre à jour l'affichage
        await loadAssignments()
        
        // Déclencher un événement pour mettre à jour les autres vues
        window.dispatchEvent(new CustomEvent('assignmentRemoved', { 
          detail: { tenantId, unitId, tenantName, unitName } 
        }))
        
      } catch (error) {
        console.error('❌ Erreur lors de la suppression de l\'assignation:', error)
        alert(`Erreur lors de la suppression de l'assignation de "${tenantName}". Vérifiez la console pour plus de détails.`)
      }
    }
  }

  return (
    <div className="space-y-6">
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
                    <h4 className="font-semibold text-gray-900">{unit.address}</h4>
                    <p className="text-sm text-gray-600">{unit.buildingName}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getUnitStatusColor(unit.currentTenants?.length > 0 ? 'occupied' : unit.status || 'vacant')}`}>
                  {getUnitStatusLabel(unit.currentTenants?.length > 0 ? 'occupied' : unit.status || 'vacant')}
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
              {unit.currentTenants?.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-3 mb-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <Users className="h-4 w-4 mr-2 text-gray-600" />
                      <span className="text-sm font-medium text-gray-900">Locataires</span>
                    </div>
                    <span className="text-xs text-gray-500">{unit.currentTenants.length} locataire{unit.currentTenants.length > 1 ? 's' : ''}</span>
                  </div>
                  
                  {/* Liste des locataires avec bouton de suppression pour chaque */}
                  <div className="space-y-2">
                    {unit.currentTenants.map((tenant, tenantIndex) => (
                      <div key={tenantIndex} className="bg-white rounded-md p-2 border border-gray-200">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="font-medium text-sm text-gray-900">{tenant.name}</div>
                            {tenant.email && (
                              <div className="flex items-center mt-1">
                                <Mail className="h-3 w-3 mr-2 text-gray-400" />
                                <span className="text-xs text-gray-600">{tenant.email}</span>
                              </div>
                            )}
                            {tenant.phone && (
                              <div className="flex items-center mt-1">
                                <Phone className="h-3 w-3 mr-2 text-gray-400" />
                                <span className="text-xs text-gray-600">{tenant.phone}</span>
                              </div>
                            )}
                          </div>
                          
                          {/* Bouton pour retirer ce locataire de cette unité */}
                          <button
                            onClick={() => handleRemoveFromUnit(
                              tenant.id, 
                              unit.id, 
                              tenant.name, 
                              `${unit.buildingName} - ${unit.unitNumber}`
                            )}
                            className="ml-2 p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                            title={`Retirer ${tenant.name} de cette unité`}
                          >
                            <UserMinus className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
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
                <button className="flex-1 btn-primary text-sm py-2" onClick={() => handleViewUnit(unit)}>
                  <Eye className="h-4 w-4 mr-1" />
                  Détails
                </button>
                <button className="flex-1 btn-secondary text-sm py-2" onClick={() => handleEditUnit(unit)}>
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

      {/* Modales */}
      {showForm && (
        <UnitForm
          unit={selectedUnit}
          isOpen={showForm}
          onSave={handleSaveUnit}
          onClose={handleCloseForm}
        />
      )}
      {showDetails && (
        <UnitDetails
          unit={selectedUnit}
          isOpen={showDetails}
          onClose={handleCloseDetails}
          onEdit={handleEditUnit}
          onDelete={handleDeleteUnit}
        />
      )}
    </div>
  )
} 