import React from 'react'
import { 
  X, 
  Edit, 
  Trash2, 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  DollarSign, 
  UserCheck,
  FileText,
  Calendar,
  Building2
} from 'lucide-react'
import { getTenantStatusLabel, getTenantStatusColor, getRelationshipLabel } from '../types/tenant'

export default function TenantDetails({ tenant, isOpen, onClose, onEdit, onDelete }) {
  if (!isOpen || !tenant) return null

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

  const formatAddress = (address) => {
    if (!address || !address.street) return 'Non spécifiée'
    const parts = [
      address.street,
      address.city,
      address.province,
      address.postalCode
    ].filter(Boolean)
    return parts.join(', ')
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Détails du locataire
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {tenant.name}
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
          {/* Informations principales */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <User className="h-8 w-8 text-primary-600 mx-auto mb-2" />
              <h3 className="text-sm font-medium text-gray-700">Nom</h3>
              <p className="text-lg font-semibold text-gray-900">{tenant.name}</p>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="mx-auto mb-2 w-8 h-8 flex items-center justify-center">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTenantStatusColor(tenant.status)}`}>
                  {getTenantStatusLabel(tenant.status)}
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-700">Statut</h3>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <Mail className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h3 className="text-sm font-medium text-gray-700">Email</h3>
              <p className="text-sm text-gray-900">{tenant.email || 'Non spécifié'}</p>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <Phone className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <h3 className="text-sm font-medium text-gray-700">Téléphone</h3>
              <p className="text-sm text-gray-900">{tenant.phone || 'Non spécifié'}</p>
            </div>
          </div>

          {/* Adresse personnelle */}
          {tenant.personalAddress?.street && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <MapPin className="h-5 w-5 mr-2" />
                Adresse personnelle
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-900">{formatAddress(tenant.personalAddress)}</p>
              </div>
            </div>
          )}

          {/* Contact d'urgence */}
          {tenant.emergencyContact?.name && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <UserCheck className="h-5 w-5 mr-2" />
                Contact d'urgence
              </h3>
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Nom: </span>
                    <span className="font-medium">{tenant.emergencyContact.name}</span>
                  </div>
                  {tenant.emergencyContact.phone && (
                    <div>
                      <span className="text-sm text-gray-600">Téléphone: </span>
                      <span className="font-medium">{tenant.emergencyContact.phone}</span>
                    </div>
                  )}
                  {tenant.emergencyContact.email && (
                    <div>
                      <span className="text-sm text-gray-600">Email: </span>
                      <span className="font-medium">{tenant.emergencyContact.email}</span>
                    </div>
                  )}
                  {tenant.emergencyContact.relationship && (
                    <div>
                      <span className="text-sm text-gray-600">Relation: </span>
                      <span className="font-medium">
                        {getRelationshipLabel(tenant.emergencyContact.relationship)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Informations financières */}
          {(tenant.financial?.monthlyIncome > 0 || tenant.financial?.creditScore > 0 || tenant.financial?.employer) && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <DollarSign className="h-5 w-5 mr-2" />
                Informations financières
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {tenant.financial.monthlyIncome > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Revenu mensuel</h4>
                    <p className="text-xl font-bold text-green-600">
                      {formatCurrency(tenant.financial.monthlyIncome)}
                    </p>
                  </div>
                )}

                {tenant.financial.creditScore > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Cote de crédit</h4>
                    <p className="text-lg font-semibold text-gray-900">
                      {tenant.financial.creditScore}
                    </p>
                  </div>
                )}

                {tenant.financial.employer && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Employeur</h4>
                    <p className="text-lg font-semibold text-gray-900">
                      {tenant.financial.employer}
                    </p>
                    {tenant.financial.employerPhone && (
                      <p className="text-sm text-gray-600">
                        {tenant.financial.employerPhone}
                      </p>
                    )}
                  </div>
                )}

                {tenant.financial.bankAccount && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Compte bancaire</h4>
                    <p className="text-lg font-semibold text-gray-900">
                      {tenant.financial.bankAccount}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Unités occupées */}
          {(tenant.building || tenant.unit) && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Building2 className="h-5 w-5 mr-2" />
                Unité actuelle
              </h3>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center">
                  <Building2 className="h-5 w-5 text-green-600 mr-2" />
                  <span className="font-medium text-green-900">
                    {tenant.building} - {tenant.unit}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Notes */}
          {tenant.notes && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Notes et commentaires
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700 whitespace-pre-wrap">{tenant.notes}</p>
              </div>
            </div>
          )}

          {/* Métadonnées */}
          <div className="border-t pt-6 text-sm text-gray-500">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="font-medium">Créé le: </span>
                {formatDate(tenant.createdAt)}
              </div>
              <div>
                <span className="font-medium">Modifié le: </span>
                {formatDate(tenant.updatedAt)}
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
            onClick={() => onEdit(tenant)}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors flex items-center"
          >
            <Edit className="h-4 w-4 mr-2" />
            Modifier
          </button>
          <button
            onClick={() => onDelete(tenant)}
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