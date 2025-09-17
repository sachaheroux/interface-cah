import React, { useState, useEffect } from 'react'
import { X, Calendar, DollarSign, FileText, Save, AlertCircle } from 'lucide-react'

const LeaseForm = ({ 
  isOpen, 
  onClose, 
  onSave, 
  tenant, 
  unit, 
  lease = null 
}) => {
  const [formData, setFormData] = useState({
    date_debut: '',
    date_fin: '',
    prix_loyer: 0,
    methode_paiement: 'Virement bancaire',
    pdf_bail: ''
  })
  
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  // Méthodes de paiement disponibles
  const paymentMethods = [
    'Virement bancaire',
    'Chèque',
    'Espèces',
    'Prélèvement automatique'
  ]

  // Initialiser le formulaire
  useEffect(() => {
    if (lease) {
      setFormData({
        date_debut: lease.date_debut || '',
        date_fin: lease.date_fin || '',
        prix_loyer: lease.prix_loyer || 0,
        methode_paiement: lease.methode_paiement || 'Virement bancaire',
        pdf_bail: lease.pdf_bail || ''
      })
    } else {
      setFormData({
        date_debut: '',
        date_fin: '',
        prix_loyer: 0,
        methode_paiement: 'Virement bancaire',
        pdf_bail: ''
      })
    }
    setErrors({})
  }, [lease, isOpen])

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    
    // Effacer l'erreur du champ modifié
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.date_debut.trim()) {
      newErrors.date_debut = 'La date de début est obligatoire'
    }
    
    if (!formData.date_fin.trim()) {
      newErrors.date_fin = 'La date de fin est obligatoire'
    }
    
    if (formData.date_debut && formData.date_fin) {
      const startDate = new Date(formData.date_debut)
      const endDate = new Date(formData.date_fin)
      
      if (startDate >= endDate) {
        newErrors.date_fin = 'La date de fin doit être après la date de début'
      }
    }
    
    if (formData.prix_loyer <= 0) {
      newErrors.prix_loyer = 'Le prix du loyer doit être supérieur à 0'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }
    
    setLoading(true)
    
    try {
      const leaseData = {
        id_locataire: tenant.id_locataire,
        date_debut: formData.date_debut,
        date_fin: formData.date_fin,
        prix_loyer: parseFloat(formData.prix_loyer),
        methode_paiement: formData.methode_paiement,
        pdf_bail: formData.pdf_bail
      }
      
      console.log('💾 Données de bail à sauvegarder:', leaseData)
      
      if (lease) {
        // Mise à jour d'un bail existant
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/leases/${lease.id_bail}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(leaseData)
        })
        
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Erreur mise à jour: ${response.status} - ${errorText}`)
        }
        
        const result = await response.json()
        console.log('✅ Bail mis à jour:', result)
        
      } else {
        // Création d'un nouveau bail
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/leases`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(leaseData)
        })
        
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Erreur création: ${response.status} - ${errorText}`)
        }
        
        const result = await response.json()
        console.log('✅ Bail créé:', result)
      }
      
      onSave()
      onClose()
      
    } catch (error) {
      console.error('❌ Erreur lors de la sauvegarde:', error)
      setErrors({ submit: error.message })
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <FileText className="h-6 w-6 text-primary-600" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {lease ? 'Modifier le bail' : 'Nouveau bail'}
              </h2>
              <p className="text-sm text-gray-600">
                {tenant?.nom} {tenant?.prenom} - {unit?.adresse_unite}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Dates */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="h-4 w-4 inline mr-2" />
                Date de début *
              </label>
              <input
                type="date"
                value={formData.date_debut}
                onChange={(e) => handleChange('date_debut', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                  errors.date_debut ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.date_debut && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.date_debut}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="h-4 w-4 inline mr-2" />
                Date de fin *
              </label>
              <input
                type="date"
                value={formData.date_fin}
                onChange={(e) => handleChange('date_fin', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                  errors.date_fin ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.date_fin && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.date_fin}
                </p>
              )}
            </div>
          </div>

          {/* Prix et méthode de paiement */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <DollarSign className="h-4 w-4 inline mr-2" />
                Prix du loyer (CAD) *
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.prix_loyer}
                onChange={(e) => handleChange('prix_loyer', parseFloat(e.target.value) || 0)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                  errors.prix_loyer ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="0.00"
              />
              {errors.prix_loyer && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.prix_loyer}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Méthode de paiement
              </label>
              <select
                value={formData.methode_paiement}
                onChange={(e) => handleChange('methode_paiement', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                {paymentMethods.map(method => (
                  <option key={method} value={method}>
                    {method}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* PDF du bail */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <FileText className="h-4 w-4 inline mr-2" />
              PDF du bail (optionnel)
            </label>
            <input
              type="text"
              value={formData.pdf_bail}
              onChange={(e) => handleChange('pdf_bail', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Nom du fichier PDF"
            />
          </div>

          {/* Erreur générale */}
          {errors.submit && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
                <p className="text-sm text-red-600">{errors.submit}</p>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Sauvegarde...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {lease ? 'Mettre à jour' : 'Créer le bail'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default LeaseForm
