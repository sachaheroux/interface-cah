import React from 'react'
import { X, Building2, MapPin, Users, DollarSign, Home, Phone, FileText, Trash2 } from 'lucide-react'
// import { getBuildingTypeLabel } from '../types/building' // Fonction supprimée

export default function BuildingDetails({ building, isOpen, onClose, onDelete }) {
  if (!isOpen || !building) return null

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const formatAddress = (address) => {
    if (typeof address === 'string') return address
    return `${address.street}, ${address.city}, ${address.province} ${address.postalCode}, ${address.country}`
  }

  const isUserCreatedBuilding = () => {
    // Les immeubles créés par l'utilisateur ont un ID >= 4 (les 3 premiers sont les immeubles par défaut)
    // Ou bien ils sont dans localStorage (mode fallback)
    if (building.id >= 4) return true
    
    // Vérifier aussi dans localStorage pour le mode fallback
    const localBuildings = JSON.parse(localStorage.getItem('localBuildings') || '[]')
    return localBuildings.some(b => b.id === building.id)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-primary-100 rounded-lg">
              <Building2 className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <div className="flex items-center space-x-2">
                <h2 className="text-2xl font-bold text-gray-900">{building.name}</h2>
                {isUserCreatedBuilding() && (
                  <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                    Créé par vous
                  </span>
                )}
              </div>
              <p className="text-gray-600">{building.type || 'Non spécifié'}</p>
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
        <div className="p-6 space-y-8">
          {/* Informations générales */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Home className="h-5 w-5 mr-2 text-primary-600" />
              Informations Générales
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Nombre d'unités</p>
                <p className="text-lg font-semibold text-gray-900">{building.units}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Nombre d'étages</p>
                <p className="text-lg font-semibold text-gray-900">{building.floors}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Année de construction</p>
                <p className="text-lg font-semibold text-gray-900">{building.yearBuilt}</p>
              </div>
              {building.totalArea && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Superficie totale</p>
                  <p className="text-lg font-semibold text-gray-900">{building.totalArea} pi²</p>
                </div>
              )}
            </div>
          </div>

          {/* Adresse */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <MapPin className="h-5 w-5 mr-2 text-primary-600" />
              Adresse
            </h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-900">{formatAddress(building.address)}</p>
            </div>
          </div>

          {/* Caractéristiques */}
          {building.characteristics && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Building2 className="h-5 w-5 mr-2 text-primary-600" />
                Caractéristiques
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Places de parking</p>
                      <p className="text-lg font-semibold text-gray-900">{building.characteristics.parking || 0}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Balcons</p>
                      <p className="text-lg font-semibold text-gray-900">{building.characteristics.balconies || 0}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Chauffage</p>
                      <p className="text-lg font-semibold text-gray-900 capitalize">
                        {building.characteristics.heating === 'electric' ? 'Électrique' :
                         building.characteristics.heating === 'gas' ? 'Gaz' :
                         building.characteristics.heating === 'oil' ? 'Mazout' :
                         building.characteristics.heating === 'heat_pump' ? 'Thermopompe' :
                         building.characteristics.heating || '-'}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-3">Équipements</p>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { key: 'elevator', label: 'Ascenseur' },
                      { key: 'storage', label: 'Rangement' },
                      { key: 'laundry', label: 'Buanderie' },
                      { key: 'airConditioning', label: 'Climatisation' },
                      { key: 'internet', label: 'Internet inclus' },
                      { key: 'security', label: 'Sécurité' }
                    ].map(item => (
                      <div key={item.key} className="flex items-center">
                        <div className={`w-2 h-2 rounded-full mr-2 ${
                          building.characteristics[item.key] ? 'bg-green-500' : 'bg-gray-300'
                        }`}></div>
                        <span className={`text-sm ${
                          building.characteristics[item.key] ? 'text-gray-900' : 'text-gray-500'
                        }`}>
                          {item.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Informations financières */}
          {building.financials && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <DollarSign className="h-5 w-5 mr-2 text-primary-600" />
                Informations Financières
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <p className="text-sm text-green-700">Prix d'achat</p>
                  <p className="text-lg font-semibold text-green-900">
                    {formatCurrency(building.financials.purchasePrice)}
                  </p>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-700">Mise de fond</p>
                  <p className="text-lg font-semibold text-blue-900">
                    {formatCurrency(building.financials.downPayment)}
                  </p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                  <p className="text-sm text-purple-700">Taux d'intérêt</p>
                  <p className="text-lg font-semibold text-purple-900">
                    {building.financials.interestRate}%
                  </p>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                  <p className="text-sm text-yellow-700">Valeur actuelle</p>
                  <p className="text-lg font-semibold text-yellow-900">
                    {formatCurrency(building.financials.currentValue)}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Contacts */}
          {building.contacts && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Phone className="h-5 w-5 mr-2 text-primary-600" />
                Contacts
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {building.contacts.owner && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 font-medium">Propriétaire</p>
                    <p className="text-gray-900 mt-1">{building.contacts.owner}</p>
                  </div>
                )}
                {building.contacts.bank && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 font-medium">Banque</p>
                    <p className="text-gray-900 mt-1">{building.contacts.bank}</p>
                  </div>
                )}
                {building.contacts.contractor && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 font-medium">Entrepreneur</p>
                    <p className="text-gray-900 mt-1">{building.contacts.contractor}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Notes */}
          {building.notes && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <FileText className="h-5 w-5 mr-2 text-primary-600" />
                Notes
              </h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-900 whitespace-pre-wrap">{building.notes}</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <div>
            {onDelete && (
              <button
                onClick={() => onDelete(building)}
                className="px-4 py-2 text-red-700 bg-red-50 border border-red-300 rounded-lg hover:bg-red-100 transition-colors flex items-center space-x-2"
              >
                <Trash2 className="h-4 w-4" />
                <span>Supprimer</span>
              </button>
            )}
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  )
} 