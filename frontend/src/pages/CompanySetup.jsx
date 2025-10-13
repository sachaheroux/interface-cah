import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Building2, Plus, Users, AlertCircle, Search } from 'lucide-react'
import api from '../services/api'

export default function CompanySetup() {
  const navigate = useNavigate()
  const location = useLocation()
  const { email, userId } = location.state || {}

  const [mode, setMode] = useState(null) // 'create' ou 'join'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Données pour créer une compagnie
  const [newCompany, setNewCompany] = useState({
    nom_compagnie: '',
    email_compagnie: email || '',
    telephone_compagnie: '',
    adresse_compagnie: '',
    site_web: '',
    numero_entreprise: ''
  })

  // Données pour rejoindre une compagnie
  const [searchQuery, setSearchQuery] = useState('')
  const [companies, setCompanies] = useState([])
  const [selectedCompany, setSelectedCompany] = useState(null)
  const [role, setRole] = useState('employe') // 'admin' ou 'employe'

  const handleCreateCompany = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const token = localStorage.getItem('auth_token')
      const response = await api.post('/api/auth/setup-company', {
        action: 'create',
        company_data: newCompany
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      // Mettre à jour les infos utilisateur
      const updatedUser = response.data.user
      localStorage.setItem('user', JSON.stringify(updatedUser))

      // Rediriger vers le dashboard
      navigate('/buildings')
    } catch (err) {
      console.error('Erreur création compagnie:', err)
      setError(err.response?.data?.detail || 'Erreur lors de la création de la compagnie')
    } finally {
      setLoading(false)
    }
  }

  const searchCompanies = async () => {
    if (!searchQuery.trim()) {
      setError('Veuillez entrer un nom de compagnie')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await api.get(`/api/auth/companies?search=${encodeURIComponent(searchQuery)}`)
      setCompanies(response.data.companies || [])
      
      if (response.data.companies.length === 0) {
        setError('Aucune compagnie trouvée avec ce nom')
      }
    } catch (err) {
      console.error('Erreur recherche compagnies:', err)
      setError('Erreur lors de la recherche')
    } finally {
      setLoading(false)
    }
  }

  const handleJoinCompany = async (e) => {
    e.preventDefault()
    
    if (!selectedCompany) {
      setError('Veuillez sélectionner une compagnie')
      return
    }

    setError('')
    setLoading(true)

    try {
      const token = localStorage.getItem('auth_token')
      const response = await api.post('/api/auth/setup-company', {
        action: 'join',
        company_id: selectedCompany.id_compagnie,
        role: role
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      // Afficher message de confirmation
      alert('Votre demande a été envoyée à l\'administrateur. Vous recevrez un email une fois approuvée.')
      
      // Rediriger vers la page de connexion
      navigate('/login')
    } catch (err) {
      console.error('Erreur demande d\'accès:', err)
      setError(err.response?.data?.detail || 'Erreur lors de l\'envoi de la demande')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {/* Logo / Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4">
            <Building2 className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Configuration de votre compagnie</h1>
          <p className="text-gray-600">Créez une nouvelle compagnie ou rejoignez-en une existante</p>
        </div>

        {/* Choix du mode */}
        {!mode && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Créer une compagnie */}
            <button
              onClick={() => setMode('create')}
              className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-shadow border-2 border-transparent hover:border-blue-500"
            >
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <Plus className="h-8 w-8 text-blue-600" />
                </div>
                <h2 className="text-xl font-bold text-gray-900">Créer une compagnie</h2>
                <p className="text-gray-600">
                  Vous êtes le premier utilisateur ? Créez votre compagnie et devenez administrateur principal.
                </p>
              </div>
            </button>

            {/* Rejoindre une compagnie */}
            <button
              onClick={() => setMode('join')}
              className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-shadow border-2 border-transparent hover:border-blue-500"
            >
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <Users className="h-8 w-8 text-green-600" />
                </div>
                <h2 className="text-xl font-bold text-gray-900">Rejoindre une compagnie</h2>
                <p className="text-gray-600">
                  Votre compagnie existe déjà ? Envoyez une demande d'accès à l'administrateur.
                </p>
              </div>
            </button>
          </div>
        )}

        {/* Formulaire de création */}
        {mode === 'create' && (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <button
              onClick={() => setMode(null)}
              className="mb-6 text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Retour
            </button>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <form onSubmit={handleCreateCompany} className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Créer votre compagnie</h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom de la compagnie *
                </label>
                <input
                  type="text"
                  required
                  value={newCompany.nom_compagnie}
                  onChange={(e) => setNewCompany(prev => ({ ...prev, nom_compagnie: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Ex: Immobilier ABC Inc."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email de la compagnie
                  </label>
                  <input
                    type="email"
                    value={newCompany.email_compagnie}
                    onChange={(e) => setNewCompany(prev => ({ ...prev, email_compagnie: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="contact@compagnie.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Téléphone
                  </label>
                  <input
                    type="tel"
                    value={newCompany.telephone_compagnie}
                    onChange={(e) => setNewCompany(prev => ({ ...prev, telephone_compagnie: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="514-555-5555"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Adresse
                </label>
                <input
                  type="text"
                  value={newCompany.adresse_compagnie}
                  onChange={(e) => setNewCompany(prev => ({ ...prev, adresse_compagnie: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="123 rue Principale, Montréal, QC"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Site web
                  </label>
                  <input
                    type="url"
                    value={newCompany.site_web}
                    onChange={(e) => setNewCompany(prev => ({ ...prev, site_web: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="https://www.compagnie.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Numéro d'entreprise (NEQ)
                  </label>
                  <input
                    type="text"
                    value={newCompany.numero_entreprise}
                    onChange={(e) => setNewCompany(prev => ({ ...prev, numero_entreprise: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="1234567890"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mx-auto" />
                ) : (
                  'Créer la compagnie'
                )}
              </button>
            </form>
          </div>
        )}

        {/* Formulaire de recherche et demande */}
        {mode === 'join' && (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <button
              onClick={() => setMode(null)}
              className="mb-6 text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Retour
            </button>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <h2 className="text-2xl font-bold text-gray-900 mb-6">Rejoindre une compagnie</h2>

            {/* Recherche */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rechercher une compagnie
              </label>
              <div className="flex space-x-3">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && searchCompanies()}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Nom de la compagnie"
                  />
                </div>
                <button
                  type="button"
                  onClick={searchCompanies}
                  disabled={loading}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
                >
                  Rechercher
                </button>
              </div>
            </div>

            {/* Résultats */}
            {companies.length > 0 && (
              <div className="mb-6 space-y-3">
                <p className="text-sm font-medium text-gray-700">Résultats ({companies.length})</p>
                {companies.map(company => (
                  <button
                    key={company.id_compagnie}
                    onClick={() => setSelectedCompany(company)}
                    className={`w-full p-4 border-2 rounded-lg text-left transition-colors ${
                      selectedCompany?.id_compagnie === company.id_compagnie
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{company.nom_compagnie}</div>
                    {company.adresse_compagnie && (
                      <div className="text-sm text-gray-600 mt-1">{company.adresse_compagnie}</div>
                    )}
                  </button>
                ))}
              </div>
            )}

            {/* Formulaire de demande */}
            {selectedCompany && (
              <form onSubmit={handleJoinCompany} className="space-y-6 pt-6 border-t">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Votre rôle *
                  </label>
                  <select
                    required
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="employe">Employé</option>
                    <option value="admin">Administrateur</option>
                  </select>
                  <p className="mt-2 text-sm text-gray-500">
                    {role === 'admin' 
                      ? "Les administrateurs ont accès à toutes les fonctionnalités" 
                      : "Les employés n'ont accès qu'à l'onglet Employés"}
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mx-auto" />
                  ) : (
                    'Envoyer la demande'
                  )}
                </button>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

