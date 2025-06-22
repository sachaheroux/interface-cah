import React, { useState, useEffect } from 'react'
import { Wrench, Plus, AlertCircle, Clock, CheckCircle } from 'lucide-react'
import { maintenanceService } from '../services/api'

export default function Maintenance() {
  const [maintenance, setMaintenance] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMaintenance()
  }, [])

  const fetchMaintenance = async () => {
    try {
      const response = await maintenanceService.getMaintenance()
      setMaintenance(response.data)
    } catch (err) {
      console.error('Maintenance error:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case 'in_progress':
        return <Clock className="h-5 w-5 text-yellow-500" />
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      default:
        return <Wrench className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'pending':
        return 'En attente'
      case 'in_progress':
        return 'En cours'
      case 'completed':
        return 'Terminé'
      default:
        return status
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
          <h1 className="text-3xl font-bold text-gray-900">Entretien & Réparations</h1>
          <p className="text-gray-600 mt-1">Suivi des interventions et maintenance</p>
        </div>
        <button className="btn-primary flex items-center">
          <Plus className="h-5 w-5 mr-2" />
          Nouvelle Demande
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {maintenance.map((item) => (
          <div key={item.id} className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                {getStatusIcon(item.status)}
                <span className="ml-2 text-sm font-medium">{getStatusText(item.status)}</span>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full ${
                item.priority === 'high' ? 'bg-red-100 text-red-800' :
                item.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-green-100 text-green-800'
              }`}>
                {item.priority === 'high' ? 'Urgent' : item.priority === 'medium' ? 'Moyen' : 'Faible'}
              </span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{item.type}</h3>
            <p className="text-gray-600 mb-2">{item.building}</p>
          </div>
        ))}
      </div>
    </div>
  )
} 