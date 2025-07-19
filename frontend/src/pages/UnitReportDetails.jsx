import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Calendar, DollarSign, ArrowLeft, Building2 } from 'lucide-react'
import { buildingsService, assignmentsService, tenantsService } from '../services/api'
import { parseAddressAndGenerateUnits } from '../types/unit'

export default function UnitReportDetails() {
  const { unitId, year } = useParams()
  const navigate = useNavigate()
  const [unit, setUnit] = useState(null)
  const [loading, setLoading] = useState(true)
  const [assignments, setAssignments] = useState([])
  const [allTenants, setAllTenants] = useState([])

  const months = [
    { value: 1, name: 'Janvier' },
    { value: 2, name: 'Février' },
    { value: 3, name: 'Mars' },
    { value: 4, name: 'Avril' },
    { value: 5, name: 'Mai' },
    { value: 6, name: 'Juin' },
    { value: 7, name: 'Juillet' },
    { value: 8, name: 'Août' },
    { value: 9, name: 'Septembre' },
    { value: 10, name: 'Octobre' },
    { value: 11, name: 'Novembre' },
    { value: 12, name: 'Décembre' }
  ]

  useEffect(() => {
    loadUnitData()
    loadAssignments()
    loadTenants()
  }, [unitId, year])

  const loadUnitData = async () => {
    try {
      // Récupérer tous les immeubles pour trouver l'unité
      const response = await buildingsService.getBuildings()
      const buildings = response.data || []
      
      let targetUnit = null
      for (const building of buildings) {
        try {
          const buildingUnits = parseAddressAndGenerateUnits(building)
          targetUnit = buildingUnits.find(u => u.id === unitId)
          if (targetUnit) break
        } catch (error) {
          console.error('Error parsing building units:', error)
        }
      }
      
      setUnit(targetUnit)
    } catch (error) {
      console.error('Error loading unit data:', error)
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

  const getMonthName = (monthNumber) => {
    const month = months.find(m => m.value === monthNumber)
    return month ? month.name : monthNumber
  }

  // Fonction pour obtenir automatiquement les données d'un mois
  const getMonthData = (monthValue) => {
    // Trouver les assignations pour cette unité
    const unitAssignments = assignments.filter(a => a.unitId === unitId)
    
    if (unitAssignments.length === 0) {
      return {
        tenantName: '-',
        paymentMethod: '-',
        rentAmount: 0,
        isHeatedLit: unit?.amenities?.electricity || false,
        isFurnished: unit?.amenities?.furnished || false,
        wifiIncluded: unit?.amenities?.wifi || false
      }
    }

    // Pour chaque assignation, vérifier si le locataire était actif ce mois-là
    const targetDate = new Date(parseInt(year), monthValue - 1, 15) // 15ème jour du mois
    
    for (const assignment of unitAssignments) {
      const tenant = allTenants.find(t => t.id === assignment.tenantId)
      if (!tenant) continue

      // Vérifier si le locataire était actif ce mois-là
      let isActiveThisMonth = false
      let rentAmount = 0
      let paymentMethod = 'Virement bancaire'

      // Vérifier avec leaseRenewal (priorité)
      if (tenant.leaseRenewal && tenant.leaseRenewal.isActive) {
        const renewalStart = new Date(tenant.leaseRenewal.startDate)
        const renewalEnd = new Date(tenant.leaseRenewal.endDate)
        
        if (targetDate >= renewalStart && targetDate <= renewalEnd) {
          isActiveThisMonth = true
          rentAmount = tenant.leaseRenewal.monthlyRent || 0
          paymentMethod = tenant.lease?.paymentMethod || 'Virement bancaire'
        }
      }
      // Sinon vérifier avec lease principal
      else if (tenant.lease) {
        const leaseStart = new Date(tenant.lease.startDate)
        const leaseEnd = new Date(tenant.lease.endDate)
        
        if (targetDate >= leaseStart && targetDate <= leaseEnd) {
          isActiveThisMonth = true
          rentAmount = tenant.lease.monthlyRent || 0
          paymentMethod = tenant.lease.paymentMethod || 'Virement bancaire'
        }
      }

      // Si le locataire était actif, retourner ses données
      if (isActiveThisMonth) {
        return {
          tenantName: tenant.name,
          paymentMethod: paymentMethod,
          rentAmount: rentAmount,
          isHeatedLit: unit?.amenities?.electricity || false,
          isFurnished: unit?.amenities?.furnished || false,
          wifiIncluded: unit?.amenities?.wifi || false
        }
      }
    }

    // Aucun locataire actif trouvé pour ce mois
    return {
      tenantName: '-',
      paymentMethod: '-',
      rentAmount: 0,
      isHeatedLit: unit?.amenities?.electricity || false,
      isFurnished: unit?.amenities?.furnished || false,
      wifiIncluded: unit?.amenities?.wifi || false
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount || 0)
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Chargement des détails...</span>
        </div>
      </div>
    )
  }

  if (!unit) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="text-center">
          <p className="text-gray-500">Unité non trouvée</p>
          <button
            onClick={() => navigate('/reports')}
            className="mt-4 text-blue-600 hover:text-blue-900"
          >
            Retour aux rapports
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/reports')}
              className="flex items-center text-gray-500 hover:text-gray-700"
            >
              <ArrowLeft className="h-5 w-5 mr-2" />
              Retour aux rapports
            </button>
            <div className="h-6 border-l border-gray-300"></div>
            <div className="flex items-center space-x-3">
              <Building2 className="h-6 w-6 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {unit.buildingName} - {unit.unitNumber}
                </h1>
                <p className="text-gray-600">Rapports mensuels pour {year}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tableau des rapports mensuels */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Rapports Mensuels - {year}
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            🤖 Données générées automatiquement à partir des fiches locataires et unité
          </p>
          <div className="text-xs text-gray-500 mt-2">
            <strong>Locataire:</strong> Basé sur les assignations et durées de bail • 
            <strong className="ml-2">Loyer:</strong> Depuis la fiche locataire (bail/renouvellement) • 
            <strong className="ml-2">Conditions:</strong> Depuis la fiche de l'unité
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mois
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Locataire
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Paiement
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Conditions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Loyer
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {months.map((month) => {
                // Utiliser les données automatiques au lieu des rapports manuels
                const monthData = getMonthData(month.value)
                
                return (
                  <tr key={month.value} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {month.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {monthData.tenantName}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {monthData.paymentMethod}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex space-x-2">
                        {monthData.isHeatedLit && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            Chauffé-éclairé
                          </span>
                        )}
                        {monthData.isFurnished && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            Meublé
                          </span>
                        )}
                        {monthData.wifiIncluded && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            WiFi inclus
                          </span>
                        )}
                        {!monthData.isHeatedLit && !monthData.isFurnished && !monthData.wifiIncluded && monthData.tenantName !== '-' && (
                          <span className="text-gray-500">Standard</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {monthData.tenantName !== '-' ? formatCurrency(monthData.rentAmount) : '-'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
} 