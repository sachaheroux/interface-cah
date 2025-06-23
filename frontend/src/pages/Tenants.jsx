import React, { useState, useEffect } from 'react'
import { Users, Plus, Phone, Mail, Home, Eye, Edit, Trash2, Search } from 'lucide-react'
import { tenantsService } from '../services/api'
import { getTenantStatusLabel, getTenantStatusColor } from '../types/tenant'
import TenantForm from '../components/TenantForm'
import TenantDetails from '../components/TenantDetails'

export default function Tenants() {
  const [tenants, setTenants] = useState([])
  const [filteredTenants, setFilteredTenants] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  
  // États pour les modales
  const [selectedTenant, setSelectedTenant] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    fetchTenants()
  }, [])

  // Filtrer les locataires
  useEffect(() => {
    let filtered = [...tenants]

    // Filtre par terme de recherche
    if (searchTerm) {
      filtered = filtered.filter(tenant => 
        tenant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tenant.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tenant.phone?.includes(searchTerm) ||
        tenant.building?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filtre par statut
    if (statusFilter) {
      filtered = filtered.filter(tenant => tenant.status === statusFilter)
    }

    setFilteredTenants(filtered)
  }, [tenants, searchTerm, statusFilter])

  const fetchTenants = async () => {
    try {
      setLoading(true)
      const response = await tenantsService.getTenants()
      setTenants(response.data || [])
    } catch (err) {
      console.error('Tenants error:', err)
      setTenants([]) // Définir un tableau vide en cas d'erreur
    } finally {
      setLoading(false)
    }
  }

  // Gestionnaires d'événements
  const handleAddTenant = () => {
    setSelectedTenant(null)
    setShowForm(true)
  }

  const handleViewTenant = (tenant) => {
    setSelectedTenant(tenant)
    setShowDetails(true)
  }

  const handleEditTenant = (tenant) => {
    setSelectedTenant(tenant)
    setShowForm(true)
  }

  const handleSaveTenant = async (tenantData) => {
    try {
      if (tenantData.id && tenants.find(t => t.id === tenantData.id)) {
        // Mise à jour d'un locataire existant
        const response = await tenantsService.updateTenant(tenantData.id, tenantData)
        const updatedTenants = tenants.map(tenant => 
          tenant.id === tenantData.id ? response.data || tenantData : tenant
        )
        setTenants(updatedTenants)
      } else {
        // Création d'un nouveau locataire
        const response = await tenantsService.createTenant(tenantData)
        setTenants(prev => [...prev, response.data || tenantData])
      }
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
      // En cas d'erreur API, on met à jour localement quand même
      if (tenantData.id && tenants.find(t => t.id === tenantData.id)) {
        const updatedTenants = tenants.map(tenant => 
          tenant.id === tenantData.id ? tenantData : tenant
        )
        setTenants(updatedTenants)
      } else {
        setTenants(prev => [...prev, tenantData])
      }
    }
  }

  const handleDeleteTenant = async (tenant) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer le locataire "${tenant.name}" ?`)) {
      try {
        await tenantsService.deleteTenant(tenant.id)
        setTenants(prev => prev.filter(t => t.id !== tenant.id))
        setShowDetails(false)
      } catch (error) {
        console.error('Erreur lors de la suppression:', error)
        // En cas d'erreur API, on supprime localement quand même
        setTenants(prev => prev.filter(t => t.id !== tenant.id))
        setShowDetails(false)
      }
    }
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setSelectedTenant(null)
  }

  const handleCloseDetails = () => {
    setShowDetails(false)
    setSelectedTenant(null)
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Locataires</h1>
          <p className="text-gray-600 mt-1">Gérez vos locataires et leurs informations</p>
        </div>
        <button onClick={handleAddTenant} className="btn-primary flex items-center">
          <Plus className="h-5 w-5 mr-2" />
          Nouveau Locataire
        </button>
      </div>

      {/* Filtres et recherche */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Filtres et Recherche</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Recherche */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Rechercher nom, email, téléphone..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Filtre par statut */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Tous les statuts</option>
            <option value="active">Actif</option>
            <option value="pending">En attente</option>
            <option value="inactive">Inactif</option>
            <option value="former">Ancien locataire</option>
          </select>

          {/* Bouton effacer filtres */}
          <button
            onClick={() => {
              setSearchTerm('')
              setStatusFilter('')
            }}
            className="btn-secondary"
          >
            Effacer filtres
          </button>
        </div>
      </div>

      {/* Liste des locataires */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Liste des Locataires ({filteredTenants.length})
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTenants.map((tenant) => (
            <div key={tenant.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              {/* En-tête du locataire */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Users className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-3">
                    <h4 className="text-lg font-semibold text-gray-900">{tenant.name}</h4>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getTenantStatusColor(tenant.status)}`}>
                      {getTenantStatusLabel(tenant.status)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Informations de contact */}
              <div className="space-y-2 mb-4">
                {tenant.email && (
                  <div className="flex items-center text-gray-600">
                    <Mail className="h-4 w-4 mr-2" />
                    <span className="text-sm">{tenant.email}</span>
                  </div>
                )}
                
                {tenant.phone && (
                  <div className="flex items-center text-gray-600">
                    <Phone className="h-4 w-4 mr-2" />
                    <span className="text-sm">{tenant.phone}</span>
                  </div>
                )}

                {(tenant.building || tenant.unit) && (
                  <div className="flex items-center text-gray-600">
                    <Home className="h-4 w-4 mr-2" />
                    <span className="text-sm">{tenant.building} - {tenant.unit}</span>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex space-x-2">
                <button 
                  onClick={() => handleViewTenant(tenant)}
                  className="flex-1 btn-primary text-sm py-2"
                >
                  <Eye className="h-4 w-4 mr-1" />
                  Détails
                </button>
                <button 
                  onClick={() => handleEditTenant(tenant)}
                  className="flex-1 btn-secondary text-sm py-2"
                >
                  <Edit className="h-4 w-4 mr-1" />
                  Modifier
                </button>
                <button 
                  onClick={() => handleDeleteTenant(tenant)}
                  className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors text-sm"
                  title="Supprimer le locataire"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredTenants.length === 0 && (
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {tenants.length === 0 ? 'Aucun locataire' : 'Aucun locataire correspondant aux filtres'}
            </h3>
            <p className="text-gray-600 mb-4">
              {tenants.length === 0 
                ? 'Commencez par ajouter votre premier locataire.'
                : 'Essayez de modifier vos critères de recherche.'
              }
            </p>
            <button onClick={handleAddTenant} className="btn-primary">
              <Plus className="h-5 w-5 mr-2" />
              Ajouter un Locataire
            </button>
          </div>
        )}
      </div>

      {/* Modales */}
      {showForm && (
        <TenantForm
          tenant={selectedTenant}
          isOpen={showForm}
          onSave={handleSaveTenant}
          onClose={handleCloseForm}
        />
      )}
      
      {showDetails && (
        <TenantDetails
          tenant={selectedTenant}
          isOpen={showDetails}
          onClose={handleCloseDetails}
          onEdit={handleEditTenant}
          onDelete={handleDeleteTenant}
        />
      )}
    </div>
  )
} 