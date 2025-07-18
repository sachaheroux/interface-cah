import React, { useState, useEffect } from 'react'
import { Building2, Users, Calendar, BarChart3 } from 'lucide-react'
import BuildingReports from '../components/BuildingReports'
import UnitReports from '../components/UnitReports'

export default function Reports() {
  const [activeTab, setActiveTab] = useState('buildings')
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())

  // Générer les années disponibles (2024 à année actuelle + 2)
  const availableYears = []
  const currentYear = new Date().getFullYear()
  for (let year = 2024; year <= currentYear + 2; year++) {
    availableYears.push(year)
  }

  const tabs = [
    {
      id: 'buildings',
      name: 'Rapports d\'Immeubles',
      icon: Building2,
      description: 'Données financières et opérationnelles par immeuble et par année'
    },
    {
      id: 'units',
      name: 'Rapports d\'Unités',
      icon: Users,
      description: 'Historique détaillé des locataires et revenus par unité et par mois'
    }
  ]

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Rapports</h1>
              <p className="text-gray-600">Analysez les performances de vos immeubles et unités</p>
            </div>
          </div>
          
          {/* Sélecteur d'année */}
          <div className="flex items-center space-x-2">
            <Calendar className="h-5 w-5 text-gray-400" />
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
              className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {availableYears.map(year => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Navigation des onglets */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors duration-200 ${
                    isActive
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Description de l'onglet actif */}
        <div className="px-6 py-4 bg-gray-50">
          <p className="text-sm text-gray-600">
            {tabs.find(tab => tab.id === activeTab)?.description}
          </p>
        </div>
      </div>

      {/* Contenu des rapports */}
      <div className="space-y-6">
        {activeTab === 'buildings' && (
          <BuildingReports selectedYear={selectedYear} />
        )}
        
        {activeTab === 'units' && (
          <UnitReports selectedYear={selectedYear} />
        )}
      </div>
    </div>
  )
} 