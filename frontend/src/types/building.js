// Types et modèles pour les immeubles
export const BuildingTypes = {
  RESIDENTIAL: 'residential',
  COMMERCIAL: 'commercial',
  MIXED: 'mixed',
  INDUSTRIAL: 'industrial'
}

// Statut supprimé selon la demande

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
    downPayment: 0,
    interestRate: 0,
    currentValue: 0
  },
  contacts: {
    owner: '',
    bank: '',
    contractor: ''
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

// Fonction getBuildingStatusLabel supprimée car statut supprimé 