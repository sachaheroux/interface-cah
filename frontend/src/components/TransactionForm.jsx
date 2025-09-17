import React, { useState, useEffect } from 'react'
import { X, Save, Building, DollarSign, Calendar, FileText, CreditCard, Tag, File } from 'lucide-react'
import api from '../services/api'

export default function TransactionForm({ transaction, buildings, constants, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    id_immeuble: '',
    type_transaction: '',
    montant: '',
    description: '',
    date_transaction: '',
    methode_paiement: '',
    statut: 'en_attente',
    reference: '',
    pdf_document: '',
    notes: ''
  })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (transaction) {
      setFormData({
        id_immeuble: transaction.id_immeuble || '',
        type_transaction: transaction.type_transaction || '',
        montant: transaction.montant || '',
        description: transaction.description || '',
        date_transaction: transaction.date_transaction || '',
        methode_paiement: transaction.methode_paiement || '',
        statut: transaction.statut || 'en_attente',
        reference: transaction.reference || '',
        pdf_document: transaction.pdf_document || '',
        notes: transaction.notes || ''
      })
    } else {
      // Valeurs par défaut pour une nouvelle transaction
      const today = new Date().toISOString().split('T')[0]
      setFormData(prev => ({
        ...prev,
        date_transaction: today
      }))
    }
  }, [transaction])

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

  const validateForm = () => {
    const newErrors = {}

    if (!formData.id_immeuble) {
      newErrors.id_immeuble = 'L\'immeuble est obligatoire'
    }

    if (!formData.type_transaction) {
      newErrors.type_transaction = 'Le type de transaction est obligatoire'
    }

    if (!formData.montant || formData.montant <= 0) {
      newErrors.montant = 'Le montant doit être supérieur à 0'
    }

    if (!formData.date_transaction) {
      newErrors.date_transaction = 'La date est obligatoire'
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
      const transactionData = {
        ...formData,
        montant: parseFloat(formData.montant)
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
      'loyer': 'Loyer',
      'facture': 'Facture',
      'maintenance': 'Maintenance',
      'revenus': 'Revenus',
      'depenses': 'Dépenses',
      'investissement': 'Investissement',
      'frais': 'Frais',
      'autre': 'Autre'
    }
    return typeLabels[type] || type
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

  const getStatusLabel = (status) => {
    const statusLabels = {
      'en_attente': 'En attente',
      'paye': 'Payé',
      'annule': 'Annulé'
    }
    return statusLabels[status] || status
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
          {/* Immeuble */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Building className="h-4 w-4 inline mr-1" />
              Immeuble *
            </label>
            <select
              value={formData.id_immeuble}
              onChange={(e) => handleChange('id_immeuble', parseInt(e.target.value))}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.id_immeuble ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Sélectionner un immeuble</option>
              {buildings.map(building => (
                <option key={building.id_immeuble} value={building.id_immeuble}>
                  {building.nom_immeuble} - {building.adresse}
                </option>
              ))}
            </select>
            {errors.id_immeuble && (
              <p className="text-red-500 text-sm mt-1">{errors.id_immeuble}</p>
            )}
          </div>

          {/* Type de transaction et Montant */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Tag className="h-4 w-4 inline mr-1" />
                Type de transaction *
              </label>
              <select
                value={formData.type_transaction}
                onChange={(e) => handleChange('type_transaction', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.type_transaction ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Sélectionner un type</option>
                {constants.types?.map(type => (
                  <option key={type} value={type}>{getTypeLabel(type)}</option>
                ))}
              </select>
              {errors.type_transaction && (
                <p className="text-red-500 text-sm mt-1">{errors.type_transaction}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <DollarSign className="h-4 w-4 inline mr-1" />
                Montant *
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.montant}
                onChange={(e) => handleChange('montant', parseFloat(e.target.value) || 0)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.montant ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="0.00"
              />
              {errors.montant && (
                <p className="text-red-500 text-sm mt-1">{errors.montant}</p>
              )}
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <FileText className="h-4 w-4 inline mr-1" />
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Description de la transaction..."
            />
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
                value={formData.date_transaction}
                onChange={(e) => handleChange('date_transaction', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.date_transaction ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.date_transaction && (
                <p className="text-red-500 text-sm mt-1">{errors.date_transaction}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <CreditCard className="h-4 w-4 inline mr-1" />
                Méthode de paiement
              </label>
              <select
                value={formData.methode_paiement}
                onChange={(e) => handleChange('methode_paiement', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Sélectionner une méthode</option>
                {constants.payment_methods?.map(method => (
                  <option key={method} value={method}>{getPaymentMethodLabel(method)}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Statut et Référence */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Statut
              </label>
              <select
                value={formData.statut}
                onChange={(e) => handleChange('statut', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {constants.statuses?.map(status => (
                  <option key={status} value={status}>{getStatusLabel(status)}</option>
                ))}
              </select>
            </div>

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
          </div>

          {/* PDF Document */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <File className="h-4 w-4 inline mr-1" />
              Document PDF
            </label>
            <input
              type="text"
              value={formData.pdf_document}
              onChange={(e) => handleChange('pdf_document', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Nom du fichier PDF..."
            />
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
