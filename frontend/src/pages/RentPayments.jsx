import React, { useState, useEffect } from 'react'
import { Check, X, Calendar, DollarSign, Building, Users, ChevronLeft, ChevronRight, Edit3 } from 'lucide-react'
import api from '../services/api'

const RentPayments = () => {
  const [buildings, setBuildings] = useState([])
  const [selectedBuilding, setSelectedBuilding] = useState(null)
  const [leases, setLeases] = useState([])
  const [payments, setPayments] = useState({})
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear())
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1)
  const [loading, setLoading] = useState(false)
  const [showDetails, setShowDetails] = useState(null)

  // Charger les immeubles
  const loadBuildings = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/buildings')
      const buildingsList = Array.isArray(response.data) ? response.data : (response.data.data || [])
      setBuildings(buildingsList)
      if (buildingsList.length > 0) {
        setSelectedBuilding(buildingsList[0])
      }
    } catch (error) {
      console.error('Erreur lors du chargement des immeubles:', error)
    } finally {
      setLoading(false)
    }
  }

  // Charger les baux pour l'immeuble sélectionné
  const loadLeases = async () => {
    if (!selectedBuilding) return
    
    try {
      setLoading(true)
      const response = await api.get('/api/leases')
      const leasesList = Array.isArray(response.data) ? response.data : (response.data.data || [])
      
      // Filtrer les baux pour l'immeuble sélectionné
      console.log('🔍 DEBUG - Tous les baux:', leasesList.length)
      console.log('🔍 DEBUG - Immeuble sélectionné:', selectedBuilding.id_immeuble)
      
      const buildingLeases = leasesList.filter(lease => {
        console.log('🔍 DEBUG - Bail:', lease.id_bail, 'Locataire:', lease.locataire)
        if (lease.locataire) {
          console.log('🔍 DEBUG - Unité:', lease.locataire.unite)
          if (lease.locataire.unite) {
            console.log('🔍 DEBUG - ID Immeuble:', lease.locataire.unite.id_immeuble, 'vs', selectedBuilding.id_immeuble)
          }
        }
        
        return lease.locataire && 
               lease.locataire.unite && 
               lease.locataire.unite.id_immeuble === selectedBuilding.id_immeuble
      })
      
      console.log('🔍 DEBUG - Baux filtrés pour l\'immeuble:', buildingLeases.length)
      setLeases(buildingLeases)
      
      // Charger les paiements pour chaque bail
      await loadPaymentsForLeases(buildingLeases)
    } catch (error) {
      console.error('Erreur lors du chargement des baux:', error)
    } finally {
      setLoading(false)
    }
  }

  // Charger les paiements pour les baux
  const loadPaymentsForLeases = async (leasesList) => {
    const paymentsData = {}
    
    for (const lease of leasesList) {
      try {
        const response = await api.get(`/api/paiements-loyers/bail/${lease.id_bail}`)
        paymentsData[lease.id_bail] = response.data.data || []
      } catch (error) {
        console.error(`Erreur lors du chargement des paiements pour le bail ${lease.id_bail}:`, error)
        paymentsData[lease.id_bail] = []
      }
    }
    
    setPayments(paymentsData)
  }

  // Charger les données au montage
  useEffect(() => {
    loadBuildings()
  }, [])

  useEffect(() => {
    if (selectedBuilding) {
      loadLeases()
    }
  }, [selectedBuilding])

  // Générer les mois à afficher (12 derniers mois + 3 mois futurs)
  const generateMonths = () => {
    const months = []
    const currentDate = new Date()
    const startDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 11, 1)
    const endDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 3, 1)
    
    let date = new Date(startDate)
    while (date <= endDate) {
      months.push({
        year: date.getFullYear(),
        month: date.getMonth() + 1,
        label: date.toLocaleDateString('fr-CA', { month: 'long', year: 'numeric' })
      })
      date.setMonth(date.getMonth() + 1)
    }
    
    return months
  }

  // Obtenir le paiement pour un bail et un mois donné
  const getPayment = (leaseId, year, month) => {
    const leasePayments = payments[leaseId] || []
    return leasePayments.find(p => p.annee === year && p.mois === month)
  }

  // Créer ou mettre à jour un paiement
  const togglePayment = async (leaseId, year, month, isPaid) => {
    try {
      const existingPayment = getPayment(leaseId, year, month)
      
      if (existingPayment) {
        // Mettre à jour le paiement existant
        await api.put(`/api/paiements-loyers/${existingPayment.id_paiement}`, {
          paye: isPaid
        })
      } else {
        // Créer un nouveau paiement
        await api.post('/api/paiements-loyers', {
          id_bail: leaseId,
          mois: month,
          annee: year,
          paye: isPaid
        })
      }
      
      // Recharger les paiements
      await loadPaymentsForLeases(leases)
    } catch (error) {
      console.error('Erreur lors de la mise à jour du paiement:', error)
    }
  }

  // Ouvrir les détails d'un paiement
  const openPaymentDetails = async (leaseId, year, month) => {
    try {
      const payment = await api.get(`/api/paiements-loyers/get-or-create?bail_id=${leaseId}&mois=${month}&annee=${year}`)
      setShowDetails({
        payment: payment.data,
        leaseId,
        year,
        month
      })
    } catch (error) {
      console.error('Erreur lors de l\'ouverture des détails:', error)
    }
  }

  // Mettre à jour les détails d'un paiement
  const updatePaymentDetails = async (updatedPayment) => {
    try {
      await api.put(`/api/paiements-loyers/${updatedPayment.id_paiement}`, updatedPayment)
      setShowDetails(null)
      await loadPaymentsForLeases(leases)
    } catch (error) {
      console.error('Erreur lors de la mise à jour des détails:', error)
    }
  }

  const months = generateMonths()

  if (loading && buildings.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des immeubles...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="w-full">
        {/* En-tête */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <DollarSign className="h-8 w-8 text-green-600" />
            <h1 className="text-3xl font-bold text-gray-900">Suivi des Paiements de Loyers</h1>
          </div>
          <p className="text-gray-600">
            Gérez et suivez les paiements de loyers par immeuble et par mois
          </p>
        </div>

        {/* Sélection de l'immeuble */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Building className="h-5 w-5" />
            Sélection de l'Immeuble
          </h2>
          
          <div className="flex flex-wrap gap-2">
            {buildings.map(building => (
              <button
                key={building.id_immeuble}
                onClick={() => setSelectedBuilding(building)}
                className={`px-4 py-2 rounded-lg border transition-colors ${
                  selectedBuilding?.id_immeuble === building.id_immeuble
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                {building.nom_immeuble}
              </button>
            ))}
          </div>
        </div>

        {/* Tableau des paiements */}
        {selectedBuilding && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Users className="h-5 w-5" />
                Paiements - {selectedBuilding.nom_immeuble}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {leases.length} locataire(s) actif(s)
              </p>
            </div>

            {leases.length === 0 ? (
              <div className="p-12 text-center">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Aucun locataire actif dans cet immeuble</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Locataire / Unité
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Loyer
                      </th>
                      {months.map(({ year, month, label }) => (
                        <th key={`${year}-${month}`} className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[80px]">
                          {label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {leases.map(lease => (
                      <tr key={lease.id_bail}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {lease.locataire?.nom_complet || 'N/A'}
                            </div>
                            <div className="text-sm text-gray-500">
                              {lease.locataire?.unite?.adresse_unite || 'N/A'}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${lease.prix_loyer?.toLocaleString() || '0'}
                        </td>
                        {months.map(({ year, month }) => {
                          const payment = getPayment(lease.id_bail, year, month)
                          const isPaid = payment?.paye || false
                          
                          return (
                            <td key={`${lease.id_bail}-${year}-${month}`} className="px-3 py-4 text-center">
                              <div className="flex flex-col items-center gap-1">
                                <button
                                  onClick={() => togglePayment(lease.id_bail, year, month, !isPaid)}
                                  className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                                    isPaid 
                                      ? 'bg-green-500 text-white hover:bg-green-600' 
                                      : 'bg-gray-200 text-gray-400 hover:bg-gray-300'
                                  }`}
                                >
                                  {isPaid ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                                </button>
                                <button
                                  onClick={() => openPaymentDetails(lease.id_bail, year, month)}
                                  className="text-xs text-gray-500 hover:text-blue-600"
                                >
                                  <Edit3 className="h-3 w-3" />
                                </button>
                              </div>
                            </td>
                          )
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Modal des détails */}
        {showDetails && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Détails du Paiement
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date de paiement réelle
                  </label>
                  <input
                    type="date"
                    value={showDetails.payment.date_paiement_reelle || ''}
                    onChange={(e) => setShowDetails({
                      ...showDetails,
                      payment: {
                        ...showDetails.payment,
                        date_paiement_reelle: e.target.value
                      }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Montant payé
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={showDetails.payment.montant_paye || ''}
                    onChange={(e) => setShowDetails({
                      ...showDetails,
                      payment: {
                        ...showDetails.payment,
                        montant_paye: parseFloat(e.target.value) || null
                      }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes
                  </label>
                  <textarea
                    value={showDetails.payment.notes || ''}
                    onChange={(e) => setShowDetails({
                      ...showDetails,
                      payment: {
                        ...showDetails.payment,
                        notes: e.target.value
                      }
                    })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowDetails(null)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  onClick={() => updatePaymentDetails(showDetails.payment)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Sauvegarder
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default RentPayments
