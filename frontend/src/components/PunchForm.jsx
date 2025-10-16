import React, { useState, useEffect } from 'react'
import { Clock, Calendar, MapPin, Save, X } from 'lucide-react'
import api from '../services/api'

export default function PunchForm({ isOpen, onClose, employee, onSuccess }) {
  const [formData, setFormData] = useState({
    id_projet: '',
    date: '',
    heure_travaillee: '',
    section: ''
  })
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Initialiser le formulaire
  useEffect(() => {
    if (isOpen) {
      // Date par défaut = aujourd'hui
      const today = new Date().toISOString().split('T')[0]
      setFormData({
        id_projet: '',
        date: today,
        heure_travaillee: '',
        section: ''
      })
      setError('')
      fetchProjects()
    }
  }, [isOpen])

  const fetchProjects = async () => {
    try {
      const response = await api.get('/api/construction/projets')
      if (response.data.success) {
        setProjects(response.data.data || [])
      }
    } catch (err) {
      console.error('Erreur lors du chargement des projets:', err)
    }
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setError('')
  }

  const validateForm = () => {
    if (!formData.id_projet) {
      setError('Veuillez sélectionner un projet')
      return false
    }
    if (!formData.date) {
      setError('Veuillez sélectionner une date')
      return false
    }
    if (!formData.heure_travaillee || parseFloat(formData.heure_travaillee) <= 0) {
      setError('Veuillez entrer un nombre d\'heures valide')
      return false
    }
    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setLoading(true)
    setError('')

    try {
      const punchData = {
        id_employe: employee.id_employe,
        id_projet: parseInt(formData.id_projet),
        date: formData.date,
        heure_travaillee: parseFloat(formData.heure_travaillee),
        section: formData.section || null
      }

      await api.post('/api/construction/punchs-employes', punchData)
      onSuccess?.('Pointage enregistré avec succès')
      onClose()
    } catch (err) {
      console.error('Erreur lors de la sauvegarde:', err)
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg mr-3">
              <Clock className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Pointage - {employee?.prenom} {employee?.nom}
              </h2>
              <p className="text-sm text-gray-600">Enregistrer vos heures travaillées</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Projet */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Projet *
            </label>
            <select
              value={formData.id_projet}
              onChange={(e) => handleChange('id_projet', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              required
            >
              <option value="">Sélectionner un projet</option>
              {projects.map((project) => (
                <option key={project.id_projet} value={project.id_projet}>
                  {project.nom}
                </option>
              ))}
            </select>
          </div>

          {/* Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date *
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="date"
                value={formData.date}
                onChange={(e) => handleChange('date', e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          {/* Heures travaillées */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Heures travaillées *
            </label>
            <div className="relative">
              <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="number"
                step="0.25"
                min="0"
                max="24"
                value={formData.heure_travaillee}
                onChange={(e) => handleChange('heure_travaillee', e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="8.0"
                required
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Utilisez 0.25 pour 15 min, 0.5 pour 30 min, etc.
            </p>
          </div>

          {/* Section */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Section (optionnel)
            </label>
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={formData.section}
                onChange={(e) => handleChange('section', e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Ex: Fondation, Toiture, etc."
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center justify-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Enregistrer
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
