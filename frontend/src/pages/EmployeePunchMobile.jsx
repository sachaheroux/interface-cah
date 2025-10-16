import React, { useState, useEffect } from 'react'
import { Clock, Calendar, Plus, User, LogOut, TrendingUp, ArrowLeft } from 'lucide-react'
import PunchFormMobile from '../components/PunchFormMobile'
import { employeesService, punchsService } from '../services/api'

export default function EmployeePunchMobile() {
  const [employee, setEmployee] = useState(null)
  const [currentUser, setCurrentUser] = useState(null)
  const [punchs, setPunchs] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(true) // S'ouvre directement sur le formulaire
  const [successMessage, setSuccessMessage] = useState('')
  const [currentWeek, setCurrentWeek] = useState(new Date())
  const [error, setError] = useState('')

  useEffect(() => {
    // Récupérer l'utilisateur connecté et trouver l'employé correspondant
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const user = JSON.parse(userStr)
        setCurrentUser(user)
        // Charger les employés pour trouver celui qui correspond
        fetchEmployeesAndMatch(user)
      } catch (e) {
        console.error('Erreur parsing user:', e)
      }
    }
  }, [])

  const fetchEmployeesAndMatch = async (user) => {
    try {
      setLoading(true)
      const response = await employeesService.getEmployees()
      const employees = response.data || []
      
      // Trouver l'employé correspondant
      const matchedEmployee = employees.find(emp => 
        emp.prenom.toLowerCase() === user.prenom?.toLowerCase() && 
        emp.nom.toLowerCase() === user.nom?.toLowerCase()
      )
      
      if (matchedEmployee) {
        setEmployee(matchedEmployee)
        fetchPunchs(matchedEmployee.id_employe)
      } else {
        setError('Aucune fiche employé trouvée avec votre nom. Veuillez demander à l\'administrateur de créer votre fiche employé.')
      }
    } catch (err) {
      console.error('Erreur lors du chargement des employés:', err)
      setError('Erreur lors du chargement des données')
    } finally {
      setLoading(false)
    }
  }

  const fetchPunchs = async (employeeId) => {
    try {
      setLoading(true)
      const response = await punchsService.getPunchsByEmployee(employeeId)
      setPunchs(response.data || [])
    } catch (err) {
      console.error('Erreur lors du chargement des pointages:', err)
      setPunchs([])
    } finally {
      setLoading(false)
    }
  }

  const handleFormSuccess = (message) => {
    setSuccessMessage(message)
    setShowForm(false)
    fetchPunchs(employee.id_employe)
    setTimeout(() => setSuccessMessage(''), 3000)
  }

  const handleFormClose = () => {
    setShowForm(false)
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('fr-CA', {
      weekday: 'short',
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

  const calculateWeekTotal = () => {
    const startOfWeek = new Date(currentWeek)
    startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay())
    const endOfWeek = new Date(startOfWeek)
    endOfWeek.setDate(endOfWeek.getDate() + 6)

    return punchs
      .filter(punch => {
        const punchDate = new Date(punch.date)
        return punchDate >= startOfWeek && punchDate <= endOfWeek
      })
      .reduce((total, punch) => total + punch.heure_travaillee, 0)
  }

  const calculateWeekEarnings = () => {
    const weekHours = calculateWeekTotal()
    return weekHours * (employee?.taux_horaire || 0)
  }

  const navigateWeek = (direction) => {
    const newWeek = new Date(currentWeek)
    newWeek.setDate(newWeek.getDate() + (direction * 7))
    setCurrentWeek(newWeek)
  }

  const getWeekPunchs = () => {
    const startOfWeek = new Date(currentWeek)
    startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay())
    const endOfWeek = new Date(startOfWeek)
    endOfWeek.setDate(endOfWeek.getDate() + 6)

    return punchs.filter(punch => {
      const punchDate = new Date(punch.date)
      return punchDate >= startOfWeek && punchDate <= endOfWeek
    })
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

  if (!employee && error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <User className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Fiche employé manquante</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.href = '/login'}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retour à la connexion
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Mobile */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg mr-3">
                <Clock className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  {employee.prenom} {employee.nom}
                </h1>
                <p className="text-sm text-gray-600">{employee.poste}</p>
              </div>
            </div>
            <button className="p-2 text-gray-400 hover:text-gray-600">
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Message de succès */}
      {successMessage && (
        <div className="mx-4 mt-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
          {successMessage}
        </div>
      )}

      {/* Stats de la semaine */}
      <div className="px-4 py-4">
        <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-900">Cette semaine</h2>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => navigateWeek(-1)}
                className="p-1 text-gray-400 hover:text-gray-600"
              >
                ←
              </button>
              <span className="text-sm text-gray-600">
                {currentWeek.toLocaleDateString('fr-CA', { month: 'short', year: 'numeric' })}
              </span>
              <button
                onClick={() => navigateWeek(1)}
                className="p-1 text-gray-400 hover:text-gray-600"
              >
                →
              </button>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {formatHours(calculateWeekTotal())}
              </div>
              <div className="text-sm text-gray-600">Heures</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                ${calculateWeekEarnings().toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">Gains</div>
            </div>
          </div>
        </div>

        {/* Bouton ajouter pointage */}
        <button
          onClick={() => setShowForm(true)}
          className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium flex items-center justify-center mb-4"
        >
          <Plus className="h-5 w-5 mr-2" />
          Ajouter un pointage
        </button>

        {/* Liste des pointages de la semaine */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-4 py-3 border-b border-gray-200">
            <h3 className="font-semibold text-gray-900">Pointages de la semaine</h3>
          </div>
          
          {getWeekPunchs().length === 0 ? (
            <div className="px-4 py-8 text-center">
              <Calendar className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600">Aucun pointage cette semaine</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {getWeekPunchs().map((punch) => (
                <div key={punch.id_punch} className="px-4 py-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">
                        {formatDate(punch.date)}
                      </div>
                      <div className="text-sm text-gray-600">
                        {punch.section && `${punch.section} • `}
                        {formatHours(punch.heure_travaillee)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-green-600">
                        ${(punch.heure_travaillee * employee.taux_horaire).toFixed(2)}
                      </div>
                      <div className="text-sm text-gray-600">
                        @ ${employee.taux_horaire}/h
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Formulaire modal */}
      <PunchFormMobile
        isOpen={showForm}
        onClose={handleFormClose}
        onSuccess={handleFormSuccess}
      />
    </div>
  )
}
