import React, { useState, useEffect } from 'react'
import { Filter, X } from 'lucide-react'

export default function BuildingFilters({ buildings, onFilterChange }) {
  const [filters, setFilters] = useState({
    city: '',
    yearBuilt: '',
    owner: '',
    currentValue: '',
    bank: ''
  })

  // Extraire les options uniques des immeubles existants
  const getUniqueOptions = () => {
    const cities = [...new Set(buildings.map(b => 
      typeof b.address === 'string' ? '' : b.address?.city
    ).filter(Boolean))].sort()
    
    const years = [...new Set(buildings.map(b => b.yearBuilt).filter(Boolean))].sort((a, b) => b - a)
    
    const owners = [...new Set(buildings.map(b => 
      b.contacts?.owner
    ).filter(Boolean))].sort()
    
    const banks = [...new Set(buildings.map(b => 
      b.contacts?.bank
    ).filter(Boolean))].sort()

    return { cities, years, owners, banks }
  }

  const { cities, years, owners, banks } = getUniqueOptions()

  const handleFilterChange = (field, value) => {
    const newFilters = { ...filters, [field]: value }
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  const clearFilters = () => {
    const emptyFilters = {
      city: '',
      yearBuilt: '',
      owner: '',
      currentValue: '',
      bank: ''
    }
    setFilters(emptyFilters)
    onFilterChange(emptyFilters)
  }

  const hasActiveFilters = Object.values(filters).some(value => value !== '')

  return (
    <div className="card mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Filter className="h-5 w-5 text-gray-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Filtres</h3>
        </div>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-gray-600 hover:text-gray-800 flex items-center"
          >
            <X className="h-4 w-4 mr-1" />
            Effacer tout
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {/* Filtre par ville */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ville
          </label>
          <select
            value={filters.city}
            onChange={(e) => handleFilterChange('city', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          >
            <option value="">Toutes les villes</option>
            {cities.map(city => (
              <option key={city} value={city}>{city}</option>
            ))}
          </select>
        </div>

        {/* Filtre par année de construction */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Date de construction
          </label>
          <select
            value={filters.yearBuilt}
            onChange={(e) => handleFilterChange('yearBuilt', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          >
            <option value="">Toutes les années</option>
            {years.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>

        {/* Filtre par propriétaire */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Propriétaire
          </label>
          <select
            value={filters.owner}
            onChange={(e) => handleFilterChange('owner', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          >
            <option value="">Tous les propriétaires</option>
            {owners.map(owner => (
              <option key={owner} value={owner}>{owner}</option>
            ))}
          </select>
        </div>

        {/* Filtre par valeur actuelle */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Valeur actuelle
          </label>
          <select
            value={filters.currentValue}
            onChange={(e) => handleFilterChange('currentValue', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          >
            <option value="">Toutes les valeurs</option>
            <option value="0-500000">Moins de 500k$</option>
            <option value="500000-1000000">500k$ - 1M$</option>
            <option value="1000000-2000000">1M$ - 2M$</option>
            <option value="2000000+">Plus de 2M$</option>
          </select>
        </div>

        {/* Filtre par banque */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Banque
          </label>
          <select
            value={filters.bank}
            onChange={(e) => handleFilterChange('bank', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          >
            <option value="">Toutes les banques</option>
            {banks.map(bank => (
              <option key={bank} value={bank}>{bank}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Indicateur de filtres actifs */}
      {hasActiveFilters && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            {Object.entries(filters).map(([key, value]) => {
              if (!value) return null
              
              const labels = {
                city: 'Ville',
                yearBuilt: 'Année',
                owner: 'Propriétaire',
                currentValue: 'Valeur',
                bank: 'Banque'
              }
              
              return (
                <span
                  key={key}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                >
                  {labels[key]}: {value}
                  <button
                    onClick={() => handleFilterChange(key, '')}
                    className="ml-2 text-primary-600 hover:text-primary-800"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
} 