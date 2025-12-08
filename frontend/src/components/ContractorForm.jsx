import React, { useState, useEffect } from 'react'
import { X, Save, Truck, MapPin, Phone, Mail } from 'lucide-react'
import { contractorsService } from '../services/api'

export default function ContractorForm({ isOpen, onClose, contractor, onSuccess }) {
  const [formData, setFormData] = useState({
    nom: '',
    rue: '',
    ville: '',
    province: '',
    code_postal: '',
    numero: '',
    adresse_courriel: ''
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (contractor) {
      setFormData({
        nom: contractor.nom || '',
        rue: contractor.rue || '',
        ville: contractor.ville || '',
        province: contractor.province || '',
        code_postal: contractor.code_postal || '',
        numero: contractor.numero || '',
        adresse_courriel: contractor.adresse_courriel || ''
      })
    } else {
      setFormData({
        nom: '',
        rue: '',
        ville: '',
        province: '',
        code_postal: '',
        numero: '',
        adresse_courriel: ''
      })
    }
  }, [contractor])

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const submitData = {
        nom: formData.nom,
        rue: formData.rue || null,
        ville: formData.ville || null,
        province: formData.province || null,
        code_postal: formData.code_postal || null,
        numero: formData.numero || null,
        adresse_courriel: formData.adresse_courriel || null
      }

      if (contractor) {
        await contractorsService.updateContractor(contractor.id_st, submitData)
        onSuccess()
      } else {
        await contractorsService.createContractor(submitData)
        onSuccess()
      }
      onClose()
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
      setError(error.response?.data?.detail || 'Erreur lors de la sauvegarde')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {contractor ? 'Modifier le sous-traitant' : 'Nouveau sous-traitant'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Formulaire */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Nom */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom du sous-traitant *
            </label>
            <input
              type="text"
              value={formData.nom}
              onChange={(e) => handleChange('nom', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Adresse */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <MapPin className="h-5 w-5 mr-2" />
              Adresse
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rue
              </label>
              <input
                type="text"
                value={formData.rue}
                onChange={(e) => handleChange('rue', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ville
                </label>
                <input
                  type="text"
                  value={formData.ville}
                  onChange={(e) => handleChange('ville', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Province
                </label>
                <input
                  type="text"
                  value={formData.province}
                  onChange={(e) => handleChange('province', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Code postal
                </label>
                <input
                  type="text"
                  value={formData.code_postal}
                  onChange={(e) => handleChange('code_postal', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Contact */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Phone className="h-5 w-5 mr-2" />
              Contact
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Phone className="h-4 w-4 inline mr-1" />
                  Numéro de téléphone
                </label>
                <input
                  type="tel"
                  value={formData.numero}
                  onChange={(e) => handleChange('numero', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Mail className="h-4 w-4 inline mr-1" />
                  Adresse courriel
                </label>
                <input
                  type="email"
                  value={formData.adresse_courriel}
                  onChange={(e) => handleChange('adresse_courriel', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Erreur */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Boutons */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
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
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Sauvegarde...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {contractor ? 'Mettre à jour' : 'Créer le sous-traitant'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

