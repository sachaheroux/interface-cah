import React, { useState, useEffect } from 'react'
import { Clock, Calendar, MapPin, Save, X, User, Building, Edit, Trash2 } from 'lucide-react'
import { employeesService, punchsService, projectsService } from '../services/api'
import api from '../services/api'

export default function PunchFormDesktop({ isOpen, onClose, employee = null, punch = null, onSuccess }) {
  const [formData, setFormData] = useState({
    id_employe: '',
    id_projet: '',
    date: '',
    heure_travaillee: '',
    section: ''
  })
  const [employees, setEmployees] = useState([])
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Fonction pour formater la date pour l'input
  const formatDateForInput = (dateString) => {
    if (!dateString) return ''
    // Gérer différents formats de date
    let date = dateString
    if (dateString.includes('T')) {
      date = dateString.split('T')[0]
    } else if (dateString.includes(' ')) {
      date = dateString.split(' ')[0]
    }
    return date
  }

  // Initialiser le formulaire
  useEffect(() => {
    if (isOpen) {
      if (punch) {
        // Mode édition : charger les données du punch
        setFormData({
          id_employe: punch.id_employe || '',
          id_projet: punch.id_projet || '',
          date: formatDateForInput(punch.date),
          heure_travaillee: punch.heure_travaillee || '',
          section: punch.section || ''
        })
      } else {
        // Mode création : valeurs par défaut
        const today = new Date().toISOString().split('T')[0]
        setFormData({
          id_employe: employee ? employee.id_employe : '',
          id_projet: '',
          date: today,
          heure_travaillee: '',
          section: ''
        })
      }
      setError('')
      fetchEmployees()
      fetchProjects()
    }
  }, [isOpen, employee, punch])

  const fetchEmployees = async () => {
    try {
      const response = await employeesService.getEmployees()
      setEmployees(response.data || [])
    } catch (err) {
      console.error('Erreur lors du chargement des employés:', err)
    }
  }

  const fetchProjects = async () => {
    try {
      const response = await projectsService.getProjects()
      setProjects(response.data || [])
    } catch (err) {
      console.error('Erreur lors du chargement des projets:', err)
    }
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setError('')
  }

  const validateForm = () => {
    if (!formData.id_employe) {
      setError('Veuillez sélectionner un employé')
      return false
    }
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
    if (!formData.section) {
      setError('Veuillez spécifier la section travaillée')
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
        id_employe: parseInt(formData.id_employe),
        id_projet: parseInt(formData.id_projet),
        date: formData.date,
        heure_travaillee: parseFloat(formData.heure_travaillee),
        section: formData.section
      }

      if (punch) {
        // Mode édition
        await punchsService.updatePunch(punch.id_punch, punchData)
        onSuccess?.()
      } else {
        // Mode création
        await punchsService.createPunch(punchData)
        onSuccess?.()
      }
      onClose()
    } catch (err) {
      console.error('Erreur lors de la sauvegarde:', err)
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde')
    } finally {
      setLoading(false)
    }
  }

  const getSelectedEmployee = () => {
    return employees.find(emp => emp.id_employe === parseInt(formData.id_employe))
  }

  const getSelectedProject = () => {
    return projects.find(proj => proj.id_projet === parseInt(formData.id_projet))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg mr-3">
              <Clock className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {punch ? 'Modifier le Pointage' : employee ? `Pointage - ${employee.prenom} ${employee.nom}` : 'Nouveau Pointage'}
              </h2>
              <p className="text-sm text-gray-600">
                {punch ? 'Modifier les heures travaillées' : 'Enregistrer les heures travaillées'}
              </p>
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
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Employé et Projet */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Employé */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <User className="h-4 w-4 inline mr-1" />
                Employé *
              </label>
              <select
                value={formData.id_employe}
                onChange={(e) => handleChange('id_employe', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
                disabled={!!employee}
              >
                <option value="">Sélectionner un employé</option>
                {employees.map((emp) => (
                  <option key={emp.id_employe} value={emp.id_employe}>
                    {emp.prenom} {emp.nom} - {emp.poste} (${emp.taux_horaire}/h)
                  </option>
                ))}
              </select>
            </div>

            {/* Projet */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Building className="h-4 w-4 inline mr-1" />
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
          </div>

          {/* Date et Heures */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="h-4 w-4 inline mr-1" />
                Date *
              </label>
              <input
                type="date"
                value={formData.date}
                onChange={(e) => handleChange('date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>

            {/* Heures travaillées */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Clock className="h-4 w-4 inline mr-1" />
                Heures travaillées *
              </label>
              <input
                type="number"
                step="0.25"
                min="0"
                max="24"
                value={formData.heure_travaillee}
                onChange={(e) => handleChange('heure_travaillee', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="8.0"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Utilisez 0.25 pour 15 min, 0.5 pour 30 min, etc.
              </p>
            </div>
          </div>

          {/* Section */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <MapPin className="h-4 w-4 inline mr-1" />
              Section travaillée *
            </label>
            <select
              value={formData.section}
              onChange={(e) => handleChange('section', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              required
            >
              <option value="">Sélectionner une section</option>
              <option value="Admin">Admin</option>
              <option value="Excavation et fondation">Excavation et fondation</option>
              <option value="Structure du batiment">Structure du bâtiment</option>
              <option value="Toiture">Toiture</option>
              <option value="Préparation intérieur">Préparation intérieur</option>
              <option value="Fenêtres">Fenêtres</option>
              <option value="Gypse">Gypse</option>
              <option value="Joint">Joint</option>
              <option value="Portes">Portes</option>
              <option value="Peinture">Peinture</option>
              <option value="Plancher">Plancher</option>
              <option value="Armoire">Armoire</option>
              <option value="Revêtement souple">Revêtement souple</option>
              <option value="Patio arrière">Patio arrière</option>
              <option value="Autres">Autres</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              ⚠️ Un pointage par section - si l'employé travaille sur plusieurs sections, créer un pointage séparé pour chaque section.
            </p>
          </div>

          {/* Résumé du calcul */}
          {formData.id_employe && formData.heure_travaillee && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Résumé du calcul</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Employé:</span>
                  <div className="font-medium">{getSelectedEmployee()?.prenom} {getSelectedEmployee()?.nom}</div>
                </div>
                <div>
                  <span className="text-gray-600">Taux horaire:</span>
                  <div className="font-medium">${getSelectedEmployee()?.taux_horaire}/h</div>
                </div>
                <div>
                  <span className="text-gray-600">Heures:</span>
                  <div className="font-medium">{formData.heure_travaillee}h</div>
                </div>
                <div>
                  <span className="text-gray-600">Total:</span>
                  <div className="font-medium text-green-600">
                    ${(parseFloat(formData.heure_travaillee || 0) * (getSelectedEmployee()?.taux_horaire || 0)).toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          )}

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
                  {punch ? 'Mettre à jour' : 'Enregistrer le pointage'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
