import React, { useState, useEffect } from 'react'
import { Shield, Bell, Database, Moon, Sun, Mail, Lock, Building2, Copy, Check, X, AlertCircle, DollarSign, FileText, Users, Calendar, Loader } from 'lucide-react'
import { useTheme } from '../hooks/useTheme'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { notificationsService } from '../services/api'

export default function Settings() {
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [company, setCompany] = useState(null)
  const [loading, setLoading] = useState(true)
  
  // États pour les modals
  const [openModal, setOpenModal] = useState(null) // 'security', 'company', 'notifications', 'backup'
  
  // États pour les notifications
  const [notifications, setNotifications] = useState([])
  const [loadingNotifications, setLoadingNotifications] = useState(false)
  const [filter, setFilter] = useState('all') // 'all', 'unread', 'read'
  
  // États pour changer email/mot de passe
  const [newEmail, setNewEmail] = useState('')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [codeCopied, setCodeCopied] = useState(false)

  useEffect(() => {
    // Récupérer les infos utilisateur depuis localStorage
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const userData = JSON.parse(userStr)
        setUser(userData)
        // Charger les infos de l'entreprise si l'utilisateur a une compagnie
        if (userData.id_compagnie) {
          fetchCompanyInfo()
        } else {
          setLoading(false)
        }
      } catch (e) {
        console.error('Erreur parsing user:', e)
        setLoading(false)
      }
    } else {
      setLoading(false)
    }
  }, [])

  const fetchCompanyInfo = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      const response = await api.get('/api/auth/company', {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (response.data.success) {
        setCompany(response.data.data)
      }
      setLoading(false)
    } catch (error) {
      console.error('Erreur lors du chargement des infos de l\'entreprise:', error)
      setLoading(false)
    }
  }

  const handleChangeEmail = async (e) => {
    e.preventDefault()
    if (!newEmail || newEmail === user?.email) {
      alert('Veuillez entrer une nouvelle adresse email différente de l\'actuelle')
      return
    }
    
    try {
      const token = localStorage.getItem('auth_token')
      // Pour changer l'email, on a besoin du mot de passe actuel
      const password = prompt('Veuillez entrer votre mot de passe actuel pour confirmer:')
      if (!password) return
      
      const response = await api.put('/api/auth/email', {
        nouveau_email: newEmail,
        mot_de_passe: password
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.data.success) {
        alert('Email mis à jour avec succès! Un code de vérification a été envoyé à votre nouvelle adresse.')
        // Mettre à jour les infos utilisateur dans localStorage
        localStorage.setItem('user', JSON.stringify(response.data.user))
        setUser(response.data.user)
        setNewEmail('')
        setOpenModal(null)
      }
    } catch (error) {
      alert(error.response?.data?.detail || 'Erreur lors du changement d\'email')
    }
  }

  const handleChangePassword = async (e) => {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      alert('Les mots de passe ne correspondent pas')
      return
    }
    
    if (!currentPassword) {
      alert('Veuillez entrer votre mot de passe actuel')
      return
    }
    
    try {
      const token = localStorage.getItem('auth_token')
      const response = await api.put('/api/auth/password', {
        mot_de_passe_actuel: currentPassword,
        nouveau_mot_de_passe: newPassword
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.data.success) {
        alert('Mot de passe mis à jour avec succès!')
        setCurrentPassword('')
        setNewPassword('')
        setConfirmPassword('')
        setOpenModal(null)
      }
    } catch (error) {
      alert(error.response?.data?.detail || 'Erreur lors du changement de mot de passe')
    }
  }

  const copyCodeToClipboard = () => {
    if (company?.code_acces) {
      navigator.clipboard.writeText(company.code_acces)
      setCodeCopied(true)
      setTimeout(() => setCodeCopied(false), 2000)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const settingsCards = [
    {
      id: 'security',
      title: 'Sécurité du compte',
      description: 'Modifiez votre adresse courriel ou votre mot de passe',
      icon: Shield,
      color: 'text-green-500',
      bgColor: 'bg-green-50 dark:bg-green-900/20'
    },
    {
      id: 'company',
      title: 'Informations de l\'entreprise',
      description: 'Consultez les informations et le code d\'accès de votre entreprise',
      icon: Building2,
      color: 'text-blue-500',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20'
    },
    {
      id: 'notifications',
      title: 'Notifications',
      description: 'Consultez l\'historique de toutes vos notifications',
      icon: Bell,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/20'
    },
    {
      id: 'backup',
      title: 'Sauvegarde',
      description: 'Gérez les sauvegardes et la restauration des données',
      icon: Database,
      color: 'text-purple-500',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20'
    }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Mon profil</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Gérez vos paramètres personnels et les informations de votre entreprise</p>
      </div>

      {/* Section Apparence - Mode jour/nuit */}
      <div className="card dark:bg-gray-800 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            {theme === 'dark' ? (
              <Moon className="h-6 w-6 text-blue-500 mr-3" />
            ) : (
              <Sun className="h-6 w-6 text-yellow-500 mr-3" />
            )}
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Apparence</h3>
          </div>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Choisissez entre le mode jour et le mode nuit pour reposer vos yeux.
        </p>
        
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Mode {theme === 'dark' ? 'Nuit' : 'Jour'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {theme === 'dark' 
                ? 'Fond sombre pour réduire la fatigue oculaire' 
                : 'Fond clair pour une meilleure visibilité'}
            </p>
          </div>
          <button
            onClick={toggleTheme}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
              theme === 'dark' ? 'bg-blue-600' : 'bg-gray-300'
            }`}
            role="switch"
            aria-checked={theme === 'dark'}
            aria-label="Basculer le thème"
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                theme === 'dark' ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Grille de 4 cartes (2x2) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {settingsCards.map((card) => {
          const Icon = card.icon
          return (
            <button
              key={card.id}
              onClick={() => setOpenModal(card.id)}
              className="card dark:bg-gray-800 dark:border-gray-700 hover:shadow-lg transition-shadow text-left p-6"
            >
              <div className={`w-12 h-12 ${card.bgColor} rounded-lg flex items-center justify-center mb-4`}>
                <Icon className={`h-6 w-6 ${card.color}`} />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {card.title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {card.description}
              </p>
            </button>
          )
        })}
      </div>

      {/* Modal Sécurité du compte */}
      {openModal === 'security' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-full">
                  <Shield className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Sécurité du compte</h3>
              </div>
              <button
                onClick={() => {
                  setOpenModal(null)
                  setNewEmail('')
                  setCurrentPassword('')
                  setNewPassword('')
                  setConfirmPassword('')
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Changer email */}
              <div>
                <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Mail className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                  Changer l'adresse courriel
                </h4>
                <form onSubmit={handleChangeEmail} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Nouvelle adresse courriel
                    </label>
                    <input
                      type="email"
                      value={newEmail}
                      onChange={(e) => setNewEmail(e.target.value)}
                      placeholder={user?.email || 'votre@email.com'}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      required
                    />
                  </div>
                  <div className="flex space-x-2">
                    <button type="submit" className="btn-primary">
                      Enregistrer
                    </button>
                    <button
                      type="button"
                      onClick={() => setNewEmail('')}
                      className="btn-secondary"
                    >
                      Annuler
                    </button>
                  </div>
                </form>
              </div>

              <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                {/* Changer mot de passe */}
                <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Lock className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                  Changer le mot de passe
                </h4>
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Mot de passe actuel
                    </label>
                    <input
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Nouveau mot de passe
                    </label>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Confirmer le nouveau mot de passe
                    </label>
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      required
                    />
                  </div>
                  <div className="flex space-x-2">
                    <button type="submit" className="btn-primary">
                      Enregistrer
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setCurrentPassword('')
                        setNewPassword('')
                        setConfirmPassword('')
                      }}
                      className="btn-secondary"
                    >
                      Annuler
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal Informations de l'entreprise */}
      {openModal === 'company' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-full">
                  <Building2 className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Informations de l'entreprise</h3>
              </div>
              <button
                onClick={() => setOpenModal(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6">
              {company ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Nom de l'entreprise
                      </label>
                      <p className="text-gray-900 dark:text-white">{company.nom_compagnie}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Email de l'entreprise
                      </label>
                      <p className="text-gray-900 dark:text-white">{company.email_compagnie}</p>
                    </div>
                    {company.telephone_compagnie && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Téléphone
                        </label>
                        <p className="text-gray-900 dark:text-white">{company.telephone_compagnie}</p>
                      </div>
                    )}
                    {company.numero_entreprise && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Numéro d'entreprise
                        </label>
                        <p className="text-gray-900 dark:text-white">{company.numero_entreprise}</p>
                      </div>
                    )}
                    {company.adresse_compagnie && (
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Adresse
                        </label>
                        <p className="text-gray-900 dark:text-white">{company.adresse_compagnie}</p>
                      </div>
                    )}
                  </div>

                  {/* Code d'accès */}
                  <div className="mt-6 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-primary-900 dark:text-primary-300 mb-2">
                          Code d'accès à partager
                        </label>
                        <p className="text-xs text-primary-700 dark:text-primary-400 mb-2">
                          Partagez ce code avec les personnes que vous souhaitez inviter à rejoindre votre entreprise.
                        </p>
                        <div className="flex items-center space-x-2">
                          <code className="px-4 py-2 bg-white dark:bg-gray-800 border border-primary-300 dark:border-primary-700 rounded-lg text-lg font-mono font-bold text-primary-900 dark:text-primary-300">
                            {company.code_acces}
                          </code>
                          <button
                            onClick={copyCodeToClipboard}
                            className="p-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                            title="Copier le code"
                          >
                            {codeCopied ? (
                              <Check className="h-5 w-5" />
                            ) : (
                              <Copy className="h-5 w-5" />
                            )}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Building2 className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400">
                    Aucune information d'entreprise disponible.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal Notifications */}
      {openModal === 'notifications' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-full">
                  <Bell className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Notifications</h3>
              </div>
              <button
                onClick={() => setOpenModal(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <NotificationsHistory 
              onClose={() => setOpenModal(null)}
              navigate={navigate}
            />
          </div>
        </div>
      )}

      {/* Modal Sauvegarde */}
      {openModal === 'backup' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-full">
                  <Database className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Sauvegarde</h3>
              </div>
              <button
                onClick={() => setOpenModal(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Gérez les sauvegardes et la restauration des données de votre application.
              </p>
              
              {/* Migration Bail ID_Unite */}
              <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <h4 className="text-sm font-semibold text-yellow-900 dark:text-yellow-300 mb-2">
                  Migration Base de Données
                </h4>
                <p className="text-xs text-yellow-800 dark:text-yellow-400 mb-3">
                  Migration : Ajouter id_unite à la table baux (pour garder l'historique des unités par bail)
                </p>
                <MigrationButton />
              </div>
              
              <div className="space-y-4">
                <button className="btn-primary w-full">
                  <Database className="h-4 w-4 mr-2" />
                  Créer une sauvegarde
                </button>
                <button className="btn-secondary w-full">
                  Restaurer depuis une sauvegarde
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Composant pour l'historique des notifications
function NotificationsHistory({ onClose, navigate }) {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // 'all', 'unread', 'read'

  useEffect(() => {
    loadNotifications()
  }, [filter])

  const loadNotifications = async () => {
    try {
      setLoading(true)
      const lue = filter === 'all' ? null : filter === 'read'
      const response = await notificationsService.getNotifications(lue, 100)
      if (response.data.success) {
        setNotifications(response.data.data || [])
      }
    } catch (error) {
      console.error('Erreur chargement notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkAsRead = async (notificationId) => {
    try {
      await notificationsService.markAsRead(notificationId)
      setNotifications(prev => prev.map(n => 
        n.id_notification === notificationId ? { ...n, lue: true } : n
      ))
    } catch (error) {
      console.error('Erreur marquer notification lue:', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await notificationsService.markAllAsRead()
      setNotifications(prev => prev.map(n => ({ ...n, lue: true })))
    } catch (error) {
      console.error('Erreur marquer toutes lues:', error)
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'loyer_non_paye':
        return <DollarSign className="h-5 w-5" />
      case 'facture_a_payer':
        return <FileText className="h-5 w-5" />
      case 'demande_acces':
        return <Users className="h-5 w-5" />
      case 'bail_expire':
        return <Calendar className="h-5 w-5" />
      default:
        return <AlertCircle className="h-5 w-5" />
    }
  }

  const getPriorityColor = (priorite) => {
    switch (priorite) {
      case 'urgent':
        return 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800'
      case 'important':
        return 'bg-orange-100 dark:bg-orange-900/20 text-orange-800 dark:text-orange-300 border-orange-200 dark:border-orange-800'
      default:
        return 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800'
    }
  }

  const unreadCount = notifications.filter(n => !n.lue).length

  return (
    <div className="p-6">
      {/* Filtres et actions */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            Toutes ({notifications.length})
          </button>
          <button
            onClick={() => setFilter('unread')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              filter === 'unread'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            Non lues ({unreadCount})
          </button>
          <button
            onClick={() => setFilter('read')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              filter === 'read'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            Lues ({notifications.length - unreadCount})
          </button>
        </div>
        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllAsRead}
            className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
          >
            Tout marquer comme lu
          </button>
        )}
      </div>

      {/* Liste des notifications */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-500 dark:text-gray-400">Chargement...</p>
        </div>
      ) : notifications.length === 0 ? (
        <div className="text-center py-12">
          <Bell className="h-16 w-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Aucune notification
          </h4>
          <p className="text-gray-500 dark:text-gray-400">
            {filter === 'unread' 
              ? 'Vous n\'avez aucune notification non lue'
              : filter === 'read'
              ? 'Vous n\'avez aucune notification lue'
              : 'Vous n\'avez pas encore de notifications'}
          </p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[60vh] overflow-y-auto">
          {notifications.map((notif) => (
            <div
              key={notif.id_notification}
              className={`p-4 rounded-lg border transition-colors cursor-pointer ${
                !notif.lue
                  ? 'bg-blue-50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800'
                  : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
              onClick={() => {
                if (!notif.lue) {
                  handleMarkAsRead(notif.id_notification)
                }
                if (notif.lien) {
                  navigate(notif.lien)
                  onClose()
                }
              }}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className={`p-2 rounded-lg ${
                    !notif.lue ? 'bg-blue-100 dark:bg-blue-900/30' : 'bg-gray-100 dark:bg-gray-700'
                  }`}>
                    {getTypeIcon(notif.type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getPriorityColor(notif.priorite)}`}>
                        {notif.priorite === 'urgent' ? 'Urgent' : notif.priorite === 'important' ? 'Important' : 'Info'}
                      </span>
                      {!notif.lue && (
                        <span className="h-2 w-2 bg-blue-500 rounded-full"></span>
                      )}
                    </div>
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                      {notif.titre}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {notif.message}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      {new Date(notif.date_creation).toLocaleDateString('fr-CA', {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// Composant pour le bouton de migration
function MigrationButton() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleMigration = async () => {
    if (!window.confirm('Êtes-vous sûr de vouloir exécuter cette migration ?\n\nUne sauvegarde sera créée automatiquement avant la migration.')) {
      return
    }

    setLoading(true)
    setResult(null)

    try {
      const token = localStorage.getItem('auth_token')
      const response = await api.post('/api/migrate/bail-add-id-unite', {}, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 300000 // 5 minutes
      })

      setResult({
        success: response.data.success,
        message: response.data.message,
        details: response.data.details
      })
    } catch (error) {
      console.error('Erreur migration:', error)
      setResult({
        success: false,
        message: error.response?.data?.message || 'Erreur lors de la migration',
        details: error.response?.data?.error || error.message
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <button
        onClick={handleMigration}
        disabled={loading}
        className="w-full px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 text-white rounded-lg font-medium flex items-center justify-center transition-colors"
      >
        {loading ? (
          <>
            <Loader className="h-4 w-4 mr-2 animate-spin" />
            Migration en cours...
          </>
        ) : (
          <>
            <Database className="h-4 w-4 mr-2" />
            Exécuter la migration
          </>
        )}
      </button>

      {result && (
        <div className={`mt-3 p-3 rounded-lg ${
          result.success 
            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' 
            : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
        }`}>
          <p className={`text-sm font-medium ${
            result.success 
              ? 'text-green-900 dark:text-green-300' 
              : 'text-red-900 dark:text-red-300'
          }`}>
            {result.success ? '✅ Succès' : '❌ Erreur'}
          </p>
          <p className={`text-xs mt-1 ${
            result.success 
              ? 'text-green-800 dark:text-green-400' 
              : 'text-red-800 dark:text-red-400'
          }`}>
            {result.message}
          </p>
          {result.details && (
            <p className={`text-xs mt-1 ${
              result.success 
                ? 'text-green-700 dark:text-green-500' 
                : 'text-red-700 dark:text-red-500'
            }`}>
              {result.details}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
