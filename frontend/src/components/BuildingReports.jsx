import React, { useState, useEffect } from 'react'
import { Building2, DollarSign, FileText, Edit3, Trash2, AlertTriangle, CheckCircle, X } from 'lucide-react'
import { buildingsService, reportsService } from '../services/api'
import DeleteConfirmationModal from './DeleteConfirmationModal'

export default function BuildingReports({ selectedYear }) {
  const [buildings, setBuildings] = useState([])
  const [reports, setReports] = useState([])
  const [selectedBuilding, setSelectedBuilding] = useState(null)
  const [editingReport, setEditingReport] = useState(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [reportToDelete, setReportToDelete] = useState(null)
  const [loading, setLoading] = useState(true)

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
    const existingReport = getReportForBuilding(building.id, selectedYear)
    setEditingReport({
      buildingId: building.id,
      buildingName: building.name || building.address,
      year: selectedYear,
      // Données fixes (de la fiche immeuble)
      purchaseCost: building.purchaseCost || 0,
      downPayment: building.downPayment || 0,
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
      const reportData = { ...editingReport }
      await reportsService.createBuildingReport(reportData)
      await loadReports()
      setEditingReport(null)
      setSelectedBuilding(null)
    } catch (error) {
      console.error('Error saving report:', error)
      alert('Erreur lors de la sauvegarde du rapport')
    }
  }

  const handleDeleteReport = async () => {
    try {
      await reportsService.deleteBuildingReport(reportToDelete.id)
      await loadReports()
      setShowDeleteModal(false)
      setReportToDelete(null)
    } catch (error) {
      console.error('Error deleting report:', error)
      alert('Erreur lors de la suppression du rapport')
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount || 0)
  }

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
          <h3 className="text-lg font-medium text-gray-900">
            Rapports d'Immeubles - {selectedYear}
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Gérez les données financières et opérationnelles par immeuble
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Immeuble
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Coût d'achat
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mise de fond
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rapport {selectedYear}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {buildings.map((building) => {
                const report = getReportForBuilding(building.id, selectedYear)
                return (
                  <tr key={building.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Building2 className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {building.name || building.address}
                          </div>
                          <div className="text-sm text-gray-500">
                            {building.address}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(building.purchaseCost)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(building.downPayment)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {report ? (
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                          <span className="text-sm text-green-700">Complété</span>
                        </div>
                      ) : (
                        <div className="flex items-center">
                          <AlertTriangle className="h-4 w-4 text-yellow-500 mr-2" />
                          <span className="text-sm text-yellow-700">En attente</span>
                        </div>
                      )}
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
                        {report && (
                          <button
                            onClick={() => {
                              setReportToDelete(report)
                              setShowDeleteModal(true)
                            }}
                            className="text-red-600 hover:text-red-900 flex items-center"
                          >
                            <Trash2 className="h-4 w-4 mr-1" />
                            Supprimer
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

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

      {/* Modal de confirmation de suppression */}
      <DeleteConfirmationModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false)
          setReportToDelete(null)
        }}
        onConfirm={handleDeleteReport}
        title="Supprimer le rapport"
        message={`Êtes-vous sûr de vouloir supprimer le rapport de ${reportToDelete?.year} ? Cette action est irréversible.`}
      />
    </div>
  )
} 