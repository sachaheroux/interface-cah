import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Lock, ArrowLeft, CheckCircle, AlertCircle, Building2, Mail } from 'lucide-react'
import api from '../services/api'

export default function ResetPassword() {
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    // Récupérer l'email depuis l'état de navigation ou le prompt
    if (location.state?.email) {
      setEmail(location.state.email)
    } else {
      // Si pas d'email dans l'état, demander à l'utilisateur
      const emailInput = prompt('Veuillez entrer votre adresse email :')
      if (emailInput) {
        setEmail(emailInput)
      } else {
        navigate('/forgot-password')
      }
    }
  }, [location, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validation
    if (code.length !== 6) {
      setError('Le code doit contenir 6 caractères')
      return
    }

    if (newPassword.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères')
      return
    }

    if (newPassword !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      return
    }

    setLoading(true)

    try {
      const response = await api.post('/api/auth/reset-password', {
        email: email.trim(),
        code: code.trim(),
        nouveau_mot_de_passe: newPassword
      })

      if (response.data.success) {
        setSuccess(true)
        // Rediriger vers login après 3 secondes
        setTimeout(() => {
          navigate('/login')
        }, 3000)
      } else {
        setError(response.data.message || 'Une erreur est survenue')
      }
    } catch (err) {
      console.error('Erreur réinitialisation:', err)
      if (err.response?.status === 400) {
        setError(err.response.data.detail || 'Code incorrect ou expiré')
      } else {
        setError(err.response?.data?.detail || 'Erreur lors de la réinitialisation. Veuillez réessayer.')
      }
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Mot de passe réinitialisé !</h2>
            <p className="text-gray-600 mb-6">
              Votre mot de passe a été modifié avec succès. Vous allez être redirigé vers la page de connexion.
            </p>
            <button
              onClick={() => navigate('/login')}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              Aller à la connexion
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo / Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4">
            <Building2 className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Interface CAH</h1>
          <p className="text-gray-600">Réinitialisation du mot de passe</p>
        </div>

        {/* Formulaire */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Nouveau mot de passe</h2>
          <p className="text-gray-600 mb-6">
            Entrez le code reçu par email et votre nouveau mot de passe.
          </p>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email (affiché mais non modifiable) */}
            {email && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    value={email}
                    disabled
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                  />
                </div>
              </div>
            )}

            {/* Code de réinitialisation */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Code de réinitialisation
              </label>
              <input
                type="text"
                required
                value={code}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '').slice(0, 6)
                  setCode(value)
                  setError('')
                }}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-center text-2xl tracking-widest font-mono"
                placeholder="000000"
                maxLength={6}
                disabled={loading}
              />
              <p className="mt-2 text-xs text-gray-500">
                Entrez le code à 6 chiffres reçu par email
              </p>
            </div>

            {/* Nouveau mot de passe */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nouveau mot de passe
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => {
                    setNewPassword(e.target.value)
                    setError('')
                  }}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  placeholder="••••••••"
                  minLength={8}
                  disabled={loading}
                />
              </div>
              <p className="mt-2 text-xs text-gray-500">
                Minimum 8 caractères
              </p>
            </div>

            {/* Confirmation mot de passe */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirmer le mot de passe
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value)
                    setError('')
                  }}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  placeholder="••••••••"
                  minLength={8}
                  disabled={loading}
                />
              </div>
            </div>

            {/* Bouton de réinitialisation */}
            <button
              type="submit"
              disabled={loading || !email || !code || !newPassword || !confirmPassword}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
              ) : (
                <span>Réinitialiser le mot de passe</span>
              )}
            </button>
          </form>

          {/* Liens */}
          <div className="mt-6 pt-6 border-t border-gray-200 space-y-3">
            <button
              onClick={() => navigate('/forgot-password')}
              className="w-full text-sm text-blue-600 hover:text-blue-800 font-medium"
              disabled={loading}
            >
              Renvoyer le code
            </button>
            <button
              onClick={() => navigate('/login')}
              className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
              disabled={loading}
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Retour à la connexion</span>
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>© 2025 Interface CAH. Tous droits réservés.</p>
        </div>
      </div>
    </div>
  )
}

