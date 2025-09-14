import React, { useState, useEffect } from 'react'
import { X, Save, User, Mail, Phone, MapPin, DollarSign, FileText, Home, Search, AlertTriangle } from 'lucide-react'
import { TenantStatus, getTenantStatusLabel } from '../types/tenant'
import { unitsService, assignmentsService } from '../services/api'

export default function TenantForm({ tenant, isOpen, onClose, onSave }) {
  // État pour éviter le rechargement automatique des données de bail
  const [isLeaseDataManuallySet, setIsLeaseDataManuallySet] = useState(false)
  const [hasLeaseDataBeenModified, setHasLeaseDataBeenModified] = useState(false)
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    status: TenantStatus.ACTIVE,
    
    unitId: '',
    unitInfo: null,
    
    // Premier bail (cellules de base)
    lease: {
      startDate: '',
      endDate: '',
      monthlyRent: 0,
      paymentMethod: 'Virement bancaire'
    },
    
    // Renouvellements (baux supplémentaires)
    leaseRenewals: [],
    
    notes: ''
  })

  const [loading, setLoading] = useState(false)
  const [availableUnits, setAvailableUnits] = useState([])
  const [loadingUnits, setLoadingUnits] = useState(false)
  const [unitSearchTerm, setUnitSearchTerm] = useState('')
  const [leaseHistory, setLeaseHistory] = useState([]) // Historique des baux depuis assignments
  const [filteredUnits, setFilteredUnits] = useState([])

  // Charger l'unité assignée et les données de bail depuis les assignations
  const loadTenantAssignmentAndLeaseData = async (tenantId) => {
    try {
      console.log('🔍 DEBUG - Chargement des données pour le locataire ID:', tenantId, 'Type:', typeof tenantId)
      
      const assignmentsResponse = await assignmentsService.getAssignments()
      const allAssignments = assignmentsResponse.data || []
      
      console.log('📋 Toutes les assignations disponibles:', allAssignments)
      console.log('🔍 Recherche d\'assignations pour le locataire:', tenantId)
      
      // Trouver TOUTES les assignations pour ce locataire (historique complet)
      const tenantAssignments = allAssignments.filter(a => {
        const tenantIdMatch = parseInt(a.tenantId) === parseInt(tenantId)
        console.log(`🔍 Comparaison: ${a.tenantId} (${typeof a.tenantId}) === ${tenantId} (${typeof tenantId}) = ${tenantIdMatch}`)
        return tenantIdMatch
      }).sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)) // Plus récent en premier
      
      console.log('📚 Historique des baux trouvé:', tenantAssignments)
      setLeaseHistory(tenantAssignments)
      
      // Le bail de base est toujours la première assignation (la plus ancienne)
      const baseAssignment = tenantAssignments[0] // Première assignation = bail de base
      
      console.log('🏠 Bail de base (première assignation):', baseAssignment)
      
      // Préparer les renouvellements (toutes les assignations SAUF la première)
      // La première = bail de base, les suivantes = renouvellements
      const renewalsData = tenantAssignments
        .slice(1) // Prendre toutes les assignations sauf la première
        .map((assignment, index) => ({
          id: `renewal_${assignment.id}`,
          startDate: assignment.leaseStartDate || assignment.startDate || '',
          endDate: assignment.leaseEndDate || assignment.endDate || '',
          monthlyRent: assignment.rentAmount || 0,
          paymentMethod: 'Virement bancaire', // Valeur par défaut
          renewalPdf: ''
        }))
      
      console.log('🔄 Renouvellements préparés:', renewalsData)
      console.log('🔍 DEBUG - Bail de base ID:', baseAssignment?.id)
      console.log('🔍 DEBUG - Toutes les assignations:', tenantAssignments.map(a => ({ id: a.id, startDate: a.leaseStartDate, rentAmount: a.rentAmount })))
      
      if (baseAssignment) {
        console.log('✅ Bail de base trouvé:', baseAssignment)
        
        // Récupérer les détails de l'unité
        const unitsResponse = await unitsService.getUnits()
        const allUnits = unitsResponse.data || []
        const unit = allUnits.find(u => parseInt(u.id) === parseInt(baseAssignment.unitId))
        
        if (unit) {
          console.log('✅ Unité trouvée:', unit)
          
          const leaseData = {
            startDate: baseAssignment.leaseStartDate || baseAssignment.startDate || '',
            endDate: baseAssignment.leaseEndDate || baseAssignment.endDate || '',
            monthlyRent: baseAssignment.rentAmount || 0,
            paymentMethod: 'Virement bancaire', // Valeur par défaut
            leasePdf: ''
          }
          
          console.log('📋 Données de bail de base extraites:', leaseData)
          
          return {
            unitData: unit,
            leaseData: leaseData,
            renewalsData: renewalsData
          }
        } else {
          console.log('❌ Unité non trouvée pour l\'assignation:', baseAssignment.unitId)
        }
      } else {
        console.log('❌ Aucune assignation trouvée pour le locataire:', tenantId)
      }
    } catch (error) {
      console.error('❌ Erreur lors du chargement des données d\'assignation:', error)
    }
    
    return { unitData: null, leaseData: null, renewalsData: [] }
  }

  // Charger les données de bail depuis les assignations
  const loadLeaseDataFromAssignments = async (tenantId) => {
    try {
      const assignmentsResponse = await assignmentsService.getAssignments()
      const allAssignments = assignmentsResponse.data || []
      
      console.log('🔍 Recherche d\'assignations pour le locataire:', tenantId)
      console.log('📋 Toutes les assignations:', allAssignments)
      
      // Trouver l'assignation active pour ce locataire
      const activeAssignment = allAssignments.find(a => 
        parseInt(a.tenantId) === parseInt(tenantId) && 
        (!a.moveOutDate || a.moveOutDate === null || a.moveOutDate === '')
      )
      
      if (activeAssignment) {
        console.log('✅ Assignation active trouvée:', activeAssignment)
        return {
          startDate: activeAssignment.leaseStartDate || '',
          endDate: activeAssignment.leaseEndDate || '',
          monthlyRent: activeAssignment.rentAmount || 0,
          paymentMethod: 'Virement bancaire', // Valeur par défaut
          leasePdf: '',
        }
      } else {
        console.log('❌ Aucune assignation active trouvée pour le locataire:', tenantId)
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données de bail:', error)
    }
    return null
  }

  useEffect(() => {
    if (tenant) {
      console.log('📋 Chargement des données locataire existant:', {
        id: tenant.id,
        name: tenant.name,
        lease: tenant.lease,
        leaseRenewal: tenant.leaseRenewal,
        isLeaseDataManuallySet: isLeaseDataManuallySet
      })
      
      // Charger l'unité assignée et les données de bail depuis les assignations
      loadTenantAssignmentAndLeaseData(tenant.id).then(({ unitData, leaseData, renewalsData }) => {
        console.log('📋 Résultat du chargement:', { unitData, leaseData, renewalsData })
        
        // Si pas de données d'assignation ET pas de données de bail dans le tenant, utiliser des valeurs vides
        const finalLeaseData = leaseData || (tenant.lease && tenant.lease !== null ? tenant.lease : {
          startDate: '',
          endDate: '',
          monthlyRent: 0,
          paymentMethod: 'Virement bancaire',
          leasePdf: '',
        })
        
        console.log('📋 Données finales chargées:', { 
          unitData, 
          leaseData: finalLeaseData,
          renewalsData: renewalsData,
          unitId: unitData?.id || tenant.unitId || '',
          unitInfo: unitData || tenant.unitInfo || null
        })
        
        setFormData({
          name: tenant.name || '',
          email: tenant.email || '',
          phone: tenant.phone || '',
          status: tenant.status || TenantStatus.ACTIVE,
          
          unitId: unitData?.id || tenant.unitId || '',
          unitInfo: unitData || tenant.unitInfo || null,
          
          lease: finalLeaseData,
          
          leaseRenewals: renewalsData || [],
          
          notes: tenant.notes || ''
        })
        
        console.log('✅ FormData mis à jour avec:', {
          name: tenant.name || '',
          unitId: unitData?.id || tenant.unitId || '',
          lease: finalLeaseData,
          renewals: renewalsData
        })
      }).catch(error => {
        console.error('❌ Erreur lors du chargement des données:', error)
      })
    } else {
      // Réinitialiser les flags pour un nouveau locataire
      setIsLeaseDataManuallySet(false)
      setHasLeaseDataBeenModified(false)
      setFormData({
        name: '',
        email: '',
        phone: '',
        status: TenantStatus.ACTIVE,
        unitId: '',
        unitInfo: null,
        lease: {
          startDate: '',
          endDate: '',
          monthlyRent: 0,
          paymentMethod: 'Virement bancaire',
          leasePdf: '', // URL ou nom du fichier PDF
        },
        leaseRenewals: [],
        notes: ''
      })
    }
  }, [tenant, isOpen])

  useEffect(() => {
    if (isOpen) {
      loadAvailableUnits()
      
      // Écouter l'événement de suppression de locataire
      const handleTenantDeleted = (event) => {
        console.log(`📢 TenantForm: Événement tenantDeleted reçu:`, event.detail)
        console.log(`🔄 TenantForm: Rechargement des unités disponibles...`)
        loadAvailableUnits()
      }
      
      // Écouter l'événement de suppression d'assignation spécifique
      const handleAssignmentRemoved = (event) => {
        console.log(`📢 TenantForm: Événement assignmentRemoved reçu:`, event.detail)
        console.log(`🔄 TenantForm: Rechargement des unités disponibles suite à la suppression d'assignation...`)
        loadAvailableUnits()
      }
      
      window.addEventListener('tenantDeleted', handleTenantDeleted)
      window.addEventListener('assignmentRemoved', handleAssignmentRemoved)
      
      return () => {
        window.removeEventListener('tenantDeleted', handleTenantDeleted)
        window.removeEventListener('assignmentRemoved', handleAssignmentRemoved)
      }
    }
  }, [isOpen])

  const loadAvailableUnits = async () => {
    try {
      setLoadingUnits(true)
      const response = await unitsService.getUnits() // Charger TOUTES les unités, pas seulement disponibles
      console.log('All units:', response.data)
      
      // Enrichir les unités avec les informations des locataires actuels
      const unitsWithTenants = await Promise.all(
        (response.data || []).map(async (unit) => {
          try {
            // Récupérer les assignations depuis le backend
            const assignmentsResponse = await assignmentsService.getAssignments()
            const allAssignments = assignmentsResponse.data || []
            const unitAssignments = allAssignments.filter(a => parseInt(a.unitId) === unit.id)
            
            const currentTenants = unitAssignments.map(assignment => {
              // Le backend retourne les données dans tenantData
              const tenantData = assignment.tenantData || assignment.tenant
              return {
                id: assignment.tenantId,
                name: tenantData?.name || 'Locataire inconnu',
                email: tenantData?.email || '',
                phone: tenantData?.phone || ''
              }
            })
            
            // Nettoyer l'adresse pour éviter la duplication
            let cleanAddress = unit.unitAddress || `${unit.unitNumber}`
            
            // Si l'adresse contient des numéros dupliqués (ex: "56 56-58-60-62 rue Vachon")
            if (cleanAddress && cleanAddress.includes(' ')) {
              const parts = cleanAddress.split(' ')
              if (parts.length >= 3) {
                // Vérifier si le deuxième élément contient des tirets (ex: "56-58-60-62")
                if (parts[1] && parts[1].includes('-')) {
                  // Prendre seulement le premier numéro et tout après le deuxième élément
                  const unitNum = parts[0]
                  const streetPart = parts.slice(2).join(' ')
                  cleanAddress = `${unitNum} ${streetPart}`
                } else {
                  // Format normal, prendre le premier numéro et tout après le premier espace
                  const unitNum = parts[0]
                  const streetPart = parts.slice(1).join(' ')
                  cleanAddress = `${unitNum} ${streetPart}`
                }
              }
            }
            
            // Fallback si l'adresse est vide ou invalide
            if (!cleanAddress || cleanAddress.trim() === '') {
              cleanAddress = `Unité ${unit.unitNumber || unit.id}`
            }
            
            return {
              ...unit,
              // Mapping des propriétés pour l'affichage
              address: cleanAddress,
              buildingName: '', // Pas de nom d'immeuble
              simpleTitle: cleanAddress,
              currentTenants,
              isOccupied: currentTenants.length > 0
            }
          } catch (error) {
            console.error('Error loading tenants for unit:', unit.id, error)
            return {
              ...unit,
              address: unit.unitAddress || `Unité ${unit.unitNumber || unit.id}`,
              buildingName: '', // Pas de nom d'immeuble
              simpleTitle: unit.unitAddress || `Unité ${unit.unitNumber || unit.id}`,
              currentTenants: [],
              isOccupied: false
            }
          }
        })
      )
      
      setAvailableUnits(unitsWithTenants)
    } catch (error) {
      console.error('Error loading units:', error)
      setAvailableUnits([])
    } finally {
      setLoadingUnits(false)
    }
  }

  // Filtrer les unités selon le terme de recherche
  useEffect(() => {
    if (!unitSearchTerm.trim()) {
      setFilteredUnits(availableUnits.slice(0, 20)) // Limiter à 20 unités par défaut
      return
    }

    const searchLower = unitSearchTerm.toLowerCase()
    const filtered = availableUnits.filter(unit => {
      return (
        unit.buildingName?.toLowerCase().includes(searchLower) ||
        unit.address?.toLowerCase().includes(searchLower) ||
        unit.unitNumber?.toString().toLowerCase().includes(searchLower) ||
        unit.type?.toLowerCase().includes(searchLower)
      )
    })

    setFilteredUnits(filtered.slice(0, 50)) // Limiter à 50 résultats
  }, [unitSearchTerm, availableUnits])

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleLeaseRenewalChange = (renewalId, field, value) => {
    setFormData(prev => ({
      ...prev,
      leaseRenewals: prev.leaseRenewals.map(renewal => 
        renewal.id === renewalId 
          ? { ...renewal, [field]: value }
          : renewal
      )
    }))
  }

  const handleRenewalPdfUpload = (event, renewalId) => {
    const file = event.target.files[0]
    if (file) {
      // Simuler l'upload (à implémenter selon vos besoins)
      const fileName = `renewal_${renewalId}_${file.name}`
      handleLeaseRenewalChange(renewalId, 'renewalPdf', fileName)
    }
  }


  // Fonction de validation de date simple
  const isValidDate = (dateString) => {
    if (!dateString) return true // Vide est valide
    if (dateString.length < 4) return true // Trop court pour valider
    const regex = /^\d{4}-\d{2}-\d{2}$/
    if (!regex.test(dateString)) return false
    const date = new Date(dateString)
    return date instanceof Date && !isNaN(date)
  }

  const handleLeaseChange = (field, value) => {
    // Marquer les données de bail comme manuellement définies
    console.log('🔧 Modification manuelle des données de bail:', field, value)
    setIsLeaseDataManuallySet(true)
    setHasLeaseDataBeenModified(true)
    
    setFormData(prev => ({
      ...prev,
      lease: {
        ...(prev.lease || {}), // S'assurer que lease existe
        [field]: value
      }
    }))
  }


  // Nouvelle fonction pour uploader un PDF
  const uploadPdfFile = async (file, type = 'lease') => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        console.log(`✅ PDF uploadé avec succès: ${result.filename}`)
        return result.filename
      } else {
        const error = await response.json()
        console.error('❌ Erreur upload PDF:', error)
        alert(`Erreur lors de l'upload: ${error.detail || 'Erreur inconnue'}`)
        return null
      }
    } catch (error) {
      console.error('❌ Erreur upload PDF:', error)
      alert('Erreur de connexion lors de l\'upload')
      return null
    }
  }

  // Fonction pour gérer l'upload du PDF du bail principal
  const handleLeasePdfUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Seuls les fichiers PDF sont acceptés')
      return
    }

    // Afficher un message de chargement
    handleLeaseChange('leasePdf', `Upload en cours: ${file.name}...`)

    const uploadedFilename = await uploadPdfFile(file, 'lease')
    if (uploadedFilename) {
      handleLeaseChange('leasePdf', uploadedFilename)
    } else {
      handleLeaseChange('leasePdf', '')
    }
  }


  const handleUnitSelection = (unit) => {
    setFormData(prev => ({
      ...prev,
      unitId: unit?.id || '',
      unitInfo: unit || null,
      building: unit?.buildingName || '',
      unit: unit?.unitNumber || ''
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    setLoading(true)
    
    // Validation des champs obligatoires
    if (!formData.name.trim()) {
      alert('Le nom du locataire est obligatoire')
      setLoading(false)
      return
    }
    
    if (!formData.unitId) {
      alert('Veuillez sélectionner une unité')
      setLoading(false)
      return
    }
    
    // Préparer les données du locataire (SEULEMENT les infos personnelles)
    const tenantData = {
      name: formData.name.trim(),
      email: formData.email.trim(),
      phone: formData.phone.trim(),
      notes: formData.notes.trim()
    }
    
    // Préparer les données d'assignation (TOUTES les données de bail)
    const assignmentData = {
      unitId: parseInt(formData.unitId),
      moveInDate: formData.lease?.startDate || null,
      moveOutDate: formData.lease?.endDate || null,
      rentAmount: parseFloat(formData.lease?.monthlyRent) || 0,
      depositAmount: 0, // Pas de champ dans le formulaire actuel
      leaseStartDate: formData.lease?.startDate || null,
      leaseEndDate: formData.lease?.endDate || null,
      rentDueDay: 1, // Valeur par défaut
      notes: formData.notes.trim()
    }
    
    console.log('💾 Données à sauvegarder:', {
      tenant: tenantData,
      assignment: assignmentData
    })
    
    // Debug supplémentaire
    console.log('🔍 DEBUG - Détails des données:')
    console.log('  - tenantData keys:', Object.keys(tenantData))
    console.log('  - assignmentData keys:', Object.keys(assignmentData))
    console.log('  - unitId type:', typeof assignmentData.unitId, 'value:', assignmentData.unitId)
    console.log('  - tenantId type:', typeof assignmentData.tenantId, 'value:', assignmentData.tenantId)
    
    try {
      if (tenant?.id) {
        // MISE À JOUR du locataire existant
        console.log('📝 Mise à jour du locataire existant...')
        
        // 1. Mettre à jour les infos personnelles du locataire
        const tenantResponse = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/tenants/${tenant.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: tenantData.name,
            email: tenantData.email,
            phone: tenantData.phone,
            notes: tenantData.notes
          })
        })
        
        if (!tenantResponse.ok) {
          const errorText = await tenantResponse.text()
          throw new Error(`Erreur mise à jour locataire: ${tenantResponse.status} - ${errorText}`)
        }
        
        const updatedTenant = await tenantResponse.json()
        console.log('✅ Locataire mis à jour:', updatedTenant)
        
        // 2. Créer une nouvelle assignation avec les données de bail
        console.log('🏠 Création d\'une nouvelle assignation...')
        const assignmentResponse = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/assignments`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            tenantId: tenant.id,
            ...assignmentData
          })
        })
        
        if (!assignmentResponse.ok) {
          const errorText = await assignmentResponse.text()
          throw new Error(`Erreur création assignation: ${assignmentResponse.status} - ${errorText}`)
        }
        
        const newAssignment = await assignmentResponse.json()
        console.log('✅ Nouvelle assignation créée:', newAssignment)
        
        // Retourner les données mises à jour (sans déclencher onSave pour éviter le double appel)
        console.log('✅ Locataire mis à jour avec succès:', updatedTenant.data || updatedTenant)
        
        // Déclencher l'événement de mise à jour de locataire
        window.dispatchEvent(new CustomEvent('tenantUpdated', {
          detail: updatedTenant.data || updatedTenant
        }))
        
        // Fermer le formulaire
        onClose()
        
      } else {
        // CRÉATION d'un nouveau locataire avec assignation
        console.log('📤 Création d\'un nouveau locataire avec assignation...')
        
        console.log('📤 Envoi vers /api/tenants/create-with-assignment')
        console.log('📤 Payload complet:', {
          tenant: tenantData,
          assignment: assignmentData
        })
        
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/tenants/create-with-assignment`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            tenant: tenantData,
            assignment: assignmentData
          })
        })
        
        console.log('📥 Réponse reçue:', {
          status: response.status,
          statusText: response.statusText,
          ok: response.ok
        })
        
        if (!response.ok) {
          const errorText = await response.text()
          console.error('❌ Erreur backend:', errorText)
          throw new Error(`Erreur création: ${response.status} - ${errorText}`)
        }
        
        const result = await response.json()
        console.log('✅ Création réussie:', result)
        
        // Retourner les données créées (sans déclencher onSave pour éviter le double appel)
        console.log('✅ Locataire créé avec succès:', result.data.tenant)
        
        // 3. CRÉER LES RENOUVELLEMENTS si présents
        if (formData.leaseRenewals && formData.leaseRenewals.length > 0) {
          console.log('🔄 Création des renouvellements:', formData.leaseRenewals)
          
          for (const renewal of formData.leaseRenewals) {
            if (renewal.startDate && renewal.endDate) {
              try {
                const renewalResponse = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/assignments`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({
                    tenantId: result.data.tenant.id,
                    unitId: formData.unitId,
                    moveInDate: renewal.startDate,
                    moveOutDate: renewal.endDate,
                    rentAmount: renewal.monthlyRent || 0,
                    depositAmount: 0,
                    leaseStartDate: renewal.startDate,
                    leaseEndDate: renewal.endDate,
                    rentDueDay: 1,
                    notes: `Renouvellement de bail - ${renewal.renewalPdf || ''}`
                  })
                })
                
                if (renewalResponse.ok) {
                  const renewalResult = await renewalResponse.json()
                  console.log('✅ Renouvellement créé:', renewalResult)
                } else {
                  console.error('❌ Erreur création renouvellement:', await renewalResponse.text())
                }
              } catch (error) {
                console.error('❌ Erreur lors de la création du renouvellement:', error)
              }
            }
          }
        }
        
        // Déclencher l'événement de création de locataire
        window.dispatchEvent(new CustomEvent('tenantCreated', {
          detail: result.data.tenant
        }))
        
        // Fermer le formulaire
        onClose()
      }
      
      // Message de succès supprimé pour éviter les interruptions
      
    } catch (error) {
      console.error('❌ Erreur lors de la sauvegarde:', error)
      alert(`Erreur lors de la sauvegarde: ${error.message}`)
    } finally {
      setLoading(false)
      onClose()
    }
  }


  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {tenant ? 'Modifier le locataire' : 'Nouveau locataire'}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Informations complètes du locataire
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-8">
          {/* Informations personnelles */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Informations personnelles
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom complet *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Téléphone
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="(514) 555-0123"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Statut
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => handleInputChange('status', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  {Object.values(TenantStatus).map(status => (
                    <option key={status} value={status}>
                      {getTenantStatusLabel(status)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Sélection d'unité */}
          <div className="space-y-4">
            <div className="flex items-center mb-4">
              <Home className="h-5 w-5 text-primary-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Unité de Résidence</h3>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rechercher et sélectionner une unité
              </label>
              {loadingUnits ? (
                <div className="flex items-center justify-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                  <span className="ml-2 text-gray-600">Chargement des unités...</span>
                </div>
              ) : (
                <div className="space-y-3">
                  {/* Barre de recherche */}
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <input
                      type="text"
                      placeholder="Rechercher par adresse, immeuble ou numéro d'unité..."
                      value={unitSearchTerm}
                      onChange={(e) => setUnitSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>

                  {/* Liste des unités filtrées */}
                  <div className="max-h-60 overflow-y-auto border border-gray-200 rounded-lg">
                    {filteredUnits.length > 0 ? (
                      <div className="divide-y divide-gray-200">
                        {filteredUnits.map(unit => (
                          <div
                            key={unit.id}
                            onClick={() => handleUnitSelection(unit)}
                            className={`p-3 cursor-pointer hover:bg-gray-50 transition-colors ${
                              formData.unitId === unit.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                            }`}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center">
                                  <Home className="h-4 w-4 text-gray-400 mr-2" />
                                  <span className="font-medium text-gray-900">
                                    {unit.address}
                                  </span>
                                  {formData.unitId === unit.id && (
                                    <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                      Sélectionnée
                                    </span>
                                  )}
                                </div>
                                <p className="text-sm text-gray-600 mt-1">{unit.buildingName}</p>
                                
                                {/* Afficher les locataires actuels s'il y en a */}
                                {unit.currentTenants && unit.currentTenants.length > 0 && (
                                  <div className="mt-2">
                                    <p className="text-xs text-gray-500">Locataires actuels:</p>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {unit.currentTenants.map((tenant, index) => (
                                        <span key={index} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                          {tenant.name}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                              
                              <div className="text-right text-sm text-gray-500">
                                <div>{unit.type || 'N/A'}</div>
                                {unit.rental?.monthlyRent && (
                                  <div className="font-medium text-gray-900">{unit.rental.monthlyRent} $/mois</div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : unitSearchTerm ? (
                      <div className="p-4 text-center text-gray-500">
                        <Search className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                        <p>Aucune unité trouvée pour "{unitSearchTerm}"</p>
                        <p className="text-sm">Essayez avec un autre terme de recherche</p>
                      </div>
                    ) : (
                      <div className="p-4 text-center text-gray-500">
                        <Home className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                        <p>Tapez pour rechercher une unité</p>
                      </div>
                    )}
                  </div>

                  {/* Unité sélectionnée - Aperçu détaillé */}
                  {formData.unitInfo && (
                    <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-center mb-3">
                        <MapPin className="h-5 w-5 text-blue-600 mr-2" />
                        <span className="font-medium text-blue-900">Unité sélectionnée</span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-blue-800"><strong>Adresse:</strong> {formData.unitInfo.address}</p>
                          <p className="text-blue-800"><strong>Immeuble:</strong> {formData.unitInfo.buildingName}</p>
                          <p className="text-blue-800"><strong>Type:</strong> {formData.unitInfo.type || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-blue-800"><strong>Superficie:</strong> {formData.unitInfo.area ? `${formData.unitInfo.area} pi²` : 'N/A'}</p>
                          {formData.unitInfo.rental?.monthlyRent && (
                            <p className="text-blue-800"><strong>Loyer:</strong> {formData.unitInfo.rental.monthlyRent} $/mois</p>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Bouton pour désélectionner */}
                  {formData.unitId && (
                    <button
                      type="button"
                      onClick={() => handleUnitSelection(null)}
                      className="text-sm text-red-600 hover:text-red-700 flex items-center"
                    >
                      <X className="h-4 w-4 mr-1" />
                      Désélectionner l'unité
                    </button>
                  )}
                </div>
              )}
              
              {availableUnits.length === 0 && !loadingUnits && (
                <div className="p-4 text-center text-gray-500 border border-gray-200 rounded-lg">
                  <AlertTriangle className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p className="font-medium">Aucune unité disponible</p>
                  <p className="text-sm">Toutes les unités sont actuellement occupées.</p>
                </div>
              )}
            </div>
          </div>

          {/* Informations de Bail */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Informations de Bail
            </h3>
            
            {/* Bail actuel */}
            <div className="space-y-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-md font-medium text-gray-900 mb-4">Bail Actuel</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="min-h-[80px]">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date de début
                    </label>
                    <input
                      type="text"
                      value={formData.lease?.startDate || ''}
                      onChange={(e) => handleLeaseChange('startDate', e.target.value)}
                      placeholder="2025-01-01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                    <div className="h-4"></div>
                  </div>
                  
                  <div className="min-h-[80px]">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date de fin
                    </label>
                    <input
                      type="text"
                      value={formData.lease?.endDate || ''}
                      onChange={(e) => handleLeaseChange('endDate', e.target.value)}
                      placeholder="2025-12-31"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                    <div className="h-4"></div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Loyer mensuel (CAD)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.lease?.monthlyRent || 0}
                      onChange={(e) => handleLeaseChange('monthlyRent', parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="0.00"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Méthode de paiement
                    </label>
                    <select
                      value={formData.lease?.paymentMethod || 'Virement bancaire'}
                      onChange={(e) => handleLeaseChange('paymentMethod', e.target.value)}
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
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      PDF du bail
                    </label>
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleLeasePdfUpload}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                    {formData.lease.leasePdf && (
                      <p className={`text-xs mt-1 ${
                        formData.lease.leasePdf.startsWith('Upload en cours') 
                          ? 'text-blue-600' 
                          : 'text-green-600'
                      }`}>
                        {formData.lease.leasePdf.startsWith('Upload en cours') 
                          ? '⏳ ' + formData.lease.leasePdf
                          : '✓ ' + formData.lease.leasePdf
                        }
                      </p>
                    )}
                  </div>
                </div>
              </div>


              {/* Renouvellement de bail */}
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-md font-medium text-gray-900">Renouvellements de Bail</h4>
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({
                      ...prev,
                      leaseRenewals: [...prev.leaseRenewals, {
                        id: Date.now() + Math.random(), // Unique ID
                        startDate: '',
                        endDate: '',
                        monthlyRent: 0,
                        paymentMethod: 'Virement bancaire',
                        renewalPdf: '',
                      }]
                    }))}
                    className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    + Ajouter un renouvellement
                  </button>
                </div>
                
                {formData.leaseRenewals.length > 0 && (
                  <div className="space-y-4">
                    {formData.leaseRenewals.map((renewal, index) => (
                      <div key={renewal.id} className="bg-white rounded-lg p-4 shadow-sm border">
                        <div className="flex items-center justify-between mb-4">
                          <h5 className="text-md font-medium text-gray-900">Renouvellement {index + 1}</h5>
                          <button
                            type="button"
                            onClick={() => setFormData(prev => ({
                              ...prev,
                              leaseRenewals: prev.leaseRenewals.filter(r => r.id !== renewal.id)
                            }))}
                            className="text-red-600 hover:text-red-700"
                          >
                            <X className="h-5 w-5" />
                          </button>
                        </div>
                        
                        {/* Même structure que le bail principal */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                          <div className="min-h-[80px]">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Date de début
                            </label>
                            <input
                              type="text"
                              value={renewal.startDate}
                              onChange={(e) => handleLeaseRenewalChange(renewal.id, 'startDate', e.target.value)}
                              placeholder="2025-01-01"
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                            />
                            <div className="h-4"></div>
                          </div>
                          
                          <div className="min-h-[80px]">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Date de fin
                            </label>
                            <input
                              type="text"
                              value={renewal.endDate}
                              onChange={(e) => handleLeaseRenewalChange(renewal.id, 'endDate', e.target.value)}
                              placeholder="2025-12-31"
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                            />
                            <div className="h-4"></div>
                          </div>
                          
                          <div className="min-h-[80px]">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Loyer mensuel (CAD)
                            </label>
                            <input
                              type="number"
                              step="0.01"
                              value={renewal.monthlyRent}
                              onChange={(e) => handleLeaseRenewalChange(renewal.id, 'monthlyRent', parseFloat(e.target.value) || 0)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                            />
                            <div className="h-4"></div>
                          </div>
                          
                          <div className="min-h-[80px]">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Méthode de paiement
                            </label>
                            <select
                              value={renewal.paymentMethod || 'Virement bancaire'}
                              onChange={(e) => handleLeaseRenewalChange(renewal.id, 'paymentMethod', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                            >
                              <option value="Virement bancaire">Virement bancaire</option>
                              <option value="Chèque">Chèque</option>
                              <option value="Espèces">Espèces</option>
                              <option value="Autre">Autre</option>
                            </select>
                            <div className="h-4"></div>
                          </div>
                        </div>
                        
                        {/* PDF du renouvellement */}
                        <div className="mt-4">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            PDF du renouvellement
                          </label>
                          <div className="flex items-center space-x-4">
                            <input
                              type="file"
                              accept=".pdf"
                              onChange={(e) => handleRenewalPdfUpload(e, renewal.id)}
                              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                            />
                            {renewal.renewalPdf && (
                              <span className={`text-sm ${
                                renewal.renewalPdf.startsWith('Upload en cours') 
                                  ? 'text-blue-600' 
                                  : 'text-green-600'
                              }`}>
                                {renewal.renewalPdf.startsWith('Upload en cours') 
                                  ? '⏳ ' + renewal.renewalPdf
                                  : '✓ ' + renewal.renewalPdf
                                }
                              </span>
                            )}
                          </div>
                        </div>
                        
                      </div>
                    ))}
                    
                  </div>
                )}
                
                {!formData.leaseRenewals.length && (
                  <p className="text-sm text-gray-600">
                    Cliquez sur "Ajouter un renouvellement" pour créer un nouveau bail pour ce locataire.
                  </p>
                )}
              </div>
            </div>
          </div>




          {/* Notes */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Notes et commentaires
            </h3>
            <textarea
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Notes additionnelles, préférences, historique, etc."
            />
          </div>

          {/* Boutons d'action */}
          <div className="flex justify-end space-x-4 pt-6 border-t">
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
              className="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors flex items-center disabled:opacity-50"
            >
              <Save className="h-4 w-4 mr-2" />
              {loading ? 'Sauvegarde...' : 'Sauvegarder'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
} 