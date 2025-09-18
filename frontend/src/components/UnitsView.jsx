import React, { useState, useEffect } from 'react'
import { 
  Users, MapPin, Eye, Edit3, Trash2, Search, Filter, Home, Mail, Phone, DollarSign, 
  Building2, Bed, Bath, Car, Wifi, Wind, CheckCircle, Clock, AlertCircle, UserMinus, Plus
} from 'lucide-react'
import { getUnitTypeLabel } from '../types/unit'
import { assignmentsService, unitsService, tenantsService } from '../services/api'
import UnitForm from './UnitForm'
import UnitDetails from './UnitDetails'
import { buildingsService } from '../services/api'

export default function UnitsView({ buildings, onBuildingUpdated }) {
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
  
  // États pour la création d'unité
  const [showAddUnitForm, setShowAddUnitForm] = useState(false)
  const [selectedBuildingForUnit, setSelectedBuildingForUnit] = useState(null)

  // Charger les locataires depuis le backend
  const loadTenants = async () => {
    try {
      setLoadingAssignments(true)
      const response = await tenantsService.getTenants()
      const tenantsData = response.data || []
      setAssignments(tenantsData) // Utiliser les locataires comme "assignments"
    } catch (error) {
      console.error('Error loading tenants:', error)
      setAssignments([])
    } finally {
      setLoadingAssignments(false)
    }
  }

  // Recharger les unités : d'abord depuis Render, sinon générer depuis les immeubles
  const reloadUnits = async () => {
    try {
      console.log('🔄 UnitsView: Rechargement des unités...')
      
      // 1. Essayer de récupérer les unités depuis Render
      let unitsFromRender = []
      try {
        const response = await unitsService.getUnits()
        unitsFromRender = response.data || []
        console.log('✅ UnitsView: Unités récupérées depuis Render:', unitsFromRender.length)
      } catch (error) {
        console.log('⚠️ UnitsView: Aucune unité sur Render, génération depuis les immeubles')
        unitsFromRender = []
      }
      
      // 2. Si pas d'unités sur Render, utiliser un tableau vide
      if (unitsFromRender.length === 0) {
        console.log('🔄 UnitsView: Aucune unité trouvée sur Render, utilisation d\'un tableau vide')
        unitsFromRender = []
      }
      
      // 3. Calculer le statut et ajouter les locataires à chaque unité
      const unitsWithStatus = unitsFromRender.map(unit => {
        // Trouver les locataires pour cette unité
        const unitTenants = assignments.filter(tenant => tenant.id_unite === unit.id_unite)
        
        const currentTenants = unitTenants.map(tenant => ({
          id: tenant.id_locataire,
          nom: tenant.nom,
          prenom: tenant.prenom,
          email: tenant.email,
          telephone: tenant.telephone,
          statut: tenant.statut
        }))
        
        // Trouver l'immeuble parent pour obtenir le nom et l'adresse complète
        const parentBuilding = buildings.find(b => b.id_immeuble === unit.id_immeuble)
        const buildingName = parentBuilding?.nom_immeuble || ''
        
        // Utiliser l'adresse de l'unité
        let simpleAddress = unit.adresse_unite || `${unit.type}`
        
        // Adresse complète avec ville et code postal (pour l'affichage détaillé)
        let fullAddress = simpleAddress
        if (parentBuilding?.ville && parentBuilding?.code_postal) {
          fullAddress = `${simpleAddress}, ${parentBuilding.ville} ${parentBuilding.code_postal}`
        }
        
        return {
          ...unit,
          // Mapping des propriétés pour l'affichage
          address: fullAddress, // Adresse complète pour l'affichage détaillé
          buildingName: buildingName,
          // Titre simple pour l'en-tête de la carte (sans ville/code postal)
          simpleTitle: simpleAddress,
          status: unit.currentTenants?.length > 0 ? 'occupied' : 'vacant',
          currentTenants: currentTenants
        }
      })
      
      setUnits(unitsWithStatus)
      setFilteredUnits(unitsWithStatus)
      console.log('✅ UnitsView: Unités finales chargées:', unitsWithStatus.length)
    } catch (error) {
      console.error('❌ UnitsView: Erreur lors du rechargement des unités:', error)
    }
  }

  // Charger les unités et les assignations
  useEffect(() => {
    loadTenants()
    
    // Écouter l'événement de suppression de locataire
    const handleTenantDeleted = (event) => {
      console.log(`📢 Événement tenantDeleted reçu:`, event.detail)
      console.log(`🔄 Rechargement des assignations suite à la suppression...`)
      loadTenants()
    }
    
    window.addEventListener('tenantDeleted', handleTenantDeleted)
    
    return () => {
      window.removeEventListener('tenantDeleted', handleTenantDeleted)
    }
  }, [])

  useEffect(() => {
    if (loadingAssignments) return // Attendre que les assignations soient chargées
    
    // Charger les unités depuis Render
    reloadUnits()
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
      console.log('✅ UnitsView: Unité sauvegardée par UnitForm, rechargement des données')

      // Notifier le parent pour recharger les données
      if (onBuildingUpdated && typeof onBuildingUpdated === 'function') {
        onBuildingUpdated(updatedUnit.buildingId)
      } else {
        console.warn('⚠️ UnitsView: onBuildingUpdated not available, skipping refresh')
      }

      // Fermer le formulaire
      setShowForm(false)
      setSelectedUnit(null)
      
      console.log('✅ UnitsView: Interface mise à jour avec succès')
      
    } catch (error) {
      console.error('❌ UnitsView: Erreur lors de la mise à jour:', error)
      throw error
    }
  }

  const handleDeleteUnit = async (unit) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer l'unité "${unit.adresse_unite}" ?`)) {
      try {
        console.log(`🗑️ Suppression de l'unité: ${unit.adresse_unite} (ID: ${unit.id_unite})`)
        
        // Supprimer via l'API
        await unitsService.deleteUnit(unit.id_unite)
        
        // Recharger les unités
        await reloadUnits()
        
        // Fermer les modales
        setShowDetails(false)
        setSelectedUnit(null)
        
        console.log(`✅ Unité ${unit.adresse_unite} supprimée avec succès`)
        
        // Déclencher un événement pour actualiser les autres vues
        window.dispatchEvent(new CustomEvent('unitDeleted', { 
          detail: { unitId: unit.id_unite, unitAddress: unit.adresse_unite } 
        }))
        
      } catch (error) {
        console.error('❌ Erreur lors de la suppression:', error)
        alert(`Erreur lors de la suppression de l'unité "${unit.adresse_unite}". Vérifiez la console pour plus de détails.`)
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

  // Gestionnaires pour la création d'unité
  const handleAddUnit = () => {
    setSelectedBuildingForUnit(null)
    setShowAddUnitForm(true)
  }

  const handleAddUnitToBuilding = (building) => {
    setSelectedBuildingForUnit(building)
    setShowAddUnitForm(true)
  }

  const handleSaveNewUnit = async (unitData) => {
    try {
      console.log('💾 UnitsView: Sauvegarde nouvelle unité:', unitData)
      
      // Créer l'unité via l'API
      const response = await unitsService.createUnit(unitData)
      console.log('✅ UnitsView: Unité créée via API:', response.data)
      
      // Recharger les unités
      await reloadUnits()
      
      // Fermer le formulaire
      setShowAddUnitForm(false)
      setSelectedBuildingForUnit(null)
      
      console.log('✅ UnitsView: Interface mise à jour avec succès')
      
    } catch (error) {
      console.error('❌ UnitsView: Erreur lors de la création de l\'unité:', error)
      throw error
    }
  }

  const handleCloseAddUnitForm = () => {
    setShowAddUnitForm(false)
    setSelectedBuildingForUnit(null)
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount || 0)
  }

  const handleRemoveFromUnit = async (tenantId, unitId, tenantName, unitName, event) => {
    // Empêcher la propagation de l'événement vers les éléments parents
    if (event) {
      event.stopPropagation()
      event.preventDefault()
    }
    
    console.log('🐛 DEBUG - handleRemoveFromUnit appelé avec:', {
      tenantId,
      unitId,
      tenantName,
      unitName,
      typeof_tenantId: typeof tenantId,
      typeof_unitId: typeof unitId
    })

    // Vérifier les IDs valides
    if (!tenantId || !unitId) {
      console.error('❌ Erreur: IDs manquants', { tenantId, unitId })
      alert('Erreur: Impossible de supprimer l\'assignation - données manquantes')
      return
    }

    const confirmMessage = `Êtes-vous sûr de vouloir retirer "${tenantName}" de l'unité "${unitName}" ?\n\nLe locataire restera dans le système, seule l'assignation à cette unité sera supprimée.`

    if (window.confirm(confirmMessage)) {
      try {
        console.log(`🔗 Suppression assignation: ${tenantName} (${tenantId}) de ${unitName} (${unitId})`)

        const result = await assignmentsService.removeSpecificAssignment(tenantId, unitId)
        console.log('🔄 Résultat de removeSpecificAssignment:', result)

        console.log(`✅ ${tenantName} retiré de ${unitName} avec succès`)

        // Recharger les assignations pour mettre à jour l'affichage
        console.log('🔄 Rechargement des assignations...')
        await loadTenants()
        console.log('✅ Assignations rechargées')

        // Déclencher un événement pour mettre à jour les autres vues
        console.log('📢 Déclenchement événement assignmentRemoved...')
        window.dispatchEvent(new CustomEvent('assignmentRemoved', {
          detail: { tenantId, unitId, tenantName, unitName }
        }))
        console.log('✅ Événement déclenché')

      } catch (error) {
        console.error('❌ Erreur lors de la suppression de l\'assignation:', error)
        alert(`Erreur lors de la suppression de l'assignation de "${tenantName}". Vérifiez la console pour plus de détails.`)
      }
    } else {
      console.log('❌ Suppression annulée par l\'utilisateur')
    }
  }

  return (
    <div className="space-y-6">
      {/* Filtres et recherche */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Filtres et Recherche</h3>
          <button onClick={handleAddUnit} className="btn-primary flex items-center">
            <Plus className="h-4 w-4 mr-2" />
            Ajouter une Unité
          </button>
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
              <option key={building.id_immeuble} value={building.id_immeuble.toString()}>
                {building.nom_immeuble}
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
            <div key={unit.id_unite} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              {/* En-tête de l'unité */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <Home className="h-5 w-5 text-primary-600" />
                  </div>
                  <div className="ml-3">
                    <h4 className="font-semibold text-gray-900">{unit.adresse_unite}</h4>
                    <p className="text-sm text-gray-600">{unit.type}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${unit.locataires?.length > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {unit.locataires?.length > 0 ? 'Occupée' : 'Libre'}
                </span>
              </div>

              {/* Informations de base */}
              <div className="flex items-center text-gray-600 mb-3">
                <Bed className="h-4 w-4 mr-2" />
                <span className="text-sm">{unit.nbr_chambre} chambre{unit.nbr_chambre > 1 ? 's' : ''}</span>
                <Bath className="h-4 w-4 mr-1 ml-4" />
                <span className="text-sm">{unit.nbr_salle_de_bain} salle{unit.nbr_salle_de_bain > 1 ? 's' : ''} de bain</span>
              </div>

              {/* Loyer */}
              {unit.rental?.monthlyRent > 0 && (
                <div className="flex items-center text-gray-600 mb-3">
                  <DollarSign className="h-4 w-4 mr-2" />
                  <span className="text-sm font-medium">{formatCurrency(unit.rental.monthlyRent)}/mois</span>
                </div>
              )}

              {/* Locataires */}
              {unit.locataires?.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-3 mb-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <Users className="h-4 w-4 mr-2 text-gray-600" />
                      <span className="text-sm font-medium text-gray-900">Locataires</span>
                    </div>
                    <span className="text-xs text-gray-500">{unit.locataires.length} locataire{unit.locataires.length > 1 ? 's' : ''}</span>
                  </div>
                  
                  {/* Liste des locataires */}
                  <div className="space-y-2">
                    {unit.locataires.map((tenant, tenantIndex) => (
                      <div key={tenant.id_locataire} className="bg-white rounded-md p-2 border border-gray-200">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="font-medium text-sm text-gray-900">{tenant.nom} {tenant.prenom}</div>
                            <div className="flex items-center mt-1">
                              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                tenant.statut === 'actif' ? 'bg-green-100 text-green-800' :
                                tenant.statut === 'en_attente' ? 'bg-yellow-100 text-yellow-800' :
                                tenant.statut === 'inactif' ? 'bg-gray-100 text-gray-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {tenant.statut}
                              </span>
                            </div>
                            {tenant.email && (
                              <div className="flex items-center mt-1">
                                <Mail className="h-3 w-3 mr-2 text-gray-400" />
                                <span className="text-xs text-gray-600">{tenant.email}</span>
                              </div>
                            )}
                            {tenant.telephone && (
                              <div className="flex items-center mt-1">
                                <Phone className="h-3 w-3 mr-2 text-gray-400" />
                                <span className="text-xs text-gray-600">{tenant.telephone}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex space-x-2">
                <button className="flex-1 btn-primary text-sm py-2" onClick={() => handleViewUnit(unit)}>
                  <Eye className="h-4 w-4 mr-1" />
                  Détails
                </button>
                <button className="flex-1 btn-secondary text-sm py-2" onClick={() => handleEditUnit(unit)}>
                  <Edit3 className="h-4 w-4 mr-1" />
                  Modifier
                </button>
                <button 
                  onClick={() => handleDeleteUnit(unit)} 
                  className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors text-sm"
                  title="Supprimer l'unité"
                >
                  <Trash2 className="h-4 w-4" />
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
          buildings={buildings}
        />
      )}
      {showDetails && (
        <UnitDetails
          unit={selectedUnit}
          isOpen={showDetails}
          onClose={handleCloseDetails}
          onEdit={handleEditUnit}
        />
      )}
      {showAddUnitForm && (
        <UnitForm
          unit={null}
          isOpen={showAddUnitForm}
          onSave={handleSaveNewUnit}
          onClose={handleCloseAddUnitForm}
          buildings={buildings}
          selectedBuilding={selectedBuildingForUnit}
        />
      )}
    </div>
  )
} 