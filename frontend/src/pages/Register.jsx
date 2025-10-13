import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserPlus, Mail, Lock, User, Phone, Calendar, Briefcase, Building2, AlertCircle, CheckCircle } from 'lucide-react'
import api from '../services/api'

export default function Register() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1) // 1: infos de base, 2: infos supplémentaires, 3: vérification email
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    nom: '',
    prenom: '',
    telephone: '',
    date_de_naissance: '',
    age: '',
    sexe: '',
    poste: '',
    role: 'employe', // Par défaut employé
    code_acces: '' // Code d'accès à la compagnie
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [userId, setUserId] = useState(null)

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setError('')
    
    // Calculer automatiquement l'âge si date de naissance change
    if (field === 'date_de_naissance' && value) {
      const birthDate = new Date(value)
      const today = new Date()
      let age = today.getFullYear() - birthDate.getFullYear()
      const monthDiff = today.getMonth() - birthDate.getMonth()
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--
      }
      setFormData(prev => ({ ...prev, age: age.toString() }))
    }
  }

  const validateStep1 = () => {
    if (!formData.email || !formData.email.includes('@')) {
      setError('Email invalide')
      return false
    }
    if (!formData.password || formData.password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères')
      return false
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      return false
    }
    if (!formData.nom || !formData.prenom) {
      setError('Nom et prénom sont obligatoires')
      return false
    }
    if (!formData.code_acces || formData.code_acces.length < 6) {
      setError('Code d\'accès à la compagnie requis (format: XXX-XXX)')
      return false
    }
    return true
  }

  const handleStep1Submit = () => {
    if (validateStep1()) {
      setStep(2)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const registerData = {
        email: formData.email,
        mot_de_passe: formData.password,
        nom: formData.nom,
        prenom: formData.prenom,
        telephone: formData.telephone || null,
        date_naissance: formData.date_de_naissance || null,
        sexe: formData.sexe || null,
        poste: formData.poste || null
      }

      const response = await api.post('/api/auth/register', registerData)
      
      setUserId(response.data.user_id)
      setStep(3) // Passer à l'étape de vérification email
    } catch (err) {
      console.error('Erreur d\'inscription:', err)
      if (err.response?.status === 400 && err.response?.data?.detail?.includes('existe déjà')) {
        setError('Cet email est déjà utilisé')
      } else {
        setError(err.response?.data?.detail || 'Erreur lors de l\'inscription. Veuillez réessayer.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyEmail = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Vérifier l'email
      await api.post('/api/auth/verify-email', {
        email: formData.email,
        code: verificationCode
      })

      // Sauvegarder le token reçu directement de la vérification
      const { access_token } = response.data
      localStorage.setItem('auth_token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      // Rejoindre automatiquement la compagnie avec le code d'accès
      await api.post('/api/auth/setup-company', {
        action: 'join',
        code_acces: formData.code_acces,
        role: formData.role
      })

      // Rediriger vers une page d'attente d'approbation
      navigate('/pending-approval', { 
        state: { 
          email: formData.email,
          role: formData.role 
        } 
      })
    } catch (err) {
      console.error('Erreur de vérification:', err)
      if (err.response?.status === 400) {
        setError('Code de vérification invalide ou expiré')
      } else {
        setError(err.response?.data?.detail || 'Erreur lors de la vérification')
      }
    } finally {
      setLoading(false)
    }
  }

  const resendVerificationCode = async () => {
    setLoading(true)
    try {
      await api.post('/api/auth/resend-verification', { email: formData.email })
      setError('')
      alert('Un nouveau code de vérification a été envoyé à votre email')
    } catch (err) {
      setError('Erreur lors de l\'envoi du code')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Logo / Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4">
            <Building2 className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Interface CAH</h1>
          <p className="text-gray-600">Créer un nouveau compte</p>
        </div>

        {/* Indicateur d'étapes */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'
              }`}>1</div>
              <span className="ml-2 text-sm font-medium hidden sm:inline">Informations</span>
            </div>
            <div className="w-8 h-px bg-gray-300" />
            <div className={`flex items-center ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'
              }`}>2</div>
              <span className="ml-2 text-sm font-medium hidden sm:inline">Détails</span>
            </div>
            <div className="w-8 h-px bg-gray-300" />
            <div className={`flex items-center ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200'
              }`}>3</div>
              <span className="ml-2 text-sm font-medium hidden sm:inline">Vérification</span>
            </div>
          </div>
        </div>

        {/* Formulaire d'inscription */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Étape 1: Informations de base */}
          {step === 1 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Informations de base</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Prénom *</label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      required
                      value={formData.prenom}
                      onChange={(e) => handleChange('prenom', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Jean"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nom *</label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      required
                      value={formData.nom}
                      onChange={(e) => handleChange('nom', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Dupont"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="jean.dupont@exemple.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Mot de passe *</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="password"
                    required
                    value={formData.password}
                    onChange={(e) => handleChange('password', e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Minimum 8 caractères"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Confirmer le mot de passe *</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="password"
                    required
                    value={formData.confirmPassword}
                    onChange={(e) => handleChange('confirmPassword', e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Confirmez votre mot de passe"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Code d'accès compagnie *</label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    required
                    value={formData.code_acces}
                    onChange={(e) => handleChange('code_acces', e.target.value.toUpperCase())}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="YRX-6HF"
                    maxLength={7}
                  />
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  Demandez ce code à votre administrateur principal
                </p>
              </div>

              <button
                type="button"
                onClick={handleStep1Submit}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                Continuer
              </button>
            </div>
          )}

          {/* Étape 2: Informations supplémentaires */}
          {step === 2 && (
            <form onSubmit={handleRegister} className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Informations supplémentaires</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Téléphone</label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="tel"
                      value={formData.telephone}
                      onChange={(e) => handleChange('telephone', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="514-555-5555"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date de naissance</label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="date"
                      value={formData.date_de_naissance}
                      onChange={(e) => handleChange('date_de_naissance', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Sexe</label>
                  <select
                    value={formData.sexe}
                    onChange={(e) => handleChange('sexe', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Sélectionner</option>
                    <option value="homme">Homme</option>
                    <option value="femme">Femme</option>
                    <option value="autre">Autre</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Poste</label>
                  <div className="relative">
                    <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      value={formData.poste}
                      onChange={(e) => handleChange('poste', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Gestionnaire immobilier"
                    />
                  </div>
                </div>
              </div>

              {/* Choix du rôle */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <label className="block text-sm font-medium text-gray-900 mb-3">
                  Rôle souhaité dans CAH Immobilier *
                </label>
                <div className="space-y-3">
                  <label className="flex items-center p-3 bg-white border-2 border-gray-200 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
                    <input
                      type="radio"
                      name="role"
                      value="employe"
                      checked={formData.role === 'employe'}
                      onChange={(e) => handleChange('role', e.target.value)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                    />
                    <div className="ml-3">
                      <div className="font-medium text-gray-900">Employé</div>
                      <div className="text-sm text-gray-600">Accès limité aux fonctionnalités employés</div>
                    </div>
                  </label>
                  <label className="flex items-center p-3 bg-white border-2 border-gray-200 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
                    <input
                      type="radio"
                      name="role"
                      value="admin"
                      checked={formData.role === 'admin'}
                      onChange={(e) => handleChange('role', e.target.value)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                    />
                    <div className="ml-3">
                      <div className="font-medium text-gray-900">Administrateur</div>
                      <div className="text-sm text-gray-600">Accès complet à toutes les fonctionnalités</div>
                    </div>
                  </label>
                </div>
                <p className="mt-3 text-xs text-gray-600">
                  ⓘ Votre demande sera soumise à l'approbation de l'administrateur principal
                </p>
              </div>

              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                  disabled={loading}
                >
                  Retour
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                  ) : (
                    <>
                      <UserPlus className="h-5 w-5" />
                      <span>S'inscrire</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          )}

          {/* Étape 3: Vérification email */}
          {step === 3 && (
            <div className="space-y-6">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Vérifiez votre email</h2>
                <p className="text-gray-600 mb-6">
                  Un code de vérification a été envoyé à <strong>{formData.email}</strong>
                </p>
              </div>

              <form onSubmit={handleVerifyEmail} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Code de vérification</label>
                  <input
                    type="text"
                    required
                    maxLength={6}
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-center text-2xl tracking-widest"
                    placeholder="000000"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading || verificationCode.length !== 6}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mx-auto" />
                  ) : (
                    'Vérifier'
                  )}
                </button>

                <div className="text-center">
                  <button
                    type="button"
                    onClick={resendVerificationCode}
                    disabled={loading}
                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Renvoyer le code
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Lien vers connexion */}
          {step < 3 && (
            <div className="mt-6 pt-6 border-t border-gray-200 text-center">
              <p className="text-sm text-gray-600">
                Vous avez déjà un compte ?{' '}
                <button
                  onClick={() => navigate('/login')}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                  disabled={loading}
                >
                  Se connecter
                </button>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

