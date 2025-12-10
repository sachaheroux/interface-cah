import React, { useState, useEffect } from 'react'
import { Package, Plus, Edit, Trash2, FileText } from 'lucide-react'
import { materialsService } from '../services/api'
import MaterialForm from '../components/MaterialForm'

export default function Materials() {
  const [materials, setMaterials] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingMaterial, setEditingMaterial] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  useEffect(() => {
    fetchMaterials()
  }, [])

  const fetchMaterials = async () => {
    try {
      setLoading(true)
      const response = await materialsService.getMaterials()
      setMaterials(response.data)
    } catch (error) {
      console.error("Erreur lors de la récupération des matières premières:", error)
      setMaterials([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateMaterial = () => {
    setEditingMaterial(null)
    setShowForm(true)
  }

  const handleEditMaterial = (material) => {
    setEditingMaterial(material)
    setShowForm(true)
  }

  const handleDeleteMaterial = async (material) => {
    try {
      await materialsService.deleteMaterial(material.id_matiere_premiere)
      fetchMaterials()
      setDeleteConfirm(null)
    } catch (error) {
      console.error("Erreur lors de la suppression:", error)
      if (error.response?.status === 400) {
        alert(`Impossible de supprimer: ${error.response.data.detail}`)
      }
      setDeleteConfirm(null)
    }
  }

  const handleFormSuccess = () => {
    setShowForm(false)
    fetchMaterials()
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingMaterial(null)
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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Matières premières</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Gestion des matières premières</p>
        </div>
        <button
          onClick={handleCreateMaterial}
          className="btn-primary flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          Nouvelle Matière première
        </button>
      </div>

      {/* Liste des matières premières */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {materials.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <Package className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Aucune matière première</h3>
            <p className="text-gray-500 dark:text-gray-400">Commencez par ajouter une nouvelle matière première.</p>
          </div>
        ) : (
          materials.map((material) => (
            <div key={material.id_matiere_premiere} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{material.nom}</h3>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEditMaterial(material)}
                    className="p-2 text-gray-400 dark:text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                    title="Modifier"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setDeleteConfirm(material)}
                    className="p-2 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                    title="Supprimer"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Notes */}
              {material.notes && (
                <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                  <div className="flex items-start">
                    <FileText className="h-4 w-4 text-gray-600 dark:text-gray-400 mr-2 mt-0.5" />
                    <div>
                      <p className="text-gray-800 dark:text-gray-200 text-xs font-medium mb-1">Notes:</p>
                      <p className="text-gray-700 dark:text-gray-300 text-xs line-clamp-3">
                        {material.notes}
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
      <MaterialForm
        isOpen={showForm}
        onClose={handleCloseForm}
        material={editingMaterial}
        onSuccess={handleFormSuccess}
      />

      {/* Modal de confirmation de suppression */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <Package className="h-6 w-6 text-red-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Confirmer la suppression
                </h3>
              </div>
              
              <p className="text-gray-600 mb-6">
                Êtes-vous sûr de vouloir supprimer la matière première <strong>"{deleteConfirm.nom}"</strong> ?
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
                  onClick={() => handleDeleteMaterial(deleteConfirm)}
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

