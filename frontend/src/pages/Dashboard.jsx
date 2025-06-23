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

// Dashboard avec données dynamiques - Version déployée 2025-06-22 23:30
export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isUsingFallback, setIsUsingFallback] = useState(false)

  useEffect(() => {
    fetchDashboardData()
    
    // Rafraîchir les données quand on revient sur la page
    const handleFocus = () => {
      fetchDashboardData()
    }
    
    // Rafraîchir les données quand le localStorage change (nouveaux immeubles)
    const handleStorageChange = (e) => {
      if (e.key === 'localBuildings') {
        fetchDashboardData()
      }
    }
    
    // Rafraîchir les données quand les immeubles sont modifiés
    const handleBuildingsUpdate = (e) => {
      console.log('Buildings updated, refreshing dashboard:', e.detail)
      fetchDashboardData()
    }
    
    window.addEventListener('focus', handleFocus)
    window.addEventListener('storage', handleStorageChange)
    window.addEventListener('buildingsUpdated', handleBuildingsUpdate)
    
    // Rafraîchir périodiquement pour capturer les changements
    const interval = setInterval(fetchDashboardData, 30000) // Toutes les 30 secondes
    
    return () => {
      window.removeEventListener('focus', handleFocus)
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('buildingsUpdated', handleBuildingsUpdate)
      clearInterval(interval)
    }
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      setIsUsingFallback(false)
      
      // Force un nouveau fetch avec timestamp pour éviter le cache
      const response = await dashboardService.getDashboardData()
      console.log('Dashboard data received:', response.data) // Debug
      setDashboardData(response.data)
      
      // Vérifier si on utilise des données de fallback (indicateur dans les logs console)
      const logMessages = JSON.stringify(response.data)
      setIsUsingFallback(logMessages.includes('Mode hors ligne') || logMessages.includes('locale'))
      
    } catch (err) {
      setError('Erreur lors du chargement des données')
      console.error('Dashboard error:', err)
      setIsUsingFallback(true)
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
      value: dashboardData?.totalBuildings || 0,
      icon: Building2,
      color: 'bg-blue-500',
      change: dashboardData?.totalBuildings > 0 ? `${dashboardData.totalBuildings} actifs` : 'Aucun immeuble',
      changeType: 'neutral'
    },
    {
      name: 'Total Unités',
      value: dashboardData?.totalUnits || 0,
      icon: Users,
      color: 'bg-green-500',
      change: dashboardData?.totalUnits > 0 ? `${dashboardData.totalUnits} unités` : 'Aucune unité',
      changeType: 'neutral'
    },
    {
      name: 'Valeur Portfolio',
      value: dashboardData?.portfolioValue ? `${dashboardData.portfolioValue.toLocaleString('fr-CA')}$` : '0$',
      icon: TrendingUp,
      color: 'bg-purple-500',
      change: dashboardData?.portfolioValue > 0 ? 'Valeur totale' : 'Aucune valeur',
      changeType: 'neutral'
    },
    {
      name: 'Revenus Mensuels Estimés',
      value: dashboardData?.monthlyRevenue ? `${Math.round(dashboardData.monthlyRevenue).toLocaleString('fr-CA')}$` : '0$',
      icon: DollarSign,
      color: 'bg-primary-500',
      change: dashboardData?.monthlyRevenue > 0 ? 'Estimation 0.5%/mois' : 'Aucun revenu',
      changeType: 'neutral'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tableau de bord</h1>
          <p className="text-gray-600 mt-1">Vue d'ensemble de vos opérations de construction</p>
          {isUsingFallback && (
            <div className="flex items-center mt-2 text-sm text-amber-600">
              <AlertTriangle className="h-4 w-4 mr-1" />
              <span>Données calculées localement (API indisponible)</span>
            </div>
          )}
        </div>
        <div className="flex items-center space-x-4">
          <button 
            onClick={fetchDashboardData}
            disabled={loading}
            className="btn-secondary flex items-center space-x-2"
          >
            <TrendingUp className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Actualiser</span>
          </button>
          <div className="text-sm text-gray-500">
            Dernière mise à jour: {new Date().toLocaleString('fr-CA')}
          </div>
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
                  <p className={`text-xs ${
                    stat.changeType === 'positive' ? 'text-green-600' : 
                    stat.changeType === 'negative' ? 'text-red-600' : 'text-gray-500'
                  }`}>
                    {stat.change}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Activity Section */}
      {dashboardData?.recentActivity && dashboardData.recentActivity.length > 0 && (
        <div className="card">
          <div className="flex items-center mb-4">
            <TrendingUp className="h-5 w-5 text-blue-500 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">Activité Récente</h2>
          </div>
          <div className="space-y-3">
            {dashboardData.recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <div className={`p-2 rounded-full ${
                  activity.type === 'success' ? 'bg-green-100' : 
                  activity.type === 'info' ? 'bg-blue-100' : 'bg-gray-100'
                }`}>
                  {activity.type === 'success' ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : activity.type === 'info' ? (
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                  ) : (
                    <Building2 className="h-4 w-4 text-gray-600" />
                  )}
                </div>
                <div className="ml-3 flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(activity.timestamp).toLocaleString('fr-CA')}
                  </p>
                </div>
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