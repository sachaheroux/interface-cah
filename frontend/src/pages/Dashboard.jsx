import React, { useState, useEffect } from 'react'
import { 
  Building2, 
  Users, 
  DollarSign, 
  AlertTriangle, 
  TrendingUp
} from 'lucide-react'
import { dashboardService, unitsService } from '../services/api'

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isUsingFallback, setIsUsingFallback] = useState(false)
  const [occupancyRate, setOccupancyRate] = useState(0)

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
    
    return () => {
      window.removeEventListener('focus', handleFocus)
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('buildingsUpdated', handleBuildingsUpdate)
    }
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      setIsUsingFallback(false)
      
      // Force un nouveau fetch avec timestamp pour éviter le cache
      const response = await dashboardService.getDashboardData()
      console.log('Dashboard data received:', response.data)
      setDashboardData(response.data)
      
      // Vérifier si on utilise des données de fallback de manière plus robuste
      const isFallback = response.data?.isFallback === true || 
                        response.data?.source === 'localStorage' ||
                        response.data?.mode === 'offline';
      setIsUsingFallback(isFallback)
      
      // Calculer le taux d'occupation comme dans Buildings.jsx
      await calculateOccupancyRate()
      
    } catch (err) {
      setError('Erreur lors du chargement des données')
      console.error('Dashboard error:', err)
      setIsUsingFallback(true)
    } finally {
      setLoading(false)
    }
  }

  const calculateOccupancyRate = async () => {
    try {
      const response = await unitsService.getUnits()
      const units = response.data || []
      const totalUnits = units.length
      
      // Compter les unités occupées (qui ont au moins un locataire)
      const occupied = units.filter(unit => unit.locataires && unit.locataires.length > 0).length
      
      // Calculer le taux d'occupation
      const rate = totalUnits > 0 ? Math.round((occupied / totalUnits) * 100) : 0
      setOccupancyRate(rate)
    } catch (error) {
      console.error('Erreur lors du calcul du taux d\'occupation:', error)
      setOccupancyRate(0)
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
      name: 'Taux d\'Occupation',
      value: `${occupancyRate}%`,
      icon: Users,
      color: 'bg-primary-500',
      change: occupancyRate >= 90 ? 'Excellent taux' : occupancyRate >= 80 ? 'Bon taux' : 'À améliorer',
      changeType: occupancyRate >= 90 ? 'positive' : occupancyRate >= 80 ? 'neutral' : 'negative'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Tableau de bord</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Vue d'ensemble de vos opérations de construction</p>
          {isUsingFallback && (
            <div className="flex items-center mt-2 text-sm text-amber-600 dark:text-amber-400">
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
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="card dark:bg-gray-800 dark:border-gray-700">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
                  <p className={`text-xs ${
                    stat.changeType === 'positive' ? 'text-green-600 dark:text-green-400' : 
                    stat.changeType === 'negative' ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-400'
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
        <div className="card dark:bg-gray-800 dark:border-gray-700">
          <div className="flex items-center mb-4">
            <TrendingUp className="h-5 w-5 text-blue-500 dark:text-blue-400 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Activité Récente</h2>
          </div>
          <div className="space-y-3">
            {dashboardData.recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                <div className={`p-2 rounded-full ${
                  activity.type === 'success' ? 'bg-green-100 dark:bg-green-900/20' : 
                  activity.type === 'info' ? 'bg-blue-100 dark:bg-blue-900/20' : 'bg-gray-100 dark:bg-gray-700'
                }`}>
                  {activity.type === 'success' ? (
                    <TrendingUp className="h-4 w-4 text-green-600 dark:text-green-400" />
                  ) : activity.type === 'info' ? (
                    <TrendingUp className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                  ) : (
                    <Building2 className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                  )}
                </div>
                <div className="ml-3 flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{activity.message}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(activity.timestamp).toLocaleString('fr-CA')}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
