import React, { useState, useEffect } from 'react'
import { 
  Building2, 
  Users, 
  Plus, 
  Eye, 
  Edit, 
  Trash2, 
  MapPin, 
  Calendar, 
  DollarSign,
  TrendingUp,
  BarChart3
} from 'lucide-react'
import { buildingsService, assignmentsService } from '../services/api'
import { parseAddressAndGenerateUnits } from '../types/unit'
import BuildingForm from '../components/BuildingForm'
import BuildingDetails from '../components/BuildingDetails'
import DeleteConfirmationModal from '../components/DeleteConfirmationModal'
import BuildingFilters from '../components/BuildingFilters'
import MapView from '../components/MapView'
import UnitsView from '../components/UnitsView'
import { getBuildingTypeLabel } from '../types/building'

export default function Buildings() {
  const [buildings, setBuildings] = useState([])
  const [filteredBuildings, setFilteredBuildings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [showDetails, setShowDetails] = useState(false)
  const [selectedBuilding, setSelectedBuilding] = useState(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [buildingToDelete, setBuildingToDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const [viewMode, setViewMode] = useState('list') // 'list', 'map', 'units'
  const [assignments, setAssignments] = useState([])

  useEffect(() => {
    fetchBuildings()
    loadAssignments()
    
    // Écouter les événements de changement de vue
    const handleViewChange = (event) => {
      setViewMode(event.detail)
    }
    
    // Écouter l'événement de suppression de locataire
    const handleTenantDeleted = (event) => {
      console.log(`📢 Buildings: Événement tenantDeleted reçu:`, event.detail)
      console.log(`🔄 Buildings: Rechargement des assignations suite à la suppression...`)
      loadAssignments()
    }
    
    // Écouter l'événement de suppression d'assignation spécifique
    const handleAssignmentRemoved = (event) => {
      console.log(`📢 Buildings: Événement assignmentRemoved reçu:`, event.detail)
      console.log(`🔄 Buildings: Rechargement des assignations suite à la suppression d'assignation...`)
      loadAssignments()
    }
    
    window.addEventListener('buildingsViewChange', handleViewChange)
    window.addEventListener('tenantDeleted', handleTenantDeleted)
    window.addEventListener('assignmentRemoved', handleAssignmentRemoved)
    
    return () => {
      window.removeEventListener('buildingsViewChange', handleViewChange)
      window.removeEventListener('tenantDeleted', handleTenantDeleted)
      window.removeEventListener('assignmentRemoved', handleAssignmentRemoved)
    }
  }, [])

  const loadAssignments = async () => {
    try {
      const response = await assignmentsService.getAssignments()
      setAssignments(response.data || [])
    } catch (error) {
      console.error('Error loading assignments:', error)
      // Fallback vers localStorage
      const localAssignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      setAssignments(localAssignments)
    }
  }

  const fetchBuildings = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await buildingsService.getBuildings()
      const buildingsData = response.data || []
      setBuildings(buildingsData)
      setFilteredBuildings(buildingsData)
    } catch (err) {
      console.error('Buildings error:', err)
      setError(`Erreur lors du chargement: ${err.response?.data?.detail || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'construction':
        return 'bg-yellow-100 text-yellow-800'
      case 'maintenance':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const handleAddBuilding = () => {
    setSelectedBuilding(null)
    setShowForm(true)
  }

  const handleEditBuilding = (building) => {
    setSelectedBuilding(building)
    setShowForm(true)
  }

  const handleViewBuilding = (building) => {
    setSelectedBuilding(building)
    setShowDetails(true)
  }

  const handleSaveBuilding = async (buildingData) => {
    try {
      setError(null) // Réinitialiser l'erreur lors de la sauvegarde
      
      // Nettoyer les données pour éviter les erreurs de validation
      const cleanedData = {
        ...buildingData,
        units: Number(buildingData.units) || 1,
        floors: Number(buildingData.floors) || 1,
        yearBuilt: Number(buildingData.yearBuilt) || new Date().getFullYear(),
        totalArea: Number(buildingData.totalArea) || null,
        characteristics: {
          ...buildingData.characteristics,
          parking: Number(buildingData.characteristics?.parking) || 0,
          balconies: Number(buildingData.characteristics?.balconies) || 0
        },
        financials: {
          ...buildingData.financials,
          purchasePrice: Number(buildingData.financials?.purchasePrice) || 0,
          downPayment: Number(buildingData.financials?.downPayment) || 0,
          interestRate: Number(buildingData.financials?.interestRate) || 0,
          currentValue: Number(buildingData.financials?.currentValue) || 0
        }
      }
      
      if (selectedBuilding) {
        // Update existing building via API
        const response = await buildingsService.updateBuilding(selectedBuilding.id, cleanedData)
        
        // Mettre à jour l'état local
        const updatedBuildings = buildings.map(b => b.id === selectedBuilding.id ? response.data : b)
        setBuildings(updatedBuildings)
        setFilteredBuildings(updatedBuildings)
      } else {
        // Create new building via API
        const response = await buildingsService.createBuilding(cleanedData)
        
        // Ajouter à l'état local
        const newBuildings = [...buildings, response.data]
        setBuildings(newBuildings)
        setFilteredBuildings(newBuildings)
      }
      
      // Déclencher un événement personnalisé pour notifier le dashboard
      window.dispatchEvent(new CustomEvent('buildingsUpdated', { 
        detail: { action: selectedBuilding ? 'update' : 'create', building: cleanedData }
      }))
      
      setShowForm(false)
      setSelectedBuilding(null)
    } catch (error) {
      console.error('Error saving building:', error)
      console.error('API Error Response:', error.response?.data)
      setError(`Erreur lors de la sauvegarde: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setSelectedBuilding(null)
  }

  const handleCloseDetails = () => {
    setShowDetails(false)
    setSelectedBuilding(null)
  }

  const handleDeleteClick = (building) => {
    setBuildingToDelete(building)
    setShowDeleteModal(true)
  }

  const handleDeleteConfirm = async () => {
    if (!buildingToDelete) return
    
    try {
      setDeleting(true)
      setError(null)
      
      // Supprimer via API
      await buildingsService.deleteBuilding(buildingToDelete.id)
      
      // Supprimer de l'état local
      const updatedBuildings = buildings.filter(b => b.id !== buildingToDelete.id)
      setBuildings(updatedBuildings)
      setFilteredBuildings(updatedBuildings)
      
      // Déclencher un événement personnalisé pour notifier le dashboard
      window.dispatchEvent(new CustomEvent('buildingsUpdated', { 
        detail: { action: 'delete', building: buildingToDelete }
      }))
      
      // Fermer les modals
      setShowDeleteModal(false)
      setShowDetails(false)
      setBuildingToDelete(null)
      setSelectedBuilding(null)
    } catch (error) {
      console.error('Delete error:', error)
      
      if (error.response?.status === 403) {
        setError('Impossible de supprimer un immeuble du système de base')
      } else {
        setError(`Erreur lors de la suppression: ${error.response?.data?.detail || error.message}`)
      }
    } finally {
      setDeleting(false)
    }
  }

  const handleDeleteCancel = () => {
    setShowDeleteModal(false)
    setBuildingToDelete(null)
  }

  const handleToggleView = (mode) => {
    setViewMode(mode)
    // Émettre l'événement pour synchroniser le sidebar
    window.dispatchEvent(new CustomEvent('buildingsViewChange', { detail: mode }))
  }

  const handleFilterChange = (filters) => {
    let filtered = [...buildings]

    // Filtre par ville
    if (filters.city) {
      filtered = filtered.filter(building => {
        const city = typeof building.address === 'string' ? '' : building.address?.city
        return city === filters.city
      })
    }

    // Filtre par année de construction
    if (filters.yearBuilt) {
      filtered = filtered.filter(building => {
        const year = building.yearBuilt
        switch (filters.yearBuilt) {
          case '2020+':
            return year >= 2020
          case '2010-2019':
            return year >= 2010 && year <= 2019
          case '2000-2009':
            return year >= 2000 && year <= 2009
          case '1990-1999':
            return year >= 1990 && year <= 1999
          case '1980-1989':
            return year >= 1980 && year <= 1989
          case '1970-1979':
            return year >= 1970 && year <= 1979
          case '1960-1969':
            return year >= 1960 && year <= 1969
          case 'before-1960':
            return year < 1960
          default:
            return true
        }
      })
    }

    // Filtre par propriétaire
    if (filters.owner) {
      filtered = filtered.filter(building => building.contacts?.owner === filters.owner)
    }

    // Filtre par valeur actuelle
    if (filters.currentValue) {
      filtered = filtered.filter(building => {
        const value = building.financials?.currentValue || 0
        switch (filters.currentValue) {
          case '0-500000':
            return value < 500000
          case '500000-1000000':
            return value >= 500000 && value < 1000000
          case '1000000-2000000':
            return value >= 1000000 && value < 2000000
          case '2000000+':
            return value >= 2000000
          default:
            return true
        }
      })
    }

    // Filtre par banque
    if (filters.bank) {
      filtered = filtered.filter(building => building.contacts?.bank === filters.bank)
    }

    setFilteredBuildings(filtered)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  // Statistiques pour le tableau de bord des immeubles (basées sur les immeubles filtrés)
  const totalBuildings = filteredBuildings.length
  const totalUnits = filteredBuildings.reduce((sum, b) => sum + b.units, 0)
  const totalValue = filteredBuildings.reduce((sum, b) => sum + (b.financials?.currentValue || 0), 0)
  
  // Calculer le vrai taux d'occupation basé sur les unités générées
  const calculateOccupancyRate = () => {
    // Utiliser les assignations du backend au lieu du localStorage
    const allUnits = []
    filteredBuildings.forEach(building => {
      try {
        const buildingUnits = parseAddressAndGenerateUnits(building)
        
        // Ajouter les currentTenants à chaque unité
        const unitsWithTenants = buildingUnits.map(unit => ({
          ...unit,
          currentTenants: assignments
            .filter(a => a.unitId === unit.id)
            .map(a => a.tenantData)
        }))
        
        allUnits.push(...unitsWithTenants)
      } catch (error) {
        console.error('Erreur lors de la génération des unités pour l\'immeuble:', building, error)
      }
    })
    
    if (allUnits.length === 0) return 0
    
    // Compter les unités occupées (qui ont des currentTenants OU status 'occupied')
    const occupiedUnits = allUnits.filter(unit => 
      unit.currentTenants?.length > 0 || unit.status === 'occupied'
    ).length
    
    const rate = Math.round((occupiedUnits / allUnits.length) * 100)
    
    return rate
  }
  
  const occupancyRate = calculateOccupancyRate()

  return (
    <div className="space-y-4 lg:space-y-6">
      {/* Tableau de bord spécifique aux immeubles */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-6 mb-6 lg:mb-8">
        <div className="card text-center">
          <Building2 className="h-6 w-6 lg:h-8 lg:w-8 text-primary-600 mx-auto mb-2" />
          <h3 className="text-sm lg:text-lg font-semibold text-gray-900">Total Immeubles</h3>
          <p className="text-xl lg:text-2xl font-bold text-primary-600">{totalBuildings}</p>
        </div>
        
        <div className="card text-center">
          <BarChart3 className="h-6 w-6 lg:h-8 lg:w-8 text-green-600 mx-auto mb-2" />
          <h3 className="text-sm lg:text-lg font-semibold text-gray-900">Valeur Portfolio</h3>
          <p className="text-xl lg:text-2xl font-bold text-green-600">
            {totalValue > 0 ? `${(totalValue / 1000000).toFixed(1)}M$` : '0$'}
          </p>
        </div>
        
        <div className="card text-center">
          <Users className="h-6 w-6 lg:h-8 lg:w-8 text-blue-600 mx-auto mb-2" />
          <h3 className="text-sm lg:text-lg font-semibold text-gray-900">Total Unités</h3>
          <p className="text-xl lg:text-2xl font-bold text-blue-600">{totalUnits}</p>
        </div>
        
        <div className="card text-center">
          <TrendingUp className="h-6 w-6 lg:h-8 lg:w-8 text-yellow-600 mx-auto mb-2" />
          <h3 className="text-sm lg:text-lg font-semibold text-gray-900">Taux Occupation</h3>
          <p className="text-xl lg:text-2xl font-bold text-yellow-600">{occupancyRate}%</p>
        </div>
      </div>

      {/* Filtres (remplacent le cadre "Gestion des immeubles") */}
      {viewMode === 'list' && (
        <BuildingFilters 
          buildings={buildings} 
          onFilterChange={handleFilterChange} 
        />
      )}

      {/* Error Display */}
      {error && (
        <div className={`border rounded-lg p-4 ${
          error.includes('Mode hors ligne') || error.includes('locale') 
            ? 'bg-yellow-50 border-yellow-200' 
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              {error.includes('Mode hors ligne') || error.includes('locale') ? (
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                  <p className="text-yellow-700">{error}</p>
                </div>
              ) : (
                <p className="text-red-700">{error}</p>
              )}
            </div>
            <button 
              onClick={() => setError(null)}
              className={`ml-4 ${
                error.includes('Mode hors ligne') || error.includes('locale')
                  ? 'text-yellow-500 hover:text-yellow-700'
                  : 'text-red-500 hover:text-red-700'
              }`}
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Contenu principal - Vue Liste, Carte ou Unités */}
      {viewMode === 'map' ? (
        // Vue carte en plein écran (sans card wrapper)
        <div className="h-[600px] lg:h-[700px]">
          <MapView />
        </div>
      ) : viewMode === 'units' ? (
        // Vue unités avec toutes les unités générées
        <UnitsView buildings={buildings} />
      ) : (
        // Vue liste avec bouton "Nouvel immeuble" intégré
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Liste des Immeubles ({filteredBuildings.length})
            </h3>
            <button onClick={handleAddBuilding} className="btn-primary flex items-center">
              <Plus className="h-4 w-4 mr-2" />
              Nouvel Immeuble
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 lg:gap-6">
            {filteredBuildings.map((building) => (
              <div key={building.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <div className="p-2 bg-primary-100 rounded-lg">
                      <Building2 className="h-6 w-6 text-primary-600" />
                    </div>
                    <div className="ml-3">
                      <h4 className="text-lg font-semibold text-gray-900">{building.name}</h4>
                      <p className="text-sm text-gray-600">{getBuildingTypeLabel(building.type)}</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center text-gray-600">
                    <MapPin className="h-4 w-4 mr-2" />
                    <span className="text-sm">
                      {typeof building.address === 'string' 
                        ? building.address 
                        : `${building.address?.street || ''}, ${building.address?.city || ''}`
                      }
                    </span>
                  </div>
                  
                  <div className="flex items-center text-gray-600">
                    <Users className="h-4 w-4 mr-2" />
                    <span className="text-sm">{building.units} unités</span>
                  </div>
                </div>

                <div className="mt-6 flex space-x-2">
                  <button onClick={() => handleViewBuilding(building)} className="flex-1 btn-primary text-sm py-2">
                    <Eye className="h-4 w-4 mr-1" />
                    Détails
                  </button>
                  <button onClick={() => handleEditBuilding(building)} className="flex-1 btn-secondary text-sm py-2">
                    <Edit className="h-4 w-4 mr-1" />
                    Modifier
                  </button>
                  <button 
                    onClick={() => handleDeleteClick(building)} 
                    className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors text-sm"
                    title="Supprimer l'immeuble"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Empty State */}
          {filteredBuildings.length === 0 && !loading && !error && (
            <div className="text-center py-12">
              <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {buildings.length === 0 ? 'Aucun immeuble' : 'Aucun immeuble correspondant aux filtres'}
              </h3>
              <p className="text-gray-600 mb-4">
                {buildings.length === 0 
                  ? 'Commencez par ajouter votre premier immeuble.'
                  : 'Essayez de modifier vos critères de filtrage.'
                }
              </p>
              <button onClick={handleAddBuilding} className="btn-primary">
                <Plus className="h-5 w-5 mr-2" />
                Ajouter un Immeuble
              </button>
            </div>
          )}
        </div>
      )}

      {/* Building Form Modal */}
      <BuildingForm
        building={selectedBuilding}
        isOpen={showForm}
        onClose={handleCloseForm}
        onSave={handleSaveBuilding}
      />

      {/* Building Details Modal */}
      <BuildingDetails
        building={selectedBuilding}
        isOpen={showDetails}
        onClose={handleCloseDetails}
        onDelete={handleDeleteClick}
      />

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        isOpen={showDeleteModal}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        buildingName={buildingToDelete?.name || ''}
        buildingValue={buildingToDelete?.financials?.currentValue || 0}
        loading={deleting}
      />
    </div>
  )
} 