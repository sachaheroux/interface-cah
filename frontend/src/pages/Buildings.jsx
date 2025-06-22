import React, { useState, useEffect } from 'react'
import { Building2, MapPin, Users, Plus, Edit, Eye } from 'lucide-react'
import { buildingsService } from '../services/api'

export default function Buildings() {
  const [buildings, setBuildings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchBuildings()
  }, [])

  const fetchBuildings = async () => {
    try {
      setLoading(true)
      const response = await buildingsService.getBuildings()
      setBuildings(response.data)
    } catch (err) {
      setError('Erreur lors du chargement des immeubles')
      console.error('Buildings error:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'construction':
        return 'bg-yellow-100 text-yellow-800'
      case 'maintenance':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'active':
        return 'Actif'
      case 'construction':
        return 'En construction'
      case 'maintenance':
        return 'Maintenance'
      default:
        return status
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Immeubles</h1>
          <p className="text-gray-600 mt-1">Gérez vos propriétés et leurs informations</p>
        </div>
        <button className="btn-primary flex items-center">
          <Plus className="h-5 w-5 mr-2" />
          Nouvel Immeuble
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Buildings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {buildings.map((building) => (
          <div key={building.id} className="card hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <Building2 className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-semibold text-gray-900">{building.name}</h3>
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(building.status)}`}>
                    {getStatusText(building.status)}
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center text-gray-600">
                <MapPin className="h-4 w-4 mr-2" />
                <span className="text-sm">{building.address}</span>
              </div>
              
              <div className="flex items-center text-gray-600">
                <Users className="h-4 w-4 mr-2" />
                <span className="text-sm">{building.units} unités</span>
              </div>
            </div>

            <div className="mt-6 flex space-x-2">
              <button className="flex-1 btn-primary text-sm py-2">
                <Eye className="h-4 w-4 mr-1" />
                Voir Détails
              </button>
              <button className="flex-1 btn-secondary text-sm py-2">
                <Edit className="h-4 w-4 mr-1" />
                Modifier
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {buildings.length === 0 && !loading && !error && (
        <div className="text-center py-12">
          <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun immeuble</h3>
          <p className="text-gray-600 mb-4">Commencez par ajouter votre premier immeuble.</p>
          <button className="btn-primary">
            <Plus className="h-5 w-5 mr-2" />
            Ajouter un Immeuble
          </button>
        </div>
      )}
    </div>
  )
} 