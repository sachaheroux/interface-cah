import React, { useState, useEffect } from 'react'
import { UserCheck, Plus, Clock, User } from 'lucide-react'
import { employeesService } from '../services/api'

export default function Employees() {
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchEmployees()
  }, [])

  const fetchEmployees = async () => {
    try {
      const response = await employeesService.getEmployees()
      setEmployees(response.data)
    } catch (err) {
      console.error('Employees error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Employés & Temps</h1>
          <p className="text-gray-600 mt-1">Gestion des employés et feuilles de temps</p>
        </div>
        <button className="btn-primary flex items-center">
          <Plus className="h-5 w-5 mr-2" />
          Nouvel Employé
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {employees.map((employee) => (
          <div key={employee.id} className="card">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-blue-100 rounded-lg">
                <User className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-semibold text-gray-900">{employee.name}</h3>
                <p className="text-sm text-gray-600">{employee.role}</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className={`px-2 py-1 text-xs rounded-full ${
                employee.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {employee.status === 'active' ? 'Actif' : 'Inactif'}
              </span>
              <button className="btn-secondary text-sm">
                <Clock className="h-4 w-4 mr-1" />
                Temps
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 