// Types et modèles pour les locataires

export const TenantStatus = {
  ACTIVE: 'active',
  PENDING: 'pending',
  INACTIVE: 'inactive',
  FORMER: 'former'
}

export const defaultTenant = {
  id: null,
  name: '',
  email: '',
  phone: '',
  status: TenantStatus.ACTIVE,
  
  // Référence à l'unité assignée
  unitId: null,
  unitInfo: null,
  
  // Champs legacy pour compatibilité
  building: '',
  unit: '',
  
  // Contact d'urgence
  emergencyContact: {
    name: '',
    phone: '',
    email: '',
    relationship: ''
  },
  
  // Informations financières
  financial: {
    monthlyIncome: 0,
    creditScore: 0,
    bankAccount: '',
    employer: '',
    employerPhone: ''
  },
  
  // Historique de location
  rentalHistory: [],
  
  // Documents
  documents: {
    idCopy: null,
    proofOfIncome: null,
    references: [],
    lease: null
  },
  
  notes: '',
  
  // Métadonnées
  createdAt: null,
  updatedAt: null
}

export const getTenantStatusLabel = (status) => {
  switch (status) {
    case TenantStatus.ACTIVE:
      return 'Actif'
    case TenantStatus.PENDING:
      return 'En attente'
    case TenantStatus.INACTIVE:
      return 'Inactif'
    case TenantStatus.FORMER:
      return 'Ancien locataire'
    default:
      return status
  }
}

export const getTenantStatusColor = (status) => {
  switch (status) {
    case TenantStatus.ACTIVE:
      return 'bg-green-100 text-green-800'
    case TenantStatus.PENDING:
      return 'bg-yellow-100 text-yellow-800'
    case TenantStatus.INACTIVE:
      return 'bg-gray-100 text-gray-800'
    case TenantStatus.FORMER:
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

export const getRelationshipLabel = (relationship) => {
  switch (relationship) {
    case 'parent':
      return 'Parent'
    case 'conjoint':
      return 'Conjoint(e)'
    case 'enfant':
      return 'Enfant'
    case 'frere_soeur':
      return 'Frère/Sœur'
    case 'ami':
      return 'Ami(e)'
    case 'collegue':
      return 'Collègue'
    case 'autre':
      return 'Autre'
    default:
      return relationship
  }
}

// Fonction pour créer un locataire de base à partir des données minimales
export const createBasicTenant = (name, email = '', phone = '') => {
  return {
    ...defaultTenant,
    id: `temp-${Date.now()}`,
    name,
    email,
    phone,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
} 