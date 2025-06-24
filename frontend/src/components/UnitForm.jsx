import React, { useState, useEffect } from 'react'
import { X, Save, User, DollarSign, Home, Calendar, Phone, Mail, UserCheck, Plus, Search } from 'lucide-react'
import { UnitStatus, UnitType, getUnitTypeLabel, getUnitStatusLabel } from '../types/unit'
import { tenantsService } from '../services/api'

export default function UnitForm({ unit, isOpen, onClose, onSave }) {
  const [formData, setFormData] = useState({
    unitNumber: '',
    type: UnitType.ONE_BEDROOM,
    status: UnitStatus.VACANT,
    area: 0,
    bedrooms: 1,
    bathrooms: 1,
    rental: {
      monthlyRent: 0,
      deposit: 0,
      leaseStart: '',
      leaseEnd: '',
      rentDueDay: 1,
    },
    amenities: {
      heating: false,
      electricity: false,
      wifi: false,
      furnished: false,
      parking: false,
      laundry: false,
      airConditioning: false,
      balcony: false,
      storage: false,
      dishwasher: false,
      washerDryer: false,
    },
    tenantId: null, // ID du locataire sélectionné
    tenant: {
      name: '',
      email: '',
      phone: '',
      emergencyContact: {
        name: '',
        phone: '',
        relationship: ''
      },
      moveInDate: '',
      moveOutDate: '',
    },
    notes: ''
  })

  const [loading, setLoading] = useState(false)
  const [tenants, setTenants] = useState([])
  const [showNewTenantForm, setShowNewTenantForm] = useState(false)
  const [newTenantData, setNewTenantData] = useState({
    name: '',
    email: '',
    phone: ''
  })

  // Charger les locataires disponibles
  useEffect(() => {
    const fetchTenants = async () => {
      try {
        const response = await tenantsService.getTenants()
        console.log('Tenants API response:', response)
        
        // Gérer les différents formats de réponse
        let tenantsData = []
        if (response.data) {
          if (Array.isArray(response.data)) {
            tenantsData = response.data
          } else if (response.data.data && Array.isArray(response.data.data)) {
            tenantsData = response.data.data
          } else if (Array.isArray(response.data.tenants)) {
            tenantsData = response.data.tenants
          }
        }
        
        console.log('Processed tenants data:', tenantsData)
        setTenants(tenantsData)
      } catch (error) {
        console.error('Erreur lors du chargement des locataires:', error)
        setTenants([]) // S'assurer que c'est toujours un tableau
      }
    }
    
    if (isOpen) {
      fetchTenants()
    }
  }, [isOpen])

  useEffect(() => {
    if (unit) {
      setFormData({
        unitNumber: unit.unitNumber || '',
        type: unit.type || UnitType.ONE_BEDROOM,
        status: unit.status || UnitStatus.VACANT,
        area: unit.area || 0,
        bedrooms: unit.bedrooms || 1,
        bathrooms: unit.bathrooms || 1,
        rental: {
          monthlyRent: unit.rental?.monthlyRent || 0,
          deposit: unit.rental?.deposit || 0,
          leaseStart: unit.rental?.leaseStart || '',
          leaseEnd: unit.rental?.leaseEnd || '',
          rentDueDay: unit.rental?.rentDueDay || 1,
        },
        amenities: {
          heating: unit.amenities?.heating || false,
          electricity: unit.amenities?.electricity || false,
          wifi: unit.amenities?.wifi || false,
          furnished: unit.amenities?.furnished || false,
          parking: unit.amenities?.parking || false,
          laundry: unit.amenities?.laundry || false,
          airConditioning: unit.amenities?.airConditioning || false,
          balcony: unit.amenities?.balcony || false,
          storage: unit.amenities?.storage || false,
          dishwasher: unit.amenities?.dishwasher || false,
          washerDryer: unit.amenities?.washerDryer || false,
        },
        tenantId: unit.tenantId || null,
        tenant: {
          name: unit.tenant?.name || '',
          email: unit.tenant?.email || '',
          phone: unit.tenant?.phone || '',
          emergencyContact: {
            name: unit.tenant?.emergencyContact?.name || '',
            phone: unit.tenant?.emergencyContact?.phone || '',
            relationship: unit.tenant?.emergencyContact?.relationship || ''
          },
          moveInDate: unit.tenant?.moveInDate || '',
          moveOutDate: unit.tenant?.moveOutDate || '',
        },
        notes: unit.notes || ''
      })
    }
  }, [unit])

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

  const handleDeepNestedChange = (section, subsection, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [subsection]: {
          ...prev[section][subsection],
          [field]: value
        }
      }
    }))
  }

  // Gestion de la sélection de locataire
  const handleTenantSelect = (tenantId) => {
    if (tenantId === '') {
      // Aucun locataire sélectionné
      setFormData(prev => ({
        ...prev,
        tenantId: null,
        tenant: {
          name: '',
          email: '',
          phone: '',
          emergencyContact: { name: '', phone: '', relationship: '' },
          moveInDate: '',
          moveOutDate: '',
        }
      }))
      return
    }

    const selectedTenant = tenants.find(t => t.id.toString() === tenantId)
    if (selectedTenant) {
      setFormData(prev => ({
        ...prev,
        tenantId: selectedTenant.id,
        tenant: {
          name: selectedTenant.name,
          email: selectedTenant.email || '',
          phone: selectedTenant.phone || '',
          emergencyContact: {
            name: selectedTenant.emergencyContact?.name || '',
            phone: selectedTenant.emergencyContact?.phone || '',
            relationship: selectedTenant.emergencyContact?.relationship || ''
          },
          moveInDate: prev.tenant.moveInDate,
          moveOutDate: prev.tenant.moveOutDate,
        }
      }))
    }
  }

  // Créer un nouveau locataire
  const handleCreateNewTenant = async () => {
    if (!newTenantData.name.trim()) {
      alert('Le nom du locataire est requis')
      return
    }

    try {
      const response = await tenantsService.createTenant({
        ...newTenantData,
        status: 'active',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      })

      const newTenant = response.data
      setTenants(prev => [...prev, newTenant])
      
      // Sélectionner automatiquement le nouveau locataire
      handleTenantSelect(newTenant.id.toString())
      
      // Réinitialiser le formulaire et fermer
      setNewTenantData({ name: '', email: '', phone: '' })
      setShowNewTenantForm(false)
    } catch (error) {
      console.error('Erreur lors de la création du locataire:', error)
      alert('Erreur lors de la création du locataire')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const updatedUnit = {
        ...unit,
        ...formData,
        updatedAt: new Date().toISOString()
      }
      
      await onSave(updatedUnit)
      onClose()
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
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
              {unit?.id ? 'Modifier l\'unité' : 'Nouvelle unité'}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {unit?.address} - {unit?.buildingName}
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
          {/* Informations de base */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Numéro d'unité
              </label>
              <input
                type="text"
                value={formData.unitNumber}
                onChange={(e) => handleInputChange('unitNumber', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type d'unité
              </label>
              <select
                value={formData.type}
                onChange={(e) => handleInputChange('type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                {Object.values(UnitType).map(type => (
                  <option key={type} value={type}>
                    {getUnitTypeLabel(type)}
                  </option>
                ))}
              </select>
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
                {Object.values(UnitStatus).map(status => (
                  <option key={status} value={status}>
                    {getUnitStatusLabel(status)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Superficie (pi²)
              </label>
              <input
                type="number"
                value={formData.area}
                onChange={(e) => handleInputChange('area', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Chambres
              </label>
              <input
                type="number"
                min="0"
                max="10"
                value={formData.bedrooms}
                onChange={(e) => handleInputChange('bedrooms', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Salles de bain
              </label>
              <input
                type="number"
                min="0"
                max="10"
                step="0.5"
                value={formData.bathrooms}
                onChange={(e) => handleInputChange('bathrooms', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          {/* Informations locatives */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <DollarSign className="h-5 w-5 mr-2" />
              Informations locatives
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Loyer mensuel
                </label>
                <input
                  type="number"
                  value={formData.rental.monthlyRent}
                  onChange={(e) => handleNestedChange('rental', 'monthlyRent', parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formatCurrency(formData.rental.monthlyRent)}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dépôt de garantie
                </label>
                <input
                  type="number"
                  value={formData.rental.deposit}
                  onChange={(e) => handleNestedChange('rental', 'deposit', parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Jour d'échéance du loyer
                </label>
                <select
                  value={formData.rental.rentDueDay}
                  onChange={(e) => handleNestedChange('rental', 'rentDueDay', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  {Array.from({length: 31}, (_, i) => i + 1).map(day => (
                    <option key={day} value={day}>{day}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Début du bail
                </label>
                <input
                  type="date"
                  value={formData.rental.leaseStart}
                  onChange={(e) => handleNestedChange('rental', 'leaseStart', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fin du bail
                </label>
                <input
                  type="date"
                  value={formData.rental.leaseEnd}
                  onChange={(e) => handleNestedChange('rental', 'leaseEnd', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
          </div>

          {/* Services inclus */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Home className="h-5 w-5 mr-2" />
              Services et commodités inclus
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {Object.entries(formData.amenities).map(([key, value]) => (
                <label key={key} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={value}
                    onChange={(e) => handleNestedChange('amenities', key, e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">
                    {getAmenityLabel(key)}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Sélection du locataire */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Locataire
            </h3>
            
            <div className="space-y-4">
              {/* Sélecteur de locataire */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sélectionner un locataire
                </label>
                <div className="flex space-x-2">
                  <select
                    value={formData.tenantId || ''}
                    onChange={(e) => handleTenantSelect(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">Aucun locataire (unité libre)</option>
                    {tenants.map(tenant => (
                      <option key={tenant.id} value={tenant.id}>
                        {tenant.name} - {tenant.email || tenant.phone || 'Pas de contact'}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => setShowNewTenantForm(!showNewTenantForm)}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors flex items-center"
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Nouveau
                  </button>
                </div>
              </div>

              {/* Formulaire de création de nouveau locataire */}
              {showNewTenantForm && (
                <div className="bg-gray-50 rounded-lg p-4 space-y-4">
                  <h4 className="font-medium text-gray-900">Créer un nouveau locataire</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nom complet *
                      </label>
                      <input
                        type="text"
                        value={newTenantData.name}
                        onChange={(e) => setNewTenantData(prev => ({ ...prev, name: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        placeholder="Nom du locataire"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Email
                      </label>
                      <input
                        type="email"
                        value={newTenantData.email}
                        onChange={(e) => setNewTenantData(prev => ({ ...prev, email: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        placeholder="email@exemple.com"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Téléphone
                      </label>
                      <input
                        type="tel"
                        value={newTenantData.phone}
                        onChange={(e) => setNewTenantData(prev => ({ ...prev, phone: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        placeholder="(514) 555-0123"
                      />
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      type="button"
                      onClick={handleCreateNewTenant}
                      className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                    >
                      Créer le locataire
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowNewTenantForm(false)}
                      className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-700 rounded-lg transition-colors"
                    >
                      Annuler
                    </button>
                  </div>
                </div>
              )}

              {/* Informations spécifiques à l'unité */}
              {formData.tenantId && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date d'emménagement
                    </label>
                    <input
                      type="date"
                      value={formData.tenant.moveInDate}
                      onChange={(e) => handleNestedChange('tenant', 'moveInDate', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date de déménagement (si applicable)
                    </label>
                    <input
                      type="date"
                      value={formData.tenant.moveOutDate}
                      onChange={(e) => handleNestedChange('tenant', 'moveOutDate', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Notes */}
          <div className="border-t pt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes et commentaires
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Notes additionnelles, historique des réparations, préférences du locataire, etc."
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

function getAmenityLabel(amenity) {
  switch (amenity) {
    case 'heating': return 'Chauffage inclus'
    case 'electricity': return 'Électricité incluse'
    case 'wifi': return 'WiFi inclus'
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