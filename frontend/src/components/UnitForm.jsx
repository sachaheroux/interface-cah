import React, { useState, useEffect } from 'react'
import { X, Save, User, Home, Calendar, Phone, Mail, UserCheck, Plus, Search, Trash2, Edit } from 'lucide-react'
import { getUnitTypeLabel } from '../types/unit'
import { unitsService } from '../services/api'

export default function UnitForm({ unit, isOpen, onClose, onSave, buildings = [], selectedBuilding = null }) {
  const [formData, setFormData] = useState({
    id_immeuble: null,
    adresse_unite: '',
    type: '4 1/2',
    nbr_chambre: 1,
    nbr_salle_de_bain: 1
  })

  const [loading, setLoading] = useState(false)
  const [assignedTenants, setAssignedTenants] = useState([])
  const [loadingTenants, setLoadingTenants] = useState(false)
  
  // États pour la recherche d'immeuble
  const [buildingSearch, setBuildingSearch] = useState('')
  const [filteredBuildings, setFilteredBuildings] = useState([])
  const [showBuildingDropdown, setShowBuildingDropdown] = useState(false)
  const [selectedBuildingName, setSelectedBuildingName] = useState('')

  // Charger les locataires assignés à cette unité
  useEffect(() => {
    const fetchAssignedTenants = async () => {
      if (!unit?.id) return
      
      try {
        setLoadingTenants(true)
        const response = await unitsService.getUnitTenants(unit.id)
        console.log('🐛 DEBUG - UnitForm: Assigned tenants for unit:', unit.id, response.data)
        
        // Vérifier les IDs des locataires
        if (response.data) {
          response.data.forEach((tenant, index) => {
            console.log(`🐛 DEBUG - UnitForm: Tenant ${index}:`, {
              tenant: tenant,
              tenantId: tenant.id,
              tenantIdType: typeof tenant.id,
              tenantJSON: JSON.stringify(tenant, null, 2)
            })
          })
        }
        
        setAssignedTenants(response.data || [])
      } catch (error) {
        console.error('❌ UnitForm: Error loading assigned tenants:', error)
        setAssignedTenants([])
      } finally {
        setLoadingTenants(false)
      }
    }
    
    if (isOpen && unit) {
      console.log('🐛 DEBUG - UnitForm: fetchAssignedTenants pour unité:', unit.id)
      fetchAssignedTenants()
    }
  }, [isOpen, unit])

  useEffect(() => {
    console.log('🔄 UnitForm: Initialisation du formulaire')
    console.log('  - unit:', unit)
    console.log('  - selectedBuilding:', selectedBuilding)
    console.log('  - buildings:', buildings)
    console.log('  - buildings.length:', buildings?.length)
    
    if (unit) {
      console.log('🔄 UnitForm: Chargement des données unité:', {
        unitId: unit.id
      })
      
      const buildingId = unit.id_immeuble || unit.buildingId || null
      setFormData({
        id_immeuble: buildingId,
        adresse_unite: unit.adresse_unite || unit.unitAddress || '',
        type: unit.type || '4 1/2',
        nbr_chambre: unit.nbr_chambre || unit.bedrooms || 1,
        nbr_salle_de_bain: unit.nbr_salle_de_bain || unit.bathrooms || 1,
      })
      
      // Trouver et définir le nom de l'immeuble sélectionné
      if (buildingId && buildings.length > 0) {
        const building = buildings.find(b => b.id_immeuble === buildingId)
        if (building) {
          setSelectedBuildingName(`${building.nom_immeuble || building.name} - ${building.adresse || building.address?.street || ''}`)
        }
      }
      
      console.log('✅ UnitForm: FormData chargé')
    } else if (selectedBuilding) {
      // Création d'une nouvelle unité pour un immeuble spécifique
      console.log('🔄 UnitForm: Création d\'une unité pour immeuble spécifique:', selectedBuilding)
      setFormData({
        id_immeuble: selectedBuilding.id_immeuble,
        adresse_unite: '',
        type: '4 1/2',
        nbr_chambre: 1,
        nbr_salle_de_bain: 1,
      })
      setSelectedBuildingName(`${selectedBuilding.nom_immeuble || selectedBuilding.name} - ${selectedBuilding.adresse || selectedBuilding.address?.street || ''}`)
    } else {
      // Création d'une nouvelle unité (sans immeuble pré-sélectionné)
      console.log('🔄 UnitForm: Création d\'une unité sans immeuble pré-sélectionné')
      setFormData({
        id_immeuble: null,
        adresse_unite: '',
        type: '4 1/2',
        nbr_chambre: 1,
        nbr_salle_de_bain: 1,
      })
      setSelectedBuildingName('')
    }
  }, [unit, selectedBuilding, buildings])

  // Fermer le dropdown quand on clique en dehors
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showBuildingDropdown && !event.target.closest('.building-search-container')) {
        setShowBuildingDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showBuildingDropdown])

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // Fonction pour filtrer les immeubles basée sur la recherche
  const filterBuildings = (searchTerm) => {
    if (!searchTerm.trim()) {
      setFilteredBuildings([])
      return
    }
    
    const filtered = buildings.filter(building => {
      const buildingName = building.nom_immeuble || building.name || ''
      const buildingAddress = building.adresse || building.address?.street || ''
      const searchLower = searchTerm.toLowerCase()
      
      return buildingName.toLowerCase().includes(searchLower) || 
             buildingAddress.toLowerCase().includes(searchLower)
    })
    
    setFilteredBuildings(filtered)
  }

  // Gestion de la recherche d'immeuble
  const handleBuildingSearch = (value) => {
    setBuildingSearch(value)
    filterBuildings(value)
    setShowBuildingDropdown(true)
  }

  // Sélection d'un immeuble
  const handleBuildingSelect = (building) => {
    setFormData(prev => ({
      ...prev,
      id_immeuble: building.id_immeuble
    }))
    setSelectedBuildingName(`${building.nom_immeuble || building.name} - ${building.adresse || building.address?.street || ''}`)
    setBuildingSearch('')
    setShowBuildingDropdown(false)
  }

  // Effacer la sélection d'immeuble
  const clearBuildingSelection = () => {
    setFormData(prev => ({
      ...prev,
      id_immeuble: null
    }))
    setSelectedBuildingName('')
    setBuildingSearch('')
    setShowBuildingDropdown(false)
  }


  const handleRemoveTenant = async (tenantId) => {
    console.log('🐛 DEBUG - UnitForm handleRemoveTenant appelé avec tenantId:', tenantId, typeof tenantId)
    console.log('🐛 DEBUG - UnitForm assignedTenants:', assignedTenants)
    
    if (!tenantId) {
      console.error('❌ UnitForm: tenantId est undefined ou null')
      alert('Erreur: Impossible de supprimer le locataire - ID manquant')
      return
    }
    
    if (window.confirm('Êtes-vous sûr de vouloir retirer ce locataire de l\'unité ?')) {
      try {
        console.log('🔗 UnitForm: Suppression du locataire ID:', tenantId)
        await unitsService.removeTenantFromUnit(tenantId)
        setAssignedTenants(prev => prev.filter(tenant => tenant.id !== tenantId))
        console.log('✅ UnitForm: Locataire supprimé avec succès')
      } catch (error) {
        console.error('❌ UnitForm: Error removing tenant from unit:', error)
        alert('Erreur lors de la suppression du locataire')
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validation pour la création d'unité
    if (!unit && !formData.id_immeuble) {
      alert('Veuillez sélectionner un immeuble')
      return
    }
    
    if (!formData.adresse_unite.trim()) {
      alert('Veuillez saisir l\'adresse de l\'unité')
      return
    }
    
    try {
      setLoading(true)
      const unitData = {
        ...formData,
        id: unit?.id || Date.now(),
        buildingId: unit?.buildingId || formData.id_immeuble,
        buildingName: unit?.buildingName,
        address: unit?.address,
        createdAt: unit?.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }

      console.log('💾 UnitForm: Sauvegarde unitData:', {
        unitId: unitData.id,
        unitData: unitData
      })

      // Utiliser le service API pour mettre à jour l'unité
      if (unit?.id) {
        // Mise à jour d'une unité existante
        // Convertir l'ID en entier si c'est un string comme "1-1"
        let unitId = unit.id
        if (typeof unitId === 'string' && unitId.includes('-')) {
          // Extraire le premier nombre de l'ID (ex: "1-1" -> 1)
          unitId = parseInt(unitId.split('-')[0])
        }
        
        console.log('🔄 UnitForm: ID original:', unit.id, 'ID converti:', unitId)
        
        const response = await unitsService.updateUnit(unitId, unitData)
        console.log('✅ UnitForm: Unité mise à jour via API:', response.data)
        
        // Notifier le parent que les données ont été mises à jour
        if (onSave) {
          await onSave(response.data)
        }
      } else {
        // Création d'une nouvelle unité
        await onSave(unitData)
        console.log('✅ UnitForm: Nouvelle unité créée')
      }
      
      onClose()
    } catch (error) {
      console.error('❌ UnitForm: Error saving unit:', error)
    } finally {
      setLoading(false)
    }
  }


  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">
            {unit ? `Modifier l'Unité ${unit.unitNumber || unit.adresse_unite}` : 'Nouvelle Unité'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-8">
          {/* Informations de base */}
          <div className="space-y-4">
            <div className="flex items-center mb-4">
              <Home className="h-5 w-5 text-primary-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Informations de Base</h3>
            </div>
            
            {/* Sélection d'immeuble (seulement pour la création) */}
            {!unit && (
              <div className="relative building-search-container">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Immeuble *
                </label>
                
                {/* Affichage de l'immeuble sélectionné */}
                {selectedBuildingName && (
                  <div className="mb-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Home className="h-4 w-4 text-blue-600 mr-2" />
                        <span className="text-sm font-medium text-blue-900">{selectedBuildingName}</span>
                      </div>
                      <button
                        type="button"
                        onClick={clearBuildingSelection}
                        className="text-blue-600 hover:text-blue-800 transition-colors"
                        title="Changer d'immeuble"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                )}
                
                {/* Barre de recherche */}
                <div className="relative">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      type="text"
                      value={buildingSearch}
                      onChange={(e) => handleBuildingSearch(e.target.value)}
                      onFocus={() => setShowBuildingDropdown(true)}
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="Rechercher un immeuble..."
                      required={!selectedBuildingName}
                    />
                  </div>
                  
                  {/* Dropdown des résultats de recherche */}
                  {showBuildingDropdown && (buildingSearch || filteredBuildings.length > 0) && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                      {filteredBuildings.length === 0 ? (
                        <div className="p-3 text-sm text-gray-500 text-center">
                          {buildingSearch ? 'Aucun immeuble trouvé' : 'Commencez à taper pour rechercher...'}
                        </div>
                      ) : (
                        filteredBuildings.map((building) => (
                          <div
                            key={building.id_immeuble}
                            onClick={() => handleBuildingSelect(building)}
                            className="p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                          >
                            <div className="flex items-start">
                              <Home className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 truncate">
                                  {building.nom_immeuble || building.name}
                                </p>
                                <p className="text-xs text-gray-500 truncate">
                                  {building.adresse || building.address?.street || ''}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Adresse de l'unité *
              </label>
              <input
                type="text"
                value={formData.adresse_unite}
                onChange={(e) => handleInputChange('adresse_unite', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Ex: 56 rue Vachon, Apt 101"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type d'unité
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => handleInputChange('type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="1 1/2">1 1/2</option>
                  <option value="2 1/2">2 1/2</option>
                  <option value="3 1/2">3 1/2</option>
                  <option value="4 1/2">4 1/2</option>
                  <option value="5 1/2">5 1/2</option>
                  <option value="6 1/2">6 1/2</option>
                  <option value="7 1/2">7 1/2</option>
                  <option value="8 1/2">8 1/2</option>
                  <option value="9 1/2">9 1/2</option>
                  <option value="10 1/2">10 1/2</option>
                  <option value="11 1/2">11 1/2</option>
                  <option value="12 1/2">12 1/2</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre de chambres
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={formData.nbr_chambre}
                  onChange={(e) => handleInputChange('nbr_chambre', parseInt(e.target.value) || 1)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre de salles de bain
                </label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  step="0.5"
                  value={formData.nbr_salle_de_bain}
                  onChange={(e) => handleInputChange('nbr_salle_de_bain', parseFloat(e.target.value) || 1)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
          </div>


          {/* Locataires assignés */}
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <User className="h-5 w-5 text-primary-600 mr-2" />
                <h3 className="text-lg font-semibold text-gray-900">Locataires Assignés</h3>
              </div>
              <span className="text-sm text-gray-500">
                {assignedTenants.length} / 4 locataires
              </span>
            </div>
            
            {loadingTenants ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                <span className="ml-2 text-gray-600">Chargement des locataires...</span>
              </div>
            ) : assignedTenants.length > 0 ? (
              <div className="space-y-3">
                {assignedTenants.map((tenant, index) => (
                  <div key={tenant.id || index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <User className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="font-medium text-gray-900">{tenant.name}</span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                          {tenant.email && (
                            <div className="flex items-center">
                              <Mail className="h-4 w-4 mr-2" />
                              <span>{tenant.email}</span>
                            </div>
                          )}
                          
                          {tenant.phone && (
                            <div className="flex items-center">
                              <Phone className="h-4 w-4 mr-2" />
                              <span>{tenant.phone}</span>
                            </div>
                          )}
                          
                          {tenant.moveInDate && (
                            <div className="flex items-center">
                              <Calendar className="h-4 w-4 mr-2" />
                              <span>Emménagement: {new Date(tenant.moveInDate).toLocaleDateString('fr-CA')}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex space-x-2 ml-4">
                        <button
                          type="button"
                          onClick={() => handleRemoveTenant(tenant.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Retirer de l'unité"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 border border-gray-200 rounded-lg bg-gray-50">
                <User className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 font-medium">Aucun locataire assigné</p>
                <p className="text-sm text-gray-400">
                  Les locataires sont assignés via la gestion des locataires
                </p>
              </div>
            )}
          </div>


          {/* Boutons d'action */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors flex items-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              {unit ? 'Mettre à jour' : 'Créer l\'Unité'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
} 