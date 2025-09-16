import React from 'react'
import { 
  X, 
  Edit, 
  Trash2, 
  User, 
  DollarSign, 
  Home, 
  Calendar,
  Phone,
  Mail,
  MapPin,
  UserCheck
} from 'lucide-react'
import { getUnitTypeLabel } from '../types/unit'

export default function UnitDetails({ unit, isOpen, onClose, onEdit, onDelete }) {
  if (!isOpen || !unit) return null

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Non spécifiée'
    return new Date(dateString).toLocaleDateString('fr-CA')
  }

  const getRelationshipLabel = (relationship) => {
    switch (relationship) {
      case 'parent': return 'Parent'
      case 'conjoint': return 'Conjoint(e)'
      case 'enfant': return 'Enfant'
      case 'frere_soeur': return 'Frère/Sœur'
      case 'ami': return 'Ami(e)'
      case 'autre': return 'Autre'
      default: return relationship
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Détails de l'unité #{unit.unitNumber}
            </h2>
            <p className="text-sm text-gray-600 mt-1 flex items-center">
              <MapPin className="h-4 w-4 mr-1" />
              {unit.address} - {unit.buildingName}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Informations de base */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <Home className="h-8 w-8 text-primary-600 mx-auto mb-2" />
              <h3 className="text-sm font-medium text-gray-700">Type</h3>
              <p className="text-lg font-semibold text-gray-900">
                {getUnitTypeLabel(unit.type)}
              </p>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="mx-auto mb-2 w-8 h-8 flex items-center justify-center">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${unit.status === 'occupied' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {unit.status === 'occupied' ? 'Occupée' : 'Libre'}
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-700">Statut</h3>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="h-8 w-8 text-blue-600 mx-auto mb-2 flex items-center justify-center">
                <span className="text-lg font-bold">{unit.area}</span>
              </div>
              <h3 className="text-sm font-medium text-gray-700">Superficie</h3>
              <p className="text-sm text-gray-600">pieds carrés</p>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="h-8 w-8 text-green-600 mx-auto mb-2 flex items-center justify-center">
                <span className="text-lg font-bold">{unit.bedrooms}</span>
              </div>
              <h3 className="text-sm font-medium text-gray-700">Chambres</h3>
              <p className="text-sm text-gray-600">{unit.bathrooms} sdb</p>
            </div>
          </div>

          {/* Informations locatives */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <DollarSign className="h-5 w-5 mr-2" />
              Informations locatives
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-700">Loyer mensuel</h4>
                <p className="text-xl font-bold text-green-600">
                  {formatCurrency(unit.rental?.monthlyRent || 0)}
                </p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700">Dépôt de garantie</h4>
                <p className="text-lg font-semibold text-gray-900">
                  {formatCurrency(unit.rental?.deposit || 0)}
                </p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700">Échéance du loyer</h4>
                <p className="text-lg font-semibold text-gray-900">
                  Le {unit.rental?.rentDueDay || 1} de chaque mois
                </p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700">Début du bail</h4>
                <p className="text-lg font-semibold text-gray-900">
                  {formatDate(unit.rental?.leaseStart)}
                </p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700">Fin du bail</h4>
                <p className="text-lg font-semibold text-gray-900">
                  {formatDate(unit.rental?.leaseEnd)}
                </p>
              </div>
            </div>
          </div>

          {/* Locataires actuels */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Locataires actuels
            </h3>
            {unit.tenant?.name ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Nom complet</h4>
                    <p className="text-lg font-semibold text-gray-900">{unit.tenant.name}</p>
                  </div>

                  {unit.tenant.email && (
                    <div className="flex items-center space-x-2">
                      <Mail className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-900">{unit.tenant.email}</span>
                    </div>
                  )}

                  {unit.tenant.phone && (
                    <div className="flex items-center space-x-2">
                      <Phone className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-900">{unit.tenant.phone}</span>
                    </div>
                  )}
                </div>

                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Date d'emménagement</h4>
                    <p className="text-gray-900 flex items-center">
                      <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                      {formatDate(unit.tenant.moveInDate)}
                    </p>
                  </div>

                  {unit.tenant.moveOutDate && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700">Date de déménagement</h4>
                      <p className="text-gray-900 flex items-center">
                        <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                        {formatDate(unit.tenant.moveOutDate)}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-gray-600">Aucun locataire actuellement.</p>
            )}

            {/* Contact d'urgence */}
            {unit.tenant?.emergencyContact?.name && (
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h4 className="text-md font-medium text-gray-900 mb-3 flex items-center">
                  <UserCheck className="h-4 w-4 mr-2" />
                  Contact d'urgence
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Nom: </span>
                    <span className="font-medium">{unit.tenant.emergencyContact.name}</span>
                  </div>
                  {unit.tenant.emergencyContact.phone && (
                    <div>
                      <span className="text-sm text-gray-600">Téléphone: </span>
                      <span className="font-medium">{unit.tenant.emergencyContact.phone}</span>
                    </div>
                  )}
                  {unit.tenant.emergencyContact.relationship && (
                    <div>
                      <span className="text-sm text-gray-600">Relation: </span>
                      <span className="font-medium">
                        {getRelationshipLabel(unit.tenant.emergencyContact.relationship)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Notes */}
          {unit.notes && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Notes et commentaires</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700 whitespace-pre-wrap">{unit.notes}</p>
              </div>
            </div>
          )}

          {/* Métadonnées */}
          <div className="border-t pt-6 text-sm text-gray-500">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="font-medium">Créée le: </span>
                {formatDate(unit.createdAt)}
              </div>
              <div>
                <span className="font-medium">Modifiée le: </span>
                {formatDate(unit.updatedAt)}
              </div>
            </div>
          </div>
        </div>

        {/* Boutons d'action */}
        <div className="flex justify-end space-x-4 p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white hover:bg-gray-100 border border-gray-300 rounded-lg transition-colors"
          >
            Fermer
          </button>
          <button
            onClick={() => onEdit(unit)}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors flex items-center"
          >
            <Edit className="h-4 w-4 mr-2" />
            Modifier
          </button>
          <button
            onClick={() => onDelete(unit)}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Supprimer
          </button>
        </div>
      </div>
    </div>
  )
} 