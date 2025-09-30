import React, { useState, useEffect } from 'react'
import { X, Save, MapPin, DollarSign, Home, Users, FileText } from 'lucide-react'
import { defaultBuilding } from '../types/building'

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
    
    if (!formData.nom_immeuble?.trim()) newErrors.nom_immeuble = 'Le nom est requis'
    if (!formData.adresse?.trim()) newErrors.adresse = 'L\'adresse est requise'
    if (!formData.ville?.trim()) newErrors.ville = 'La ville est requise'
    if (!formData.province?.trim()) newErrors.province = 'La province est requise'
    if (!formData.code_postal?.trim()) {
      newErrors.code_postal = 'Le code postal est requis'
    } else if (!/^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$/.test(formData.code_postal)) {
      newErrors.code_postal = 'Format de code postal invalide (ex: H1H 1H1)'
    }
    // Convertir en nombres pour la validation
    const units = parseInt(formData.nbr_unite) || 0
    
    if (units <= 0) newErrors.nbr_unite = 'Le nombre d\'unités doit être supérieur à 0'

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
      
      // Debug: Afficher les données avant envoi
      console.log('🔍 DEBUG - Données du formulaire:', formData)
      console.log('🔍 DEBUG - Données à envoyer:', buildingData)
      
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
                      value={formData.nom_immeuble || formData.name}
                      onChange={(e) => handleInputChange('nom_immeuble', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        errors.nom_immeuble ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="Ex: Immeuble Maple"
                    />
                    {errors.nom_immeuble && <p className="text-red-500 text-sm mt-1">{errors.nom_immeuble}</p>}
                  </div>


                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Année de construction
                    </label>
                    <input
                      type="number"
                      value={formData.annee_construction || formData.yearBuilt}
                      onChange={(e) => handleInputChange('annee_construction', parseInt(e.target.value))}
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
                      value={formData.nbr_unite || formData.units}
                      onChange={(e) => handleInputChange('nbr_unite', parseInt(e.target.value))}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        errors.nbr_unite ? 'border-red-500' : 'border-gray-300'
                      }`}
                      min="1"
                    />
                    {errors.nbr_unite && <p className="text-red-500 text-sm mt-1">{errors.nbr_unite}</p>}
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
                    value={formData.adresse || formData.address?.street}
                    onChange={(e) => handleInputChange('adresse', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                      errors.adresse ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="56 rue Vachon"
                  />
                  {errors.adresse && <p className="text-red-500 text-sm mt-1">{errors.adresse}</p>}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Ville *
                    </label>
                    <input
                      type="text"
                      value={formData.ville || formData.address?.city}
                      onChange={(e) => handleInputChange('ville', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        errors.ville ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="Montréal"
                    />
                    {errors.ville && <p className="text-red-500 text-sm mt-1">{errors.ville}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Province *
                    </label>
                    <select
                      value={formData.province || formData.address?.province}
                      onChange={(e) => handleInputChange('province', e.target.value)}
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
                      value={formData.code_postal || formData.address?.postalCode}
                      onChange={(e) => handleInputChange('code_postal', e.target.value.toUpperCase())}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        errors.code_postal ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="H1A 1A1"
                      maxLength="7"
                    />
                    {errors.code_postal && <p className="text-red-500 text-sm mt-1">{errors.code_postal}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Pays
                    </label>
                    <input
                      type="text"
                      value={formData.pays || formData.address?.country || 'Canada'}
                      onChange={(e) => handleInputChange('pays', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
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
                      value={formData.prix_achete || formData.financials?.purchasePrice}
                      onChange={(e) => handleInputChange('prix_achete', parseFloat(e.target.value) || 0)}
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
                      value={formData.mise_de_fond || formData.financials?.downPayment}
                      onChange={(e) => handleInputChange('mise_de_fond', parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      min="0"
                      step="0.01"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Taux d'intérêt (%)
                    </label>
                    <input
                      type="number"
                      value={formData.taux_interet || formData.financials?.interestRate}
                      onChange={(e) => handleInputChange('taux_interet', parseFloat(e.target.value) || 0)}
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
                      value={formData.valeur_actuel || formData.financials?.currentValue}
                      onChange={(e) => handleInputChange('valeur_actuel', parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      min="0"
                      step="0.01"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Dette restante ($)
                    </label>
                    <input
                      type="number"
                      value={formData.dette_restante || ''}
                      onChange={(e) => handleInputChange('dette_restante', e.target.value ? parseFloat(e.target.value) : null)}
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
                    value={formData.proprietaire || formData.contacts?.owner}
                    onChange={(e) => handleInputChange('proprietaire', e.target.value)}
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
                    value={formData.banque || formData.contacts?.bank}
                    onChange={(e) => handleInputChange('banque', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Nom de la banque et détails du prêt"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contracteur
                  </label>
                  <input
                    type="text"
                    value={formData.contracteur || formData.contacts?.contractor}
                    onChange={(e) => handleInputChange('contracteur', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Nom et coordonnées du contracteur"
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