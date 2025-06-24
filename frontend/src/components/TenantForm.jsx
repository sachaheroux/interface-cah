import React, { useState, useEffect } from 'react'
import { X, Save, User, Mail, Phone, MapPin, DollarSign, FileText, UserCheck, Home } from 'lucide-react'
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
      const response = await unitsService.getAvailableUnits()
      console.log('Available units:', response.data)
      setAvailableUnits(response.data || [])
    } catch (error) {
      console.error('Error loading available units:', error)
      setAvailableUnits([])
    } finally {
      setLoadingUnits(false)
    }
  }

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

  const handleUnitSelection = (e) => {
    const selectedUnitId = e.target.value
    const selectedUnit = availableUnits.find(unit => unit.id === selectedUnitId)
    
    setFormData(prev => ({
      ...prev,
      unitId: selectedUnitId,
      unitInfo: selectedUnit || null,
      building: selectedUnit?.buildingName || '',
      unit: selectedUnit?.unitNumber || ''
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
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Home className="h-5 w-5 mr-2" />
              Unité de Résidence
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sélectionner une unité
                </label>
                {loadingUnits ? (
                  <div className="flex items-center justify-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                    <span className="ml-2 text-gray-600">Chargement des unités...</span>
                  </div>
                ) : (
                  <select
                    value={formData.unitId}
                    onChange={handleUnitSelection}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">Sélectionner une unité...</option>
                    {availableUnits.map(unit => (
                      <option key={unit.id} value={unit.id}>
                        {unit.buildingName} - Unité {unit.unitNumber} ({unit.address})
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {formData.unitInfo && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center mb-2">
                    <MapPin className="h-4 w-4 text-blue-600 mr-2" />
                    <span className="font-medium text-blue-900">Unité sélectionnée</span>
                  </div>
                  <div className="text-sm text-blue-800">
                    <p><strong>Immeuble:</strong> {formData.unitInfo.buildingName}</p>
                    <p><strong>Unité:</strong> {formData.unitInfo.unitNumber}</p>
                    <p><strong>Adresse:</strong> {formData.unitInfo.address}</p>
                  </div>
                </div>
              )}

              {availableUnits.length === 0 && !loadingUnits && (
                <p className="text-sm text-gray-500 mt-1">
                  Aucune unité disponible. Toutes les unités sont occupées ou en maintenance.
                </p>
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