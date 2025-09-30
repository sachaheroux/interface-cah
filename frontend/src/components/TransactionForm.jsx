import React, { useState, useEffect } from 'react'
import { X, Save, Building, DollarSign, Calendar, FileText, CreditCard, Tag, File, Search, Upload } from 'lucide-react'
import api from '../services/api'

export default function TransactionForm({ transaction, buildings, constants, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    id_immeuble: '',
    type: '',
    categorie: '',
    montant: '',
    date_de_transaction: '',
    methode_de_paiement: '',
    reference: '',
    source: '',
    pdf_transaction: '',
    notes: ''
  })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})
  const [buildingSearch, setBuildingSearch] = useState('')
  const [showBuildingDropdown, setShowBuildingDropdown] = useState(false)
  const [filteredBuildings, setFilteredBuildings] = useState([])

  // Catégories selon le type
  const getCategoriesByType = (type) => {
    if (type === 'revenu') {
      return ['Capital']
    } else if (type === 'depense') {
      return [
        'Assurances',
        'Frais d\'utilisation',
        'Frais fixes d\'utilisation',
        'Frais dépôt commercial',
        'Hydro Québec',
        'Frais crédit',
        'Intérêts',
        'Frais de gestion',
        'Taxes scolaires',
        'Taxes municipales',
        'Entretien',
        'Réparation mineure',
        'Réparation majeure',
        'Internet',
        'Fournitures'
      ]
    }
    return []
  }

  useEffect(() => {
    if (transaction) {
      setFormData({
        id_immeuble: transaction.id_immeuble || '',
        type: transaction.type || '',
        categorie: transaction.categorie || '',
        montant: transaction.montant || '',
        date_de_transaction: transaction.date_de_transaction || '',
        methode_de_paiement: transaction.methode_de_paiement || '',
        reference: transaction.reference || '',
        source: transaction.source || '',
        pdf_transaction: transaction.pdf_transaction || '',
        notes: transaction.notes || ''
      })
    } else {
      // Valeurs par défaut pour une nouvelle transaction
      const today = new Date().toISOString().split('T')[0]
      setFormData(prev => ({
        ...prev,
        date_de_transaction: today
      }))
    }
  }, [transaction])

  // Réinitialiser la catégorie quand le type change
  useEffect(() => {
    if (formData.type) {
      const availableCategories = getCategoriesByType(formData.type)
      if (!availableCategories.includes(formData.categorie)) {
        setFormData(prev => ({ ...prev, categorie: '' }))
      }
    }
  }, [formData.type])

  useEffect(() => {
    // Filtrer les immeubles selon la recherche
    if (buildingSearch) {
      const filtered = buildings.filter(building =>
        building.nom_immeuble.toLowerCase().includes(buildingSearch.toLowerCase()) ||
        building.adresse.toLowerCase().includes(buildingSearch.toLowerCase())
      )
      setFilteredBuildings(filtered)
    } else {
      setFilteredBuildings(buildings)
    }
  }, [buildingSearch, buildings])

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    
    // Effacer l'erreur pour ce champ
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }))
    }
  }

  const handleBuildingSearch = (value) => {
    setBuildingSearch(value)
    setShowBuildingDropdown(value.length > 0)
  }

  const handleBuildingSelect = (building) => {
    setFormData(prev => ({
      ...prev,
      id_immeuble: building.id_immeuble
    }))
    setBuildingSearch(`${building.nom_immeuble} - ${building.adresse}`)
    setShowBuildingDropdown(false)
  }

  const handlePdfUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Seuls les fichiers PDF sont acceptés')
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Utiliser fetch directement pour éviter les problèmes de Content-Type
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/upload?context=transaction`, {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        handleChange('pdf_transaction', result.filename)
        console.log('✅ PDF uploadé:', result.filename)
      } else {
        const errorData = await response.json()
        console.error('❌ Erreur upload PDF:', errorData)
        alert(`Erreur lors de l'upload: ${errorData.detail || 'Erreur inconnue'}`)
      }
    } catch (error) {
      console.error('❌ Erreur upload PDF:', error)
      alert('Erreur de connexion lors de l\'upload')
    }
  }

  const validateForm = () => {
    const newErrors = {}

    if (!formData.id_immeuble) {
      newErrors.id_immeuble = 'L\'immeuble est obligatoire'
    }

    if (!formData.type) {
      newErrors.type = 'Le type est obligatoire'
    }

    if (!formData.categorie) {
      newErrors.categorie = 'La catégorie est obligatoire'
    }

    if (!formData.montant || formData.montant === 0) {
      newErrors.montant = 'Le montant est obligatoire'
    } else if (formData.type === 'revenu' && formData.montant <= 0) {
      newErrors.montant = 'Le montant doit être positif pour un revenu'
    } else if (formData.type === 'depense' && formData.montant >= 0) {
      newErrors.montant = 'Le montant doit être négatif pour une dépense'
    }

    if (!formData.date_de_transaction) {
      newErrors.date_de_transaction = 'La date est obligatoire'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    // Vérifier si c'est une création et si la référence existe déjà
    if (!transaction && formData.reference) {
      try {
        const checkResponse = await api.get(`/api/transactions/check-reference/${encodeURIComponent(formData.reference)}`)
        if (checkResponse.data.exists) {
          const existingTransaction = checkResponse.data.transaction
          const confirmMessage = `Une transaction avec la référence "${formData.reference}" existe déjà.\n\n` +
            `Transaction existante:\n` +
            `- Date: ${existingTransaction.date_de_transaction}\n` +
            `- Montant: $${existingTransaction.montant}\n` +
            `- Type: ${existingTransaction.type}\n` +
            `- Catégorie: ${existingTransaction.categorie}\n\n` +
            `Voulez-vous vraiment créer cette nouvelle transaction ?`
          
          if (!window.confirm(confirmMessage)) {
            return
          }
        }
      } catch (error) {
        console.error('Erreur lors de la vérification de la référence:', error)
        // Continue même en cas d'erreur de vérification
      }
    }

    setLoading(true)
    try {
      // Utiliser le nouveau format français
      const transactionData = {
        id_immeuble: formData.id_immeuble,
        type: formData.type,
        categorie: formData.categorie,
        montant: parseFloat(formData.montant),
        date_de_transaction: formData.date_de_transaction,
        methode_de_paiement: formData.methode_de_paiement,
        reference: formData.reference,
        source: formData.source,
        pdf_transaction: formData.pdf_transaction,
        notes: formData.notes
      }

      let savedTransaction
      if (transaction) {
        // Mise à jour
        const response = await api.put(`/api/transactions/${transaction.id_transaction}`, transactionData)
        savedTransaction = response.data.data
      } else {
        // Création
        const response = await api.post('/api/transactions', transactionData)
        savedTransaction = response.data.data
      }

      onSave(savedTransaction)
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
      alert('Erreur lors de la sauvegarde de la transaction')
    } finally {
      setLoading(false)
    }
  }

  const getTypeLabel = (type) => {
    const typeLabels = {
      'revenu': 'Revenu',
      'depense': 'Dépense'
    }
    return typeLabels[type] || type
  }

  const getCategoryLabel = (category) => {
    const categoryLabels = {
      'taxes_scolaires': 'Taxes scolaires',
      'taxes_municipales': 'Taxes municipales',
      'electricite': 'Électricité',
      'gaz': 'Gaz',
      'eau': 'Eau',
      'entretien': 'Entretien',
      'reparation': 'Réparation',
      'assurance': 'Assurance',
      'loyer': 'Loyer',
      'autre': 'Autre'
    }
    return categoryLabels[category] || category
  }

  const getPaymentMethodLabel = (method) => {
    const methodLabels = {
      'virement': 'Virement',
      'cheque': 'Chèque',
      'especes': 'Espèces',
      'carte': 'Carte',
      'autre': 'Autre'
    }
    return methodLabels[method] || method
  }

  const getSelectedBuilding = () => {
    return buildings.find(b => b.id_immeuble === formData.id_immeuble)
  }

  const getBuildingDisplayName = (building) => {
    if (!building) return ''
    return `${building.nom_immeuble} - ${building.adresse}`
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {transaction ? 'Modifier la transaction' : 'Nouvelle transaction'}
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Immeuble avec recherche */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Building className="h-4 w-4 inline mr-1" />
              Immeuble *
            </label>
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                value={buildingSearch || getBuildingDisplayName(getSelectedBuilding())}
                onChange={(e) => handleBuildingSearch(e.target.value)}
                onFocus={() => setShowBuildingDropdown(true)}
                className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.id_immeuble ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Rechercher un immeuble..."
              />
              {showBuildingDropdown && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {filteredBuildings.map(building => (
                    <div
                      key={building.id_immeuble}
                      onClick={() => handleBuildingSelect(building)}
                      className="p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                    >
                      <div className="font-medium text-gray-900">{building.nom_immeuble}</div>
                      <div className="text-sm text-gray-500">{building.adresse}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {errors.id_immeuble && (
              <p className="text-red-500 text-sm mt-1">{errors.id_immeuble}</p>
            )}
          </div>

          {/* Type et Catégorie */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Tag className="h-4 w-4 inline mr-1" />
                Type *
              </label>
              <select
                value={formData.type}
                onChange={(e) => handleChange('type', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.type ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Sélectionner un type</option>
                {constants?.types?.map(type => (
                  <option key={type} value={type}>{getTypeLabel(type)}</option>
                ))}
              </select>
              {errors.type && (
                <p className="text-red-500 text-sm mt-1">{errors.type}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Tag className="h-4 w-4 inline mr-1" />
                Catégorie *
              </label>
              <select
                value={formData.categorie}
                onChange={(e) => handleChange('categorie', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.categorie ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={!formData.type}
              >
                <option value="">
                  {formData.type ? 'Sélectionner une catégorie' : 'Sélectionnez d\'abord un type'}
                </option>
                {getCategoriesByType(formData.type).map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
              {errors.categorie && (
                <p className="text-red-500 text-sm mt-1">{errors.categorie}</p>
              )}
            </div>
          </div>

          {/* Montant */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <DollarSign className="h-4 w-4 inline mr-1" />
              Montant *
              {formData.type === 'depense' && (
                <span className="text-red-600 text-xs ml-2">(sera automatiquement négatif)</span>
              )}
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={Math.abs(formData.montant) || ''}
              onChange={(e) => {
                const value = parseFloat(e.target.value) || 0
                const finalValue = formData.type === 'depense' ? -value : value
                handleChange('montant', finalValue)
              }}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.montant ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="0.00"
            />
            {formData.montant !== 0 && (
              <p className="text-sm text-gray-600 mt-1">
                Montant final: {formData.montant < 0 ? '-' : '+'}${Math.abs(formData.montant).toFixed(2)}
              </p>
            )}
            {errors.montant && (
              <p className="text-red-500 text-sm mt-1">{errors.montant}</p>
            )}
          </div>

          {/* Date et Méthode de paiement */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="h-4 w-4 inline mr-1" />
                Date de transaction *
              </label>
              <input
                type="date"
                value={formData.date_de_transaction}
                onChange={(e) => handleChange('date_de_transaction', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.date_de_transaction ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.date_de_transaction && (
                <p className="text-red-500 text-sm mt-1">{errors.date_de_transaction}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <CreditCard className="h-4 w-4 inline mr-1" />
                Méthode de paiement
              </label>
              <select
                value={formData.methode_de_paiement}
                onChange={(e) => handleChange('methode_de_paiement', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Sélectionner une méthode</option>
                {constants.payment_methods?.map(method => (
                  <option key={method} value={method}>{getPaymentMethodLabel(method)}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Référence et Source */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Référence
              </label>
              <input
                type="text"
                value={formData.reference}
                onChange={(e) => handleChange('reference', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Numéro de facture, référence..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Source
              </label>
              <input
                type="text"
                value={formData.source}
                onChange={(e) => handleChange('source', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Compagnie qui a émis la facture..."
              />
            </div>
          </div>

          {/* PDF Transaction */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <File className="h-4 w-4 inline mr-1" />
              Document PDF
            </label>
            <div className="flex items-center space-x-3">
              <input
                type="file"
                accept=".pdf"
                onChange={handlePdfUpload}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              {formData.pdf_transaction && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-green-600">✓ {formData.pdf_transaction}</span>
                  <button
                    type="button"
                    onClick={() => {
                      const pdfUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/${formData.pdf_transaction}`
                      window.open(pdfUrl, '_blank')
                    }}
                    className="text-blue-600 hover:text-blue-800 text-sm underline"
                  >
                    Ouvrir
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Notes supplémentaires..."
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <Save className="h-4 w-4" />
              <span>{loading ? 'Sauvegarde...' : 'Sauvegarder'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}