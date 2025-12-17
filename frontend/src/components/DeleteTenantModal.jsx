import React, { useState, useEffect } from 'react'
import { X, AlertTriangle, FileText, Calendar, Home, Trash2 } from 'lucide-react'

export default function DeleteTenantModal({ tenant, isOpen, onClose, onConfirm }) {
  const [confirmName, setConfirmName] = useState('')
  const [leases, setLeases] = useState([])
  const [loadingLeases, setLoadingLeases] = useState(true)
  const [canDelete, setCanDelete] = useState(false)

  useEffect(() => {
    if (isOpen && tenant) {
      setConfirmName('')
      loadTenantLeases()
    }
  }, [isOpen, tenant])

  useEffect(() => {
    const expectedName = `${tenant?.nom} ${tenant?.prenom}`.trim()
    setCanDelete(confirmName.trim() === expectedName)
  }, [confirmName, tenant])

  const loadTenantLeases = async () => {
    try {
      setLoadingLeases(true)
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/leases`)
      if (response.ok) {
        const data = await response.json()
        const allLeases = data.data || []
        // Filtrer les baux de ce locataire
        const tenantLeases = allLeases.filter(lease => 
          lease.id_locataire === tenant.id_locataire
        )
        setLeases(tenantLeases)
      }
    } catch (error) {
      console.error('Erreur lors du chargement des baux:', error)
      setLeases([])
    } finally {
      setLoadingLeases(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Non spécifiée'
    return new Date(dateString).toLocaleDateString('fr-CA', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const handleConfirm = () => {
    if (canDelete) {
      onConfirm(tenant)
      onClose()
    }
  }

  if (!isOpen || !tenant) return null

  const expectedName = `${tenant.nom} ${tenant.prenom}`.trim()

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* En-tête avec icône d'avertissement */}
        <div className="bg-red-50 border-b border-red-200 p-6">
          <div className="flex items-start">
            <div className="p-3 bg-red-100 rounded-full mr-4">
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-red-900 mb-2">
                Suppression définitive du locataire
              </h2>
              <p className="text-red-700">
                Cette action est <strong>irréversible</strong> et supprimera toutes les données associées à ce locataire.
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-red-100 rounded-lg transition-colors"
            >
              <X className="h-6 w-6 text-red-600" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Avertissement principal */}
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
            <div className="flex items-start">
              <AlertTriangle className="h-6 w-6 text-red-600 mr-3 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-red-900 mb-2">
                  ⚠️ Attention : Cette action supprimera :
                </h3>
                <ul className="list-disc list-inside space-y-1 text-red-800">
                  <li>Le locataire <strong>{tenant.nom} {tenant.prenom}</strong></li>
                  <li><strong>Tous les baux</strong> associés à ce locataire ({leases.length} bail{leases.length > 1 ? 'x' : ''})</li>
                  <li><strong>Tous les paiements de loyer</strong> liés à ces baux</li>
                  <li><strong>Toutes les données historiques</strong> de ce locataire</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Liste des baux qui seront supprimés */}
          {loadingLeases ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-red-600"></div>
              <span className="ml-2 text-gray-600">Chargement des baux...</span>
            </div>
          ) : leases.length > 0 ? (
            <div className="border border-gray-200 rounded-lg">
              <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                <h3 className="font-semibold text-gray-900 flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-red-600" />
                  Baux qui seront supprimés ({leases.length})
                </h3>
              </div>
              <div className="divide-y divide-gray-200">
                {leases.map((lease, index) => (
                  <div key={lease.id_bail || index} className="p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <Home className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="font-medium text-gray-900">
                            {lease.unite?.adresse_unite || 'Unité non spécifiée'}
                          </span>
                          {lease.unite?.immeuble && (
                            <span className="ml-2 text-sm text-gray-500">
                              ({lease.unite.immeuble.nom_immeuble})
                            </span>
                          )}
                        </div>
                        <div className="flex items-center text-sm text-gray-600 space-x-4">
                          <div className="flex items-center">
                            <Calendar className="h-4 w-4 mr-1" />
                            <span>
                              {formatDate(lease.date_debut)} - {formatDate(lease.date_fin) || 'En cours'}
                            </span>
                          </div>
                          {lease.prix_loyer && (
                            <div className="flex items-center">
                              <span className="font-medium">
                                {parseFloat(lease.prix_loyer).toLocaleString('fr-CA', {
                                  style: 'currency',
                                  currency: 'CAD',
                                  minimumFractionDigits: 0
                                })}/mois
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center text-gray-600">
              <FileText className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p>Aucun bail associé à ce locataire</p>
            </div>
          )}

          {/* Double confirmation - taper le nom */}
          <div className="border-2 border-red-200 rounded-lg p-4 bg-red-50">
            <label className="block text-sm font-semibold text-red-900 mb-2">
              Pour confirmer, tapez le nom complet du locataire :
            </label>
            <input
              type="text"
              value={confirmName}
              onChange={(e) => setConfirmName(e.target.value)}
              placeholder={`${tenant.nom} ${tenant.prenom}`}
              className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 ${
                confirmName && !canDelete
                  ? 'border-red-500 bg-red-100'
                  : canDelete
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-300 bg-white'
              }`}
            />
            {confirmName && !canDelete && (
              <p className="mt-2 text-sm text-red-600">
                Le nom ne correspond pas. Tapez exactement : <strong>{expectedName}</strong>
              </p>
            )}
            {canDelete && (
              <p className="mt-2 text-sm text-green-700 font-medium">
                ✓ Nom correct. Vous pouvez maintenant supprimer.
              </p>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3 p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-6 py-3 text-gray-700 bg-white border-2 border-gray-300 hover:bg-gray-50 rounded-lg transition-colors font-medium"
          >
            Annuler
          </button>
          <button
            onClick={handleConfirm}
            disabled={!canDelete}
            className={`px-6 py-3 rounded-lg transition-colors font-medium flex items-center ${
              canDelete
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            <Trash2 className="h-5 w-5 mr-2" />
            Supprimer définitivement
          </button>
        </div>
      </div>
    </div>
  )
}

