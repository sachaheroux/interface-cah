import React, { useState, useEffect } from 'react'
import { Users, Calendar, DollarSign, Edit3, Trash2, Eye, X, Plus } from 'lucide-react'
import { buildingsService, reportsService } from '../services/api'
import { parseAddressAndGenerateUnits } from '../types/unit'
import DeleteConfirmationModal from './DeleteConfirmationModal'

export default function UnitReports({ selectedYear }) {
  const [buildings, setBuildings] = useState([])
  const [units, setUnits] = useState([])
  const [reports, setReports] = useState([])
  const [selectedUnit, setSelectedUnit] = useState(null)
  const [editingReport, setEditingReport] = useState(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [reportToDelete, setReportToDelete] = useState(null)
  const [loading, setLoading] = useState(true)

  const months = [
    { value: 1, name: 'Janvier' },
    { value: 2, name: 'Février' },
    { value: 3, name: 'Mars' },
    { value: 4, name: 'Avril' },
    { value: 5, name: 'Mai' },
    { value: 6, name: 'Juin' },
    { value: 7, name: 'Juillet' },
    { value: 8, name: 'Août' },
    { value: 9, name: 'Septembre' },
    { value: 10, name: 'Octobre' },
    { value: 11, name: 'Novembre' },
    { value: 12, name: 'Décembre' }
  ]

  const paymentMethods = [
    'Comptant',
    'Chèque',
    'Virement bancaire',
    'Carte de crédit',
    'Prélèvement automatique',
    'Autre'
  ]

  useEffect(() => {
    loadBuildings()
    loadReports()
  }, [])

  const loadBuildings = async () => {
    try {
      const response = await buildingsService.getBuildings()
      const buildingsData = response.data || []
      setBuildings(buildingsData)
      
      // Générer toutes les unités
      const allUnits = []
      buildingsData.forEach(building => {
        try {
          const buildingUnits = parseAddressAndGenerateUnits(building)
          allUnits.push(...buildingUnits)
        } catch (error) {
          console.error('Error parsing building units:', error)
        }
      })
      setUnits(allUnits)
    } catch (error) {
      console.error('Error loading buildings:', error)
    }
  }

  const loadReports = async () => {
    try {
      setLoading(true)
      const response = await reportsService.getUnitReports()
      setReports(response.data || [])
    } catch (error) {
      console.error('Error loading unit reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const getReportsForUnit = (unitId, year) => {
    return reports.filter(r => r.unitId === unitId && r.year === year)
  }

  const handleAddReport = (unit) => {
    setEditingReport({
      unitId: unit.id,
      unitName: `${unit.buildingName} - ${unit.unitNumber}`,
      year: selectedYear,
      month: 1,
      tenantName: '',
      paymentMethod: '',
      isHeatedLit: false,
      isFurnished: false,
      rentAmount: 0,
      startDate: '',
      endDate: '',
      id: null
    })
    setSelectedUnit(unit)
  }

  const handleEditReport = (unit, report) => {
    setEditingReport({
      unitId: unit.id,
      unitName: `${unit.buildingName} - ${unit.unitNumber}`,
      year: report.year,
      month: report.month,
      tenantName: report.tenantName || '',
      paymentMethod: report.paymentMethod || '',
      isHeatedLit: report.isHeatedLit || false,
      isFurnished: report.isFurnished || false,
      rentAmount: report.rentAmount || 0,
      startDate: report.startDate || '',
      endDate: report.endDate || '',
      id: report.id
    })
    setSelectedUnit(unit)
  }

  const handleSaveReport = async () => {
    try {
      const reportData = { ...editingReport }
      await reportsService.createUnitReport(reportData)
      await loadReports()
      setEditingReport(null)
      setSelectedUnit(null)
    } catch (error) {
      console.error('Error saving unit report:', error)
      alert('Erreur lors de la sauvegarde du rapport')
    }
  }

  const handleDeleteReport = async () => {
    try {
      await reportsService.deleteUnitReport(reportToDelete.id)
      await loadReports()
      setShowDeleteModal(false)
      setReportToDelete(null)
    } catch (error) {
      console.error('Error deleting unit report:', error)
      alert('Erreur lors de la suppression du rapport')
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount || 0)
  }

  const getMonthName = (monthNumber) => {
    const month = months.find(m => m.value === monthNumber)
    return month ? month.name : monthNumber
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Chargement des rapports d'unités...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Liste des unités */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Rapports d'Unités - {selectedYear}
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Historique détaillé des locataires et revenus par unité et par mois
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Unité
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rapports {selectedYear}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Revenus totaux
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {units.map((unit) => {
                const unitReports = getReportsForUnit(unit.id, selectedYear)
                const totalRevenue = unitReports.reduce((sum, report) => sum + (report.rentAmount || 0), 0)
                
                return (
                  <tr key={unit.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Users className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {unit.buildingName} - {unit.unitNumber}
                          </div>
                          <div className="text-sm text-gray-500">
                            {unit.address}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {unitReports.length} mois documenté{unitReports.length > 1 ? 's' : ''}
                      </div>
                      {unitReports.length > 0 && (
                        <div className="text-xs text-gray-500">
                          {unitReports.map(r => getMonthName(r.month)).join(', ')}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(totalRevenue)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleAddReport(unit)}
                          className="text-blue-600 hover:text-blue-900 flex items-center"
                        >
                          <Plus className="h-4 w-4 mr-1" />
                          Ajouter
                        </button>
                        {unitReports.length > 0 && (
                          <button
                            onClick={() => setSelectedUnit(unit)}
                            className="text-green-600 hover:text-green-900 flex items-center"
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            Voir
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

      {/* Détails des rapports d'une unité */}
      {selectedUnit && !editingReport && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                {selectedUnit.buildingName} - {selectedUnit.unitNumber}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Historique des rapports mensuels pour {selectedYear}
              </p>
            </div>
            <button
              onClick={() => setSelectedUnit(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Mois
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Locataire
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Paiement
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Conditions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Loyer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {months.map((month) => {
                  const report = getReportsForUnit(selectedUnit.id, selectedYear)
                    .find(r => r.month === month.value)
                  
                  return (
                    <tr key={month.value} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {month.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {report?.tenantName || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {report?.paymentMethod || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex space-x-2">
                          {report?.isHeatedLit && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                              Chauffé-éclairé
                            </span>
                          )}
                          {report?.isFurnished && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              Meublé
                            </span>
                          )}
                          {!report?.isHeatedLit && !report?.isFurnished && report && (
                            <span className="text-gray-500">Standard</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {report ? formatCurrency(report.rentAmount) : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          {report ? (
                            <>
                              <button
                                onClick={() => handleEditReport(selectedUnit, report)}
                                className="text-blue-600 hover:text-blue-900 flex items-center"
                              >
                                <Edit3 className="h-4 w-4 mr-1" />
                                Modifier
                              </button>
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
                            </>
                          ) : (
                            <button
                              onClick={() => {
                                setEditingReport({
                                  unitId: selectedUnit.id,
                                  unitName: `${selectedUnit.buildingName} - ${selectedUnit.unitNumber}`,
                                  year: selectedYear,
                                  month: month.value,
                                  tenantName: '',
                                  paymentMethod: '',
                                  isHeatedLit: false,
                                  isFurnished: false,
                                  rentAmount: 0,
                                  startDate: '',
                                  endDate: '',
                                  id: null
                                })
                              }}
                              className="text-green-600 hover:text-green-900 flex items-center"
                            >
                              <Plus className="h-4 w-4 mr-1" />
                              Ajouter
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
      )}

      {/* Formulaire d'édition */}
      {editingReport && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Rapport {editingReport.unitName} - {getMonthName(editingReport.month)} {editingReport.year}
              </h3>
              <button
                onClick={() => {
                  setEditingReport(null)
                  if (!selectedUnit) setSelectedUnit(null)
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Mois</label>
                  <select
                    value={editingReport.month}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, month: parseInt(e.target.value) }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    {months.map(month => (
                      <option key={month.value} value={month.value}>
                        {month.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Nom du locataire</label>
                  <input
                    type="text"
                    value={editingReport.tenantName}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, tenantName: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Nom complet du locataire"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Méthode de paiement</label>
                  <select
                    value={editingReport.paymentMethod}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, paymentMethod: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Sélectionnez...</option>
                    {paymentMethods.map(method => (
                      <option key={method} value={method}>
                        {method}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Montant du loyer</label>
                  <input
                    type="number"
                    step="0.01"
                    value={editingReport.rentAmount}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, rentAmount: parseFloat(e.target.value) || 0 }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Date de début</label>
                  <input
                    type="date"
                    value={editingReport.startDate}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, startDate: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Date de fin</label>
                  <input
                    type="date"
                    value={editingReport.endDate}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, endDate: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Conditions spéciales */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Conditions spéciales</label>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="heatedLit"
                      checked={editingReport.isHeatedLit}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, isHeatedLit: e.target.checked }))}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="heatedLit" className="ml-2 block text-sm text-gray-900">
                      Chauffé-éclairé
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="furnished"
                      checked={editingReport.isFurnished}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, isFurnished: e.target.checked }))}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="furnished" className="ml-2 block text-sm text-gray-900">
                      Meublé
                    </label>
                  </div>
                </div>
              </div>

              {/* Boutons d'action */}
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    setEditingReport(null)
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
        message={`Êtes-vous sûr de vouloir supprimer le rapport de ${getMonthName(reportToDelete?.month)} ${reportToDelete?.year} ? Cette action est irréversible.`}
      />
    </div>
  )
} 