import React, { useState, useEffect } from 'react'
import { X, Save, Building, DollarSign, Calendar, FileText, Tag, Upload, User } from 'lucide-react'
import { invoicesSTService, projectsService, contractorsService } from '../services/api'

export default function InvoiceSTForm({ isOpen, onClose, invoice, onSuccess }) {
  const [formData, setFormData] = useState({
    id_projet: '',
    id_st: '',
    montant: '',
    section: '',
    notes: '',
    reference: '',
    date_de_paiement: '',
    pdf_facture: ''
  })
  const [projects, setProjects] = useState([])
  const [contractors, setContractors] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [uploadingPdf, setUploadingPdf] = useState(false)

  useEffect(() => {
    if (isOpen) {
      fetchProjects()
      fetchContractors()
      
      if (invoice) {
        setFormData({
          id_projet: invoice.id_projet || '',
          id_st: invoice.id_st || '',
          montant: invoice.montant || '',
          section: invoice.section || '',
          notes: invoice.notes || '',
          reference: invoice.reference || '',
          date_de_paiement: formatDateForInput(invoice.date_de_paiement),
          pdf_facture: invoice.pdf_facture || ''
        })
      } else {
        setFormData({
          id_projet: '',
          id_st: '',
          montant: '',
          section: '',
          notes: '',
          reference: '',
          date_de_paiement: '',
          pdf_facture: ''
        })
      }
    }
  }, [isOpen, invoice])

  const formatDateForInput = (dateString) => {
    if (!dateString) return ''
    let date = dateString
    if (dateString.includes('T')) {
      date = dateString.split('T')[0]
    } else if (dateString.includes(' ')) {
      date = dateString.split(' ')[0]
    }
    return date
  }

  const fetchProjects = async () => {
    try {
      const response = await projectsService.getProjects()
      setProjects(response.data || [])
    } catch (err) {
      console.error('Erreur lors du chargement des projets:', err)
    }
  }

  const fetchContractors = async () => {
    try {
      const response = await contractorsService.getContractors()
      setContractors(response.data || [])
    } catch (err) {
      console.error('Erreur lors du chargement des sous-traitants:', err)
    }
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handlePdfUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Seuls les fichiers PDF sont acceptés')
      return
    }

    setUploadingPdf(true)
    try {
      const formDataUpload = new FormData()
      formDataUpload.append('file', file)

      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/upload?context=facture`, {
        method: 'POST',
        body: formDataUpload
      })

      if (response.ok) {
        const result = await response.json()
        handleChange('pdf_facture', result.filename)
        console.log('✅ PDF uploadé:', result.filename)
      } else {
        const errorData = await response.json()
        console.error('❌ Erreur upload PDF:', errorData)
        alert(`Erreur lors de l'upload: ${errorData.detail || 'Erreur inconnue'}`)
      }
    } catch (error) {
      console.error('❌ Erreur upload PDF:', error)
      alert('Erreur de connexion lors de l\'upload')
    } finally {
      setUploadingPdf(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const submitData = {
        id_projet: parseInt(formData.id_projet),
        id_st: parseInt(formData.id_st),
        montant: parseFloat(formData.montant),
        section: formData.section || null,
        notes: formData.notes || null,
        reference: formData.reference || null,
        date_de_paiement: formData.date_de_paiement || null,
        pdf_facture: formData.pdf_facture || null
      }

      if (invoice) {
        await invoicesSTService.updateInvoice(invoice.id_facture, submitData)
        onSuccess()
      } else {
        await invoicesSTService.createInvoice(submitData)
        onSuccess()
      }
      onClose()
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
      setError(error.response?.data?.detail || 'Erreur lors de la sauvegarde')
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
          <h2 className="text-2xl font-bold text-gray-900">
            {invoice ? 'Modifier la facture' : 'Nouvelle facture'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Formulaire */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Projet et Sous-traitant */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Building className="h-4 w-4 inline mr-1" />
                Projet *
              </label>
              <select
                value={formData.id_projet}
                onChange={(e) => handleChange('id_projet', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">Sélectionner un projet</option>
                {projects.map((project) => (
                  <option key={project.id_projet} value={project.id_projet}>
                    {project.nom}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <User className="h-4 w-4 inline mr-1" />
                Sous-traitant *
              </label>
              <select
                value={formData.id_st}
                onChange={(e) => handleChange('id_st', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">Sélectionner un sous-traitant</option>
                {contractors.map((contractor) => (
                  <option key={contractor.id_st} value={contractor.id_st}>
                    {contractor.nom}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Montant et Référence */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <DollarSign className="h-4 w-4 inline mr-1" />
                Montant ($) *
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.montant}
                onChange={(e) => handleChange('montant', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Tag className="h-4 w-4 inline mr-1" />
                Référence
              </label>
              <input
                type="text"
                value={formData.reference}
                onChange={(e) => handleChange('reference', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Section et Date de paiement */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Section
              </label>
              <input
                type="text"
                value={formData.section}
                onChange={(e) => handleChange('section', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Calendar className="h-4 w-4 inline mr-1" />
                Date de paiement
              </label>
              <input
                type="date"
                value={formData.date_de_paiement}
                onChange={(e) => handleChange('date_de_paiement', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <FileText className="h-4 w-4 inline mr-1" />
              Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Notes sur la facture..."
            />
          </div>

          {/* PDF Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <FileText className="h-4 w-4 inline mr-1" />
              Document PDF
            </label>
            <div className="flex items-center space-x-4">
              <label className="flex-1 cursor-pointer">
                <div className="flex items-center justify-center px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition-colors">
                  {uploadingPdf ? (
                    <div className="flex items-center text-gray-600">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                      Upload en cours...
                    </div>
                  ) : (
                    <div className="flex items-center text-gray-600">
                      <Upload className="h-4 w-4 mr-2" />
                      <span>{formData.pdf_facture || 'Choisir un fichier PDF'}</span>
                    </div>
                  )}
                </div>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handlePdfUpload}
                  className="hidden"
                  disabled={uploadingPdf}
                />
              </label>
              {formData.pdf_facture && (
                <div className="flex items-center text-sm text-green-600">
                  <FileText className="h-4 w-4 mr-1" />
                  PDF sélectionné
                </div>
              )}
            </div>
          </div>

          {/* Erreur */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Boutons */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Sauvegarde...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {invoice ? 'Mettre à jour' : 'Créer la facture'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

