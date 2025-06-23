import axios from 'axios'

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
  { id: 1, name: "Jean Dupont", building: "Immeuble A", unit: "A-101", status: "active" },
  { id: 2, name: "Marie Martin", building: "Immeuble A", unit: "A-102", status: "active" },
  { id: 3, name: "Pierre Durand", building: "Immeuble B", unit: "B-201", status: "pending" }
]

export const tenantsService = {
  getTenants: async () => {
    try {
      return await api.get('/api/tenants')
    } catch (error) {
      console.warn('API tenants failed, using fallback data')
      return { data: fallbackTenants }
    }
  },
  getTenant: (id) => api.get(`/api/tenants/${id}`),
  createTenant: (data) => api.post('/api/tenants', data),
  updateTenant: (id, data) => api.put(`/api/tenants/${id}`, data),
  deleteTenant: (id) => api.delete(`/api/tenants/${id}`),
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

export default api 