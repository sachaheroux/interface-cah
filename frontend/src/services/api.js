import axios from 'axios'
import { parseAddressAndGenerateUnits } from '../types/unit.js'

// Configuration de base pour axios
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // Timeout de 10 secondes
  headers: {
    'Content-Type': 'application/json',
  },
})

// Intercepteur pour les requêtes (pour ajouter des tokens d'auth plus tard)
api.interceptors.request.use(
  (config) => {
    // Ici on pourra ajouter les tokens d'authentification plus tard
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur pour les réponses (pour gérer les erreurs globalement)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirection vers login si non autorisé
      // window.location.href = '/login'
    }
    
    // Log des erreurs pour debug
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message
    })
    
    return Promise.reject(error)
  }
)

// Services API pour chaque module
export const dashboardService = {
  getDashboardData: async () => {
    try {
      return await api.get(`/api/dashboard?t=${Date.now()}`)
    } catch (error) {
      console.warn('API dashboard failed, calculating from local buildings data')
      
      // Fallback : calculer les données à partir des immeubles locaux et de l'API
      try {
        // Essayer de récupérer les immeubles depuis l'API d'abord
        let buildings = []
        try {
          const buildingsResponse = await api.get('/api/buildings')
          buildings = buildingsResponse.data || []
        } catch (buildingError) {
          console.warn('API buildings failed, using local storage')
          buildings = []
        }
        
        // Ajouter les immeubles du localStorage (mode fallback)
        const localBuildings = JSON.parse(localStorage.getItem('localBuildings') || '[]')
        buildings = [...buildings, ...localBuildings]
        
        // Calculer les statistiques
        const totalBuildings = buildings.length
        const totalUnits = buildings.reduce((sum, building) => sum + (building.units || 0), 0)
        const portfolioValue = buildings.reduce((sum, building) => {
          const currentValue = building.financials?.currentValue || 0
          return sum + currentValue
        }, 0)
        const monthlyRevenue = portfolioValue * 0.005 // 0.5% par mois
        
        return {
          data: {
            totalBuildings,
            totalUnits,
            portfolioValue,
            monthlyRevenue,
            recentActivity: [
              {
                type: "info",
                message: `Portfolio actuel : ${totalBuildings} immeubles`,
                timestamp: new Date().toISOString()
              },
              {
                type: "success",
                message: `Total unités : ${totalUnits}`,
                timestamp: new Date().toISOString()
              },
              {
                type: "info",
                message: `Valeur portfolio : ${portfolioValue.toLocaleString('fr-CA')} $`,
                timestamp: new Date().toISOString()
              }
            ]
          }
        }
      } catch (fallbackError) {
        console.error('Fallback calculation failed:', fallbackError)
        return {
          data: {
            totalBuildings: 0,
            totalUnits: 0,
            portfolioValue: 0,
            monthlyRevenue: 0,
            recentActivity: []
          }
        }
      }
    }
  },
}

