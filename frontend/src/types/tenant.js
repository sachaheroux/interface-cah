// Types et modèles pour les locataires

export const TenantStatus = {
  ACTIVE: 'actif',
  PENDING: 'en_attente',
  INACTIVE: 'inactif',
  FORMER: 'ancien'
}

export const defaultTenant = {
  id: null,
  nom: '',
  prenom: '',
  email: '',
  telephone: '',
  statut: TenantStatus.ACTIVE,
  
  // Référence à l'unité assignée
  id_unite: null,
  unitInfo: null,
  
  // Champs legacy pour compatibilité
  building: '',
  unit: '',
  
  notes: '',
  
  // Métadonnées
  date_creation: null,
  date_modification: null
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

// Fonction pour créer un locataire de base à partir des données minimales
export const createBasicTenant = (nom, prenom, email = '', telephone = '') => {
  return {
    ...defaultTenant,
    id: `temp-${Date.now()}`,
    nom,
    prenom,
    email,
    telephone,
    date_creation: new Date().toISOString(),
    date_modification: new Date().toISOString()
  }
} 