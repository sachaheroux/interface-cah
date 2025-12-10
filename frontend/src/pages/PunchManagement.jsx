import React, { useState, useEffect } from 'react'
import { Clock, Calendar, Plus, User, Building, Edit, Trash2, Filter, Download } from 'lucide-react'
import PunchFormDesktop from '../components/PunchFormDesktop'
import { employeesService, punchsService, projectsService } from '../services/api'
import api from '../services/api'

export default function PunchManagement() {
  const [punchs, setPunchs] = useState([])
  const [employees, setEmployees] = useState([])
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState(null)
  const [editingPunch, setEditingPunch] = useState(null)
  const [filters, setFilters] = useState({
    employee: '',
    project: '',
    dateFrom: '',
    dateTo: ''
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [punchsRes, employeesRes, projectsRes] = await Promise.all([
        punchsService.getPunchs(),
        employeesService.getEmployees(),
        projectsService.getProjects()
      ])
      
      setPunchs(punchsRes.data || [])
      setEmployees(employeesRes.data || [])
      setProjects(projectsRes.data || [])
    } catch (err) {
      console.error('Erreur lors du chargement des données:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePunch = () => {
    setSelectedEmployee(null)
    setEditingPunch(null)
    setShowForm(true)
  }

  const handleEditPunch = (punch) => {
    setEditingPunch(punch)
    setSelectedEmployee(null)
    setShowForm(true)
  }

  const handleDeletePunch = async (punch) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce pointage ?')) {
      return
    }

    try {
      await punchsService.deletePunch(punch.id_punch)
      fetchData()
    } catch (err) {
      console.error('Erreur lors de la suppression:', err)
    }
  }

  const handleFormSuccess = () => {
    setShowForm(false)
    setEditingPunch(null)
    fetchData()
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('fr-CA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatHours = (hours) => {
    const wholeHours = Math.floor(hours)
    const minutes = Math.round((hours - wholeHours) * 60)
    return `${wholeHours}h${minutes > 0 ? minutes.toString().padStart(2, '0') : ''}`
  }

  const getEmployeeName = (employeeId) => {
    const employee = employees.find(emp => emp.id_employe === employeeId)
    return employee ? `${employee.prenom} ${employee.nom}` : 'Employé inconnu'
  }

  const getProjectName = (projectId) => {
    const project = projects.find(proj => proj.id_projet === projectId)
    return project ? project.nom : 'Projet inconnu'
  }

  const getEmployeeRate = (employeeId) => {
    const employee = employees.find(emp => emp.id_employe === employeeId)
    return employee ? employee.taux_horaire : 0
  }

  const filteredPunchs = punchs.filter(punch => {
    if (filters.employee && punch.id_employe !== parseInt(filters.employee)) return false
    if (filters.project && punch.id_projet !== parseInt(filters.project)) return false
    if (filters.dateFrom && punch.date < filters.dateFrom) return false
    if (filters.dateTo && punch.date > filters.dateTo) return false
    return true
  })

  const calculateTotalHours = () => {
    return filteredPunchs.reduce((total, punch) => total + punch.heure_travaillee, 0)
  }

  const calculateTotalCost = () => {
    return filteredPunchs.reduce((total, punch) => {
      const rate = getEmployeeRate(punch.id_employe)
      return total + (punch.heure_travaillee * rate)
    }, 0)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg mr-3">
                <Clock className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Gestion des Pointages</h1>
                <p className="text-sm text-gray-600">Suivi des heures travaillées par les employés</p>
              </div>
            </div>
            <button
              onClick={handleCreatePunch}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center"
            >
              <Plus className="h-4 w-4 mr-2" />
              Nouveau Pointage
            </button>
          </div>
        </div>
      </div>

      <div className="px-6 py-6">
        {/* Filtres */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center mb-4">
            <Filter className="h-5 w-5 text-gray-400 dark:text-gray-500 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Filtres</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Employé */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Employé</label>
              <select
                value={filters.employee}
                onChange={(e) => setFilters(prev => ({ ...prev, employee: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Tous les employés</option>
                {employees.map((employee) => (
                  <option key={employee.id_employe} value={employee.id_employe}>
                    {employee.prenom} {employee.nom}
                  </option>
                ))}
              </select>
            </div>

            {/* Projet */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Projet</label>
              <select
                value={filters.project}
                onChange={(e) => setFilters(prev => ({ ...prev, project: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Tous les projets</option>
                {projects.map((project) => (
                  <option key={project.id_projet} value={project.id_projet}>
                    {project.nom}
                  </option>
                ))}
              </select>
            </div>

            {/* Date de début */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date de début</label>
              <input
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            {/* Date de fin */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date de fin</label>
              <input
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters(prev => ({ ...prev, dateTo: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
        </div>

        {/* Résumé */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Résumé</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {formatHours(calculateTotalHours())}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total heures</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                ${calculateTotalCost().toFixed(2)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Coût total</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                {filteredPunchs.length}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Pointages</div>
            </div>
          </div>
        </div>

        {/* Liste des pointages */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Pointages ({filteredPunchs.length})</h2>
          </div>
          
          {filteredPunchs.length === 0 ? (
            <div className="px-6 py-8 text-center">
              <Calendar className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600">Aucun pointage trouvé</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Employé
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Projet
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Section
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Heures
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Taux
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredPunchs.map((punch) => {
                    const rate = getEmployeeRate(punch.id_employe)
                    const total = punch.heure_travaillee * rate
                    
                    return (
                      <tr key={punch.id_punch} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {getEmployeeName(punch.id_employe)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {getProjectName(punch.id_projet)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {formatDate(punch.date)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {punch.section || '-'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {formatHours(punch.heure_travaillee)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            ${rate}/h
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-semibold text-green-600">
                            ${total.toFixed(2)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleEditPunch(punch)}
                              className="text-blue-600 hover:text-blue-900"
                              title="Modifier"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDeletePunch(punch)}
                              className="text-red-600 hover:text-red-900"
                              title="Supprimer"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Formulaire modal */}
      <PunchFormDesktop
        isOpen={showForm}
        onClose={() => {
          setShowForm(false)
          setEditingPunch(null)
        }}
        employee={selectedEmployee}
        punch={editingPunch}
        onSuccess={handleFormSuccess}
      />
    </div>
  )
}
