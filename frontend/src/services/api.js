import axios from 'axios'

// Configuration de base pour axios
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://interface-cah-backend.onrender.com'

const api = axios.create({
  baseURL: API_BASE_URL,
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
    return Promise.reject(error)
  }
)

// Services API pour chaque module
export const dashboardService = {
  getDashboardData: () => api.get('/api/dashboard'),
}

export const buildingsService = {
  getBuildings: () => api.get('/api/buildings'),
  getBuilding: (id) => api.get(`/api/buildings/${id}`),
  createBuilding: (data) => api.post('/api/buildings', data),
  updateBuilding: (id, data) => api.put(`/api/buildings/${id}`, data),
  deleteBuilding: (id) => api.delete(`/api/buildings/${id}`),
}

export const tenantsService = {
  getTenants: () => api.get('/api/tenants'),
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

export const employeesService = {
  getEmployees: () => api.get('/api/employees'),
  getEmployee: (id) => api.get(`/api/employees/${id}`),
  createEmployee: (data) => api.post('/api/employees', data),
  updateEmployee: (id, data) => api.put(`/api/employees/${id}`, data),
  deleteEmployee: (id) => api.delete(`/api/employees/${id}`),
}

export const projectsService = {
  getProjects: () => api.get('/api/projects'),
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