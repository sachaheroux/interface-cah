import React, { useState, useEffect } from 'react'
import { Settings as SettingsIcon, User, Shield, Bell, Database, Moon, Sun, Mail, Lock, Building2, Copy, Check } from 'lucide-react'
import { useTheme } from '../hooks/useTheme'
import api from '../services/api'

export default function Settings() {
  const { theme, toggleTheme } = useTheme()
  const [user, setUser] = useState(null)
  const [company, setCompany] = useState(null)
  const [loading, setLoading] = useState(true)
  
  // États pour changer email/mot de passe
  const [showEmailForm, setShowEmailForm] = useState(false)
  const [showPasswordForm, setShowPasswordForm] = useState(false)
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
        setShowEmailForm(false)
        setNewEmail('')
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
        setShowPasswordForm(false)
        setCurrentPassword('')
        setNewPassword('')
        setConfirmPassword('')
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

      {/* Section Changer email/mot de passe */}
      <div className="card dark:bg-gray-800 dark:border-gray-700">
        <div className="flex items-center mb-4">
          <Shield className="h-6 w-6 text-green-500 mr-3" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Sécurité du compte</h3>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Modifiez votre adresse courriel ou votre mot de passe pour sécuriser votre compte.
        </p>

        <div className="space-y-4">
          {/* Changer email */}
          <div>
            <button
              onClick={() => setShowEmailForm(!showEmailForm)}
              className="btn-secondary w-full sm:w-auto"
            >
              <Mail className="h-4 w-4 mr-2" />
              {showEmailForm ? 'Annuler' : 'Changer l\'adresse courriel'}
            </button>
            
            {showEmailForm && (
              <form onSubmit={handleChangeEmail} className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Nouvelle adresse courriel
                  </label>
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    placeholder={user?.email || 'votre@email.com'}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
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
                      setShowEmailForm(false)
                      setNewEmail('')
                    }}
                    className="btn-secondary"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* Changer mot de passe */}
          <div>
            <button
              onClick={() => setShowPasswordForm(!showPasswordForm)}
              className="btn-secondary w-full sm:w-auto"
            >
              <Lock className="h-4 w-4 mr-2" />
              {showPasswordForm ? 'Annuler' : 'Changer le mot de passe'}
            </button>
            
            {showPasswordForm && (
              <form onSubmit={handleChangePassword} className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Mot de passe actuel
                  </label>
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Nouveau mot de passe
                  </label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Confirmer le nouveau mot de passe
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
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
                      setShowPasswordForm(false)
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
            )}
          </div>
        </div>
      </div>

      {/* Section Informations de l'entreprise */}
      <div className="card dark:bg-gray-800 dark:border-gray-700">
        <div className="flex items-center mb-4">
          <Building2 className="h-6 w-6 text-blue-500 mr-3" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Informations de l'entreprise</h3>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Consultez les informations de votre entreprise et partagez le code d'accès pour inviter de nouveaux membres.
        </p>

        {company ? (
          <div className="space-y-4">
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
            <div className="mt-6 p-4 bg-primary-50 dark:bg-primary-900 rounded-lg border border-primary-200 dark:border-primary-800">
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

      {/* Section Notifications */}
      <div className="card dark:bg-gray-800 dark:border-gray-700">
        <div className="flex items-center mb-4">
          <Bell className="h-6 w-6 text-yellow-500 mr-3" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Notifications</h3>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Consultez l'historique de toutes vos notifications.
        </p>
        <div className="text-center py-8 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
          <Bell className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            L'historique des notifications sera disponible prochainement.
          </p>
        </div>
      </div>

      {/* Section Sauvegarde */}
      <div className="card dark:bg-gray-800 dark:border-gray-700">
        <div className="flex items-center mb-4">
          <Database className="h-6 w-6 text-purple-500 mr-3" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Sauvegarde</h3>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Gérez les sauvegardes et la restauration des données.
        </p>
        <div className="space-y-4">
          <button className="btn-primary">
            <Database className="h-4 w-4 mr-2" />
            Créer une sauvegarde
          </button>
          <button className="btn-secondary">
            Restaurer depuis une sauvegarde
          </button>
        </div>
      </div>
    </div>
  )
}
