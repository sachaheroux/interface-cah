import React, { useState, useEffect } from 'react'
import { FileText, Plus, Search, Calendar, DollarSign, User, Home, Edit, Trash2, Eye } from 'lucide-react'
import LeaseForm from '../components/LeaseForm'

export default function Leases() {
  const [leases, setLeases] = useState([])
  const [filteredLeases, setFilteredLeases] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  // États pour les modales
  const [selectedLease, setSelectedLease] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    fetchLeases()
  }, [])

  // Filtrer les baux
  useEffect(() => {
    let filtered = leases

    if (searchTerm) {
      filtered = filtered.filter(lease => 
        lease.locataire?.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lease.locataire?.prenom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lease.unite?.adresse_unite?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    setFilteredLeases(filtered)
  }, [leases, searchTerm])

  const fetchLeases = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/leases`)
      if (response.ok) {
        const data = await response.json()
        setLeases(data.data || [])
      }
    } catch (error) {
      console.error('Erreur lors du chargement des baux:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleViewLease = (lease) => {
    setSelectedLease(lease)
    setShowDetails(true)
  }

  const handleEditLease = (lease) => {
    setSelectedLease(lease)
    setShowForm(true)
  }

  const handleSaveLease = () => {
    fetchLeases()
    setShowForm(false)
    setSelectedLease(null)
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setSelectedLease(null)
  }

  const handleCloseDetails = () => {
    setShowDetails(false)
    setSelectedLease(null)
  }

  const handleDeleteLease = async (lease) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer ce bail ?`)) {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/leases/${lease.id_bail}`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          setLeases(prev => prev.filter(l => l.id_bail !== lease.id_bail))
          console.log('✅ Bail supprimé avec succès')
        } else {
          console.error('❌ Erreur lors de la suppression du bail')
        }
      } catch (error) {
        console.error('❌ Erreur lors de la suppression:', error)
      }
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Non spécifié'
    return new Date(dateString).toLocaleDateString('fr-CA')
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount || 0)
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
        <div className="flex items-center space-x-3">
          <FileText className="h-8 w-8 text-primary-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Gestion des Baux</h1>
            <p className="text-gray-600">
              Gérez tous les baux de vos locataires
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Nouveau bail</span>
        </button>
      </div>

      {/* Filtres */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Rechercher par locataire ou unité..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Liste des baux */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {filteredLeases.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {leases.length === 0 ? 'Aucun bail' : 'Aucun bail correspondant aux filtres'}
            </h3>
            <p className="text-gray-600 mb-4">
              {leases.length === 0
                ? 'Commencez par créer votre premier bail.'
                : 'Essayez de modifier vos critères de recherche.'
              }
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              Créer un bail
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredLeases.map((lease) => (
              <div key={lease.id_bail} className="p-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-2">
                      <div className="flex items-center space-x-2">
                        <User className="h-4 w-4 text-gray-400" />
                        <span className="font-medium text-gray-900">
                          {lease.locataire?.nom} {lease.locataire?.prenom}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Home className="h-4 w-4 text-gray-400" />
                        <div>
                          <span className="text-gray-600">
                            {lease.unite?.adresse_unite}
                          </span>
                          {lease.unite?.immeuble?.nom_immeuble && (
                            <span className="text-xs text-gray-500 ml-2">
                              ({lease.unite.immeuble.nom_immeuble})
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4" />
                        <span>
                          {formatDate(lease.date_debut)} - {formatDate(lease.date_fin)}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <DollarSign className="h-4 w-4" />
                        <span className="font-medium">
                          {formatCurrency(lease.prix_loyer)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">
                          {lease.methode_paiement || 'Non spécifié'}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <FileText className="h-4 w-4" />
                        <span className="text-gray-500">
                          {lease.pdf_bail ? 'PDF disponible' : 'Aucun PDF'}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleViewLease(lease)}
                      className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                      title="Voir les détails"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleEditLease(lease)}
                      className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                      title="Modifier"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteLease(lease)}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                      title="Supprimer"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modales */}
      {showForm && (
        <LeaseForm
          lease={selectedLease}
          isOpen={showForm}
          onClose={handleCloseForm}
          onSave={handleSaveLease}
        />
      )}
    </div>
  )
}