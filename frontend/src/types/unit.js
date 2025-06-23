// Types et modèles pour les unités d'immeubles

export const UnitStatus = {
  OCCUPIED: 'occupied',
  VACANT: 'vacant',
  MAINTENANCE: 'maintenance',
  RESERVED: 'reserved'
}

export const UnitType = {
  STUDIO: 'studio',
  ONE_BEDROOM: '1_bedroom',
  TWO_BEDROOM: '2_bedroom',
  THREE_BEDROOM: '3_bedroom',
  FOUR_BEDROOM: '4_bedroom',
  OTHER: 'other'
}

export const defaultUnit = {
  id: null,
  buildingId: null,
  buildingName: '',
  unitNumber: '',
  address: '',
  type: UnitType.ONE_BEDROOM,
  status: UnitStatus.VACANT,
  area: 0, // en pieds carrés
  bedrooms: 1,
  bathrooms: 1,
  
  // Informations locatives
  rental: {
    monthlyRent: 0,
    deposit: 0,
    leaseStart: null,
    leaseEnd: null,
    rentDueDay: 1, // jour du mois
  },
  
  // Services inclus
  amenities: {
    heating: false,        // chauffage inclus
    electricity: false,    // électricité incluse
    wifi: false,          // wifi inclus
    furnished: false,     // meublé
    parking: false,       // stationnement inclus
    laundry: false,       // buanderie incluse
    airConditioning: false, // climatisation
    balcony: false,       // balcon
    storage: false,       // rangement
    dishwasher: false,    // lave-vaisselle
    washerDryer: false,   // laveuse-sécheuse
  },
  
  // Informations du locataire
  tenant: {
    name: '',
    email: '',
    phone: '',
    emergencyContact: {
      name: '',
      phone: '',
      relationship: ''
    },
    moveInDate: null,
    moveOutDate: null,
  },
  
  // Historique des loyers
  rentHistory: [],
  
  // Notes et commentaires
  notes: '',
  
  // Métadonnées
  createdAt: null,
  updatedAt: null
}

export const getUnitTypeLabel = (type) => {
  switch (type) {
    case UnitType.STUDIO:
      return 'Studio'
    case UnitType.ONE_BEDROOM:
      return '1 chambre'
    case UnitType.TWO_BEDROOM:
      return '2 chambres'
    case UnitType.THREE_BEDROOM:
      return '3 chambres'
    case UnitType.FOUR_BEDROOM:
      return '4 chambres'
    case UnitType.OTHER:
      return 'Autre'
    default:
      return type
  }
}

export const getUnitStatusLabel = (status) => {
  switch (status) {
    case UnitStatus.OCCUPIED:
      return 'Occupée'
    case UnitStatus.VACANT:
      return 'Libre'
    case UnitStatus.MAINTENANCE:
      return 'Maintenance'
    case UnitStatus.RESERVED:
      return 'Réservée'
    default:
      return status
  }
}

export const getUnitStatusColor = (status) => {
  switch (status) {
    case UnitStatus.OCCUPIED:
      return 'bg-green-100 text-green-800'
    case UnitStatus.VACANT:
      return 'bg-red-100 text-red-800'
    case UnitStatus.MAINTENANCE:
      return 'bg-yellow-100 text-yellow-800'
    case UnitStatus.RESERVED:
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// Fonction pour parser l'adresse et générer les unités
export const parseAddressAndGenerateUnits = (building) => {
  const units = []
  const address = typeof building.address === 'string' ? building.address : building.address?.street || ''
  const city = typeof building.address === 'string' ? '' : building.address?.city || ''
  const province = typeof building.address === 'string' ? '' : building.address?.province || ''
  const postalCode = typeof building.address === 'string' ? '' : building.address?.postalCode || ''
  const country = typeof building.address === 'string' ? '' : building.address?.country || ''
  
  // Format 1: 4932-4934-4936 Route Des Vétérans (adresses séparées par des tirets)
  if (address.includes('-') && !address.includes('#')) {
    const parts = address.split(' ')
    const numbers = parts[0].split('-')
    const streetName = parts.slice(1).join(' ')
    
    numbers.forEach((number, index) => {
      const unitAddress = `${number.trim()} ${streetName}`
      units.push(createUnitFromBuilding(building, index + 1, unitAddress, city, province, postalCode, country))
    })
  }
  // Format 2: 4490, 1-2-3-4-5-6, Rue Denault (numéro de base + unités numérotées)
  else if (address.includes(',')) {
    const parts = address.split(',').map(part => part.trim())
    if (parts.length >= 3) {
      const baseNumber = parts[0]
      const unitNumbers = parts[1].split('-')
      const streetName = parts.slice(2).join(', ')
      
      unitNumbers.forEach((unitNum, index) => {
        const unitAddress = `${baseNumber} #${unitNum.trim()} ${streetName}`
        units.push(createUnitFromBuilding(building, index + 1, unitAddress, city, province, postalCode, country))
      })
    }
  }
  // Format standard: créer des unités numérotées basées sur le nombre d'unités
  else {
    for (let i = 1; i <= building.units; i++) {
      const unitAddress = `${address} #${i}`
      units.push(createUnitFromBuilding(building, i, unitAddress, city, province, postalCode, country))
    }
  }
  
  return units
}

const createUnitFromBuilding = (building, unitNumber, unitAddress, city, province, postalCode, country) => {
  return {
    ...defaultUnit,
    id: `${building.id}-${unitNumber}`,
    buildingId: building.id,
    buildingName: building.name,
    unitNumber: unitNumber.toString(),
    address: unitAddress,
    fullAddress: {
      street: unitAddress,
      city,
      province,
      postalCode,
      country
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
} 