import React, { useState, useEffect } from 'react'
import { Check, X, Calendar, DollarSign, Building, Users, ChevronLeft, ChevronRight, Edit3 } from 'lucide-react'
import api from '../services/api'

const RentPayments = () => {
  const [buildings, setBuildings] = useState([])
  const [selectedBuilding, setSelectedBuilding] = useState(null)
  const [leases, setLeases] = useState([])
  const [payments, setPayments] = useState({})
  // Initialiser avec 12 mois AVANT aujourd'hui
  const today = new Date()
  const twelveMonthsAgo = new Date(today.getFullYear(), today.getMonth() - 11, 1)
  const [displayYear, setDisplayYear] = useState(twelveMonthsAgo.getFullYear())
  const [displayMonth, setDisplayMonth] = useState(twelveMonthsAgo.getMonth() + 1)
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
      const buildingLeases = leasesList.filter(lease => 
        lease.locataire && 
        lease.locataire.unite && 
        lease.locataire.unite.id_immeuble === selectedBuilding.id_immeuble
      )
      
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

  // Générer les mois à afficher (12 mois à partir du mois sélectionné)
  const generateMonths = () => {
    const months = []
    const startDate = new Date(displayYear, displayMonth - 1, 1)
    const endDate = new Date(displayYear, displayMonth + 10, 1) // 12 mois à partir du mois sélectionné
    
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

  // Vérifier si le bail est actif pour un mois donné
  const isLeaseActiveForMonth = (lease, year, month) => {
    if (!lease.date_debut || !lease.date_fin) return false
    
    const leaseStart = new Date(lease.date_debut)
    const leaseEnd = new Date(lease.date_fin)
    const checkDate = new Date(year, month - 1, 1) // Premier jour du mois
    
    return checkDate >= leaseStart && checkDate <= leaseEnd
  }

  // Créer ou supprimer un paiement
  const togglePayment = async (leaseId, year, month, isPaid) => {
    try {
      const existingPayment = getPayment(leaseId, year, month)
      
      if (isPaid) {
        // Si on coche, créer le paiement (s'il n'existe pas déjà)
        if (!existingPayment) {
          await api.post('/api/paiements-loyers', {
            id_bail: leaseId,
            mois: month,
            annee: year
          })
        }
      } else {
        // Si on décoche, supprimer complètement le paiement
        if (existingPayment) {
          await api.delete(`/api/paiements-loyers/${existingPayment.id_paiement}`)
        }
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
      // Récupérer le paiement existant
      const existingPayment = getPayment(leaseId, year, month)
      
      if (existingPayment) {
        // Le paiement existe, l'afficher
        setShowDetails({
          payment: existingPayment,
          leaseId,
          year,
          month
        })
      } else {
        // Le paiement n'existe pas, on ne peut pas le modifier
        alert('Veuillez d\'abord cocher le paiement avant de le modifier.')
      }
    } catch (error) {
      console.error('Erreur lors de l\'ouverture des détails:', error)
    }
  }

  // Mettre à jour les détails d'un paiement
  const updatePaymentDetails = async (updatedPayment) => {
    try {
      // Envoyer seulement les champs modifiables
      const updateData = {
        date_paiement_reelle: updatedPayment.date_paiement_reelle,
        montant_paye: updatedPayment.montant_paye,
        notes: updatedPayment.notes
      }
      
      await api.put(`/api/paiements-loyers/${updatedPayment.id_paiement}`, updateData)
      setShowDetails(null)
      await loadPaymentsForLeases(leases)
    } catch (error) {
      console.error('Erreur lors de la mise à jour des détails:', error)
      alert('Erreur lors de la mise à jour du paiement')
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
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="w-full">
        {/* En-tête */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <DollarSign className="h-8 w-8 text-green-600 dark:text-green-400" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Suivi des Paiements de Loyers</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Gérez et suivez les paiements de loyers par immeuble et par mois
          </p>
        </div>

        {/* Sélection de l'immeuble */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
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
                    : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
                }`}
              >
                {building.nom_immeuble}
              </button>
            ))}
          </div>
        </div>

        {/* Navigation temporelle */}
        {selectedBuilding && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-4">
              <Calendar className="h-5 w-5" />
              Navigation temporelle
            </h3>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Année:</label>
                <select
                  value={displayYear}
                  onChange={(e) => setDisplayYear(parseInt(e.target.value))}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  {Array.from({ length: 10 }, (_, i) => {
                    const year = new Date().getFullYear() - 5 + i
                    return (
                      <option key={year} value={year}>
                        {year}
                      </option>
                    )
                  })}
                </select>
              </div>
              
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Mois de début:</label>
                <select
                  value={displayMonth}
                  onChange={(e) => setDisplayMonth(parseInt(e.target.value))}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  {Array.from({ length: 12 }, (_, i) => {
                    const month = i + 1
                    const date = new Date(2024, month - 1, 1)
                    return (
                      <option key={month} value={month}>
                        {date.toLocaleDateString('fr-CA', { month: 'long' })}
                      </option>
                    )
                  })}
                </select>
              </div>
              
              <button
                onClick={() => {
                  const today = new Date()
                  const twelveMonthsAgo = new Date(today.getFullYear(), today.getMonth() - 11, 1)
                  setDisplayYear(twelveMonthsAgo.getFullYear())
                  setDisplayMonth(twelveMonthsAgo.getMonth() + 1)
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                12 derniers mois
              </button>
            </div>
            
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-3">
              Affichage de 12 mois à partir de {new Date(displayYear, displayMonth - 1, 1).toLocaleDateString('fr-CA', { month: 'long', year: 'numeric' })}
            </p>
          </div>
        )}

        {/* Tableau des paiements */}
        {selectedBuilding && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <Users className="h-5 w-5" />
                Paiements - {selectedBuilding.nom_immeuble}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {leases.length} unité(s) avec bail actif
              </p>
            </div>

            {leases.length === 0 ? (
              <div className="p-12 text-center">
                <Users className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">Aucune unité avec bail actif dans cet immeuble</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Unité
                      </th>
                      {months.map(({ year, month, label }) => (
                        <th key={`${year}-${month}`} className="px-3 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider min-w-[80px]">
                          {label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {leases.map(lease => (
                      <tr key={lease.id_bail}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {lease.locataire?.unite?.adresse_unite || 'N/A'}
                          </div>
                        </td>
                        {months.map(({ year, month }) => {
                          const payment = getPayment(lease.id_bail, year, month)
                          const isPaid = !!payment  // Si le paiement existe, il est payé
                          const isActive = isLeaseActiveForMonth(lease, year, month)
                          
                          return (
                            <td key={`${lease.id_bail}-${year}-${month}`} className="px-3 py-4 text-center">
                              {isActive ? (
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
                              ) : (
                                <div className="text-gray-300">-</div>
                              )}
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
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Détails du Paiement
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Date de paiement réelle
                  </label>
                  <input
                    type="date"
                    value={showDetails.payment.date_paiement_reelle ? showDetails.payment.date_paiement_reelle.split('T')[0] : ''}
                    onChange={(e) => setShowDetails({
                      ...showDetails,
                      payment: {
                        ...showDetails.payment,
                        date_paiement_reelle: e.target.value
                      }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
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
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
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
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowDetails(null)}
                  className="px-4 py-2 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
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
