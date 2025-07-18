import React, { useState, useEffect } from 'react'
import { Users, Calendar, DollarSign, Edit3, Trash2, Eye, X, Plus, Search, ExternalLink } from 'lucide-react'
import { buildingsService, reportsService, tenantsService, assignmentsService } from '../services/api'
import { parseAddressAndGenerateUnits } from '../types/unit'
import { useNavigate } from 'react-router-dom'
import DeleteConfirmationModal from './DeleteConfirmationModal'

export default function UnitReports({ selectedYear }) {
  const [buildings, setBuildings] = useState([])
  const [units, setUnits] = useState([])
  const [reports, setReports] = useState([])
  const [selectedUnit, setSelectedUnit] = useState(null)
  const [editingReport, setEditingReport] = useState(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [reportToDelete, setReportToDelete] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [assignments, setAssignments] = useState([])
  const [allTenants, setAllTenants] = useState([])
  const [autoGenerating, setAutoGenerating] = useState(false)
  const navigate = useNavigate()

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

  const paymentMethods = [
    'Comptant',
    'Chèque',
    'Virement bancaire',
    'Carte de crédit',
    'Prélèvement automatique',
    'Autre'
  ]

  useEffect(() => {
    loadBuildings()
    loadReports()
    loadAssignments()
    loadTenants()
  }, [])

  // Génération automatique des rapports manquants quand toutes les données sont chargées
  useEffect(() => {
    if (!loading && units.length > 0 && assignments.length > 0 && allTenants.length > 0 && reports.length >= 0) {
      console.log('🚀 Déclenchement génération automatique:', {
        loading,
        unitsCount: units.length,
        assignmentsCount: assignments.length,
        tenantsCount: allTenants.length,
        reportsCount: reports.length,
        selectedYear
      })
      autoGenerateMissingReports()
    } else {
      console.log('⏸️ Génération automatique en attente:', {
        loading,
        unitsCount: units.length,
        assignmentsCount: assignments.length,
        tenantsCount: allTenants.length,
        reportsCount: reports.length
      })
    }
    
    // Écouter l'événement de suppression de locataire
    const handleTenantDeleted = (event) => {
      console.log(`📢 UnitReports: Événement tenantDeleted reçu:`, event.detail)
      console.log(`🔄 UnitReports: Rechargement des données suite à la suppression...`)
      loadAssignments()
      loadTenants()
      loadReports() // Les rapports pourraient aussi être affectés
    }
    
    window.addEventListener('tenantDeleted', handleTenantDeleted)
    
    return () => {
      window.removeEventListener('tenantDeleted', handleTenantDeleted)
    }
  }, [loading, units, assignments, allTenants, reports, selectedYear])

  // Fonction pour générer automatiquement les rapports manquants
  const autoGenerateMissingReports = async () => {
    try {
      setAutoGenerating(true)
      console.log('🔍 Vérification des rapports manquants pour', selectedYear)
      
      let newReportsCreated = 0
      
      for (const unit of units) {
        // Récupérer les assignations pour cette unité
        const unitAssignments = assignments.filter(a => a.unitId === unit.id)
        
        if (unitAssignments.length === 0) {
          console.log(`⏭️ Aucun locataire assigné à ${unit.buildingName} - ${unit.unitNumber}`)
          continue
        }

        // Pour chaque assignation, vérifier les rapports manquants
        for (const assignment of unitAssignments) {
          const tenant = allTenants.find(t => t.id === assignment.tenantId)
          if (!tenant) continue

          // Récupérer les dates de bail depuis la fiche locataire (nouveau système)
          let leaseStart, leaseEnd, rentAmount, paymentMethod
          
          // Vérifier s'il y a un renouvellement actif
          if (tenant.leaseRenewal?.isActive && tenant.leaseRenewal?.startDate && tenant.leaseRenewal?.endDate) {
            leaseStart = tenant.leaseRenewal.startDate
            leaseEnd = tenant.leaseRenewal.endDate
            rentAmount = tenant.leaseRenewal.monthlyRent || tenant.lease?.monthlyRent || 0
            paymentMethod = tenant.lease?.paymentMethod || 'Virement bancaire'
            console.log(`📋 Utilisation renouvellement de bail pour ${tenant.name}: ${leaseStart} - ${leaseEnd}`)
          } else if (tenant.lease?.startDate && tenant.lease?.endDate) {
            leaseStart = tenant.lease.startDate
            leaseEnd = tenant.lease.endDate
            rentAmount = tenant.lease.monthlyRent || 0
            paymentMethod = tenant.lease.paymentMethod || 'Virement bancaire'
            console.log(`📋 Utilisation bail principal pour ${tenant.name}: ${leaseStart} - ${leaseEnd}`)
          } else {
            // Fallback vers ancien système (unité/assignment) si pas de données dans fiche locataire
            leaseStart = unit.rental?.leaseStart || assignment.tenantData?.leaseStart
            leaseEnd = unit.rental?.leaseEnd || assignment.tenantData?.leaseEnd
            rentAmount = unit.rental?.monthlyRent || 0
            paymentMethod = tenant.paymentMethod || 'Virement bancaire'
            console.log(`📋 Fallback ancien système pour ${tenant.name}: ${leaseStart} - ${leaseEnd}`)
          }

          if (!leaseStart || !leaseEnd) {
            console.log(`⚠️ Dates de bail manquantes pour ${tenant.name} dans ${unit.buildingName} - ${unit.unitNumber}`)
            continue
          }

          // Générer les mois pour l'année sélectionnée
          const startDate = new Date(leaseStart)
          const endDate = new Date(leaseEnd)
          const monthsToCheck = []

          let currentDate = new Date(startDate.getFullYear(), startDate.getMonth(), 1)
          while (currentDate <= endDate) {
            if (currentDate.getFullYear() === selectedYear) {
              monthsToCheck.push({
                year: currentDate.getFullYear(),
                month: currentDate.getMonth() + 1
              })
            }
            currentDate.setMonth(currentDate.getMonth() + 1)
          }

          // Créer les rapports manquants
          for (const monthData of monthsToCheck) {
            const existingReport = reports.find(r => 
              r.unitId === unit.id && 
              r.year === monthData.year && 
              r.month === monthData.month
            )

            if (!existingReport) {
              console.log(`✨ Création automatique: ${tenant.name} - ${unit.buildingName} ${unit.unitNumber} - ${monthData.month}/${monthData.year}`)
              
              const reportData = {
                unitId: unit.id,
                year: monthData.year,
                month: monthData.month,
                tenantName: tenant.name,
                paymentMethod: paymentMethod,
                isHeatedLit: unit.amenities?.electricity || false,
                isFurnished: unit.amenities?.furnished || false,
                wifiIncluded: unit.amenities?.wifi || false,
                rentAmount: rentAmount,
                startDate: leaseStart,
                endDate: leaseEnd
              }

              await reportsService.createUnitReport(reportData)
              newReportsCreated++
            }
          }
        }
      }

      if (newReportsCreated > 0) {
        console.log(`🎉 ${newReportsCreated} nouveaux rapports créés automatiquement`)
        // Recharger les rapports après création
        await loadReports()
      } else {
        console.log('✅ Tous les rapports sont à jour')
      }

    } catch (error) {
      console.error('❌ Erreur lors de la génération automatique:', error)
    } finally {
      setAutoGenerating(false)
    }
  }

  // Fonction pour regénérer manuellement (remplace l'ancienne génération)
  const regenerateReportsForUnit = async (unit) => {
    try {
      console.log('🔄 Régénération manuelle pour:', unit)
      
      // Récupérer les assignations pour cette unité
      const unitAssignments = assignments.filter(a => a.unitId === unit.id)
      
      if (unitAssignments.length === 0) {
        alert('Aucun locataire assigné à cette unité')
        return
      }

      let reportsCreated = 0

      // Pour chaque assignation, regénérer les rapports
      for (const assignment of unitAssignments) {
        const tenant = allTenants.find(t => t.id === assignment.tenantId)
        if (!tenant) continue

        const leaseStart = unit.rental?.leaseStart || assignment.tenantData?.leaseStart
        const leaseEnd = unit.rental?.leaseEnd || assignment.tenantData?.leaseEnd

        if (!leaseStart || !leaseEnd) {
          console.warn('Dates de bail manquantes pour:', tenant.name)
          continue
        }

        // Générer les mois pour l'année sélectionnée
        const startDate = new Date(leaseStart)
        const endDate = new Date(leaseEnd)
        const monthsToGenerate = []

        let currentDate = new Date(startDate.getFullYear(), startDate.getMonth(), 1)
        while (currentDate <= endDate) {
          if (currentDate.getFullYear() === selectedYear) {
            monthsToGenerate.push({
              year: currentDate.getFullYear(),
              month: currentDate.getMonth() + 1
            })
          }
          currentDate.setMonth(currentDate.getMonth() + 1)
        }

        // Créer/mettre à jour les rapports pour chaque mois
        for (const monthData of monthsToGenerate) {
          const reportData = {
            unitId: unit.id,
            year: monthData.year,
            month: monthData.month,
            tenantName: tenant.name,
            paymentMethod: tenant.paymentMethod || 'Virement bancaire',
            isHeatedLit: unit.amenities?.electricity || false,
            isFurnished: unit.amenities?.furnished || false,
            wifiIncluded: unit.amenities?.wifi || false,
            rentAmount: unit.rental?.monthlyRent || 0,
            startDate: leaseStart,
            endDate: leaseEnd
          }

          await reportsService.createUnitReport(reportData)
          reportsCreated++
        }
      }

      // Recharger les rapports
      await loadReports()
      alert(`${reportsCreated} rapport(s) régénéré(s) pour ${selectedYear} !`)

    } catch (error) {
      console.error('Error regenerating reports:', error)
      alert('Erreur lors de la régénération des rapports')
    }
  }

  const loadBuildings = async () => {
    try {
      const response = await buildingsService.getBuildings()
      const buildingsData = response.data || []
      setBuildings(buildingsData)
      
      // Générer toutes les unités
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

  const loadReports = async () => {
    try {
      setLoading(true)
      const response = await reportsService.getUnitReports()
      setReports(response.data || [])
    } catch (error) {
      console.error('Error loading unit reports:', error)
    } finally {
      setLoading(false)
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
    }
  }

  const getReportsForUnit = (unitId, year) => {
    return reports.filter(r => r.unitId === unitId && r.year === year)
  }

  const handleAddReport = async (unit) => {
    console.log('Adding report for unit:', unit)
    console.log('Unit rental info:', unit.rental)
    console.log('Unit amenities:', unit.amenities)
    
    // Récupérer les assignations pour cette unité
    const unitAssignments = assignments.filter(a => a.unitId === unit.id)
    console.log('Unit assignments:', unitAssignments)
    
    // Récupérer le premier locataire assigné pour pré-remplir
    let tenantName = ''
    let paymentMethod = 'Virement bancaire'
    let startDate = ''
    let endDate = ''
    
    if (unitAssignments.length > 0) {
      const assignment = unitAssignments[0]
      const tenant = allTenants.find(t => t.id === assignment.tenantId)
      if (tenant) {
        tenantName = tenant.name
        paymentMethod = tenant.paymentMethod || 'Virement bancaire'
      }
      
      // Utiliser les dates de bail de l'unité ou de l'assignation
      startDate = unit.rental?.leaseStart || assignment.tenantData?.leaseStart || ''
      endDate = unit.rental?.leaseEnd || assignment.tenantData?.leaseEnd || ''
    }
    
    setEditingReport({
      unitId: unit.id,
      unitName: `${unit.buildingName} - ${unit.unitNumber}`,
      year: selectedYear,
      month: 1,
      // Données automatiques depuis la fiche unité
      tenantName: tenantName,
      paymentMethod: paymentMethod,
      isHeatedLit: unit.amenities?.electricity || false,
      isFurnished: unit.amenities?.furnished || false,
      wifiIncluded: unit.amenities?.wifi || false,
      rentAmount: unit.rental?.monthlyRent || 0,
      startDate: startDate,
      endDate: endDate,
      id: null
    })
    setSelectedUnit(unit)
  }

  const handleEditReport = (unit, report) => {
    console.log('Editing report:', report)
    console.log('Unit data:', unit)
    
    setEditingReport({
      unitId: unit.id,
      unitName: `${unit.buildingName} - ${unit.unitNumber}`,
      year: report.year,
      month: report.month,
      // Utiliser les données du rapport existant, sinon fallback sur unité
      tenantName: report.tenantName || '',
      paymentMethod: report.paymentMethod || 'Virement bancaire',
      isHeatedLit: report.isHeatedLit !== undefined ? report.isHeatedLit : (unit.amenities?.electricity || false),
      isFurnished: report.isFurnished !== undefined ? report.isFurnished : (unit.amenities?.furnished || false),
      wifiIncluded: report.wifiIncluded !== undefined ? report.wifiIncluded : (unit.amenities?.wifi || false),
      rentAmount: report.rentAmount || unit.rental?.monthlyRent || 0,
      startDate: report.startDate || unit.rental?.leaseStart || '',
      endDate: report.endDate || unit.rental?.leaseEnd || '',
      id: report.id
    })
    setSelectedUnit(unit)
  }

  const handleSaveReport = async () => {
    try {
      const reportData = {
        unitId: editingReport.unitId,
        year: editingReport.year,
        month: editingReport.month,
        tenantName: editingReport.tenantName,
        paymentMethod: editingReport.paymentMethod,
        isHeatedLit: editingReport.isHeatedLit,
        isFurnished: editingReport.isFurnished,
        wifiIncluded: editingReport.wifiIncluded,
        rentAmount: editingReport.rentAmount,
        startDate: editingReport.startDate,
        endDate: editingReport.endDate,
        // Inclure l'ID si c'est une modification
        ...(editingReport.id && { id: editingReport.id })
      }
      
      console.log('Saving unit report with data:', reportData)
      await reportsService.createUnitReport(reportData)
      await loadReports()
      setEditingReport(null)
      setSelectedUnit(null)
    } catch (error) {
      console.error('Error saving unit report:', error)
      alert('Erreur lors de la sauvegarde du rapport')
    }
  }

  const handleDeleteReport = async () => {
    try {
      await reportsService.deleteUnitReport(reportToDelete.id)
      await loadReports()
      setShowDeleteModal(false)
      setReportToDelete(null)
    } catch (error) {
      console.error('Error deleting unit report:', error)
      alert('Erreur lors de la suppression du rapport')
    }
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

  const getMonthName = (monthNumber) => {
    const month = months.find(m => m.value === monthNumber)
    return month ? month.name : monthNumber
  }

  // Filtrer les unités selon le terme de recherche
  const filteredUnits = units.filter(unit => {
    const searchLower = searchTerm.toLowerCase()
    const unitName = `${unit.buildingName} - ${unit.unitNumber}`.toLowerCase()
    const address = formatAddress(unit.address).toLowerCase()
    return unitName.includes(searchLower) || address.includes(searchLower)
  })

  if (loading || autoGenerating) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">
            {autoGenerating ? 'Génération automatique des rapports...' : 'Chargement des rapports d\'unités...'}
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
              
              {/* Indicateur de génération automatique */}
              <div className="text-xs text-gray-500 max-w-sm">
                {autoGenerating ? (
                  <div className="flex items-center text-blue-600">
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600 mr-2"></div>
                    <strong>🤖 Génération automatique en cours...</strong>
                  </div>
                ) : (
                  <div>
                    <strong>🤖 Génération automatique activée !</strong> Les rapports se créent automatiquement quand vous avez des unités avec locataires et dates de bail.
                    <br />
                    <span className="text-green-600">Cliquez sur "Voir détails" pour consulter ou modifier les rapports.</span>
                  </div>
                )}
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
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUnits.map((unit) => {
                const unitReports = getReportsForUnit(unit.id, selectedYear)
                const totalRevenue = unitReports.reduce((sum, report) => sum + (report.rentAmount || 0), 0)
                
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
                        {unitReports.length} mois documenté{unitReports.length > 1 ? 's' : ''}
                      </div>
                      {unitReports.length > 0 && (
                        <div className="text-xs text-gray-500">
                          {unitReports.map(r => getMonthName(r.month)).join(', ')}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(totalRevenue)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleAddReport(unit)}
                          className="text-blue-600 hover:text-blue-900 flex items-center"
                        >
                          <Plus className="h-4 w-4 mr-1" />
                          Ajouter
                        </button>
                        <button
                          onClick={() => navigate(`/unit-reports/${unit.id}/${selectedYear}`)}
                          className="text-green-600 hover:text-green-900 flex items-center"
                        >
                          <ExternalLink className="h-4 w-4 mr-1" />
                          Voir détails
                        </button>
                      </div>
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

      {/* Formulaire d'édition */}
      {editingReport && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Rapport {editingReport.unitName} - {getMonthName(editingReport.month)} {editingReport.year}
              </h3>
              <button
                onClick={() => {
                  setEditingReport(null)
                  if (!selectedUnit) setSelectedUnit(null)
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Mois</label>
                  <select
                    value={editingReport.month}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, month: parseInt(e.target.value) }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    {months.map(month => (
                      <option key={month.value} value={month.value}>
                        {month.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Nom du locataire</label>
                  <input
                    type="text"
                    value={editingReport.tenantName}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, tenantName: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Nom complet du locataire"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Méthode de paiement</label>
                  <select
                    value={editingReport.paymentMethod}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, paymentMethod: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Sélectionnez...</option>
                    {paymentMethods.map(method => (
                      <option key={method} value={method}>
                        {method}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Montant du loyer</label>
                  <input
                    type="number"
                    step="0.01"
                    value={editingReport.rentAmount}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, rentAmount: parseFloat(e.target.value) || 0 }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Date de début</label>
                  <input
                    type="date"
                    value={editingReport.startDate}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, startDate: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Date de fin</label>
                  <input
                    type="date"
                    value={editingReport.endDate}
                    onChange={(e) => setEditingReport(prev => ({ ...prev, endDate: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Conditions spéciales */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Conditions spéciales</label>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="heatedLit"
                      checked={editingReport.isHeatedLit}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, isHeatedLit: e.target.checked }))}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="heatedLit" className="ml-2 block text-sm text-gray-900">
                      Chauffé-éclairé
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="furnished"
                      checked={editingReport.isFurnished}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, isFurnished: e.target.checked }))}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="furnished" className="ml-2 block text-sm text-gray-900">
                      Meublé
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="wifiIncluded"
                      checked={editingReport.wifiIncluded}
                      onChange={(e) => setEditingReport(prev => ({ ...prev, wifiIncluded: e.target.checked }))}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="wifiIncluded" className="ml-2 block text-sm text-gray-900">
                      WiFi inclus
                    </label>
                  </div>
                </div>
              </div>

              {/* Boutons d'action */}
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    setEditingReport(null)
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  onClick={handleSaveReport}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  Sauvegarder
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de confirmation de suppression */}
      <DeleteConfirmationModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false)
          setReportToDelete(null)
        }}
        onConfirm={handleDeleteReport}
        title="Supprimer le rapport"
        message={`Êtes-vous sûr de vouloir supprimer le rapport de ${getMonthName(reportToDelete?.month)} ${reportToDelete?.year} ? Cette action est irréversible.`}
      />
    </div>
  )
} 