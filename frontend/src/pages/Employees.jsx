import React, { useState, useEffect } from 'react'
import { UserCheck, Plus, Clock, User, Edit, Trash2 } from 'lucide-react'
import { employeesService } from '../services/api'
import EmployeeForm from '../components/EmployeeForm'

export default function Employees() {
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingEmployee, setEditingEmployee] = useState(null)
  const [successMessage, setSuccessMessage] = useState('')

  useEffect(() => {
    fetchEmployees()
  }, [])

  const fetchEmployees = async () => {
    try {
      setLoading(true)
      const response = await employeesService.getEmployees()
      setEmployees(response.data || [])
    } catch (err) {
      console.error('Employees error:', err)
      setEmployees([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateEmployee = () => {
    setEditingEmployee(null)
    setShowForm(true)
  }

  const handleEditEmployee = (employee) => {
    setEditingEmployee(employee)
    setShowForm(true)
  }

  const handleDeleteEmployee = async (employee) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer ${employee.prenom} ${employee.nom} ?`)) {
      try {
        await employeesService.deleteEmployee(employee.id_employe)
        setSuccessMessage('Employé supprimé avec succès')
        fetchEmployees()
        setTimeout(() => setSuccessMessage(''), 3000)
      } catch (err) {
        console.error('Erreur lors de la suppression:', err)
        alert('Erreur lors de la suppression de l\'employé')
      }
    }
  }

  const handleFormSuccess = (message) => {
    setSuccessMessage(message)
    setShowForm(false)
    setEditingEmployee(null)
    fetchEmployees()
    setTimeout(() => setSuccessMessage(''), 3000)
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingEmployee(null)
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Employés Construction</h1>
          <p className="text-gray-600 mt-1">Gestion des employés de construction</p>
        </div>
        <button 
          onClick={handleCreateEmployee}
          className="btn-primary flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          Nouvel Employé
        </button>
      </div>

      {/* Message de succès */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
          {successMessage}
        </div>
      )}

      {/* Liste des employés */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {employees.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun employé</h3>
            <p className="text-gray-600 mb-4">Commencez par ajouter votre premier employé</p>
            <button 
              onClick={handleCreateEmployee}
              className="btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              Ajouter un employé
            </button>
          </div>
        ) : (
          employees.map((employee) => (
            <div key={employee.id_employe} className="card">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <User className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-3 flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {employee.prenom} {employee.nom}
                  </h3>
                  <p className="text-sm text-gray-600">{employee.poste || 'Poste non défini'}</p>
                </div>
              </div>
              
              {/* Informations de contact */}
              <div className="space-y-2 mb-4">
                {employee.numero && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Clock className="h-4 w-4 mr-2" />
                    {employee.numero}
                  </div>
                )}
                {employee.adresse_courriel && (
                  <div className="flex items-center text-sm text-gray-600">
                    <User className="h-4 w-4 mr-2" />
                    {employee.adresse_courriel}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between">
                <div className="flex space-x-2">
                  <button 
                    onClick={() => handleEditEmployee(employee)}
                    className="btn-secondary text-sm flex items-center"
                  >
                    <Edit className="h-4 w-4 mr-1" />
                    Modifier
                  </button>
                  <button 
                    onClick={() => handleDeleteEmployee(employee)}
                    className="btn-secondary text-sm flex items-center text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    Supprimer
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Formulaire modal */}
      <EmployeeForm
        isOpen={showForm}
        onClose={handleCloseForm}
        employee={editingEmployee}
        onSuccess={handleFormSuccess}
      />
    </div>
  )
} 