import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { BarChart3, DollarSign, TrendingUp, Users, Package, Truck, Clock, ArrowLeft, AlertCircle, CheckCircle, Download } from 'lucide-react'
import { projectsService } from '../services/api'
import projectReportExport from '../services/projectReportExport'

export default function ProjectAnalysis() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [analysis, setAnalysis] = useState(null)
  const [project, setProject] = useState(null)
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [error, setError] = useState('')
  const [selectedProjectId, setSelectedProjectId] = useState(projectId || null)

  useEffect(() => {
    if (projectId) {
      setSelectedProjectId(projectId)
      fetchAnalysis(projectId)
      fetchProject(projectId)
    } else {
      fetchProjects()
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    if (selectedProjectId && selectedProjectId !== projectId) {
      navigate(`/project-analysis/${selectedProjectId}`, { replace: true })
    }
  }, [selectedProjectId, navigate, projectId])

  const fetchProjects = async () => {
    try {
      const response = await projectsService.getProjects()
      setProjects(response.data || [])
    } catch (err) {
      console.error('Erreur lors du chargement des projets:', err)
    }
  }

  const fetchAnalysis = async (id) => {
    try {
      setLoading(true)
      setError('')
      const response = await projectsService.getProjectExpenseAnalysis(id)
      setAnalysis(response.data)
    } catch (err) {
      console.error('Erreur lors du chargement de l\'analyse:', err)
      setError('Erreur lors du chargement de l\'analyse des dépenses')
    } finally {
      setLoading(false)
    }
  }

  const fetchProject = async (id) => {
    try {
      const response = await projectsService.getProject(id)
      setProject(response.data.data)
    } catch (err) {
      console.error('Erreur lors du chargement du projet:', err)
    }
  }

  const handleProjectSelect = (id) => {
    setSelectedProjectId(id)
    fetchAnalysis(id)
    fetchProject(id)
  }

  const formatCurrency = (amount) => {
    if (!amount || amount === 0) return '$0.00'
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount)
  }

  const formatHours = (hours) => {
    if (!hours || hours === 0) return '0 h'
    return `${hours.toFixed(1)} h`
  }

  const getBudgetStatus = () => {
    if (!analysis || !project || !project.budget_total) return null
    
    const total = analysis.totaux.total
    const budget = project.budget_total || 0
    const percentage = budget > 0 ? (total / budget) * 100 : 0
    const remaining = budget - total
    
    return {
      total,
      budget,
      percentage: Math.round(percentage * 10) / 10,
      remaining,
      isOverBudget: total > budget
    }
  }

  const getMaxValue = () => {
    if (!analysis || !analysis.depenses_par_section.length) return 0
    return Math.max(...analysis.depenses_par_section.map(d => d.total))
  }

  const handleExportReport = async () => {
    if (!analysis || !project) {
      alert('Veuillez d\'abord charger l\'analyse du projet')
      return
    }

    try {
      setExporting(true)
      await projectReportExport.exportReport(analysis, project)
      alert('Rapport exporté avec succès !')
    } catch (error) {
      console.error('Erreur lors de l\'export:', error)
      alert('Erreur lors de l\'export du rapport. Veuillez réessayer.')
    } finally {
      setExporting(false)
    }
  }

  if (!selectedProjectId) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analyse de projet</h1>
            <p className="text-gray-600 mt-1">Sélectionnez un projet pour voir son analyse</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun projet</h3>
              <p className="text-gray-500">Créez un projet pour commencer l'analyse.</p>
            </div>
          ) : (
            projects.map((proj) => (
              <div
                key={proj.id_projet}
                onClick={() => handleProjectSelect(proj.id_projet)}
                className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all cursor-pointer"
              >
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{proj.nom}</h3>
                {proj.budget_total && (
                  <p className="text-sm text-gray-600">
                    Budget: {formatCurrency(proj.budget_total)}
                  </p>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error || 'Aucune donnée disponible'}
        </div>
      </div>
    )
  }

  const budgetStatus = getBudgetStatus()
  const maxValue = getMaxValue()

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/projects')}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            title="Retour aux projets"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analyse de projet</h1>
            {project && (
              <p className="text-gray-600 mt-1">{project.nom}</p>
            )}
          </div>
        </div>
        <button
          onClick={handleExportReport}
          disabled={exporting || !analysis || !project}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          <Download className="h-5 w-5" />
          <span>{exporting ? 'Export en cours...' : 'Exporter le rapport'}</span>
        </button>
      </div>

      {/* Comparaison avec le budget */}
      {budgetStatus && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <DollarSign className="h-5 w-5 mr-2" />
            Comparaison avec le budget
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 mb-1">Budget total</p>
              <p className="text-2xl font-bold text-blue-600">
                {formatCurrency(budgetStatus.budget)}
              </p>
            </div>
            
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 mb-1">Dépenses totales</p>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(budgetStatus.total)}
              </p>
            </div>
            
            <div className={`border rounded-lg p-4 ${budgetStatus.isOverBudget ? 'bg-red-50 border-red-200' : 'bg-gray-50 border-gray-200'}`}>
              <p className="text-sm font-medium text-gray-700 mb-1">
                {budgetStatus.isOverBudget ? 'Dépassement' : 'Reste disponible'}
              </p>
              <p className={`text-2xl font-bold ${budgetStatus.isOverBudget ? 'text-red-600' : 'text-gray-900'}`}>
                {formatCurrency(Math.abs(budgetStatus.remaining))}
              </p>
            </div>
            
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 mb-1">Pourcentage utilisé</p>
              <p className="text-2xl font-bold text-purple-600">
                {budgetStatus.percentage}%
              </p>
            </div>
          </div>

          {/* Barre de progression */}
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Progression du budget</span>
              <span className="text-sm text-gray-600">
                {budgetStatus.percentage}% utilisé
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  budgetStatus.percentage > 100
                    ? 'bg-red-600'
                    : budgetStatus.percentage > 80
                    ? 'bg-yellow-500'
                    : 'bg-green-600'
                }`}
                style={{ width: `${Math.min(budgetStatus.percentage, 100)}%` }}
              />
            </div>
            {budgetStatus.percentage > 100 && (
              <div className="mt-2 flex items-center text-red-600 text-sm">
                <AlertCircle className="h-4 w-4 mr-1" />
                Budget dépassé de {formatCurrency(budgetStatus.total - budgetStatus.budget)}
              </div>
            )}
          </div>
        </div>
      )}

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

      {/* Graphique en barres verticales par catégorie */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
          <BarChart3 className="h-5 w-5 mr-2" />
          Coûts par catégorie
        </h2>
        
        {analysis.depenses_par_section.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Aucune dépense enregistrée pour ce projet
          </div>
        ) : (
          <div className="space-y-4">
            {/* Graphique avec axe Y */}
            <div className="flex items-end space-x-3" style={{ minHeight: '300px', paddingLeft: '60px' }}>
              {/* Axe Y (graduations) */}
              <div className="absolute left-0 flex flex-col justify-between h-full pb-8" style={{ width: '50px' }}>
                {[100, 75, 50, 25, 0].map((percent) => {
                  const value = (maxValue * percent) / 100
                  return (
                    <div key={percent} className="text-xs text-gray-500 text-right">
                      {formatCurrency(value)}
                    </div>
                  )
                })}
              </div>
              
              {/* Barres */}
              <div className="flex-1 flex items-end justify-between space-x-2">
                {analysis.depenses_par_section.map((item, index) => {
                  const barHeight = maxValue > 0 ? (item.total / maxValue) * 100 : 0
                  return (
                    <div key={index} className="flex-1 flex flex-col items-center space-y-2 max-w-[120px]">
                      {/* Barre verticale */}
                      <div className="w-full relative flex flex-col justify-end" style={{ height: '250px' }}>
                        <div
                          className="w-full bg-blue-600 rounded-t transition-all duration-500 hover:bg-blue-700 relative group"
                          style={{ height: `${barHeight}%`, minHeight: barHeight > 0 ? '10px' : '0' }}
                          title={`${item.section}: ${formatCurrency(item.total)}`}
                        >
                          {/* Valeur sur la barre */}
                          {barHeight > 8 && (
                            <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs font-medium text-gray-700 whitespace-nowrap">
                              {formatCurrency(item.total)}
                            </div>
                          )}
                        </div>
                      </div>
                      {/* Label catégorie */}
                      <div className="text-xs text-gray-700 text-center font-medium w-full px-1">
                        <div className="line-clamp-2" title={item.section}>
                          {item.section}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tableau détaillé avec heures */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="h-5 w-5 mr-2" />
          Détails par catégorie
        </h2>
        
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
                    <Clock className="h-4 w-4 inline mr-1" />
                    Heures
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
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                      {formatHours(item.heures_travaillees)}
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
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-bold text-gray-600">
                    {formatHours(analysis.depenses_par_section.reduce((sum, d) => sum + (d.heures_travaillees || 0), 0))}
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
  )
}

