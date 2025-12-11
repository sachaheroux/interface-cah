import React, { useState, useEffect } from 'react'
import { X, User, Mail, Phone, Home, Save, AlertCircle, Plus } from 'lucide-react'
import { TenantStatus } from '../types/tenant'

export default function TenantForm({ tenant, isOpen, onClose, onSave }) {
  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    statut: TenantStatus.ACTIVE,
    id_unite: '',
    unitInfo: null,
    notes: ''
  })

  const [loading, setLoading] = useState(false)
  const [availableUnits, setAvailableUnits] = useState([])
  const [loadingUnits, setLoadingUnits] = useState(false)
  const [unitSearchTerm, setUnitSearchTerm] = useState('')
  const [filteredUnits, setFilteredUnits] = useState([])

  // Charger les unités disponibles
  useEffect(() => {
    if (isOpen) {
      loadUnits()
    }
  }, [isOpen])

  // Filtrer les unités selon le terme de recherche
  useEffect(() => {
    if (unitSearchTerm.trim() === '') {
      setFilteredUnits(availableUnits)
    } else {
      const filtered = availableUnits.filter(unit =>
        unit.adresse_unite.toLowerCase().includes(unitSearchTerm.toLowerCase()) ||
        unit.immeuble?.nom_immeuble?.toLowerCase().includes(unitSearchTerm.toLowerCase())
      )
      setFilteredUnits(filtered)
    }
  }, [unitSearchTerm, availableUnits])

  // Charger les unités
  const loadUnits = async () => {
    setLoadingUnits(true)
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/units`)
      if (response.ok) {
        const data = await response.json()
        setAvailableUnits(data.data || [])
        setFilteredUnits(data.data || [])
      }
    } catch (error) {
      console.error('Erreur lors du chargement des unités:', error)
    } finally {
      setLoadingUnits(false)
    }
  }

  // Initialiser le formulaire
  useEffect(() => {
    if (tenant) {
      setFormData({
        nom: tenant.nom || '',
        prenom: tenant.prenom || '',
        email: tenant.email || '',
        telephone: tenant.telephone || '',
        statut: tenant.statut || TenantStatus.ACTIVE,
        id_unite: tenant.id_unite || '',
        unitInfo: tenant.unitInfo || null,
        notes: tenant.notes || ''
      })
    } else {
      setFormData({
        nom: '',
        prenom: '',
        email: '',
        telephone: '',
        statut: TenantStatus.ACTIVE,
        id_unite: '',
        unitInfo: null,
        notes: ''
      })
    }
  }, [tenant, isOpen])

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleUnitSelect = (unit) => {
    setFormData(prev => ({
      ...prev,
      id_unite: unit.id_unite,
      unitInfo: unit
    }))
  }

  const handleUnitDeselect = () => {
    setFormData(prev => ({
      ...prev,
      id_unite: '',
      unitInfo: null
    }))
  }

  const validateForm = () => {
    const errors = {}
    
    if (!formData.nom.trim()) errors.nom = 'Le nom est obligatoire'
    if (!formData.prenom.trim()) errors.prenom = 'Le prénom est obligatoire'
    // Email et téléphone ne sont plus obligatoires
    // L'unité n'est plus obligatoire (peut être désélectionnée)
    
    return errors
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const errors = validateForm()
    if (Object.keys(errors).length > 0) {
      console.error('Erreurs de validation:', errors)
      return
    }

    setLoading(true)
    
    try {
      const tenantData = {
        nom: formData.nom.trim(),
        prenom: formData.prenom.trim(),
        email: formData.email.trim(),
        telephone: formData.telephone.trim(),
        statut: formData.statut,
        id_unite: formData.id_unite ? parseInt(formData.id_unite) : null,
        notes: formData.notes.trim()
      }

      console.log('💾 Données à sauvegarder:', tenantData)

      if (tenant?.id_locataire) {
        // MISE À JOUR du locataire existant
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/tenants/${tenant.id_locataire}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(tenantData)
        })
        
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Erreur mise à jour: ${response.status} - ${errorText}`)
        }
        
        const result = await response.json()
        console.log('✅ Locataire mis à jour:', result)
        
      } else {
        // CRÉATION d'un nouveau locataire
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/tenants`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(tenantData)
        })
        
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Erreur création: ${response.status} - ${errorText}`)
        }
        
        const result = await response.json()
        console.log('✅ Locataire créé:', result)
      }
      
      onSave()
      onClose()
      
    } catch (error) {
      console.error('❌ Erreur lors de la sauvegarde:', error)
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
            <User className="h-6 w-6 text-primary-600" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {tenant ? 'Modifier le locataire' : 'Nouveau locataire'}
              </h2>
              <p className="text-sm text-gray-600">
                {tenant ? 'Modifiez les informations du locataire' : 'Ajoutez un nouveau locataire'}
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
          {/* Informations personnelles */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Informations personnelles
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom *
                </label>
                <input
                  type="text"
                  value={formData.nom}
                  onChange={(e) => handleChange('nom', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Nom de famille"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prénom *
                </label>
                <input
                  type="text"
                  value={formData.prenom}
                  onChange={(e) => handleChange('prenom', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Prénom"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Mail className="h-4 w-4 inline mr-2" />
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="email@exemple.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Phone className="h-4 w-4 inline mr-2" />
                  Téléphone
                </label>
                <input
                  type="tel"
                  value={formData.telephone}
                  onChange={(e) => handleChange('telephone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="514-555-1234"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Statut
              </label>
              <select
                value={formData.statut}
                onChange={(e) => handleChange('statut', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value={TenantStatus.ACTIVE}>Actif</option>
                <option value={TenantStatus.PENDING}>En attente</option>
                <option value={TenantStatus.INACTIVE}>Inactif</option>
                <option value={TenantStatus.FORMER}>Ancien</option>
              </select>
            </div>
          </div>

          {/* Sélection d'unité */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Home className="h-5 w-5 mr-2" />
                Unité assignée
              </h3>
              {formData.id_unite && (
                <button
                  type="button"
                  onClick={handleUnitDeselect}
                  className="text-sm text-red-600 hover:text-red-700 font-medium"
                >
                  Retirer l'unité
                </button>
              )}
            </div>
            
            {formData.id_unite ? (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{formData.unitInfo?.adresse_unite || 'Unité sélectionnée'}</p>
                    <p className="text-sm text-gray-600">{formData.unitInfo?.immeuble?.nom_immeuble}</p>
                  </div>
                  <button
                    type="button"
                    onClick={handleUnitDeselect}
                    className="text-red-600 hover:text-red-700"
                    title="Retirer l'unité"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Rechercher une unité
                  </label>
                  <input
                    type="text"
                    value={unitSearchTerm}
                    onChange={(e) => setUnitSearchTerm(e.target.value)}
                    placeholder="Tapez pour rechercher une unité..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                {loadingUnits ? (
                  <div className="text-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
                    <p className="text-sm text-gray-600 mt-2">Chargement des unités...</p>
                  </div>
                ) : (
                  <div className="max-h-48 overflow-y-auto border border-gray-200 rounded-lg">
                    {filteredUnits.length === 0 ? (
                      <div className="text-center py-4 text-gray-500">
                        Aucune unité trouvée
                      </div>
                    ) : (
                      filteredUnits.map((unit) => (
                        <div
                          key={unit.id_unite}
                          onClick={() => handleUnitSelect(unit)}
                          className="p-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50"
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium text-gray-900">{unit.adresse_unite}</p>
                              <p className="text-sm text-gray-600">{unit.immeuble?.nom_immeuble}</p>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </>
            )}
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Notes additionnelles..."
            />
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
                  {tenant ? 'Mettre à jour' : 'Créer le locataire'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
