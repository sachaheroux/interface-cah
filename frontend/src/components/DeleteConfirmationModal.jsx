import React, { useState } from 'react'
import { AlertTriangle, X } from 'lucide-react'

export default function DeleteConfirmationModal({ 
  isOpen, 
  onClose, 
  onConfirm, 
  buildingName,
  buildingValue,
  loading = false 
}) {
  const [confirmationText, setConfirmationText] = useState('')
  const [step, setStep] = useState(1) // 1: Warning, 2: Confirmation input
  
  const expectedText = "SUPPRIMER"
  const isConfirmationValid = confirmationText.toUpperCase() === expectedText

  const handleClose = () => {
    setConfirmationText('')
    setStep(1)
    onClose()
  }

  const handleConfirm = () => {
    if (step === 1) {
      setStep(2)
    } else if (isConfirmationValid) {
      onConfirm()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-red-100 rounded-full">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Supprimer l'immeuble
            </h3>
          </div>
          <button
            onClick={handleClose}
            disabled={loading}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {step === 1 ? (
            // Step 1: Warning
            <div className="space-y-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h4 className="font-medium text-red-800 mb-2">⚠️ Action irréversible</h4>
                <p className="text-red-700 text-sm">
                  Vous êtes sur le point de supprimer définitivement cet immeuble. 
                  Cette action ne peut pas être annulée.
                </p>
              </div>
              
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h5 className="font-medium text-gray-800 mb-2">Immeuble à supprimer :</h5>
                <p className="text-gray-700">
                  <span className="font-medium">{buildingName}</span>
                </p>
                {buildingValue > 0 && (
                  <p className="text-gray-600 text-sm mt-1">
                    Valeur : {buildingValue.toLocaleString('fr-CA')}$
                  </p>
                )}
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h5 className="font-medium text-yellow-800 mb-2">Conséquences :</h5>
                <ul className="text-yellow-700 text-sm space-y-1">
                  <li>• Toutes les données de l'immeuble seront perdues</li>
                  <li>• La valeur du portfolio sera mise à jour</li>
                  <li>• Les statistiques seront recalculées</li>
                </ul>
              </div>
            </div>
          ) : (
            // Step 2: Confirmation input
            <div className="space-y-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 font-medium mb-2">
                  Pour confirmer la suppression, tapez exactement :
                </p>
                <p className="text-red-900 font-mono text-lg bg-red-100 px-3 py-2 rounded border">
                  {expectedText}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirmation de suppression
                </label>
                <input
                  type="text"
                  value={confirmationText}
                  onChange={(e) => setConfirmationText(e.target.value)}
                  placeholder="Tapez SUPPRIMER pour confirmer"
                  className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                    confirmationText && !isConfirmationValid
                      ? 'border-red-300 focus:ring-red-500 bg-red-50'
                      : confirmationText && isConfirmationValid
                      ? 'border-green-300 focus:ring-green-500 bg-green-50'
                      : 'border-gray-300 focus:ring-blue-500'
                  }`}
                  disabled={loading}
                  autoFocus
                />
                {confirmationText && !isConfirmationValid && (
                  <p className="text-red-600 text-sm mt-1">
                    Le texte ne correspond pas. Tapez exactement "SUPPRIMER".
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            onClick={handleClose}
            disabled={loading}
            className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
          >
            Annuler
          </button>
          
          {step === 1 ? (
            <button
              onClick={handleConfirm}
              disabled={loading}
              className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              Continuer
            </button>
          ) : (
            <button
              onClick={handleConfirm}
              disabled={loading || !isConfirmationValid}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Suppression...</span>
                </span>
              ) : (
                'Supprimer définitivement'
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
} 