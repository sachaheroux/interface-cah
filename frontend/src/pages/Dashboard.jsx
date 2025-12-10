import React, { useState, useEffect } from 'react'
import { 
  Building2, 
  Users, 
  DollarSign, 
  AlertTriangle, 
  TrendingUp,
  Calendar,
  FileText,
  CheckCircle
} from 'lucide-react'
import { dashboardService, unitsService, invoicesSTService } from '../services/api'
import api from '../services/api'

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isUsingFallback, setIsUsingFallback] = useState(false)
  const [occupancyRate, setOccupancyRate] = useState(0)
  const [unpaidRents, setUnpaidRents] = useState([])
  const [pendingInvoices, setPendingInvoices] = useState([])

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
      
      // Charger les loyers non payés et les factures à payer
      await loadUnpaidRents()
      await loadPendingInvoices()
      
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

  const loadUnpaidRents = async () => {
    try {
      // Récupérer tous les baux actifs
      const leasesResponse = await api.get('/api/leases')
      const leases = Array.isArray(leasesResponse.data) ? leasesResponse.data : (leasesResponse.data.data || [])
      
      // Obtenir le mois dernier
      const today = new Date()
      const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1)
      const lastMonthYear = lastMonth.getFullYear()
      const lastMonthMonth = lastMonth.getMonth() + 1
      
      const unpaid = []
      
      // Pour chaque bail actif, vérifier s'il y a un paiement pour le mois dernier
      for (const lease of leases) {
        // Vérifier si le bail était actif le mois dernier
        if (!lease.date_debut || !lease.date_fin) continue
        
        const leaseStart = new Date(lease.date_debut)
        const leaseEnd = new Date(lease.date_fin)
        const checkDate = new Date(lastMonthYear, lastMonthMonth - 1, 1)
        
        // Si le bail était actif le mois dernier
        if (checkDate >= leaseStart && checkDate <= leaseEnd) {
          try {
            // Vérifier s'il y a un paiement pour ce bail et ce mois
            const paymentsResponse = await api.get(`/api/paiements-loyers/bail/${lease.id_bail}`)
            const payments = paymentsResponse.data.data || []
            
            const hasPayment = payments.some(p => p.annee === lastMonthYear && p.mois === lastMonthMonth)
            
            if (!hasPayment) {
              unpaid.push({
                lease,
                year: lastMonthYear,
                month: lastMonthMonth,
                amount: lease.prix_loyer || 0,
                tenant: lease.locataire,
                unit: lease.locataire?.unite
              })
            }
          } catch (error) {
            console.error(`Erreur lors de la vérification des paiements pour le bail ${lease.id_bail}:`, error)
          }
        }
      }
      
      setUnpaidRents(unpaid)
    } catch (error) {
      console.error('Erreur lors du chargement des loyers non payés:', error)
      setUnpaidRents([])
    }
  }

  const loadPendingInvoices = async () => {
    try {
      const response = await invoicesSTService.getInvoices()
      const invoices = response.data || []
      
      // Filtrer les factures sans date_de_paiement (à payer)
      const pending = invoices.filter(invoice => !invoice.date_de_paiement)
      
      setPendingInvoices(pending)
    } catch (error) {
      console.error('Erreur lors du chargement des factures à payer:', error)
      setPendingInvoices([])
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD',
      minimumFractionDigits: 2
    }).format(amount || 0)
  }

  const formatMonthYear = (year, month) => {
    const date = new Date(year, month - 1, 1)
    return date.toLocaleDateString('fr-CA', { month: 'long', year: 'numeric' })
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
          <p className="text-gray-600 dark:text-gray-400 mt-1">Vue d'ensemble de vos opérations</p>
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

      {/* Deux colonnes : Loyers non payés et Factures à payer */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Loyers non payés - Colonne gauche */}
        <div className="card dark:bg-gray-800 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <DollarSign className="h-5 w-5 text-red-500 dark:text-red-400 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Loyers non payés</h2>
            </div>
            <span className="px-2 py-1 bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300 rounded-full text-xs font-medium">
              {unpaidRents.length}
            </span>
          </div>
          
          {unpaidRents.length === 0 ? (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-500 dark:text-green-400 mx-auto mb-2" />
              <p className="text-gray-500 dark:text-gray-400">Tous les loyers du mois dernier sont payés</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {unpaidRents.map((item, index) => (
                <div key={index} className="p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <Users className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {item.tenant?.nom} {item.tenant?.prenom}
                        </p>
                      </div>
                      {item.unit && (
                        <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                          {item.unit.adresse_unite}
                        </p>
                      )}
                      <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                        <Calendar className="h-3 w-3" />
                        <span>{formatMonthYear(item.year, item.month)}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-red-600 dark:text-red-400">
                        {formatCurrency(item.amount)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Factures à payer - Colonne droite */}
        <div className="card dark:bg-gray-800 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <FileText className="h-5 w-5 text-yellow-500 dark:text-yellow-400 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Factures à payer</h2>
            </div>
            <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300 rounded-full text-xs font-medium">
              {pendingInvoices.length}
            </span>
          </div>
          
          {pendingInvoices.length === 0 ? (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-500 dark:text-green-400 mx-auto mb-2" />
              <p className="text-gray-500 dark:text-gray-400">Aucune facture en attente</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {pendingInvoices.map((invoice) => (
                <div key={invoice.id_facture} className="p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                        {invoice.reference || `Facture #${invoice.id_facture}`}
                      </p>
                      {invoice.section && (
                        <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                          Section: {invoice.section}
                        </p>
                      )}
                      {invoice.date_creation && (
                        <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                          <Calendar className="h-3 w-3" />
                          <span>Créée le {new Date(invoice.date_creation).toLocaleDateString('fr-CA')}</span>
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-yellow-600 dark:text-yellow-400">
                        {formatCurrency(invoice.montant)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
