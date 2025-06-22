import React, { useState, useEffect } from 'react'
import { 
  Building2, 
  Users, 
  Wrench, 
  DollarSign, 
  AlertTriangle, 
  TrendingUp,
  Calendar,
  CheckCircle
} from 'lucide-react'
import { dashboardService } from '../services/api'

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const response = await dashboardService.getDashboardData()
      setDashboardData(response.data)
    } catch (err) {
      setError('Erreur lors du chargement des données')
      console.error('Dashboard error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Erreur</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  const stats = [
    {
      name: 'Total Immeubles',
      value: dashboardData?.total_buildings || 0,
      icon: Building2,
      color: 'bg-blue-500',
      change: '+2 ce mois',
      changeType: 'positive'
    },
    {
      name: 'Total Locataires',
      value: dashboardData?.total_tenants || 0,
      icon: Users,
      color: 'bg-green-500',
      change: '+5 ce mois',
      changeType: 'positive'
    },
    {
      name: 'Entretiens en Attente',
      value: dashboardData?.pending_maintenance || 0,
      icon: Wrench,
      color: 'bg-yellow-500',
      change: '-2 cette semaine',
      changeType: 'positive'
    },
    {
      name: 'Revenus Mensuels',
      value: `${dashboardData?.monthly_revenue?.toLocaleString('fr-CA')}$` || '0$',
      icon: DollarSign,
      color: 'bg-primary-500',
      change: '+12% vs mois dernier',
      changeType: 'positive'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tableau de bord</h1>
          <p className="text-gray-600 mt-1">Vue d'ensemble de vos opérations de construction</p>
        </div>
        <div className="text-sm text-gray-500">
          Dernière mise à jour: {new Date().toLocaleString('fr-CA')}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className={`text-xs ${stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
                    {stat.change}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Alerts Section */}
      {dashboardData?.alerts && dashboardData.alerts.length > 0 && (
        <div className="card">
          <div className="flex items-center mb-4">
            <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">Alertes et Notifications</h2>
          </div>
          <div className="space-y-3">
            {dashboardData.alerts.map((alert, index) => (
              <div key={index} className="flex items-center p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className={`p-2 rounded-full ${
                  alert.type === 'maintenance' ? 'bg-yellow-100' : 'bg-red-100'
                }`}>
                  {alert.type === 'maintenance' ? (
                    <Wrench className="h-4 w-4 text-yellow-600" />
                  ) : (
                    <DollarSign className="h-4 w-4 text-red-600" />
                  )}
                </div>
                <div className="ml-3 flex-1">
                  <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                  <p className="text-xs text-gray-500">Il y a 2 heures</p>
                </div>
                <button className="text-gray-400 hover:text-gray-600">
                  <CheckCircle className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions Rapides</h2>
          <div className="grid grid-cols-2 gap-3">
            <button className="btn-primary text-center py-3">
              <Building2 className="h-5 w-5 mx-auto mb-1" />
              <span className="text-sm">Nouvel Immeuble</span>
            </button>
            <button className="btn-secondary text-center py-3">
              <Users className="h-5 w-5 mx-auto mb-1" />
              <span className="text-sm">Nouveau Locataire</span>
            </button>
            <button className="btn-secondary text-center py-3">
              <Wrench className="h-5 w-5 mx-auto mb-1" />
              <span className="text-sm">Demande Entretien</span>
            </button>
            <button className="btn-secondary text-center py-3">
              <Calendar className="h-5 w-5 mx-auto mb-1" />
              <span className="text-sm">Planifier Tâche</span>
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Activité Récente</h2>
          <div className="space-y-3">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">Nouveau locataire ajouté - Immeuble A</p>
                <p className="text-xs text-gray-500">Il y a 1 heure</p>
              </div>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-blue-400 rounded-full mr-3"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">Entretien complété - Plomberie Immeuble B</p>
                <p className="text-xs text-gray-500">Il y a 3 heures</p>
              </div>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-yellow-400 rounded-full mr-3"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">Facture en attente - Électricité</p>
                <p className="text-xs text-gray-500">Il y a 5 heures</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 