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
// Fonction pour formater les dates en français
const formatDate = (date) => {
  const months = [
    'janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin',
    'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'
  ]
  return `${months[date.getMonth()]} ${date.getFullYear()}`
}

export default function ProfitabilityAnalysis() {
  const [buildings, setBuildings] = useState([])
  const [selectedBuildings, setSelectedBuildings] = useState([])
  const [startYear, setStartYear] = useState('2025')
  const [startMonth, setStartMonth] = useState('07')
  const [endYear, setEndYear] = useState('2026')
  const [endMonth, setEndMonth] = useState('06')
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
    if (selectedBuildings.length === 0 || !startYear || !startMonth || !endYear || !endMonth) {
      alert('Veuillez sélectionner au moins un immeuble et une période')
      return
    }

    setLoading(true)
    try {
      console.log('Analyse pour:', selectedBuildings, `${startMonth}/${startYear} à ${endMonth}/${endYear}`)
      
      // Données bidon pour tester l'interface
      setTimeout(() => {
        const mockData = generateMockAnalysisData(selectedBuildings, startYear, startMonth, endYear, endMonth)
        setAnalysisData(mockData)
        setLoading(false)
      }, 2000)
      
    } catch (error) {
      console.error('Erreur lors de l\'analyse:', error)
      setLoading(false)
    }
  }

  const generateMockAnalysisData = (buildingIds, startYear, startMonth, endYear, endMonth) => {
    const selectedBuildingsData = buildings.filter(b => buildingIds.includes(b.id_immeuble))
    
    // Générer les mois de la période sélectionnée
    const months = []
    let currentYear = parseInt(startYear)
    let currentMonth = parseInt(startMonth)
    const endYearInt = parseInt(endYear)
    const endMonthInt = parseInt(endMonth)

    // Ajouter tous les mois de la période, y compris le mois de fin
    while (currentYear < endYearInt || (currentYear === endYearInt && currentMonth <= endMonthInt)) {
      const date = new Date(currentYear, currentMonth - 1, 1)
      months.push(formatDate(date))
      
      // Passer au mois suivant
      currentMonth++
      if (currentMonth > 12) {
        currentMonth = 1
        currentYear++
      }
    }
    
    // Debug: vérifier la logique
    console.log('🔍 Debug génération mois:')
    console.log('  - Début:', startYear, startMonth)
    console.log('  - Fin:', endYear, endMonth)
    console.log('  - Mois générés:', months.length)
    console.log('  - Liste:', months)
    
    // Debug: afficher les mois générés
    console.log('📅 Période sélectionnée:', `${startMonth}/${startYear} à ${endMonth}/${endYear}`)
    console.log('📅 Nombre de mois:', months.length)
    console.log('📅 Mois générés:', months)
    
    // Exemples de périodes personnalisées :
    // Janvier 2025 à Mars 2025 = 3 mois
    // Juillet 2025 à Juin 2026 = 12 mois  
    // Octobre 2024 à Février 2025 = 5 mois
    
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
      period: { start: `${startMonth}/${startYear}`, end: `${endMonth}/${endYear}` },
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
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Mois de début</label>
                <select
                  value={startMonth}
                  onChange={(e) => setStartMonth(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="01">Janvier</option>
                  <option value="02">Février</option>
                  <option value="03">Mars</option>
                  <option value="04">Avril</option>
                  <option value="05">Mai</option>
                  <option value="06">Juin</option>
                  <option value="07">Juillet</option>
                  <option value="08">Août</option>
                  <option value="09">Septembre</option>
                  <option value="10">Octobre</option>
                  <option value="11">Novembre</option>
                  <option value="12">Décembre</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Année de début</label>
                <select
                  value={startYear}
                  onChange={(e) => setStartYear(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="2023">2023</option>
                  <option value="2024">2024</option>
                  <option value="2025">2025</option>
                  <option value="2026">2026</option>
                  <option value="2027">2027</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Mois de fin</label>
                <select
                  value={endMonth}
                  onChange={(e) => setEndMonth(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="01">Janvier</option>
                  <option value="02">Février</option>
                  <option value="03">Mars</option>
                  <option value="04">Avril</option>
                  <option value="05">Mai</option>
                  <option value="06">Juin</option>
                  <option value="07">Juillet</option>
                  <option value="08">Août</option>
                  <option value="09">Septembre</option>
                  <option value="10">Octobre</option>
                  <option value="11">Novembre</option>
                  <option value="12">Décembre</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Année de fin</label>
                <select
                  value={endYear}
                  onChange={(e) => setEndYear(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="2023">2023</option>
                  <option value="2024">2024</option>
                  <option value="2025">2025</option>
                  <option value="2026">2026</option>
                  <option value="2027">2027</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Bouton d'analyse */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={runAnalysis}
            disabled={loading || selectedBuildings.length === 0 || !startYear || !startMonth || !endYear || !endMonth}
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
              <div className="flex">
                {/* Axe Y avec montants */}
                <div className="flex flex-col justify-between h-80 pr-4 w-20">
                  {(() => {
                    const maxValue = Math.max(...analysisData.buildings.map(b => b.summary.netCashflow))
                    const minValue = Math.min(...analysisData.buildings.map(b => b.summary.netCashflow))
                    const range = Math.max(Math.abs(maxValue), Math.abs(minValue))
                    const stepSize = Math.ceil(range / 5 / 1000) * 1000 // Arrondir à la centaine supérieure
                    const steps = 5
                    
                    return Array.from({ length: steps + 1 }, (_, i) => {
                      const value = stepSize * (steps - i) // Inverser l'ordre pour que 0 soit en bas
                      return (
                        <div key={i} className="text-xs text-gray-600 text-right font-medium">
                          ${value.toLocaleString()}
                        </div>
                      )
                    })
                  })()}
                </div>
                
                {/* Graphique principal */}
                <div className="flex-1 relative border-l-2 border-b-2 border-gray-800">
                  {/* Lignes de grille */}
                  <div className="absolute inset-0 flex flex-col justify-between">
                    {(() => {
                      const maxValue = Math.max(...analysisData.buildings.map(b => b.summary.netCashflow))
                      const minValue = Math.min(...analysisData.buildings.map(b => b.summary.netCashflow))
                      const range = Math.max(Math.abs(maxValue), Math.abs(minValue))
                      const stepSize = Math.ceil(range / 5 / 1000) * 1000
                      const steps = 5
                      
                      return Array.from({ length: steps + 1 }, (_, i) => (
                        <div key={i} className="border-t border-gray-300"></div>
                      ))
                    })()}
                  </div>
                  
                  {/* Barres avec noms intégrés */}
                  <div className="h-80 flex items-end justify-center space-x-1 relative z-10 px-2">
                    {analysisData.buildings.map((building, index) => {
                      const maxValue = Math.max(...analysisData.buildings.map(b => b.summary.netCashflow))
                      const minValue = Math.min(...analysisData.buildings.map(b => b.summary.netCashflow))
                      const range = Math.max(Math.abs(maxValue), Math.abs(minValue))
                      const stepSize = Math.ceil(range / 5 / 1000) * 1000
                      const maxHeight = stepSize * 5
                      
                      const barHeight = (building.summary.netCashflow / maxHeight) * 320
                      const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
                      
                      return (
                        <div key={building.id} className="flex flex-col items-center" style={{ width: `${100 / analysisData.buildings.length}%` }}>
                          {/* Barre */}
                          <div className="flex flex-col items-end justify-end w-full h-80">
                            <div 
                              className="w-full transition-all duration-700"
                              style={{ 
                                height: `${Math.abs(barHeight)}px`,
                                backgroundColor: colors[index % colors.length]
                              }}
                            ></div>
                          </div>
                          {/* Nom sous la barre */}
                          <div 
                            className="text-xs text-gray-600 text-center font-medium mt-2"
                            style={{ 
                              width: '100%',
                              height: '60px', // Hauteur pour 2-3 lignes
                              display: 'flex',
                              alignItems: 'flex-start',
                              justifyContent: 'center',
                              lineHeight: '1.2'
                            }}
                            title={building.name}
                          >
                            <div style={{ wordWrap: 'break-word', maxWidth: '100%' }}>
                              {building.name}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  
                </div>
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
              
              <div className="flex">
                {/* Axe Y avec montants */}
                <div className="flex flex-col justify-between h-80 pr-4 w-20">
                  {(() => {
                    const maxRevenue = Math.max(...analysisData.buildings.map(b => b.summary.totalRevenue))
                    const stepSize = Math.ceil(maxRevenue / 5 / 1000) * 1000
                    const steps = 5
                    
                    return Array.from({ length: steps + 1 }, (_, i) => {
                      const value = stepSize * (steps - i) // Inverser l'ordre pour que 0 soit en bas
                      return (
                        <div key={i} className="text-xs text-gray-600 text-right font-medium">
                          ${value.toLocaleString()}
                        </div>
                      )
                    })
                  })()}
                </div>
                
                {/* Graphique principal */}
                <div className="flex-1 relative border-l-2 border-b-2 border-gray-800">
                  {/* Lignes de grille */}
                  <div className="absolute inset-0 flex flex-col justify-between">
                    {(() => {
                      const maxRevenue = Math.max(...analysisData.buildings.map(b => b.summary.totalRevenue))
                      const stepSize = Math.ceil(maxRevenue / 5 / 1000) * 1000
                      const steps = 5
                      
                      return Array.from({ length: steps + 1 }, (_, i) => (
                        <div key={i} className="border-t border-gray-300"></div>
                      ))
                    })()}
                  </div>
                  
                  {/* Barres avec noms intégrés */}
                  <div className="h-80 flex items-end justify-center space-x-1 relative z-10 px-2">
                    {analysisData.buildings.map((building, index) => {
                      const maxRevenue = Math.max(...analysisData.buildings.map(b => b.summary.totalRevenue))
                      const stepSize = Math.ceil(maxRevenue / 5 / 1000) * 1000
                      const maxHeight = stepSize * 5
                      const totalHeight = (building.summary.totalRevenue / maxHeight) * 320
                      const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#ef4444']
                      
                      // Simuler des catégories de revenus (loyers, autres revenus, etc.)
                      const revenueCategories = [
                        { name: 'Loyers', amount: building.summary.totalRevenue * 0.8 },
                        { name: 'Autres', amount: building.summary.totalRevenue * 0.2 }
                      ]
                      
                      return (
                        <div key={building.id} className="flex flex-col items-center" style={{ width: `${100 / analysisData.buildings.length}%` }}>
                          {/* Barre empilée */}
                          <div className="flex flex-col items-end justify-end w-full h-80">
                            <div className="w-full overflow-hidden" style={{ height: `${totalHeight}px` }}>
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
                          </div>
                          {/* Nom sous la barre */}
                          <div 
                            className="text-xs text-gray-600 text-center font-medium mt-2"
                            style={{ 
                              width: '100%',
                              height: '60px', // Hauteur pour 2-3 lignes
                              display: 'flex',
                              alignItems: 'flex-start',
                              justifyContent: 'center',
                              lineHeight: '1.2'
                            }}
                            title={building.name}
                          >
                            <div style={{ wordWrap: 'break-word', maxWidth: '100%' }}>
                              {building.name}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  
                </div>
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
              
              <div className="flex">
                {/* Axe Y avec montants */}
                <div className="flex flex-col justify-between h-80 pr-4 w-20">
                  {(() => {
                    const maxExpenses = Math.max(...analysisData.buildings.map(b => b.summary.totalExpenses))
                    const stepSize = Math.ceil(maxExpenses / 5 / 1000) * 1000
                    const steps = 5
                    
                    return Array.from({ length: steps + 1 }, (_, i) => {
                      const value = stepSize * (steps - i) // Inverser l'ordre pour que 0 soit en bas
                      return (
                        <div key={i} className="text-xs text-gray-600 text-right font-medium">
                          ${value.toLocaleString()}
                        </div>
                      )
                    })
                  })()}
                </div>
                
                {/* Graphique principal */}
                <div className="flex-1 relative border-l-2 border-b-2 border-gray-800">
                  {/* Lignes de grille */}
                  <div className="absolute inset-0 flex flex-col justify-between">
                    {(() => {
                      const maxExpenses = Math.max(...analysisData.buildings.map(b => b.summary.totalExpenses))
                      const stepSize = Math.ceil(maxExpenses / 5 / 1000) * 1000
                      const steps = 5
                      
                      return Array.from({ length: steps + 1 }, (_, i) => (
                        <div key={i} className="border-t border-gray-300"></div>
                      ))
                    })()}
                  </div>
                  
                  {/* Barres avec noms intégrés */}
                  <div className="h-80 flex items-end justify-center space-x-1 relative z-10 px-2">
                    {analysisData.buildings.map((building, index) => {
                      const maxExpenses = Math.max(...analysisData.buildings.map(b => b.summary.totalExpenses))
                      const stepSize = Math.ceil(maxExpenses / 5 / 1000) * 1000
                      const maxHeight = stepSize * 5
                      const totalHeight = (building.summary.totalExpenses / maxHeight) * 320
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
                        <div key={building.id} className="flex flex-col items-center" style={{ width: `${100 / analysisData.buildings.length}%` }}>
                          {/* Barre empilée */}
                          <div className="flex flex-col items-end justify-end w-full h-80">
                            <div className="w-full overflow-hidden" style={{ height: `${totalHeight}px` }}>
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
                          </div>
                          {/* Nom sous la barre */}
                          <div 
                            className="text-xs text-gray-600 text-center font-medium mt-2"
                            style={{ 
                              width: '100%',
                              height: '60px', // Hauteur pour 2-3 lignes
                              display: 'flex',
                              alignItems: 'flex-start',
                              justifyContent: 'center',
                              lineHeight: '1.2'
                            }}
                            title={building.name}
                          >
                            <div style={{ wordWrap: 'break-word', maxWidth: '100%' }}>
                              {building.name}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  
                </div>
              </div>
            </div>
          </div>

          {/* Pie chart - Répartition des dépenses globales */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Répartition des dépenses globales</h3>
            
            {/* Pie Chart SVG */}
            <div className="flex justify-center mb-6">
              <svg width="200" height="200" className="transform -rotate-90">
                {(() => {
                  const total = Object.values(analysisData.categories).reduce((sum, val) => sum + val, 0)
                  let currentAngle = 0
                  const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4']
                  
                  return Object.entries(analysisData.categories).map(([category, amount], index) => {
                    const percentage = (amount / total) * 100
                    const angle = (percentage / 100) * 360
                    const startAngle = currentAngle
                    const endAngle = currentAngle + angle
                    
                    const startAngleRad = (startAngle * Math.PI) / 180
                    const endAngleRad = (endAngle * Math.PI) / 180
                    
                    const x1 = 100 + 80 * Math.cos(startAngleRad)
                    const y1 = 100 + 80 * Math.sin(startAngleRad)
                    const x2 = 100 + 80 * Math.cos(endAngleRad)
                    const y2 = 100 + 80 * Math.sin(endAngleRad)
                    
                    const largeArcFlag = angle > 180 ? 1 : 0
                    
                    const pathData = [
                      `M 100 100`,
                      `L ${x1} ${y1}`,
                      `A 80 80 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                      'Z'
                    ].join(' ')
                    
                    currentAngle += angle
                    
                    return (
                      <path
                        key={category}
                        d={pathData}
                        fill={colors[index % colors.length]}
                        className="hover:opacity-80 transition-opacity duration-200"
                        style={{ cursor: 'pointer' }}
                      />
                    )
                  })
                })()}
              </svg>
            </div>
            
            {/* Légende détaillée */}
            <div className="space-y-3">
              {Object.entries(analysisData.categories).map(([category, amount], index) => {
                const total = Object.values(analysisData.categories).reduce((sum, val) => sum + val, 0)
                const percentage = ((amount / total) * 100).toFixed(1)
                const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4']
                
                return (
                  <div key={category} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: colors[index % colors.length] }}
                      ></div>
                      <div>
                        <span className="text-sm font-medium text-gray-900 capitalize">
                          {category.replace('_', ' ')}
                        </span>
                        <div className="text-xs text-gray-500">
                          {percentage}% du total
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-gray-900">
                        ${amount.toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-500">
                        {percentage}%
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
            
            {/* Résumé total */}
            <div className="mt-4 p-4 bg-primary-50 rounded-lg border border-primary-200">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-primary-900">Total des dépenses</span>
                <span className="text-lg font-bold text-primary-900">
                  ${Object.values(analysisData.categories).reduce((sum, val) => sum + val, 0).toLocaleString()}
                </span>
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
                        {month.month}
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
