import React, { useState, useEffect } from 'react'
import { Package, Plus, Edit, Trash2, Phone, Mail, MapPin } from 'lucide-react'
import { suppliersService } from '../services/api'
import SupplierForm from '../components/SupplierForm'

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingSupplier, setEditingSupplier] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  useEffect(() => {
    fetchSuppliers()
  }, [])

  const fetchSuppliers = async () => {
    try {
      setLoading(true)
      const response = await suppliersService.getSuppliers()
      setSuppliers(response.data)
    } catch (error) {
      console.error("Erreur lors de la récupération des fournisseurs:", error)
      setSuppliers([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSupplier = () => {
    setEditingSupplier(null)
    setShowForm(true)
  }

  const handleEditSupplier = (supplier) => {
    setEditingSupplier(supplier)
    setShowForm(true)
  }

  const handleDeleteSupplier = async (supplier) => {
    try {
      await suppliersService.deleteSupplier(supplier.id_fournisseur)
      fetchSuppliers()
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
    fetchSuppliers()
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingSupplier(null)
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
          <h1 className="text-3xl font-bold text-gray-900">Fournisseurs</h1>
          <p className="text-gray-600 mt-1">Gestion des fournisseurs</p>
        </div>
        <button
          onClick={handleCreateSupplier}
          className="btn-primary flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          Nouveau Fournisseur
        </button>
      </div>

      {/* Liste des fournisseurs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {suppliers.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <Package className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Aucun fournisseur</h3>
            <p className="text-gray-500 dark:text-gray-400">Commencez par ajouter un nouveau fournisseur.</p>
          </div>
        ) : (
          suppliers.map((supplier) => (
            <div key={supplier.id_fournisseur} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{supplier.nom}</h3>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEditSupplier(supplier)}
                    className="p-2 text-gray-400 dark:text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                    title="Modifier"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setDeleteConfirm(supplier)}
                    className="p-2 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                    title="Supprimer"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Adresse */}
              {(supplier.rue || supplier.ville) && (
                <div className="flex items-start text-gray-600 dark:text-gray-400 text-sm mb-2">
                  <MapPin className="h-4 w-4 mr-2 text-gray-500 dark:text-gray-400 mt-0.5" />
                  <div>
                    {supplier.rue && <div>{supplier.rue}</div>}
                    {(supplier.ville || supplier.province || supplier.code_postal) && (
                      <div>
                        {supplier.ville && `${supplier.ville}`}
                        {supplier.ville && supplier.province && ', '}
                        {supplier.province && `${supplier.province}`}
                        {supplier.code_postal && ` ${supplier.code_postal}`}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Contact */}
              <div className="space-y-1">
                {supplier.numero && (
                  <div className="flex items-center text-gray-600 dark:text-gray-400 text-sm">
                    <Phone className="h-4 w-4 mr-2 text-gray-500 dark:text-gray-400" />
                    <span>{supplier.numero}</span>
                  </div>
                )}
                {supplier.adresse_courriel && (
                  <div className="flex items-center text-gray-600 dark:text-gray-400 text-sm">
                    <Mail className="h-4 w-4 mr-2 text-gray-500 dark:text-gray-400" />
                    <span>{supplier.adresse_courriel}</span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Formulaire modal */}
      <SupplierForm
        isOpen={showForm}
        onClose={handleCloseForm}
        supplier={editingSupplier}
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
                Êtes-vous sûr de vouloir supprimer le fournisseur <strong>"{deleteConfirm.nom}"</strong> ?
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
                  onClick={() => handleDeleteSupplier(deleteConfirm)}
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

