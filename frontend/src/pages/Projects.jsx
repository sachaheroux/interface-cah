import React, { useState, useEffect } from 'react'
import { Hammer, Plus, Edit, Trash2, MapPin, Calendar, DollarSign, User, FileText, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import { projectsService } from '../services/api'
import ProjectForm from '../components/ProjectForm'

export default function Projects() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingProject, setEditingProject] = useState(null)
  const [successMessage, setSuccessMessage] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    setLoading(true)
    try {
      const response = await projectsService.getProjects()
      setProjects(response.data)
    } catch (error) {
      console.error("Erreur lors de la récupération des projets:", error)
      setProjects([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProject = () => {
    setEditingProject(null)
    setShowForm(true)
  }

  const handleEditProject = (project) => {
    setEditingProject(project)
    setShowForm(true)
  }

  const handleDeleteProject = async (project) => {
    try {
      await projectsService.deleteProject(project.id_projet)
      setSuccessMessage(`Le projet "${project.nom}" a été supprimé avec succès.`)
      fetchProjects()
      setDeleteConfirm(null)
    } catch (error) {
      console.error("Erreur lors de la suppression du projet:", error)
      if (error.response?.status === 400) {
        setSuccessMessage(`Impossible de supprimer le projet "${project.nom}": ${error.response.data.detail}`)
      } else {
        setSuccessMessage(`Erreur lors de la suppression du projet "${project.nom}".`)
      }
      setDeleteConfirm(null)
    }
  }

  const handleFormSuccess = (message) => {
    setSuccessMessage(message)
    setShowForm(false)
    fetchProjects()
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingProject(null)
  }

  const getStatutColor = (statut) => {
    switch (statut) {
      case 'planification':
        return 'bg-blue-100 text-blue-800'
      case 'en_cours':
        return 'bg-green-100 text-green-800'
      case 'termine':
        return 'bg-gray-100 text-gray-800'
      case 'suspendu':
        return 'bg-yellow-100 text-yellow-800'
      case 'annule':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatutLabel = (statut) => {
    switch (statut) {
      case 'planification':
        return 'Planification'
      case 'en_cours':
        return 'En cours'
      case 'termine':
        return 'Terminé'
      case 'suspendu':
        return 'Suspendu'
      case 'annule':
        return 'Annulé'
      default:
        return statut
    }
  }

  const formatCurrency = (amount) => {
    if (!amount || amount === 0) return '$0.00'
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Non défini'
    return new Date(dateString).toLocaleDateString('fr-CA')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projets de Construction</h1>
          <p className="text-gray-600 mt-1">Gestion des projets de construction</p>
        </div>
        <button
          onClick={handleCreateProject}
          className="btn-primary flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          Nouveau Projet
        </button>
      </div>

      {/* Message de succès */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
          {successMessage}
        </div>
      )}

      {/* Liste des projets */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {projects.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <Hammer className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun projet</h3>
            <p className="text-gray-500">Commencez par ajouter un nouveau projet.</p>
          </div>
        ) : (
          projects.map((project) => (
            <div key={project.id_projet} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              {/* Header du projet */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-1">{project.nom}</h3>
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatutColor(project.statut)}`}>
                    {getStatutLabel(project.statut)}
                  </span>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEditProject(project)}
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                    title="Modifier le projet"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setDeleteConfirm(project)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                    title="Supprimer le projet"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Description */}
              {project.description && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {project.description}
                </p>
              )}

              {/* Adresse */}
              {project.adresse && (
                <div className="flex items-center text-gray-600 text-sm mb-2">
                  <MapPin className="h-4 w-4 mr-2 text-gray-500" />
                  <span>{project.adresse}, {project.ville}</span>
                </div>
              )}

              {/* Dates */}
              <div className="space-y-1 mb-4">
                {project.date_debut && (
                  <div className="flex items-center text-gray-600 text-sm">
                    <Calendar className="h-4 w-4 mr-2 text-gray-500" />
                    <span>Début: {formatDate(project.date_debut)}</span>
                  </div>
                )}
                {project.date_fin_prevue && (
                  <div className="flex items-center text-gray-600 text-sm">
                    <Clock className="h-4 w-4 mr-2 text-gray-500" />
                    <span>Fin prévue: {formatDate(project.date_fin_prevue)}</span>
                  </div>
                )}
              </div>

              {/* Informations financières */}
              <div className="space-y-2 mb-4">
                {project.budget_total > 0 && (
                  <div className="flex items-center text-gray-700 text-sm">
                    <DollarSign className="h-4 w-4 mr-2 text-gray-500" />
                    <span>Budget: {formatCurrency(project.budget_total)}</span>
                  </div>
                )}
                {project.cout_actuel > 0 && (
                  <div className="flex items-center text-gray-700 text-sm">
                    <DollarSign className="h-4 w-4 mr-2 text-gray-500" />
                    <span>Coût actuel: {formatCurrency(project.cout_actuel)}</span>
                  </div>
                )}
                {project.progression_pourcentage > 0 && (
                  <div className="flex items-center text-gray-700 text-sm">
                    <CheckCircle className="h-4 w-4 mr-2 text-gray-500" />
                    <span>Progression: {project.progression_pourcentage}%</span>
                  </div>
                )}
              </div>

              {/* Client */}
              {project.client_nom && (
                <div className="flex items-center text-gray-600 text-sm mb-2">
                  <User className="h-4 w-4 mr-2 text-gray-500" />
                  <span>{project.client_nom}</span>
                </div>
              )}

              {/* Chef de projet */}
              {project.chef_projet && (
                <div className="flex items-center text-gray-600 text-sm mb-2">
                  <User className="h-4 w-4 mr-2 text-gray-500" />
                  <span>Chef: {project.chef_projet}</span>
                </div>
              )}

              {/* Notes importantes */}
              {project.risques_identifies && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-start">
                    <AlertTriangle className="h-4 w-4 text-yellow-600 mr-2 mt-0.5" />
                    <div>
                      <p className="text-yellow-800 text-xs font-medium mb-1">Risques identifiés:</p>
                      <p className="text-yellow-700 text-xs line-clamp-2">
                        {project.risques_identifies}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Formulaire modal */}
      <ProjectForm
        isOpen={showForm}
        onClose={handleCloseForm}
        project={editingProject}
        onSuccess={handleFormSuccess}
      />

      {/* Modal de confirmation de suppression */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <AlertTriangle className="h-6 w-6 text-red-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Confirmer la suppression
                </h3>
              </div>
              
              <p className="text-gray-600 mb-6">
                Êtes-vous sûr de vouloir supprimer le projet <strong>"{deleteConfirm.nom}"</strong> ?
                Cette action est irréversible.
              </p>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setDeleteConfirm(null)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={() => handleDeleteProject(deleteConfirm)}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Supprimer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}