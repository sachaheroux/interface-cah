import React, { useState, useEffect } from 'react'
import { Search, TrendingUp, TrendingDown, DollarSign, Home, Calculator } from 'lucide-react'
import api from '../services/api'

const MortgageAnalysis = () => {
  const [buildings, setBuildings] = useState([])
  const [selectedBuildings, setSelectedBuildings] = useState([])
  const [buildingSearchTerm, setBuildingSearchTerm] = useState('')
  const [filteredBuildings, setFilteredBuildings] = useState([])
  const [loading, setLoading] = useState(false)
  const [showAnalysis, setShowAnalysis] = useState(false)
  const [analysisData, setAnalysisData] = useState(null)

  // Charger les immeubles
  const loadBuildings = async () => {
    try {
      setLoading(true)
      console.log('🔄 Chargement des immeubles...')
      const response = await api.get('/api/buildings')
      console.log('📊 Réponse immeubles:', response.status)
      const data = response.data
      console.log('📋 Données immeubles:', data)
      
      // Gérer la réponse qui peut être un array direct ou un objet avec une propriété data
      const buildingsList = Array.isArray(data) ? data : (data.data || [])
      console.log('✅ Immeubles chargés:', buildingsList.length)
      setBuildings(buildingsList)
    } catch (error) {
      console.error('Erreur lors du chargement des immeubles:', error)
    } finally {
      setLoading(false)
    }
  }

  // Filtrer les immeubles selon le terme de recherche
  useEffect(() => {
    if (buildingSearchTerm) {
      const filtered = buildings.filter(building =>
        building.nom_immeuble.toLowerCase().includes(buildingSearchTerm.toLowerCase()) ||
        building.adresse.toLowerCase().includes(buildingSearchTerm.toLowerCase())
      )
      setFilteredBuildings(filtered)
    } else {
      setFilteredBuildings(buildings)
    }
  }, [buildings, buildingSearchTerm])

  // Charger les immeubles au montage du composant
  useEffect(() => {
    loadBuildings()
  }, [])

  // Gérer la sélection/désélection d'un immeuble
  const handleBuildingToggle = (buildingId) => {
    setSelectedBuildings(prev => {
      if (prev.includes(buildingId)) {
        return prev.filter(id => id !== buildingId)
      } else {
        return [...prev, buildingId]
      }
    })
  }

  // Sélectionner/désélectionner tous les immeubles filtrés
  const handleSelectAllBuildings = () => {
    const filteredIds = filteredBuildings.map(b => b.id_immeuble)
    const allSelected = filteredIds.every(id => selectedBuildings.includes(id))
    
    if (allSelected) {
      // Désélectionner tous les immeubles filtrés
      setSelectedBuildings(prev => prev.filter(id => !filteredIds.includes(id)))
    } else {
      // Sélectionner tous les immeubles filtrés
      setSelectedBuildings(prev => {
        const newSelection = [...prev]
        filteredIds.forEach(id => {
          if (!newSelection.includes(id)) {
            newSelection.push(id)
          }
        })
        return newSelection
      })
    }
  }

  // Lancer l'analyse de dette hypothécaire
  const runAnalysis = async () => {
    if (selectedBuildings.length === 0) {
      alert('Veuillez sélectionner au moins un immeuble')
      return
    }

    try {
      setLoading(true)
      console.log('🔍 Analyse pour:', selectedBuildings)
      
      const buildingIdsParam = selectedBuildings.join(',')
      const response = await api.get(`/api/analysis/mortgage?building_ids=${buildingIdsParam}`)
      
      console.log('📊 Données d\'analyse:', response.data)
      setAnalysisData(response.data)
      setShowAnalysis(true)
    } catch (error) {
      console.error('Erreur lors de l\'analyse:', error)
      alert('Erreur lors de l\'analyse de dette hypothécaire')
    } finally {
      setLoading(false)
    }
  }

  // Formater les montants
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount)
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* En-tête */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Home className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">Analyse de Dette Hypothécaire</h1>
          </div>
          <p className="text-gray-600">Analysez la dette restante, le montant remboursé et la valeur de vos immeubles</p>
        </div>

        {/* Sélection des immeubles */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Calculator className="h-5 w-5 text-blue-600" />
            Sélection des Immeubles
          </h2>
          
          {/* Barre de recherche */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Rechercher un immeuble..."
              value={buildingSearchTerm}
              onChange={(e) => setBuildingSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Bouton sélectionner tout */}
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={handleSelectAllBuildings}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {filteredBuildings.every(b => selectedBuildings.includes(b.id_immeuble)) 
                ? 'Tout désélectionner' 
                : 'Tout sélectionner'
              }
            </button>
            <span className="text-sm text-gray-600">
              {selectedBuildings.length} immeuble(s) sélectionné(s)
            </span>
          </div>

          {/* Liste des immeubles */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-60 overflow-y-auto">
            {filteredBuildings.map(building => (
              <label key={building.id_immeuble} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedBuildings.includes(building.id_immeuble)}
                  onChange={() => handleBuildingToggle(building.id_immeuble)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {building.nom_immeuble}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {building.adresse}, {building.ville}
                  </p>
                </div>
              </label>
            ))}
          </div>

          {filteredBuildings.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              {buildings.length === 0 ? 'Aucun immeuble trouvé' : 'Aucun immeuble correspond à votre recherche'}
            </div>
          )}

          {/* Bouton d'analyse */}
          <div className="mt-6 flex justify-center">
            <button
              onClick={runAnalysis}
              disabled={selectedBuildings.length === 0 || loading}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Analyse en cours...
                </>
              ) : (
                <>
                  <TrendingUp className="h-4 w-4" />
                  Lancer l'analyse
                </>
              )}
            </button>
          </div>
        </div>

        {/* Résultats de l'analyse */}
        {showAnalysis && analysisData && (
          <div className="space-y-6">
            {/* Métriques clés */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <TrendingDown className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Dette Restante</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(analysisData.summary.total_dette_restante)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Montant Remboursé</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(analysisData.summary.total_montant_rembourse)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <DollarSign className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Gain de Valeur</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(analysisData.summary.total_gain_valeur)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Home className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Valeur Actuelle</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(analysisData.summary.total_valeur_actuel)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Graphique en barres empilées */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Répartition de la Dette par Immeuble</h3>
              
              <div className="space-y-4">
                {analysisData.buildings.map((building, index) => {
                  const maxValue = Math.max(...analysisData.buildings.map(b => b.valeur_actuel))
                  const barHeight = (building.valeur_actuel / maxValue) * 100
                  
                  // Calculer les proportions pour chaque segment
                  const detteRestanteHeight = (building.dette_restante / building.valeur_actuel) * barHeight
                  const montantRembourseHeight = (building.montant_rembourse / building.valeur_actuel) * barHeight
                  const gainValeurHeight = (building.gain_valeur / building.valeur_actuel) * barHeight

                  return (
                    <div key={building.id_immeuble} className="flex items-end space-x-4">
                      {/* Nom de l'immeuble */}
                      <div className="w-48 text-right">
                        <p className="text-sm font-medium text-gray-900 truncate" title={building.nom_immeuble}>
                          {building.nom_immeuble}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatCurrency(building.valeur_actuel)}
                        </p>
                      </div>

                      {/* Barre empilée */}
                      <div className="flex-1">
                        <div className="relative h-80 border-b-2 border-gray-800">
                          {/* Segment gain de valeur (bleu) - en haut */}
                          {building.gain_valeur > 0 && (
                            <div
                              className="absolute bottom-0 left-0 bg-blue-500 w-full"
                              style={{ height: `${gainValeurHeight}%` }}
                              title={`Gain de valeur: ${formatCurrency(building.gain_valeur)}`}
                            />
                          )}
                          
                          {/* Segment montant remboursé (vert) - au milieu */}
                          {building.montant_rembourse > 0 && (
                            <div
                              className="absolute bg-green-500 w-full"
                              style={{ 
                                height: `${montantRembourseHeight}%`,
                                bottom: `${gainValeurHeight}%`
                              }}
                              title={`Montant remboursé: ${formatCurrency(building.montant_rembourse)}`}
                            />
                          )}
                          
                          {/* Segment dette restante (rouge) - en bas */}
                          {building.dette_restante > 0 && (
                            <div
                              className="absolute bg-red-500 w-full"
                              style={{ 
                                height: `${detteRestanteHeight}%`,
                                bottom: `${gainValeurHeight + montantRembourseHeight}%`
                              }}
                              title={`Dette restante: ${formatCurrency(building.dette_restante)}`}
                            />
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* Légende */}
              <div className="mt-6 flex justify-center">
                <div className="flex space-x-6">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-red-500 rounded"></div>
                    <span className="text-sm text-gray-600">Dette restante</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-green-500 rounded"></div>
                    <span className="text-sm text-gray-600">Montant remboursé</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-blue-500 rounded"></div>
                    <span className="text-sm text-gray-600">Gain de valeur</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Tableau détaillé */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Détail par Immeuble</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Immeuble
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Prix Acheté
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Mise de Fond
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Dette Restante
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Montant Remboursé
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Gain de Valeur
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Valeur Actuelle
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {analysisData.buildings.map((building) => (
                      <tr key={building.id_immeuble}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {building.nom_immeuble}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatCurrency(building.prix_achete)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatCurrency(building.mise_de_fond)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-medium">
                          {formatCurrency(building.dette_restante)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                          {formatCurrency(building.montant_rembourse)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 font-medium">
                          {formatCurrency(building.gain_valeur)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                          {formatCurrency(building.valeur_actuel)}
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
    </div>
  )
}

export default MortgageAnalysis
