import React, { useState, useEffect } from 'react'
import { X, Save, MapPin, DollarSign, Home, Users, FileText } from 'lucide-react'
import { defaultBuilding, BuildingTypes, getBuildingTypeLabel } from '../types/building'

export default function BuildingForm({ building = null, isOpen, onClose, onSave }) {
  const [formData, setFormData] = useState(defaultBuilding)
  const [activeTab, setActiveTab] = useState('general')
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (building) {
      setFormData({ ...defaultBuilding, ...building })
    } else {
      setFormData({ ...defaultBuilding, createdAt: new Date().toISOString() })
    }
  }, [building])

  const tabs = [
    { id: 'general', name: 'Général', icon: Home },
    { id: 'address', name: 'Adresse', icon: MapPin },
    { id: 'characteristics', name: 'Caractéristiques', icon: Users },
    { id: 'financials', name: 'Financier', icon: DollarSign },
    { id: 'contacts', name: 'Contacts', icon: Users },
    { id: 'notes', name: 'Notes', icon: FileText }
  ]

  const handleInputChange = (field, value, nested = null) => {
    if (nested) {
      setFormData(prev => ({
        ...prev,
        [nested]: {
          ...prev[nested],
          [field]: value
        }
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }))
    }
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }))
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.name.trim()) newErrors.name = 'Le nom est requis'
    if (!formData.address.street.trim()) newErrors.street = 'L\'adresse est requise'
    if (!formData.address.city.trim()) newErrors.city = 'La ville est requise'
    if (!formData.address.province.trim()) newErrors.province = 'La province est requise'
    if (!formData.address.postalCode.trim()) {
      newErrors.postalCode = 'Le code postal est requis'
    } else if (!/^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$/.test(formData.address.postalCode)) {
      newErrors.postalCode = 'Format de code postal invalide (ex: H1H 1H1)'
    }
    // Convertir en nombres pour la validation
    const units = parseInt(formData.units) || 0
    const floors = parseInt(formData.floors) || 0
    
    if (units <= 0) newErrors.units = 'Le nombre d\'unités doit être supérieur à 0'
    if (floors <= 0) newErrors.floors = 'Le nombre d\'étages doit être supérieur à 0'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setLoading(true)
    try {
      const buildingData = {
        ...formData,
        updatedAt: new Date().toISOString()
      }
      await onSave(buildingData)
      onClose()
    } catch (error) {
      console.error('Error saving building:', error)
      setErrors({ general: `Erreur lors de la sauvegarde: ${error.message}` })
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {building ? 'Modifier l\'immeuble' : 'Nouvel immeuble'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Form Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto">
          <div className="p-6 space-y-6">
            
            {/* General Tab */}
            {activeTab === 'general' && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nom de l'immeuble *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        errors.name ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="Ex: Immeuble Maple"
                    />
                    {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Type d'immeuble
                    </label>
                    <select
                      value={formData.type}
                      onChange={(e) => handleInputChange('type', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      {Object.values(BuildingTypes).map(type => (
                        <option key={type} value={type}>
                          {getBuildingTypeLabel(type)}
                        </option>
                      ))}
                    </select>
                  </div>



                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Année de construction
                    </label>
                    <input
                      type="number"
                      value={formData.yearBuilt}
                      onChange={(e) => handleInputChange('yearBuilt', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      min="1800"
                      max={new Date().getFullYear() + 5}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nombre d'unités *
                    </label>
                    <input
                      type="number"
                      value={formData.units}
                      onChange={(e) => handleInputChange('units', parseInt(e.target.value))}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        errors.units ? 'border-red-500' : 'border-gray-300'
                      }`}
                      min="1"
                    />
                    {errors.units && <p className="text-red-500 text-sm mt-1">{errors.units}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nombre d'étages *
                    </label>
                    <input
                      type="number"
                      value={formData.floors}
                      onChange={(e) => handleInputChange('floors', parseInt(e.target.value))}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        errors.floors ? 'border-red-500' : 'border-gray-300'
                      }`}
                      min="1"
                    />
                    {errors.floors && <p className="text-red-500 text-sm mt-1">{errors.floors}</p>}
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Superficie totale (pi²)
                    </label>
                    <input
                      type="number"
                      value={formData.totalArea}
                      onChange={(e) => handleInputChange('totalArea', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      min="0"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Address Tab */}
            {activeTab === 'address' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Adresse *
                  </label>
                  <input
                    type="text"
                    value={formData.address.street}
                    onChange={(e) => handleInputChange('street', e.target.value, 'address')}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                      errors.street ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="123 Rue Example"
                  />
                  {errors.street && <p className="text-red-500 text-sm mt-1">{errors.street}</p>}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Ville *
                    </label>
                    <input
                      type="text"
                      value={formData.address.city}
                      onChange={(e) => handleInputChange('city', e.target.value, 'address')}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        errors.city ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="Montréal"
                    />
                    {errors.city && <p className="text-red-500 text-sm mt-1">{errors.city}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Province *
                    </label>
                    <select
                      value={formData.address.province}
                      onChange={(e) => handleInputChange('province', e.target.value, 'address')}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        errors.province ? 'border-red-500' : 'border-gray-300'
                      }`}
                    >
                      <option value="">Sélectionnez...</option>
                      <option value="QC">Québec</option>
                      <option value="ON">Ontario</option>
                      <option value="BC">Colombie-Britannique</option>
                      <option value="AB">Alberta</option>
                      <option value="MB">Manitoba</option>
                      <option value="SK">Saskatchewan</option>
                      <option value="NS">Nouvelle-Écosse</option>
                      <option value="NB">Nouveau-Brunswick</option>
                      <option value="NL">Terre-Neuve-et-Labrador</option>
                      <option value="PE">Île-du-Prince-Édouard</option>
                      <option value="YT">Yukon</option>
                      <option value="NT">Territoires du Nord-Ouest</option>
                      <option value="NU">Nunavut</option>
                    </select>
                    {errors.province && <p className="text-red-500 text-sm mt-1">{errors.province}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Code postal *
                    </label>
                    <input
                      type="text"
                      value={formData.address.postalCode}
                      onChange={(e) => handleInputChange('postalCode', e.target.value.toUpperCase(), 'address')}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        errors.postalCode ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="H1A 1A1"
                      maxLength="7"
                    />
                    {errors.postalCode && <p className="text-red-500 text-sm mt-1">{errors.postalCode}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Pays
                    </label>
                    <input
                      type="text"
                      value={formData.address.country}
                      onChange={(e) => handleInputChange('country', e.target.value, 'address')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Characteristics Tab */}
            {activeTab === 'characteristics' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Places de stationnement
                    </label>
                    <input
                      type="number"
                      value={formData.characteristics.parking}
                      onChange={(e) => handleInputChange('parking', parseInt(e.target.value) || 0, 'characteristics')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      min="0"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Balcons
                    </label>
                    <input
                      type="number"
                      value={formData.characteristics.balconies}
                      onChange={(e) => handleInputChange('balconies', parseInt(e.target.value) || 0, 'characteristics')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      min="0"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Type de chauffage
                    </label>
                    <select
                      value={formData.characteristics.heating}
                      onChange={(e) => handleInputChange('heating', e.target.value, 'characteristics')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="electric">Électrique</option>
                      <option value="gas">Gaz</option>
                      <option value="oil">Mazout</option>
                      <option value="heat_pump">Thermopompe</option>
                    </select>
                  </div>
                </div>

                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Équipements</h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {[
                      { key: 'elevator', label: 'Ascenseur' },
                      { key: 'storage', label: 'Rangement' },
                      { key: 'laundry', label: 'Buanderie' },
                      { key: 'airConditioning', label: 'Climatisation' },
                      { key: 'internet', label: 'Internet inclus' },
                      { key: 'security', label: 'Système de sécurité' }
                    ].map(item => (
                      <label key={item.key} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={formData.characteristics[item.key]}
                          onChange={(e) => handleInputChange(item.key, e.target.checked, 'characteristics')}
                          className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                        />
                        <span className="text-sm text-gray-700">{item.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Financials Tab */}
            {activeTab === 'financials' && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Prix d'achat ($)
                    </label>
                    <input
                      type="number"
                      value={formData.financials.purchasePrice}
                      onChange={(e) => handleInputChange('purchasePrice', parseFloat(e.target.value) || 0, 'financials')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      min="0"
                      step="0.01"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Mise de fond ($)
                    </label>
                    <input
                      type="number"
                      value={formData.financials.downPayment}
                      onChange={(e) => handleInputChange('downPayment', parseFloat(e.target.value) || 0, 'financials')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      min="0"
                      step="0.01"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Taux d'intérêt actuel (%)
                    </label>
                    <input
                      type="number"
                      value={formData.financials.interestRate}
                      onChange={(e) => handleInputChange('interestRate', parseFloat(e.target.value) || 0, 'financials')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      min="0"
                      max="100"
                      step="0.01"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Valeur actuelle ($)
                    </label>
                    <input
                      type="number"
                      value={formData.financials.currentValue}
                      onChange={(e) => handleInputChange('currentValue', parseFloat(e.target.value) || 0, 'financials')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      min="0"
                      step="0.01"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Contacts Tab */}
            {activeTab === 'contacts' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Propriétaire
                  </label>
                  <input
                    type="text"
                    value={formData.contacts.owner}
                    onChange={(e) => handleInputChange('owner', e.target.value, 'contacts')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Nom et coordonnées du propriétaire"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Banque (prêt hypothécaire)
                  </label>
                  <input
                    type="text"
                    value={formData.contacts.bank}
                    onChange={(e) => handleInputChange('bank', e.target.value, 'contacts')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Nom de la banque et détails du prêt"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Entrepreneur
                  </label>
                  <input
                    type="text"
                    value={formData.contacts.contractor}
                    onChange={(e) => handleInputChange('contractor', e.target.value, 'contacts')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Nom et coordonnées de l'entrepreneur"
                  />
                </div>
              </div>
            )}

            {/* Notes Tab */}
            {activeTab === 'notes' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes et commentaires
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Ajoutez des notes, commentaires ou informations supplémentaires..."
                />
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end space-x-4 p-6 border-t border-gray-200 bg-gray-50">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2 disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              <span>{loading ? 'Enregistrement...' : 'Enregistrer'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
} 