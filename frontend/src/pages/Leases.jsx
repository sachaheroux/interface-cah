import React, { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Calendar, DollarSign, FileText, AlertCircle, Home, User } from 'lucide-react'
import LeaseForm from '../components/LeaseForm'

const Leases = () => {
  const [leases, setLeases] = useState([])
  const [tenants, setTenants] = useState([])
  const [units, setUnits] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [selectedLease, setSelectedLease] = useState(null)
  const [selectedTenant, setSelectedTenant] = useState(null)
  const [selectedUnit, setSelectedUnit] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')

  // Charger les données
  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [leasesRes, tenantsRes, unitsRes] = await Promise.all([
        fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/leases`),
        fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/tenants`),
        fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/units`)
      ])

      const [leasesData, tenantsData, unitsData] = await Promise.all([
        leasesRes.json(),
        tenantsRes.json(),
        unitsRes.json()
      ])

      setLeases(leasesData.data || [])
      setTenants(tenantsData.data || [])
      setUnits(unitsData.data || [])
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
    } finally {
      setLoading(false)
    }
  }

  // Filtrer les baux
  const filteredLeases = leases.filter(lease => {
    const tenant = tenants.find(t => t.id_locataire === lease.id_locataire)
    const unit = units.find(u => u.id_unite === lease.id_unite)
    
    const matchesSearch = !searchTerm || 
      (tenant && `${tenant.nom} ${tenant.prenom}`.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (unit && unit.adresse_unite.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesStatus = filterStatus === 'all' || 
      (filterStatus === 'active' && isLeaseActive(lease)) ||
      (filterStatus === 'expired' && isLeaseExpired(lease)) ||
      (filterStatus === 'upcoming' && isLeaseUpcoming(lease))
    
    return matchesSearch && matchesStatus
  })

  // Vérifier si un bail est actif
  const isLeaseActive = (lease) => {
    const now = new Date()
    const startDate = new Date(lease.date_debut)
    const endDate = new Date(lease.date_fin)
    return startDate <= now && endDate >= now
  }

  // Vérifier si un bail est expiré
  const isLeaseExpired = (lease) => {
    const now = new Date()
    const endDate = new Date(lease.date_fin)
    return endDate < now
  }

  // Vérifier si un bail est à venir
  const isLeaseUpcoming = (lease) => {
    const now = new Date()
    const startDate = new Date(lease.date_debut)
    return startDate > now
  }

  // Obtenir le statut d'un bail
  const getLeaseStatus = (lease) => {
    if (isLeaseActive(lease)) return { text: 'Actif', color: 'bg-green-100 text-green-800' }
    if (isLeaseExpired(lease)) return { text: 'Expiré', color: 'bg-red-100 text-red-800' }
    if (isLeaseUpcoming(lease)) return { text: 'À venir', color: 'bg-blue-100 text-blue-800' }
    return { text: 'Inconnu', color: 'bg-gray-100 text-gray-800' }
  }

  // Formater une date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-CA')
  }

  // Formater un montant
  const formatAmount = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount)
  }

  // Ouvrir le formulaire de création
  const handleCreateLease = () => {
    setSelectedLease(null)
    setSelectedTenant(null)
    setSelectedUnit(null)
    setShowForm(true)
  }

  // Ouvrir le formulaire de modification
  const handleEditLease = (lease) => {
    const tenant = tenants.find(t => t.id_locataire === lease.id_locataire)
    const unit = units.find(u => u.id_unite === lease.id_unite)
    
    setSelectedLease(lease)
    setSelectedTenant(tenant)
    setSelectedUnit(unit)
    setShowForm(true)
  }

  // Supprimer un bail
  const handleDeleteLease = async (lease) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce bail ?')) {
      return
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/leases/${lease.id_bail}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setLeases(prev => prev.filter(l => l.id_bail !== lease.id_bail))
        console.log('✅ Bail supprimé avec succès')
      } else {
        console.error('❌ Erreur lors de la suppression')
      }
    } catch (error) {
      console.error('❌ Erreur lors de la suppression:', error)
    }
  }

  // Sauvegarder un bail
  const handleSaveLease = () => {
    loadData()
    setShowForm(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestion des baux</h1>
          <p className="text-gray-600">Gérez les baux de vos locataires</p>
        </div>
        <button
          onClick={handleCreateLease}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Nouveau bail</span>
        </button>
      </div>

      {/* Filtres */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Rechercher
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Nom du locataire ou adresse..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Statut
            </label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">Tous les baux</option>
              <option value="active">Actifs</option>
              <option value="expired">Expirés</option>
              <option value="upcoming">À venir</option>
            </select>
          </div>
        </div>
      </div>

      {/* Liste des baux */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {filteredLeases.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun bail trouvé</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || filterStatus !== 'all' 
                ? 'Aucun bail ne correspond à vos critères de recherche.'
                : 'Commencez par créer votre premier bail.'
              }
            </p>
            {!searchTerm && filterStatus === 'all' && (
              <button
                onClick={handleCreateLease}
                className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
              >
                Créer un bail
              </button>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredLeases.map((lease) => {
              const tenant = tenants.find(t => t.id_locataire === lease.id_locataire)
              const unit = units.find(u => u.id_unite === lease.id_unite)
              const status = getLeaseStatus(lease)

              return (
                <div key={lease.id_bail} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-medium text-gray-900">
                          {tenant ? `${tenant.nom} ${tenant.prenom}` : 'Locataire inconnu'}
                        </h3>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${status.color}`}>
                          {status.text}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
                        <div className="flex items-center">
                          <Home className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{unit ? unit.adresse_unite : 'Unité inconnue'}</span>
                        </div>
                        
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{formatDate(lease.date_debut)} - {formatDate(lease.date_fin)}</span>
                        </div>
                        
                        <div className="flex items-center">
                          <DollarSign className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{formatAmount(lease.prix_loyer)}/mois</span>
                        </div>
                        
                        <div className="flex items-center">
                          <FileText className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{lease.methode_paiement}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => handleEditLease(lease)}
                        className="text-primary-600 hover:text-primary-700 p-2 rounded-lg hover:bg-primary-50"
                        title="Modifier"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteLease(lease)}
                        className="text-red-600 hover:text-red-700 p-2 rounded-lg hover:bg-red-50"
                        title="Supprimer"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Formulaire de bail */}
      {showForm && (
        <LeaseForm
          isOpen={showForm}
          onClose={() => setShowForm(false)}
          onSave={handleSaveLease}
          tenant={selectedTenant}
          unit={selectedUnit}
          lease={selectedLease}
        />
      )}
    </div>
  )
}

export default Leases
