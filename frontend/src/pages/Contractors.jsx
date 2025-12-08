import React, { useState, useEffect } from 'react'
import { Truck, Plus, Edit, Trash2, Phone, Mail, MapPin } from 'lucide-react'
import { contractorsService } from '../services/api'
import ContractorForm from '../components/ContractorForm'

export default function Contractors() {
  const [contractors, setContractors] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingContractor, setEditingContractor] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  useEffect(() => {
    fetchContractors()
  }, [])

  const fetchContractors = async () => {
    try {
      setLoading(true)
      const response = await contractorsService.getContractors()
      setContractors(response.data)
    } catch (error) {
      console.error("Erreur lors de la récupération des sous-traitants:", error)
      setContractors([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateContractor = () => {
    setEditingContractor(null)
    setShowForm(true)
  }

  const handleEditContractor = (contractor) => {
    setEditingContractor(contractor)
    setShowForm(true)
  }

  const handleDeleteContractor = async (contractor) => {
    try {
      await contractorsService.deleteContractor(contractor.id_st)
      fetchContractors()
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
    fetchContractors()
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingContractor(null)
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
          <h1 className="text-3xl font-bold text-gray-900">Sous-traitants</h1>
          <p className="text-gray-600 mt-1">Gestion des fournisseurs et sous-traitants</p>
        </div>
        <button
          onClick={handleCreateContractor}
          className="btn-primary flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          Nouveau Sous-traitant
        </button>
      </div>

      {/* Liste des sous-traitants */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {contractors.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <Truck className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun sous-traitant</h3>
            <p className="text-gray-500">Commencez par ajouter un nouveau sous-traitant.</p>
          </div>
        ) : (
          contractors.map((contractor) => (
            <div key={contractor.id_st} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900">{contractor.nom}</h3>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEditContractor(contractor)}
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                    title="Modifier"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setDeleteConfirm(contractor)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                    title="Supprimer"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Adresse */}
              {(contractor.rue || contractor.ville) && (
                <div className="flex items-start text-gray-600 text-sm mb-2">
                  <MapPin className="h-4 w-4 mr-2 text-gray-500 mt-0.5" />
                  <div>
                    {contractor.rue && <div>{contractor.rue}</div>}
                    {(contractor.ville || contractor.province || contractor.code_postal) && (
                      <div>
                        {contractor.ville && `${contractor.ville}`}
                        {contractor.ville && contractor.province && ', '}
                        {contractor.province && `${contractor.province}`}
                        {contractor.code_postal && ` ${contractor.code_postal}`}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Contact */}
              <div className="space-y-1">
                {contractor.numero && (
                  <div className="flex items-center text-gray-600 text-sm">
                    <Phone className="h-4 w-4 mr-2 text-gray-500" />
                    <span>{contractor.numero}</span>
                  </div>
                )}
                {contractor.adresse_courriel && (
                  <div className="flex items-center text-gray-600 text-sm">
                    <Mail className="h-4 w-4 mr-2 text-gray-500" />
                    <span>{contractor.adresse_courriel}</span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Formulaire modal */}
      <ContractorForm
        isOpen={showForm}
        onClose={handleCloseForm}
        contractor={editingContractor}
        onSuccess={handleFormSuccess}
      />

      {/* Modal de confirmation de suppression */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <Truck className="h-6 w-6 text-red-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Confirmer la suppression
                </h3>
              </div>
              
              <p className="text-gray-600 mb-6">
                Êtes-vous sûr de vouloir supprimer le sous-traitant <strong>"{deleteConfirm.nom}"</strong> ?
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
                  onClick={() => handleDeleteContractor(deleteConfirm)}
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