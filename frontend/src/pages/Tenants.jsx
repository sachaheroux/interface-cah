import React, { useState, useEffect } from 'react'
import { Users, Plus, Phone, Mail, Home } from 'lucide-react'
import { tenantsService } from '../services/api'

export default function Tenants() {
  const [tenants, setTenants] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTenants()
  }, [])

  const fetchTenants = async () => {
    try {
      const response = await tenantsService.getTenants()
      setTenants(response.data)
    } catch (err) {
      console.error('Tenants error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Locataires</h1>
          <p className="text-gray-600 mt-1">Gérez vos locataires et leurs informations</p>
        </div>
        <button className="btn-primary flex items-center">
          <Plus className="h-5 w-5 mr-2" />
          Nouveau Locataire
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tenants.map((tenant) => (
          <div key={tenant.id} className="card">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-green-100 rounded-lg">
                <Users className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-semibold text-gray-900">{tenant.name}</h3>
                <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                  tenant.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {tenant.status === 'active' ? 'Actif' : 'En attente'}
                </span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center text-gray-600">
                <Home className="h-4 w-4 mr-2" />
                <span className="text-sm">{tenant.building} - {tenant.unit}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 