export const buildingsService = {
  getBuildings: async () => {
    try {
      return await api.get('/api/buildings')
    } catch (error) {
      console.warn('API buildings failed, using fallback data')
      // Retourner les données du localStorage en cas d'échec API
      const localBuildings = JSON.parse(localStorage.getItem('localBuildings') || '[]')
      return { data: localBuildings }
    }
  },
  getBuilding: (id) => api.get(`/api/buildings/${id}`),
  createBuilding: async (data) => {
    try {
      return await api.post('/api/buildings', data)
    } catch (error) {
      console.warn('API create building failed, saving locally')
      // Fallback vers localStorage
      const localBuildings = JSON.parse(localStorage.getItem('localBuildings') || '[]')
      const newBuilding = {
        ...data,
        id: Date.now(), // ID temporaire basé sur timestamp
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      localBuildings.push(newBuilding)
      localStorage.setItem('localBuildings', JSON.stringify(localBuildings))
      return { data: newBuilding }
    }
  },
  updateBuilding: async (id, data) => {
    try {
      return await api.put(`/api/buildings/${id}`, data)
    } catch (error) {
      console.warn('API update building failed, updating locally')
      // Fallback vers localStorage
      const localBuildings = JSON.parse(localStorage.getItem('localBuildings') || '[]')
      const index = localBuildings.findIndex(b => b.id === id)
      if (index !== -1) {
        localBuildings[index] = { ...localBuildings[index], ...data, updatedAt: new Date().toISOString() }
        localStorage.setItem('localBuildings', JSON.stringify(localBuildings))
        return { data: localBuildings[index] }
      }
      throw error
    }
  },
  deleteBuilding: async (id) => {
    try {
      return await api.delete(`/api/buildings/${id}`)
    } catch (error) {
      console.warn('API delete building failed, deleting locally')
      // Fallback vers localStorage
      const localBuildings = JSON.parse(localStorage.getItem('localBuildings') || '[]')
      const filteredBuildings = localBuildings.filter(b => b.id !== id)
      localStorage.setItem('localBuildings', JSON.stringify(filteredBuildings))
      return { data: { message: 'Immeuble supprimé localement' } }
    }
  },
}

// Données de fallback pour les locataires
const fallbackTenants = [
  { 
    id: 1, 
    name: "Jean Dupont", 
    email: "jean.dupont@email.com",
    phone: "(514) 555-0123",
    building: "Immeuble A", 
    unit: "A-101", 
    status: "active",
    createdAt: "2024-01-15T10:00:00Z",
    updatedAt: "2024-01-15T10:00:00Z"
  },
  { 
    id: 2, 
    name: "Marie Martin", 
    email: "marie.martin@email.com",
    phone: "(514) 555-0124",
    building: "Immeuble A", 
    unit: "A-102", 
    status: "active",
    createdAt: "2024-01-20T14:30:00Z",
    updatedAt: "2024-01-20T14:30:00Z"
  },
  { 
    id: 3, 
    name: "Pierre Durand", 
    email: "pierre.durand@email.com",
    phone: "(514) 555-0125",
    building: "Immeuble B", 
    unit: "B-201", 
    status: "pending",
    createdAt: "2024-02-01T09:15:00Z",
    updatedAt: "2024-02-01T09:15:00Z"
  }
]

export const tenantsService = {
  getTenants: async () => {
    try {
      const response = await api.get('/api/tenants')
      console.log('Raw API tenants response:', response)
      console.log('Response data:', response.data)
      
      // Simplifier la logique - juste extraire le tableau de données
      let tenantsArray = []
      
      if (response.data) {
        // Si response.data est déjà un tableau
        if (Array.isArray(response.data)) {
          tenantsArray = response.data
        }
        // Si response.data.data contient le tableau
        else if (response.data.data && Array.isArray(response.data.data)) {
          tenantsArray = response.data.data
        }
        // Si response.data contient une propriété tenants
        else if (response.data.tenants && Array.isArray(response.data.tenants)) {
          tenantsArray = response.data.tenants
        }
        // Sinon, essayer de convertir en tableau
        else {
          console.warn('Unexpected data format, using fallback')
          tenantsArray = []
        }
      }
      
      console.log('Final tenants array:', tenantsArray)
      return { data: tenantsArray }
    } catch (error) {
      console.warn('API tenants failed, using fallback data:', error.message)
      // Retourner les données du localStorage en cas d'échec API
      const localTenants = JSON.parse(localStorage.getItem('localTenants') || '[]')
      if (localTenants.length === 0) {
        // Si pas de données locales, utiliser les données par défaut
        return { data: fallbackTenants }
      }
      return { data: localTenants }
    }
  },
  
  getTenant: async (id) => {
    try {
      const response = await api.get(`/api/tenants/${id}`)
      console.log('Get tenant response:', response)
      
      // Extraire les données de manière simple
      if (response.data?.data) {
        return { data: response.data.data }
      } else if (response.data) {
        return { data: response.data }
      }
      
      throw new Error('No data in response')
    } catch (error) {
      console.warn('API get tenant failed, searching locally')
      const localTenants = JSON.parse(localStorage.getItem('localTenants') || '[]')
      const tenant = localTenants.find(t => t.id === parseInt(id))
      if (tenant) {
        return { data: tenant }
      }
      // Fallback vers les données par défaut
      const fallbackTenant = fallbackTenants.find(t => t.id === parseInt(id))
      if (fallbackTenant) {
        return { data: fallbackTenant }
      }
      throw error
    }
  },
  
  createTenant: async (data) => {
    try {
      console.log('📤 Creating tenant with data:', {
        name: data.name,
        lease: data.lease,
        leaseRenewal: data.leaseRenewal,
        fullData: data
      })
      const response = await api.post('/api/tenants', data)
      console.log('📥 Create tenant response:', response)
      
      // Extraire les données créées
      if (response.data?.data) {
        console.log('✅ Tenant créé avec succès (response.data.data):', response.data.data)
        return { data: response.data.data }
      } else if (response.data) {
        console.log('✅ Tenant créé avec succès (response.data):', response.data)
        return { data: response.data }
      }
      
      throw new Error('No data in create response')
    } catch (error) {
      console.warn('⚠️ API create tenant failed, saving locally:', error.message)
      
      // Fallback vers localStorage avec un ID plus sûr
      const localTenants = JSON.parse(localStorage.getItem('localTenants') || '[]')
      
      // Utiliser un ID basé sur le nom plutôt qu'un timestamp pour éviter les conflits
      const safeId = localTenants.length > 0 ? Math.max(...localTenants.map(t => t.id || 0)) + 1 : 1
      
      const newTenant = {
        ...data,
        id: safeId, // ID séquentiel au lieu de timestamp
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      
      localTenants.push(newTenant)
      localStorage.setItem('localTenants', JSON.stringify(localTenants))
      console.log('💾 Tenant saved locally:', {
        id: newTenant.id,
        name: newTenant.name,
        lease: newTenant.lease,
        leaseRenewal: newTenant.leaseRenewal
      })
      
      return { data: newTenant }
    }
  },
  
  updateTenant: async (id, data) => {
    try {
      console.log('📤 Updating tenant with ID:', id, 'Data:', {
        name: data.name,
        lease: data.lease,
        leaseRenewal: data.leaseRenewal,
        fullData: data
      })
      const response = await api.put(`/api/tenants/${id}`, data)
      console.log('📥 Update tenant response:', response)
      
      // Extraire les données mises à jour
      if (response.data?.data) {
        console.log('✅ Tenant mis à jour avec succès (response.data.data):', response.data.data)
        return { data: response.data.data }
      } else if (response.data) {
        console.log('✅ Tenant mis à jour avec succès (response.data):', response.data)
        return { data: response.data }
      }
      
      throw new Error('No data in update response')
    } catch (error) {
      console.warn('⚠️ API update tenant failed, updating locally:', error.message)
      
      // Fallback vers localStorage
      const localTenants = JSON.parse(localStorage.getItem('localTenants') || '[]')
      const index = localTenants.findIndex(t => t.id === parseInt(id))
      
      if (index !== -1) {
        localTenants[index] = { 
          ...localTenants[index], 
          ...data, 
          updatedAt: new Date().toISOString() 
        }
        localStorage.setItem('localTenants', JSON.stringify(localTenants))
        console.log('Tenant updated locally:', localTenants[index])
        return { data: localTenants[index] }
      }
      
      throw error
    }
  },
  
  deleteTenant: async (id) => {
    try {
      const response = await api.delete(`/api/tenants/${id}`)
      console.log('Delete tenant response:', response)
      return response
    } catch (error) {
      console.warn('API delete tenant failed, deleting locally:', error.message)
      
      // Fallback vers localStorage
      const localTenants = JSON.parse(localStorage.getItem('localTenants') || '[]')
      const filteredTenants = localTenants.filter(t => t.id !== parseInt(id))
      localStorage.setItem('localTenants', JSON.stringify(filteredTenants))
      console.log('Tenant deleted locally, remaining:', filteredTenants.length)
      
      return { data: { message: 'Locataire supprimé localement' } }
    }
  },
}

export const maintenanceService = {
  getMaintenance: () => api.get('/api/maintenance'),
  getMaintenanceItem: (id) => api.get(`/api/maintenance/${id}`),
  createMaintenanceItem: (data) => api.post('/api/maintenance', data),
  updateMaintenanceItem: (id, data) => api.put(`/api/maintenance/${id}`, data),
  deleteMaintenanceItem: (id) => api.delete(`/api/maintenance/${id}`),
}

// Données de fallback pour les employés
const fallbackEmployees = [
  { id: 1, name: "Marc Ouvrier", role: "Contremaître", status: "active" },
  { id: 2, name: "Sophie Tech", role: "Électricienne", status: "active" },
  { id: 3, name: "Paul Plombier", role: "Plombier", status: "active" }
]

export const employeesService = {
  getEmployees: async () => {
    try {
      return await api.get('/api/employees')
    } catch (error) {
      console.warn('API employees failed, using fallback data')
      return { data: fallbackEmployees }
    }
  },
  getEmployee: (id) => api.get(`/api/employees/${id}`),
  createEmployee: (data) => api.post('/api/employees', data),
  updateEmployee: (id, data) => api.put(`/api/employees/${id}`, data),
  deleteEmployee: (id) => api.delete(`/api/employees/${id}`),
}

// Données de fallback pour les projets
const fallbackProjects = [
  { id: 1, name: "Nouveau Complexe D", status: "planning", progress: 10 },
  { id: 2, name: "Rénovation Immeuble E", status: "in_progress", progress: 65 },
  { id: 3, name: "Extension Immeuble F", status: "completed", progress: 100 }
]

export const projectsService = {
  getProjects: async () => {
    try {
      return await api.get('/api/projects')
    } catch (error) {
      console.warn('API projects failed, using fallback data')
      return { data: fallbackProjects }
    }
  },
  getProject: (id) => api.get(`/api/projects/${id}`),
  createProject: (data) => api.post('/api/projects', data),
  updateProject: (id, data) => api.put(`/api/projects/${id}`, data),
  deleteProject: (id) => api.delete(`/api/projects/${id}`),
}

// Service générique pour les appels API personnalisés
export const apiService = {
  get: (url) => api.get(url),
  post: (url, data) => api.post(url, data),
  put: (url, data) => api.put(url, data),
  delete: (url) => api.delete(url),
}

export const unitsService = {
  getUnits: async () => {
    try {
      // Pour l'instant, générer les unités à partir des immeubles
      const buildingsResponse = await buildingsService.getBuildings()
      const buildings = Array.isArray(buildingsResponse.data) ? buildingsResponse.data : buildingsResponse
      
      let allUnits = []
      
      buildings.forEach(building => {
        if (building && typeof building === 'object') {
          const buildingUnits = parseAddressAndGenerateUnits(building)
          allUnits = [...allUnits, ...buildingUnits]
        }
      })
      
      console.log('Generated units from buildings:', allUnits)
      return { data: allUnits }
    } catch (error) {
      console.error('Error getting units:', error)
      return { data: [] }
    }
  },
  
  getAvailableUnits: async () => {
    try {
      const unitsResponse = await unitsService.getUnits()
      const units = unitsResponse.data || []
      
      // Récupérer les assignations depuis le backend au lieu du localStorage
      const assignmentsResponse = await assignmentsService.getAssignments()
      const assignments = assignmentsResponse.data || []
      
      const availableUnits = units.filter(unit => {
        const unitAssignments = assignments.filter(a => a.unitId === unit.id)
        // Considérer qu'une unité peut avoir jusqu'à 4 locataires (configurable)
        return unitAssignments.length < 4
      })
      
      return { data: availableUnits }
    } catch (error) {
      console.error('Error getting available units:', error)
      return { data: [] }
    }
  },
  
  getUnitTenants: async (unitId) => {
    try {
      const response = await assignmentsService.getUnitAssignments(unitId)
      const assignments = response.data || []
      
      // Retourner les données des locataires avec leurs IDs
      return { 
        data: assignments.map(a => ({
          ...a.tenantData,
          id: a.tenantData?.id || a.tenantId // S'assurer que l'ID est présent
        }))
      }
    } catch (error) {
      console.error('Error getting unit tenants:', error)
      return { data: [] }
    }
  },
  
  assignTenantToUnit: async (unitId, tenantId, tenantData) => {
    try {
      console.log('Assigning tenant to unit:', { unitId, tenantId, tenantData })
      
      const assignmentData = {
        unitId,
        tenantId,
        tenantData
      }
      
      // Utiliser le backend au lieu du localStorage
      const response = await assignmentsService.createAssignment(assignmentData)
      
      console.log('Tenant assigned to unit successfully')
      return response
    } catch (error) {
      console.error('Error assigning tenant to unit:', error)
      throw error
    }
  },
  
  removeTenantFromUnit: async (tenantId) => {
    try {
      const response = await assignmentsService.removeTenantAssignment(tenantId)
      
      console.log('Tenant removed from unit successfully')
      return response
    } catch (error) {
      console.error('Error removing tenant from unit:', error)
      throw error
    }
  },
  
  getTenantUnit: async (tenantId) => {
    try {
      const assignmentResponse = await assignmentsService.getTenantAssignment(tenantId)
      const assignment = assignmentResponse.data
      
      if (assignment) {
        const unitsResponse = await unitsService.getUnits()
        const units = unitsResponse.data || []
        const unit = units.find(u => u.id === assignment.unitId)
        
        if (unit) {
          // Enrichir l'unité avec tous ses locataires
          const unitAssignmentsResponse = await assignmentsService.getUnitAssignments(unit.id)
          const unitAssignments = unitAssignmentsResponse.data || []
          const allTenants = unitAssignments.map(a => a.tenantData)
          
          return { 
            data: {
              ...unit,
              currentTenants: allTenants,
              assignmentDate: assignment.assignedAt
            }
          }
        }
      }
      
      return { data: null }
    } catch (error) {
      console.error('Error getting tenant unit:', error)
      return { data: null }
    }
  },

  getUnitWithTenants: async (unitId) => {
    try {
      const unitsResponse = await unitsService.getUnits()
      const units = unitsResponse.data || []
      const unit = units.find(u => u.id === unitId)
      
      if (unit) {
        const assignmentsResponse = await assignmentsService.getUnitAssignments(unitId)
        const unitAssignments = assignmentsResponse.data || []
        const tenants = unitAssignments.map(a => ({
          ...a.tenantData,
          assignedAt: a.assignedAt
        }))
        
        return {
          data: {
            ...unit,
            tenants,
            occupancyCount: tenants.length
          }
        }
      }
      
      return { data: null }
    } catch (error) {
      console.error('Error getting unit with tenants:', error)
      return { data: null }
    }
  }
}

// Service pour les assignations locataires-unités
export const assignmentsService = {
  // Fonction de migration des données localStorage vers backend
  migrateLocalStorageToBackend: async () => {
    try {
      const localAssignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      
      if (localAssignments.length === 0) {
        console.log('📦 Aucune assignation locale à migrer')
        return { migrated: 0, success: true }
      }

      console.log(`📦 Migration de ${localAssignments.length} assignations vers le backend...`)
      
      let migrated = 0
      let errors = 0

      // Migrer chaque assignation directement via l'API (sans modifier localStorage)
      for (const assignment of localAssignments) {
        try {
          const response = await fetch(`${API_BASE_URL}/api/assignments`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              unitId: assignment.unitId,
              tenantId: assignment.tenantId,
              tenantData: assignment.tenantData
            })
          })

          if (response.ok) {
            migrated++
            console.log(`✅ Assignation migrée: Locataire ${assignment.tenantId} → Unité ${assignment.unitId}`)
          } else {
            console.error(`❌ Erreur HTTP migration assignation ${assignment.tenantId}: ${response.status}`)
            errors++
          }
        } catch (error) {
          console.error(`❌ Erreur migration assignation ${assignment.tenantId}:`, error)
          errors++
        }
      }

      if (errors === 0) {
        // Migration réussie, effacer le localStorage
        localStorage.removeItem('unitTenantAssignments')
        localStorage.setItem('assignationsMigrated', 'true')
        console.log(`🎉 Migration terminée avec succès: ${migrated} assignations migrées`)
      } else {
        console.log(`⚠️ Migration partielle: ${migrated} réussies, ${errors} erreurs`)
      }

      return { 
        migrated, 
        errors, 
        success: errors === 0,
        total: localAssignments.length 
      }
    } catch (error) {
      console.error('❌ Erreur lors de la migration des assignations:', error)
      return { migrated: 0, errors: 1, success: false, total: 0 }
    }
  },

  // Vérifier si les assignations ont déjà été migrées
  hasMigrated: () => {
    return localStorage.getItem('assignationsMigrated') === 'true'
  },

  getAssignments: async () => {
    try {
      // Vérifier et effectuer la migration si nécessaire
      if (!assignmentsService.hasMigrated()) {
        const migrationResult = await assignmentsService.migrateLocalStorageToBackend()
        if (migrationResult.success && migrationResult.migrated > 0) {
          console.log(`🔄 Migration automatique effectuée: ${migrationResult.migrated} assignations`)
        }
      }

      const response = await fetch(`${API_BASE_URL}/api/assignments`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error getting assignments:', error)
      // Fallback vers localStorage pour la transition
      const localAssignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      return { data: localAssignments }
    }
  },

  createAssignment: async (assignmentData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/assignments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(assignmentData)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      
      // Mettre à jour aussi le localStorage pour la compatibilité
      const existingAssignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      const filteredAssignments = existingAssignments.filter(a => a.tenantId !== assignmentData.tenantId)
      filteredAssignments.push({
        unitId: assignmentData.unitId,
        tenantId: assignmentData.tenantId,
        tenantData: assignmentData.tenantData,
        assignedAt: new Date().toISOString()
      })
      localStorage.setItem('unitTenantAssignments', JSON.stringify(filteredAssignments))
      
      return result
    } catch (error) {
      console.error('Error creating assignment:', error)
      throw error
    }
  },

  removeTenantAssignment: async (tenantId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/assignments/tenant/${tenantId}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      
      // Mettre à jour aussi le localStorage pour la compatibilité
      const assignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      const filteredAssignments = assignments.filter(a => a.tenantId !== tenantId)
      localStorage.setItem('unitTenantAssignments', JSON.stringify(filteredAssignments))
      
      return result
    } catch (error) {
      console.error('Error removing tenant assignment:', error)
      throw error
    }
  },

  // Nouvelle méthode pour supprimer une assignation spécifique (locataire + unité)
  removeSpecificAssignment: async (tenantId, unitId) => {
    try {
      console.log(`🔗 Suppression assignation spécifique: Locataire ${tenantId} de l'unité ${unitId}`)
      
      // Utiliser la nouvelle route API spécifique
      const response = await fetch(`${API_BASE_URL}/api/assignments/tenant/${tenantId}/unit/${unitId}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      // Mettre à jour le localStorage pour la compatibilité
      const localAssignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      const filteredAssignments = localAssignments.filter(a => 
        !(a.tenantId === tenantId && a.unitId === unitId)
      )
      localStorage.setItem('unitTenantAssignments', JSON.stringify(filteredAssignments))
      
      console.log(`✅ Assignation spécifique supprimée: Locataire ${tenantId} retiré de l'unité ${unitId}`)
      return result
      
    } catch (error) {
      console.error('❌ Error removing specific assignment:', error)
      
      // Fallback: Supprimer directement du localStorage
      const localAssignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      const filteredAssignments = localAssignments.filter(a => 
        !(a.tenantId === tenantId && a.unitId === unitId)
      )
      localStorage.setItem('unitTenantAssignments', JSON.stringify(filteredAssignments))
      
      console.log(`⚠️ Fallback: Assignation supprimée localement`)
      return { success: true, fallback: true }
    }
  },

  getUnitAssignments: async (unitId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/assignments/unit/${unitId}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error getting unit assignments:', error)
      // Fallback vers localStorage
      const localAssignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      const unitAssignments = localAssignments.filter(a => a.unitId === unitId)
      return { data: unitAssignments }
    }
  },

  getTenantAssignment: async (tenantId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/assignments/tenant/${tenantId}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error getting tenant assignment:', error)
      // Fallback vers localStorage
      const localAssignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      const assignment = localAssignments.find(a => a.tenantId === parseInt(tenantId))
      return { data: assignment || null }
    }
  },

  // Nouvelle méthode pour nettoyer les assignations invalides
  cleanInvalidAssignments: async () => {
    try {
      console.log('🧹 Nettoyage des assignations invalides...')
      const response = await fetch(`${API_BASE_URL}/api/assignments/clean`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      console.log('✅ Nettoyage terminé:', result)
      return result
    } catch (error) {
      console.error('❌ Erreur lors du nettoyage:', error)
      throw error
    }
  }
}

// Service pour les rapports d'immeubles et d'unités
export const reportsService = {
  // === RAPPORTS D'IMMEUBLES ===
  getBuildingReports: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/building-reports`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error getting building reports:', error)
      throw error
    }
  },

  getBuildingReport: async (buildingId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/building-reports/${buildingId}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error getting building report:', error)
      throw error
    }
  },

  createBuildingReport: async (reportData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/building-reports`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reportData)
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error creating building report:', error)
      throw error
    }
  },

  deleteBuildingReport: async (reportId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/building-reports/${reportId}`, {
        method: 'DELETE'
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error deleting building report:', error)
      throw error
    }
  },

  // === RAPPORTS D'UNITÉS ===
  getUnitReports: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/unit-reports`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error getting unit reports:', error)
      throw error
    }
  },

  getUnitReport: async (unitId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/unit-reports/${unitId}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error getting unit report:', error)
      throw error
    }
  },

  createUnitReport: async (reportData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/unit-reports`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reportData)
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error creating unit report:', error)
      throw error
    }
  },

  deleteUnitReport: async (reportId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/unit-reports/${reportId}`, {
        method: 'DELETE'
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error deleting unit report:', error)
      throw error
    }
  }
}

export default api 