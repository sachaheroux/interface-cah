// Types et modèles pour les immeubles
export const BuildingTypes = {
  RESIDENTIAL: 'residential',
  COMMERCIAL: 'commercial',
  MIXED: 'mixed',
  INDUSTRIAL: 'industrial'
}

export const BuildingStatus = {
  ACTIVE: 'active',
  CONSTRUCTION: 'construction',
  MAINTENANCE: 'maintenance',
  INACTIVE: 'inactive'
}

export const defaultBuilding = {
  id: null,
  name: '',
  address: {
    street: '',
    city: '',
    province: '',
    postalCode: '',
    country: 'Canada'
  },
  type: BuildingTypes.RESIDENTIAL,
  status: BuildingStatus.ACTIVE,
  units: 0,
  floors: 1,
  yearBuilt: new Date().getFullYear(),
  totalArea: 0, // en pieds carrés
  characteristics: {
    parking: 0,
    elevator: false,
    balconies: 0,
    storage: false,
    laundry: false,
    airConditioning: false,
    heating: 'electric', // electric, gas, oil
    internet: false,
    security: false
  },
  financials: {
    purchasePrice: 0,
    currentValue: 0,
    monthlyRevenue: 0,
    monthlyExpenses: 0,
    taxes: 0,
    insurance: 0
  },
  contacts: {
    manager: '',
    contractor: '',
    insurance: ''
  },
  notes: '',
  images: [],
  documents: [],
  createdAt: null,
  updatedAt: null
}

export const getBuildingTypeLabel = (type) => {
  const labels = {
    [BuildingTypes.RESIDENTIAL]: 'Résidentiel',
    [BuildingTypes.COMMERCIAL]: 'Commercial',
    [BuildingTypes.MIXED]: 'Mixte',
    [BuildingTypes.INDUSTRIAL]: 'Industriel'
  }
  return labels[type] || type
}

export const getBuildingStatusLabel = (status) => {
  const labels = {
    [BuildingStatus.ACTIVE]: 'Actif',
    [BuildingStatus.CONSTRUCTION]: 'En construction',
    [BuildingStatus.MAINTENANCE]: 'Maintenance',
    [BuildingStatus.INACTIVE]: 'Inactif'
  }
  return labels[status] || status
} 