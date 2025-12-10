import React, { useState, useEffect } from 'react'
import { X, DollarSign, TrendingUp, Users, Package, Truck, BarChart3 } from 'lucide-react'
import { projectsService } from '../services/api'

export default function ProjectExpenseAnalysis({ isOpen, onClose, projectId }) {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen && projectId) {
      fetchAnalysis()
    }
  }, [isOpen, projectId])

  const fetchAnalysis = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await projectsService.getProjectExpenseAnalysis(projectId)
      setAnalysis(response.data)
    } catch (err) {
      console.error('Erreur lors du chargement de l\'analyse:', err)
      setError('Erreur lors du chargement de l\'analyse des dépenses')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    if (!amount || amount === 0) return '$0.00'
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Analyse des dépenses</h2>
            {analysis?.projet && (
              <p className="text-gray-600 mt-1">Projet: {analysis.projet.nom}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Contenu */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          ) : analysis ? (
            <div className="space-y-6">
              {/* Totaux généraux */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <Truck className="h-5 w-5 text-blue-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">Sous-traitants</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-600">
                    {formatCurrency(analysis.totaux.sous_traitants)}
                  </p>
                </div>
                
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <Package className="h-5 w-5 text-green-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">Commandes</span>
                  </div>
                  <p className="text-2xl font-bold text-green-600">
                    {formatCurrency(analysis.totaux.commandes)}
                  </p>
                </div>
                
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <Users className="h-5 w-5 text-purple-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">Employés</span>
                  </div>
                  <p className="text-2xl font-bold text-purple-600">
                    {formatCurrency(analysis.totaux.employes)}
                  </p>
                </div>
                
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <DollarSign className="h-5 w-5 text-gray-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">Total</span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(analysis.totaux.total)}
                  </p>
                </div>
              </div>

              {/* Dépenses par section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2" />
                  Dépenses par catégorie
                </h3>
                
                {analysis.depenses_par_section.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    Aucune dépense enregistrée pour ce projet
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Catégorie
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Sous-traitants
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Commandes
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Employés
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Total
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {analysis.depenses_par_section.map((item, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="text-sm font-medium text-gray-900">
                                {item.section}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                              {formatCurrency(item.sous_traitants)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                              {formatCurrency(item.commandes)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                              {formatCurrency(item.employes)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right">
                              <span className="text-sm font-semibold text-gray-900">
                                {formatCurrency(item.total)}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot className="bg-gray-50">
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                            TOTAL
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-bold text-blue-600">
                            {formatCurrency(analysis.totaux.sous_traitants)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-bold text-green-600">
                            {formatCurrency(analysis.totaux.commandes)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-bold text-purple-600">
                            {formatCurrency(analysis.totaux.employes)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-bold text-gray-900">
                            {formatCurrency(analysis.totaux.total)}
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  )
}

