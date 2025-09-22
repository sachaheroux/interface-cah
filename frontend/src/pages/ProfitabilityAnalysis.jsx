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
  RefreshCw
} from 'lucide-react'

export default function ProfitabilityAnalysis() {
  const [buildings, setBuildings] = useState([])
  const [selectedBuildings, setSelectedBuildings] = useState([])
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [loading, setLoading] = useState(false)
  const [analysisData, setAnalysisData] = useState(null)
  const [showFilters, setShowFilters] = useState(false)

  // Charger les immeubles au montage
  useEffect(() => {
    loadBuildings()
  }, [])

  const loadBuildings = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/buildings`)
      if (response.ok) {
        const data = await response.json()
        setBuildings(data.data || [])
      }
    } catch (error) {
      console.error('Erreur lors du chargement des immeubles:', error)
    }
  }

  const handleBuildingToggle = (buildingId) => {
    setSelectedBuildings(prev => 
      prev.includes(buildingId) 
        ? prev.filter(id => id !== buildingId)
        : [...prev, buildingId]
    )
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
            <label className="block text-sm font-medium text-gray-700 mb-3">
              <Building className="h-4 w-4 inline mr-2" />
              Immeubles à analyser
            </label>
            <div className="space-y-2 max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-3">
              {buildings.map((building) => (
                <label key={building.id_immeuble} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedBuildings.includes(building.id_immeuble)}
                    onChange={() => handleBuildingToggle(building.id_immeuble)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">
                    {building.nom_immeuble} - {building.adresse}
                  </span>
                </label>
              ))}
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

          {/* Graphiques d'analyse */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Bar chart - Comparaison des immeubles */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Comparaison des immeubles</h3>
              <div className="space-y-3">
                {analysisData.buildings.map((building, index) => (
                  <div key={building.id} className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700">{building.name}</span>
                        <span className="text-sm text-gray-500">${building.summary.netCashflow.toLocaleString()}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                          style={{ 
                            width: `${(building.summary.netCashflow / Math.max(...analysisData.buildings.map(b => b.summary.netCashflow))) * 100}%` 
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Pie chart - Répartition des dépenses */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Répartition des dépenses</h3>
              <div className="space-y-2">
                {Object.entries(analysisData.categories).map(([category, amount], index) => {
                  const total = Object.values(analysisData.categories).reduce((sum, val) => sum + val, 0)
                  const percentage = ((amount / total) * 100).toFixed(1)
                  const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-blue-500', 'bg-purple-500']
                  
                  return (
                    <div key={category} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full ${colors[index % colors.length]}`}></div>
                        <span className="text-sm text-gray-700 capitalize">{category}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">{percentage}%</span>
                        <span className="text-sm font-medium text-gray-900">${amount.toLocaleString()}</span>
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
            <div className="space-y-4">
              {analysisData.monthlyTotals.map((month, index) => (
                <div key={month.month} className="flex items-center space-x-4">
                  <div className="w-20 text-sm text-gray-600">
                    {new Date(month.month + '-01').toLocaleDateString('fr-CA', { month: 'short', year: 'numeric' })}
                  </div>
                  <div className="flex-1 flex items-center space-x-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-4 relative">
                      <div 
                        className="bg-green-500 h-4 rounded-l-full"
                        style={{ width: `${(month.revenue / Math.max(...analysisData.monthlyTotals.map(m => m.revenue))) * 100}%` }}
                      ></div>
                      <div 
                        className="bg-red-500 h-4 rounded-r-full absolute top-0"
                        style={{ 
                          width: `${(month.expenses / Math.max(...analysisData.monthlyTotals.map(m => m.revenue))) * 100}%`,
                          left: `${(month.revenue / Math.max(...analysisData.monthlyTotals.map(m => m.revenue))) * 100}%`
                        }}
                      ></div>
                    </div>
                    <div className="w-32 text-right text-sm">
                      <div className="text-green-600">+${month.revenue.toLocaleString()}</div>
                      <div className="text-red-600">-${month.expenses.toLocaleString()}</div>
                      <div className={`font-medium ${month.netCashflow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ${month.netCashflow.toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
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
