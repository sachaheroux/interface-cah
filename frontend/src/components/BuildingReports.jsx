import React, { useState, useEffect } from 'react'
import { Building2, DollarSign, FileText, Edit3, AlertTriangle, CheckCircle, X, Search, Upload, Eye } from 'lucide-react'
import { buildingsService, reportsService } from '../services/api'

export default function BuildingReports({ selectedYear }) {
  const [buildings, setBuildings] = useState([])
  const [reports, setReports] = useState([])
  const [selectedBuilding, setSelectedBuilding] = useState(null)
  const [editingReport, setEditingReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showDetails, setShowDetails] = useState(false)
  const [selectedBuildingDetails, setSelectedBuildingDetails] = useState(null)

  useEffect(() => {
    loadBuildings()
    loadReports()
  }, [])

  const loadBuildings = async () => {
    try {
      const response = await buildingsService.getBuildings()
      setBuildings(response.data || [])
    } catch (error) {
      console.error('Error loading buildings:', error)
    }
  }

  const loadReports = async () => {
    try {
      setLoading(true)
      const response = await reportsService.getBuildingReports()
      setReports(response.data || [])
    } catch (error) {
      console.error('Error loading reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const getReportForBuilding = (buildingId, year) => {
    return reports.find(r => r.buildingId === buildingId && r.year === year)
  }

  const handleEditReport = (building) => {
    console.log('Building data:', building)
    console.log('Financial info:', building.financials)
    console.log('Purchase price:', building.financials?.purchasePrice)
    console.log('Down payment:', building.financials?.downPayment)
    
    const existingReport = getReportForBuilding(building.id, selectedYear)
    console.log('Existing report:', existingReport)
    
    const purchaseCost = building.financials?.purchasePrice || 0
    const downPayment = building.financials?.downPayment || 0
    
    setEditingReport({
      buildingId: building.id,
      buildingName: building.name || formatAddress(building.address),
      year: selectedYear,
      // Données fixes (de la fiche immeuble) - toujours prendre depuis building
      purchaseCost: purchaseCost,
      downPayment: downPayment,
      // Données variables par année
      interestRate: existingReport?.interestRate || 0,
      currentValue: existingReport?.currentValue || 0,
      municipalTaxes: existingReport?.municipalTaxes || 0,
      schoolTaxes: existingReport?.schoolTaxes || 0,
      insurance: existingReport?.insurance || 0,
      snowRemoval: existingReport?.snowRemoval || 0,
      lawn: existingReport?.lawn || 0,
      management: existingReport?.management || 0,
      renovation: existingReport?.renovation || 0,
      other: existingReport?.other || 0,
      id: existingReport?.id || null
    })
    setSelectedBuilding(building)
  }

  const handleSaveReport = async () => {
    try {
      // S'assurer que toutes les données sont incluses, y compris les données fixes
      const reportData = {
        buildingId: editingReport.buildingId,
        year: editingReport.year,
        // Données fixes - s'assurer qu'elles sont sauvegardées
        purchaseCost: editingReport.purchaseCost,
        downPayment: editingReport.downPayment,
        // Données variables par année
        interestRate: editingReport.interestRate,
        currentValue: editingReport.currentValue,
        municipalTaxes: editingReport.municipalTaxes,
        schoolTaxes: editingReport.schoolTaxes,
        insurance: editingReport.insurance,
        snowRemoval: editingReport.snowRemoval,
        lawn: editingReport.lawn,
        management: editingReport.management,
        renovation: editingReport.renovation,
        other: editingReport.other,
        // Inclure l'ID si c'est une modification
        ...(editingReport.id && { id: editingReport.id })
      }
      
      console.log('Sauvegarde rapport avec données:', reportData)
      await reportsService.createBuildingReport(reportData)
      await loadReports()
      setEditingReport(null)
      setSelectedBuilding(null)
    } catch (error) {
      console.error('Error saving report:', error)
      alert('Erreur lors de la sauvegarde du rapport')
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount || 0)
  }

  const formatAddress = (address) => {
    if (typeof address === 'string') {
      return address
    }
    if (address && typeof address === 'object') {
      return `${address.street || ''}, ${address.city || ''}`.replace(/^,\s*/, '').replace(/,\s*$/, '')
    }
    return ''
  }

  // Filtrer les immeubles selon le terme de recherche
  const filteredBuildings = buildings.filter(building => {
    const searchLower = searchTerm.toLowerCase()
    const name = building.name || ''
    const address = formatAddress(building.address)
    return name.toLowerCase().includes(searchLower) || 
           address.toLowerCase().includes(searchLower)
  })

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Chargement des rapports...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Liste des immeubles */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                Rapports d'Immeubles - {selectedYear}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Gérez les données financières et opérationnelles par immeuble
              </p>
            </div>
            
            {/* Champ de recherche */}
            <div className="flex items-center space-x-2">
              <div className="relative">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Rechercher un immeuble..."
                  className="pl-8 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <Search className="h-4 w-4 text-gray-400 absolute left-2.5 top-2.5" />
              </div>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Immeuble
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rapport Excel
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Détails & Factures
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredBuildings.map((building) => {
                const report = getReportForBuilding(building.id, selectedYear)
                return (
                  <tr key={building.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Building2 className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {building.name || formatAddress(building.address)}
                          </div>
                          <div className="text-sm text-gray-500">
                            {formatAddress(building.address)}
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            Coût: {formatCurrency(building.financials?.purchasePrice || 0)} | Mise de fond: {formatCurrency(building.financials?.downPayment || 0)}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEditReport(building)}
                          className="text-blue-600 hover:text-blue-900 flex items-center"
                        >
                          <Edit3 className="h-4 w-4 mr-1" />
                          {report ? 'Modifier' : 'Créer'}
                        </button>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-center">
                        <button className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                          <Upload className="h-4 w-4 mr-2" />
                          Importer Excel
                        </button>
                        <p className="text-xs text-gray-500 mt-1">Disponible prochainement</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        {report ? (
                          <div className="flex items-center space-x-2">
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            <span className="text-sm text-green-700">Données complètes</span>
                            <button
                              onClick={() => {
                                setSelectedBuildingDetails(building)
                                setShowDetails(true)
                              }}
                              className="text-blue-600 hover:text-blue-900 flex items-center"
                            >
                              <Eye className="h-4 w-4 mr-1" />
                              Voir détails
                            </button>
                          </div>
                        ) : (
                          <div className="flex items-center">
                            <AlertTriangle className="h-4 w-4 text-yellow-500 mr-2" />
                            <span className="text-sm text-yellow-700">En attente</span>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Message si aucun résultat */}
        {filteredBuildings.length === 0 && searchTerm && (
          <div className="text-center py-8">
            <p className="text-gray-500">Aucun immeuble trouvé pour "{searchTerm}"</p>
          </div>
        )}
      </div>

      {/* Modal des détails et factures */}
      {showDetails && selectedBuildingDetails && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-4/5 lg:w-3/4 shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Détails & Factures - {selectedBuildingDetails.name || formatAddress(selectedBuildingDetails.address)} ({selectedYear})
              </h3>
              <button
                onClick={() => {
                  setShowDetails(false)
                  setSelectedBuildingDetails(null)
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Données fixes */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-medium text-gray-900 mb-3">Données Fixes</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white p-3 rounded border">
                    <label className="block text-sm font-medium text-gray-700">Coût d'achat</label>
                    <p className="text-lg font-semibold text-gray-900">
                      {(() => {
                        const report = getReportForBuilding(selectedBuildingDetails.id, selectedYear)
                        return formatCurrency(report?.purchaseCost || selectedBuildingDetails.financials?.purchasePrice || 0)
                      })()}
                    </p>
                  </div>
                  <div className="bg-white p-3 rounded border">
                    <label className="block text-sm font-medium text-gray-700">Mise de fond</label>
                    <p className="text-lg font-semibold text-gray-900">
                      {(() => {
                        const report = getReportForBuilding(selectedBuildingDetails.id, selectedYear)
                        return formatCurrency(report?.downPayment || selectedBuildingDetails.financials?.downPayment || 0)
                      })()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Données variables pour l'année */}
              {(() => {
                const report = getReportForBuilding(selectedBuildingDetails.id, selectedYear)
                if (!report) {
                  return (
                    <div className="text-center py-8">
                      <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                      <p className="text-gray-500">Aucun rapport créé pour {selectedYear}</p>
                      <button
                        onClick={() => {
                          setShowDetails(false)
                          setSelectedBuildingDetails(null)
                          handleEditReport(selectedBuildingDetails)
                        }}
                        className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                      >
                        Créer le rapport
                      </button>
                    </div>
                  )
                }

                const dataItems = [
                  { label: 'Pourcentage d\'intérêt', value: `${report.interestRate || 0}%`, type: 'rate' },
                  { label: 'Valeur actuelle', value: formatCurrency(report.currentValue), type: 'currency' },
                  { label: 'Taxes municipales', value: formatCurrency(report.municipalTaxes), type: 'invoice' },
                  { label: 'Taxes scolaires', value: formatCurrency(report.schoolTaxes), type: 'invoice' },
                  { label: 'Assurance', value: formatCurrency(report.insurance), type: 'invoice' },
                  { label: 'Déneigement', value: formatCurrency(report.snowRemoval), type: 'invoice' },
                  { label: 'Gazon', value: formatCurrency(report.lawn), type: 'invoice' },
                  { label: 'Gestion', value: formatCurrency(report.management), type: 'invoice' },
                  { label: 'Rénovation', value: formatCurrency(report.renovation), type: 'invoice' },
                  { label: 'Autres', value: formatCurrency(report.other), type: 'invoice' }
                ]

                return (
                  <div>
                    <h4 className="text-md font-medium text-gray-900 mb-3">Données Variables - {selectedYear}</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {dataItems.map((item, index) => (
                        <div key={index} className="bg-white border rounded-lg p-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <label className="block text-sm font-medium text-gray-700">{item.label}</label>
                              <p className="text-lg font-semibold text-gray-900 mt-1">{item.value}</p>
                            </div>
                            {item.type === 'invoice' && (
                              <div className="ml-2">
                                <button className="text-gray-400 hover:text-blue-600 p-1">
                                  <FileText className="h-4 w-4" />
                                </button>
                                <p className="text-xs text-gray-500 mt-1">PDF</p>
                              </div>
                            )}
                          </div>
                          {item.type === 'invoice' && (
                            <p className="text-xs text-gray-500 mt-2">
                              Facture disponible prochainement
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })()}

              {/* Actions */}
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    setShowDetails(false)
                    setSelectedBuildingDetails(null)
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Fermer
                </button>
                <button
                  onClick={() => {
                    setShowDetails(false)
                    setSelectedBuildingDetails(null)
                    handleEditReport(selectedBuildingDetails)
                  }}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  Modifier le rapport
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Formulaire d'édition */}
      {editingReport && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Rapport {editingReport.buildingName} - {editingReport.year}
              </h3>
              <button
                onClick={() => {
                  setEditingReport(null)
                  setSelectedBuilding(null)
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Données fixes */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3">Données Fixes</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Coût d'achat</label>
                    <input
                      type="number"
                      value={editingReport.purchaseCost}
                      disabled
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm bg-gray-100 text-gray-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Modifiable depuis la fiche immeuble</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Mise de fond</label>
                    <input
                      type="number"
                      value={editingReport.downPayment}
                      disabled
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm bg-gray-100 text-gray-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Modifiable depuis la fiche immeuble</p>
                  </div>
                </div>
              </div>

              {/* Données variables par année */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3">Données Variables - {editingReport.year}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Pourcentage d'intérêt (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={editingReport.interestRate}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, interestRate: parseFloat(e.target.value) || 0 }))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Valeur actuelle de l'immeuble</label>
                    <input
                      type="number"
                      value={editingReport.currentValue}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, currentValue: parseFloat(e.target.value) || 0 }))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Taxes municipales</label>
                    <input
                      type="number"
                      value={editingReport.municipalTaxes}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, municipalTaxes: parseFloat(e.target.value) || 0 }))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Sera automatiquement rempli depuis la section factures</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Taxes scolaires</label>
                    <input
                      type="number"
                      value={editingReport.schoolTaxes}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, schoolTaxes: parseFloat(e.target.value) || 0 }))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Sera automatiquement rempli depuis la section factures</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Assurance</label>
                    <input
                      type="number"
                      value={editingReport.insurance}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, insurance: parseFloat(e.target.value) || 0 }))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Sera automatiquement rempli depuis la section factures</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Déneigement</label>
                    <input
                      type="number"
                      value={editingReport.snowRemoval}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, snowRemoval: parseFloat(e.target.value) || 0 }))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Sera automatiquement rempli depuis la section factures</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Gazon</label>
                    <input
                      type="number"
                      value={editingReport.lawn}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, lawn: parseFloat(e.target.value) || 0 }))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Sera automatiquement rempli depuis la section factures</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Gestion</label>
                    <input
                      type="number"
                      value={editingReport.management}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, management: parseFloat(e.target.value) || 0 }))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Sera automatiquement rempli depuis la section factures</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Rénovation</label>
                    <input
                      type="number"
                      value={editingReport.renovation}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, renovation: parseFloat(e.target.value) || 0 }))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Sera automatiquement rempli depuis la section factures</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Autres</label>
                    <input
                      type="number"
                      value={editingReport.other}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, other: parseFloat(e.target.value) || 0 }))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Sera automatiquement rempli depuis la section factures</p>
                  </div>
                </div>
              </div>

              {/* Boutons d'action */}
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    setEditingReport(null)
                    setSelectedBuilding(null)
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  onClick={handleSaveReport}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  Sauvegarder
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 