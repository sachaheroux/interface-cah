import React, { useState, useEffect } from 'react'
import { X, Save, User, Mail, Phone, MapPin, DollarSign, FileText, UserCheck, Home, Search, AlertTriangle } from 'lucide-react'
import { TenantStatus, getTenantStatusLabel, getRelationshipLabel } from '../types/tenant'
import { unitsService } from '../services/api'

export default function TenantForm({ tenant, isOpen, onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    status: TenantStatus.ACTIVE,
    
    unitId: '',
    unitInfo: null,
    
    emergencyContact: {
      name: '',
      phone: '',
      email: '',
      relationship: ''
    },
    
    financial: {
      monthlyIncome: 0,
      creditScore: 0,
      bankAccount: '',
      employer: '',
      employerPhone: ''
    },
    
    notes: ''
  })

  const [loading, setLoading] = useState(false)
  const [availableUnits, setAvailableUnits] = useState([])
  const [loadingUnits, setLoadingUnits] = useState(false)
  const [unitSearchTerm, setUnitSearchTerm] = useState('')
  const [filteredUnits, setFilteredUnits] = useState([])

  useEffect(() => {
    if (tenant) {
      setFormData({
        name: tenant.name || '',
        email: tenant.email || '',
        phone: tenant.phone || '',
        status: tenant.status || TenantStatus.ACTIVE,
        
        unitId: tenant.unitId || '',
        unitInfo: tenant.unitInfo || null,
        
        emergencyContact: {
          name: tenant.emergencyContact?.name || '',
          phone: tenant.emergencyContact?.phone || '',
          email: tenant.emergencyContact?.email || '',
          relationship: tenant.emergencyContact?.relationship || ''
        },
        
        financial: {
          monthlyIncome: tenant.financial?.monthlyIncome || 0,
          creditScore: tenant.financial?.creditScore || 0,
          bankAccount: tenant.financial?.bankAccount || '',
          employer: tenant.financial?.employer || '',
          employerPhone: tenant.financial?.employerPhone || ''
        },
        
        notes: tenant.notes || ''
      })
    } else {
      setFormData({
        name: '',
        email: '',
        phone: '',
        status: TenantStatus.ACTIVE,
        unitId: '',
        unitInfo: null,
        emergencyContact: {
          name: '',
          phone: '',
          email: '',
          relationship: ''
        },
        financial: {
          monthlyIncome: 0,
          creditScore: 0,
          bankAccount: '',
          employer: '',
          employerPhone: ''
        },
        notes: ''
      })
    }
  }, [tenant, isOpen])

  useEffect(() => {
    if (isOpen) {
      loadAvailableUnits()
    }
  }, [isOpen])

  const loadAvailableUnits = async () => {
    try {
      setLoadingUnits(true)
      const response = await unitsService.getUnits() // Charger TOUTES les unités, pas seulement disponibles
      console.log('All units:', response.data)
      
      // Enrichir les unités avec les informations des locataires actuels
      const unitsWithTenants = await Promise.all(
        (response.data || []).map(async (unit) => {
          try {
            const assignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
            const unitAssignments = assignments.filter(a => a.unitId === unit.id)
            
            const currentTenants = unitAssignments.map(assignment => ({
              id: assignment.tenantId,
              name: assignment.tenantData.name,
              email: assignment.tenantData.email,
              phone: assignment.tenantData.phone
            }))
            
            return {
              ...unit,
              currentTenants,
              isOccupied: currentTenants.length > 0
            }
          } catch (error) {
            console.error('Error loading tenants for unit:', unit.id, error)
            return {
              ...unit,
              currentTenants: [],
              isOccupied: false
            }
          }
        })
      )
      
      setAvailableUnits(unitsWithTenants)
    } catch (error) {
      console.error('Error loading units:', error)
      setAvailableUnits([])
    } finally {
      setLoadingUnits(false)
    }
  }

  // Filtrer les unités selon le terme de recherche
  useEffect(() => {
    if (!unitSearchTerm.trim()) {
      setFilteredUnits(availableUnits.slice(0, 20)) // Limiter à 20 unités par défaut
      return
    }

    const searchLower = unitSearchTerm.toLowerCase()
    const filtered = availableUnits.filter(unit => {
      return (
        unit.buildingName?.toLowerCase().includes(searchLower) ||
        unit.address?.toLowerCase().includes(searchLower) ||
        unit.unitNumber?.toString().toLowerCase().includes(searchLower) ||
        unit.type?.toLowerCase().includes(searchLower)
      )
    })

    setFilteredUnits(filtered.slice(0, 50)) // Limiter à 50 résultats
  }, [unitSearchTerm, availableUnits])

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleNestedChange = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }))
  }

  const handleUnitSelection = (unit) => {
    setFormData(prev => ({
      ...prev,
      unitId: unit?.id || '',
      unitInfo: unit || null,
      building: unit?.buildingName || '',
      unit: unit?.unitNumber || ''
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      setLoading(true)
      
      // Préparer les données à sauvegarder
      const tenantData = {
        ...formData,
        id: tenant?.id || Date.now(),
        createdAt: tenant?.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }

      // Si une unité est sélectionnée, assigner le locataire à l'unité
      if (formData.unitId && formData.unitInfo) {
        try {
          await unitsService.assignTenantToUnit(
            formData.unitId,
            tenantData.id,
            {
              name: tenantData.name,
              email: tenantData.email,
              phone: tenantData.phone,
              moveInDate: new Date().toISOString(),
              moveOutDate: null
            }
          )
          console.log('Tenant assigned to unit successfully')
        } catch (assignError) {
          console.error('Error assigning tenant to unit:', assignError)
          // Continuer même si l'assignation échoue
        }
      }

      await onSave(tenantData)
      onClose()
    } catch (error) {
      console.error('Error saving tenant:', error)
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

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {tenant ? 'Modifier le locataire' : 'Nouveau locataire'}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Informations complètes du locataire
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-8">
          {/* Informations personnelles */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Informations personnelles
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom complet *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Téléphone
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="(514) 555-0123"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Statut
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => handleInputChange('status', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  {Object.values(TenantStatus).map(status => (
                    <option key={status} value={status}>
                      {getTenantStatusLabel(status)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Sélection d'unité */}
          <div className="space-y-4">
            <div className="flex items-center mb-4">
              <Home className="h-5 w-5 text-primary-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Unité de Résidence</h3>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rechercher et sélectionner une unité
              </label>
              {loadingUnits ? (
                <div className="flex items-center justify-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                  <span className="ml-2 text-gray-600">Chargement des unités...</span>
                </div>
              ) : (
                <div className="space-y-3">
                  {/* Barre de recherche */}
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <input
                      type="text"
                      placeholder="Rechercher par adresse, immeuble ou numéro d'unité..."
                      value={unitSearchTerm}
                      onChange={(e) => setUnitSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>

                  {/* Liste des unités filtrées */}
                  <div className="max-h-60 overflow-y-auto border border-gray-200 rounded-lg">
                    {filteredUnits.length > 0 ? (
                      <div className="divide-y divide-gray-200">
                        {filteredUnits.map(unit => (
                          <div
                            key={unit.id}
                            onClick={() => handleUnitSelection(unit)}
                            className={`p-3 cursor-pointer hover:bg-gray-50 transition-colors ${
                              formData.unitId === unit.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                            }`}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center">
                                  <Home className="h-4 w-4 text-gray-400 mr-2" />
                                  <span className="font-medium text-gray-900">
                                    {unit.address}
                                  </span>
                                  {formData.unitId === unit.id && (
                                    <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                      Sélectionnée
                                    </span>
                                  )}
                                </div>
                                <p className="text-sm text-gray-600 mt-1">{unit.buildingName}</p>
                                
                                {/* Afficher les locataires actuels s'il y en a */}
                                {unit.currentTenants && unit.currentTenants.length > 0 && (
                                  <div className="mt-2">
                                    <p className="text-xs text-gray-500">Locataires actuels:</p>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {unit.currentTenants.map((tenant, index) => (
                                        <span key={index} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                          {tenant.name}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                              
                              <div className="text-right text-sm text-gray-500">
                                <div>{unit.type || 'N/A'}</div>
                                {unit.rental?.monthlyRent && (
                                  <div className="font-medium text-gray-900">{unit.rental.monthlyRent} $/mois</div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : unitSearchTerm ? (
                      <div className="p-4 text-center text-gray-500">
                        <Search className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                        <p>Aucune unité trouvée pour "{unitSearchTerm}"</p>
                        <p className="text-sm">Essayez avec un autre terme de recherche</p>
                      </div>
                    ) : (
                      <div className="p-4 text-center text-gray-500">
                        <Home className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                        <p>Tapez pour rechercher une unité</p>
                      </div>
                    )}
                  </div>

                  {/* Unité sélectionnée - Aperçu détaillé */}
                  {formData.unitInfo && (
                    <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-center mb-3">
                        <MapPin className="h-5 w-5 text-blue-600 mr-2" />
                        <span className="font-medium text-blue-900">Unité sélectionnée</span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-blue-800"><strong>Adresse:</strong> {formData.unitInfo.address}</p>
                          <p className="text-blue-800"><strong>Immeuble:</strong> {formData.unitInfo.buildingName}</p>
                          <p className="text-blue-800"><strong>Type:</strong> {formData.unitInfo.type || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-blue-800"><strong>Superficie:</strong> {formData.unitInfo.area ? `${formData.unitInfo.area} pi²` : 'N/A'}</p>
                          {formData.unitInfo.rental?.monthlyRent && (
                            <p className="text-blue-800"><strong>Loyer:</strong> {formData.unitInfo.rental.monthlyRent} $/mois</p>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Bouton pour désélectionner */}
                  {formData.unitId && (
                    <button
                      type="button"
                      onClick={() => handleUnitSelection(null)}
                      className="text-sm text-red-600 hover:text-red-700 flex items-center"
                    >
                      <X className="h-4 w-4 mr-1" />
                      Désélectionner l'unité
                    </button>
                  )}
                </div>
              )}
              
              {availableUnits.length === 0 && !loadingUnits && (
                <div className="p-4 text-center text-gray-500 border border-gray-200 rounded-lg">
                  <AlertTriangle className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p className="font-medium">Aucune unité disponible</p>
                  <p className="text-sm">Toutes les unités sont actuellement occupées.</p>
                </div>
              )}
            </div>
          </div>

          {/* Contact d'urgence */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <UserCheck className="h-5 w-5 mr-2" />
              Contact d'urgence
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom
                </label>
                <input
                  type="text"
                  value={formData.emergencyContact.name}
                  onChange={(e) => handleNestedChange('emergencyContact', 'name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Téléphone
                </label>
                <input
                  type="tel"
                  value={formData.emergencyContact.phone}
                  onChange={(e) => handleNestedChange('emergencyContact', 'phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.emergencyContact.email}
                  onChange={(e) => handleNestedChange('emergencyContact', 'email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Relation
                </label>
                <select
                  value={formData.emergencyContact.relationship}
                  onChange={(e) => handleNestedChange('emergencyContact', 'relationship', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Sélectionner...</option>
                  <option value="parent">Parent</option>
                  <option value="conjoint">Conjoint(e)</option>
                  <option value="enfant">Enfant</option>
                  <option value="frere_soeur">Frère/Sœur</option>
                  <option value="ami">Ami(e)</option>
                  <option value="collegue">Collègue</option>
                  <option value="autre">Autre</option>
                </select>
              </div>
            </div>
          </div>

          {/* Informations financières */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <DollarSign className="h-5 w-5 mr-2" />
              Informations financières
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Revenu mensuel
                </label>
                <input
                  type="number"
                  value={formData.financial.monthlyIncome}
                  onChange={(e) => handleNestedChange('financial', 'monthlyIncome', parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formatCurrency(formData.financial.monthlyIncome)}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cote de crédit
                </label>
                <input
                  type="number"
                  min="300"
                  max="900"
                  value={formData.financial.creditScore}
                  onChange={(e) => handleNestedChange('financial', 'creditScore', parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="700"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Compte bancaire
                </label>
                <input
                  type="text"
                  value={formData.financial.bankAccount}
                  onChange={(e) => handleNestedChange('financial', 'bankAccount', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Banque Nationale - ****1234"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Employeur
                </label>
                <input
                  type="text"
                  value={formData.financial.employer}
                  onChange={(e) => handleNestedChange('financial', 'employer', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Téléphone employeur
                </label>
                <input
                  type="tel"
                  value={formData.financial.employerPhone}
                  onChange={(e) => handleNestedChange('financial', 'employerPhone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
          </div>

          {/* Notes */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Notes et commentaires
            </h3>
            <textarea
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Notes additionnelles, préférences, historique, etc."
            />
          </div>

          {/* Boutons d'action */}
          <div className="flex justify-end space-x-4 pt-6 border-t">
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
              className="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors flex items-center disabled:opacity-50"
            >
              <Save className="h-4 w-4 mr-2" />
              {loading ? 'Sauvegarde...' : 'Sauvegarder'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
} 