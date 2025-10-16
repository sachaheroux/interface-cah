import React, { useState, useEffect } from 'react'
import { Clock, Calendar, MapPin, Save, X, User, Building } from 'lucide-react'
import { employeesService, punchsService } from '../services/api'
import api from '../services/api'

export default function PunchFormMobile({ isOpen, onClose, onSuccess }) {
  const [step, setStep] = useState(1) // 1: Employé, 2: Projet, 3: Détails
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

  // Initialiser le formulaire
  useEffect(() => {
    if (isOpen) {
      // Date par défaut = aujourd'hui
      const today = new Date().toISOString().split('T')[0]
      setFormData({
        id_employe: '',
        id_projet: '',
        date: today,
        heure_travaillee: '',
        section: ''
      })
      setStep(1)
      setError('')
      fetchEmployees()
      fetchProjects()
    }
  }, [isOpen])

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

  const handleNext = () => {
    if (step === 1 && !formData.id_employe) {
      setError('Veuillez sélectionner un employé')
      return
    }
    if (step === 2 && !formData.id_projet) {
      setError('Veuillez sélectionner un projet')
      return
    }
    setStep(step + 1)
    setError('')
  }

  const handleBack = () => {
    setStep(step - 1)
    setError('')
  }

  const validateForm = () => {
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
        id_employe: parseInt(formData.id_employe),
        id_projet: parseInt(formData.id_projet),
        date: formData.date,
        heure_travaillee: parseFloat(formData.heure_travaillee),
        section: formData.section || null
      }

      await punchsService.createPunch(punchData)
      onSuccess?.('Pointage enregistré avec succès')
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
      <div className="bg-white rounded-lg shadow-xl w-full max-w-sm mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg mr-3">
              <Clock className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Pointage - Étape {step}/3
              </h2>
              <p className="text-xs text-gray-600">
                {step === 1 && 'Sélectionner l\'employé'}
                {step === 2 && 'Choisir le projet'}
                {step === 3 && 'Détails du pointage'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-4 py-2 bg-gray-50">
          <div className="flex space-x-2">
            {[1, 2, 3].map((stepNum) => (
              <div
                key={stepNum}
                className={`flex-1 h-2 rounded-full ${
                  stepNum <= step ? 'bg-green-600' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Étape 1: Sélection Employé */}
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <User className="h-4 w-4 inline mr-1" />
                  Sélectionner l'employé *
                </label>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {employees.map((employee) => (
                    <button
                      key={employee.id_employe}
                      type="button"
                      onClick={() => handleChange('id_employe', employee.id_employe)}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        formData.id_employe === employee.id_employe
                          ? 'border-green-500 bg-green-50 text-green-700'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium">
                        {employee.prenom} {employee.nom}
                      </div>
                      <div className="text-sm text-gray-600">
                        {employee.poste} • ${employee.taux_horaire}/h
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Étape 2: Sélection Projet */}
          {step === 2 && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Building className="h-4 w-4 inline mr-1" />
                  Choisir le projet *
                </label>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {projects.map((project) => (
                    <button
                      key={project.id_projet}
                      type="button"
                      onClick={() => handleChange('id_projet', project.id_projet)}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        formData.id_projet === project.id_projet
                          ? 'border-green-500 bg-green-50 text-green-700'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium">{project.nom}</div>
                      <div className="text-sm text-gray-600">
                        {project.adresse && `${project.adresse} • `}
                        {project.date_debut && `Début: ${new Date(project.date_debut).toLocaleDateString('fr-CA')}`}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Étape 3: Détails du pointage */}
          {step === 3 && (
            <div className="space-y-4">
              {/* Résumé */}
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Résumé du pointage</div>
                <div className="font-medium text-gray-900">
                  {getSelectedEmployee()?.prenom} {getSelectedEmployee()?.nom}
                </div>
                <div className="text-sm text-gray-600">
                  {getSelectedProject()?.nom}
                </div>
              </div>

              {/* Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
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
                <label className="block text-sm font-medium text-gray-700 mb-1">
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
                <p className="text-xs text-gray-500 mt-1">
                  ⚠️ Un pointage par section - si vous travaillez sur plusieurs sections, faites un pointage séparé pour chaque section.
                </p>
              </div>

              {/* Section */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <MapPin className="h-4 w-4 inline mr-1" />
                  Section travaillée *
                </label>
                <input
                  type="text"
                  value={formData.section}
                  onChange={(e) => handleChange('section', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Ex: Fondation, Toiture, Charpente, etc."
                  required
                />
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex space-x-3 pt-4">
            {step > 1 && (
              <button
                type="button"
                onClick={handleBack}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Retour
              </button>
            )}
            
            {step < 3 ? (
              <button
                type="button"
                onClick={handleNext}
                className="flex-1 px-4 py-2 bg-green-600 text-white hover:bg-green-700 rounded-lg transition-colors"
              >
                Suivant
              </button>
            ) : (
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
            )}
          </div>
        </form>
      </div>
    </div>
  )
}
