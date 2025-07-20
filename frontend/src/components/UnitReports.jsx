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
    console.log(`🎯 DEBUG - Calcul revenus totaux pour unité ${unitId}`)
    let totalRevenue = 0
    let monthsWithRevenue = 0
    
    // Pour chaque mois de l'année
    for (let month = 1; month <= 12; month++) {
      const targetDate = new Date(parseInt(selectedYear), month - 1, 15) // 15ème jour du mois
      console.log(`📅 DEBUG - Mois ${month}: ${targetDate.toISOString()}`)
      
      // Trouver les assignations pour cette unité
      const unitAssignments = assignments.filter(a => a.unitId === unitId)
      console.log(`🔍 DEBUG - Assignations pour unité ${unitId}:`, unitAssignments.length)
      
      if (unitAssignments.length === 0) {
        console.log(`⚠️ DEBUG - Aucune assignation pour unité ${unitId} en mois ${month}`)
        continue
      }
      
      let monthRevenue = 0
      let activeTenantsThisMonth = 0
      
      // Pour chaque assignation, vérifier si le locataire était actif ce mois-là
      for (const assignment of unitAssignments) {
        console.log(`🔍 DEBUG - Vérification assignment ${assignment.id} (tenantId: ${assignment.tenantId})`)
        
        // Vérifier si le tenantId est valide (pas un timestamp JavaScript)
        const tenantId = assignment.tenantId
        const isInvalidId = typeof tenantId === 'number' && tenantId > 1000000000000 // Timestamp JavaScript typique
        
        if (isInvalidId) {
          console.log(`❌ DEBUG - TenantId invalide détecté: ${tenantId} (probablement un timestamp)`)
          continue
        }
        
        // Recherche plus flexible des locataires
        const tenant = allTenants.find(t => 
          t.id === tenantId || 
          t.id === String(tenantId) || 
          String(t.id) === tenantId ||
          t.id === parseInt(tenantId) ||
          parseInt(t.id) === tenantId
        )
        
        if (!tenant) {
          console.log(`❌ DEBUG - Locataire ${tenantId} non trouvé`)
          continue
        }

        console.log(`✅ DEBUG - Locataire trouvé: ${tenant.name}`)

        // Vérifier si le locataire était actif ce mois-là
        let isActiveThisMonth = false
        let currentRentAmount = 0
        
        // Vérifier avec les renouvellements (priorité)
        if (tenant.leaseRenewals && tenant.leaseRenewals.length > 0) {
          console.log(`🔍 DEBUG - Vérification ${tenant.leaseRenewals.length} renouvellements pour ${tenant.name}`)
          
          const activeRenewal = tenant.leaseRenewals.find(renewal => {
            const renewalStart = new Date(renewal.startDate)
            const renewalEnd = new Date(renewal.endDate)
            const isActive = targetDate >= renewalStart && targetDate <= renewalEnd
            
            console.log(`🔍 DEBUG - Renouvellement ${renewal.startDate} - ${renewal.endDate}: ${isActive ? 'ACTIF' : 'inactif'}`)
            
            return isActive
          })
          
          if (activeRenewal) {
            isActiveThisMonth = true
            currentRentAmount = activeRenewal.monthlyRent || 0
            console.log(`✅ DEBUG - Actif via renouvellement: ${currentRentAmount}$`)
          } else {
            console.log(`❌ DEBUG - Aucun renouvellement actif pour ${tenant.name} en mois ${month}`)
          }
        }
        // Sinon vérifier avec lease principal
        else if (tenant.lease) {
          const leaseStart = new Date(tenant.lease.startDate)
          const leaseEnd = new Date(tenant.lease.endDate)
          
          console.log(`🔍 DEBUG - Vérification bail principal: ${leaseStart} <= ${targetDate} <= ${leaseEnd}`)
          
          if (targetDate >= leaseStart && targetDate <= leaseEnd) {
            isActiveThisMonth = true
            currentRentAmount = tenant.lease.monthlyRent || 0
            console.log(`✅ DEBUG - Actif via bail principal: ${currentRentAmount}$`)
          } else {
            console.log(`❌ DEBUG - Bail principal non actif pour ${tenant.name} en mois ${month}`)
          }
        } else {
          console.log(`❌ DEBUG - Aucun bail trouvé pour ${tenant.name}`)
        }
        
        // Si le locataire était actif, ajouter le loyer au total du mois
        if (isActiveThisMonth) {
          monthRevenue += currentRentAmount
          activeTenantsThisMonth++
          console.log(`💰 DEBUG - Revenu ajouté pour mois ${month} (${tenant.name}): ${currentRentAmount}$ (Total mois: ${monthRevenue}$)`)
          // Continuer avec le prochain locataire (pas de break)
        } else {
          console.log(`❌ DEBUG - ${tenant.name} non actif pour mois ${month}`)
        }
      }
      
      // Ajouter le revenu du mois au total annuel
      if (monthRevenue > 0) {
        totalRevenue += monthRevenue
        monthsWithRevenue++
        console.log(`📊 DEBUG - Revenu du mois ${month}: ${monthRevenue}$ (Total annuel: ${totalRevenue}$)`)
      } else {
        console.log(`📊 DEBUG - Aucun revenu pour mois ${month}`)
      }
    }
    
    console.log(`🎯 DEBUG - Revenus totaux pour unité ${unitId}: ${totalRevenue}$ (${monthsWithRevenue} mois avec revenus)`)
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
                // Ne calculer que si les données sont chargées
                const totalRevenue = assignments.length > 0 && allTenants.length > 0 
                  ? calculateTotalRevenue(unit.id) 
                  : 0
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
                      {assignments.length === 0 || allTenants.length === 0 ? (
                        <span className="text-gray-500">Chargement...</span>
                      ) : (
                        formatCurrency(totalRevenue)
                      )}
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