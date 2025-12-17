import React, { useState, useEffect } from 'react'
import { X, Save, FileText, Calendar, DollarSign, User, Home } from 'lucide-react'

export default function LeaseForm({ lease, isOpen, onClose, onSave }) {
  const [formData, setFormData] = useState({
    id_locataire: '',
    id_unite: '',
    date_debut: '',
    date_fin: '',
    prix_loyer: 0,
    methode_paiement: 'Virement bancaire',
    pdf_bail: ''
  })

  const [loading, setLoading] = useState(false)
  const [availableTenants, setAvailableTenants] = useState([])
  const [availableUnits, setAvailableUnits] = useState([])
  const [tenantSearchTerm, setTenantSearchTerm] = useState('')
  const [filteredTenants, setFilteredTenants] = useState([])
  const [showTenantDropdown, setShowTenantDropdown] = useState(false)
  const [selectedTenant, setSelectedTenant] = useState(null)
  const [unitSearchTerm, setUnitSearchTerm] = useState('')
  const [filteredUnits, setFilteredUnits] = useState([])
  const [showUnitDropdown, setShowUnitDropdown] = useState(false)
  const [selectedUnit, setSelectedUnit] = useState(null)

  // Charger les données
  useEffect(() => {
    if (isOpen) {
      loadTenants()
      loadUnits()
    }
  }, [isOpen])

  // Filtrer les locataires selon le terme de recherche
  useEffect(() => {
    if (tenantSearchTerm.trim() === '') {
      setFilteredTenants([])
    } else {
      const filtered = availableTenants.filter(tenant =>
        `${tenant.nom} ${tenant.prenom}`.toLowerCase().includes(tenantSearchTerm.toLowerCase()) ||
        tenant.email?.toLowerCase().includes(tenantSearchTerm.toLowerCase()) ||
        tenant.telephone?.includes(tenantSearchTerm)
      )
      setFilteredTenants(filtered)
    }
  }, [tenantSearchTerm, availableTenants])

  // Filtrer les unités selon le terme de recherche
  useEffect(() => {
    if (unitSearchTerm.trim() === '') {
      setFilteredUnits([])
    } else {
      const filtered = availableUnits.filter(unit =>
        unit.adresse_unite?.toLowerCase().includes(unitSearchTerm.toLowerCase()) ||
        unit.type?.toLowerCase().includes(unitSearchTerm.toLowerCase())
      )
      setFilteredUnits(filtered)
    }
  }, [unitSearchTerm, availableUnits])

  // Fermer le dropdown quand on clique ailleurs
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showTenantDropdown && !event.target.closest('.tenant-search-container')) {
        setShowTenantDropdown(false)
      }
      if (showUnitDropdown && !event.target.closest('.unit-search-container')) {
        setShowUnitDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showTenantDropdown, showUnitDropdown])

  // Initialiser le formulaire
  useEffect(() => {
    if (lease) {
      setFormData({
        id_locataire: lease.id_locataire || '',
        id_unite: lease.id_unite || (lease.locataire?.unite?.id_unite || ''),
        date_debut: lease.date_debut || '',
        date_fin: lease.date_fin || '',
        prix_loyer: lease.prix_loyer || 0,
        methode_paiement: lease.methode_paiement || 'Virement bancaire',
        pdf_bail: lease.pdf_bail || ''
      })
      
      // Trouver le locataire correspondant pour l'affichage
      if (lease.id_locataire && availableTenants.length > 0) {
        const tenant = availableTenants.find(t => t.id_locataire === lease.id_locataire)
        if (tenant) {
          setSelectedTenant(tenant)
          setTenantSearchTerm(`${tenant.nom} ${tenant.prenom}`)
        }
      }
      
      // Trouver l'unité correspondante pour l'affichage
      if (lease.id_unite && availableUnits.length > 0) {
        const unit = availableUnits.find(u => u.id_unite === lease.id_unite)
        if (unit) {
          setSelectedUnit(unit)
          setUnitSearchTerm(unit.adresse_unite)
        }
      }
    } else {
      setFormData({
        id_locataire: '',
        id_unite: '',
        date_debut: '',
        date_fin: '',
        prix_loyer: 0,
        methode_paiement: 'Virement bancaire',
        pdf_bail: ''
      })
      setSelectedTenant(null)
      setTenantSearchTerm('')
      setSelectedUnit(null)
      setUnitSearchTerm('')
    }
  }, [lease, isOpen, availableTenants, availableUnits])

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

  const handlePdfUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    console.log('📤 Tentative d\'upload PDF:', file.name, file.size, 'bytes')

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Seuls les fichiers PDF sont acceptés')
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)

      const apiUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/upload`
      console.log('🌐 URL d\'upload:', apiUrl)

      const response = await fetch(`${apiUrl}?context=bail`, {
        method: 'POST',
        body: formData
      })

      console.log('📊 Réponse reçue:', response.status, response.statusText)

      if (response.ok) {
        const result = await response.json()
        console.log('✅ Résultat upload:', result)
        handleChange('pdf_bail', result.filename)
        console.log('✅ PDF uploadé:', result.filename)
        
        // Si on est en mode édition, mettre à jour le bail immédiatement
        if (lease?.id_bail) {
          await updateLeasePdf(lease.id_bail, result.filename)
        }
      } else {
        const errorText = await response.text()
        console.error('❌ Erreur upload PDF - Status:', response.status)
        console.error('❌ Erreur upload PDF - Response:', errorText)
        
        try {
          const error = JSON.parse(errorText)
          alert(`Erreur lors de l'upload: ${error.detail || 'Erreur inconnue'}`)
        } catch {
          alert(`Erreur lors de l'upload: ${response.status} - ${errorText}`)
        }
      }
    } catch (error) {
      console.error('❌ Erreur upload PDF:', error)
      alert(`Erreur de connexion lors de l'upload: ${error.message}`)
    }
  }

  const updateLeasePdf = async (leaseId, pdfFilename) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/leases/${leaseId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          pdf_bail: pdfFilename
        })
      })

      if (response.ok) {
        console.log('✅ PDF du bail mis à jour')
      } else {
        console.error('❌ Erreur lors de la mise à jour du PDF')
      }
    } catch (error) {
      console.error('❌ Erreur lors de la mise à jour du PDF:', error)
    }
  }

  const handleTenantSearch = (value) => {
    setTenantSearchTerm(value)
    setShowTenantDropdown(value.length > 0)
  }

  const handleTenantSelect = (tenant) => {
    setSelectedTenant(tenant)
    setTenantSearchTerm(`${tenant.nom} ${tenant.prenom}`)
    setFormData(prev => ({
      ...prev,
      id_locataire: tenant.id_locataire
    }))
    setShowTenantDropdown(false)
  }

  const handleTenantClear = () => {
    setSelectedTenant(null)
    setTenantSearchTerm('')
    setFormData(prev => ({
      ...prev,
      id_locataire: ''
    }))
  }

  const handleUnitSearch = (value) => {
    setUnitSearchTerm(value)
    setShowUnitDropdown(value.length > 0)
  }

  const handleUnitSelect = (unit) => {
    setSelectedUnit(unit)
    setUnitSearchTerm(unit.adresse_unite)
    setFormData(prev => ({
      ...prev,
      id_unite: unit.id_unite
    }))
    setShowUnitDropdown(false)
  }

  const handleUnitClear = () => {
    setSelectedUnit(null)
    setUnitSearchTerm('')
    setFormData(prev => ({
      ...prev,
      id_unite: ''
    }))
  }

  const validateForm = () => {
    const errors = {}
    
    if (!formData.id_locataire) errors.id_locataire = 'Le locataire est obligatoire'
    if (!formData.id_unite) errors.id_unite = 'L\'unité est obligatoire'
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
        id_unite: parseInt(formData.id_unite),
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
          {/* Sélection de l'unité */}
          <div className="relative unit-search-container">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Home className="h-4 w-4 inline mr-2" />
              Unité *
            </label>
            <div className="relative">
              <input
                type="text"
                value={unitSearchTerm}
                onChange={(e) => handleUnitSearch(e.target.value)}
                onFocus={() => setShowUnitDropdown(unitSearchTerm.length > 0)}
                placeholder="Rechercher une unité par adresse..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
              />
              {selectedUnit && (
                <button
                  type="button"
                  onClick={handleUnitClear}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
            
            {/* Dropdown des résultats */}
            {showUnitDropdown && filteredUnits.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                {filteredUnits.slice(0, 10).map((unit) => (
                  <div
                    key={unit.id_unite}
                    onClick={() => handleUnitSelect(unit)}
                    className="p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">
                          {unit.adresse_unite}
                        </p>
                        {unit.type && (
                          <p className="text-sm text-gray-600">
                            {unit.type}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {filteredUnits.length > 10 && (
                  <div className="p-2 text-xs text-gray-500 text-center">
                    ... et {filteredUnits.length - 10} autres résultats
                  </div>
                )}
              </div>
            )}
            
            {showUnitDropdown && filteredUnits.length === 0 && unitSearchTerm.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg p-3">
                <p className="text-sm text-gray-500 text-center">
                  Aucune unité trouvée pour "{unitSearchTerm}"
                </p>
              </div>
            )}
          </div>

          {/* Sélection du locataire */}
          <div className="relative tenant-search-container">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <User className="h-4 w-4 inline mr-2" />
              Locataire *
            </label>
            <div className="relative">
              <input
                type="text"
                value={tenantSearchTerm}
                onChange={(e) => handleTenantSearch(e.target.value)}
                onFocus={() => setShowTenantDropdown(tenantSearchTerm.length > 0)}
                placeholder="Rechercher un locataire par nom, email ou téléphone..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
              />
              {selectedTenant && (
                <button
                  type="button"
                  onClick={handleTenantClear}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
            
            {/* Dropdown des résultats */}
            {showTenantDropdown && filteredTenants.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                {filteredTenants.slice(0, 10).map((tenant) => (
                  <div
                    key={tenant.id_locataire}
                    onClick={() => handleTenantSelect(tenant)}
                    className="p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">
                          {tenant.nom} {tenant.prenom}
                        </p>
                        <p className="text-sm text-gray-600">
                          {tenant.email} • {tenant.telephone}
                        </p>
                      </div>
                      <div className="text-xs text-gray-500">
                        {tenant.statut}
                      </div>
                    </div>
                  </div>
                ))}
                {filteredTenants.length > 10 && (
                  <div className="p-2 text-xs text-gray-500 text-center">
                    ... et {filteredTenants.length - 10} autres résultats
                  </div>
                )}
              </div>
            )}
            
            {showTenantDropdown && filteredTenants.length === 0 && tenantSearchTerm.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg p-3">
                <p className="text-sm text-gray-500 text-center">
                  Aucun locataire trouvé pour "{tenantSearchTerm}"
                </p>
              </div>
            )}
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
              onChange={handlePdfUpload}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            {formData.pdf_bail && (
              <div className="mt-2 flex items-center space-x-2">
                <span className="text-sm text-green-600">✓ {formData.pdf_bail}</span>
                <button
                  type="button"
                  onClick={() => {
                    const pdfUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/${formData.pdf_bail}`
                    window.open(pdfUrl, '_blank')
                  }}
                  className="text-blue-600 hover:text-blue-800 text-sm underline"
                >
                  Ouvrir le PDF
                </button>
              </div>
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