import React from 'react'
import { 
  X, 
  Edit, 
  Trash2, 
  Home, 
  MapPin,
  Bed,
  Bath,
  Calendar
} from 'lucide-react'

export default function UnitDetails({ unit, isOpen, onClose, onEdit, onDelete }) {
  if (!isOpen || !unit) return null

  const formatDate = (dateString) => {
    if (!dateString) return 'Non spécifiée'
    return new Date(dateString).toLocaleDateString('fr-CA')
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-primary-100 rounded-lg">
              <Home className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <h2 className="text-2xl font-bold text-gray-900">{unit.adresse_unite}</h2>
              <p className="text-gray-600">Unité {unit.type}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-6 w-6 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Informations générales */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Home className="h-5 w-5 mr-2 text-primary-600" />
              Informations Générales
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Type d'unité</p>
                <p className="text-lg font-semibold text-gray-900">{unit.type}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Adresse complète</p>
                <p className="text-lg font-semibold text-gray-900">{unit.adresse_unite}</p>
              </div>
            </div>
          </div>

          {/* Caractéristiques */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Bed className="h-5 w-5 mr-2 text-primary-600" />
              Caractéristiques
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center mb-2">
                  <Bed className="h-5 w-5 text-gray-600 mr-2" />
                  <p className="text-sm text-gray-600">Nombre de chambres</p>
                </div>
                <p className="text-lg font-semibold text-gray-900">{unit.nbr_chambre}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center mb-2">
                  <Bath className="h-5 w-5 text-gray-600 mr-2" />
                  <p className="text-sm text-gray-600">Nombre de salles de bain</p>
                </div>
                <p className="text-lg font-semibold text-gray-900">{unit.nbr_salle_de_bain}</p>
              </div>
            </div>
          </div>

          {/* Métadonnées */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-primary-600" />
              Métadonnées
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Date de création</p>
                <p className="text-lg font-semibold text-gray-900">{formatDate(unit.date_creation)}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Dernière modification</p>
                <p className="text-lg font-semibold text-gray-900">{formatDate(unit.date_modification)}</p>
              </div>
            </div>
          </div>

          {/* Statut */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Statut</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Disponibilité</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  unit.currentTenants?.length > 0 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {unit.currentTenants?.length > 0 ? 'Occupée' : 'Libre'}
                </span>
              </div>
              {unit.currentTenants?.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm text-gray-600 mb-2">Locataires actuels :</p>
                  <div className="space-y-1">
                    {unit.currentTenants.map((tenant, index) => (
                      <div key={index} className="text-sm text-gray-900">
                        • {tenant.nom} {tenant.prenom}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Fermer
          </button>
          <button
            onClick={() => onEdit(unit)}
            className="px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center"
          >
            <Edit className="h-4 w-4 mr-2" />
            Modifier
          </button>
          <button
            onClick={() => onDelete(unit)}
            className="px-4 py-2 text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors flex items-center"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Supprimer
          </button>
        </div>
      </div>
    </div>
  )
}