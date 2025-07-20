import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Building2, FileText, Calendar, DollarSign, Users, Eye } from 'lucide-react'
import { buildingsService, assignmentsService, tenantsService } from '../services/api'
import { parseAddressAndGenerateUnits } from '../types/unit'

// Configuration de l'API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
      setLoading(true)
      console.log(`🔄 UnitReportDetails: Recherche de l'unité avec ID: "${unitId}"`)
      // Récupérer tous les immeubles pour trouver l'unité
      const response = await buildingsService.getBuildings()
      const buildings = response.data || []
      console.log('🏢 UnitReportDetails: Immeubles chargés:', buildings.length)
      
      let targetUnit = null
      for (const building of buildings) {
        try {
          const buildingUnits = parseAddressAndGenerateUnits(building)
          console.log(`🏠 Building "${building.name}" - unités générées:`, buildingUnits.map(u => ({
            id: u.id,
            unitNumber: u.unitNumber,
            buildingName: u.buildingName
          })))
          
          targetUnit = buildingUnits.find(u => u.id === unitId)
          if (targetUnit) {
            console.log('✅ UnitReportDetails: Unité trouvée:', {
              id: targetUnit.id,
              buildingName: targetUnit.buildingName,
              unitNumber: targetUnit.unitNumber
            })
            break
          }
        } catch (error) {
          console.error('Error parsing building units:', error)
        }
      }
      
      if (targetUnit) {
        setUnit(targetUnit)
      } else {
        console.error(`❌ UnitReportDetails: Unité ${unitId} non trouvée`)
      }
    } catch (error) {
      console.error('Error loading unit data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadAssignments = async () => {
    try {
      console.log('🔄 UnitReportDetails: Chargement des assignations...')
      const response = await assignmentsService.getAssignments()
      const assignmentsData = response.data || []
      console.log('✅ UnitReportDetails: Assignations chargées:', {
        count: assignmentsData.length,
        assignments: assignmentsData
      })
      
      // Debug: Afficher tous les unitId des assignations
      const allUnitIds = assignmentsData.map(a => a.unitId)
      console.log('🔍 UnitReportDetails: Tous les unitId des assignations:', allUnitIds)
      console.log(`🎯 UnitReportDetails: Recherche pour unitId: "${unitId}"`)
      console.log('🔍 UnitReportDetails: Correspondance exacte?', allUnitIds.includes(unitId))
      
      // Debug: Afficher les détails des assignations pour cette unité
      const targetAssignments = assignmentsData.filter(a => a.unitId === unitId)
      if (targetAssignments.length > 0) {
        console.log(`🔍 UnitReportDetails: Assignations pour unité "${unitId}":`, targetAssignments.map(a => ({
          id: a.id,
          unitId: a.unitId,
          tenantId: a.tenantId,
          tenantIdType: typeof a.tenantId
        })))
      }
      
      setAssignments(assignmentsData)
    } catch (error) {
      console.error('❌ UnitReportDetails: Error loading assignments:', error)
    }
  }

  const loadTenants = async () => {
    try {
      console.log('🔄 UnitReportDetails: Chargement des locataires...')
      const response = await tenantsService.getTenants()
      const tenantsData = response.data || []
      console.log('✅ UnitReportDetails: Locataires chargés:', {
        count: tenantsData.length,
        tenants: tenantsData
      })
      
      // Debug: Afficher tous les IDs des locataires
      const allTenantIds = tenantsData.map(t => t.id)
      console.log('🔍 UnitReportDetails: Tous les IDs des locataires:', allTenantIds)
      
      setAllTenants(tenantsData)
    } catch (error) {
      console.error('❌ UnitReportDetails: Error loading tenants:', error)
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
    console.log(`🐛 DEBUG - getMonthData pour mois ${monthValue}:`, {
      unitId,
      year,
      assignmentsCount: assignments.length,
      tenantsCount: allTenants.length,
      unitExists: !!unit
    })

    // Trouver les assignations pour cette unité
    const unitAssignments = assignments.filter(a => a.unitId === unitId)
    console.log(`🐛 DEBUG - Assignations pour unité ${unitId}:`, unitAssignments)
    console.log(`🐛 DEBUG - Tous les assignments:`, assignments.map(a => ({ unitId: a.unitId, tenantId: a.tenantId })))
    
    if (unitAssignments.length === 0) {
      console.log(`⚠️ Aucune assignation trouvée pour unité ${unitId}`)
      return {
        tenantName: '-',
        paymentMethod: '-',
        rentAmount: 0,
        isHeatedLit: unit?.amenities?.heating || unit?.amenities?.electricity || false,
        isFurnished: unit?.amenities?.furnished || false,
        wifiIncluded: unit?.amenities?.wifi || false
      }
    }

    // Pour chaque assignation, vérifier si le locataire était actif ce mois-là
    const targetDate = new Date(parseInt(year), monthValue - 1, 15) // 15ème jour du mois
    console.log(`🐛 DEBUG - Date cible pour mois ${monthValue}:`, targetDate)
    
    // Collecter TOUS les locataires actifs pour ce mois
    const activeTenantsThisMonth = []
    let totalRentAmount = 0
    
    console.log(`🐛 DEBUG - Tous les locataires disponibles:`, allTenants.map(t => ({ id: t.id, name: t.name })))
    
    for (const assignment of unitAssignments) {
      // Recherche plus flexible des locataires
      let tenant = allTenants.find(t => 
        t.id === assignment.tenantId || 
        t.id === String(assignment.tenantId) || 
        String(t.id) === assignment.tenantId ||
        t.id === parseInt(assignment.tenantId) ||
        parseInt(t.id) === assignment.tenantId
      )
      
      console.log(`🐛 DEBUG - Assignment ${assignment.id}, recherche locataire ${assignment.tenantId}:`, {
        assignment,
        tenantFound: !!tenant,
        tenant: tenant,
        tenantIdType: typeof assignment.tenantId,
        allTenantIds: allTenants.map(t => ({ id: t.id, type: typeof t.id }))
      })
      
      if (!tenant) {
        console.log(`⚠️ Locataire ${assignment.tenantId} non trouvé - assignation orpheline`)
        
        // Vérifier si le tenantId est un timestamp invalide
        const tenantId = assignment.tenantId
        const isInvalidId = typeof tenantId === 'number' && tenantId > 1000000000000 // Timestamp JavaScript typique
        
        if (isInvalidId) {
          console.log(`❌ TenantId invalide détecté: ${tenantId} (probablement un timestamp) - assignation ignorée`)
          continue
        }
        
        // Essayer de trouver par nom si available dans tenantData
        if (assignment.tenantData && assignment.tenantData.name) {
          const tenantByName = allTenants.find(t => t.name === assignment.tenantData.name)
          if (tenantByName) {
            console.log(`🔄 Correspondance par nom trouvée: ${tenantByName.name} (ID: ${tenantByName.id})`)
            tenant = tenantByName
          }
        }
        
        // Si toujours pas trouvé, ignorer cette assignation
        if (!tenant) {
          console.log(`❌ Assignment ${assignment.id} ignorée - locataire introuvable`)
          continue
        }
      }

      // Vérifier si le locataire était actif ce mois-là
      let isActiveThisMonth = false
      let currentRentAmount = 0
      let currentPaymentMethod = 'Virement bancaire'

      console.log(`🐛 DEBUG - Vérification bail pour ${tenant.name}:`, {
        leaseRenewals: tenant.leaseRenewals,
        lease: tenant.lease
      })

      // Vérifier avec les renouvellements (priorité)
      if (tenant.leaseRenewals && tenant.leaseRenewals.length > 0) {
        console.log(`🔍 Vérification des ${tenant.leaseRenewals.length} renouvellements pour ${tenant.name}`)
        
        // Trouver le renouvellement actif pour cette date
        const activeRenewal = tenant.leaseRenewals.find(renewal => {
          const renewalStart = new Date(renewal.startDate)
          const renewalEnd = new Date(renewal.endDate)
          const isActive = targetDate >= renewalStart && targetDate <= renewalEnd
          
          console.log(`🔍 Renouvellement ${renewal.startDate} - ${renewal.endDate}: ${isActive ? 'ACTIF' : 'inactif'}`)
          
          return isActive
        })
        
        if (activeRenewal) {
          isActiveThisMonth = true
          currentRentAmount = activeRenewal.monthlyRent || 0
          currentPaymentMethod = tenant.lease?.paymentMethod || 'Virement bancaire'
          console.log(`✅ Actif via renouvellement: ${currentRentAmount}$ ${currentPaymentMethod}`)
        } else {
          console.log(`❌ Aucun renouvellement actif pour ${tenant.name} en ${monthValue}/${year}`)
        }
      }
      // Sinon vérifier avec lease principal
      else if (tenant.lease) {
        const leaseStart = new Date(tenant.lease.startDate)
        const leaseEnd = new Date(tenant.lease.endDate)
        
        console.log(`🔄 Vérification bail principal: ${leaseStart} <= ${targetDate} <= ${leaseEnd}`)
        
        if (targetDate >= leaseStart && targetDate <= leaseEnd) {
          isActiveThisMonth = true
          currentRentAmount = tenant.lease.monthlyRent || 0
          currentPaymentMethod = tenant.lease.paymentMethod || 'Virement bancaire'
          console.log(`✅ Actif via bail principal: ${currentRentAmount}$ ${currentPaymentMethod}`)
        } else {
          console.log(`❌ Bail principal non actif pour ${tenant.name} en ${monthValue}/${year}`)
        }
      } else {
        console.log(`❌ Aucun bail trouvé pour ${tenant.name}`)
      }

      // Si le locataire était actif, l'ajouter à la liste
      if (isActiveThisMonth) {
        // Déterminer les conditions du bail actuel
        let currentAmenities = {
          heating: false,
          electricity: false,
          wifi: false,
          furnished: false
        }
        
        // Utiliser les conditions du renouvellement si actif
        if (tenant.leaseRenewals && tenant.leaseRenewals.length > 0) {
          // Trouver le renouvellement actif pour cette date
          const activeRenewal = tenant.leaseRenewals.find(renewal => {
            const renewalStart = new Date(renewal.startDate)
            const renewalEnd = new Date(renewal.endDate)
            return targetDate >= renewalStart && targetDate <= renewalEnd
          })
          
          if (activeRenewal) {
            currentAmenities = activeRenewal.amenities || tenant.lease?.amenities || currentAmenities
            console.log(`✅ Conditions du renouvellement pour ${tenant.name}:`, currentAmenities)
          }
        }
        // Sinon utiliser les conditions du bail principal
        else if (tenant.lease) {
          currentAmenities = tenant.lease.amenities || currentAmenities
          console.log(`✅ Conditions du bail principal pour ${tenant.name}:`, currentAmenities)
        }
        
        activeTenantsThisMonth.push({
          name: tenant.name,
          rentAmount: currentRentAmount,
          paymentMethod: currentPaymentMethod,
          amenities: currentAmenities
        })
        
        // Ne pas additionner au total des revenus ici - on le fera après avoir traité tous les locataires
        // totalRentAmount += currentRentAmount
        
        console.log(`✅ Locataire actif ajouté: ${tenant.name} (${currentRentAmount}$)`)
      } else {
        console.log(`❌ Locataire ${tenant.name} non actif pour ce mois`)
      }
      // Continuer avec le prochain locataire (pas de break)
    }

    // Après avoir traité tous les locataires, prendre le montant du premier locataire seulement
    // (puisque tous les locataires d'une même unité partagent le même bail)
    if (activeTenantsThisMonth.length > 0) {
      totalRentAmount = activeTenantsThisMonth[0].rentAmount || 0
      console.log(`💰 Revenu total pour unité ${unitId}, mois ${monthValue}: ${totalRentAmount}$ (basé sur le premier locataire seulement)`)
    }

    console.log(`🐛 DEBUG - Résumé final pour mois ${monthValue}:`, {
      totalAssignments: unitAssignments.length,
      activeTenantsCount: activeTenantsThisMonth.length,
      activeTenants: activeTenantsThisMonth.map(t => t.name),
      totalRentAmount: totalRentAmount
    })

    // Construire le résultat avec tous les locataires actifs
    if (activeTenantsThisMonth.length > 0) {
      const allTenantNames = activeTenantsThisMonth.map(t => t.name).join(', ')
      
      // Utiliser les conditions du premier locataire (ils ont tous les mêmes conditions)
      const firstTenantAmenities = activeTenantsThisMonth[0].amenities || {
        heating: false,
        electricity: false,
        wifi: false,
        furnished: false
      }
      
      // Afficher le loyer du premier locataire seulement (pas d'addition)
      const firstTenantRent = activeTenantsThisMonth[0].rentAmount || 0
      
      const result = {
        tenantName: allTenantNames,
        paymentMethod: activeTenantsThisMonth[0].paymentMethod || 'Virement bancaire',
        rentAmount: firstTenantRent, // Loyer du premier locataire seulement
        isHeatedLit: firstTenantAmenities.heating || firstTenantAmenities.electricity || false,
        isFurnished: firstTenantAmenities.furnished || false,
        wifiIncluded: firstTenantAmenities.wifi || false
      }
      
      console.log(`🐛 DEBUG - Conditions du bail pour ${unitId}:`, {
        firstTenantAmenities,
        resultConditions: {
          isHeatedLit: result.isHeatedLit,
          isFurnished: result.isFurnished,
          wifiIncluded: result.wifiIncluded
        }
      })
      
      console.log(`🎉 Données trouvées pour mois ${monthValue} (${activeTenantsThisMonth.length} locataires):`, result)
      return result
    }

    // Aucun locataire actif trouvé pour ce mois
    console.log(`❌ Aucun locataire actif trouvé pour mois ${monthValue}`)
    
    // Utiliser les conditions de l'unité par défaut si aucun locataire
    return {
      tenantName: '-',
      paymentMethod: '-',
      rentAmount: 0,
      isHeatedLit: unit?.amenities?.heating || unit?.amenities?.electricity || false,
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
            Détails pour chaque mois de l'année
          </p>
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

      {/* Section des PDFs des baux */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Documents de Bail
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            PDFs des baux et renouvellements pour cette unité
          </p>
        </div>
        
        <div className="p-6">
          {/* Trouver les locataires assignés à cette unité */}
          {(() => {
            const unitAssignments = assignments.filter(a => a.unitId === unitId)
            const tenantsWithLeases = []
            
            console.log(`🔍 DEBUG - Recherche des locataires pour unité ${unitId}:`)
            console.log(`📋 Assignations trouvées:`, unitAssignments)
            
            unitAssignments.forEach(assignment => {
              const tenant = allTenants.find(t => t.id === assignment.tenantId)
              console.log(`🔍 Assignment ${assignment.id}:`, {
                tenantId: assignment.tenantId,
                tenantFound: !!tenant,
                tenant: tenant ? { id: tenant.id, name: tenant.name } : null,
                hasLease: tenant?.lease ? true : false,
                hasRenewals: tenant?.leaseRenewals ? tenant.leaseRenewals.length : 0
              })
              
              if (tenant) {
                tenantsWithLeases.push(tenant)
              } else {
                console.log(`⚠️ Assignment ${assignment.id} ignorée - tenantId ${assignment.tenantId} non trouvé`)
              }
            })
            
            // Si aucun locataire trouvé via assignations, essayer de trouver tous les locataires qui ont des baux
            if (tenantsWithLeases.length === 0) {
              console.log(`🔍 Aucun locataire trouvé via assignations, recherche de tous les locataires avec baux...`)
              
              // Chercher tous les locataires qui ont des baux (pour afficher l'historique)
              const allTenantsWithLeases = allTenants.filter(tenant => 
                tenant.lease || (tenant.leaseRenewals && tenant.leaseRenewals.length > 0)
              )
              
              console.log(`📋 Locataires avec baux trouvés:`, allTenantsWithLeases.map(t => ({
                id: t.id,
                name: t.name,
                hasLease: !!t.lease,
                hasRenewals: t.leaseRenewals ? t.leaseRenewals.length : 0
              })))
              
              tenantsWithLeases.push(...allTenantsWithLeases)
            }
            
            console.log(`📊 Résumé des locataires avec baux:`, tenantsWithLeases.map(t => ({
              id: t.id,
              name: t.name,
              hasLease: !!t.lease,
              hasRenewals: t.leaseRenewals ? t.leaseRenewals.length : 0,
              leasePdf: t.lease?.leasePdf || 'Aucun',
              renewalsWithPdf: t.leaseRenewals ? t.leaseRenewals.filter(r => r.renewalPdf).length : 0
            })))
            
            if (tenantsWithLeases.length === 0) {
              return (
                <div className="text-center py-8">
                  <p className="text-gray-500">Aucun locataire assigné à cette unité</p>
                </div>
              )
            }
            
            return (
              <div className="space-y-4">
                {tenantsWithLeases.map((tenant, index) => (
                  <div key={tenant.id} className="border rounded-lg p-4">
                    <h4 className="text-md font-medium text-gray-900 mb-3">
                      {tenant.name}
                    </h4>
                    
                    <div className="space-y-3">
                      {/* PDF du bail principal */}
                      {tenant.lease?.leasePdf && (
                        <div className="flex items-center justify-between bg-blue-50 p-3 rounded">
                          <div className="flex items-center">
                            <FileText className="h-4 w-4 text-blue-600 mr-2" />
                            <span className="text-sm font-medium text-gray-900">Bail principal</span>
                          </div>
                          <button
                            onClick={async () => {
                              console.log(`🔍 Tentative d'ouverture PDF: ${tenant.lease.leasePdf}`)
                              const pdfUrl = `${API_BASE_URL}/api/documents/${tenant.lease.leasePdf}`
                              console.log(`🔗 URL PDF: ${pdfUrl}`)
                              
                              try {
                                const response = await fetch(pdfUrl)
                                if (response.ok) {
                                  window.open(pdfUrl, '_blank')
                                } else {
                                  console.error(`❌ PDF non trouvé: ${tenant.lease.leasePdf}`)
                                  alert(`Le fichier PDF "${tenant.lease.leasePdf}" n'existe pas sur le serveur.\n\nPour résoudre ce problème:\n1. Uploadez le fichier PDF via l'interface\n2. Ou contactez l'administrateur`)
                                }
                              } catch (error) {
                                console.error('Erreur lors de l\'ouverture du PDF:', error)
                                alert('Erreur lors de l\'ouverture du PDF. Vérifiez votre connexion.')
                              }
                            }}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            Voir PDF
                          </button>
                        </div>
                      )}
                      
                      {/* PDFs des renouvellements */}
                      {tenant.leaseRenewals && tenant.leaseRenewals.length > 0 && (
                        <div className="space-y-2">
                          {tenant.leaseRenewals.map((renewal, renewalIndex) => (
                            <div key={renewal.id || renewalIndex} className="flex items-center justify-between bg-green-50 p-3 rounded">
                              <div className="flex items-center">
                                <FileText className="h-4 w-4 text-green-600 mr-2" />
                                <span className="text-sm font-medium text-gray-900">
                                  Renouvellement {renewalIndex + 1} ({renewal.startDate} - {renewal.endDate})
                                </span>
                              </div>
                              {renewal.renewalPdf ? (
                                <button
                                  onClick={async () => {
                                    console.log(`🔍 Tentative d'ouverture PDF renouvellement: ${renewal.renewalPdf}`)
                                    const pdfUrl = `${API_BASE_URL}/api/documents/${renewal.renewalPdf}`
                                    console.log(`🔗 URL PDF renouvellement: ${pdfUrl}`)
                                    
                                    try {
                                      const response = await fetch(pdfUrl)
                                      if (response.ok) {
                                        window.open(pdfUrl, '_blank')
                                      } else {
                                        console.error(`❌ PDF renouvellement non trouvé: ${renewal.renewalPdf}`)
                                        alert(`Le fichier PDF "${renewal.renewalPdf}" n'existe pas sur le serveur.\n\nPour résoudre ce problème:\n1. Uploadez le fichier PDF via l'interface\n2. Ou contactez l'administrateur`)
                                      }
                                    } catch (error) {
                                      console.error('Erreur lors de l\'ouverture du PDF:', error)
                                      alert('Erreur lors de l\'ouverture du PDF. Vérifiez votre connexion.')
                                    }
                                  }}
                                  className="text-green-600 hover:text-green-800 text-sm font-medium"
                                >
                                  Voir PDF
                                </button>
                              ) : (
                                <span className="text-gray-500 text-sm">Aucun PDF</span>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Message si aucun PDF */}
                      {(!tenant.lease?.leasePdf && (!tenant.leaseRenewals || tenant.leaseRenewals.every(r => !r.renewalPdf))) && (
                        <div className="text-center py-4 text-gray-500 text-sm">
                          Aucun PDF de bail disponible pour ce locataire
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )
          })()}
        </div>
      </div>

      {/* Section Historique des Baux */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Historique des Baux
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Tous les baux et renouvellements pour cette unité (actifs et inactifs)
          </p>
        </div>
        
        <div className="p-6">
          {(() => {
            const unitAssignments = assignments.filter(a => a.unitId === unitId)
            const tenantsWithLeases = []
            
            unitAssignments.forEach(assignment => {
              const tenant = allTenants.find(t => t.id === assignment.tenantId)
              if (tenant) {
                tenantsWithLeases.push(tenant)
              }
            })
            
            if (tenantsWithLeases.length === 0) {
              return (
                <div className="text-center py-8">
                  <p className="text-gray-500">Aucun locataire assigné à cette unité</p>
                </div>
              )
            }
            
            return (
              <div className="space-y-6">
                {tenantsWithLeases.map((tenant, index) => (
                  <div key={tenant.id} className="border rounded-lg p-4">
                    <h4 className="text-lg font-medium text-gray-900 mb-4">
                      {tenant.name}
                    </h4>
                    
                    <div className="space-y-4">
                      {/* Bail principal */}
                      {tenant.lease && (
                        <div className="bg-gray-50 p-4 rounded">
                          <h5 className="text-md font-medium text-gray-900 mb-2">Bail Principal</h5>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                            <div>
                              <span className="font-medium">Début:</span> {tenant.lease.startDate}
                            </div>
                            <div>
                              <span className="font-medium">Fin:</span> {tenant.lease.endDate}
                            </div>
                            <div>
                              <span className="font-medium">Loyer:</span> {formatCurrency(tenant.lease.monthlyRent)}
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {/* Renouvellements */}
                      {tenant.leaseRenewals && tenant.leaseRenewals.length > 0 && (
                        <div className="space-y-3">
                          <h5 className="text-md font-medium text-gray-900">Renouvellements</h5>
                          {tenant.leaseRenewals.map((renewal, renewalIndex) => (
                            <div key={renewal.id} className="bg-blue-50 p-4 rounded">
                              <h6 className="text-sm font-medium text-gray-900 mb-2">
                                Renouvellement {renewalIndex + 1}
                              </h6>
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                                <div>
                                  <span className="font-medium">Début:</span> {renewal.startDate}
                                </div>
                                <div>
                                  <span className="font-medium">Fin:</span> {renewal.endDate}
                                </div>
                                <div>
                                  <span className="font-medium">Loyer:</span> {formatCurrency(renewal.monthlyRent)}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )
          })()}
        </div>
      </div>
    </div>
  )
} 