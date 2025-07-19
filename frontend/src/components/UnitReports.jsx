import React, { useState, useEffect } from 'react'
import { Users, DollarSign, Eye, Search } from 'lucide-react'
import { buildingsService, assignmentsService, tenantsService } from '../services/api'
import { parseAddressAndGenerateUnits } from '../types/unit'
import { useNavigate } from 'react-router-dom'

export default function UnitReports({ selectedYear }) {
  const [buildings, setBuildings] = useState([])
  const [units, setUnits] = useState([])
  const [assignments, setAssignments] = useState([])
  const [allTenants, setAllTenants] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadBuildings()
    loadAssignments()
    loadTenants()
  }, [selectedYear])

  const loadBuildings = async () => {
    try {
      setLoading(true)
      const response = await buildingsService.getBuildings()
      const buildingsData = response.data || []
      setBuildings(buildingsData)
      
      // Générer les unités pour tous les immeubles
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

  const loadAssignments = async () => {
    try {
      const response = await assignmentsService.getAssignments()
      setAssignments(response.data || [])
    } catch (error) {
      console.error('Error loading assignments:', error)
    }
  }

  const loadTenants = async () => {
    try {
      const response = await tenantsService.getTenants()
      setAllTenants(response.data || [])
    } catch (error) {
      console.error('Error loading tenants:', error)
    } finally {
      setLoading(false)
    }
  }

  // Fonction pour calculer les revenus totaux d'une unité pour l'année
  const calculateTotalRevenue = (unitId) => {
    let totalRevenue = 0
    
    // Pour chaque mois de l'année
    for (let month = 1; month <= 12; month++) {
      const targetDate = new Date(parseInt(selectedYear), month - 1, 15) // 15ème jour du mois
      
      // Trouver les assignations pour cette unité
      const unitAssignments = assignments.filter(a => a.unitId === unitId)
      
      if (unitAssignments.length === 0) continue
      
      // Pour chaque assignation, vérifier si le locataire était actif ce mois-là
      for (const assignment of unitAssignments) {
        const tenant = allTenants.find(t => t.id === assignment.tenantId)
        if (!tenant) continue
        
        let isActiveThisMonth = false
        let currentRentAmount = 0
        
        // Vérifier avec les renouvellements (priorité)
        if (tenant.leaseRenewals && tenant.leaseRenewals.length > 0) {
          const activeRenewal = tenant.leaseRenewals.find(renewal => {
            const renewalStart = new Date(renewal.startDate)
            const renewalEnd = new Date(renewal.endDate)
            return targetDate >= renewalStart && targetDate <= renewalEnd
          })
          
          if (activeRenewal) {
            isActiveThisMonth = true
            currentRentAmount = activeRenewal.monthlyRent || 0
          }
        }
        // Sinon vérifier avec lease principal
        else if (tenant.lease) {
          const leaseStart = new Date(tenant.lease.startDate)
          const leaseEnd = new Date(tenant.lease.endDate)
          
          if (targetDate >= leaseStart && targetDate <= leaseEnd) {
            isActiveThisMonth = true
            currentRentAmount = tenant.lease.monthlyRent || 0
          }
        }
        
        // Si le locataire était actif, ajouter le loyer au total
        if (isActiveThisMonth) {
          totalRevenue += currentRentAmount
          break // Un seul locataire actif par mois
        }
      }
    }
    
    return totalRevenue
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount || 0)
  }

  const formatAddress = (address) => {
    if (typeof address === 'string') {
      return address
    }
    if (address && typeof address === 'object') {
      return `${address.street || ''}, ${address.city || ''}`.replace(/^,\s*/, '').replace(/,\s*$/, '')
    }
    return ''
  }

  // Filtrer les unités selon le terme de recherche
  const filteredUnits = units.filter(unit => {
    const searchLower = searchTerm.toLowerCase()
    const unitName = `${unit.buildingName} - ${unit.unitNumber}`.toLowerCase()
    const address = formatAddress(unit.address).toLowerCase()
    return unitName.includes(searchLower) || address.includes(searchLower)
  })

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">
            Chargement des rapports d'unités...
          </span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Liste des unités */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                Rapports d'Unités - {selectedYear}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Historique détaillé des locataires et revenus par unité et par mois
              </p>
            </div>
            
            {/* Champ de recherche */}
            <div className="flex items-center space-x-2">
              <div className="relative">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Rechercher une unité..."
                  className="pl-8 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <Search className="h-4 w-4 text-gray-400 absolute left-2.5 top-2.5" />
              </div>
            </div>
          </div>
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
                  Détails
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUnits.map((unit) => {
                const totalRevenue = calculateTotalRevenue(unit.id)
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
                            {formatAddress(unit.address)}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        Données automatiques basées sur les fiches locataires
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(totalRevenue)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => navigate(`/unit-reports/${unit.id}/${selectedYear}`)}
                        className="text-blue-600 hover:text-blue-900 flex items-center"
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        Voir détails
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Message si aucun résultat */}
        {filteredUnits.length === 0 && searchTerm && (
          <div className="text-center py-8">
            <p className="text-gray-500">Aucune unité trouvée pour "{searchTerm}"</p>
          </div>
        )}
      </div>
    </div>
  )
} 