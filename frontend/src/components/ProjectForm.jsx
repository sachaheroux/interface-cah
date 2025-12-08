import React, { useState, useEffect } from 'react'
import { X, Save, Calendar, MapPin, DollarSign, User, FileText, AlertTriangle, CheckCircle } from 'lucide-react'
import { projectsService } from '../services/api'

export default function ProjectForm({ isOpen, onClose, project, onSuccess }) {
  const [formData, setFormData] = useState({
    nom: '',
    description: '',
    adresse: '',
    ville: '',
    province: '',
    code_postal: '',
    date_debut: '',
    date_fin_prevue: '',
    date_fin_reelle: '',
    budget_total: '',
    cout_actuel: '',
    marge_beneficiaire: '',
    statut: 'planification',
    progression_pourcentage: '',
    client_nom: '',
    client_telephone: '',
    client_email: '',
    chef_projet: '',
    architecte: '',
    entrepreneur_principal: '',
    plans_pdf: '',
    permis_construction: '',
    numero_permis: '',
    notes: '',
    risques_identifies: '',
    ameliorations_futures: '',
    cree_par: '',
    modifie_par: ''
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const statutOptions = [
    { value: 'planification', label: 'Planification' },
    { value: 'en_cours', label: 'En cours' },
    { value: 'termine', label: 'Terminé' },
    { value: 'suspendu', label: 'Suspendu' },
    { value: 'annule', label: 'Annulé' }
  ]

  useEffect(() => {
    if (project) {
      setFormData({
        nom: project.nom || '',
        description: project.description || '',
        adresse: project.adresse || '',
        ville: project.ville || '',
        province: project.province || '',
        code_postal: project.code_postal || '',
        date_debut: project.date_debut ? project.date_debut.split('T')[0] : '',
        date_fin_prevue: project.date_fin_prevue ? project.date_fin_prevue.split('T')[0] : '',
        date_fin_reelle: project.date_fin_reelle ? project.date_fin_reelle.split('T')[0] : '',
        budget_total: project.budget_total || '',
        cout_actuel: project.cout_actuel || '',
        marge_beneficiaire: project.marge_beneficiaire || '',
        statut: project.statut || 'planification',
        progression_pourcentage: project.progression_pourcentage || '',
        client_nom: project.client_nom || '',
        client_telephone: project.client_telephone || '',
        client_email: project.client_email || '',
        chef_projet: project.chef_projet || '',
        architecte: project.architecte || '',
        entrepreneur_principal: project.entrepreneur_principal || '',
        plans_pdf: project.plans_pdf || '',
        permis_construction: project.permis_construction || '',
        numero_permis: project.numero_permis || '',
        notes: project.notes || '',
        risques_identifies: project.risques_identifies || '',
        ameliorations_futures: project.ameliorations_futures || '',
        cree_par: project.cree_par || '',
        modifie_par: project.modifie_par || ''
      })
    } else {
      // Réinitialiser le formulaire pour un nouveau projet
      setFormData({
        nom: '',
        description: '',
        adresse: '',
        ville: '',
        province: '',
        code_postal: '',
        date_debut: '',
        date_fin_prevue: '',
        date_fin_reelle: '',
        budget_total: '',
        cout_actuel: '',
        marge_beneficiaire: '',
        statut: 'planification',
        progression_pourcentage: '',
        client_nom: '',
        client_telephone: '',
        client_email: '',
        chef_projet: '',
        architecte: '',
        entrepreneur_principal: '',
        plans_pdf: '',
        permis_construction: '',
        numero_permis: '',
        notes: '',
        risques_identifies: '',
        ameliorations_futures: '',
        cree_par: '',
        modifie_par: ''
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
        ...formData,
        budget_total: formData.budget_total ? parseFloat(formData.budget_total) : 0,
        cout_actuel: formData.cout_actuel ? parseFloat(formData.cout_actuel) : 0,
        marge_beneficiaire: formData.marge_beneficiaire ? parseFloat(formData.marge_beneficiaire) : 0,
        progression_pourcentage: formData.progression_pourcentage ? parseFloat(formData.progression_pourcentage) : 0,
        cree_par: project ? formData.modifie_par : formData.cree_par || 'Admin'
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
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Statut
                </label>
                <select
                  value={formData.statut}
                  onChange={(e) => handleChange('statut', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {statutOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Description détaillée du projet..."
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

          {/* Informations financières */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <DollarSign className="h-5 w-5 mr-2" />
              Informations financières
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Coût actuel ($)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.cout_actuel}
                  onChange={(e) => handleChange('cout_actuel', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Marge bénéficiaire ($)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.marge_beneficiaire}
                  onChange={(e) => handleChange('marge_beneficiaire', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Progression (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                step="0.1"
                value={formData.progression_pourcentage}
                onChange={(e) => handleChange('progression_pourcentage', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Informations client */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Informations client
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom du client
                </label>
                <input
                  type="text"
                  value={formData.client_nom}
                  onChange={(e) => handleChange('client_nom', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Téléphone
                </label>
                <input
                  type="tel"
                  value={formData.client_telephone}
                  onChange={(e) => handleChange('client_telephone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.client_email}
                  onChange={(e) => handleChange('client_email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Équipe de projet */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Équipe de projet
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Chef de projet
                </label>
                <input
                  type="text"
                  value={formData.chef_projet}
                  onChange={(e) => handleChange('chef_projet', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Architecte
                </label>
                <input
                  type="text"
                  value={formData.architecte}
                  onChange={(e) => handleChange('architecte', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Entrepreneur principal
                </label>
                <input
                  type="text"
                  value={formData.entrepreneur_principal}
                  onChange={(e) => handleChange('entrepreneur_principal', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Documents et permis */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Documents et permis
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Plans PDF
                </label>
                <input
                  type="text"
                  value={formData.plans_pdf}
                  onChange={(e) => handleChange('plans_pdf', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Chemin vers le fichier PDF"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Permis de construction
                </label>
                <input
                  type="text"
                  value={formData.permis_construction}
                  onChange={(e) => handleChange('permis_construction', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Numéro de permis
                </label>
                <input
                  type="text"
                  value={formData.numero_permis}
                  onChange={(e) => handleChange('numero_permis', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Notes et observations */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Notes et observations
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes générales
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => handleChange('notes', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Notes importantes sur le projet..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Risques identifiés
                </label>
                <textarea
                  value={formData.risques_identifies}
                  onChange={(e) => handleChange('risques_identifies', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Risques potentiels identifiés..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Améliorations futures
                </label>
                <textarea
                  value={formData.ameliorations_futures}
                  onChange={(e) => handleChange('ameliorations_futures', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Améliorations suggérées pour de futurs projets..."
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


