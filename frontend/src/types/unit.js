// Types et modèles pour les unités d'immeubles

export const defaultUnit = {
  id: null,
  id_immeuble: null,
  nom_immeuble: '',
  adresse_unite: '',
  type: '1 1/2',
  nbr_chambre: 1,
  nbr_salle_de_bain: 1,
  
  // Métadonnées
  date_creation: null,
  date_modification: null
}

// Fonction pour obtenir le label du type d'unité
export const getUnitTypeLabel = (type) => {
  return type || '1 1/2'
}

// Fonction pour parser une adresse et générer des unités
export const parseAddressAndGenerateUnits = (building) => {
  if (!building || !building.adresse) {
    console.warn('Immeuble sans adresse:', building)
    return []
  }

  const units = []
  
  // Gérer les différents formats d'adresse
  let address = building.adresse.trim()
  
  if (!address) {
    console.warn('Adresse vide pour l\'immeuble:', building)
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
        // Construire l'adresse sans duplication
        let unitAddress = `${num} ${streetName}`
        
        // Si l'adresse de l'immeuble contient déjà le numéro, éviter la duplication
        if (streetName.includes(num)) {
          // Extraire seulement la partie nom de rue après le numéro
          const streetParts = streetName.split(' ')
          const cleanStreetName = streetParts.filter(part => !part.includes(num)).join(' ')
          unitAddress = `${num} ${cleanStreetName}`.trim()
        }
        
        units.push({
          id: `${building.id}-${index + 1}`,
          id_immeuble: building.id,
          nom_immeuble: building.nom_immeuble,
          adresse_unite: unitAddress,
          type: '4 1/2', // Valeur par défaut
          nbr_chambre: 2,
          nbr_salle_de_bain: 1,
          notes: '',
          date_creation: new Date().toISOString(),
          date_modification: new Date().toISOString()
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
            id_immeuble: building.id,
            nom_immeuble: building.nom_immeuble,
            adresse_unite: `${baseAddress} Unité ${num}, ${streetName}`,
            type: '4 1/2', // Valeur par défaut
            nbr_chambre: 2,
            nbr_salle_de_bain: 1,
            notes: '',
            date_creation: new Date().toISOString(),
            date_modification: new Date().toISOString()
          })
        })
      }
    }
  }
  
  // Format 3: Adresse simple (une seule unité)
  else {
    units.push({
      id: `${building.id}-1`,
      id_immeuble: building.id,
      nom_immeuble: building.nom_immeuble,
      adresse_unite: address,
      type: '4 1/2', // Valeur par défaut
      nbr_chambre: 2,
      nbr_salle_de_bain: 1,
      notes: '',
      date_creation: new Date().toISOString(),
      date_modification: new Date().toISOString()
    })
  }

  return units
} 