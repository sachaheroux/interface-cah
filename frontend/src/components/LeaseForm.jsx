import React, { useState, useEffect } from 'react'
import { X, Save, FileText, Calendar, DollarSign, User, Home } from 'lucide-react'

export default function LeaseForm({ lease, isOpen, onClose, onSave }) {
  const [formData, setFormData] = useState({
    id_locataire: '',
    date_debut: '',
    date_fin: '',
    prix_loyer: 0,
    methode_paiement: 'Virement bancaire',
    pdf_bail: ''
  })

  const [loading, setLoading] = useState(false)
  const [availableTenants, setAvailableTenants] = useState([])
  const [availableUnits, setAvailableUnits] = useState([])

  // Charger les données
  useEffect(() => {
    if (isOpen) {
      loadTenants()
      loadUnits()
    }
  }, [isOpen])

  // Initialiser le formulaire
  useEffect(() => {
    if (lease) {
      setFormData({
        id_locataire: lease.id_locataire || '',
        date_debut: lease.date_debut || '',
        date_fin: lease.date_fin || '',
        prix_loyer: lease.prix_loyer || 0,
        methode_paiement: lease.methode_paiement || 'Virement bancaire',
        pdf_bail: lease.pdf_bail || ''
      })
    } else {
      setFormData({
        id_locataire: '',
        date_debut: '',
        date_fin: '',
        prix_loyer: 0,
        methode_paiement: 'Virement bancaire',
        pdf_bail: ''
      })
    }
  }, [lease, isOpen])

  const loadTenants = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/tenants`)
      if (response.ok) {
        const data = await response.json()
        setAvailableTenants(data.data || [])
      }
    } catch (error) {
      console.error('Erreur lors du chargement des locataires:', error)
    }
  }

  const loadUnits = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/units`)
      if (response.ok) {
        const data = await response.json()
        setAvailableUnits(data.data || [])
      }
    } catch (error) {
      console.error('Erreur lors du chargement des unités:', error)
    }
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const validateForm = () => {
    const errors = {}
    
    if (!formData.id_locataire) errors.id_locataire = 'Le locataire est obligatoire'
    if (!formData.date_debut) errors.date_debut = 'La date de début est obligatoire'
    if (!formData.date_fin) errors.date_fin = 'La date de fin est obligatoire'
    if (!formData.prix_loyer || formData.prix_loyer <= 0) errors.prix_loyer = 'Le prix du loyer doit être supérieur à 0'
    
    return errors
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const errors = validateForm()
    if (Object.keys(errors).length > 0) {
      console.error('Erreurs de validation:', errors)
      alert('Veuillez corriger les erreurs dans le formulaire')
      return
    }

    setLoading(true)
    
    try {
      const leaseData = {
        id_locataire: parseInt(formData.id_locataire),
        date_debut: formData.date_debut,
        date_fin: formData.date_fin,
        prix_loyer: parseFloat(formData.prix_loyer),
        methode_paiement: formData.methode_paiement,
        pdf_bail: formData.pdf_bail
      }

      console.log('💾 Données du bail à sauvegarder:', leaseData)

      if (lease?.id_bail) {
        // MISE À JOUR du bail existant
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
        // CRÉATION d'un nouveau bail
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
      alert(`Erreur lors de la sauvegarde: ${error.message}`)
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
                {lease ? 'Modifiez les informations du bail' : 'Créez un nouveau bail'}
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
          {/* Sélection du locataire */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <User className="h-4 w-4 inline mr-2" />
              Locataire *
            </label>
            <select
              value={formData.id_locataire}
              onChange={(e) => handleChange('id_locataire', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              required
            >
              <option value="">Sélectionner un locataire</option>
              {availableTenants.map((tenant) => (
                <option key={tenant.id_locataire} value={tenant.id_locataire}>
                  {tenant.nom} {tenant.prenom}
                </option>
              ))}
            </select>
          </div>

          {/* Dates du bail */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="h-4 w-4 inline mr-2" />
                Date de début *
              </label>
              <input
                type="date"
                value={formData.date_debut}
                onChange={(e) => handleChange('date_debut', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
              />
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
              />
            </div>
          </div>

          {/* Prix et méthode de paiement */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="0.00"
                required
              />
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
                <option value="Virement bancaire">Virement bancaire</option>
                <option value="Chèque">Chèque</option>
                <option value="Comptant">Comptant</option>
                <option value="Carte de crédit">Carte de crédit</option>
                <option value="Prélèvement automatique">Prélèvement automatique</option>
                <option value="Autre">Autre</option>
              </select>
            </div>
          </div>

          {/* PDF du bail */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              PDF du bail
            </label>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => {
                const file = e.target.files[0]
                if (file) {
                  handleChange('pdf_bail', file.name)
                }
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            {formData.pdf_bail && (
              <p className="text-sm text-green-600 mt-1">
                ✓ {formData.pdf_bail}
              </p>
            )}
          </div>

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