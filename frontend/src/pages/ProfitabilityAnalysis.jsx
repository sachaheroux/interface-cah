import React, { useState, useEffect } from 'react'
import { 
  BarChart3, 
  TrendingUp, 
  Calendar, 
  Building, 
  DollarSign, 
  PieChart, 
  Download,
  Filter,
  RefreshCw,
  Search
} from 'lucide-react'

export default function ProfitabilityAnalysis() {
  const [buildings, setBuildings] = useState([])
  const [selectedBuildings, setSelectedBuildings] = useState([])
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [loading, setLoading] = useState(false)
  const [analysisData, setAnalysisData] = useState(null)
  const [showFilters, setShowFilters] = useState(false)
  const [buildingSearchTerm, setBuildingSearchTerm] = useState('')
  const [filteredBuildings, setFilteredBuildings] = useState([])

  // Charger les immeubles au montage
  useEffect(() => {
    loadBuildings()
  }, [])

  // Filtrer les immeubles selon la recherche
  useEffect(() => {
    if (buildingSearchTerm.trim() === '') {
      setFilteredBuildings(buildings)
    } else {
      const filtered = buildings.filter(building =>
        building.nom_immeuble.toLowerCase().includes(buildingSearchTerm.toLowerCase()) ||
        building.adresse.toLowerCase().includes(buildingSearchTerm.toLowerCase())
      )
      setFilteredBuildings(filtered)
    }
  }, [buildings, buildingSearchTerm])

  const loadBuildings = async () => {
    try {
      console.log('🔄 Chargement des immeubles...')
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/buildings`)
      console.log('📊 Réponse immeubles:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('📋 Données immeubles:', data)
        
        // L'API retourne directement un tableau, pas un objet avec data
        const buildingsList = Array.isArray(data) ? data : (data.data || [])
        setBuildings(buildingsList)
        console.log('✅ Immeubles chargés:', buildingsList.length)
      } else {
        console.error('❌ Erreur API immeubles:', response.status)
      }
    } catch (error) {
      console.error('❌ Erreur lors du chargement des immeubles:', error)
    }
  }

  const handleBuildingToggle = (buildingId) => {
    setSelectedBuildings(prev => 
      prev.includes(buildingId) 
        ? prev.filter(id => id !== buildingId)
        : [...prev, buildingId]
    )
  }

  const handleSelectAllBuildings = () => {
    if (selectedBuildings.length === filteredBuildings.length) {
      // Désélectionner tous les immeubles filtrés
      setSelectedBuildings(prev => prev.filter(id => !filteredBuildings.some(b => b.id_immeuble === id)))
    } else {
      // Sélectionner tous les immeubles filtrés
      const newSelected = [...new Set([...selectedBuildings, ...filteredBuildings.map(b => b.id_immeuble)])]
      setSelectedBuildings(newSelected)
    }
  }

  const runAnalysis = async () => {
    if (selectedBuildings.length === 0 || !startDate || !endDate) {
      alert('Veuillez sélectionner au moins un immeuble et une période')
      return
    }

    setLoading(true)
    try {
      console.log('Analyse pour:', selectedBuildings, startDate, endDate)
      
      // Données bidon pour tester l'interface
      setTimeout(() => {
        const mockData = generateMockAnalysisData(selectedBuildings, startDate, endDate)
        setAnalysisData(mockData)
        setLoading(false)
      }, 2000)
      
    } catch (error) {
      console.error('Erreur lors de l\'analyse:', error)
      setLoading(false)
    }
  }

  const generateMockAnalysisData = (buildingIds, startDate, endDate) => {
    const selectedBuildingsData = buildings.filter(b => buildingIds.includes(b.id_immeuble))
    
    // Générer des données mensuelles pour la période
    const start = new Date(startDate)
    const end = new Date(endDate)
    const months = []
    
    for (let d = new Date(start); d <= end; d.setMonth(d.getMonth() + 1)) {
      months.push(new Date(d).toISOString().slice(0, 7)) // Format YYYY-MM
    }
    
    // Données par immeuble et par mois
    const buildingData = selectedBuildingsData.map(building => {
      const monthlyData = months.map(month => {
        const baseRevenue = Math.floor(Math.random() * 5000) + 2000 // 2000-7000
        const baseExpenses = Math.floor(Math.random() * 2000) + 500  // 500-2500
        
        return {
          month,
          revenue: baseRevenue,
          expenses: baseExpenses,
          netCashflow: baseRevenue - baseExpenses,
          categories: {
            loyers: baseRevenue,
            taxes: Math.floor(baseExpenses * 0.3),
            entretien: Math.floor(baseExpenses * 0.25),
            reparation: Math.floor(baseExpenses * 0.2),
            assurance: Math.floor(baseExpenses * 0.15),
            autre: Math.floor(baseExpenses * 0.1)
          }
        }
      })
      
      const totalRevenue = monthlyData.reduce((sum, month) => sum + month.revenue, 0)
      const totalExpenses = monthlyData.reduce((sum, month) => sum + month.expenses, 0)
      
      return {
        id: building.id_immeuble,
        name: building.nom_immeuble,
        address: building.adresse,
        monthlyData,
        summary: {
          totalRevenue,
          totalExpenses,
          netCashflow: totalRevenue - totalExpenses,
          roi: ((totalRevenue - totalExpenses) / totalRevenue * 100).toFixed(1)
        }
      }
    })
    
    // Calculer les totaux globaux
    const totalRevenue = buildingData.reduce((sum, building) => sum + building.summary.totalRevenue, 0)
    const totalExpenses = buildingData.reduce((sum, building) => sum + building.summary.totalExpenses, 0)
    const netCashflow = totalRevenue - totalExpenses
    
    // Données pour les pie charts (toutes catégories confondues)
    const allCategories = buildingData.reduce((acc, building) => {
      building.monthlyData.forEach(month => {
        Object.keys(month.categories).forEach(category => {
          if (category !== 'loyers') { // Exclure les loyers des dépenses
            acc[category] = (acc[category] || 0) + month.categories[category]
          }
        })
      })
      return acc
    }, {})
    
    return {
      period: { start: startDate, end: endDate },
      buildings: buildingData,
      summary: {
        totalRevenue,
        totalExpenses,
        netCashflow,
        roi: (netCashflow / totalRevenue * 100).toFixed(1)
      },
      categories: allCategories,
      monthlyTotals: months.map(month => {
        const monthData = buildingData.reduce((acc, building) => {
          const monthInfo = building.monthlyData.find(m => m.month === month)
          if (monthInfo) {
            acc.revenue += monthInfo.revenue
            acc.expenses += monthInfo.expenses
            acc.netCashflow += monthInfo.netCashflow
          }
          return acc
        }, { revenue: 0, expenses: 0, netCashflow: 0 })
        
        return {
          month,
          ...monthData
        }
      })
    }
  }

  const exportReport = () => {
    // TODO: Générer et télécharger le rapport PDF
    console.log('Export du rapport PDF')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BarChart3 className="h-8 w-8 text-primary-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analyse de Rentabilité</h1>
            <p className="text-gray-600">
              Analysez la performance financière de vos immeubles
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary flex items-center space-x-2"
          >
            <Filter className="h-4 w-4" />
            <span>Filtres</span>
          </button>
          <button
            onClick={exportReport}
            className="btn-primary flex items-center space-x-2"
            disabled={!analysisData}
          >
            <Download className="h-4 w-4" />
            <span>Exporter PDF</span>
          </button>
        </div>
      </div>

      {/* Configuration */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuration de l'analyse</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Sélection des immeubles */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-700">
                <Building className="h-4 w-4 inline mr-2" />
                Immeubles à analyser ({selectedBuildings.length} sélectionnés)
              </label>
              <button
                onClick={loadBuildings}
                className="text-xs text-gray-500 hover:text-gray-700 flex items-center space-x-1"
              >
                <RefreshCw className="h-3 w-3" />
                <span>Recharger</span>
              </button>
            </div>
            
            {/* Barre de recherche */}
            <div className="mb-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Rechercher un immeuble..."
                  value={buildingSearchTerm}
                  onChange={(e) => setBuildingSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
                />
              </div>
            </div>

            {/* Bouton tout sélectionner */}
            <div className="mb-3">
              <button
                onClick={handleSelectAllBuildings}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                {selectedBuildings.length === filteredBuildings.length && filteredBuildings.length > 0
                  ? 'Tout désélectionner'
                  : 'Tout sélectionner'
                } ({filteredBuildings.length} immeubles)
              </button>
            </div>

            <div className="space-y-1 max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-3">
              {filteredBuildings.length === 0 ? (
                <div className="text-center py-4">
                  <div className="text-sm text-gray-500">
                    {buildings.length === 0 ? 'Chargement des immeubles...' : 'Aucun immeuble trouvé'}
                  </div>
                </div>
              ) : (
                filteredBuildings.map((building) => (
                  <label key={building.id_immeuble} className="flex items-center space-x-2 hover:bg-gray-50 p-2 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedBuildings.includes(building.id_immeuble)}
                      onChange={() => handleBuildingToggle(building.id_immeuble)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {building.nom_immeuble}
                      </div>
                      <div className="text-xs text-gray-500 truncate">
                        {building.adresse}
                      </div>
                    </div>
                  </label>
                ))
              )}
            </div>
          </div>

          {/* Période */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              <Calendar className="h-4 w-4 inline mr-2" />
              Période d'analyse
            </label>
            <div className="space-y-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Date de début</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Date de fin</label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Bouton d'analyse */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={runAnalysis}
            disabled={loading || selectedBuildings.length === 0 || !startDate || !endDate}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Analyse en cours...</span>
              </>
            ) : (
              <>
                <TrendingUp className="h-4 w-4" />
                <span>Lancer l'analyse</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Résultats de l'analyse */}
      {analysisData && (
        <div className="space-y-6">
          {/* Métriques clés */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Revenus totaux</p>
                  <p className="text-2xl font-bold text-green-600">
                    ${analysisData.summary.totalRevenue.toLocaleString()}
                  </p>
                </div>
                <DollarSign className="h-8 w-8 text-green-600" />
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Dépenses totales</p>
                  <p className="text-2xl font-bold text-red-600">
                    ${analysisData.summary.totalExpenses.toLocaleString()}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-red-600" />
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Cashflow net</p>
                  <p className="text-2xl font-bold text-blue-600">
                    ${analysisData.summary.netCashflow.toLocaleString()}
                  </p>
                </div>
                <BarChart3 className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">ROI</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {analysisData.summary.roi}%
                  </p>
                </div>
                <PieChart className="h-8 w-8 text-purple-600" />
              </div>
            </div>
          </div>

          {/* Graphiques d'analyse - 3 bar charts verticaux */}
          <div className="space-y-8">
            {/* 1. Bar chart - Cashflow net par immeuble */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Cashflow net par immeuble</h3>
              <div className="h-80 flex items-end justify-center space-x-4">
                {analysisData.buildings.map((building, index) => {
                  const maxAbsValue = Math.max(...analysisData.buildings.map(b => Math.abs(b.summary.netCashflow)))
                  const isPositive = building.summary.netCashflow >= 0
                  const barHeight = (Math.abs(building.summary.netCashflow) / maxAbsValue) * 280 // Hauteur max 280px
                  const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
                  
                  return (
                    <div key={building.id} className="flex flex-col items-center space-y-2" style={{ width: `${100 / analysisData.buildings.length}%` }}>
                      <div className="text-xs text-gray-600 text-center font-medium">
                        {building.name}
                      </div>
                      <div className="flex flex-col items-center">
                        <div 
                          className={`w-full rounded-t-lg transition-all duration-700 ${
                            isPositive ? 'bg-gradient-to-t from-green-500 to-green-400' : 'bg-gradient-to-b from-red-500 to-red-400'
                          }`}
                          style={{ 
                            height: `${barHeight}px`,
                            backgroundColor: colors[index % colors.length]
                          }}
                        ></div>
                        <div className="text-xs text-gray-500 mt-1">
                          {isPositive ? '+' : ''}${building.summary.netCashflow.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* 2. Bar chart - Revenus par catégorie et immeuble (stacked) */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Revenus par catégorie et immeuble</h3>
              
              {/* Légende pour les revenus */}
              <div className="flex justify-center mb-4 space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded" style={{ backgroundColor: '#3b82f6' }}></div>
                  <span className="text-xs text-gray-600">Loyers</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded" style={{ backgroundColor: '#10b981' }}></div>
                  <span className="text-xs text-gray-600">Autres</span>
                </div>
              </div>
              
              <div className="h-80 flex items-end justify-center space-x-2">
                {analysisData.buildings.map((building, index) => {
                  const maxRevenue = Math.max(...analysisData.buildings.map(b => b.summary.totalRevenue))
                  const totalHeight = (building.summary.totalRevenue / maxRevenue) * 280
                  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#ef4444']
                  
                  // Simuler des catégories de revenus (loyers, autres revenus, etc.)
                  const revenueCategories = [
                    { name: 'Loyers', amount: building.summary.totalRevenue * 0.8 },
                    { name: 'Autres', amount: building.summary.totalRevenue * 0.2 }
                  ]
                  
                  return (
                    <div key={building.id} className="flex flex-col items-center space-y-2" style={{ width: `${100 / analysisData.buildings.length}%` }}>
                      <div className="text-xs text-gray-600 text-center font-medium">
                        {building.name}
                      </div>
                      <div className="flex flex-col items-center w-full">
                        <div className="w-full rounded-t-lg overflow-hidden" style={{ height: `${totalHeight}px` }}>
                          {revenueCategories.map((category, catIndex) => {
                            const categoryHeight = (category.amount / building.summary.totalRevenue) * totalHeight
                            return (
                              <div
                                key={catIndex}
                                className="w-full transition-all duration-700 hover:opacity-80"
                                style={{ 
                                  height: `${categoryHeight}px`,
                                  backgroundColor: colors[catIndex % colors.length]
                                }}
                                title={`${category.name}: $${category.amount.toLocaleString()}`}
                              ></div>
                            )
                          })}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          ${building.summary.totalRevenue.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* 3. Bar chart - Dépenses par catégorie et immeuble (stacked) */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Dépenses par catégorie et immeuble</h3>
              
              {/* Légende pour les dépenses */}
              <div className="flex justify-center mb-4 space-x-3 flex-wrap">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded" style={{ backgroundColor: '#ef4444' }}></div>
                  <span className="text-xs text-gray-600">Taxes</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded" style={{ backgroundColor: '#f97316' }}></div>
                  <span className="text-xs text-gray-600">Entretien</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded" style={{ backgroundColor: '#eab308' }}></div>
                  <span className="text-xs text-gray-600">Réparation</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded" style={{ backgroundColor: '#22c55e' }}></div>
                  <span className="text-xs text-gray-600">Assurance</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded" style={{ backgroundColor: '#3b82f6' }}></div>
                  <span className="text-xs text-gray-600">Autres</span>
                </div>
              </div>
              
              <div className="h-80 flex items-end justify-center space-x-2">
                {analysisData.buildings.map((building, index) => {
                  const maxExpenses = Math.max(...analysisData.buildings.map(b => b.summary.totalExpenses))
                  const totalHeight = (building.summary.totalExpenses / maxExpenses) * 280
                  const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4']
                  
                  // Simuler des catégories de dépenses basées sur les données réelles
                  const expenseCategories = [
                    { name: 'Taxes', amount: building.summary.totalExpenses * 0.3 },
                    { name: 'Entretien', amount: building.summary.totalExpenses * 0.25 },
                    { name: 'Réparation', amount: building.summary.totalExpenses * 0.2 },
                    { name: 'Assurance', amount: building.summary.totalExpenses * 0.15 },
                    { name: 'Autres', amount: building.summary.totalExpenses * 0.1 }
                  ]
                  
                  return (
                    <div key={building.id} className="flex flex-col items-center space-y-2" style={{ width: `${100 / analysisData.buildings.length}%` }}>
                      <div className="text-xs text-gray-600 text-center font-medium">
                        {building.name}
                      </div>
                      <div className="flex flex-col items-center w-full">
                        <div className="w-full rounded-t-lg overflow-hidden" style={{ height: `${totalHeight}px` }}>
                          {expenseCategories.map((category, catIndex) => {
                            const categoryHeight = (category.amount / building.summary.totalExpenses) * totalHeight
                            return (
                              <div
                                key={catIndex}
                                className="w-full transition-all duration-700 hover:opacity-80"
                                style={{ 
                                  height: `${categoryHeight}px`,
                                  backgroundColor: colors[catIndex % colors.length]
                                }}
                                title={`${category.name}: $${category.amount.toLocaleString()}`}
                              ></div>
                            )
                          })}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          ${building.summary.totalExpenses.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Graphique de cashflow mensuel */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Cashflow mensuel</h3>
            <div className="space-y-6">
              {analysisData.monthlyTotals.map((month, index) => {
                const maxRevenue = Math.max(...analysisData.monthlyTotals.map(m => m.revenue))
                const maxExpenses = Math.max(...analysisData.monthlyTotals.map(m => m.expenses))
                const maxTotal = Math.max(maxRevenue, maxExpenses)
                
                const revenueWidth = (month.revenue / maxTotal) * 100
                const expensesWidth = (month.expenses / maxTotal) * 100
                
                return (
                  <div key={month.month} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="w-24 text-sm font-medium text-gray-700">
                        {new Date(month.month + '-01').toLocaleDateString('fr-CA', { month: 'short', year: 'numeric' })}
                      </div>
                      <div className="flex items-center space-x-6 text-sm">
                        <div className="text-green-600 font-medium">+${month.revenue.toLocaleString()}</div>
                        <div className="text-red-600 font-medium">-${month.expenses.toLocaleString()}</div>
                        <div className={`font-bold ${month.netCashflow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          ${month.netCashflow.toLocaleString()}
                        </div>
                      </div>
                    </div>
                    
                    {/* Barre de revenus */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>Revenus</span>
                        <span>{revenueWidth.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                        <div 
                          className="bg-green-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${revenueWidth}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    {/* Barre de dépenses */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>Dépenses</span>
                        <span>{expensesWidth.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                        <div 
                          className="bg-red-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${expensesWidth}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Tableau détaillé */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Détail par immeuble</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Immeuble</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenus</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dépenses</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cashflow net</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ROI</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {analysisData.buildings.map((building) => (
                    <tr key={building.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{building.name}</div>
                          <div className="text-sm text-gray-500">{building.address}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                        ${building.summary.totalRevenue.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-medium">
                        ${building.summary.totalExpenses.toLocaleString()}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                        building.summary.netCashflow >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        ${building.summary.netCashflow.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {building.summary.roi}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
