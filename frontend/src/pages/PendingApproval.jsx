import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Clock, Mail, Building2, LogOut } from 'lucide-react'

export default function PendingApproval() {
  const navigate = useNavigate()
  const location = useLocation()
  const { email, role } = location.state || {}

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    navigate('/login')
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
        </div>

        {/* Message d'attente */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-yellow-100 rounded-full mb-4">
              <Clock className="h-8 w-8 text-yellow-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">En attente d'approbation</h2>
            <p className="text-gray-600">
              Votre demande d'accès à <strong>CAH Immobilier</strong> a été envoyée avec succès
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start space-x-3">
              <Mail className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-gray-700 mb-2">
                  <strong>Rôle demandé :</strong> {role === 'admin' ? 'Administrateur' : 'Employé'}
                </p>
                <p className="text-sm text-gray-700">
                  <strong>Email :</strong> {email}
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Prochaines étapes :</h3>
              <ol className="list-decimal list-inside space-y-2 text-sm text-gray-600">
                <li>L'administrateur principal recevra un email de notification</li>
                <li>Il examinera votre demande et vos informations</li>
                <li>Vous recevrez un email de confirmation une fois approuvé</li>
                <li>Vous pourrez ensuite vous connecter et accéder au système</li>
              </ol>
            </div>

            <div className="text-center text-sm text-gray-500">
              <p>Cela peut prendre quelques heures à quelques jours</p>
            </div>

            <button
              onClick={handleLogout}
              className="w-full bg-gray-100 text-gray-700 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors flex items-center justify-center space-x-2"
            >
              <LogOut className="h-5 w-5" />
              <span>Retour à la connexion</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

