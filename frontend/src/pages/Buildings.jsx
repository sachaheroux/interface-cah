import React, { useState, useEffect } from 'react'
import { Building2, MapPin, Users, Plus, Edit, Eye, BarChart3, TrendingUp, AlertTriangle, Trash2 } from 'lucide-react'
import { buildingsService } from '../services/api'
import BuildingForm from '../components/BuildingForm'
import BuildingDetails from '../components/BuildingDetails'
import DeleteConfirmationModal from '../components/DeleteConfirmationModal'
import { getBuildingTypeLabel } from '../types/building'

export default function Buildings() {
  const [buildings, setBuildings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [showDetails, setShowDetails] = useState(false)
  const [selectedBuilding, setSelectedBuilding] = useState(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [buildingToDelete, setBuildingToDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    fetchBuildings()
  }, [])

  const fetchBuildings = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await buildingsService.getBuildings()
      setBuildings(response.data)
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
        setBuildings(prev => prev.map(b => b.id === selectedBuilding.id ? response.data : b))
      } else {
        // Create new building via API
        const response = await buildingsService.createBuilding(cleanedData)
        
        // Ajouter à l'état local
        setBuildings(prev => [...prev, response.data])
      }
      
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
      setBuildings(prev => prev.filter(b => b.id !== buildingToDelete.id))
      
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  // Statistiques pour le tableau de bord des immeubles
  const totalBuildings = buildings.length
  const totalUnits = buildings.reduce((sum, b) => sum + b.units, 0)
  const occupancyRate = 85 // Mock data

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
          <p className="text-xl lg:text-2xl font-bold text-green-600">2.5M$</p>
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

      {/* Actions rapides */}
      <div className="card">
        <h3 className="text-base lg:text-lg font-semibold text-gray-900 mb-3 lg:mb-4">Actions Rapides</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 lg:gap-3">
          <button onClick={handleAddBuilding} className="btn-primary text-center py-2 lg:py-3">
            <Plus className="h-4 w-4 lg:h-5 lg:w-5 mx-auto mb-1" />
            <span className="text-xs lg:text-sm">Nouvel Immeuble</span>
          </button>
          <button className="btn-secondary text-center py-2 lg:py-3">
            <MapPin className="h-4 w-4 lg:h-5 lg:w-5 mx-auto mb-1" />
            <span className="text-xs lg:text-sm">Vue Carte</span>
          </button>
          <button className="btn-secondary text-center py-2 lg:py-3">
            <BarChart3 className="h-4 w-4 lg:h-5 lg:w-5 mx-auto mb-1" />
            <span className="text-xs lg:text-sm">Rapport</span>
          </button>
          <button className="btn-secondary text-center py-2 lg:py-3">
            <AlertTriangle className="h-4 w-4 lg:h-5 lg:w-5 mx-auto mb-1" />
            <span className="text-xs lg:text-sm">Maintenance</span>
          </button>
        </div>
      </div>

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

      {/* Liste des immeubles */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Liste des Immeubles</h3>
          <button onClick={handleAddBuilding} className="btn-primary flex items-center text-sm">
            <Plus className="h-4 w-4 mr-2" />
            Ajouter
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 lg:gap-6">
          {buildings.map((building) => (
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
                      : `${building.address.street}, ${building.address.city}`
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
      </div>

      {/* Empty State */}
      {buildings.length === 0 && !loading && !error && (
        <div className="text-center py-12">
          <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun immeuble</h3>
          <p className="text-gray-600 mb-4">Commencez par ajouter votre premier immeuble.</p>
          <button onClick={handleAddBuilding} className="btn-primary">
            <Plus className="h-5 w-5 mr-2" />
            Ajouter un Immeuble
          </button>
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