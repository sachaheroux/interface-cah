import React, { useState, useEffect } from 'react'
import { Users, Plus, Phone, Mail, Home, Eye, Edit, Trash2, Search, FileText } from 'lucide-react'
import { tenantsService, assignmentsService } from '../services/api'
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
    
    // Écouter les événements de création et mise à jour de locataires
    const handleTenantCreated = (event) => {
      console.log('📢 Tenants: Événement tenantCreated reçu:', event.detail)
      console.log('🔄 Tenants: Rechargement de la liste des locataires...')
      fetchTenants()
    }
    
    const handleTenantUpdated = (event) => {
      console.log('📢 Tenants: Événement tenantUpdated reçu:', event.detail)
      console.log('🔄 Tenants: Rechargement de la liste des locataires...')
      fetchTenants()
    }
    
    window.addEventListener('tenantCreated', handleTenantCreated)
    window.addEventListener('tenantUpdated', handleTenantUpdated)
    
    return () => {
      window.removeEventListener('tenantCreated', handleTenantCreated)
      window.removeEventListener('tenantUpdated', handleTenantUpdated)
    }
  }, [])

  // Filtrer les locataires avec vérifications de sécurité renforcées
  useEffect(() => {
    console.log('Filtering tenants, current tenants:', tenants)
    
    // Vérifications de sécurité multiples
    if (!tenants) {
      console.warn('Tenants is null or undefined')
      setFilteredTenants([])
      return
    }

    if (!Array.isArray(tenants)) {
      console.error('Tenants is not an array:', typeof tenants, tenants)
      setFilteredTenants([])
      return
    }

    try {
      let filtered = [...tenants]

      // Filtre par terme de recherche
      if (searchTerm && searchTerm.trim()) {
        filtered = filtered.filter(tenant => {
          if (!tenant || typeof tenant !== 'object') return false
          
          const name = `${tenant.nom || ''} ${tenant.prenom || ''}`.trim()
          const email = tenant.email || ''
          const phone = tenant.telephone || ''
          const building = tenant.building || ''
          
          const searchLower = searchTerm.toLowerCase()
          
          return (
            name.toLowerCase().includes(searchLower) ||
            email.toLowerCase().includes(searchLower) ||
            phone.includes(searchTerm) ||
            building.toLowerCase().includes(searchLower)
          )
        })
      }

      // Filtre par statut
      if (statusFilter && statusFilter.trim()) {
        filtered = filtered.filter(tenant => {
          if (!tenant || typeof tenant !== 'object') return false
          return tenant.statut === statusFilter
        })
      }

      console.log('Filtered tenants result:', filtered)
      setFilteredTenants(filtered)
    } catch (error) {
      console.error('Error filtering tenants:', error)
      setFilteredTenants([])
    }
  }, [tenants, searchTerm, statusFilter])

  const fetchTenants = async () => {
    try {
      setLoading(true)
      const response = await tenantsService.getTenants()
      console.log('Tenants service response:', response)
      
      // Simplifier - juste prendre response.data et s'assurer que c'est un tableau
      const tenantsData = response.data || []
      
      // Vérification de sécurité
      if (Array.isArray(tenantsData)) {
        console.log('Setting tenants data:', tenantsData)
        setTenants(tenantsData)
      } else {
        console.error('Tenants data is not an array:', tenantsData)
        setTenants([])
      }
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
    // Cette fonction n'est plus utilisée car TenantForm gère directement les appels API
    // Elle est gardée pour la compatibilité mais ne fait rien
    console.log('⚠️ handleSaveTenant appelée mais ignorée (TenantForm gère directement les API)')
  }

  const handleManageLeases = (tenant) => {
    // Rediriger vers la page des baux avec le locataire sélectionné
    window.location.href = `/leases?tenant=${tenant.id_locataire}`
  }

  const handleDeleteTenant = async (tenant) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer le locataire "${tenant.nom} ${tenant.prenom}" ?`)) {
      try {
        console.log(`🗑️ Suppression du locataire: ${tenant.nom} ${tenant.prenom} (ID: ${tenant.id_locataire})`)
        
        // Étape 1: Supprimer d'abord toutes les assignations du locataire
        try {
          console.log(`🔗 Suppression des assignations pour le locataire ${tenant.id_locataire}...`)
          await assignmentsService.removeTenantAssignment(tenant.id_locataire)
          console.log(`✅ Assignations supprimées pour le locataire ${tenant.id_locataire}`)
        } catch (assignmentError) {
          console.warn(`⚠️ Erreur lors de la suppression des assignations:`, assignmentError)
          // Continuer même si la suppression des assignations échoue
        }
        
        // Étape 2: Supprimer le locataire lui-même
        console.log(`👤 Suppression du locataire de la base de données...`)
        await tenantsService.deleteTenant(tenant.id_locataire)
        
        // Étape 3: Mettre à jour l'interface
        setTenants(prev => prev.filter(t => t.id_locataire !== tenant.id_locataire))
        setShowDetails(false)
        
        console.log(`✅ Locataire ${tenant.nom} ${tenant.prenom} supprimé avec succès`)
        
        // Étape 4: Déclencher un événement pour actualiser les autres vues
        window.dispatchEvent(new CustomEvent('tenantDeleted', { 
          detail: { tenantId: tenant.id_locataire, tenantName: `${tenant.nom} ${tenant.prenom}` } 
        }))
        
      } catch (error) {
        console.error('❌ Erreur lors de la suppression:', error)
        alert(`Erreur lors de la suppression du locataire "${tenant.nom} ${tenant.prenom}". Vérifiez la console pour plus de détails.`)
        
        // En cas d'erreur API majeure, on supprime localement quand même
        setTenants(prev => prev.filter(t => t.id_locataire !== tenant.id_locataire))
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
            Liste des Locataires ({Array.isArray(filteredTenants) ? filteredTenants.length : 0})
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.isArray(filteredTenants) && filteredTenants.map((tenant) => (
            <div key={tenant.id_locataire} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              {/* En-tête du locataire */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Users className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-3">
                    <h4 className="text-lg font-semibold text-gray-900">{tenant.nom} {tenant.prenom}</h4>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getTenantStatusColor(tenant.statut)}`}>
                      {getTenantStatusLabel(tenant.statut)}
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
                
                {tenant.telephone && (
                  <div className="flex items-center text-gray-600">
                    <Phone className="h-4 w-4 mr-2" />
                    <span className="text-sm">{tenant.telephone}</span>
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
                  onClick={() => handleManageLeases(tenant)}
                  className="flex-1 btn-primary text-sm py-2"
                  title="Gérer les baux de ce locataire"
                >
                  <FileText className="h-4 w-4 mr-1" />
                  Baux
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
        {(!Array.isArray(filteredTenants) || filteredTenants.length === 0) && (
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {(!Array.isArray(tenants) || tenants.length === 0) ? 'Aucun locataire' : 'Aucun locataire correspondant aux filtres'}
            </h3>
            <p className="text-gray-600 mb-4">
              {(!Array.isArray(tenants) || tenants.length === 0)
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