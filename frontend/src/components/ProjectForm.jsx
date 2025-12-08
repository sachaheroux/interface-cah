import React, { useState, useEffect } from 'react'
import { X, Save, Calendar, MapPin, DollarSign, FileText } from 'lucide-react'
import { projectsService } from '../services/api'

export default function ProjectForm({ isOpen, onClose, project, onSuccess }) {
  const [formData, setFormData] = useState({
    nom: '',
    date_debut: '',
    date_fin_prevue: '',
    date_fin_reelle: '',
    notes: '',
    adresse: '',
    ville: '',
    province: '',
    code_postal: '',
    budget_total: ''
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (project) {
      setFormData({
        nom: project.nom || '',
        date_debut: project.date_debut ? project.date_debut.split('T')[0] : '',
        date_fin_prevue: project.date_fin_prevue ? project.date_fin_prevue.split('T')[0] : '',
        date_fin_reelle: project.date_fin_reelle ? project.date_fin_reelle.split('T')[0] : '',
        notes: project.notes || '',
        adresse: project.adresse || '',
        ville: project.ville || '',
        province: project.province || '',
        code_postal: project.code_postal || '',
        budget_total: project.budget_total || ''
      })
    } else {
      // Réinitialiser le formulaire pour un nouveau projet
      setFormData({
        nom: '',
        date_debut: '',
        date_fin_prevue: '',
        date_fin_reelle: '',
        notes: '',
        adresse: '',
        ville: '',
        province: '',
        code_postal: '',
        budget_total: ''
      })
    }
  }, [project])

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
      // Préparer les données pour l'API
      const submitData = {
        nom: formData.nom,
        date_debut: formData.date_debut || null,
        date_fin_prevue: formData.date_fin_prevue || null,
        date_fin_reelle: formData.date_fin_reelle || null,
        notes: formData.notes || null,
        adresse: formData.adresse || null,
        ville: formData.ville || null,
        province: formData.province || null,
        code_postal: formData.code_postal || null,
        budget_total: formData.budget_total ? parseFloat(formData.budget_total) : 0
      }

      if (project) {
        await projectsService.updateProject(project.id_projet, submitData)
        onSuccess(`Projet "${formData.nom}" mis à jour avec succès.`)
      } else {
        await projectsService.createProject(submitData)
        onSuccess(`Projet "${formData.nom}" créé avec succès.`)
      }
    } catch (error) {
      console.error('Erreur lors de la sauvegarde du projet:', error)
      setError(error.response?.data?.detail || 'Erreur lors de la sauvegarde du projet')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {project ? 'Modifier le projet' : 'Nouveau projet'}
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
          {/* Informations de base */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Informations de base
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom du projet *
              </label>
              <input
                type="text"
                value={formData.nom}
                onChange={(e) => handleChange('nom', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          {/* Adresse */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <MapPin className="h-5 w-5 mr-2" />
              Adresse du projet
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Adresse
                </label>
                <input
                  type="text"
                  value={formData.adresse}
                  onChange={(e) => handleChange('adresse', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
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

          {/* Dates */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Calendar className="h-5 w-5 mr-2" />
              Dates importantes
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date de début
                </label>
                <input
                  type="date"
                  value={formData.date_debut}
                  onChange={(e) => handleChange('date_debut', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date de fin prévue
                </label>
                <input
                  type="date"
                  value={formData.date_fin_prevue}
                  onChange={(e) => handleChange('date_fin_prevue', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date de fin réelle
                </label>
                <input
                  type="date"
                  value={formData.date_fin_reelle}
                  onChange={(e) => handleChange('date_fin_reelle', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Budget */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <DollarSign className="h-5 w-5 mr-2" />
              Budget
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Budget total ($)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.budget_total}
                onChange={(e) => handleChange('budget_total', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Notes
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notes générales
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => handleChange('notes', e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Notes importantes sur le projet..."
              />
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
                  {project ? 'Mettre à jour' : 'Créer le projet'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


