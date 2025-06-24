// Types et modèles pour les unités d'immeubles

// Types d'unités selon le format québécois
export const UnitType = {
  THREE_HALF: '3_1_2',
  FOUR_HALF: '4_1_2', 
  FIVE_HALF: '5_1_2',
  SIX_HALF: '6_1_2',
  SEVEN_HALF: '7_1_2'
}

// Statut d'unité (calculé dynamiquement)
export const UnitStatus = {
  VACANT: 'vacant',
  OCCUPIED: 'occupied'
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
  
  // Référence au locataire (ID du système de gestion des locataires)
  tenantId: null,
  
  // Informations du locataire (copiées pour affichage, source de vérité dans le système locataires)
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
  const labels = {
    [UnitType.THREE_HALF]: '3 1/2',
    [UnitType.FOUR_HALF]: '4 1/2', 
    [UnitType.FIVE_HALF]: '5 1/2',
    [UnitType.SIX_HALF]: '6 1/2',
    [UnitType.SEVEN_HALF]: '7 1/2'
  }
  return labels[type] || type
}

export const getUnitStatusLabel = (status) => {
  const labels = {
    [UnitStatus.VACANT]: 'Libre',
    [UnitStatus.OCCUPIED]: 'Occupée'
  }
  return labels[status] || status
}

export const getUnitStatusColor = (status) => {
  const colors = {
    [UnitStatus.VACANT]: 'bg-red-100 text-red-800',
    [UnitStatus.OCCUPIED]: 'bg-green-100 text-green-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

// Fonction pour calculer le statut dynamiquement
export const calculateUnitStatus = (unit, assignments = []) => {
  if (!assignments || assignments.length === 0) {
    return UnitStatus.VACANT
  }
  
  const unitAssignments = assignments.filter(a => a.unitId === unit.id)
  return unitAssignments.length > 0 ? UnitStatus.OCCUPIED : UnitStatus.VACANT
}

// Fonction pour parser une adresse et générer des unités
export const parseAddressAndGenerateUnits = (building) => {
  if (!building || !building.address) {
    console.warn('Immeuble sans adresse:', building)
    return []
  }

  const units = []
  
  // Gérer les différents formats d'adresse
  let address = ''
  try {
    if (typeof building.address === 'string') {
      address = building.address.trim()
    } else if (typeof building.address === 'object' && building.address.street) {
      // Format objet avec street, city, etc.
      address = building.address.street.trim()
    } else {
      console.warn('Format d\'adresse non supporté pour l\'immeuble:', building)
      return []
    }
    
    if (!address) {
      console.warn('Adresse vide pour l\'immeuble:', building)
      return []
    }
  } catch (error) {
    console.error('Erreur lors du traitement de l\'adresse:', building, error)
    return []
  }
  
  // Format 1: Adresses séparées par des tirets (ex: 4932-4934-4936 Route Des Vétérans)
  if (address.includes('-') && !address.includes(',')) {
    const parts = address.split(' ')
    const addressNumbers = parts[0]
    const streetName = parts.slice(1).join(' ')
    
    if (addressNumbers.includes('-')) {
      const numbers = addressNumbers.split('-')
      numbers.forEach((num, index) => {
        units.push({
          id: `${building.id}-${index + 1}`,
          buildingId: building.id,
          buildingName: building.name,
          unitNumber: num,
          address: `${num} ${streetName}`,
          type: UnitType.FOUR_HALF, // Valeur par défaut
          area: 0,
          bedrooms: 2,
          bathrooms: 1,
          rental: {
            monthlyRent: 0,
            deposit: 0,
            leaseStart: '',
            leaseEnd: '',
            rentDueDay: 1,
          },
          amenities: {
            heating: false,
            electricity: false,
            wifi: false,
            furnished: false,
            parking: false,
            laundry: false,
            airConditioning: false,
            balcony: false,
            storage: false,
            dishwasher: false,
            washerDryer: false,
          },
          notes: '',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
      })
    }
  }
  
  // Format 2: Adresse avec numéros d'unités (ex: 4490, 1-2-3-4-5-6, Rue Denault)
  else if (address.includes(',')) {
    const parts = address.split(',').map(part => part.trim())
    
    if (parts.length >= 3) {
      const baseAddress = parts[0]
      const unitNumbers = parts[1]
      const streetName = parts[2]
      
      if (unitNumbers.includes('-')) {
        const numbers = unitNumbers.split('-')
        numbers.forEach((num, index) => {
          units.push({
            id: `${building.id}-${index + 1}`,
            buildingId: building.id,
            buildingName: building.name,
            unitNumber: num,
            address: `${baseAddress} Unité ${num}, ${streetName}`,
            type: UnitType.FOUR_HALF, // Valeur par défaut
            area: 0,
            bedrooms: 2,
            bathrooms: 1,
            rental: {
              monthlyRent: 0,
              deposit: 0,
              leaseStart: '',
              leaseEnd: '',
              rentDueDay: 1,
            },
            amenities: {
              heating: false,
              electricity: false,
              wifi: false,
              furnished: false,
              parking: false,
              laundry: false,
              airConditioning: false,
              balcony: false,
              storage: false,
              dishwasher: false,
              washerDryer: false,
            },
            notes: '',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          })
        })
      }
    }
  }
  
  // Format 3: Adresse simple (une seule unité)
  else {
    // Construire l'adresse complète si c'est un objet
    let fullAddress = address
    if (typeof building.address === 'object') {
      const parts = [
        building.address.street,
        building.address.city,
        building.address.province,
        building.address.postalCode
      ].filter(Boolean)
      fullAddress = parts.join(', ')
    }
    
    units.push({
      id: `${building.id}-1`,
      buildingId: building.id,
      buildingName: building.name,
      unitNumber: '1',
      address: fullAddress,
      type: UnitType.FOUR_HALF, // Valeur par défaut
      area: 0,
      bedrooms: 2,
      bathrooms: 1,
      rental: {
        monthlyRent: 0,
        deposit: 0,
        leaseStart: '',
        leaseEnd: '',
        rentDueDay: 1,
      },
      amenities: {
        heating: false,
        electricity: false,
        wifi: false,
        furnished: false,
        parking: false,
        laundry: false,
        airConditioning: false,
        balcony: false,
        storage: false,
        dishwasher: false,
        washerDryer: false,
      },
      notes: '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    })
  }

  return units
} 