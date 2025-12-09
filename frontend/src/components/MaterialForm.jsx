import React, { useState, useEffect } from 'react'
import { X, Save, Package } from 'lucide-react'
import { materialsService } from '../services/api'

export default function MaterialForm({ isOpen, onClose, material, onSuccess }) {
  const [formData, setFormData] = useState({
    nom: '',
    notes: ''
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (material) {
      setFormData({
        nom: material.nom || '',
        notes: material.notes || ''
      })
    } else {
      setFormData({
        nom: '',
        notes: ''
      })
    }
  }, [material])

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
        notes: formData.notes || null
      }

      if (material) {
        await materialsService.updateMaterial(material.id_matiere_premiere, submitData)
        onSuccess()
      } else {
        await materialsService.createMaterial(submitData)
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
            {material ? 'Modifier la matière première' : 'Nouvelle matière première'}
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
              Nom de la matière première *
            </label>
            <input
              type="text"
              value={formData.nom}
              onChange={(e) => handleChange('nom', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Notes sur la matière première..."
            />
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
                  {material ? 'Mettre à jour' : 'Créer la matière première'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

