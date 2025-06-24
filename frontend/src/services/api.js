import axios from 'axios'
import { parseAddressAndGenerateUnits } from '../types/unit.js'

// Configuration de base pour axios
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://interface-cah-backend.onrender.com'

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
      console.log('Creating tenant with data:', data)
      const response = await api.post('/api/tenants', data)
      console.log('Create tenant response:', response)
      
      // Extraire les données créées
      if (response.data?.data) {
        return { data: response.data.data }
      } else if (response.data) {
        return { data: response.data }
      }
      
      throw new Error('No data in create response')
    } catch (error) {
      console.warn('API create tenant failed, saving locally:', error.message)
      
      // Fallback vers localStorage
      const localTenants = JSON.parse(localStorage.getItem('localTenants') || '[]')
      const newTenant = {
        ...data,
        id: Date.now(), // ID temporaire basé sur timestamp
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      
      localTenants.push(newTenant)
      localStorage.setItem('localTenants', JSON.stringify(localTenants))
      console.log('Tenant saved locally:', newTenant)
      
      return { data: newTenant }
    }
  },
  
  updateTenant: async (id, data) => {
    try {
      console.log('Updating tenant with ID:', id, 'Data:', data)
      const response = await api.put(`/api/tenants/${id}`, data)
      console.log('Update tenant response:', response)
      
      // Extraire les données mises à jour
      if (response.data?.data) {
        return { data: response.data.data }
      } else if (response.data) {
        return { data: response.data }
      }
      
      throw new Error('No data in update response')
    } catch (error) {
      console.warn('API update tenant failed, updating locally:', error.message)
      
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
      
      // Filtrer les unités libres (pas occupées)
      const availableUnits = units.filter(unit => 
        unit.status === 'vacant' || !unit.tenantId
      )
      
      return { data: availableUnits }
    } catch (error) {
      console.error('Error getting available units:', error)
      return { data: [] }
    }
  },
  
  assignTenantToUnit: async (unitId, tenantId, tenantData) => {
    try {
      console.log('Assigning tenant to unit:', { unitId, tenantId, tenantData })
      
      // Pour l'instant, on stocke cette information localement
      // Dans une vraie application, cela irait vers une API
      const assignmentData = {
        unitId,
        tenantId,
        tenantData,
        assignedAt: new Date().toISOString()
      }
      
      // Stocker dans localStorage pour la persistance
      const existingAssignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      
      // Supprimer l'ancienne assignation pour ce locataire s'il y en a une
      const filteredAssignments = existingAssignments.filter(a => a.tenantId !== tenantId)
      
      // Ajouter la nouvelle assignation
      filteredAssignments.push(assignmentData)
      
      localStorage.setItem('unitTenantAssignments', JSON.stringify(filteredAssignments))
      
      console.log('Tenant assigned to unit successfully')
      return { data: assignmentData }
    } catch (error) {
      console.error('Error assigning tenant to unit:', error)
      throw error
    }
  },
  
  getTenantUnit: async (tenantId) => {
    try {
      const assignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
      const assignment = assignments.find(a => a.tenantId === parseInt(tenantId))
      
      if (assignment) {
        const unitsResponse = await unitsService.getUnits()
        const units = unitsResponse.data || []
        const unit = units.find(u => u.id === assignment.unitId)
        
        if (unit) {
          return { data: unit }
        }
      }
      
      return { data: null }
    } catch (error) {
      console.error('Error getting tenant unit:', error)
      return { data: null }
    }
  }
}

export default api 